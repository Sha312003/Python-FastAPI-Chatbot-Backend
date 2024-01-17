from fastapi import FastAPI, HTTPException, Query, Request, UploadFile,File
import requests
from fastapi.middleware.cors import CORSMiddleware
import re
from downloader import downloader
from pydantic import BaseModel
from chatbot import csv_query,general_query
from pathlib import Path
from log_script import logger

app = FastAPI()
csv_uploaded=False
csv_path=""


UPLOAD_DIR= Path('../')/'uploads'

class Item(BaseModel):  
    link: str


origins=['http://localhost:3000']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/search")
async def search(tags: str = None, query: str = None):
    # Implement your search logic here, considering both tags and query
    # You can handle each parameter as needed
    logger.info(f"Get request started with-> tags:{tags} and query:{query} ")
    tags_lis=[]
    query_lis=[]

    if tags:
        tags_lis=re.split(r'\W+', tags)
        tags_lis=list(filter(None, tags_lis))

    if query:
        query_lis=re.split(r'\W+', query)
        query_lis=list(filter(None, query_lis))

    main_api_url = "https://catalog.data.gov/api/3/action/package_search"

    # Set up the parameters for the API request
    params = {
        "q": query_lis,
        "fq=tags": tags_lis,
    }

    filtered_params = {key: values for key, values in params.items() if values}

    # Concatenate values with '+' for the 'key' parameter
    formatted_params = '&'.join([f"{key}={'+'.join(map(str, values))}" if key=='q'
                                else f"{key}:{'+'.join(map(str, values))}" for key, values in filtered_params.items() ])

    # Concatenate the formatted parameters to the URL
    full_url = f"{main_api_url}?{formatted_params}"

    # Make the GET request
    try:
        if(len(tags_lis)==0 and len(query_lis)==0):
            logger.info("Process starts to get data using data.gov api")
            # Make a request to the data.gov API
            response = requests.get(full_url)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes

            # Print the response content
            data=response.json()
            

            back_data=[]
            title_check = []

            for item in data['result']['results']:

                for res in item['resources']:
                    if res['format']=="csv"or"CSV":
                        if item['title'] in title_check:
                            pass
                        else:
                            dict={}
                            dict['title']=item['title']
                            dict['description']=item['notes']
                            dict['link']=res['url']
                            title_check.append(item['title'])
                            back_data.append(dict)

            logger.info("Search process succesfully ends by providing data to frontend")
            return {"results": back_data}
        
        else:
            logger.info("Process starts to get data using data.gov api")
            # Make a request to the data.gov API
            response = requests.get(full_url)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes

            # Print the response content
            data=response.json()
            back_data=[]
            title_check = []


            cnt=1
            total_cnt=data['result']['count']
            full_url=full_url+'&start='
            if(total_cnt>50):
                total_cnt=50
            while(cnt<total_cnt):
                url=full_url+str(cnt)
                cnt+=10
                response = requests.get(url)
                response.raise_for_status()
                data=response.json()
                for item in data['result']['results']:

                    for res in item['resources']:
                        if res['format']=="csv"or"CSV":
                            if item['title'] in title_check:
                                pass
                            else:
                                dict={}
                                dict['title']=item['title']
                                dict['description']=item['notes']
                                dict['link']=res['url']
                                title_check.append(item['title'])
                                back_data.append(dict)

            print(len(back_data))
            logger.info("Search process succesfully ends by providing data to frontend")
            return {"results": back_data}
    

    except requests.RequestException as e:
        # Handle API request errors
        logger.info("Caught error while searching for datasets")
        raise HTTPException(status_code=500, detail=f"Error fetching data from data.gov API: {str(e)}")


@app.post("/card_clicked")
async def card_clicked(item:Item): 
    logger.info(f"Process for Csv download start using received link: {item.link}") 
    print(item.link)
    downloader(item.link)
    logger.info("CSV successfully downloaded")
    return {"message": "Download started successfully"}


@app.post("/upload_csv/")
async def upload_csv_file(file: UploadFile):
    logger.info("Request to upload file in backend initialised")
    data=await file.read()
    save_to=UPLOAD_DIR/file.filename
    with open(save_to,'wb') as f:
        f.write(data)
    global csv_uploaded
    global csv_path
    csv_uploaded=True
    csv_path=str(save_to)
    logger.info(f"file successfully downloaded to location:{csv_path} having filename: {file.filename}")
    return {"file": file.filename}


class UserInput(BaseModel):
    question: str
    max_tokens: int

@app.post("/ask_chatbot/")
async def ask_chatbot(data :UserInput):
    print(data.question)
    logger.info("Question/ Answer Session started for chatbot")
    if csv_uploaded:
        logger.info("CSV received, Specific QnA session in progress")
        ans=csv_query(csv_path,data.question)
        return {"result": ans}
    else:
        logger.info("CSV not received, General QnA session in progress")
        ans=general_query(data.question)
        return {"result": ans}
    
