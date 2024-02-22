import tkinter
import customtkinter
import PIL
import data_backend

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()
app.geometry("720x780")
last_geometry = app.winfo_geometry()
app.title("Test")
app.update()

img = PIL.Image.open("test.jpg")
img = img.resize((200, 300))
img = PIL.ImageTk.PhotoImage(img)
#img = PIL.ImageTk.PhotoImage(file="test.jpg")

buttons = []

def switch_to_game_details(software):
    '''Switch to the details of the clicked tile'''
    pass

def create_main_window_tile(software):
    '''Create the main window tile'''

    button = customtkinter.CTkButton(app, image=img, width=200, height=300,
                                     command=lambda: switch_to_game_details(game),
                                     border_width=0, corner_radius=0, border_spacing=0,
                                     text="Test Title LOLOLOL",
                                     fg_color="transparent", compound="top", anchor="s")
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


if __init__ == "__main__":

    # define data backend #
    db = data_backend.LocalFS(None, None, "./cache", remote_root_dir="example_software_root")

    # create tiles from meta files #
    for software in db.find_all_metadata():
        create_main_window_tile(software)

    # set update listener & update positions #
    app.bind("<Configure>", update_button_positions)
    update_button_positions()

    # run app #
    app.mainloop()
