import customtkinter

class ProgressBarWrapper:
    '''Provide a progress bar wrapper, so PGs can be created and destroyed
    on the GUI level without affecting the references stored for updates
    in the DataBackend and Software Objects'''

    def __init__(self):

        self.progress_bar = None
        self.progress_text = None
        self.tk_parent = None

    def update(self):

        if self.tk_parent:
            self.tk_parent.update_idletasks()

    def new(self, tk_parent):

        self.tk_parent = tk_parent
        self.progress_bar = customtkinter.CTkProgressBar(tk_parent, height=20, width=200)
        self.progress_bar["maximum"] = 10000
        self.progress_bar.set(0)

        return self.progress_bar

    def new_text(self, tk_parent):

        self.tk_parent = tk_parent
        self.progress_text = customtkinter.CTkLabel(tk_parent, height=20, width=130, text="")
        return self.progress_text
    
    def get_pb(self):

        if self.progress_bar:
            return self.progress_bar
        else:
            raise AssertionError("No progress bar in this wrapper created")

    def set_text(self, text):

        if self.progress_text:
            self.progress_text.configure(text=text)
        else:
            raise AssertionError("No progress text in this wrapper created")
