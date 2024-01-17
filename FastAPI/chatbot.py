from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.prompts import PromptTemplate
from langchain_experimental.agents.agent_toolkits import create_csv_agent


def csv_query(path,query):
    llm = GoogleGenerativeAI(model="gemini-pro", google_api_key="AIzaSyBfC19UW2oyq2fb-atswzNtPuPOj2xUWp4")
    agent = create_csv_agent(llm, path, verbose=False)
    output=agent.invoke(query)

    return output['output']

def general_query(query):
    llm = GoogleGenerativeAI(model="gemini-pro", google_api_key="AIzaSyBfC19UW2oyq2fb-atswzNtPuPOj2xUWp4")
    template = """Question: {question}
    Answer: Let's think step by step."""
    prompt = PromptTemplate.from_template(template)

    chain = prompt | llm

    ans=chain.invoke({"question": query})
    return ans
