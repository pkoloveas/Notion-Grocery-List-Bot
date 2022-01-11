import os
import requests
import re
import json
import pandas as pd


class NotionService:

    def __init__(self) -> None:
        pass

    def setup_settings(self) -> None:
        self.api_key: str = os.getenv('NOTION_API_KEY')
        self.db_id: str = os.getenv('NOTION_DATABASE_ID')
        self.URL_HEADERS = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2021-08-16"
        }

    def query_db(self) -> object:
        headers = self.URL_HEADERS

        payload = {
            'filter': {
                'property': 'Buy',  # Column name
                'checkbox': {
                    'equals': True
                }
            }
        }
        response = requests.post('https://api.notion.com/v1/databases/{}/query'.format(self.db_id), headers=headers, json=payload)

        if not response.ok:
            raise NotionServiceException(response.json())

        return response.json()['results']

    def get_grocery_list(self) -> list:

        rows = self.query_db()

        data = []
        grocery_list = []

        for row in rows:
            for property_key in row['properties']:
                prop = row['properties'][property_key]
                if prop['type'] == 'title':
                    product = ''.join([t['plain_text'] for t in prop['title']])
                if prop['type'] == 'rich_text':
                    if len(prop['rich_text']) == 0:
                        quantity = ''
                    else:
                        quantity = ''.join([t['plain_text'] for t in prop['rich_text']])
                if prop['type'] == 'select':
                    category = ''.join(prop['select']['name'])
            data.append([product, quantity, category])

        df_grouped_by_category = pd.DataFrame.from_records(data, columns=["Product", "Quantity", "Category"]).groupby("Category")

        for category in list(df_grouped_by_category.groups.keys()):
            group = df_grouped_by_category.get_group(category).values.tolist()
            grocery_list.append("--------------------------------------------")
            grocery_list.append(category)
            grocery_list.append("--------------------------------------------")
            for item in group:
                grocery_list.append(' '.join([item[0], item[1]]))
            grocery_list.append(" ")

        return grocery_list


class NotionServiceException(Exception):
    pass
