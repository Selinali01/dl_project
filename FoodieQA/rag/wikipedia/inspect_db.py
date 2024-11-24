from recipe_db import LocalRecipeDB
import json
from typing import Dict, List

class ChromaInspector:
    def __init__(self):
        self.db = LocalRecipeDB()
    
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

    def get_dish_entries(self, food_name: str) -> List[Dict]:
        """Search the database for entries matching a specific food name."""
        entries = self.get_all_entries()
        matches = [entry for entry in entries if entry['metadata'].get('dish_name') == food_name]
        print(matches)
        
        if matches:
            print(f"\n=== Entries Matching Food Name '{food_name}' ===\n")
            for i, match in enumerate(matches, 1):
                print(f"\n--- Match {i} ---")
                print(f"ID: {match['id']}")
                print("\nMetadata:")
                for key, value in match['metadata'].items():
                    print(f"  {key}: {value}")
                print("\nContent Preview:")
                content_preview = match['content'][:200] + "..." if len(match['content']) > 200 else match['content']
                print(f"  {content_preview}")
                print("\n" + "="*50)
        else:
            print(f"No entries found for food name: {food_name}")
        
        return matches
    
    def export_to_json(self, filename: str = "recipe_db_dump.json"):
        """Export the entire database to a JSON file"""
        entries = self.get_all_entries()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
        
        print(f"\nDatabase exported to {filename}")

if __name__ == "__main__":
    inspector = ChromaInspector()
    
    # Print all contents
    inspector.print_database_contents()
    
    # Example search
    print("\nPerforming example searches:")
    inspector.search_database("Sichuan spicy dishes")
    
    # Export to JSON
    inspector.export_to_json()