import requests
import os

REPO = "FAUSheppy/homelab_gamevault"
API_URL = f"https://api.github.com/repos/{REPO}/releases/latest"
VERSION_FILE = ".gamevault_version"

def get_latest_release():
    response = requests.get(API_URL)
    response.raise_for_status()
    data = response.json()
    version = data['tag_name']
    zip_url = data['zipball_url']
    return version, zip_url


def read_local_version():
    if not os.path.exists(VERSION_FILE):
        return None
    with open(VERSION_FILE, 'r') as f:
        return f.read().strip()

def update_updater():
    pass # TODO
    # download updater
    # replace updater

def execute_updater(new_version):
    # TODO
    # os.system(["updater.exe", new_version])
    pass