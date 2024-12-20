import requests
import torch
from PIL import Image
from io import BytesIO
import yaml
import os
import json
from tqdm import tqdm 
from transformers import AutoProcessor, AutoModelForVision2Seq
from transformers.image_utils import load_image
from FoodieQA.rag.wikipedia.recipe_db import LocalRecipeDB
import utils
import argparse

class FoodieQARAG:
    def __init__(self, cache_dir="/scratch/project/dd-23-107/wenyan/cache"):
        self.db = LocalRecipeDB()
        self.processor = AutoProcessor.from_pretrained("HuggingFaceM4/idefics2-8b", 
                                                     cache_dir=cache_dir, 
                                                     do_image_splitting=False)
        self.model = AutoModelForVision2Seq.from_pretrained(
            "HuggingFaceM4/idefics2-8b", 
            cache_dir=cache_dir,
            device_map="auto", 
            torch_dtype=torch.float16
        )

    def retrieve_context(self, question, n_results=2):
        """Retrieve relevant context based on the question"""
        # Extract dish name and question type
        dish_name = question.get('food_name', '')
        question_type = question.get('question_type', '')
        
        # Construct search query based on question type
        search_queries = []
        if dish_name:
            search_queries.append(dish_name)
            
        if question_type == "cuisine_type":
            search_queries.append(f"{dish_name} cuisine origin traditional")
        elif question_type == "flavor":
            search_queries.append(f"{dish_name} taste flavor characteristics")
        elif question_type == "cooking-skills":
            search_queries.append(f"{dish_name} cooking preparation method")
        elif question_type == "region-2":
            search_queries.append(f"{dish_name} regional origin location")
            
        # Get results
        context = ""
        for query in search_queries:
            results = self.db.search_recipes(query, n_results=n_results)
            for result in results:
                context += f"\n相关信息 (Related Information):\n{result['content']}\n"
                
        return context.strip()

    def format_image_input(self, img_idx, template=0):
        idx2choice = {0: "A", 1: "B", 2: "C", 3: "D"}
        if template == 0:
            img_input = {
                "role": "user",
                "content": [{"type": "image"}]
            }
        if template == 1:
            img_input = {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": "图"+idx2choice[img_idx]},
                ]
            }
        if template == 2:
            img_input = {
                "role": "user",
                "content": [
                    {"type": "text", "text": "图"+idx2choice[img_idx]},
                    {"type": "image"},
                ]
            }
        return img_input

    def format_text_input(self, question, context, template=0, add_prompt_general=False):
        q = question["question"]
        if template == 0:
            if "以下" in q:
                q = q.replace("以下", "以上")
            
            text_prompt = f"""根据以上四张图和以下相关信息回答问题:

{context}

他们分别为图A, 图B, 图C, 图D.
{"请从给定选项ABCD中选择一个最合适的答案。" if add_prompt_general else ""}
问题：{q}, 答案为：图"""
            
            text_input = {
                "role": "user",
                "content": [{"type": "text", "text": text_prompt}]
            }
            
        # Add other template formats as needed...
        return text_input

    def build_input(self, mivqa, idx, prompt=0, add_prompt_general=False):
        messages = []
        question = mivqa[idx]
        images = [load_image(os.path.join(data_dir, img)) for img in question["images"]]
        
        # Retrieve relevant context
        context = self.retrieve_context(question)
        
        if prompt == 0 or prompt == 1:
            for i in range(4):
                img_input = self.format_image_input(i, template=prompt)
                messages.append(img_input)
            text_input = self.format_text_input(question, context, template=prompt, 
                                              add_prompt_general=add_prompt_general)
            messages.append(text_input)
            
        # Add other prompt formats as needed...
        return messages, images

    def eval_question(self, mivqa, idx, prompt, add_prompt_general=False):
        messages, images = self.build_input(mivqa, idx, prompt=prompt, 
                                          add_prompt_general=add_prompt_general)
        prompt = self.processor.apply_chat_template(messages, add_generation_prompt=True)
        inputs = self.processor(text=prompt, images=images, return_tensors="pt")
        inputs = {k: v.to() for k, v in inputs.items()}
        generated_ids = self.model.generate(**inputs, max_new_tokens=500)
        generated_texts = self.processor.batch_decode(generated_ids, skip_special_tokens=True)
        return {
            "response": generated_texts,
            "qid": mivqa[idx]["qid"]
        }

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--cache_dir", default="/scratch/project/dd-23-107/wenyan/cache")
    argparser.add_argument("--data_dir", default="/scratch/project/dd-23-107/wenyan/data/foodie")
    argparser.add_argument("--eval_file", default="mivqa_filtered.json")
    argparser.add_argument("--prompt", type=int, default=3)
    argparser.add_argument("--out_dir", default="/scratch/project/dd-23-107/wenyan/data/foodie/results")
    args = argparser.parse_args()

    # Initialize the RAG-enhanced QA system
    qa_system = FoodieQARAG(cache_dir=args.cache_dir)
    
    # Read data
    data_dir = args.data_dir
    mivqa = utils.read_mivqa(data_dir, args.eval_file)
    
    # Setup output
    out_file_name = f"mivqa_idefics2-8b_rag_prompt{args.prompt}.jsonl"
    os.makedirs(args.out_dir, exist_ok=True)
    
    print(f"Evaluating model on {len(mivqa)} questions")
    with open(os.path.join(args.out_dir, out_file_name), "w") as f:
        for i in tqdm(range(len(mivqa))):
            res = qa_system.eval_question(mivqa, i, prompt=args.prompt, 
                                        add_prompt_general=True)
            f.write(json.dumps(res, ensure_ascii=False)+"\n")
            
    print(f"Saved model response to {out_file_name}, Calculate accuracy")
    accuracy = utils.get_accuracy(os.path.join(args.out_dir, out_file_name), 
                                mivqa, parse_fn=utils.parse_idefics)

if __name__ == "__main__":
    main()