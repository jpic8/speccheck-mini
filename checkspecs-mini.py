from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pymediainfo import MediaInfo
from pathlib import Path
import time
import logging
logging.basicConfig(level=logging.INFO, format=' %(asctime)s -  %(levelname) s -  %(message)s')

"""watches folder with Python Watchdog module for new mp4 files, 
inspects media with MediaInfo for 1920x1080 sizing, 
then moves to PASS/FAIL folder based on that info"""

WATCH_DIR = './Submit/'
PASS_DIR = './PASS/'
FAIL_DIR = './FAIL/'

class App:

    def __init__(self, path):
        self.path = path
        self.media_item = MediaItem(self.path)

    def run_app(self):
        mp4 = self.media_item.create_new_media_object()
        if mp4.is_valid_resolution():
            mp4.move_to_pass()
        else:
            mp4.move_to_fail()

class MediaItem:

    def __init__(self, path):
        self.path = path
        self.track_width = None
        self.track_height = None

    def create_new_media_object(self):
        media_info = MediaInfo.parse(self.path)
        for track in media_info.tracks:
            if track.track_type == 'Video':
                self.track_width = track.width
                self.track_height = track.height
        logging.info(f'New file metadata captured')
        return self

    def is_valid_resolution(self):
        logging.info(f"{self.media_object.track_width}x{self.media_object.track_height}")
        if self.media_object.track_width == 1920 and self.media_object.track_height == 1080:
            logging.info('check_video_size - PASS, moving to PASS folder')
            return True
        else:
            logging.info('check_video_size - FAIL, moving to FAIL folder')
            return False

    def move_to_pass(self):
        p = Path(f'{self.path}')
        logging.info(f'Moving {p.stem}{p.suffix} to PASS folder')
        p.rename(PASS_DIR/p.stem+p.suffix)

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
            return None
        elif event.event_type == 'created':
            time.sleep(2)
            logging.info(f'Recieved new file - {event.src_path}')
            check_for_submit_folder(str(event.src_path))
        elif event.event_type == 'moved':
            time.sleep(2)
            logging.info(f'Received move event - {event.src_path} to {event.dest_path}')
            check_for_submit_folder(str(event.dest_path))
        elif event.event_type == 'modified':
            logging.debug('Received modified event')
            return None

def check_for_submit_folder(path):
    substring = ('/Submit')
    if substring in (path):
        logging.info('Received new file - PROCESSING')
        a = App(path)
        a.run_app()
    else:
        logging.info('Received new file NOT in Submit folder - IGNORE')
        return None

if __name__ == '__main__':
    w = Watcher()
    w.run()