from pytube import YouTube
from utils.utils import Path
import shutil
import os
import re


class VideoManger:
    def __init__(self):
        p = Path()

    def download_video(self, video_url: str, file_extension="mp4"):
        stream = (
            YouTube(video_url)
            .streams.filter(file_extension=file_extension, resolution="720p")
            .first()
        )
        title = self.sanitize_file_name(stream.title)
        stream.download(
            output_path="assets/downloads", filename=f"{title}.{file_extension}"
        )
        return title

    def from_downloads_to_storage(self, video_name: str):
        downloads_path = self.p.get_downloads_path(f"{video_name}.mp4")
        storage_path = self.p.get_assets_path(f"{video_name}.mp4")
        shutil.move(downloads_path, storage_path)
        print(f"Moved {downloads_path} to {storage_path}")

    def get_files_in_downloads(self):
        return os.listdir("assets/downloads")

    def sanitize_file_name(self, file_name: str):
        return re.sub(r"[^a-zA-Z0-9]+", "_", file_name)


if __name__ == "__main__":
    vm = VideoManger()
    print(vm.download_video("https://www.youtube.com/watch?v=d7nLiYN-PoM"))
