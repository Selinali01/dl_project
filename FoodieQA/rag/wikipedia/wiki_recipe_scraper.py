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
            "烤羊肉串": ["Chunar", "Chinese lamb skewers", "Xinjiang kebab", "Yang rou chuan"],
            "馕": ["Nang bread", "Uyghur naan", "Xinjiang naan"],
            "羊肉抓饭": ["Uyghur polo", "Xinjiang pilaf", "Lamb pilaf"],
            "过油肉拌面": ["Yourou banmian", "Oil-mixed noodles with meat", "pulled noodles with fried lamb and vegetables", "Uyghur Laghman"],
            "菠菜面": ["Spinach noodles", "Xinjiang spinach noodles"],
            "拉条子": ["Latiaozi", "Hand-pulled noodles", "Laghman"],
            "大盘鸡": ["Dapanji", "Big plate chicken"],
            "干煸炒面": ["Ganbian chaomian", "Dry-fried noodles"],
            "新疆架子肉": ["Jiazi meat", "Xinjiang rack of lamb"], # no related link
            "丁丁炒面": ["Dingding chaomian", "Chopped noodles"], # no related link

            # Sichuan cuisine
            "辣子鸡丁": ["Laziji", "Chongqing Chicken", "Sichuan spicy diced chicken"],
            "青椒肉丝": ["Qingjiao rousi", "Shredded pork with green peppers"], 
            "啤酒鸭": ["Beer duck", "Pijiu ya"], # no related page
            "水煮肉片": ["Shuizhu beef", "Water-boiled beef"],
            "四川火锅": ["Sichuan hotpot", "Sichuan huoguo"],
            "宫保鸡丁": ["Kung Pao chicken", "Gongbao chicken"],
            "酸菜鱼": ["Fish with pickled mustard greens"],
            "辣椒炒肉": ["Stir-fried pork with chili"], # no related page
            "麻辣烫": ["Malatang"],
            "毛血旺": ["Mao xue wang"],
            "冒菜": ["Maocai", "Boiled meat in spicy soup"],
            "口水鸡": ["Mouth-watering chicken", "Saliva chicken", "Kou shui ji"], # no related link        
            "回锅肉": ["Twice-cooked pork", "Hui guo rou"],
            "四川冰粉": ["bingfen"],
            "重庆火锅": ["Chongqing hotpot"],

            # Northwest cuisine
            "水煮鱼": ["Shuizhu"],
            "米皮": ["Liangpi", "Rice skin noodles"],
            "酿皮": ["Liangpi", "Niang pi", "Cold skin noodles"], 
            "糖醋丸子": ["Sweet and sour meatballs"], # no related page 
            "酱牛肉": ["Braised beef", "Jiang niu rou"], # no related page
            "手抓羊肉": ["Hand-pulled lamb", "Shou zhua yang rou"], # no related page
            "猪皮冻": ["Pork jelly", "Pork skin jelly"],
            "面皮/凉皮": ["Liang pi", "Cold rice noodles"],

            # Guizhou cuisine
            "凯里酸汤鱼": ["Sour soup fish"],
            "豆腐圆子": ["Tofu balls", "Doufu yuanzi"], # no related page
            "荷叶粉蒸肉": ["Lotus leaf steamed pork"], # no related page
            "水城烙锅": ["Shuicheng lao guo", "Water town pot"], # no related page
            "辣子鸡": ["laziji", "Spicy chicken"],
            "丝娃娃": ["Si wa wa", "Guizhou lettuce wraps"],

            # Jiangsu cuisine
            "毛式红烧肉": ["Mao-style red braised pork"],
            "盐水鸭": ["Nanjing salted duck"],
            "无锡小笼包": ["Wuxi xiaolongbao", "Wuxi soup dumplings"],
            "松鼠鱼": ["Squirrel fish", "Song shu yu"],
            "青团": ["Qingtuan", "Green rice balls"],
            "太湖银鱼": ["Lake Tai silverfish"], # no related page
            "响油鳝糊": ["Crispy eel paste"], # no related page
            "阳春面": ["Yang chun noodles"],
            "蟹黄汤包": ["Crab roe soup dumplings"], # no related page

            # Cantonese cuisine
            "鸡蛋肠粉": ["Egg cheung fun", "Rice noodle rolls with egg"],
            "红米肠粉": ["Red rice cheung fun"], # no related page
            "叉烧包": ["Char siu bao", "BBQ pork bun"],
            "黑椒牛仔骨": ["Black pepper short ribs"], # no related page
            "虾饺": ["Har gow", "Shrimp dumplings"],
            "煲仔饭": ["Claypot rice", "Bo zai fan"],
            "咖喱牛腩牛筋面": ["Curry beef brisket noodles"], # no related page
            "鱼丸粉": ["Fish ball", "Fish ball noodles"],
            "脆皮烧鹅": ["Roast goose"], #
            "清蒸鲈鱼": ["Steamed bass"], # no related page
            "干炒牛河": ["Beef chow fun"],
            "陈皮牛肉丸": ["Steamed meatballs", "chenpi", "Dried tangerine peel beef balls"], # added steamed meatballs, chenpi, no related page

            # Other regional cuisines
            "臭鳜鱼": ["Stinky mandarin fish"], # no related page
            "猪血丸子": ["Pork blood balls"], # no related page
            "剁椒鱼头": ["Chopped chili fish head"], # no related page
            "桂花糖藕": ["Osmanthus lotus root"], # no related food
            "梅菜扣肉": ["Mei cai kou rou", "Preserved vegetable pork"], # no related page
            "红烧牛肉": ["Red braised beef"], # no related page
            "荔枝肉": ["Lychee pork"],
            "姜母鸭": ["Ginger mother duck"], # no related page
            "同安封肉": ["Tong'an wrapped pork"], 
            "白切鸡": ["White cut chicken", "Bai qie ji"],
            "西湖醋鱼": ["West Lake vinegar fish"],
            "黄鱼烧年糕": ["Yellow croaker with rice cakes"], # no related pages
            "龙井虾仁": ["Longjing shrimp", "Dragon well shrimp"],
            "扬州炒饭": ["Yangzhou fried rice"],
            "椒麻鸡": ["Chinese Pepper chicken"], # no related page
            "油爆虾": ["chili shrimp", "Deep-fried prawns"],
            "锅包肉": ["Guo bao rou", "Northeastern sweet and sour pork"],
            "拉皮": ["Liangpi", "La pi", "Mung bean sheets"],
            "大碴子粥": ["Da cha zi zhou", "Corn porridge"], # no related page
            "内蒙烤全羊": ["Khorkhog", "Inner Mongolian whole roasted lamb"],
            "鸭血粉丝汤": ["Duck blood vermicelli soup"],
            "酒酿圆子": ["Tangyuan", "Rice wine sweet rice balls"], 
            "客家酿豆腐": ["Hakka stuffed tofu"],
            "北京烤鸭": ["Peking duck", "Beijing roast duck"]
        }
        
    def clean_text(self, text: str) -> str:
        """Clean Wikipedia text by removing references and extra whitespace"""
        text = re.sub(r'\[\d+\]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def search_wiki_page(self, dish_name: str, cuisine_type: str) -> Optional[Dict]:
        """Search for a dish on Wikipedia and extract relevant information"""
        try:
            translations = self.dish_translations.get(dish_name, [dish_name])
            # translations = [dish_name]
            
            # Try each translation
            page = None
            used_term = None
            
            for term in translations:
                search_terms = [
                    term,
                    f"{term} dish",
                    f"{term} Chinese cuisine",
                    f"{term} {cuisine_type}",
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