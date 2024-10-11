import os
import yt_dlp
import logging

# Initialize logging
logging.basicConfig(filename='link_extractor.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_video_links(playlist_url, output_file):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True  # This option extracts only the URLs without downloading
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Extract the playlist information
            playlist_info = ydl.extract_info(playlist_url, download=False)
            entries = playlist_info.get('entries', [])
            
            # Filter accessible video URLs
            accessible_urls = []
            for entry in entries:
                if 'url' in entry and entry.get('is_unavailable') is not True:  # Filter out unavailable videos
                    accessible_urls.append(entry['url'])

            # Save the accessible URLs to the output file
            if accessible_urls:
                with open(output_file, 'w') as f:
                    f.write(', '.join(accessible_urls))  # Save in a single line, separated by commas
                print(f"Successfully extracted {len(accessible_urls)} accessible video URLs to '{output_file}'.")
                logging.info(f"Successfully extracted {len(accessible_urls)} accessible video URLs.")
            else:
                print("No accessible videos found in the playlist.")
                logging.warning("No accessible videos found in the playlist.")

        except Exception as e:
            logging.error(f"Failed to extract video links: {e}")
            print(f"Error occurred while extracting video links: {e}")

def main():
    playlist_url = input("Enter the YouTube playlist URL: ").strip()
    output_file = input("Enter the output file path (e.g., links.txt): ").strip()

    if not os.path.exists(os.path.dirname(output_file)):
        print("Output directory does not exist. Please enter a valid path.")
        logging.error("Invalid output path: " + output_file)
        return

    extract_video_links(playlist_url, output_file)

if __name__ == "__main__":
    main()
