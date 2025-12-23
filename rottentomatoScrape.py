import sys
import os
import datetime
import requests
from bs4 import BeautifulSoup

dataset_folder = os.path.join(os.path.dirname(__file__), "DataSets")
os.makedirs(dataset_folder, exist_ok=True)

file_path = os.path.join(dataset_folder, f"BestRottenThisMonth.txt")
with open(file_path, "w") as file:
    request_ = requests.get("https://www.rottentomatoes.com/browse/tv_series_browse/sort:popular")
    soup = BeautifulSoup(request_.text, "html.parser")

    flexContainer = soup.find_all("div", class_="flex-container")

    for flex in flexContainer:
        title = flex.find("span", class_="p--small")
        critic_score = flex.find("rt-text", class_="criticsScore")
        audience_score = flex.find("rt-text", class_="audienceScore")
        if title and critic_score and audience_score:
            titlText = title.text.strip()
            critic_scoreText = critic_score.text.strip()
            audience_scoreText = audience_score.text.strip()
            file.write(f"{titleText} - Critic Score: {critic_scoreText} - Audience Score: {audience_scoreText}\n")
            





