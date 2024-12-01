# Human: {question} Here are the options: {options} Assistant: If had to select one of the options, my answer would be (
import json
import os
import sys
sys.path.insert(0,"C:\\Users\\choyd\cs5787\\final\\dl_project\\FoodieQA\\rag\\wikipedia" )
sys.path.insert(0,"C:\\Users\\choyd\cs5787\\final\\dl_project\\FoodieQA\\rag\\baidu" )
print(sys.path)
from inspect_db import ChromaInspector



def read_sivqa(data_dir, file_name="sivqa_tidy.json"):
    question_file = os.path.join(data_dir, file_name)
    with open(question_file, 'r', encoding='utf-8') as f:
        sivqa = json.load(f)
    return sivqa

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
    food_name = question["food_name"]
    
    return q, img, choices_str, food_name

def format_text_prompt(q, choices_str, template=0, lang="zh", food_name = ""):
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
                # aspects = ['cuisine_type', 'flavor', 'region', 'main_ingredient', 'cooking_skills']
                # context = []
                # for aspect in aspects:
                #     info = inspector.extract_info(entry['content'], aspect)
                #     if info:
                #         context.append(f"{aspect}: {'; '.join(info)}")
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
            with open("C:\\Users\\choyd\\cs5787\\final\\dl_project\\FoodieQA\\rag\\baidu\\baidu_recipe_db\\all_recipes.json", "r", encoding="utf-8") as f:
                json_db = json.load(f)

            # Format the context for the given food name
            context = _format_rag_context(food_name=food_name, json_db=json_db)

            # Return the prompt for the VQA system
            return [
                f"根据以下内容：\n{context}\n问题：{q}\n选项：{choices_str}",
                "根据上下文和图片，我选择（"
            ]

        
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
        if template == 5:  # New RAG template
            def _format_rag_context(food_name):
                inspector = ChromaInspector()
                entries = inspector.get_dish_entries(food_name)
                if not entries:
                    return ""
                entry = entries[0]
                # aspects = ['cuisine_type', 'flavor', 'region', 'main_ingredient', 'cooking_skills']
                # context = []
                # for aspect in aspects:
                #     info = inspector.extract_info(entry['content'], aspect)
                #     if info:
                #         context.append(f"{aspect}: {'; '.join(info)}")
                context = entry["content"]
                return "\n".join(context)
                
            context = _format_rag_context(food_name=food_name)
            return [
                f"Based on this context:\n{context}\nQuestion: {q}\nOptions: {choices_str}",
                "Based on the context and image, I select ("
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