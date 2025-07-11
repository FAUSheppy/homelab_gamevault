import customtkinter
import PIL
import data_backend
import client_details
import pgwrapper
import sys
import json
import os
import cache_utils
import imagetools
import webbrowser
import statekeeper
import infowidget
import requests
import tkinter

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()

app.geometry("1490x700")
last_geometry = app.winfo_geometry()

scrollable_frame = customtkinter.CTkScrollableFrame(app, width=app.winfo_width(), height=app.winfo_height())

buttons = []
details_elements = []

non_disabled_entry_color = None
all_metadata = None

infowidget_window = None

db = None # app data-backend (i.e. LocalFS or FTP)

CONFIG_FILE = "gamevault_config.json"


def close_input_window(input_window):
    '''Close the config window and save the settings'''

    # retrieve values #
    entries = list(filter(lambda x: isinstance(x, (customtkinter.CTkEntry, customtkinter.CTkOptionMenu)), input_window.winfo_children()))
    labels = [ input_window.grid_slaves(row=e.grid_info()["row"], column=e.grid_info()["column"]-1)[0] for e in entries ]

    ret_dict = dict()
    for e, l in zip(entries, labels):
        ret_dict.update({ l.cget("text") : e.get() })

    # dump config and write to file #
    print(json.dumps(ret_dict))
    with open(CONFIG_FILE, "w") as f:
        json.dump(ret_dict, f, indent=2)

    # quit input window #
    input_window.update()
    input_window.quit()
    input_window.withdraw()

def dropdown_changed(dropdown_var, user_entry, password_entry, server_path_entry,
                     install_dir_entry):

    global non_disabled_entry_color

    # FIXME or not idfk #
    if type(dropdown_var) != str:
        dropdown_var = dropdown_var.get()

    # Check the current value of the dropdown and enable/disable user and password inputs accordingly
    if dropdown_var == "Local Filesystem":
        user_entry.configure(state=customtkinter.DISABLED)
        password_entry.configure(state=customtkinter.DISABLED)
        non_disabled_entry_color = password_entry.cget("fg_color")
        print(non_disabled_entry_color)
        password_entry.configure(fg_color="#CCCCCC")
        user_entry.configure(fg_color="#CCCCCC")
        server_path_entry.delete(0, customtkinter.END)
        server_path_entry.insert(0, "C:/path/to/game/mount/")
    elif dropdown_var == "FTP/FTPS":
        user_entry.configure(state=customtkinter.NORMAL)
        password_entry.configure(state=customtkinter.NORMAL)
        if non_disabled_entry_color: # else first run and nothing to do
            password_entry.configure(fg_color=non_disabled_entry_color)
            user_entry.configure(fg_color=non_disabled_entry_color)
        server_path_entry.delete(0, customtkinter.END)
        server_path_entry.insert(0, "ftp://server:port/path or ftps://server:port/path")
    else:
        user_entry.configure(state=customtkinter.NORMAL)
        password_entry.configure(state=customtkinter.NORMAL)
        if non_disabled_entry_color: # else first run and nothing to do
            password_entry.configure(fg_color=non_disabled_entry_color)
            user_entry.configure(fg_color=non_disabled_entry_color)
        server_path_entry.delete(0, customtkinter.END)


    install_dir_entry.delete(0, customtkinter.END)
    install_dir_entry.insert(0, "./install-dir")

# Create a frame to hold the inputs

def get_config_inputs():
    '''Create a config input window and use the settings from it'''

    input_window = customtkinter.CTk()
    input_window.geometry("500x250")
    input_window.title("Vault Configuration")

    # Server/Path
    server_path_label = customtkinter.CTkLabel(input_window, text="Server/Path:")
    server_path_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
    server_path_entry = customtkinter.CTkEntry(input_window)
    server_path_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew", columnspan=2)

    # User
    user_label = customtkinter.CTkLabel(input_window, text="User:")
    user_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
    user_entry = customtkinter.CTkEntry(input_window)
    user_entry.grid(row=2, column=1, padx=10, pady=5)

    # Password
    password_label = customtkinter.CTkLabel(input_window, text="Password:")
    password_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)
    password_entry = customtkinter.CTkEntry(input_window, show="*")
    password_entry.grid(row=3, column=1, padx=10, pady=5)

    # Install dir
    install_dir_label = customtkinter.CTkLabel(input_window, text="Install dir:")
    install_dir_label.grid(row=4, column=0, sticky="w", padx=10, pady=5)
    install_dir_entry = customtkinter.CTkEntry(input_window)
    install_dir_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew", columnspan=2)

    # Dropdown
    dropdown_var = customtkinter.StringVar(value="HTTP/HTTPS")
    dropdown_label = customtkinter.CTkLabel(input_window, text="Select option:")
    dropdown_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
    dropdown = customtkinter.CTkOptionMenu(input_window, variable=dropdown_var, values=["HTTP/HTTPS", "FTP/FTPS", "Local Filesystem"],
        command=lambda dropdown_var=dropdown_var, user_entry=user_entry, password_entry=password_entry,
                        server_path_entry=server_path_entry, install_dir_entry=install_dir_entry:
                        dropdown_changed(dropdown_var, user_entry, password_entry, server_path_entry, install_dir_entry))

    # set dropdown & field defaults
    dropdown_changed(dropdown_var, user_entry, password_entry, server_path_entry, install_dir_entry)
    dropdown.grid(row=0, column=1, padx=10, pady=5)

    # Button to abort & close #
    abort_button = customtkinter.CTkButton(input_window, text="Abort", command=lambda: input_window.quit(), fg_color="red")
    abort_button.grid(row=5, column=0, padx=10, pady=20)

    # Button to save & close #
    save_button = customtkinter.CTkButton(input_window, text="Save & Close", command=lambda: close_input_window(input_window))
    save_button.grid(row=5, column=2, padx=10, pady=20)


    input_window.update()
    input_window.mainloop()

def create_navbar():
    '''Create basic navigation bar'''

    # spawn frame at very top #
    # add "Home" button

def switch_to_main():
    '''Switch back to main view from details'''

    global details_elements
    global last_geometry

    last_geometry = (0,0)

    # destroy details elements #
    for el in details_elements:
        el.destroy()

    details_elements = []
    load_main()

def switch_to_game_details(software):
    '''Switch to the details of the clicked tile'''

    destroy_main()
    load_details(app, software)

def load_main():
    '''Load the main page overview'''

    global all_metadata
    global infowidget_window

    app.title("Lan Vault: Overview")

    if not infowidget_window:
        infowidget_window = infowidget.ProgressBarApp(app, data_backend=db)

    infowidget_window.root.grid(row=1, column=0, sticky="n")

    # navbar should not expand when window is resized
    app.grid_rowconfigure(0, weight=0)
    # buttongrid (scrollable frame) should expand when window is resized
    app.grid_rowconfigure(1, weight=1)
    app.grid_columnconfigure(1, weight=1)
    # place scrollable frame
    scrollable_frame.grid(row=1, column=1, sticky="nsew", columnspan=2)


    # create tiles from meta files #
    cache_dir_size = 0
    if not all_metadata:
        all_metadata = db.find_all_metadata()

    for software in all_metadata:

        print("Software:", software)
        create_main_window_tile(software, scrollable_frame)

        # retrieve cache dir from any software #
        if not cache_dir_size:
            cache_dir_size = cache_utils.get_cache_size()
            label = customtkinter.CTkLabel(app, text="Cache Size: {:.2f} GB".format(cache_dir_size))
            GITHUB_URL = "https://github.com/FAUSheppy/homelab_gamevault"
            github = customtkinter.CTkButton(app, text="Star on Github",
                            command=lambda: webbrowser.open_new(GITHUB_URL))
            label.grid(row=0, column=0)
            github.grid(row=0, column=1)

    # set update listener & update positions #
    update_button_positions()
    app.bind("<Configure>", update_button_positions)

def destroy_main():
    '''Destroy all elements in the main view'''

    global buttons
    scrollable_frame.grid_remove()
    app.unbind("<Configure>")
    for b in buttons:
        b.destroy()
    
    buttons = []
    app.update()

def load_details(app, software):
    '''Load the details page for a software'''

    global details_elements

    app.title("Lan Vault: {}".format(software.title))
    details_elements = client_details.create_details_page(app, software, switch_to_main, infowidget_window)

def create_main_window_tile(software, parent):
    '''Create the main window tile'''

    img = PIL.Image.new('RGB', (200, 300))
    imgTk = PIL.ImageTk.PhotoImage(img)
    button = customtkinter.CTkButton(parent, image=imgTk,
                                        width=200, height=300,
                                        command=lambda: switch_to_game_details(software),
                                        border_width=0, corner_radius=0, border_spacing=0,
                                        text=software.title,
                                        fg_color="transparent", compound="top", anchor="s")


    def callback_update_thumbnail():

        # TODO: bind button & software into this callback

        try:
            target_file = software.get_thumbnail()
            if not target_file:
                return
            print("Loading thumbnail (async):",  target_file)
            img = PIL.Image.open(target_file)
            img = imagetools.smart_resize(img, 200, 300)
        except PIL.UnidentifiedImageError:
            print("Failed to load thumbnail:", target_file)
            img = PIL.Image.new('RGB', (200, 300))
        
        button.configure(image=PIL.ImageTk.PhotoImage(img))

    # register the update task for the image #
    statekeeper.add_to_task_queue(callback_update_thumbnail)

    # cache button and return #
    buttons.append(button)
    return button

def update_button_positions(event=None):
    '''Sets the tile positions initially and on resize'''

    global last_geometry
    # check vs old location #
    new_geometry = app.winfo_geometry()
    if last_geometry[0] == new_geometry[0] and last_geometry[1] == new_geometry[1]:
        return
    else:
        last_geometry = new_geometry
        scrollable_frame.configure(width=app.winfo_width(), height=app.winfo_height())

    # Calculate the number of columns based on the current width of the window #
    num_columns = app.winfo_width() // 301  # Adjust 100 as needed for button width

    # window became too small #
    if num_columns == 0:
        return

    # calculated and set positions
    for i, button in enumerate(buttons):

        grid_info_current = button.grid_info()
        column_new = i % num_columns
        row_new = i // num_columns

        if(grid_info_current.get("row") and grid_info_current["row"] == row_new 
                    and grid_info_current["column"] == column_new):
            continue
        else:
            DOWNSHIFT = 1 # FIXME make real navbar
            RIGHTSHIFT = 1 # first column for loading stuff
            button.grid(row=(i // num_columns)+ DOWNSHIFT, column=i % num_columns + RIGHTSHIFT, sticky="we")


if __name__ == "__main__":

    # run updater #

    pgw = pgwrapper.ProgressBarWrapper()
    pgw.new(app)

    # define data backend #
    #db = data_backend.LocalFS(None, None, "./install/", remote_root_dir="example_software_root")
    # db = data_backend.FTP(None, None, "./install/", server="ftp://192.168.1.132:2121",
    #                     remote_root_dir="/", progress_bar_wrapper=pgw, tkinter_root=app)

    if not os.path.isfile(CONFIG_FILE):
        get_config_inputs()

    # load config #
    with open(CONFIG_FILE) as f:

        config_loaded = json.load(f)

        # load login & install dir #
        user = config_loaded.get("User:")
        password = config_loaded.get("Password:")
        install_dir = config_loaded["Install dir:"]
        backend_type = config_loaded["Select option:"]
        hide_above_age = config_loaded.get("hide_above_age") or 100


        # fix abs path if not set #
        if os.path.abspath(install_dir):
            install_dir = os.path.join(os.getcwd(), install_dir)

        # get the secod part of the server string, then split once at first / to get path and prepend / again#
        if backend_type == "FTP/FTPS":
            remote_root_dir = "/" + config_loaded["Server/Path:"].split("://")[1].split("/", 1)[1]
            server = config_loaded["Server/Path:"][:-len(remote_root_dir)]
        elif backend_type == "HTTP/HTTPS":
            server = config_loaded["Server/Path:"]
            remote_root_dir = None
            if not any(server.startswith(s) for s in ["http://", "https://"]):
                server = "http://" + server
            #if not ":" in server.split("://")[1]:
            #    server = server + ":5000"
            print(server)
        elif backend_type == "Local Filesystem":
            remote_root_dir = config_loaded["Server/Path:"]
            server = None
        else:
            raise NotImplementedError("Unsupported Backend")

        # debug output #
        print(user, password, install_dir, remote_root_dir, server, config_loaded["Server/Path:"])

        # add db backend #
        if backend_type == "HTTP/HTTPS":
            db = data_backend.HTTP(user, password, install_dir, 
                                    remote_root_dir="./", server=server, progress_bar_wrapper=pgw,
                                    tkinter_root=app, hide_above_age=hide_above_age)
        elif backend_type == "FTP/FTPS":
            db = data_backend.FTP(user, password, install_dir, server=server,
                remote_root_dir=remote_root_dir, progress_bar_wrapper=pgw, tkinter_root=app)
        elif backend_type == "Local Filesystem":
            db = data_backend.LocalFS(user, password, install_dir, server=server,
                remote_root_dir=remote_root_dir, progress_bar_wrapper=pgw, tkinter_root=app)
        else:
            raise NotImplementedError("Unsupported Backend")

    # geometry is set at the very beginning #
    app.update()

    # fill and run app #
    try:
        load_main() # TODO add button to reopen config # TODO add button to purge cache/purge cache window # TODO show game size on remote
    except requests.exceptions.ConnectionError as e:
        app.withdraw()
        tkinter.messagebox.showerror("There was a connection problem", str(e))
    app.mainloop()
