# YouTube Video Downloader

A simple Python application that allows users to download YouTube videos and playlists in high quality (up to 1080p) to a specified local directory.

## Features

- Download individual YouTube videos or entire playlists.
- Save videos in 1080p quality with a user-defined file path.
- Maintain the order of videos in playlists by numbering them according to their sequence in the playlist.

## Requirements

- Python 3.x
- `yt_dlp` library for downloading videos.

## Installation

### Step 1: Clone the Repository

Open your terminal or command prompt and clone the repository using the following command:

```bash
git clone https://github.com/devang-bhardwaj/Youtube_Videos_and_Playlist_Downloader.git
```

### Step 2: Navigate to the Project Directory

Change your working directory to the project folder:

```bash
cd Youtube_Videos_and_Playlist_Downloader
```

### Step 3: Install Required Libraries

- Before running the application, you need to install the necessary libraries. This project uses pytube for downloading videos. You can install the required packages using the requirements.txt file.

- Install Libraries using requirements.txt

- Ensure you have pip installed. pip is included with Python installations.

Run the following command to install the required libraries:

```bash
pip install -r requirements.txt
```

### Step 4: Run the Program

Once the libraries are installed, you can run the application. Use the following command:

```bash
python youtube_downloader.py
```

### Usage Instructions-

1. Choose the Download Option: When prompted, enter 1 to download a single video or 2 to download a playlist.
2. Enter the URL: Provide the URL of the YouTube video or playlist you want to download.
3. Specify the Download Folder: Enter the path to the folder where you want the files to be saved.
4. Download Progress: The application will display the download progress in the terminal.
