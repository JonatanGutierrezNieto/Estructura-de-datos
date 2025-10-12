import sys
from PyQt5.QtWidgets import (
    QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QListWidget, QMessageBox,
    QDesktopWidget, QTableWidget, QTableWidgetItem
)
from models.library_controller import LibraryController
from styles.style import APP_STYLESHEET, tune_table

class MainWindow(QWidget):
    def __init__(self, controller: LibraryController):
        super().__init__()
        self.controller = controller

        self.setWindowTitle("Sistema de Gestión de Biblioteca — Estructuras Lineales")
        self.resize(900, 560)
        self.center()
        self.setStyleSheet(APP_STYLESHEET)

        tabs = QTabWidget()
        tabs.addTab(self._tab_books(), "Libros")
        tabs.addTab(self._tab_users(), "Usuarios")
        tabs.addTab(self._tab_loans(), "Préstamos")

        lay = QVBoxLayout()
        lay.addWidget(tabs)
        self.setLayout(lay)

        # Seed
        self.controller.seed_sample_data()
        # Si estaba visible, refresca luego de seed:
        self.on_list_books()
        self.on_list_users()

    # ---------- utils ----------
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp); self.move(qr.topLeft())

    def _alert(self, text: str):
        QMessageBox.information(self, "Aviso", text)

    def _log(self, text: str):
        self.log.addItem(text); self.log.scrollToBottom()

    # ---------- pestaña Libros ----------
    def _tab_books(self):
        w = QWidget(); form = QFormLayout()
        self.book_id = QLineEdit();  self.book_title = QLineEdit()
        self.book_author = QLineEdit(); self.book_year = QLineEdit()
        self.book_copies = QLineEdit()
        form.addRow("ID:", self.book_id)
        form.addRow("Título:", self.book_title)
        form.addRow("Autor:", self.book_author)
        form.addRow("Año:", self.book_year)
        form.addRow("Copias totales:", self.book_copies)

        btn_add = QPushButton("Registrar libro")
        btn_add.clicked.connect(self.on_add_book)

        self.btn_list_books = QPushButton("Listar libros")
        self.btn_list_books.clicked.connect(self.on_toggle_list_books)

        self.book_filter = QLineEdit()
        self.book_filter.setPlaceholderText("Filtrar libros (ID, Título, Autor, Año, Totales, Disponibles, En cola)…")
        self.book_filter.textChanged.connect(self.filter_books_table)
        self.book_filter.setVisible(False)

        self.table_books = QTableWidget()
        self.table_books.setColumnCount(7)
        self.table_books.setHorizontalHeaderLabels(["ID", "Título", "Autor", "Año", "Totales", "Disponibles", "En cola"])
        tune_table(self.table_books)
        self.table_books.setVisible(False)

        col = QVBoxLayout()
        col.addLayout(form)
        col.addWidget(btn_add)
        col.addWidget(self.btn_list_books)
        col.addWidget(self.book_filter)
        col.addWidget(self.table_books)
        w.setLayout(col)
        return w

    # ---------- pestaña Usuarios ----------
    def _tab_users(self):
        w = QWidget(); form = QFormLayout()
        self.user_id = QLineEdit(); self.user_name = QLineEdit(); self.user_email = QLineEdit()
        form.addRow("ID:", self.user_id); form.addRow("Nombre:", self.user_name); form.addRow("Email:", self.user_email)

        btn_add = QPushButton("Registrar usuario")
        btn_add.clicked.connect(self.on_add_user)

        self.btn_list_users = QPushButton("Listar usuarios")
        self.btn_list_users.clicked.connect(self.on_toggle_list_users)

        self.user_filter = QLineEdit()
        self.user_filter.setPlaceholderText("Filtrar usuarios (ID, Nombre, Email o Prestados)…")
        self.user_filter.textChanged.connect(self.filter_users_table)
        self.user_filter.setVisible(False)

        self.table_users = QTableWidget()
        self.table_users.setColumnCount(4)
        self.table_users.setHorizontalHeaderLabels(["ID", "Nombre", "Email", "Prestados"])
        tune_table(self.table_users)
        self.table_users.setVisible(False)

        col = QVBoxLayout()
        col.addLayout(form)
        col.addWidget(btn_add)
        col.addWidget(self.btn_list_users)
        col.addWidget(self.user_filter)
        col.addWidget(self.table_users)
        w.setLayout(col)
        return w

    # ---------- pestaña Préstamos ----------
    def _tab_loans(self):
        w = QWidget(); form = QFormLayout()
        self.loan_user_id = QLineEdit(); self.loan_book_id = QLineEdit()
        form.addRow("ID Usuario:", self.loan_user_id)
        form.addRow("ID Libro:", self.loan_book_id)

        row_btns = QHBoxLayout()
        btn_borrow = QPushButton("Prestar");  btn_borrow.clicked.connect(self.on_borrow)
        btn_return = QPushButton("Devolver"); btn_return.clicked.connect(self.on_return)
        btn_undo   = QPushButton("Deshacer último"); btn_undo.clicked.connect(self.on_undo)
        row_btns.addWidget(btn_borrow); row_btns.addWidget(btn_return); row_btns.addWidget(btn_undo)

        self.log = QListWidget()

        col = QVBoxLayout()
        col.addLayout(form); col.addLayout(row_btns)
        col.addWidget(QLabel("Actividad:")); col.addWidget(self.log)
        w.setLayout(col); return w

    # ---------- acciones Libros ----------
    def on_add_book(self):
        try:
            y = int(self.book_year.text()); c = int(self.book_copies.text())
        except ValueError:
            self._alert("Año y copias deben ser números enteros."); return
        self.controller.add_book(self.book_id.text(), self.book_title.text(),
                                 self.book_author.text(), y, c)
        self.on_list_books()

    def on_toggle_list_books(self):
        if not self.table_books.isVisible():
            self.on_list_books()
            self.table_books.setVisible(True)
            self.book_filter.setVisible(True)
            self.book_filter.setFocus()
            self.btn_list_books.setText("Ocultar lista de libros")
        else:
            self.table_books.setVisible(False)
            self.book_filter.clear()
            self.book_filter.setVisible(False)
            self.btn_list_books.setText("Listar libros")

    def on_list_books(self):
        books = self.controller.get_books()
        self.table_books.setRowCount(len(books))
        for row, b in enumerate(books):
            data = [b.id, b.title, b.author, str(b.year),
                    str(b.copies_total), str(b.copies_available),
                    str(len(b.reservations))]
            for col, val in enumerate(data):
                self.table_books.setItem(row, col, QTableWidgetItem(val))
        if self.book_filter.isVisible() and self.book_filter.text().strip():
            self.filter_books_table(self.book_filter.text())

    def filter_books_table(self, text: str):
        text = text.strip().lower()
        rows = self.table_books.rowCount()
        for r in range(rows):
            show = not bool(text)
            if text:
                for c in range(self.table_books.columnCount()):
                    item = self.table_books.item(r, c)
                    if item and text in item.text().lower():
                        show = True; break
            self.table_books.setRowHidden(r, not show)

    # ---------- acciones Usuarios ----------
    def on_add_user(self):
        uid = self.user_id.text().strip(); name = self.user_name.text().strip(); email = self.user_email.text().strip()
        if not uid or not name or not email:
            self._alert("Todos los campos de usuario son obligatorios."); return
        self.controller.add_user(uid, name, email)
        self.on_list_users()

    def on_toggle_list_users(self):
        if not self.table_users.isVisible():
            self.on_list_users()
            self.table_users.setVisible(True)
            self.user_filter.setVisible(True)
            self.user_filter.setFocus()
            self.btn_list_users.setText("Ocultar lista de usuarios")
        else:
            self.table_users.setVisible(False)
            self.user_filter.clear()
            self.user_filter.setVisible(False)
            self.btn_list_users.setText("Listar usuarios")

    def on_list_users(self):
        users = self.controller.get_users()
        self.table_users.setRowCount(len(users))
        for row, u in enumerate(users):
            self.table_users.setItem(row, 0, QTableWidgetItem(u.id))
            self.table_users.setItem(row, 1, QTableWidgetItem(u.name))
            self.table_users.setItem(row, 2, QTableWidgetItem(u.email))
            prestados = ", ".join(u.borrowed) if u.borrowed else "—"
            self.table_users.setItem(row, 3, QTableWidgetItem(prestados))
        if self.user_filter.isVisible() and self.user_filter.text().strip():
            self.filter_users_table(self.user_filter.text())

    def filter_users_table(self, text: str):
        text = text.strip().lower()
        rows = self.table_users.rowCount()
        for r in range(rows):
            show = not bool(text)
            if text:
                for c in range(self.table_users.columnCount()):
                    item = self.table_users.item(r, c)
                    if item and text in item.text().lower():
                        show = True; break
            self.table_users.setRowHidden(r, not show)

    # ---------- acciones Préstamos ----------
    def on_borrow(self):
        uid = self.loan_user_id.text().strip(); bid = self.loan_book_id.text().strip()
        if not uid or not bid:
            self._alert("Debes indicar ID de usuario y de libro."); return
        self.controller.borrow(uid, bid)
        self.on_list_books(); self.on_list_users()

    def on_return(self):
        uid = self.loan_user_id.text().strip(); bid = self.loan_book_id.text().strip()
        if not uid or not bid:
            self._alert("Debes indicar ID de usuario y de libro."); return
        self.controller.return_(uid, bid)
        self.on_list_books(); self.on_list_users()

    def on_undo(self):
        self.controller.undo()
        self.on_list_books(); self.on_list_users()

    # ---------- hook para recibir logs del controller ----------
    def set_logger(self):
        # Inyecta el logger para que el controller escriba en la QListWidget
        self.controller._logger = self._log
