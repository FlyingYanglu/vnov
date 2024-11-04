import requests
from .chapterize import Book
import os
import pathlib

class Novel_Retriever():

    def __init__(self):
        pass

    def retrieve_novel(self, url, save_dir, book_name=None):
        response = requests.get(url)
        if not book_name:
            book_name = os.path.basename(url).split('.')[0]
        save_folder = os.path.join(save_dir, book_name)
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        save_path = os.path.join(save_folder, 'all.txt')
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return save_path
    
    def chapterize_novel(self, book_path, save_dir=None):
        if not save_dir:
            save_dir = os.path.dirname(book_path)
        book = Book(book_path)
        book.processBook(save_dir=save_dir)

    def process_book(self, url, save_dir):
        save_path = self.retrieve_novel(url, save_dir)
        self.chapterize_novel(save_path)


    


    


