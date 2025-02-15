import PIL
import tkinter
import customtkinter
import imagetools
import os
import statekeeper

def show_large_picture(app, path):
    '''Show a full-window version of the clicked picture'''

    if not path:
        print("Genrated images cannot be enlarged.")
        return

    x = app.winfo_width()
    y = app.winfo_height()

    img = PIL.Image.open(path)
    img = imagetools.smart_resize(img, x-2*30, y-2*30)
    img = PIL.ImageTk.PhotoImage(img)

    large_image = customtkinter.CTkButton(app, text="", image=img, width=x-2*30, height=y-2*30,
                    fg_color="transparent", hover_color="black", corner_radius=0, border_width=0, border_spacing=0,
                    command=lambda: large_image.destroy())

    large_image.place(x=30, y=30)

def create_details_page(app, software, backswitch_function):
    '''Create the details page for a software and return its elements for later destruction'''

    elements = []

    if software.get_thumbnail():
        path = software.get_thumbnail()
        img = PIL.Image.open(path)
        img = imagetools.smart_resize(img, 500, 700)
    else:
        img = PIL.Image.new('RGB', (500, 700))
        path = None

    img = PIL.ImageTk.PhotoImage(img)

    # navbar #
    navbar = customtkinter.CTkFrame(app, fg_color="transparent")
    navbar.grid(column=0, row=0, padx=10, pady=5, sticky="ew")

    # back button
    back_button = customtkinter.CTkButton(navbar, text="Back", command=backswitch_function)
    back_button.pack(anchor="nw", side="left")

    # progress bar #
    #progress_bar = software.progress_bar_wrapper.new(navbar)
    #progress_bar.pack(anchor="nw", side="left", padx=20, pady=5)

    # progress bar text #
    #progress_text = software.progress_bar_wrapper.new_text(navbar)
    #progress_text.pack(anchor="nw", side="left", padx=20, pady=5)

    elements.append(navbar)
    elements.append(back_button)
    #elements.append(progress_bar)
    #elements.append(progress_text)

    # thumbnail image #
    thumbnail_image = customtkinter.CTkButton(app, text="", image=img, width=500, height=700,
                    fg_color="transparent", hover_color="black", corner_radius=0,
                    command=lambda path=path: show_large_picture(app, path))
    thumbnail_image.grid(column=0, row=1, padx=10)
    elements.append(thumbnail_image)

    # fonts #
    title_font = customtkinter.CTkFont(family="Helvetica", size=29, weight="bold")
    genre_font = customtkinter.CTkFont(family="Helvetica", size=14, slant="italic")

    # info box #
    info_frame = customtkinter.CTkFrame(app, width=500)
    info_frame.grid(column=1, row=1, sticky="nswe", padx=10)
    elements.append(info_frame)

    # title #
    title = customtkinter.CTkLabel(info_frame, text=software.title, font=title_font)
    title.grid(column=0, row=0, padx=20, pady=10, sticky="w")
    print("Title:", software.title)
    elements.append(title)

    # genre #
    genre_text = "Genre: {}".format(software.genre)
    genre = customtkinter.CTkLabel(info_frame, text=genre_text, padx=20, font=genre_font)
    genre.grid(column=0, row=1, sticky="w")
    elements.append(genre)

    # description #
    description = customtkinter.CTkTextbox(info_frame)
    description.insert("0.0", software.description)
    description.grid(column=0, row=2, padx=20, pady=15, sticky="we")
    elements.append(description)

    # registry modification #
    reg_mod_yes_no = "yes" if software.reg_files else "no"
    reg_mod_text = "Requires Registry Modification: {}".format(reg_mod_yes_no)
    reg_mod_info = customtkinter.CTkLabel(info_frame, text=reg_mod_text, padx=20)
    reg_mod_info.grid(column=0, row=3, sticky="w")
    elements.append(reg_mod_info)

    # dependencies #
    if software.dependencies:
        dependencies_text = "Dependencies: " + ",".join(software.dependencies)
        dependencies = customtkinter.CTkLabel(info_frame, text=dependencies_text)
        dependencies.grid(column=0, row=4, padx=20, sticky="w")
        elements.append(dependencies)

    # extra_files #
    if software.extra_files:
        extra_text = "Targets extra directories: " + ",".join(set(software.extra_files.values()))
        extra_text_label = customtkinter.CTkLabel(info_frame, text=extra_text)
        extra_text_label.grid(column=0, row=5, padx=20, sticky="w")
        elements.append(extra_text_label)

    # buttons #
    button_frame = customtkinter.CTkFrame(info_frame, fg_color="transparent")
    button_frame.grid(column=0, row=6, sticky="w")
    elements.append(button_frame)

    if software.link_only and "steam" in software.link_only:
        install_text = "Open Steam"
        remove_text = "Remove from Steam"
    elif software.link_only:
        install_text = "Open in Browser"
        remove_text = "Remove Manually"
    else:
        install_text = "Install"
        remove_text = "Remove (not implemented)" # FIXME: change text once implemented

    install_button = customtkinter.CTkButton(button_frame, text=install_text,
                        command=lambda: software.install_async())

    # add remove button #
    remove_button = customtkinter.CTkButton(button_frame, text=remove_text,
                    command=lambda: software.remove())

    if remove_text != "Remove":
        remove_button.configure(state=tkinter.DISABLED)
        remove_button.configure(fg_color="gray")

    # FIXME: disable remove button until implemented
    remove_button.configure(state=tkinter.DISABLED)

    remove_button.pack(padx=10, pady=15, anchor="sw", side="left")


    # run button #
    run_button = customtkinter.CTkButton(button_frame, text="Run",
                    command=lambda: software.run())
    run_button.pack(padx=10, pady=15, anchor="sw", side="left")
    software.run_button = run_button

    # install button #
    print(software.run_exe)
    print(os.path.join(software.backend.install_dir, software.run_exe or ""))
    if not software.run_exe or not (os.path.isfile(software.run_exe) 
            or os.path.isfile(os.path.join(software.backend.install_dir, software.title, software.run_exe))):
        run_button.configure(state=tkinter.DISABLED)
        run_button.configure(fg_color="gray")

    install_button.pack(padx=10, pady=15, anchor="sw", side="left")

    # add buttons #
    elements.append(install_button)
    elements.append(run_button)
    elements.append(remove_button)

    # add other pictures #
    if software.pictures:

        def callback_add_pictures():

            picture_frame = customtkinter.CTkScrollableFrame(info_frame, height=200, width=300, orientation="horizontal", fg_color="transparent")
            picture_frame.grid(column=0, row=7, sticky="we")

            i = 0
            print("Software pictures in callback:", software.pictures[1:])
            for path in software.pictures[1:]:

                print("Doing picture:", path)
                img = PIL.Image.open(software.backend.get(path))
                img = imagetools.smart_resize(img, 180, 180)
                img = PIL.ImageTk.PhotoImage(img)
                extra_pic_button = customtkinter.CTkButton(picture_frame, text="", image=img, command=lambda path=path: show_large_picture(app, path),
                                        hover_color="black", corner_radius=0,)
                extra_pic_button.configure(fg_color="transparent")
                extra_pic_button.grid(pady=10, row=0, column=i)
                elements.append(extra_pic_button)
                i += 1
            
            elements.append(picture_frame)

        statekeeper.add_to_task_queue(callback_add_pictures)

    return elements
