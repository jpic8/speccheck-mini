from pymediainfo import MediaInfo
from pathlib import Path
import logging
logging.basicConfig(level=logging.INFO, format=' %(asctime)s -  %(levelname) s -  %(message)s')
# set level=logging.NOTSET to see all logs, INFO to only see INFO, CRITICAL to see only critical

# pass and fail directories
PASS_DIR = './PASS/'
FAIL_DIR = './FAIL/'

# check if new media is in Submit folder
def submit_checker(path):
    substring = ('/Submit')
    if substring in (path):
        logging.info('Received new file - PROCESSING')
        m = MediaItem(path)
        m.create_new_media_object()
    else:
        logging.info('Received new file NOT in Submit folder - IGNORE')
        return None

# create new media object for inspection
class MediaItem:

    def __init__(self, path):
        self.path = path
        self.track_width = []
        self.track_height = []

    def create_new_media_object(self):
        media_info = MediaInfo.parse(self.path)
        for track in media_info.tracks:
            if track.track_type == 'Video':
                self.track_width = track.width
                self.track_height = track.height
        logging.info(f'New file metadata captured')
        s = SpecChecker(self)
        s.check_video_size()

# check new media object for 1920x1080 video sizing
class SpecChecker:

    def __init__(self, media_object):
        self.media_object = media_object

    def check_video_size(self):
        logging.info(f"{self.media_object.track_width}x{self.media_object.track_height}")
        if self.media_object.track_width == 1920 and self.media_object.track_height == 1080:
            logging.info('check_video_size - PASS, moving to PASS folder')
            f = FileMover(self.media_object.path)
            f.pass_move()
        else:
            logging.info('check_video_size - FAIL, moving to FAIL folder')
            f = FileMover(self.media_object.path)
            f.fail_move()

# move file to PASS or FAIL folder depending on SpecChecker result
class FileMover:

    def __init__(self, path):
        self.path = path

    def pass_move(self):
        p = Path(f'{self.path}')
        logging.info(f'Moving {p.stem}{p.suffix} to PASS folder')
        p.rename(PASS_DIR+p.stem+p.suffix)

    def fail_move(self):
        p = Path(f'{self.path}')
        logging.info(f'Moving {p.stem}{p.suffix} to FAIL folder')
        p.rename(FAIL_DIR+p.stem+p.suffix)