import os
import yt_dlp
import logging
from plyer import notification
import subprocess
from tqdm import tqdm
import requests

# Initialize logging
logging.basicConfig(filename='download.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function for desktop notifications
def notify(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=10
    )

# Function to update yt-dlp
def update_yt_dlp():
    try:
        subprocess.run(['pip', 'install', '--upgrade', 'yt-dlp'], check=True)
        print("yt-dlp has been updated to the latest version.")
    except Exception as e:
        logging.error(f"Failed to update yt-dlp: {e}")
        print(f"Failed to update yt-dlp: {e}")

# Function to download top pinned comment using requests
def get_pinned_comment(video_url):
    try:
        response = requests.get(video_url)
        # Placeholder for actual HTML parsing to extract the pinned comment
        # Implement parsing logic as needed
        pinned_comment = "Top pinned comment would be parsed here"
        return pinned_comment
    except Exception as e:
        logging.error(f"Failed to retrieve pinned comment for video {video_url}: {e}")
        return None

# Function for progress reporting (per video)
def progress_hook(tqdm_instance):
    def hook(d):
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes']:
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes', 0)
                progress = downloaded / total
                tqdm_instance.update(downloaded - tqdm_instance.n)
    return hook

# Function to download a single video with retries and metadata handling
def download_video(video_url, save_path, quality, download_metadata, retries=3):
    ydl_opts = {
        'format': quality,
        'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'writesubtitles': True,
        'subtitleslangs': ['en'],
        'continuedl': True,
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True
    }

    if download_metadata:
        ydl_opts['writeinfojson'] = True

    for attempt in range(1, retries + 1):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=True)
                title = info_dict.get('title', 'Unknown Title')
                description = info_dict.get('description', '')
                print(f"\nTitle: {title}")
                print(f"Description: {description}")

                if download_metadata:
                    pinned_comment = get_pinned_comment(video_url)
                    if pinned_comment:
                        print(f"Pinned Comment: {pinned_comment}")

            logging.info(f"Successfully downloaded video: {video_url}")
            notify("Download Complete", f"Video downloaded: {title}")
            break  # Exit loop if download is successful
        except yt_dlp.utils.DownloadError as e:
            logging.error(f"Attempt {attempt} failed for video {video_url}: {e}")
            if attempt < retries:
                print(f"Attempt {attempt} failed for video {video_url}. Retrying...")
            else:
                print(f"Failed to download video after {retries} attempts: {e}")
                logging.error(f"Download failed after {retries} attempts for video {video_url}")
                notify("Download Failed", f"Failed to download video: {video_url}")

# Function to download a playlist with range selection and error handling for unavailable videos
def download_playlist(playlist_url, save_path, quality, max_items=None, retries=3):
    ydl_opts = {
        'format': quality,
        'outtmpl': os.path.join(save_path, '%(playlist_index)s - %(title)s.%(ext)s'),  # Index for playlist
        'writesubtitles': True,
        'subtitleslangs': ['en'],
        'continuedl': True,
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True
    }

    # Retrieve playlist information without downloading
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        try:
            playlist_info = ydl.extract_info(playlist_url, download=False)
            entries = playlist_info.get('entries', [])
            available_entries = [video for video in entries if video and video.get('availability') == 'public']  # Only public videos
            total_videos = len(available_entries)
            print(f"Total available videos in playlist: {total_videos}")
        except yt_dlp.utils.DownloadError as e:
            logging.error(f"Failed to extract playlist info: {e}")
            print(f"Failed to extract playlist info: {e}")
            notify("Download Failed", f"Failed to extract playlist info: {playlist_url}")
            return

    # Prompt for video range
    try:
        start = int(input(f"Enter the starting video index (1 to {total_videos}): "))
        end_input = input(f"Enter the ending video index (1 to {total_videos}, or leave empty to download till the last): ")
        end = int(end_input) if end_input else total_videos

        if max_items and end > max_items:
            end = max_items

        selected_entries = available_entries[start - 1:end]
    except (ValueError, IndexError) as e:
        logging.error(f"Invalid range input: {e}")
        print(f"Invalid input for range: {e}")
        return

    # Initialize tqdm progress bar for the playlist
    with tqdm(total=len(selected_entries), desc="Downloading Playlist", unit="video") as pbar:
        for video in selected_entries:
            if video is None:
                logging.warning("Skipped an unavailable video.")
                pbar.set_postfix({"status": "Skipped unavailable video"})
                pbar.update(1)
                continue

            video_url = video.get('webpage_url')
            if not video_url:
                logging.warning("Skipped a video with no URL.")
                pbar.set_postfix({"status": "Skipped video with no URL"})
                pbar.update(1)
                continue

            try:
                print(f"\nDownloading video: {video.get('title', 'Unknown Title')}")
                download_video(video_url, save_path, quality, download_metadata=False, retries=retries)
                pbar.set_postfix({"status": "Downloaded"})
            except Exception as e:
                logging.error(f"Failed to download video {video_url}: {e}")
                pbar.set_postfix({"status": f"Failed: {e}"})
            finally:
                pbar.update(1)

    logging.info(f"Playlist download completed for URL: {playlist_url}")
    notify("Download Complete", f"Playlist downloaded: {playlist_url}")

# Function to download multiple videos via a list of URLs
def batch_download(urls, save_path, quality, download_metadata, retries=3):
    total_videos = len(urls)
    with tqdm(total=total_videos, desc="Batch Download", unit="video") as pbar:
        for i, video_url in enumerate(urls, start=1):  # Adding index with enumerate
            video_url = video_url.strip()
            if not video_url:
                pbar.set_postfix({"status": "Skipped empty URL"})
                pbar.update(1)
                continue
            
            # Adjust the outtmpl to include batch index for title prefix
            ydl_opts = {
                'format': quality,
                'outtmpl': os.path.join(save_path, f'{i:03d} - %(title)s.%(ext)s'),  # Index for batch download
                'writesubtitles': True,
                'subtitleslangs': ['en'],
                'continuedl': True,
                'merge_output_format': 'mp4',
                'quiet': True,
                'no_warnings': True
            }

            print(f"\nDownloading video {i}/{total_videos}: {video_url}")
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                pbar.set_postfix({"status": "Downloaded"})
            except Exception as e:
                logging.error(f"Failed to download video {video_url}: {e}")
                pbar.set_postfix({"status": f"Failed: {e}"})
            finally:
                pbar.update(1)

# Main program
def main():
    # Optionally update yt-dlp before running
    # update_yt_dlp()

    # Choose between video, playlist, or batch download
    print("Do you want to download a (1) Video, (2) Playlist, or (3) Batch of Videos?")
    choice = input("Enter 1 for Video, 2 for Playlist, or 3 for Batch: ").strip()

    # Get the folder path for saving downloads
    save_path = input("Enter the folder path where you want to save the files: ").strip()

    if not os.path.exists(save_path):
        print(f"Directory '{save_path}' does not exist. Please enter a valid folder path.")
        logging.error(f"Invalid save path: {save_path}")
        return

    # Select video quality
    print("\nSelect video quality:")
    print("1. Best Quality")
    print("2. 1080p")
    print("3. 720p")
    print("4. 480p")
    print("5. 360p")
    print("6. Worst Quality")
    quality_choice = input("Enter the quality option number (default: 1): ").strip() or '1'
    quality_mapping = {
        '1': 'best',
        '2': 'best[height<=1080]',
        '3': 'best[height<=720]',
        '4': 'best[height<=480]',
        '5': 'best[height<=360]',
        '6': 'worst'
    }
    quality = quality_mapping.get(quality_choice, 'best')

    # Download based on user's choice
    if choice == '1':
        video_url = input("Enter the video URL: ").strip()
        download_video(video_url, save_path, quality, download_metadata=True)

    elif choice == '2':
        playlist_url = input("Enter the playlist URL: ").strip()
        download_playlist(playlist_url, save_path, quality)

    elif choice == '3':
        batch_urls = input("Enter the video URLs separated by commas: ").strip().split(',')
        batch_download(batch_urls, save_path, quality, download_metadata=True)

    else:
        print("Invalid choice. Please select 1, 2, or 3.")
        logging.error(f"Invalid choice entered: {choice}")

if __name__ == "__main__":
    main()
