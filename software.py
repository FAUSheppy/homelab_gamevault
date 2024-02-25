import yaml
import os
import localaction
import zipfile
import shutil
import pathlib

class Software:

    def __init__(self, meta_file, backend):

        self.meta_file = meta_file
        self.directory = os.path.dirname(meta_file)
        self.backend = backend
        self.cache_dir = os.path.join("cache", self.directory)
        self._load_from_yaml()

    def _load_from_yaml(self):

        content = self.backend.get(self.meta_file, self.cache_dir, return_content=True)

        meta = yaml.safe_load(content)
        self.title = meta.get("title")
        self.genre = meta.get("genre")
        self.description = meta.get("description")
        self.dependencies = meta.get("dependencies")
        self.link_only = meta.get("link_only")
        self.link = meta.get("link")
        self.extra_files = meta.get("extra_files")
        self.run_exe = meta.get("run_exe")
        self.installer = meta.get("installer")

        self.pictures = [ self.backend.get(pp, self.cache_dir) for pp in
                self.backend.list(os.path.join(self.directory, "pictures"), fullpaths=True) ]
        
        self.reg_files = self.backend.list(os.path.join(self.directory, "registry_files"), fullpaths=True)


    def get_thumbnail(self):
        '''Return the thumbnail for this software'''

        if not self.pictures:
            return None

        return self.pictures[0]
    
    def _extract_to_target(self, cache_src, target):
        '''Extract a cached, downloaded zip to the target location'''

        software_path = os.path.join(target, self.title)
        os.makedirs(software_path, exist_ok=True)

        with zipfile.ZipFile(cache_src, 'r') as zip_ref:
            zip_ref.extractall(software_path)

    def install(self):
        '''Install this software from the backend'''

        print("Installing:", self.title, self.directory)

        path = os.path.join(self.directory, "main_dir")
        remote_file = self.backend.list(path, fullpaths=True)[0]
        local_file = self.backend.get(remote_file, self.cache_dir)

        # execute or unpack #
        if local_file.endswith(".exe"):
            localaction.run_exe(local_file)
        elif local_file.endswith(".zip"):
            self._extract_to_target(local_file, self.backend.install_dir)
        
        # download & install registry files #
        for rf in self.reg_files:
            path = self.backend.get(rf, cache_dir=self.cache_dir)
            localaction.install_registry_file(path)

        # install dependencies #
        if self.dependencies:
            avail_software = self.backend.find_all_metadata()
            for s in avail_software:
                if s.title in self.dependencies:
                    s.install()

        # run installer if set #
        if self.installer:
            installer_path = os.path.join(self.backend.install_dir,  self.title, self.installer)
            print("Running installer:", installer_path)
            localaction.run_exe(installer_path)

        # install gamefiles #
        if self.extra_files:
            for src, dest in self.extra_files.items():
                tmp = self.backend.get(os.path.join(self.directory, "extra_files", src), self.cache_dir)
                dest_dir = os.path.expandvars(dest)
                os.makedirs(dest_dir, exist_ok=True)
                shutil.copy(tmp, dest_dir)
    
    def run(self):
        '''Run the configured exe for this software'''
        if self.run_exe:
            localaction.run_exe(os.path.join(self.backend.install_dir, self.title, self.run_exe)) 