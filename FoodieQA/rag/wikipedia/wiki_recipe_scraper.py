import requests
from bs4 import BeautifulSoup
import time
from typing import Dict, Optional, List
from recipe_db import LocalRecipeDB
import wikipedia
import re

class WikiRecipeScraper:
    def __init__(self):
        self.db = LocalRecipeDB()
        wikipedia.set_lang('en')
        
        # Dictionary of Chinese dish names to English translations
        self.dish_translations = {
            # Xinjiang cuisine
            "烤羊肉串": ["Chuanr", "Chinese lamb skewers", "Xinjiang kebab", "Yang rou chuan"],
            "馕": ["Nang bread", "Uyghur naan", "Xinjiang naan"],
            "羊肉抓饭": ["Uyghur polo", "Xinjiang pilaf", "Lamb pilaf Xinjiang"],
            "大盘鸡": ["Dapanji", "Big plate chicken Xinjiang"],
            
            # Sichuan cuisine
            "辣子鸡丁": ["Laziji", "Chongqing Chicken", "Sichuan spicy diced chicken"],
            "水煮肉片": ["Shuizhu beef", "Water boiled beef Sichuan"],
            "宫保鸡丁": ["Kung Pao chicken", "Gongbao chicken"],
            "回锅肉": ["Twice cooked pork", "Hui guo rou", "Double cooked pork Sichuan"],
            
            # Cantonese cuisine
            "叉烧包": ["Char siu bao", "BBQ pork bun Cantonese"],
            "虾饺": ["Har gow", "Ha gau", "Cantonese shrimp dumpling"],
            "煲仔饭": ["Clay pot rice", "Bo zai fan"],
        }
        
    def clean_text(self, text: str) -> str:
        """Clean Wikipedia text by removing references and extra whitespace"""
        text = re.sub(r'\[\d+\]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def search_wiki_page(self, dish_name: str, cuisine_type: str) -> Optional[Dict]:
        """Search for a dish on Wikipedia and extract relevant information"""
        try:
            # Get English translations for the dish
            translations = self.dish_translations.get(dish_name, [dish_name])
            
            # Try each translation
            page = None
            used_term = None
            
            for term in translations:
                search_terms = [
                    f"{term} dish",
                    f"{term} Chinese cuisine",
                    f"{term} {cuisine_type}",
                    term
                ]
                
                for search_term in search_terms:
                    try:
                        print(f"  Trying search term: {search_term}")
                        search_results = wikipedia.search(search_term, results=1)
                        if search_results:
                            page = wikipedia.page(search_results[0], auto_suggest=False)
                            used_term = term
                            break
                    except wikipedia.exceptions.DisambiguationError as e:
                        # Try the first option in disambiguation
                        try:
                            page = wikipedia.page(e.options[0], auto_suggest=False)
                            used_term = term
                            break
                        except:
                            continue
                    except:
                        continue
                
                if page:
                    break
                    
            if not page:
                return None
                
            # Extract content
            summary = self.clean_text(page.summary)
            
            # Structure the information
            recipe_info = {
                'title': page.title,
                'summary': summary,
                'url': page.url,
                'cuisine_type': cuisine_type,
                'chinese_name': dish_name,
                'english_name': used_term
            }
            
            return recipe_info
            
        except Exception as e:
            print(f"  Error processing {dish_name}: {str(e)}")
            return None
    
    def clear_database(self):
        """Clear all entries from the database"""
        try:
            self.db.client.delete_collection("chinese_recipes")
            self.db.collection = self.db.client.create_collection(
                name="chinese_recipes",
                embedding_function=self.db.embedding_fn,
                metadata={"description": "Chinese recipe database"}
            )
            print("Database cleared successfully")
        except Exception as e:
            print(f"Error clearing database: {str(e)}")
    
    def scrape_and_store_recipes(self, dishes_by_cuisine: Dict[str, List[str]]):
        """Scrape Wikipedia for each dish and store in the database"""
        total_processed = 0
        total_failed = 0
        
        for cuisine_type, dishes in dishes_by_cuisine.items():
            print(f"\nProcessing {cuisine_type}...")
            
            for dish in dishes:
                print(f"\nSearching for: {dish}")
                recipe_info = self.search_wiki_page(dish, cuisine_type)
                
                if recipe_info:
                    # Store in database
                    content = (
                        f"Title: {recipe_info['title']}\n"
                        f"Chinese Name: {recipe_info['chinese_name']}\n"
                        f"English Name: {recipe_info['english_name']}\n"
                        f"Cuisine Type: {recipe_info['cuisine_type']}\n\n"
                        f"{recipe_info['summary']}"
                    )
                    
                    metadata = {
                        'dish_name': dish,
                        'english_name': recipe_info['english_name'],
                        'cuisine_type': cuisine_type,
                        'source_url': recipe_info['url']
                    }
                    
                    self.db.add_recipe(content=content, metadata=metadata, source='wikipedia')
                    total_processed += 1
                    print(f"✓ Successfully stored {dish} ({recipe_info['english_name']})")
                else:
                    total_failed += 1
                    print(f"✗ Failed to find information for {dish}")
                
                # Be nice to Wikipedia's servers
                time.sleep(1)
        
        print(f"\nProcessing complete!")
        print(f"Successfully processed: {total_processed}")
        print(f"Failed to process: {total_failed}")
        
        # Print database stats
        stats = self.db.get_collection_stats()
        print(f"\nDatabase stats:")
        print(f"Total recipes in database: {stats['total_recipes']}")