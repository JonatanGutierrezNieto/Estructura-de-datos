from typing import Callable, Optional
from controllers.store import LibraryStore
from controllers.book import Book
from controllers.user import User

class LibraryController:
    """Cola de comandos entre la Vista (PyQt) y el Store (modelo)."""

    def __init__(self, store: Optional[LibraryStore] = None, logger: Optional[Callable[[str], None]] = None):
        self.store = store or LibraryStore()
        self._logger = logger or (lambda msg: None)

    # ------- utilidades --------
    def log(self, msg: str):
        self._logger(msg)

    # ------- operaciones -------
    def add_book(self, id_: str, title: str, author: str, year: int, copies: int):
        msg = self.store.add_book(Book(id=id_.strip(), title=title.strip(),
                                       author=author.strip(), year=year, copies_total=copies))
        self.log(msg)

    def add_user(self, id_: str, name: str, email: str):
        msg = self.store.add_user(User(id=id_.strip(), name=name.strip(), email=email.strip()))
        self.log(msg)

    def borrow(self, user_id: str, book_id: str):
        msg = self.store.borrow_book(user_id.strip(), book_id.strip())
        self.log(msg)

    def return_(self, user_id: str, book_id: str):
        msg = self.store.return_book(user_id.strip(), book_id.strip())
        self.log(msg)

    def undo(self):
        msg = self.store.undo_last()
        self.log(msg)

    # ------- datos para la vista -------
    def get_books(self):
        return self.store.books

    def get_users(self):
        return self.store.users

    # ------- datos de ejemplo -------
    def seed_sample_data(self):
        self.store.add_book(Book(id="B001", title="El Quijote", author="Cervantes", year=1605, copies_total=2))
        self.store.add_book(Book(id="B002", title="Cien años de soledad", author="García Márquez", year=1967, copies_total=1))
        self.store.add_user(User(id="U001", name="Ana", email="ana@example.com"))
        self.store.add_user(User(id="U002", name="Luis", email="luis@example.com"))
