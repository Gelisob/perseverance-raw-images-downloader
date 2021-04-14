# perseverance-raw-images-downloader
Small Python script that lets you download the Raw Images from Mars 2020 Perseverance.


## Features

- Downloads both the Full and Thumbnail Images into separate folders.
- Keeps a list of the last downloaded images and skips them in the next run.
- Detailed output of the progress in the Terminal.


## Requirements

- A system running Python3 and Pip3
- Write permissions in the folder you plan to install the Script


## How to Install and use it
(Tested on Ubuntu 20.04 and Manjaro 21.0)

Step 1: Download or Clone the GitHub repository

Step 2: Navigate into `/perseverance-raw-images-downloader`

Step 3: To install the dependencies run `pip3 install -r requirements.txt`

Step 4: Start the downloader by running `python3 downloader.py`