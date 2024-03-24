import PIL

def smart_resize(img, height, width):
    '''Crop to aspect ratio and then resize'''

    current_height, current_width = img.size
    target_ratio = height/width
    current_ratio = current_height/current_width

    if current_ratio > target_ratio:
        target_crop_height = current_width*target_ratio
        diff = current_height - target_crop_height
        img = img.crop((diff/2, 0, current_height-diff/2, current_width))
    elif current_ratio < target_ratio:
        target_crop_width = current_height/target_ratio
        diff = current_width - target_crop_width
        img = img.crop((0, diff/2, current_height, current_width-diff/2))

    img = img.resize((height, width))
    return img