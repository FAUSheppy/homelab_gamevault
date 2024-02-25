from pyuac.main_decorator import main_requires_admin
import sys
import subprocess

@main_requires_admin(return_output=True)
def main(path):
    p = subprocess.Popen(path, subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    stdout, stderr = p.communicate()

if __name__ == '__main__':
    path = sys.argv[-1]
    rv = main(path)
    print(rv)