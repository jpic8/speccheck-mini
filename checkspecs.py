from pymediainfo import MediaInfo
from pathlib import Path
import logging
logging.basicConfig(level=logging.INFO, format=' %(asctime)s -  %(levelname) s -  %(message)s')

# pass and fail directories
PASS_DIR = '/path/to/PASS_directory/'
FAIL_DIR = '/path/to/FAIL_directory/'

# check for media in Submit folder
def get_path(path):
    substring = ('/Submit')
    if substring in (path):
        logging.info('Received new file - PROCESSING')
        m = MediaItem(path)
        m.create_new_media_object(path)
    else:
        logging.info('Received new file NOT in Submit folder - IGNORE')
        return None

# create new media object for inspection
class MediaItem:

    def __init__(self, path):
        self.path = path
        self.track_width = []
        self.track_height = []
        self.audio_channels = []

    def create_new_media_object(self, path):
        media_info = MediaInfo.parse(path)
        logging.info('create_new_media_object started')
        for track in media_info.tracks:
            if track.track_type == 'Video':
                self.track_width = track.width
                self.track_height = track.height
            elif track.track_type == 'Audio':
                self.audio_channels = track.channel_s
        logging.info(f'New file metadata captured')
        s = SpecChecker(self)
        s.check_video_size(self)

# check new media object for 1920x1080 video sizing
class SpecChecker:

    def __init__(self, media_object):
        self.media_object = media_object

    def check_video_size(self, media_object):
        logging.info(f"{media_object.track_width}x{media_object.track_height}")
        if media_object.track_width == 1920 and media_object.track_height == 1080:
            logging.info('check_video_size - PASS, moving to PASS folder')
            f = FileMover(media_object.path)
            f.pass_move(media_object.path)
        else:
            logging.info('check_video_size - FAIL, moving to FAIL folder')
            f = FileMover(media_object.path)
            f.fail_move(media_object.path)

# move file to PASS or FAIL folder depending on SpecChecker outcome
class FileMover:

    def __init__(self, path):
        self.path = path

    def pass_move(self, path):
        p = Path(f'{self.path}')
        logging.info(f'Moving {p.stem}{p.suffix} to PASS folder')
        p.rename(PASS_DIR+p.stem+p.suffix)

    def fail_move(self, path):
        p = Path(f'{self.path}')
        logging.info(f'Moving {p.stem}{p.suffix} to FAIL folder')
        p.rename(FAIL_DIR+p.stem+p.suffix)