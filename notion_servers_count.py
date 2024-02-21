import requests
import json, os, logging
from datetime import datetime


file_path = os.path.join(os.path.dirname(__file__), f'info.json')
with open(file_path, 'r') as f:
    data = json.load(f)

NOTION_TOKEN = data["notion_api"]["notion_token"]
DATABASE_ID = data["notion_api"]["database_id"]

headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "accept": "application/json",
    "Notion-Version": "2022-06-28",
    "content-type": "application/json"
}

def get_page(id):
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

    payload = {"filter": {"property": "ID", "rich_text": {"contains": id}}}
    response = requests.post(url, json=payload, headers=headers)

    data = response.json()
    results = data["results"]
    if results:
        results = results[0]

    return results

def which_conf(page):
    if page:
        return page['properties']['conf']['select']['name']

def any_count(page):
    try:
        if page['properties']['count']['number'] > 0:
            return True
        else:
            return False
    except TypeError:
        return False
    

def reduce_and_try_date(page, succ, id, conf):
    page_id = page['id']
    url = f"https://api.notion.com/v1/pages/{page_id}"

    try:
        previous_succ_try = page["properties"]["latest_try"]["date"]["start"]
        add_difference = True

        now = datetime.today()
        previous_datetime_object = datetime.strptime(previous_succ_try, '%Y-%m-%dT%H:%M:%S.000+03:30')
        difference = str(now - previous_datetime_object).split(".")[0]
        now = now.strftime('%Y-%m-%dT%H:%M:%S.000+03:30')

    except TypeError:
        add_difference = False
        now = datetime.today().strftime('%Y-%m-%dT%H:%M:%S.000+03:30')


    if add_difference:
        if succ:
            reduced_count = page['properties']['count']['number'] - 1
            updated_count = {'latest_try': {'date': {'start': now}},
                             'succ_try': {'checkbox': True}, 
                             'time_difference': {'rich_text': [{'text': {'content': difference}}]}, 
                             'count': {'number': reduced_count}}
        else:
            updated_count = {'latest_try': {'date': {'start': now}},
                             'time_difference': {'rich_text': [{'text': {'content': difference}}]},
                             'succ_try': {'checkbox': False}}
    else:
        if succ:
            reduced_count = page['properties']['count']['number'] - 1
            updated_count = {'latest_try': {'date': {'start': now}}, 'succ_try': {'checkbox': True}, 'count': {'number': reduced_count}}
        else:
            updated_count = {'latest_try': {'date': {'start': now}}, 'succ_try': {'checkbox': False}}

    payload = {"properties": updated_count}

    count_patch_request = 0
    while True:
        count_patch_request += 1
        res = requests.patch(url, json=payload, headers=headers)
        if res.status_code == 200 or count_patch_request == 10:
            break
    
    logging.info(f"NotionID: {id} {conf} {res} - Reduce: {succ} - TryDate: {True} - CountRequests: {count_patch_request}")
