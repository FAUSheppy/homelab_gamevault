import subprocess
import sys
import os
import json
import win32com.client
import pythoncom

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

def install_registry_file(registry_file):
    '''Install a given registy file'''

    # test path:
    # ./example_software_root/FreeDink/registry_files/game_path_example_1.reg

    if sys.platform.startswith("linux"):
        p = subprocess.Popen(["wine64", "start", "regedit", registry_file],
                subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        print("Running regedit for wine..")

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

def substitute_win_paths(path):

    pythoncom.CoInitialize()  
    shell = win32com.client.Dispatch("WScript.Shell")
    common_programs = shell.SpecialFolders("AllUsersPrograms")
    path = path.replace("%ProgramData%", common_programs)
    return path

def check_substitute_path_exists(path):

    if "%" in path:
        return os.path.isfile(substitute_win_paths(path))

def run_exe(path, synchronous=False):
    '''Launches a given software'''

    if type(path) == str:
        paths = [path]
    else:
        paths = path

    # sanity check path is list #
    if not type(paths) == list:
        raise AssertionError("ERROR: run_exe could not build a list of paths")

    if os.name != "nt":
        if ".lnk" in path:
            subprocess.Popen(["wine64", "start", path])
        else:
            subprocess.Popen(["wine64", path], cwd=os.path.dirname(path))
        return

    if synchronous:
        raise NotImplementedError("SYNC not yet implemented")

    print("Raw paths:", paths)

    # substitute program data #
    paths = [ substitute_win_paths(p) for p in paths ]

    # substituted paths #
    print("Subs paths:", paths)

    # resolve links #
    paths = [resolve_lnk(p) if p.endswith(".lnk") else p for p in paths]

    print("Executing prepared:", paths)

    try:
        if paths[0].endswith(".reg"):
            raise OSError("WinError 740")
        path = paths[0].replace("\\\\", "\\")
        subprocess.Popen(path, cwd=os.path.dirname(paths[0])) # TODO fix this BS
    except OSError as e:
        if "WinError 740" in str(e):
            p = subprocess.Popen(["powershell", "-ExecutionPolicy", "Bypass", "-File",
                "windows_run_as_admin.ps1", json.dumps(paths)],
                subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            try:
                print(p.communicate())
            except UnicodeDecodeError as e:
                print("WARNING: cannot show you ERROR from exe because output contained illegal characters. This maybe because your refused the admin prompt.")
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