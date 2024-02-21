from pyuac.main_decorator import main_requires_admin
import sys
import subprocess

@main_requires_admin(return_output=True)
def main(registry_file):
    p = subprocess.Popen(["regedit", registry_file], 
            subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    stdout, stderr = p.communicate()

if __name__ == '__main__':
    registry_file = sys.argv[-1]
    rv = main(registry_file)
    print(rv)