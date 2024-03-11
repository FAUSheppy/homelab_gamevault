import customtkinter
import PIL
import data_backend
import client_details
import pgwrapper
import sys

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()

app.geometry("1030x770")
last_geometry = app.winfo_geometry()

buttons = []
details_elements = []

non_disabled_entry_color = None

def close_input_window(input_window):
    # Placeholder function for the button action
    print("Closing input window")
    input_window.quit()

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
    else:
        user_entry.configure(state=customtkinter.NORMAL)
        password_entry.configure(state=customtkinter.NORMAL)
        if non_disabled_entry_color: # else first run and nothing to do
            password_entry.configure(fg_color=non_disabled_entry_color)
            user_entry.configure(fg_color=non_disabled_entry_color)
        server_path_entry.delete(0, customtkinter.END)
        server_path_entry.insert(0, "ftp://server/path::port or ftps://server/path:port")

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
    dropdown_var = customtkinter.StringVar(value="Local Filesystem")
    dropdown_label = customtkinter.CTkLabel(input_window, text="Select option:")
    dropdown_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
    dropdown = customtkinter.CTkOptionMenu(input_window, variable=dropdown_var, values=["FTP/FTPS", "Local Filesystem"],
        command=lambda dropdown_var=dropdown_var, user_entry=user_entry, password_entry=password_entry,
                        server_path_entry=server_path_entry, install_dir_entry=install_dir_entry:
                        dropdown_changed(dropdown_var, user_entry, password_entry, server_path_entry, install_dir_entry))

    # set dropdown & field defaults
    dropdown_changed(dropdown_var, user_entry, password_entry, server_path_entry, install_dir_entry)
    dropdown.grid(row=0, column=1, padx=10, pady=5)

    # Button to save & close #
    save_button = customtkinter.CTkButton(input_window, text="Save & Close", command=lambda: close_input_window(input_window))
    save_button.grid(row=5, column=0, padx=10, pady=20)

    # Button to abort & close #
    abort_button = customtkinter.CTkButton(input_window, text="Abort", command=lambda: input_window.quit())
    abort_button.grid(row=5, column=2, padx=10, pady=20)

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

    app.title("Lan Vault: Overview")

    # create tiles from meta files #
    for software in db.find_all_metadata():
        create_main_window_tile(software)

    # set update listener & update positions #
    update_button_positions()
    app.bind("<Configure>", update_button_positions)

def destroy_main():
    '''Destroy all elements in the main view'''

    global buttons

    app.unbind("<Configure>")
    for b in buttons:
        b.destroy()
    
    buttons = []

def load_details(app, software):
    '''Load the details page for a software'''

    global details_elements

    app.title("Lan Vault: {}".format(software.title))
    details_elements = client_details.create_details_page(app, software, switch_to_main)

def create_main_window_tile(software):
    '''Create the main window tile'''

    if software.get_thumbnail():
        img = PIL.Image.open(software.get_thumbnail())
        img = img.resize((200, 300))
    else:
        img = PIL.Image.new('RGB', (200, 300))

    img = PIL.ImageTk.PhotoImage(img)
    button = customtkinter.CTkButton(app, image=img,
                                        width=200, height=300,
                                        command=lambda: switch_to_game_details(software),
                                        border_width=0, corner_radius=0, border_spacing=0,
                                        text=software.title,
                                        fg_color="transparent", compound="top", anchor="s")
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

    # Calculate the number of columns based on the current width of the window #
    num_columns = app.winfo_width() // 201  # Adjust 100 as needed for button width

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
            button.grid(row=i // num_columns, column=i % num_columns, sticky="we")


if __name__ == "__main__":

    pgw = pgwrapper.ProgressBarWrapper()
    pgw.new(app)
    # define data backend #
    #db = data_backend.LocalFS(None, None, "./install/", remote_root_dir="example_software_root")
    db = data_backend.FTP(None, None, "./install/", server="ftp://192.168.1.132:2121",
                            remote_root_dir="/", progress_bar_wrapper=pgw, tkinter_root=app) # TODO load values instead of hardcode

    get_config_inputs() # TODO save values

    # geometry is set at the very beginning #
    app.update()

    # fill and run app #
    load_main() # TODO add button to reopen config # TODO add button to purge cache/purge cache window # TODO show cache size # TODO show game size on remote
    app.mainloop()
