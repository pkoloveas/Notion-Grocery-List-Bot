import requests
import json
import os
import pandas as pd
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

NOTION_TOKEN = os.getenv('NOTION_SECRET', '')
DATABASE_ID = os.getenv('DATABASE_ID', '')


def query_filter(notion_id: str):

    payload = {
        'filter':
            {
                'property': 'Buy',  # Column name
                'checkbox': {
                    'equals': True
                }
            }
    }

    response = requests.post('https://api.notion.com/v1/databases/{}/query'.format(notion_id), json=payload, headers={
        'Authorization': 'Bearer ' + NOTION_TOKEN, 'Notion-Version': '2021-08-16'})

    # If the request was not successful, we print the error and return
    if not response.ok:
        print('Error:', response.status_code)
        print('Error:', response.content)
        return

    # Parse the response as JSON
    data = response.json()

    # If you want to see the complete response, uncomment the following line
    # print(json.dumps(data, indent=4))

    return data['results']


if __name__ == "__main__":

    database_id = DATABASE_ID

    # Call function to query the database
    rows = query_filter(database_id)

    # Something failed
    if rows is None:
        exit(1)

    # with open('data.json', 'w', encoding='utf-8') as f:
    #     json.dump(rows, f, ensure_ascii=False, indent=4)

    data = []

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
        print("--------------------------------------------")
        print(category)
        print("--------------------------------------------")
        for item in group:
            print(item[0], item[1])
        print()
