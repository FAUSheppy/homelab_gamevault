import os
import glob
import yaml
import software
import ftplib
import tqdm
import ssl
import concurrent.futures
import statekeeper
import requests


class DataBackend:

    def _create_cache_dir(self, cache_dir):
        os.makedirs(cache_dir, exist_ok=True)

    def __init__(self, user, password, install_dir, server=None, remote_root_dir=None,
                    progress_bar_wrapper=None, tkinter_root=None):

        self.user = user
        self.password = password
        self.remote_root_dir = remote_root_dir
        self.server = server
        self.install_dir = install_dir
        self.progress_bar_wrapper = progress_bar_wrapper
        self.root = tkinter_root
        self.cache_dir = "./cache/"

    def get(self, path, return_content=False):
        '''Return the contents of this path'''
        raise NotImplementedError()

    def list(self, path):
        '''List the contents of this path'''
        raise NotImplementedError()

    def find_all_metadata(self):
        '''Return key-value map of { software : metadata-dict }'''
        raise NotImplementedError

class LocalFS(DataBackend):

    def get(self, path, cache_dir=None, return_content=False):

        # check the load cache dir #
        if cache_dir:
            self._create_cache_dir(cache_dir)
        elif not cache_dir and not return_content:
            AssertionError("Need to set either cache_dir or return_content!")

        # prepend root dir if not given #
        fullpath = path
        if self.remote_root_dir and not path.startswith(self.remote_root_dir):
            fullpath = os.path.join(self.remote_root_dir, path)

        # load the file on remote #
        with open(fullpath, "rb") as f:
            target = os.path.join(cache_dir, os.path.basename(path))
            print("Cache-Dir-Base", cache_dir, "Cache-Dir-Target", target, "Path:", path)
            with open(target, "wb") as ft:
                if return_content:
                    return f.read()
                ft.write(f.read())

        return target

    def list(self, path, fullpaths=False):

        # prepend root dir if not given #
        fullpath = path
        if self.remote_root_dir and not path.startswith(self.remote_root_dir):
            fullpath = os.path.join(self.remote_root_dir, path)

        if not os.path.isdir(fullpath):
            return []

        if fullpaths:
            return [ os.path.join(path, filename) for filename in os.listdir(fullpath)]
        else:
            return os.listdir(fullpath)

    def find_all_metadata(self):

        meta_info_list = []
        for software_dir in glob.iglob(self.remote_root_dir + "/*"):
            meta_file = os.path.join(software_dir, "meta.yaml")
            if not os.path.isfile(meta_file):
                continue
            else:
                meta_info_list.append(software.Software(meta_file, self, self.progress_bar_wrapper))

        return list(filter(lambda x: not x.invalid, meta_info_list))
class HTTP(DataBackend):

    paths_listed = {}
    REMOTE_PATH = "/get-path"

    def _get_url(self):
        #print(self.server + HTTP.REMOTE_PATH)
        return self.server + HTTP.REMOTE_PATH
 
    def get_local_target(self, path):

        # prepend root dir if not given #
        fullpath = path
        if self.remote_root_dir and not path.startswith(self.remote_root_dir):
            fullpath = os.path.join(self.remote_root_dir, path)

        fullpath = fullpath.replace("\\", "/")
        local_file = os.path.join(self.cache_dir, fullpath)
        print("Local Target is", local_file)
        return local_file

    def get(self, path, cache_dir=None, return_content=False, wait=False):

        print("Getting", path, "cache dir", cache_dir, "return content:", return_content)

        if cache_dir is None:
            print("Setting cache dir from backend default", "cur:", cache_dir, "new (default):", self.cache_dir)
            cache_dir = self.cache_dir

        # fix cache path reuse #
        if path.startswith(cache_dir):
            path = path[len(cache_dir):]
            print("Fixed path to not duble include cache dir, path:", path)

        # check the load cache dir #
        if cache_dir:
            self._create_cache_dir(cache_dir)
        elif not cache_dir and not return_content:
            AssertionError("Need to set either cache_dir or return_content!")

        local_file = self.get_local_target(path)
        local_dir = os.path.dirname(local_file)

        # sanity check and create directory #
        if not local_dir.startswith(cache_dir):
            raise AssertionError("Local Dir does not start with cache dir:" + local_dir)
        else:
            os.makedirs(local_dir, exist_ok=True)

        print("Requiring:", path)

        if not os.path.isfile(local_file) or os.stat(local_file).st_size == 0:

            if return_content or wait:

                # the content is needed for the UI now and not cached, it's needs to be downloaded synchroniously #
                # as there cannot be a meaningful UI-draw without it. #
                # THIS IS THE OLD WAY
                # r = requests.get(self._get_url(), params={ "path" : path, "as_string": True })

                # # cache the download imediatelly #
                # with open(local_file, encoding="utf-8", mode="w") as f:
                #     f.write(r.text)

                # this is with streaming
                chunk_size = 1024 * 1024  * 5 # 5MB
                r = requests.get(self._get_url(), params={"path": path, "as_string": True}, stream=True)

                with open(local_file, "wb") as f:
                    for chunk in r.iter_content(chunk_size=chunk_size, decode_unicode=True):
                        if chunk:
                            f.write(chunk)

                if return_content:                    
                    print("Content for", path, ":",  r.text)
                    return r.text
                else:
                    return local_file

            else:
                print("Async Requested for:", local_file)
                statekeeper.add_to_download_queue(self._get_url(), path)
                return local_file

        elif return_content:
            print("Returning Cached file:", local_file)
            with open(local_file, encoding="utf-8") as fr:
                return fr.read()
        else:
            print("Already present:", local_file)
            return local_file

    def list(self, path, fullpaths=False):

        fullpath = path
        if self.remote_root_dir and not path.startswith(self.remote_root_dir):
            fullpath = os.path.join(self.remote_root_dir, path)
        fullpath = fullpath.replace("\\", "/")

        # retrieve session cached paths #
        if fullpath in self.paths_listed:
            paths = self.paths_listed[fullpath]
        else:

            r = requests.get(self._get_url(), params={ "path" : path })
            r.raise_for_status()
            #print(r, r.status_code, r.content)
            paths = r.json()["contents"]

            if not fullpaths:
                return paths
            else:
                return [ os.path.join(path, filename).replace("\\", "/") for filename in paths ]

    def find_all_metadata(self):

        local_meta_file_list = []

        root_elements = self.list(self.remote_root_dir)
        print("root elements:", root_elements)
        with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()*5) as executor:

            software_dir_contents = list(executor.map(
                    lambda s: self.list(s, fullpaths=True), root_elements))

            # this caches the paths, done remove it #
            cache_list = [os.path.join(s, "registry_files") for s in root_elements ]
            cache_list += [os.path.join(s, "pictures") for s in root_elements ]

            # THIS PRELOAD IMAGES-paths, DO NOT REMOVE IT #
            picture_contents_async_cache = list(executor.map(
                    lambda s: self.list(s, fullpaths=True), cache_list))

        for files in software_dir_contents:
            for f in files:
                if f.endswith("meta.yaml"):
                    local_meta_file_list.append(f)


        print("local meta:", local_meta_file_list)
        software_list = None
        with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()*5) as executor:
            software_list = executor.map(lambda meta_file: software.Software(meta_file, self, self.progress_bar_wrapper), local_meta_file_list)

        # evaluate
        software_list = list(software_list)
        print("Software List:", software_list)
        print("Invalid:", list(filter(lambda x: x.invalid, software_list)))
        print("Valid:", list(filter(lambda x: not x.invalid, software_list)))
        return list(filter(lambda x: not x.invalid, software_list))