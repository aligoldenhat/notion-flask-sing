import requests
import os, json

file_path = os.path.join(os.path.dirname(__file__), f'info.json')
with open(file_path, 'r') as f:
    data = json.load(f)

GITHUB_TOKEN = data['github']['token']
GITHUB_OWNER = data['github']['owner']
GITHUB_REPO = data['github']['repo']

def get_config_from_github(path):
    r = requests.get(
        f'https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{path}',
        headers={
            'accept': 'application/vnd.github.v3.raw',
            'authorization': f'token {GITHUB_TOKEN}'
                }
        )
    text =  r.text
    if 'Not Found' in text:
        return 'Not Found'
    else:
        return text

