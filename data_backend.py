import os
import glob
import yaml
import software
import ftplib
import tqdm

class DataBackend:

    def _create_cache_dir(self, cache_dir):
        os.makedirs(cache_dir, exist_ok=True)

    def __init__(self, user, password, install_dir, server=None, remote_root_dir=None,
                    progress_bar=None, tkinter_root=None):

        self.user = user
        self.password = password
        self.remote_root_dir = remote_root_dir
        self.server = server
        self.install_dir = install_dir

        self.pro

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

class FTP(DataBackend):

    def _connect(self):

        if self.server.startswith("ftp://"):
            ftp = ftplib.FTP(self.server)
        elif self.server.startswith("ftps://"):
            ftp = ftplib.FTP_TLS(self.server)

        if self.user:
            ftp.login(self.user, self.password)
        else:
            ftp.login()

        return ftp
    

    def get(self, path, cache_dir=None, return_content=False):

        # prepend root dir if not given #
        fullpath = path
        if self.remote_root_dir and not path.startswith(self.remote_root_dir):
            fullpath = os.path.join(self.remote_root_dir, path)
        
        ftp = self._connect()

        # load the file on remote #
        total_size = ftp.size(fullpath)
        local_file = os.path.join(cache_dir, os.path.basename(path))
        self.progress_bar["maximum"] = total_size

        with open(local_file, 'wb') as local_file, tqdm(
            desc="Downloading", 
            total=total_size, 
            unit='B', 
            unit_scale=True
        ) as progress_bar:
            
            # Define a callback function to update the progress bar #
            def callback(data):
                local_file.write(data)
                self.root.update_idletasks() # Update the GUI
                self.progress_bar.step(len(data))

            # run with callback #
            ftp.retrbinary('RETR ' + fullpath, callback)

        return local_file
    
    def list(self, path, fullpaths=False):
        
        # prepend root dir if not given #
        fullpath = path
        if self.remote_root_dir and not path.startswith(self.remote_root_dir):
            fullpath = os.path.join(self.remote_root_dir, path)

        if not os.path.isdir(fullpath):
            return []

        ftp = self._connect()
        try:
            paths = ftp.nlst(fullpath)
            if not fullpaths:
                return paths
            return [ os.path.join(path, filename) for filename in paths ]
        except ftplib.error_perm as e:
            if str(e) == "550 No files found":
                print("No files in this directory: {}".format(fullpath))
                return []
            else:
                raise e
    
    def find_all_metadata(self):
        
        local_meta_file_list = []

        root_elements = self.list(self.remote_root_dir)
        for s in root_elements:
            files = self.list(s, fullpaths=True)
            for f in files:
                if f.endswith("meta.yaml"):
                    local_meta_file = self.get(meta_file)
                    local_meta_file_list.append(local_meta_file)
        
        return [ software.Software(meta_file, self) for meta_file in local_meta_file_list ]