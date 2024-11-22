import requests
from bs4 import BeautifulSoup
import json
import time
import pandas as pd
from urllib.parse import quote
import random
import logging

class XiachufangScraper:
    def __init__(self):
        self.base_url = "https://m.xiachufang.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='scraper_debug.log'
        )
        
    def search_recipe(self, dish_name):
        """Search for a specific dish and return top 3 recipes."""
        encoded_name = quote(dish_name)
        search_url = f"{self.base_url}/search/?keyword={encoded_name}&cat=1001"
        
        try:
            logging.info(f"Searching for dish: {dish_name}")
            logging.info(f"URL: {search_url}")
            
            response = requests.get(search_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find recipe cards with the correct class
            recipe_cards = soup.find_all('a', class_='recipe-96-horizon')[:3]
            
            logging.info(f"Found {len(recipe_cards)} recipe cards")
            
            recipes = []
            for card in recipe_cards:
                recipe = {}
                
                # Get recipe URL
                recipe['url'] = self.base_url + card['href'] if card['href'].startswith('/') else card['href']
                
                # Get recipe name
                name_elem = card.find('header', class_='name')
                if name_elem:
                    recipe['name'] = name_elem.text.strip()
                
                # Get recipe stats
                stats_elem = card.find('div', class_='stat')
                if stats_elem:
                    # Extract rating and number of people who made it
                    rating = stats_elem.find('span')
                    made_count = stats_elem.text.split()[-2] if stats_elem.text else '0'
                    recipe['rating'] = rating.text if rating else 'N/A'
                    recipe['made_count'] = made_count
                
                recipes.append(recipe)
            
            return recipes
            
        except Exception as e:
            logging.error(f"Error scraping {dish_name}: {str(e)}", exc_info=True)
            return []
            
    def scrape_all_dishes(self, dishes_data):
        """Scrape all dishes from the provided data structure."""
        results = {}
        
        for cuisine, dishes in dishes_data['dishes_by_cuisine'].items():
            logging.info(f"\nScraping cuisine: {cuisine}")
            cuisine_results = {}
            
            for dish in dishes:
                logging.info(f"Scraping dish: {dish}")
                recipes = self.search_recipe(dish)
                cuisine_results[dish] = recipes
                
                # Random delay between requests
                delay = random.uniform(2, 5)
                logging.info(f"Waiting {delay:.2f} seconds before next request")
                time.sleep(delay)
            
            results[cuisine] = cuisine_results
        
        return results
    
    def save_results(self, results, filename='recipe_results.json'):
        """Save the scraped results to a JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
    def create_excel_report(self, results, filename='recipe_results.xlsx'):
        """Create an Excel report from the scraped data."""
        rows = []
        
        for cuisine, dishes in results.items():
            for dish_name, recipes in dishes.items():
                for recipe in recipes:
                    rows.append({
                        'Cuisine': cuisine,
                        'Dish Name': dish_name,
                        'Recipe Name': recipe.get('name', ''),
                        'Recipe URL': recipe.get('url', ''),
                        'Rating': recipe.get('rating', ''),
                        'Made Count': recipe.get('made_count', '')
                    })
                    
        df = pd.DataFrame(rows)
        df.to_excel(filename, index=False)

def main():
    # Your complete dishes data
    dishes_data = {
        "total_dishes": 84,
        "dishes_by_cuisine": {
            "新疆菜": ["烤羊肉串", "馕", "羊肉抓饭"],  # Testing with first cuisine
        }
    }
    
    scraper = XiachufangScraper()
    results = scraper.scrape_all_dishes(dishes_data)
    
    # Save results
    scraper.save_results(results)
    scraper.create_excel_report(results)

if __name__ == "__main__":
    main()