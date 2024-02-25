import PIL
import tkinter
import customtkinter

def show_large_picture(app, path):
    '''Show a full-window version of the clicked picture'''
    pass

def create_details_page(app, software):
    '''Create the details page for a software and return its elements for later destruction'''

    elements = []

    if software.get_thumbnail():
        img = PIL.Image.open(software.get_thumbnail())
        img = img.resize((200, 300))
    else:
        img = PIL.Image.new('RGB', (200, 300))

    img = PIL.ImageTk.PhotoImage(img)

    # thumbnail image #
    thumbnail_image = customtkinter.CTkButton(app, text="", image=img, width=500, height=700,
                    command=lambda: show_large_picture(app, path))
    thumbnail_image.grid(column=0, row=0, padx=10, pady=10)
    elements.append(thumbnail_image)

    # fonts #
    title_font = customtkinter.CTkFont(family="Helvetica", size=29, weight="bold")
    genre_font = customtkinter.CTkFont(family="Helvetica", size=14, slant="italic")

    # info box #
    info_frame = customtkinter.CTkFrame(app)
    info_frame.grid(column=1, row=0, sticky="ns", padx=10, pady=10)

    # title #
    title = customtkinter.CTkLabel(info_frame, text=software.title, font=title_font)
    title.pack(anchor="w", side="top", padx=20, pady=10)
    print("Title:", software.title)
    elements.append(title)

    # genre #
    genre_text = "Genre: {}".format(software.genre)
    genre = customtkinter.CTkLabel(info_frame, text=genre_text, padx=20, font=genre_font)
    genre.pack(anchor="w", side="top")
    elements.append(genre)

    # description #
    description = customtkinter.CTkTextbox(info_frame, width=400, height=200)
    description.insert("0.0", software.description)
    description.pack(anchor="w", side="top", fill="both", padx=20, pady=15)
    elements.append(description)

    # dependencies #
    if software.dependencies:
        dependencies_text = ",".join(software.dependencies)
        dependencies = customtkinter.CTkLabel(info_frame, text=dependencies_text)
        dependencies.pack(anchor="w", side="top", padx=20)
        elements.append(dependencies)

    # buttons #
    install_button = customtkinter.CTkButton(info_frame, text="Install",
                        command=lambda: software.install())
    remove_button = customtkinter.CTkButton(info_frame, text="Remove",
                        command=lambda: software.remove())
    if software.run_exe:
        run_button = customtkinter.CTkButton(info_frame, text="Run",
                        command=lambda: software.run())
        run_button.pack(padx=10, pady=30, anchor="sw", side="left")
        elements.append(run_button)

    install_button.pack(padx=10, pady=30, anchor="sw", side="left")
    remove_button.pack(padx=10, pady=30, anchor="sw", side="left")
    elements.append(install_button)
    elements.append(remove_button)

    # add other pictures #
    i = 0
    for path in software.pictures[1:]:
        img = PIL.Image.open(path)
        img = img.resize((200, 300))
        img = PIL.ImageTk.PhotoImage(img)
        extra_pic_button = customtkinter.CTkButton(app, text="", image=img, width=200, height=300,
                    command=lambda: show_large_picture(app, path))
        extra_pic_button.grid(padx=10, pady=10, row=0, column=i)
        elements.append(extra_pic_button)
        i += 1

    return elements
