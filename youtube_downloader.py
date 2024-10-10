import os
import yt_dlp

# Function to download a single video
def download_video(video_url, save_path):
    ydl_opts = {
        'format': 'bestvideo[height<=1080]+bestaudio/best',
        'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

# Function to download a playlist
def download_playlist(playlist_url, save_path):
    ydl_opts = {
        'format': 'bestvideo[height<=1080]+bestaudio/best',
        'outtmpl': os.path.join(save_path, '%(playlist_index)s - %(title)s.%(ext)s'),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([playlist_url])

# Main program
def main():
    # Ask user to choose between video and playlist download
    print("Do you want to download a (1) Video or (2) Playlist?")
    choice = input("Enter 1 for Video, 2 for Playlist: ")

    # Ask for YouTube URL
    url = input("Enter the YouTube video or playlist URL: ")

    # Ask for the folder path to save the downloads
    save_path = input("Enter the folder path where you want to save the files: ")

    # Make sure the folder exists
    if not os.path.exists(save_path):
        print(f"Directory '{save_path}' does not exist. Please enter a valid folder path.")
        return

    # Download either video or playlist based on user choice
    if choice == "1":
        download_video(url, save_path)
    elif choice == "2":
        download_playlist(url, save_path)
    else:
        print("Invalid choice! Please enter 1 for Video or 2 for Playlist.")

if __name__ == "__main__":
    main()
