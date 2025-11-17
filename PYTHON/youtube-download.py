# Install --  pip3 install pipenv
# Install --- pipenv install pytube


from pytube import YouTube as yt
from pytube.cli import on_progress

try:
    # This will get the youtube video link from the user
    video_url = input('Enter the link of the video you want to download: ')

    # Create a YouTube object using the URL
    # The on_progress_callback is a function that will be called to show download progress
    youtube_video = yt(video_url, on_progress_callback=on_progress)

    print(f"Fetching '{youtube_video.title}'...")

    # Get the highest resolution progressive stream (video + audio)
    # Filtering explicitly for progressive mp4 streams is more robust.
    download_stream = youtube_video.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

    if not download_stream:
        print("No progressive stream available. Please try another video.")
    else:
        print(f"Downloading '{youtube_video.title}' ({download_stream.resolution}, {download_stream.filesize_mb:.2f}MB)...")
    # You can specify a download location like: download_stream.download('/path/to/directory')
        download_stream.download()
        print("\nDownload completed successfully!")

except Exception as e:
    print(f"\nAn error occurred: {e}")
    print("This might be due to an update on YouTube's side.")
    print("Please try updating pytube with: pip install --upgrade pytube")