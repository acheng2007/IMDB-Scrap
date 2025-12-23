import os
import json
import datetime
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm # Optional: for a progress bar (pip install tqdm)

def main():
    # 1. Setup Folders correctly
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_dir = os.path.join(base_dir, "DataSets")
    os.makedirs(dataset_dir, exist_ok=True)

    current_year = int(datetime.datetime.now().year)
    
    # 2. Use Headers to avoid 403 Forbidden errors
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    # Loop from 1898 to present
    for year in tqdm(range(1898, current_year + 1)):
        
        # 3. Use 'requests' instead of 'urllib'
        url = f"https://www.imdb.com/search/title/?release_date={year}-01-01,{year}-12-31&title_type=feature"
        
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            
            dataset_top50 = {}
            
            # 4. UPDATED SELECTORS for New IMDB Layout
            # The main list is now a UL with class 'ipc-metadata-list'
            # Each movie is an LI with class 'ipc-metadata-list-summary-item'
            movie_rows = soup.find_all('li', class_='ipc-metadata-list-summary-item')

            for index, row in enumerate(movie_rows, 1):
                movie_item = {
                    'name': 'N/A',
                    'year': str(year),
                    'runtime': 'N/A',
                    'certificate': 'N/A',
                    'rating': 'N/A'
                }

                # -- Title --
                title_tag = row.find('h3', class_='ipc-title__text')
                if title_tag:
                    # Remove "1. " from "1. The Movie"
                    raw_text = title_tag.get_text(strip=True)
                    movie_item['name'] = raw_text.split('. ', 1)[-1] if '. ' in raw_text else raw_text

                # -- Metadata (Year, Duration, Rated) --
                # These are usually in a specific list inside the row
                metadata_items = row.find_all('span', class_='sc-b189961a-8') # Note: These random classes change frequently!
                # A safer bet is looking for the inline-list
                metadata_container = row.find('div', class_='sc-b189961a-7')
                if metadata_container:
                     spans = metadata_container.find_all('span', recursive=False)
                     # Usually [Year, Duration, Certificate] order, but not always.
                     # This part is tricky on the new layout without complex logic.
                     if len(spans) > 1:
                         movie_item['runtime'] = spans[1].get_text(strip=True)
                
                # -- Rating --
                rating_span = row.find('span', class_='ipc-rating-star')
                if rating_span:
                    movie_item['rating'] = rating_span.get_text(strip=True).split('(')[0].strip()

                dataset_top50[index] = movie_item

            # 5. Write JSON cleanly (Don't hijack sys.stdout)
            file_path = os.path.join(dataset_dir, f'IMDB_Top_50_{year}.json')
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(dataset_top50, f, indent=4)
                
        except Exception as e:
            print(f"Failed to scrape {year}: {e}")

if __name__ == "__main__":
    main()