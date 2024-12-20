# Human: {question} Here are the options: {options} Assistant: If had to select one of the options, my answer would be (
import json
import os
import sys
sys.path.insert(0,"D:\\cs5787\\final\\dl_project\\FoodieQA\\rag\\wikipedia" )
sys.path.insert(0,"D:\\cs5787\\final\\dl_project\\FoodieQA\\rag\\baidu" )
print(sys.path)
from inspect_db import ChromaInspector



def read_sivqa(data_dir, file_name="sivqa_tidy.json"):
    question_file = os.path.join(data_dir, file_name)
    with open(question_file, 'r', encoding='utf-8') as f:
        sivqa = json.load(f)
    return sivqa

def read_dish_info(data_dir, file_name=""):
    dish_file = os.path.join(data_dir, file_name)
    data = []
    with open(dish_file, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line.strip()))
    return data
        

def format_choices(choices, template=0):
    idx2choice = {0:"A", 1:"B", 2:"C", 3:"D"}
    choices_str = ''
    for idx, choice in enumerate(choices):
        choices_str += "（{}) {}\n".format(idx2choice[idx], choice.strip())
    return choices_str

def format_question(question, lang="zh", show_food_name=False, use_web_img=False):
    if lang == "zh":
        q = question["question"].strip()
        choices = question["choices"]
    else:
        q = question["question_en"].strip()
        choices = question["choices_en"]
    
    if show_food_name:
        if lang == "zh":
            q = q.replace("图片中的食物", question["food_name"])
        else:
            q = q.replace("The food in the picture", question["food_name"])
    
    if use_web_img and "web_file" in question["food_meta"]:
        img = question["food_meta"]["web_file"]
    else:
        img = question["food_meta"]["food_file"]
    
    choices_str = format_choices(choices)
    
    return q, img, choices_str

def format_text_prompt(q, choices_str, template=0, lang="zh", food_name = "", predicted_food_names = [], full_response= ""):
    if lang == "zh":
        if template == 0:
            return "{} 选项有: {}, 请根据上图从所提供的选项中选择一个正确答案，为（".format(q, choices_str)
        if template == 1:
            return "你是一个人工智能助手，请你看图 回答以下选择题：{} 选项有: {}, 请从中选择一个正确答案，为（".format(q, choices_str)
        if template == 2:
            return ["你是一个智能助手，现在请看图回答以下选择题：{} 选项有: {}".format(q, choices_str), "我从所提供的选项中选择一个正确答案，为（"]
            # return "用户：你是一个智能助手，现在请看图回答以下选择题：{} 选项有: {}, 智能助手：我从所提供的选项中选择一个正确答案，为（".format(q, choices_str)
        if template == 3:
            return ["{} 这是选项: {} 请根据上图从所提供的选项中选择一个正确答案。".format(q, choices_str), "我选择（"]
        if template == 4:
            return ["{} 这是选项: {} 请根据上图从所提供的选项中选择一个正确答案。请保证你的答案清晰简洁并输出字母选项。".format(q, choices_str), "我选择（"]
            # return "用户：{} 这是选项: {} 请根据上图从所提供的选项中选择一个正确答案。智能助手：我选择（".format(q, choices_str)
        if template == 5:  # New RAG template
            def _format_rag_context(food_name):
                inspector = ChromaInspector()
                entries = inspector.get_dish_entries(food_name)
                if not entries:
                    return ""
                entry = entries[0]
                context = entry["content"]
                return "\n".join(context)
                
            context = _format_rag_context(food_name=food_name)
            return [
                f"根据以下内容：\n{context}\n问题：{q}\n选项：{choices_str}",
                "根据上下文和图片，我选择（"
            ]
        
        if template == 6:
            def _format_rag_context(food_name, json_db):
                """
                Format the context using data from the JSON database.
                :param food_name: Name of the food item to search for.
                :param json_db: The JSON database loaded as a dictionary.
                :return: Formatted context string.
                """
                # Attempt to find the dish by its name in the JSON keys
                entry = json_db.get(food_name)
                
                if not entry:
                    return "未找到与该食品名称相关的内容。"

                # Extract relevant fields from the entry
                dish_name = entry.get("dish_name", food_name)
                cuisine_type = entry.get("cuisine_type", "未知菜系")
                description = entry.get("description", "暂无描述。")
                ingredients = entry.get("ingredients", [])
                steps = entry.get("steps", [])
                url = entry.get("url", "无可用链接。")

                # Format the context
                context = "\n".join([
                    f"菜名: {dish_name}",
                    f"菜系: {cuisine_type}",
                    f"描述: {description if description else 'no descriptions'}",
                    f"配料: {', '.join(ingredients) if ingredients else 'no ingredients'}",
                    "步骤:",
                    "\n".join(steps) if steps else "no steps",
                    f"参考链接: {url}"
                ])
                return context

            # Load the JSON database (assuming it's already in memory or loaded previously)
            with open("rag\\baidu\\baidu_recipe_db\\all_recipes.json", "r", encoding="utf-8") as f:
                json_db = json.load(f)

            # Format the context for the given food name
            context = _format_rag_context(food_name=food_name, json_db=json_db)

            # Return the prompt for the VQA system
            return [
                f"根据以下内容：\n{context}\n问题：{q}\n选项：{choices_str}",
                "根据上下文和图片，我选择（"
            ]
        
        if template == 11:  # Visual Analysis Template
            return [
                """You are an AI assistant examining this dish visually. Question: {} 
            Options: {}

            Let me examine the image carefully for visual clues:

            1. Surface & Texture:
            - What's the outer appearance? (shiny/dry/crispy/soft)
            - Can I see any distinct textures? (rough/smooth/flaky)
            - Are there any visible layers or cross-sections?

            2. Colors & Ingredients:
            - What are the dominant colors?
            - Can I spot specific ingredients? (peppers/herbs/sauces)
            - Are there any characteristic garnishes?

            3. Presentation & State:
            - How is the dish arranged? (whole/pieces/mixed)
            - What cooking effects are visible? (charring/browning/steaming)
            - Are there any signature presentation elements?

            Looking at these visual elements and comparing to the options...""".format(q, choices_str),
                            "\nBased on these visible characteristics, I select ("
            ]
        
        if template == 100:
            def _format_wiki_context(food_name):
                inspector = ChromaInspector()
                entries = inspector.get_dish_entries(food_name)
                if not entries:
                    return ""
                entry = entries[0]
                context = entry["content"]
                return "\n".join(context)
            def _format_baidu_context(food_name, json_db):
                """
                Format the context using data from the JSON database.
                :param food_name: Name of the food item to search for.
                :param json_db: The JSON database loaded as a dictionary.
                :return: Formatted context string.
                """
                # Attempt to find the dish by its name in the JSON keys
                entry = json_db.get(food_name)
                
                if not entry:
                    return "未找到与该食品名称相关的内容。"

                # Extract relevant fields from the entry
                dish_name = entry.get("dish_name", food_name)
                cuisine_type = entry.get("cuisine_type", "未知菜系")
                description = entry.get("description", "暂无描述。")
                ingredients = entry.get("ingredients", [])
                steps = entry.get("steps", [])
                url = entry.get("url", "无可用链接。")

                # Format the context
                context = "\n".join([
                    f"菜名: {dish_name}",
                    f"菜系: {cuisine_type}",
                    f"描述: {description if description else 'no descriptions'}",
                    f"配料: {', '.join(ingredients) if ingredients else 'no ingredients'}",
                    "步骤:",
                    "\n".join(steps) if steps else "no steps",
                    f"参考链接: {url}"
                ])
                return context
            with open("rag\\baidu\\baidu_recipe_db\\all_recipes.json", "r", encoding="utf-8") as f:
                json_db = json.load(f)
            context = full_response
            for food_name in predicted_food_names:
                wiki_context = _format_wiki_context(food_name=food_name)
                baidu_context = _format_baidu_context(food_name=food_name, json_db=json_db)
                context.join(wiki_context)
                context.join(baidu_context)
            return [
                f"根据以下内容：\n{context}\n问题：{q}\n选项：{choices_str}",
                "根据上下文和图片，我选择（"]

            
            


        
    else:
        if template == 0:
            return "{} Here are the options: {} If had to select one of the options, my answer would be (".format(q, choices_str)
        if template == 1:
            return "You are an AI assistant. Please answer the following multiple choice question based on the image: {} Here are the options: {} Please select one of the options as your answer (".format(q, choices_str)
        if template == 2:
            return ["{} Here are the options: {}".format(q, choices_str), "If had to select one of the options, my answer would be ("] 
            # return "Human: {} Here are the options: {} Assistant: If had to select one of the options, my answer would be (".format(q, choices_str)
        if template == 3:
            return ["{} These are the options: {} Please select one of the options as your answer.".format(q, choices_str), "I would select ("]
            # return "Human: {} These are the options: {} Please select one of the options as your answer. Assistant: I would select (".format(q, choices_str)
        if template == 4:
            return [
                "{} These are the options: {} Looking at the image carefully, I will examine each detail before selecting an answer.".format(q, choices_str),
                "After careful consideration, I select ("
            ]
        if template == 5:
            return [
                "You are an AI assistant analyzing a food image. Question: {} Options: {}\n\nLet me break this down:\n1. Visual Characteristics:\n   - Appearance:\n   - Colors:\n   - Textures:\n2. Key Ingredients/Components:\n   - Main ingredients:\n   - Cooking method:\n3. Cultural/Regional Indicators:\n   - Presentation style:\n   - Distinctive features:\n\nNow evaluating each option based on these observations...".format(q, choices_str),
                "After careful analysis of these factors, I select ("
            ]
        if template == 6:
            return [
                "You are an AI assistant. Please answer the following multiple choice question based on the image. First, I'll identify what aspect this question is asking about (region, flavor, cuisine type, ingredients, presentation, or cooking skills). Question: {} Here are the options: {}".format(q, choices_str),
                "After analyzing the image according to the question type, I select ("
            ]
        
        if template == 7:
            question_guides = {
                "region": "I will examine regional cooking styles, ingredients, and presentation methods.",
                "flavor": "I will analyze visible ingredients, cooking methods, and seasoning indicators.",
                "cuisine_type": "I will look for characteristic cooking techniques and ingredient combinations.",
                "main-ingredient": "I will identify key visible ingredients in the dish.",
                "present": "I will focus on the visual presentation and arrangement.",
                "cooking-skills": "I will assess preparation methods and cooking techniques."
            }
            
            return [
                "You are an AI assistant. Please answer this food-related question: {} Options: {} First, I'll determine what aspect this question is focusing on by analyzing the question and its options. Then, I'll examine the image accordingly, paying special attention to ingredients, preparation methods, visual characteristics, and cultural indicators.".format(q, choices_str),
                "Based on my analysis, I select ("
            ]
        
        if template == 8:
            return "You are an AI assistant. Please identify the food in the picture first. Then, please answer the following multiple choice question based on the image: {} Here are the options: {} Please select one of the options as your answer (".format(q, choices_str)
        if template == 9:
            return [
                "You are an AI assistant. Let me first analyze the food in this image:\n\n1. Dish Identification:\n   - What type of dish this appears to be\n   - Key visible components\n   - Overall presentation\n\n2. Preparation Details:\n   - Cooking methods evident\n   - Level of complexity\n   - Notable techniques used\n\n3. Cultural/Regional Elements:\n   - Style of presentation\n   - Traditional indicators\n   - Regional characteristics\n\nNow, with this detailed understanding of the dish, let me address the question: {} \n\nThe options are: {}".format(q, choices_str),
                "Based on my analysis of the dish and the question at hand, I select ("
            ]
        if template == 10:  # Knowledge-based CoT template
            return [
                "You are analyzing a question about {}: {} Options: {}\n\nLet me think through this step by step:\n\n1. What is this dish?\n2. Where did it originate?\n3. What are its defining characteristics?\n4. How is it traditionally prepared?\n\nAnalyzing each option...".format(
                    "cuisine type" if "cuisine" in q.lower() else 
                    "regional origin" if "region" in q.lower() else 
                    "cooking methods" if "cook" in q.lower() else "food culture",
                    q, choices_str),
                "\nBased on this analysis, I select ("
            ]
        if template == 11:  # Visual Analysis Template
            return [
                """You are an AI assistant examining this dish visually. Question: {} 
            Options: {}

            Let me examine the image carefully for visual clues:

            1. Surface & Texture:
            - What's the outer appearance? (shiny/dry/crispy/soft)
            - Can I see any distinct textures? (rough/smooth/flaky)
            - Are there any visible layers or cross-sections?

            2. Colors & Ingredients:
            - What are the dominant colors?
            - Can I spot specific ingredients? (peppers/herbs/sauces)
            - Are there any characteristic garnishes?

            3. Presentation & State:
            - How is the dish arranged? (whole/pieces/mixed)
            - What cooking effects are visible? (charring/browning/steaming)
            - Are there any signature presentation elements?

            Looking at these visual elements and comparing to the options...""".format(q, choices_str),
                            "\nBased on these visible characteristics, I select ("
            ]
        if template == 12:
            return "You are a helpful chef AI assistant. Please answer the following multiple choice question based on the image: {} Here are the options: {} Please look carefully at the dish and all of the ingredients and composition, and think carefully before you select one of the options as your answer (".format(q, choices_str)
        if template == 13:
            return "You are a helpful chef AI assistant. Please answer the following multiple choice question based on the image: {} Here are the options: {} Please look carefully at the dish and list out all of the ingredients, and think carefully step-by-step against all posible options before you select one of the options as your answer (".format(q, choices_str)
        if template == 14:
            return [
                """You are a helpful chef AI assistant. Please analyze the following question about the food image:
                Question: {}
                Options: {}
                
                Please follow these steps:
                1. List all visible ingredients and components in the dish
                2. Think carefully about each option step-by-step
                3. Explain your reasoning
                4. End your response with 'Final Answer: [X]' where X is your chosen option (A, B, C, or D)""".format(q, choices_str),
                "Let me analyze the image and provide my answer..."
            ]

def get_prompt_qwen(question, data_dir, show_food_name=False, use_web_img=False, template=0, lang="zh"):
    # for qwen model
    q, img, choices_str = format_question(question, lang=lang, show_food_name=show_food_name, use_web_img=use_web_img)

    query_list = [{"image": os.path.join(data_dir, img)}]
    text_prompt = format_text_prompt(q, choices_str, template, lang=lang)
    if isinstance(text_prompt, list):
        if lang == "zh":
            query_list.append({"text": "用户："+ text_prompt[0] + "智能助手："+ text_prompt[1]})
        else:
            query_list.append({"text": "Human: "+ text_prompt[0] + "Assistant: "+ text_prompt[1]})
    else:
        query_list.append({"text": format_text_prompt(q, choices_str, template, lang=lang)})

    return query_list

def get_prompt_phi(question, data_dir, show_food_name=False, template=0, lang="zh"):
    # for qwen model
    q, img, choices_str = format_question(question, lang=lang, show_food_name=show_food_name)

    text_prompt = format_text_prompt(q, choices_str, template, lang=lang)
    query_list = []
    if isinstance(text_prompt, list):
        query_list.append({"role": "user", "content": "<|image_1|>\n" + text_prompt[0]})
        query_list.append({"role": "assistant", "content": text_prompt[1]})
    else:
        query_list.append({"role": "user", "content": "<|image_1|>\n" + text_prompt})

    return query_list


def get_prompt_idefics(question, data_dir, show_food_name=False, template=0, lang="zh"):
    # for both idefics2 and mantis
    q, img, choices_str = format_question(question, lang=lang, show_food_name=show_food_name)
    text_prompt = format_text_prompt(q, choices_str, template, lang=lang)
    if isinstance(text_prompt, list):
        query_list = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "image", "image": os.path.join(data_dir, img)},
                            {"type": "text", "text": text_prompt[0]}
                        ]
                    },
                    {
                        "role": "assistant",
                        "content": [
                            {"type": "text", "text": text_prompt[1]}
                        ]
                    }
                ]
    else:
        query_list = [
                        {
                            "role": "user",
                            "content": [
                                {"type": "image"},
                                {"type": "text", "text": text_prompt},
                            ]}
                        ]
    return query_list

def find_dish_info(dish_info, q_id):
    for item in dish_info:
        if item.get("question_id") == q_id:
            predicted_dishes = item.get("predicted_dishes", [])
            full_response = item.get("full_response", "")
            return predicted_dishes, full_response



'''
        if template == 5:  # New RAG template
            def _format_rag_context(food_name):
                inspector = ChromaInspector()
                entries = inspector.get_dish_entries(food_name)
                if not entries:
                    return ""
                entry = entries[0]
                aspects = ['cuisine_type', 'flavor', 'region', 'main_ingredient', 'cooking_skills']
                context = []
                for aspect in aspects:
                    info = inspector.extract_info(entry['content'], aspect)
                    if info:
                        context.append(f"{aspect}: {'; '.join(info)}")
                return "\n".join(context)
                
            context = _format_rag_context(q.get("food_name", ""))
            return [
                f"Based on this context:\n{context}\nQuestion: {q}\nOptions: {choices_str}",
                "Based on the context and image, I select ("
            ]
        '''