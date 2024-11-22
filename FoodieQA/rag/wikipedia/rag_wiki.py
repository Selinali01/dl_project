from recipe_db import LocalRecipeDB
import json
from typing import Dict, List, Tuple
import re

class ChromaInspector:
    def __init__(self):
        self.db = LocalRecipeDB()
        
    def extract_info_by_question_type(self, query: Dict) -> Tuple[str, List[str]]:
        """
        Extract relevant search terms and keywords based on question type
        Returns: (search_query, relevant_content_patterns)
        """
        question_type = query.get("question_type")
        food_name = query.get("food_name")
        choices = query.get("choices", [])
        
        search_terms = []
        content_patterns = []
        
        if question_type == "cuisine_type":
            # Look for cuisine type mentions
            search_terms = [food_name, "cuisine", "菜系"]
            content_patterns = [
                r"Cuisine Type:\s*(.*)",
                r"菜系:\s*(.*)",
                r"cuisine of",
                food_name
            ]

        elif question_type == "region":
            # Look for regional information
            search_terms = [food_name, "region", "origin", "provincial"]
            content_patterns = [
                r"found in the cuisines of(.*?)\.",
                r"originated in(.*?)\.",
                r"traditional dish from(.*?)\.",
                food_name
            ]

        elif question_type == "flavor":
            # Look for flavor descriptions
            search_terms = [food_name, "taste", "flavor", "texture"]
            content_patterns = [
                r"characterized by(.*?)\.",
                r"flavored with(.*?)\.",
                r"tastes(.*?)\.",
                food_name
            ]

        elif question_type == "presentation":
            # Look for serving and presentation details
            search_terms = [food_name, "served", "presented", "accompanies"]
            content_patterns = [
                r"served with(.*?)\.",
                r"presented(.*?)\.",
                r"accompanied by(.*?)\.",
                food_name
            ]

        elif question_type == "cooking_skills":
            # Look for cooking methods and techniques
            search_terms = [food_name, "prepared", "cooked", "method"]
            content_patterns = [
                r"prepared by(.*?)\.",
                r"cooked(.*?)\.",
                r"method includes(.*?)\.",
                food_name
            ]

        elif question_type == "main_ingredient":
            # Look for main ingredients
            search_terms = [food_name, "made with", "ingredients", "contains"]
            content_patterns = [
                r"main ingredients?(.*?)\.",
                r"made with(.*?)\.",
                r"contains(.*?)\.",
                food_name
            ]

        search_query = " ".join(search_terms)
        return search_query, content_patterns

    def extract_relevant_content(self, content: str, patterns: List[str]) -> str:
        """Extract relevant portions of content based on patterns"""
        relevant_parts = []
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                if match.groups():
                    relevant_parts.append(match.group(1).strip())
                else:
                    # If no capture group, get the context around the match
                    start = max(0, match.start() - 50)
                    end = min(len(content), match.end() + 50)
                    relevant_parts.append(content[start:end].strip())
                    
        return "\n".join(relevant_parts) if relevant_parts else ""

    def answer_question(self, query: Dict) -> Dict:
        """
        Answer a specific question using the database
        Returns: {
            'answer': str,
            'evidence': str,
            'confidence': float
        }
        """
        search_query, content_patterns = self.extract_info_by_question_type(query)
        
        # Search the database
        results = self.db.search_recipes(search_query, n_results=3)
        
        evidence = []
        for result in results:
            relevant_content = self.extract_relevant_content(
                result['content'], 
                content_patterns
            )
            if relevant_content:
                evidence.append({
                    'content': relevant_content,
                    'distance': result['distance'],
                    'metadata': result['metadata']
                })
        
        return {
            'question': query['question'],
            'food_name': query['food_name'],
            'question_type': query['question_type'],
            'choices': query['choices'],
            'evidence': evidence
        }

    def get_all_entries(self) -> List[Dict]:
        """Retrieve all entries from the database"""
        # Get all IDs from the collection
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
    
    def print_database_contents(self):
        """Print a formatted view of all database contents"""
        entries = self.get_all_entries()
        
        print(f"\n=== Database Contents ({len(entries)} entries) ===\n")
        
        for i, entry in enumerate(entries, 1):
            print(f"\n--- Entry {i} ---")
            print(f"ID: {entry['id']}")
            print("\nMetadata:")
            for key, value in entry['metadata'].items():
                print(f"  {key}: {value}")
            print("\nContent Preview:")
            # Print first 100000 characters of content
            content_preview = entry['content'][:100000] + "..." if len(entry['content']) > 100000 else entry['content']
            print(f"  {content_preview}")
            print("\n" + "="*50)
    
    def search_database(self, query: str, n_results: int = 3):
        """Search the database and show results"""
        results = self.db.search_recipes(query, n_results)
        
        print(f"\n=== Search Results for '{query}' ===\n")
        
        for i, result in enumerate(results, 1):
            print(f"\n--- Result {i} (Distance: {result['distance']:.4f}) ---")
            print("\nMetadata:")
            for key, value in result['metadata'].items():
                print(f"  {key}: {value}")
            print("\nContent Preview:")
            content_preview = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
            print(f"  {content_preview}")
            print("\n" + "="*50)
    
    def export_to_json(self, filename: str = "recipe_db_dump.json"):
        """Export the entire database to a JSON file"""
        entries = self.get_all_entries()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
        
        print(f"\nDatabase exported to {filename}")

def main():
    inspector = ChromaInspector()
    
    # Example question
    ''''
    test_question = {
        "question": "图片中的食物通常属于哪个菜系?",
        "choices": ["京菜", "徽菜", "新疆菜", "桂菜"],
        "question_type": "cuisine_type",
        "food_name": "烤羊肉串"
    }
    '''
    test_question = {
    "question": "这道菜的口味特点是什么?",
    "question_type": "flavor",
    "food_name": "水煮鱼",
    "choices": ["清淡", "麻辣", "咸鲜", "酸甜"]
}
    # Get answer
    result = inspector.answer_question(test_question)
    print("\nQuestion Analysis:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()