import os
import glob
import yaml
import software

class DataBackend:

    def __init__(self, user, password, cache_dir, remote_root_dir=None):

        self.user = user
        self.password = password
        self.cache_dir = cache_dir
        self.remote_root_dir = remote_root_dir

        if not os.path.isdir(self.cache_dir):
            os.mkdir(self.cache_dir)

    def get(self, path):
        '''Return the contents of this path'''
        raise NotImplementedError()
    
    def list(self, path):
        '''List the contents of this path'''
        raise NotImplementedError()
    
    def find_all_metadata(self):
        '''Return key-value map of { software : metadata-dict }'''
        raise NotImplementedError

class LocalFS(DataBackend):

    def get(self, path):
        fullpath = os.path.join(self.remote_root_dir, path)
        with open(fullpath, "rb") as f:
            target = os.path.join(self.cache_dir, os.path.basename(path))
            with open(target, "wb") as ft:
                ft.write(f.read())
    
    def list(self, path):
        fullpath = os.path.join(self.remote_root_dir, path)
        return os.listdir(fullpath)
    
    def find_all_metadata(self):
        
        meta_info_list = []
        for software_dir in glob.iglob(self.remote_root_dir + "/*"):
            meta_file = os.path.join(software_dir, "meta.yaml")
            if not os.path.isfile(meta_file):
                continue
            else:
                meta_info_list.append(software.Software(meta_file))
        
        return meta_info_list
