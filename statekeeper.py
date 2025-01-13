import requests
import os
import threading

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