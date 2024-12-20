import chromadb
from chromadb.utils import embedding_functions
import json
import os
from typing import List, Dict, Optional
from datetime import datetime

class LocalRecipeDB:
    def __init__(self, persist_dir: str = "./recipe_db"):
        """Initialize the local recipe database"""
        os.makedirs(persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name="chinese_recipes",
            embedding_function=self.embedding_fn,
            metadata={"description": "Chinese recipe database"}
        )
    
    def _prepare_metadata(self, metadata: Dict) -> Dict:
        """Convert metadata to Chroma-compatible format"""
        processed_metadata = {}
        for key, value in metadata.items():
            # Convert lists to comma-separated strings
            if isinstance(value, list):
                processed_metadata[key] = ", ".join(str(v) for v in value)
            # Convert all other values to strings
            else:
                processed_metadata[key] = str(value)
        return processed_metadata
    
    def add_recipe(self, 
                   content: str, 
                   metadata: Optional[Dict] = None,
                   source: Optional[str] = None) -> str:
        """Add a single recipe to the database"""
        doc_id = f"recipe_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Prepare metadata
        meta = {
            "timestamp": datetime.now().isoformat(),
            "source": source or "unknown"
        }
        if metadata:
            meta.update(self._prepare_metadata(metadata))
            
        # Add to collection
        self.collection.add(
            documents=[content],
            metadatas=[meta],
            ids=[doc_id]
        )
        
        return doc_id
    
    def search_recipes(self, 
                      query: str, 
                      n_results: int = 3) -> List[Dict]:
        """Search for recipes similar to the query"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        formatted_results = []
        for i in range(len(results['documents'][0])):
            # Convert string back to list for main_ingredients
            metadata = results['metadatas'][0][i]
            if 'main_ingredients' in metadata:
                metadata['main_ingredients'] = [
                    ing.strip() 
                    for ing in metadata['main_ingredients'].split(',')
                ]
                
            formatted_results.append({
                'content': results['documents'][0][i],
                'metadata': metadata,
                'distance': results['distances'][0][i]
            })
            
        return formatted_results
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        return {
            "total_recipes": self.collection.count(),
            "peek": self.collection.peek()
        }