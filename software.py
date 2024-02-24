import yaml
import os
import localaction

class Software:

    def __init__(self, directory, backend):

        if os.path.isfile(directory) and directory.endswith("meta.yaml"):
            directory = os.path.dirname(directory)

        self.directory = directory
        self._load_from_yaml()
        self.backend = backend

    def _load_from_yaml(self):

        fullpath = os.path.join(self.directory, "meta.yaml")
        self.info_file = fullpath
        with open(fullpath) as f:
            meta = yaml.safe_load(f)

            self.title = meta.get("title")
            self.genre = meta.get("genre")
            self.description = meta.get("description")
            self.dependencies = meta.get("dependencies")
            self.link_only = meta.get("link_only")
            self.link = meta.get("link")
            self.extra_files = meta.get("extra_files")

            self.pictures = [os.path.join(self.directory, "pictures", p) for p in
                                os.listdir(os.path.join(self.directory, "pictures"))]

    def get_thumbnail(self):

        return self.pictures[0]
    
    def _extract_to_target(self, cache_src, target):
        '''Extract a cached, downloaded zip to the target location'''

    def install(self):
        '''Install this software from the backend'''

        local_file = self.backend.get_exe_or_data():

        if local_file.endswith(".exe"):
            localaction.run_exe(local_file)
        elif local_file.endswith(".zip"):
            _extract_to_target(INSTALL_DIR)
        
        # download registry
        # install registry
        # TODO dependencies #
        # download gamefiles
        # install gamefiles
        