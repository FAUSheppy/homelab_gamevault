import yaml
import tkinter
import os
import localaction
import zipfile
import shutil
import pathlib
import tqdm
import webbrowser
import jinja_helper
import threading
import sys
import tkinter
import statekeeper
from tkinter import messagebox

class Software:

    def __init__(self, meta_file, backend, progress_bar_wrapper):

        self.meta_file = meta_file
        self.directory = os.path.dirname(meta_file)
        self.backend = backend
        self.run_button = None
        print("Software Directory:", self.directory)

        self.cache_dir = backend.cache_dir or os.path.join("cache", self.directory.lstrip("/").lstrip("\\"))

        # return None instead of the object if yaml failed #
        try:
            self.invalid = False
            self._load_from_yaml()
        except ValueError as e:
            print(e)
            raise e
            self.invalid = True

        # if not progress_bar_wrapper:
        #     raise AssertionError()

        # self.progress_bar_wrapper = progress_bar_wrapper

    def _load_from_yaml(self):

        content = self.backend.get(self.meta_file, self.cache_dir, return_content=True)
        # print("Meta-Content:", content)

        meta = yaml.safe_load(content)
        if not meta:
            raise ValueError("Empty Meta File")

        self.title = meta.get("title")
        self.genre = meta.get("genre")
        self.description = meta.get("description")
        self.dependencies = meta.get("dependencies")
        self.link_only = meta.get("link_only")
        self.link = meta.get("link")
        self.extra_files = meta.get("extra_files")
        self.run_exe = meta.get("run_exe")
        self.installer = meta.get("installer")
        self.installer_no_admin = meta.get("installer_no_admin")
        self.age_limit = meta.get("age_limit") or 20

        self.pictures = [ self.backend.get(pp, self.cache_dir) for pp in
                self.backend.list(os.path.join(self.directory, "pictures"), fullpaths=True) ]
        
        if any([x is None for x in self.pictures]):
            raise AssertionError("None Entries in self.pictures: " + str(self.pictures))

        self.reg_files = self.backend.list(os.path.join(self.directory, "registry_files"), fullpaths=True)

        print("Finished Init for", self.title)


    def get_thumbnail(self):
        '''Return the thumbnail for this software'''

        if not self.pictures:
            return None

        return self.pictures[0]

    def _extract_to_target(self, cache_src, target):
        '''Extract a cached, downloaded zip to the target location'''

        software_path = os.path.join(target, self.title)

        if os.path.isdir(software_path):
            overwrite = messagebox.askyesno(
                "Overwrite Existing Directory",
                f"The directory '{software_path}' already exists.\nDo you want to overwrite it?"
            )
            if not overwrite:
                print("Skipping install as instructed by user...")
                return

        os.makedirs(software_path, exist_ok=True)

        with zipfile.ZipFile(cache_src, 'r') as zip_ref:

            total_count = zip_ref.infolist()
            count = 0
            for member in tqdm.tqdm(total_count, desc='Extracting '):
                try:
                    zip_ref.extract(member, software_path)
                    count += 1
                    #self.progress_bar_wrapper.get_pb().set(count/len(total_count))
                    #self.progress_bar_wrapper.get_pb().update_idletasks()
                    #self.progress_bar_wrapper.set_text(
                    #                text="Extracting: {:.2f}%".format(count/len(total_count)*100))
                except zipfile.error as e:
                    print(e)
                    pass # TODO ???
            #zip_ref.extractall(software_path)

        #self.progress_bar_wrapper.set_text(text="Loading..")
        #self.progress_bar_wrapper.update()

    def install_async(self):

        thread = threading.Thread(target=self.install)
        thread.start()

    def install(self):
        '''Install this software from the backend'''

        # things to execute #
        admin_run_list = []

        print("Installing:", self.title, self.directory)

        # handle link-only software #
        if self.link_only:
            webbrowser.open(self.link_only)
            return

        #self.progress_bar_wrapper.set_text(text="Please wait..")
        #self.progress_bar_wrapper.tk_parent.update_idletasks()
        path = os.path.join(self.directory, "main_dir")

        try:
            remote_file = self.backend.list(path, fullpaths=True)[0]
        except IndexError:
            print("No main_dir:", path)
            raise AssertionError("No main_dir for this software")
        
        statekeeper.log_begin_download(remote_file, self.backend.get_local_target(remote_file), self.backend._get_url())
        local_file = self.backend.get(remote_file, self.cache_dir, wait=True)
        statekeeper.log_end_download(remote_file)

        print("Deciding on installer...")

        # execute or unpack #
        if local_file.endswith(".exe"):
            print("Target is an executable.. running as installer.")
            if os.name != "nt" and not os.path.isabs(local_file):
                # need abs path for wine #
                local_file = os.path.join(os.getcwd(), local_file)
            localaction.run_exe(local_file)
        elif local_file.endswith(".zip"):
            print("Target is a zip.. unpacking first.")
            self._extract_to_target(local_file, self.backend.install_dir)

        # download & install registry files #
        for rf in self.reg_files:
            path = self.backend.get(rf, cache_dir=self.cache_dir)
            if path.endswith(".j2"):
                target_install_dir = os.path.join(self.backend.install_dir, self.title)
                print("Install dir Registry:", target_install_dir)
                path = jinja_helper.render_path(path, target_install_dir, self.directory)

            if sys.platform == "win32":
                admin_run_list.append(path)
            else:
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
            if os.name != "nt" and not os.path.isabs(installer_path):
                # need abs path for wine #
                installer_path = os.path.join(os.getcwd(), installer_path)


            print("Running installer:", installer_path)
            if not self.installer_no_admin:
                admin_run_list.append(installer_path)
            else:
                localaction.run_exe(installer_path)

        if admin_run_list:
            print("admin list", admin_run_list)
            localaction.run_exe(admin_run_list)

        # install gamefiles #
        if self.extra_files:
            for src, dest in self.extra_files.items():
                tmp = self.backend.get(os.path.join(self.directory, "extra_files", src), self.cache_dir, wait=True)
                dest_dir = os.path.expandvars(dest)
                os.makedirs(dest_dir, exist_ok=True)
                shutil.copy(tmp, dest_dir)

        #self.progress_bar_wrapper.set_text(text="")
        try:
            if self.run_button:
                self.run_button.configure(state=tkinter.NORMAL)
                self.run_button.configure(fg_color="green")
        except tkinter.TclError:
            print("INFO: No longer in installation view - no button to update")

    def run(self):
        '''Run the configured exe for this software'''

        print(self.run_exe, self.link_only)
        if self.run_exe == "steam" and "steam://" in self.link_only:
            print("steam://runid/{}".format(self.link_only.split("/")[-1]))
            webbrowser.open("steam://rungameid/{}".format(self.link_only.split("/")[-1]))
            return

        if self.run_exe:
            if os.name == "nt" or not ".lnk" in self.run_exe:
                localaction.run_exe(os.path.join(self.backend.install_dir, self.title, self.run_exe))
            else:
                localaction.run_exe(self.run_exe)
