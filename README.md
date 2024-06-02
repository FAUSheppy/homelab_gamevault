# Example Game
You can download the GNU GPL Licensed game "FreeDink" from [here](https://nextcloud.atlantishq.de/s/9T62K9WjpEt3AQ7) and put it into `example_software_root/FreeDink/main_dir" to test it out.

# TODO
- async load from remote, currently the who GUI blocks during the loading process

# Linux

    sudo mkdir -pm755 /etc/apt/keyrings
    sudo wget -O /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key
    chmod a+r /etc/apt/keyrings/*
    sudo wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/debian/dists/bullseye/winehq-bullseye.sources\n
    sudo apt update
    sudo dpkg --add-architecture i386 \n
    sudo apt install --install-recommends winehq-staging
    sudo apt install libgl1:i386 nvidia-driver-libs:i386
    sudo apt install python3 python3-pip python3-tk

    # non sudo in project #
    python -m pip install -r requirements.txt
    python client.py
