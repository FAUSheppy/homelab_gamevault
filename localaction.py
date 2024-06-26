import subprocess
import sys
import os

# windows imports #
if os.name == "nt":
    import win32com.client
else:
    os.environ.update({"WINEARCH": "win64"})

def _template_registry_file(template_file, game_path=None):
    '''Template the registry file before installation'''
    pass

def unpack_software(software_cache_path, target_path):
    '''Unpack a downloaded software to the target location'''
    pass

def install_registry_file(registry_file, game_path=None):
    '''Install a given registy file'''

    # test path:
    # ./example_software_root/FreeDink/registry_files/game_path_example_1.reg

    if sys.platform.startswith("linux"):
        p = subprocess.Popen(["wine64", "start", "regedit", registry_file],
                subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        print("Running regedit for wine..")
    else:
        # windows sucky sucky #
        if not os.path.isabs(registry_file):
            registry_file = os.path.join(os.getcwd(), registry_file)

        p = subprocess.Popen(["python", "regedit.py", registry_file],
                subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    print(p.communicate())

def install_extra_files(extra_files_list, path):
    '''Copy/Install extra gamedata to a give location'''
    pass

def resolve_lnk(lnk_file_path):

    if os.name == "nt":
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(lnk_file_path)
        return shortcut.TargetPath
    else:
        return lnk_file_path # not required on linux

def run_exe(path, synchronous=False):
    '''Launches a given software'''

    if os.name != "nt":
        if ".lnk" in path:
            subprocess.Popen(["wine64", "start", path])
        else:
            subprocess.Popen(["wine64", path], cwd=os.path.dirname(path))
        return

    if synchronous:
        raise NotImplementedError("SYNC not yet implemented")

    if path.endswith(".lnk"):
        path = resolve_lnk(path)

    print("Executing:", path)

    try:
        subprocess.Popen(path, cwd=os.path.dirname(path))
    except OSError as e:
        if "WinError 740" in str(e):
            p = subprocess.Popen(["python", "adminrun.py", path],
                subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            print(p.communicate())
        else:
            raise e

def remove_software(path):
    '''Remove a software at the target location'''
    pass

def uninstall_registry_file(registry_file):
    '''Uninstall given registry file by it's keys'''
    pass

def uninstall_extra_files(extra_file_list, path):
    '''Uninstall all extra game data'''
    pass
