import sys
import os
import datetime
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# 1. Setup Paths
# using os.makedirs ensures the folder exists; exist_ok=True prevents errors if it's already there
dataset_folder = os.path.join(os.path.dirname(__file__), "DataSets")
os.makedirs(dataset_folder, exist_ok=True)

current_year = int(datetime.datetime.now().year)
# IMDB requires a robust User-Agent now to avoid 403 Forbidden errors
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

input_year = int(input("Please enter start year (eg. 2016): "))

if input_year > current_year:
    print(f"No movies recorded for {input_year} yet!")
else:
    for year in tqdm(range(input_year, input_year + 1)):
        file_path = os.path.join(dataset_folder, f"IMDB_Top_{year}.txt")
        
        # 2. Safer File Writing (Context Manager)
        # Instead of hijacking sys.stdout, we open the file and write to it directly
        with open(file_path, 'w+', encoding='utf-8') as f:
            
            url = f"https://www.imdb.com/search/title/?title_type=tv_series&release_date={year}-01-01,{year}-12-31&user_rating=8,10"
            
            try:
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.text, "html.parser")

                # Write Header
                f.write(f"Top Movies for {year}:\n")
                f.write("-" * 20 + "\n")

                # 3. NEW SELECTORS (The Critical Fix)
                # IMDB now uses 'ipc-metadata-list-summary-item' for movie rows
                # We look for the main list <ul>, then find all <li> items inside it
                movie_items = soup.find_all('li', class_='ipc-metadata-list-summary-item')
                movie_ratings = soup.find_all('span', class_='ipc-rating-star--rating')
                

                if not movie_items:
                    f.write("No movies found or layout changed.\n")
                    continue
                if not movie_ratings:
                    f.write("No ratings found or layout changed.\n")
                    continue

                for i, (item,rating) in enumerate(zip(movie_items,movie_ratings), 1):
                    # Find the title inside the h3 tag
                    title_tag = item.find('h3', class_='ipc-title__text')
                    rating_text = rating.get_text(strip=True)
                    
                    if title_tag and rating_text:
                        # Clean the title (IMDB sometimes includes "1. " in the text now)
                        title_text = title_tag.get_text(strip=True)
                        # Remove existing numbering if present (e.g. "1. The Movie")
                        if title_text[0].isdigit() and '. ' in title_text:
                            title_text = title_text.split('. ', 1)[1]
                            
                        f.write(f"{i}. Series: {title_text} ({rating_text})\n")
            
            except Exception as e:
                print(f"Error processing year {year}: {e}")

print("Done! Check the 'DataSets' folder.")