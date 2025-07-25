import requests
import os
import sqlalchemy
import threading
from db import db, Download
from sqlalchemy import or_, and_

def _bytes_to_mb(size):
    return size / (1024*1024)

def add_to_download_queue(url, path, auth):
    '''The download is added to the global queue and downloaded eventually'''
    #_download(url, path)
    thread = threading.Thread(target=_download, args=(url, path, auth))
    thread.start()

def add_to_task_queue(task):
    '''Add a callback to background execution queue'''
    #print("Executing tasks", task)
    thread = threading.Thread(target=task)
    thread.start()
    #task()

def _download(url, path, auth):

    response = requests.get(url + "?path=" + path, stream=True, auth=auth)

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

def log_begin_download(path, local_path, url, type="download", start_size=-1):

    if type == "extraction":
        print("Extraction path:", path)
    else:
        print("Download path", path)
    
    session = db.session()
    path_exists = session.query(Download).filter(and_(Download.path==path, Download.finished==False, Download.type==type)).first()

    if path_exists and False: # TODO FIX THIS
        print("DAFUG", path_exists)
        print("WTF", path_exists.path)
        raise AssertionError("ERROR: {} is already downloading.".format(path))
    else:
        print("Adding to download log:", path)
        session.merge(Download(path=path, size=start_size, type=type, local_path=local_path, url=url, finished=False, count=1))
        session.commit()

    db.close_session()

def set_extraction_status(path, count):

    session = db.session()
    obj = session.query(Download).filter(and_(Download.path==path, Download.type=="extraction")).first()
    if not obj:
        print("ERROR: {} is not currently extraction, cannot set status.".format(path))
    else:
        obj.count = count
        session.merge(obj)
        session.commit()

    db.close_session()

def log_end_download(path, type="download"):

    print("Downlod end logged", path)
    session = db.session()
    obj = session.query(Download).filter(and_(Download.path==path, Download.type==type)).first()
    if not obj:
        raise AssertionError("ERROR: {} is not downloading/cannot remove.".format(path))
    else:
        print("Removing from download log:", path)
        obj.finished = True
        session.merge(obj)
        session.commit()

    db.close_session()

def get_download_size(path, auth):

    session = db.session()
    obj = session.query(Download).filter(Download.path==path).first()

    if not obj :
        print("Warning: Download-Object does no longe exist in DB. Returning -1")
        return -1
    elif obj.size != -1:
        session.close()
        return obj.size

    # query size #
    r = requests.get(obj.url, params={"path": path, "info": 1}, auth=auth)
    r.raise_for_status()
    
    size = r.json()["size"]
    obj.size = _bytes_to_mb(size)
    session.merge(obj)
    session.commit()
    session.close()

    return size

def get_percent_filled(path, auth):

    session = db.session()
    obj = session.query(Download).filter(Download.path==path, Download.finished==False).first()
    
    if not obj:
        return 100

    if obj.type == "extraction":
        return obj.count / obj.size * 100

    if not obj:
        return 100 # means its finished

    size = _bytes_to_mb(os.stat(obj.local_path).st_size)
    total_size = get_download_size(obj.path, auth)
    session.close()

    if total_size == 0:
        return 0
    
    print("Current filled:", size / total_size * 100)
    return size / total_size * 100

def get_download(path=None):

    session = db.session()
    if path:
        MIN_SIZE_PGBAR_LIMIT = 1024*1024*100 # 100mb
        downloads = session.query(Download).filter(Download.size>MIN_SIZE_PGBAR_LIMIT, Download.finished==False).all()
    else:
        downloads = session.query(Download).filter(Download.finished==False).all()

    session.close()
    return downloads
