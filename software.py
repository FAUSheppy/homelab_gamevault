import yaml
import os

class Software:

    def __init__(self, directory):

        if os.path.isfile(directory) and directory.endswith("meta.yaml"):
            directory = os.path.dirname(directory)

        self.directory = directory
        self._load_from_yaml()

    def _load_from_yaml(self):

        fullpath = os.path.join(self.directory, "meta.yaml")
        self.info_file = fullpath
        with open(fullpath) as f:
            meta = yaml.load(f)

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


