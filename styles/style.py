from PyQt5.QtWidgets import QTableWidget, QHeaderView

APP_STYLESHEET = """
QWidget { background-color: #F5F5DC; }  /* beige */
QPushButton {
    background-color: #32CD32;
    color: white;
    font-size: 15px;
    font-weight: bold;
    border-radius: 8px;
    padding: 8px 12px;
}
QPushButton:hover { background-color: #228B22; }
"""

def tune_table(table: QTableWidget):
    table.setAlternatingRowColors(True)
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    table.setSelectionBehavior(QTableWidget.SelectRows)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.horizontalHeader().setHighlightSections(False)
    table.setSortingEnabled(True)
