import os
import glob
import yaml
import software

class DataBackend:

    def _create_cache_dir(self, cache_dir):
        os.makedirs(cache_dir, exist_ok=True)

    def __init__(self, user, password, install_dir, remote_root_dir=None):

        self.user = user
        self.password = password
        self.remote_root_dir = remote_root_dir
        self.install_dir = install_dir

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
            print(cache_dir, path)
            target = os.path.join(cache_dir, os.path.basename(path))
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
                meta_info_list.append(software.Software(meta_file, self))
        
        return meta_info_list
