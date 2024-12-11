# we need a way to access files
# https://stackoverflow.com/questions/59268696/why-is-os-scandir-as-slow-as-os-listdir
# https://github.com/tuomaskivioja/File-Downloads-Automator/blob/main/fileAutomator.py

import os
from os import rename
from os.path import splitext, exists, join
from shutil import move
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import multiprocessing

# Helper Functions
def make_unique(dest, name):
    filename, extension = splitext(name)
    counter = 1
    while exists(f"{dest}/{name}"):
        name = f"{filename}({str(counter)}){extension}"
        counter += 1
    return name


def move_file(dest, entry, name):
    if exists(f"{dest}/{name}"):
        unique_name = make_unique(dest, name)
        newName = join(dest, unique_name)
        rename(entry, newName)
    else:
        move(entry, dest)


# Custom Event Handler
class FileMoverHandler(FileSystemEventHandler):
    def __init__(self, directories):
        self.directories = directories

    def on_modified(self, event):
        if event.is_directory:
            return
        self.check_and_move_files()

    def on_created(self, event):
        if event.is_directory:
            return
        self.check_and_move_files()

    def check_and_move_files(self):
        for folder, extensions, dest in self.directories:
            for entry in os.scandir(folder):
                if entry.is_file():
                    file_ext = splitext(entry.name)[1].lower()
                    if file_ext in extensions:
                        move_file(dest, entry.path, entry.name)


# Scansione iniziale
def initial_scan(directories):
    logging.info("Eseguendo la scansione iniziale...")
    for folder, extensions, dest in directories:
        for entry in os.scandir(folder):
            if entry.is_file():
                file_ext = splitext(entry.name)[1].lower()
                if file_ext in extensions:
                    logging.info(f"Movendo il file iniziale: {entry.name} -> {dest}")
                    move_file(dest, entry.path, entry.name)


# Directory Configuration
desktop_dir = '/Users/francescapagano/Desktop'
downloads_dir = '/Users/francescapagano/Downloads'
user_dir = '/Users/francescapagano'

img_dir = '/Users/francescapagano/Pictures'
image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".tiff", ".bmp", ".svg", ".ico"]

docs_dir = '/Users/francescapagano/Desktop/pdf'
document_extensions = [".doc", ".docx", ".odt", ".pdf", ".xls", ".xlsx", ".ppt", ".pptx"]

coding_dir = '/Users/francescapagano/Desktop/coding'
coding_extensions = [".ipynb", ".py", ".html", ".c", ".m",".cpp",".R", ".tex"]

TREd_printer_dir = '/Users/francescapagano/Desktop/3d_printer'
TREd_extensions = ['.stl']

books_dir = '/Users/francescapagano/Desktop/ebook'
books_extension = ['.epub']


directories = [
    (desktop_dir, image_extensions, img_dir),
    (desktop_dir, document_extensions, docs_dir),
    (desktop_dir, coding_extensions, coding_dir),
    (desktop_dir, books_extension, books_dir),
    (desktop_dir, TREd_extensions, TREd_printer_dir),

    (downloads_dir, image_extensions, img_dir),
    (downloads_dir, document_extensions, docs_dir),
    (downloads_dir, coding_extensions, coding_dir),
    (downloads_dir, books_extension, books_dir),
    (downloads_dir, TREd_extensions, TREd_printer_dir),

    (user_dir, image_extensions, img_dir),
    (user_dir, document_extensions, docs_dir),
    (user_dir, coding_extensions, coding_dir),
    (user_dir, books_extension, books_dir),
    (user_dir, TREd_extensions, TREd_printer_dir),


]



# Monitor Folder
def monitor_folder(folder, directories):
    event_handler = FileMoverHandler(directories)
    observer = Observer()
    observer.schedule(event_handler, folder, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print(f"Monitor stopped for folder: {folder}")
    observer.join()


if __name__ == "__main__":
    # Configurazione logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%d-%m-%Y %H:%M:%S')

    # Esegui la scansione iniziale
    initial_scan(directories)

    # Avvia il monitoraggio
    processes = []
    for folder in [desktop_dir, downloads_dir, user_dir]:
        p = multiprocessing.Process(target=monitor_folder, args=(folder, directories))
        processes.append(p)
        p.start()

    print("File monitor is now running.")
    for process in processes:
        process.join()
