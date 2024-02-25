import PIL

def load_and_keep_aspect_rescale(path, target_x, target_y):
    '''Load an image and resize it while keeping the aspect ratio (crop if it doesnt fit)'''

    img = PIL.Image.open(path)
    # get size 
    # img.size()

    img = img.resize((x-2*30, y-2*30))
    img = PIL.ImageTk.PhotoImage(img)