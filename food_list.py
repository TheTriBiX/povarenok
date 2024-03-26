from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import json


class RecipePage:
    def __init__(self, url: str):
        self.url = url
        self.soup = BeautifulSoup(requests.get(url).text, 'lxml')
        self.name = self.soup.find('h1').text
        self.ingredients = self.get_ingredients()
        self.pfc = self.get_pfc()
        self.recipe = self.get_recipe()

    def get_ingredients(self) -> Dict[str, str]:
        ingredients = {}
        for i in self.soup.find_all('li', itemprop='recipeIngredient'):
            ingr = list(map(lambda x: x.text, i.find_all('span')))
            ingredients[ingr[0]] = None if len(ingr) < 2 else ingr[-1]
        return ingredients if ingredients else {self.url: 'ingredients not found'}

    def get_recipe(self) -> Dict[str, Dict[str, str]]:
        recipe = {}
        for count, step in enumerate(self.soup.find_all(name='li', class_='cooking-bl'), start=1):
            img = step.find('a')
            text = step.find('p').text
            recipe[f'step {count}.'] = {'img': img['href'], 'text': text}
        return recipe if recipe else {self.url: 'recipe not found'}

    def get_main_image(self) -> str:
        image_tag = self.soup.find('img', {
            'class': 'm-img'})  # замените 'your-image-class' на реальный класс изображения
        return image_tag['src'] if image_tag else None

    def get_pfc(self) -> Dict[str, str]:
        return {
            'calories': self.soup.find(itemprop='calories'),
            'protein': self.soup.find(itemprop='proteinContent'),
            'fat': self.soup.find(itemprop='fatContent'),
            'carbohydrate': self.soup.find(itemprop='carbohydrateContent')
        }

    def get_json(self) -> str:
        return json.dumps({self.url: {'name': self.name, 'ingredients': self.ingredients, 'recipe': self.recipe}},
                          ensure_ascii=False).encode('utf8').decode()

    def get_mongo_dict(self) -> dict:
        return {'_id': {'url': self.url, 'name': self.name}, 'ingredients': self.ingredients, 'recipe': self.recipe}


class MainPage:
    def __init__(self, url: str):
        self.url = url

    def get_recipe_list(self, count: int) -> List[str]:
        url_list = []
        for i in range(count):
            soup = BeautifulSoup(requests.get(fr'{self.url}/~{i}/').text, 'lxml')
            items = soup.find_all(class_='item-bl', name='article')
            url_list.extend([item.find(name='a')['href'] for item in items])
        return url_list
