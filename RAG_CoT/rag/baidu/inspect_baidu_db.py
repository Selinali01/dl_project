from recipe_db import LocalRecipeDB
import json
from typing import Dict, List

class BaiduInspector:
    def __init__(self):
        self.db = LocalRecipeDB("./baidu_recipe_db")
        self.patterns = {
            'cuisine_type': {
                'keywords': ['菜系', '传统', '起源'],
                'patterns': [
                    r'属于([^，。]+)菜系',
                    r'是([^，。]+)的传统名菜',
                ]
            },
            'flavor': {
                'keywords': ['口味', '味道', '特色', '风味'],
                'patterns': [
                    r'具有([^，。]+)的口味',
                    r'以([^，。]+)为特色',
                ]
            },
            # ... (similar patterns as ChromaInspector but adapted for Chinese text)
        }

    # ... (rest of the methods similar to ChromaInspector)