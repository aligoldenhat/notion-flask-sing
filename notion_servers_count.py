import requests
import json, os


file_path = os.path.join(os.path.dirname(__file__), f'info.json')
with open(file_path, 'r') as f:
    data = json.load(f)

NOTION_TOKEN = data['notion_token']
DATABASE_ID = data['database_id']

headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "accept": "application/json",
    "Notion-Version": "2022-06-28",
    "content-type": "application/json"
}


def get_pages(num_pages=None):
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages

    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=headers)

    data = response.json()
    results = data["results"]

    return results


def find_id(id, pages):
    for page in pages:
        try:
            if page['properties']['ID']['rich_text'][0]['plain_text'] == id:
                return page
        except IndexError:
            pass

def which_server(page):
    if page:
        return page['properties']['server']['select']['name']

def any_count(page):
    try:
        if page['properties']['count']['number'] > 0:
            return True
        else:
            return False
    except TypeError:
        return False
    
def reduce_count(page):
    page_id = page['id']
    url = f"https://api.notion.com/v1/pages/{page_id}"

    reduced_count = page['properties']['count']['number'] - 1
    updated_count = {'count': {'number': reduced_count}}

    payload = {"properties": updated_count}

    while True:
        res = requests.patch(url, json=payload, headers=headers)
        print ("Notion: ReduceValue:", res)
        if res == "<Response [200]>":
            break

def add_one_try(page):
    page_id = page['id']
    url = f"https://api.notion.com/v1/pages/{page_id}"

    one_more_try = page['properties']['try']['number'] + 1
    updated_count = {'try': {'number': one_more_try}}

    payload = {"properties": updated_count}

    res = requests.patch(url, json=payload, headers=headers)
    print ("Notion: OneMoreTry:", res)

