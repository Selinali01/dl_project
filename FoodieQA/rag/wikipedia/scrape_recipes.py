from wiki_recipe_scraper import WikiRecipeScraper

# Your dishes_by_cuisine dictionary
dishes_by_cuisine = {
    "新疆菜": [
        "烤羊肉串",
        "馕",
        "羊肉抓饭",
        "大盘鸡",
    ],
    "川菜（四川，重庆）": [
        "辣子鸡丁",
        "水煮肉片",
        "宫保鸡丁",
        "回锅肉",
    ],
    "粤菜（广东等地）": [
        "叉烧包",
        "虾饺",
        "煲仔饭",
    ],
    # Add more as needed...
}

def main():
    scraper = WikiRecipeScraper()
    
    # Clear the database if needed
    scraper.clear_database()
    
    # Scrape and store recipes
    scraper.scrape_and_store_recipes(dishes_by_cuisine)

if __name__ == "__main__":
    main()