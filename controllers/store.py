from typing import List, Optional, Dict, Any
from .book import Book
from .user import User

class LibraryStore:
    def __init__(self):
        self.books: List[Book] = []
        self.users: List[User] = []
        self.undo_stack: List[Dict[str, Any]] = []

    # --------- helpers ----------
    def find_book(self, book_id: str) -> Optional[Book]:
        return next((b for b in self.books if b.id == book_id), None)

    def find_user(self, user_id: str) -> Optional[User]:
        return next((u for u in self.users if u.id == user_id), None)

    # --------- commands ----------
    def add_book(self, book: Book) -> str:
        if self.find_book(book.id):
            return f"[X] Ya existe un libro con ID {book.id}."
        self.books.append(book)
        return f"[✓] Libro '{book.title}' agregado."

    def add_user(self, user: User) -> str:
        if self.find_user(user.id):
            return f"[X] Ya existe un usuario con ID {user.id}."
        self.users.append(user)
        return f"[✓] Usuario '{user.name}' agregado."

    def borrow_book(self, user_id: str, book_id: str) -> str:
        user = self.find_user(user_id); book = self.find_book(book_id)
        if not user: return f"[X] Usuario {user_id} no existe."
        if not book: return f"[X] Libro {book_id} no existe."
        if book.copies_available > 0:
            book.copies_available -= 1
            user.borrowed.append(book.id)
            self.undo_stack.append({"op": "borrow", "user_id": user_id, "book_id": book_id})
            return f"[✓] Préstamo exitoso: '{book.title}' para {user.name}. Disponibles: {book.copies_available}."
        else:
            if user_id in book.reservations:
                return f"[i] {user.name} ya está en la lista de espera de '{book.title}'."
            book.reservations.append(user_id)
            return f"[→] Sin copias. {user.name} quedó en cola para '{book.title}'. Posición: {len(book.reservations)}."

    def return_book(self, user_id: str, book_id: str) -> str:
        user = self.find_user(user_id); book = self.find_book(book_id)
        if not user: return f"[X] Usuario {user_id} no existe."
        if not book: return f"[X] Libro {book_id} no existe."
        if book_id not in user.borrowed: return f"[X] {user.name} no tiene prestado '{book.title}'."
        user.borrowed.remove(book_id); book.copies_available += 1
        autoloan_to_next = None
        if book.reservations:
            next_user_id = book.reservations.popleft()
            next_user = self.find_user(next_user_id)
            if next_user:
                book.copies_available -= 1
                next_user.borrowed.append(book.id)
                autoloan_to_next = next_user_id
                msg_auto = f" y asignado automáticamente a {next_user.name} por reserva."
            else:
                msg_auto = " (el siguiente en cola ya no existe)."
        else:
            msg_auto = ""
        self.undo_stack.append({"op": "return", "user_id": user_id, "book_id": book_id, "autoloan_to_next": autoloan_to_next})
        return f"[✓] Devolución de '{book.title}' registrada{msg_auto} Disponibles: {book.copies_available}."

    def undo_last(self) -> str:
        if not self.undo_stack: return "[i] No hay operaciones para deshacer."
        last = self.undo_stack.pop(); op = last.get("op")
        if op == "borrow":
            user = self.find_user(last["user_id"]); book = self.find_book(last["book_id"])
            if user and book and book.id in user.borrowed:
                user.borrowed.remove(book.id); book.copies_available += 1
                return f"[↶] Deshecho: préstamo de '{book.title}' a {user.name}."
            return "[X] No se pudo deshacer el préstamo."
        elif op == "return":
            user = self.find_user(last["user_id"]); book = self.find_book(last["book_id"])
            if not user or not book: return "[X] No se pudo deshacer la devolución."
            next_user_id = last.get("autoloan_to_next")
            if next_user_id:
                next_user = self.find_user(next_user_id)
                if next_user and book.id in next_user.borrowed:
                    next_user.borrowed.remove(book.id)
                    book.reservations.appendleft(next_user_id)
                    book.copies_available += 1
            if book.copies_available > 0:
                book.copies_available -= 1; user.borrowed.append(book.id)
                return f"[↶] Deshecho: devolución de '{book.title}' de {user.name}."
            return "[X] No se pudo deshacer: no hay copia disponible."
        else:
            return "[X] Operación desconocida en pila."
