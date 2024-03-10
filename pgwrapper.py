import customtkinter

class ProgressBarWrapper:
    '''Provide a progress bar wrapper, so PGs can be created and destroyed
    on the GUI level without affecting the references stored for updates
    in the DataBackend and Software Objects'''

    def __init__(self):
        self.progress_bar = None

    def new(self, tk_parent):
        self.progress_bar = customtkinter.CTkProgressBar(tk_parent)
        self.progress_bar["maximum"] = 10000
        self.progress_bar.set(0)
        return self.progress_bar
    
    def get_pb(self):
        if self.progress_bar:
            return self.progress_bar
        else:
            raise AssertionError("No progress bar in this wrapper created")