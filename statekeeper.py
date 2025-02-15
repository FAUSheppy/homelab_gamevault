import requests
import os
import sqlalchemy
import threading
from db import db, Download
from sqlalchemy import or_, and_

def add_to_download_queue(url, path):
    '''The download is added to the global queue and downloaded eventually'''
    #_download(url, path)
    thread = threading.Thread(target=_download, args=(url, path))
    thread.start()

def add_to_task_queue(task):
    '''Add a callback to background execution queue'''
    #print("Executing tasks", task)
    thread = threading.Thread(target=task)
    thread.start()
    #task()

def _download(url, path):

    response = requests.get(url + "?path=" + path, stream=True)

    # Check if the request was successful
    if response.status_code == 200:

        # Save the file locally
        local_filename = os.path.join("./cache", path)

        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):  # Download in chunks
                f.write(chunk)

        print(f"File downloaded successfully as {local_filename}")
    
    else:

        raise AssertionError("Non-200 Response for:", url, path, response.status_code, response.text)

def log_begin_download(path):

    session = db.session()
    print("Current path", path)
    path_exists = session.query(Download).filter(and_(Download.path==path, Download.finished==False)).first()
    if path_exists:
        print("DAFUG", path_exists)
        print("WTF", path_exists.path)
        raise AssertionError("ERROR: {} is already downloading.".format(path))
    else:
        print("Adding to download log:", path)
        session.merge(Download(path=path, size=0, type="download", finished=False))
        session.commit()

    db.close_session()

def log_end_download(path):

    session = db.session()
    path_exists = session.query(Download).filter(Download.path==path).first()
    if not path_exists:
        raise AssertionError("ERROR: {} is not downloading/cannot remove.".format(path))
    else:
        print("Removing from download log:", path)
        session.merge(Download(path=path, size=0, type="download", finished=True))
        session.commit()

    db.close_session()