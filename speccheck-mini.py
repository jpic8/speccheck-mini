from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pymediainfo import MediaInfo
from pathlib import Path
import time
import logging
logging.basicConfig(level=logging.NOTSET, format=' %(asctime)s -  %(levelname) s -  %(message)s')

"""watches folder with Python Watchdog module for new files, 
inspects mp4 with MediaInfo for 1920x1080 sizing, 
then moves to PASS/FAIL folder based on that info"""

WATCH_DIR = './Submit/'
PASS_DIR = './PASS/'
FAIL_DIR = './FAIL/'

class App:

    def __init__(self, path):
        self.path = path
        self.media_item = MediaItem(self.path, track_width=None, track_height=None)

    def process_file(self):
        mp4 = self.media_item.create_new_media_object()
        if mp4.is_valid_resolution():
            mp4.move_to_pass()
        else:
            mp4.move_to_fail()

class MediaItem:

    def __init__(self, path, track_width, track_height):
        self.path = path
        self.track_width = track_width
        self.track_height = track_height

    def create_new_media_object(self):
        media_info = MediaInfo.parse(self.path)
        for track in media_info.tracks:
            if track.track_type == 'Video':
                self.track_width = track.width
                self.track_height = track.height
        return self

    def is_valid_resolution(self):
        logging.info(f"{self.track_width}x{self.track_height}")
        if self.track_width == 1920 and self.track_height == 1080:
            logging.info('1920x1080 detected, moving to PASS folder')
            return True
        else:
            logging.info('video is NOT 1920x1080, moving to FAIL folder')
            return False

    def move_to_pass(self):
        p = Path(f'{self.path}')
        logging.info(f'Moving {p.stem}{p.suffix} to PASS folder')
        p.rename(PASS_DIR+p.stem+p.suffix)

    def move_to_fail(self):
        p = Path(f'{self.path}')
        logging.info(f'Moving {p.stem}{p.suffix} to FAIL folder')
        p.rename(FAIL_DIR+p.stem+p.suffix)

class Watcher:
    
    DIRECTORY_TO_WATCH = WATCH_DIR

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        logging.info('Starting queue monitor')
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            self.observer.stop()
            logging.info('Stopping queue monitor')
        self.observer.join()

class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            time.sleep(2)
            logging.info(f'checking directory event for new files')
            check_directory_for_files(str(event.src_path))
        elif event.event_type == 'created':
            time.sleep(2)
            logging.info(f'Received new file - {event.src_path}')
            check_for_submit_folder(str(event.src_path))
        elif event.event_type == 'moved':
            time.sleep(2)
            logging.info(f'Received move event - {event.src_path} to {event.dest_path}')
            check_for_submit_folder(str(event.dest_path))
        elif event.event_type == 'modified':
            logging.debug('Received modified event')
            return None

def check_for_submit_folder(path):
    p = Path(path)
    substring = ('/Submit')
    if substring in (str(p)) and p.suffix == '.mp4':
        logging.info('Received new file - PROCESSING')
        a = App(path)
        a.process_file()
    else:
        logging.info('Received new file NOT in Submit folder - IGNORE')
        return None

def check_directory_for_files(path):
    p = Path(path)
    for file in list(p.glob('*.mp4')):
        logging.info('Received new file from folder action - PROCESSING')
        a = App(file)
        a.process_file()

if __name__ == '__main__':
    w = Watcher()
    w.run()