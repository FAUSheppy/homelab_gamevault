import PIL
import tkinter
import customtkinter

def show_large_picture(app, path):
    '''Show a full-window version of the clicked picture'''
    pass

def create_details_page(app, software):
    '''Create the details page for a software and return its elements for later destruction'''

    elements = []

    img = PIL.Image.open(software.get_thumbnail())
    img = img.resize((200, 300))
    img = PIL.ImageTk.PhotoImage(img)

    # thumbnail image #
    thumbnail_image = customtkinter.CTkButton(app, text="", image=img, width=200, height=300,
                    command=lambda: show_large_picture(app, path))
    thumbnail_image.pack()
    elements.append(thumbnail_image)

    # title #
    title = customtkinter.CTkLabel(app, textvariable=software.title)
    title.pack()
    elements.append(title)

    # genre #
    genre = customtkinter.CTkLabel(app, textvariable=software.genre)
    genre.pack()
    elements.append(genre)

    # description #
    description = customtkinter.CTkTextbox(app)
    description.insert("0.0", software.description)
    description.pack()
    elements.append(description)

    # dependencies #
    dependencies = customtkinter.CTkTextbox(app)
    dependencies.insert("0.0", str(software.dependencies))
    description.pack()
    elements.append(description)

    # buttons #
    install_button = customtkinter.CTkButton(app, text="Install",
                        command=lambda: software.install(software))
    remove_button = customtkinter.CTkButton(app, text="Remove",
                        command=lambda: software.remove(software))

    install_button.pack()
    remove_button.pack()
    elements.append(install_button)
    elements.append(remove_button)

    # add other pictures #
    for path in software.pictures[1:]:
        img = PIL.Image.open(software.get_thumbnail())
        img = img.resize((200, 300))
        img = PIL.ImageTk.PhotoImage(img)
        extra_pic_button = customtkinter.CTkButton(app, text="", image=img, width=200, height=300,
                    command=lambda: show_large_picture(app, path))
        extra_pic_button.pack()
        elements.append(extra_pic_button)

    return elements
