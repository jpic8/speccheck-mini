from checkspecs import get_path

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
logging.basicConfig(level=logging.INFO, format=' %(asctime)s -  %(levelname) s -  %(message)s')

WATCH_DIR = '/path/to/WATCH_directory/'

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
            # Take action when a file is first created
            time.sleep(2)
            logging.info(f'Recieved new file - {event.src_path}')
            get_path(str(event.src_path))
        elif event.event_type == 'moved':
            # Take action when a file is moved
            time.sleep(2)
            logging.info(f'Received move event - {event.src_path} to {event.dest_path}')
            get_path(str(event.dest_path))
        elif event.event_type == 'modified':
            logging.debug('Received modified event')
            return None

if __name__ == '__main__':
    w = Watcher()
    w.run()