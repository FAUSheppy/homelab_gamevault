def _template_registry_file(template_file, game_path=None):
    '''Template the registry file before installation'''
    pass

def unpack_software(software_cache_path, target_path):
    '''Unpack a downloaded software to the target location'''
    pass

def install_registry_file(registry_file, game_path=None):
    '''Install a given registy file'''

def install_extra_files(extra_files_list, path):
    '''Copy/Install extra gamedata to a give location'''
    pass

def launch_software(path, synchronous=False):
    '''Launches a given software'''
    pass

def remove_software(path):
    '''Remove a software at the target location'''
    pass

def uninstall_registry_file(registry_file):
    '''Uninstall given registry file by it's keys'''
    pass

def uninstall_extra_files(extra_file_list, path):
    '''Uninstall all extra game data'''
    pass