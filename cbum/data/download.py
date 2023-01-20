"""
Installation:
1. Install youtube-dl (using pip is fine). https://github.com/ytdl-org/youtube-dl
2. Install pafy
"""
import os
from pytube import YouTube
import logging
from utils import LogicBlock, setup_logger




if __name__ == "__main__":
    setup_logger()
    logger = logging.getLogger()
    download_dir = os.path.abspath(os.path.join(os.getcwd(), "cbum/data/raw/"))
    """ TODO: writer a trawler that produces a list of URLs
    Alternatively, figure out youtube APIs and get more data.
    """
    manually_curated_urls = {
        "olympia_classic_2021.mp4": "https://www.youtube.com/watch?v=_4VRmEYFVcg",
    }
    for filename, url in manually_curated_urls.items():
        with LogicBlock(description=f"{url=}", logger=logger):
            video = YouTube(url)
            video.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc().first().download(output_path=download_dir, filename=filename)
