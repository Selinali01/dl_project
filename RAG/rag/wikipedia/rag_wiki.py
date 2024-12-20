from recipe_db import LocalRecipeDB
import json
from typing import Dict, List
import re

class ChromaInspector:
    def __init__(self):
        self.db = LocalRecipeDB()
        self.question_types = {
            'cuisine_type': "菜系 cuisine traditional origin",
            'flavor': "taste flavor characteristics 口味 味道",
            'region': "region location geographical origin 地区 产地",
            'present': "presentation appearance plating 外形 样式",
            'cooking_skills': "cooking method preparation technique 烹饪 制作",
            'main_ingredient': "ingredients components 主料 配料"
        }
        
        # Move patterns definition into __init__
        self.patterns = {
            'cuisine_type': {
                'keywords': ['cuisine', '菜系', 'traditional', 'origin'],
                'patterns': [
                    r'Cuisine Type: ([^\.]+)',
                    r'From its origins in ([^\.]+)',
                ]
            },
            'flavor': {
                'keywords': ['spicy', 'sweet', 'sour', 'taste', 'flavor', '口味', '味道'],
                'patterns': [
                    r'is a ([^,]+), ([^,]+) Chinese dish',
                    r'flavors? include[s]? ([^\.]+)',
                ]
            },
            'region': {
                'keywords': ['region', 'province', 'origins', '地区', '产地'],
                'patterns': [
                    r'From its origins in ([^\.]+)',
                    r'popular in ([^\.]+)',
                ]
            },
            'present': {
                'keywords': ['made with', 'served', 'presentation', '外形', '样式'],
                'patterns': [
                    r'made with ([^\.]+)',
                    r'served with ([^\.]+)',
                ]
            },
            'cooking_skills': {
                'keywords': ['stir-fried', 'cooked', 'preparation', '烹饪', '制作'],
                'patterns': [
                    r'is a [^,]*, ([^,]*-[^,]* dish)',
                    r'prepared by ([^\.]+)',
                ]
            },
            'main_ingredient': {
                'keywords': ['made with', 'ingredients', 'contains', '主料', '配料'],
                'patterns': [
                    r'made with ([^\.]+)',
                    r'containing ([^\.]+)',
                ]
            }
        }

    
    def get_dish_entries(self, dish_name: str) -> List[Dict]:
        """Get all entries for a specific dish"""
        entries = self.get_all_entries()
        return [entry for entry in entries 
                if entry['metadata'].get('dish_name') == dish_name]
    
    
    def inspect_dish(self, dish_name: str):
        """Inspect a specific dish across all question types"""
        print(f"\n=== Analysis of '{dish_name}' ===\n")
        
        dish_entries = self.get_dish_entries(dish_name)
        if not dish_entries:
            print(f"No entries found for dish: {dish_name}")
            return
            
        for entry in dish_entries:
            print(f"\nAnalyzing entry: {entry['id']}")
            print("\nBase Information:")
            print(f"Cuisine Type: {entry['metadata'].get('cuisine_type', 'Not specified')}")
            print(f"English Name: {entry['metadata'].get('english_name', 'Not specified')}")
            
            print("\nAspect Analysis:")
            for aspect in self.patterns.keys():
                print(f"\n{aspect.upper()}:")
                info = self.extract_info(entry['content'], aspect)
                if info:
                    for i, text in enumerate(info, 1):
                        # Clean up the output
                        if len(text) > 100:  # If text is too long
                            # Try to find a shorter relevant phrase
                            shorter = re.split(r'[,.]', text)[0]
                            print(f"{i}. {shorter}")
                        else:
                            print(f"{i}. {text}")
                else:
                    print("No specific information found")
    def extract_info(self, content: str, aspect: str) -> List[str]:
        """Extract relevant information for a specific aspect"""
        info = set()  # Use set to avoid duplicates from the start
        patterns = self.patterns[aspect]['patterns']
        
        # Try each pattern
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                info.add(match.group(1).strip())
        
        # Find relevant sentences containing keywords
        keywords = self.patterns[aspect]['keywords']
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        for sentence in sentences:
            if any(keyword.lower() in sentence.lower() for keyword in keywords):
                # Don't add full metadata block or repetitive content
                if not (sentence.startswith('Title:') or 
                    sentence.startswith('Chinese Name:') or 
                    'pinyin:' in sentence):
                    # Extract just the relevant part if it's a long sentence
                    for keyword in keywords:
                        if keyword.lower() in sentence.lower():
                            # Find the relevant clause containing the keyword
                            clauses = sentence.split(',')
                            relevant_clauses = [c.strip() for c in clauses 
                                            if keyword.lower() in c.lower()]
                            if relevant_clauses:
                                info.add(relevant_clauses[0])
        
        return list(info)
                
    def get_all_entries(self) -> List[Dict]:
        """Retrieve all entries from the database"""
        collection = self.db.collection
        result = collection.get()
        
        entries = []
        for i in range(len(result['ids'])):
            entry = {
                'id': result['ids'][i],
                'content': result['documents'][i],
                'metadata': result['metadatas'][i]
            }
            entries.append(entry)
            
        return entries

    def list_dishes(self):
        """List all unique dish names in the database"""
        entries = self.get_all_entries()
        dishes = set()
        for entry in entries:
            if 'dish_name' in entry['metadata']:
                dishes.add(entry['metadata']['dish_name'])
        return sorted(list(dishes))

if __name__ == "__main__":
    inspector = ChromaInspector()
    
    # List available dishes
    dishes = inspector.list_dishes()
    print("\nAvailable dishes in database:")
    for dish in dishes:
        print(f"- {dish}")
    
    # Analyze a specific dish
    print("\nAnalyzing a sample dish...")
    inspector.inspect_dish("宫保鸡丁")  # Kung Pao Chicken
    inspector.inspect_dish("黄鱼烧年糕")