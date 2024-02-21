class LocalConfig:

    def __init__(self):

        self.remote_user = None
        self.remote_pass = None
        self.skip_registry_ask = None

    def save_to_fs(self):
        '''Save the current config to the local file system'''
        pass

    def load_from_fs(self):
        '''Load a config file from the filesystem'''
        pass