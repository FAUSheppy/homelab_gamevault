import os

def get_cache_size(directory="./cache"):

    '''check directory sizes and sum up'''
    print(directory)
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    
    # Convert bytes to gigabytes #
    total_size_gb = total_size / (1024 * 1024 * 1024)
    return total_size_gb