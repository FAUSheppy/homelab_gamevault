import os
import glob
import yaml
import software
import ftplib
import tqdm
import ssl
import concurrent.futures

class SESSION_REUSE_FTP_TLS(ftplib.FTP_TLS):
    """Explicit FTPS, with shared TLS session"""

    def ntransfercmd(self, cmd, rest=None):

        conn, size = ftplib.FTP.ntransfercmd(self, cmd, rest)
        if self._prot_p:
            conn = self.context.wrap_socket(
                conn,
                server_hostname=self.host,
                session=self.sock.session)  # this is the fix
        return conn, size

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
        self.ftp = None # ftp connection object

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

class FTP(DataBackend):

    paths_listed = {}

    def _connect(self, individual_connection=False):

        if self.ftp and not individual_connection:
            try:
                self.ftp.voidcmd("NOOP")
                return self.ftp
            except ssl.SSLError:
                pass # reconnect

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
            server = server.split(":")[0]
        except (IndexError, ValueError):
            port = 0

        # try extract server #
        try:
            server = server.split(":")[0]
        except (IndexError, ValueError):
            server = self.server

        print("Connecting to:", server, "on port:", port, "ssl =", tls)

        # connect #
        if not tls:
            ftp = ftplib.FTP()
        else:
            ftp = SESSION_REUSE_FTP_TLS()
            ftp.ssl_version = ssl.PROTOCOL_TLSv1_2

        ftp.connect(server, port=port or 0)

        if self.user:
            ftp.login(self.user, self.password)
        else:
            ftp.login()

        # open a secure session for tls #
        if tls:
            ftp.prot_p()

        # cache dir is automatically set #
        self.cache_dir = None

        if not individual_connection:
            self.ftp = ftp
        return ftp


    def get(self, path, cache_dir=None, return_content=False, new_connection=False):

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

        # print("Cachedir:", cache_dir, os.path.basename(path), local_file)

        if not os.path.isfile(local_file):

            ftp = self._connect(individual_connection=True)
            ftp.sendcmd('TYPE I')

            # load the file on remote #
            if not new_connection:

                total_size = ftp.size(fullpath)
                print("Total Size:", total_size)
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
                        if new_connection: # return if parralell
                            return
                        self.root.update_idletasks() # Update the GUI
                        current_total = self.progress_bar_wrapper.get_pb().get() + len(data)/total_size
                        self.progress_bar_wrapper.get_pb().set(current_total)
                        self.progress_bar_wrapper.set_text(
                                        text="Downloading: {:.2f}%".format(current_total*100))
                        cmd_progress_bar.update(len(data))

                    # run with callback #
                    ftp.retrbinary('RETR ' + fullpath, callback)
            else:
                with open(local_file, 'wb') as fp:
                    ftp.retrbinary('RETR ' + fullpath, fp.write)

            if new_connection:
                ftp.close()

        if return_content:
            with open(local_file, encoding="utf-8") as fr:
                return fr.read()

        return local_file

    def list(self, path, fullpaths=False, new_connection=False):

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
                ftp = self._connect(individual_connection=new_connection)
                print("Listing previously unlisted path: {}".format(fullpath))
                self.paths_listed.update({fullpath: []}) # in case dir does not exit
                paths = ftp.nlst(fullpath)
                self.paths_listed.update({fullpath: paths})

                if new_connection: # close individual connections
                    ftp.close()

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
        with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()*5) as executor:

            software_dir_contents = list(executor.map(
                    lambda s: self.list(s, fullpaths=True, new_connection=True), root_elements))

            # this caches the paths, done remove it #
            cache_list = [os.path.join(s, "registry_files") for s in root_elements ]
            cache_list += [os.path.join(s, "pictures") for s in root_elements ]
            picture_contents_async_cache = list(executor.map(
                    lambda s: self.list(s, fullpaths=True, new_connection=True), cache_list))

        for files in software_dir_contents:
            #print(s)
            #files = self.list(s, fullpaths=True)
            print(files)
            for f in files:
                if f.endswith("meta.yaml"):
                    meta_file_content = self.get(f, cache_dir="cache", return_content=True)
                    #print(meta_file_content)
                    local_meta_file_list.append(f)

        with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()*5) as executor:
            software_list = executor.map(lambda meta_file: software.Software(meta_file, self, self.progress_bar_wrapper), local_meta_file_list)
            return list(filter(lambda x: not x.invalid, software_list))
