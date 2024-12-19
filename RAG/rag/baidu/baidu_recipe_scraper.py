from bs4 import BeautifulSoup
import requests
import time
from typing import Dict, Optional, List
import re
from urllib.parse import quote
import json
import os

class BaiduRecipeScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        self.all_recipes = {}
        
        # Create directory if it doesn't exist
        os.makedirs('./baidu_recipe_db', exist_ok=True)

    def search_recipe_info(self, dish_name: str, cuisine_type: str) -> Optional[Dict]:
        """Search for detailed recipe information on Baidu"""
        try:
            baike_url = f"https://baike.baidu.com/item/{quote(dish_name)}"
            baike_response = requests.get(baike_url, headers=self.headers)
            baike_response.encoding = 'utf-8'
            
            recipe_info = {
                'dish_name': dish_name,
                'cuisine_type': cuisine_type,
                'description': '',
                'ingredients': [],
                'steps': [],
                'url': baike_url
            }
            
            if baike_response.status_code == 200:
                soup = BeautifulSoup(baike_response.text, 'html.parser')
                self._extract_basic_info(soup, recipe_info)
                self._extract_recipe_details(soup, recipe_info)
            
            return recipe_info
            
        except Exception as e:
            print(f"Error processing {dish_name}: {str(e)}")
            return None

    def _extract_basic_info(self, soup: BeautifulSoup, recipe_info: Dict):
        """Extract basic information from Baidu Baike"""
        # Description
        summary_div = soup.find('div', class_='lemma-summary')
        if summary_div:
            recipe_info['description'] = self.clean_text(summary_div.get_text())
        
        # Characteristics and history
        for para_title in soup.find_all('div', class_='para-title'):
            title_text = para_title.get_text().strip()
            para_content = para_title.find_next('div', class_='para')
            if para_content:
                content_text = self.clean_text(para_content.get_text())
                
                if any(keyword in title_text for keyword in ['特点', '特色']):
                    recipe_info['characteristics'].append(content_text)
                elif '历史' in title_text:
                    recipe_info['history'] = content_text

    def _extract_recipe_details(self, soup: BeautifulSoup, recipe_info: Dict):
        """Extract recipe-specific details from Baidu Baike"""
        # Ingredients
        ingredients_section = soup.find(text=re.compile('主料|配料|材料'))
        if ingredients_section:
            parent = ingredients_section.find_parent('div')
            if parent:
                ingredients_text = parent.get_text()
                ingredients = re.findall(r'[^，。：;\s]+', ingredients_text)
                recipe_info['ingredients'].extend([ing for ing in ingredients if len(ing) > 1])
        
        # Cooking steps - updated to handle numbered steps
        steps = []
        # Look for sections containing cooking steps
        for section in soup.find_all(['div', 'ol']):
            text = section.get_text()
            if any(keyword in text for keyword in ['菜品制作', '制作方法', '做法']):
                # Find numbered steps
                step_matches = re.findall(r'[步骤]?\d+[.、．]+(.*?)(?=\d+[.、．]|$)', text)
                if step_matches:
                    steps.extend([self.clean_text(step) for step in step_matches if step.strip()])
        
        if steps:
            recipe_info['steps'] = steps

    def _extract_meishi_info(self, url: str, recipe_info: Dict):
        """Extract additional recipe information from Baidu Meishi"""
        try:
            response = requests.get(url, headers=self.headers)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract additional recipe details
                recipe_cards = soup.find_all('div', class_='recipe-card')
                if recipe_cards:
                    first_recipe = recipe_cards[0]
                    
                    # Additional ingredients
                    ingredients_div = first_recipe.find('div', class_='ingredients')
                    if ingredients_div:
                        new_ingredients = [
                            ing.strip() 
                            for ing in ingredients_div.get_text().split('、')
                        ]
                        recipe_info['ingredients'].extend(new_ingredients)
                    
                    # Additional steps
                    steps_div = first_recipe.find('div', class_='steps')
                    if steps_div:
                        new_steps = [
                            self.clean_text(step.get_text())
                            for step in steps_div.find_all('div', class_='step')
                        ]
                        if new_steps:
                            recipe_info['steps'] = new_steps
        
        except Exception as e:
            print(f"Error extracting Meishi info: {str(e)}")

    def clean_text(self, text: str) -> str:
        """Clean scraped text"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'展开全部|收起|编辑|播报|分享', '', text)
        return text.strip()

    def store_recipe(self, recipe_info: Dict):
        """Store recipe information in both database and JSON"""
        # Store in memory dictionary
        self.all_recipes[recipe_info['dish_name']] = recipe_info
        
        # Save to single JSON file
        with open('./baidu_recipe_db/all_recipes.json', 'w', encoding='utf-8') as f:
            json.dump(self.all_recipes, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    dishes_by_cuisine = {
        "新疆菜": [
            "烤羊肉串", "馕", "羊肉抓饭", "过油肉拌面", "菠菜面",
            "拉条子", "大盘鸡", "干煸炒面", "新疆架子肉", "丁丁炒面"
        ],
        "川菜": [
            "辣子鸡丁", "青椒肉丝", "啤酒鸭", "水煮肉片", "四川火锅",
            "宫保鸡丁", "酸菜鱼", "辣椒炒肉", "麻辣烫", "毛血旺",
            "冒菜", "口水鸡", "回锅肉", "四川冰粉", "重庆火锅"
        ],
        "陕西菜": [
            "水煮鱼", "米皮", "酿皮", "糖醋丸子", "酱牛肉",
            "手抓羊肉", "猪皮冻", "凉皮"
        ],
        "贵州菜": [
            "凯里酸汤鱼", "豆腐圆子", "荷叶粉蒸肉", "水城烙锅",
            "辣子鸡", "丝娃娃"
        ],
        "苏菜": [
            "毛式红烧肉", "盐水鸭", "无锡小笼包", "松鼠鱼", "青团",
            "太湖银鱼", "响油鳝糊", "阳春面", "蟹黄汤包"
        ],
        "粤菜": [
            "鸡蛋肠粉", "红米肠粉", "叉烧包", "黑椒牛仔骨", "虾饺",
            "煲仔饭", "咖喱牛腩牛筋面", "鱼丸粉", "脆皮烧鹅",
            "清蒸鲈鱼", "干炒牛河", "陈皮牛肉丸"
        ],
        "徽菜": ["臭鳜鱼"],
        "湘菜": ["猪血丸子", "剁椒鱼头"],
        "上海菜": ["桂花糖藕"],
        "客家菜": ["梅菜扣肉"],
        "云南菜": ["红烧牛肉"],
        "闽菜": ["荔枝肉", "姜母鸭", "同安封肉"],
        "浙菜": [
            "西湖醋鱼", "黄鱼烧年糕", "龙井虾仁", "扬州炒饭",
            "椒麻鸡", "油爆虾"
        ],
        "东北菜": ["锅包肉", "拉皮", "大碴子粥"],
        "内蒙菜": ["内蒙烤全羊"]
    }
    
    scraper = BaiduRecipeScraper()
    
    # Track progress
    total_recipes = sum(len(dishes) for dishes in dishes_by_cuisine.values())
    processed = 0
    failed = []
    
    for cuisine_type, dishes in dishes_by_cuisine.items():
        print(f"\nProcessing {cuisine_type}...")
        for dish in dishes:
            processed += 1
            print(f"[{processed}/{total_recipes}] Processing: {dish}")
            recipe_info = scraper.search_recipe_info(dish, cuisine_type)
            if recipe_info:
                scraper.store_recipe(recipe_info)
                print(f"✓ Successfully stored recipe for {dish}")
            else:
                failed.append((cuisine_type, dish))
                print(f"✗ Failed to retrieve recipe for {dish}")
            time.sleep(2)  # Be nice to Baidu's servers
    
    # Print summary
    print("\n=== Scraping Summary ===")
    print(f"Total recipes attempted: {total_recipes}")
    print(f"Successfully scraped: {total_recipes - len(failed)}")
    print(f"Failed: {len(failed)}")
    if failed:
        print("\nFailed recipes:")
        for cuisine, dish in failed:
            print(f"- {dish} ({cuisine})")