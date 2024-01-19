import tkinter as tk
from tkinter import filedialog
import requests
import threading
import pygame
from pathlib import Path

# import matplotlib
# matplotlib.use('Agg')

pygame.mixer.init()
def play_sound():
    pygame.mixer.Sound("alert.wav").play()

def download_file(url, local_filename):
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(local_filename, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
    # print(f'Downloaded: {local_filename}')

def choose_download_location():
    root = tk.Tk()
    root.attributes('-topmost', 1)
    root.withdraw()  # Hide the main window

    file_path = filedialog.asksaveasfilename(defaultextension=".csv" ,filetypes=[("CSV files", "*.csv")])

    root.destroy()  # Close the main window after selection
    return file_path

def downloader(url):
        download_location = str(Path.home() / "Downloads")
        # download_location = choose_download_location()
        if download_location:
            threading.Thread(target=play_sound).start()
            download_file(url, download_location)

