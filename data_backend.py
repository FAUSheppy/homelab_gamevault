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
                    progress_bar_wrapper=None, tkinter_root=None):

        self.user = user
        self.password = password
        self.remote_root_dir = remote_root_dir
        self.server = server
        self.install_dir = install_dir
        self.progress_bar_wrapper = progress_bar_wrapper
        self.root = tkinter_root

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

    paths_listed = {}

    def _connect(self):

        if self.server.startswith("ftp://"):
            tls = False
        elif self.server.startswith("ftps://"):
            tls = True
        else:
            raise ValueError("FTP Server must start with ftp:// or ftps://")

        # build connection parameters #
        server = self.server.split("://")[1]
        port = None
        try:
            port = int(server.split(":")[-1])
            server = server.split(":")[0]
        except (IndexError, ValueError):
            server = self.server
        
        #print("Connectiong to:", server, "on port:", port)

        # connect #
        if not tls:
            ftp = ftplib.FTP()
        else:
            ftp = ftplib.FTP_TLS()
        ftp.connect(server, port=port)

        if self.user:
            ftp.login(self.user, self.password)
        else:
            ftp.login()

        return ftp


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
            #print(self.remote_root_dir, path, fullpath)
        fullpath = fullpath.replace("\\", "/")
        local_file = os.path.join(cache_dir, os.path.basename(path))
        
        if not os.path.isfile(local_file):
            ftp = self._connect()
            ftp.sendcmd('TYPE I')

            # load the file on remote #
            total_size = ftp.size(fullpath)
            self.progress_bar_wrapper.get_pb()["maximum"] = total_size

            print(local_file, "not in cache, retriving..")
            with open(local_file, "w") as f:
                f.write(local_file)
            with open(local_file, 'wb') as local_file_open, tqdm.tqdm(
                desc="Downloading", 
                total=total_size, 
                unit='B', 
                unit_scale=True
            ) as cmd_progress_bar:

                # Define a callback function to update the progress bar #
                def callback(data):
                    local_file_open.write(data)
                    self.root.update_idletasks() # Update the GUI
                    self.progress_bar_wrapper.get_pb().set(
                        self.progress_bar_wrapper.get_pb().get() + len(data))
                    cmd_progress_bar.update(len(data))

                # run with callback #
                ftp.retrbinary('RETR ' + fullpath, callback)
        
        if return_content:
            with open(local_file, encoding="utf-8") as fr:
                return fr.read()

        return local_file
    
    def list(self, path, fullpaths=False):
        
        # prepend root dir if not given #
        fullpath = path
        if self.remote_root_dir and not path.startswith(self.remote_root_dir):
            fullpath = os.path.join(self.remote_root_dir, path)
        fullpath = fullpath.replace("\\", "/")
        #print(fullpath)

        # if not os.path.isdir(fullpath):
        #     return []

        try:
            # retrieve session cached paths #
            if fullpath in self.paths_listed:
                paths = self.paths_listed[fullpath]
                #print("Retrieved paths from cache:", fullpath, paths)
            else:
                ftp = self._connect()
                self.paths_listed.update({fullpath: []}) # in case dir does not exit
                paths = ftp.nlst(fullpath)
                self.paths_listed.update({fullpath: paths})

            if not fullpaths:
                return paths
            return [ os.path.join(path, filename).replace("\\", "/") for filename in paths ]
        except ftplib.error_perm as e:
            if "550 No files found" in str(e):
                print("No files in this directory: {}".format(fullpath))
                return []
            elif "550 No such file or directory" in str(e):
                print("File or dir does not exist: {}".format(fullpath))
                return []
            else:
                raise e
    
    def find_all_metadata(self):
        
        local_meta_file_list = []

        root_elements = self.list(self.remote_root_dir)
        for s in root_elements:
            #print(s)
            files = self.list(s, fullpaths=True)
            #print(files)
            for f in files:
                if f.endswith("meta.yaml"):
                    meta_file_content = self.get(f, cache_dir="cache", return_content=True)
                    #print(meta_file_content)
                    local_meta_file_list.append(f)
        
        return [ software.Software(meta_file, self, self.progress_bar_wrapper) 
                    for meta_file in local_meta_file_list ]