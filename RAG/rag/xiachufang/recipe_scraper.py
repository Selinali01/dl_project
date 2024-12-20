import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional, List
from recipe_db import LocalRecipeDB
import time
import random
import logging
from urllib.parse import quote

class XiachufangScraper:
    def __init__(self):
        self.base_url = "https://m.xiachufang.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.db = LocalRecipeDB()
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='xiachufang_scraper.log'
        )

    def extract_recipe_content(self, url: str) -> Optional[str]:
        """Extract all text content from a recipe page."""
        try:
            # Add longer timeout and verify=False for testing
            response = requests.get(url, headers=self.headers, timeout=20, verify=False)
            response.raise_for_status()
            
            # Save HTML content for debugging
            with open('last_recipe_page.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract all text nodes while preserving structure
            content_parts = []
            
            # Helper function to extract text from elements
            def extract_text(element):
                if element.string and element.string.strip():
                    return element.string.strip()
                return ' '.join(text.strip() for text in element.stripped_strings)
            
            # Get all elements that might contain recipe content
            for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'div', 'li']):
                text = extract_text(element)
                if text and len(text) > 1:  # Ignore single characters
                    content_parts.append(text)
            
            # Remove duplicates while preserving order
            seen = set()
            content_parts = [x for x in content_parts if x not in seen and not seen.add(x)]
            
            # Join with newlines
            content = '\n'.join(content_parts)
            
            # Log the extracted content
            logging.info(f"Extracted content length: {len(content)}")
            logging.debug(f"Extracted content: {content[:500]}...")
            
            return content if len(content) > 20 else None  # Only return if we have substantial content
            
        except Exception as e:
            logging.error(f"Error extracting recipe content from {url}: {str(e)}")
            return None

    def search_recipe(self, dish_name: str) -> List[Dict]:
        """Search for a specific dish and return top 3 recipes."""
        encoded_name = quote(dish_name)
        search_url = f"{self.base_url}/search/?keyword={encoded_name}&cat=1001"
        
        try:
            logging.info(f"Searching for dish: {dish_name}")
            logging.info(f"Search URL: {search_url}")
            
            # Add longer timeout and verify=False for testing
            response = requests.get(search_url, headers=self.headers, timeout=20, verify=False)
            response.raise_for_status()
            
            # Save search page HTML for debugging
            with open('last_search_page.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try different selectors for recipe links
            recipe_links = []
            selectors = [
                'a.recipe-96-horizon',
                'div.recipe-item a',
                'a[href*="/recipe/"]',
                '.recipe-card a',
                '.recipe-link'
            ]
            
            for selector in selectors:
                links = soup.select(selector)
                logging.info(f"Selector '{selector}' found {len(links)} links")
                recipe_links.extend(links)
            
            # Remove duplicates while preserving order
            seen_urls = set()
            unique_links = []
            for link in recipe_links:
                url = link.get('href', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_links.append(link)
            
            recipe_links = unique_links[:3]  # Take top 3
            
            recipes = []
            for link in recipe_links:
                recipe_url = self.base_url + link['href'] if link['href'].startswith('/') else link['href']
                logging.info(f"Processing recipe URL: {recipe_url}")
                
                # Add longer delay
                time.sleep(random.uniform(3, 5))
                
                recipe_content = self.extract_recipe_content(recipe_url)
                if recipe_content:
                    recipes.append({
                        'url': recipe_url,
                        'content': recipe_content
                    })
            
            return recipes
            
        except Exception as e:
            logging.error(f"Error searching for {dish_name}: {str(e)}")
            return []

    def scrape_and_store_recipes(self, dishes_by_cuisine: Dict[str, List[str]]):
        """Scrape Xiachufang for each dish and store in the database"""
        total_processed = 0
        total_failed = 0
        
        for cuisine_type, dishes in dishes_by_cuisine.items():
            print(f"\nProcessing {cuisine_type}...")
            
            for dish in dishes:
                print(f"\nSearching for: {dish}")
                recipes = self.search_recipe(dish)
                
                for i, recipe in enumerate(recipes, 1):
                    if recipe['content']:
                        metadata = {
                            'dish_name': dish,
                            'cuisine_type': cuisine_type,
                            'source_url': recipe['url'],
                            'recipe_number': i
                        }
                        
                        self.db.add_recipe(
                            content=recipe['content'],
                            metadata=metadata,
                            source='xiachufang'
                        )
                        total_processed += 1
                        print(f"✓ Successfully stored recipe {i} for {dish}")
                    else:
                        print(f"✗ Failed to extract content for recipe {i} of {dish}")
                
                if not recipes:
                    total_failed += 1
                    print(f"✗ Failed to find recipes for {dish}")
                
                # Add longer delay between dishes
                time.sleep(random.uniform(5, 8))
        
        print(f"\nProcessing complete!")
        print(f"Successfully processed: {total_processed}")
        print(f"Failed to process: {total_failed}")
        
        stats = self.db.get_collection_stats()
        print(f"\nDatabase stats:")
        print(f"Total recipes in database: {stats['total_recipes']}")

def main():
    dishes_data = {
        "浙江菜": ["黄鱼烧年糕"]  # Test with one dish first
    }
    
    scraper = XiachufangScraper()
    scraper.scrape_and_store_recipes(dishes_data)

if __name__ == "__main__":
    main()