import shutil
import sqlite3

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QLabel, QTableWidget, QScrollArea, QMenuBar, QTableWidgetItem, QSizePolicy, \
    QFileDialog, QMessageBox

with open('style.css', 'r') as css:
    style = css.read()


class FunctionBase(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.connection = sqlite3.Connection("function_db.sqlite")
        self.cursor = self.connection.cursor()

        self.cursor.execute("""delete from last""")
        self.connection.commit()

        self.parent = parent

        self.is_choose_mode = True

        self.sort_type = '*'

        self.initUI()

    def initUI(self):
        self.setWindowTitle('База функций')
        self.setGeometry(400, 200, 750, 750)
        self.setMinimumSize(750, 750)
        self.setStyleSheet(style)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.move(100, 75)
        self.scroll_area.resize(550, 600)
        self.scroll_area.setWidgetResizable(True)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(('Функция', 'Тип'))
        self.table.setColumnWidth(0, 407)
        self.table.setColumnWidth(1, 100)

        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.scroll_area.setWidget(self.table)
        self.load()

        self.mode = QLabel('<html><head/><body><p><span style=" font-size:10pt; font-weight:600;"'
                           '>Режим выбора</span></p></body></html>', self)
        self.mode.move(50, 35)
        self.mode.resize(120, 20)

        self.menu = QMenuBar(self)

        self.file_menu = self.menu.addMenu('Файл')
        self.save = self.file_menu.addAction('Сохранить')
        self.save.setIcon(QIcon('iсons/save.png'))
        self.save.triggered.connect(self.saving)
        self.open = self.file_menu.addAction('Открыть')
        self.open.setIcon(QIcon('iсons/open.png'))
        self.open.triggered.connect(self.opening)

        self.mode_menu = self.menu.addMenu('Режим')
        self.choose_mode = self.mode_menu.addAction('Выбор')
        self.choose_mode.setIcon(QIcon('iсons/choose.png'))
        self.choose_mode.triggered.connect(self.change_mode)
        self.remove_mode = self.mode_menu.addAction('Удаление ️')
        self.remove_mode.setIcon(QIcon('iсons/remove.png'))
        self.remove_mode.triggered.connect(self.change_mode)

        self.actions_menu = self.menu.addMenu('Инструменты')
        self.clear_funcs = self.actions_menu.addAction('Очистить')
        self.clear_funcs.setIcon(QIcon('iсons/clear.png'))
        self.clear_funcs.triggered.connect(self.clearing)
        self.back = self.actions_menu.addAction('Вернуть последнее действие')
        self.back.setIcon(QIcon('iсons/back.png'))
        self.back.triggered.connect(self.backing)

        self.sort_menu = self.menu.addMenu('Сортировка')
        self.all = self.sort_menu.addAction('Все')
        self.all.triggered.connect(self.sorting)
        self.fx = self.sort_menu.addAction('f(x)')
        self.fx.triggered.connect(self.sorting)
        self.fy = self.sort_menu.addAction('f(y)')
        self.fy.triggered.connect(self.sorting)
        self.fxy = self.sort_menu.addAction('f(x, y)')
        self.fxy.triggered.connect(self.sorting)
        self.table.itemClicked.connect(self.interaction)

    def load(self):
        if self.sort_type == '*':
            res = self.cursor.execute("""select function, type from functions""").fetchall()
        else:
            res = self.cursor.execute("""
            select function, type 
            from functions
            where type = ?
            """, (self.sort_type, )).fetchall()
        self.table.setRowCount(0)
        for i, row in enumerate(res):
            self.table.setRowCount(
                self.table.rowCount() + 1)
            for j, elem in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(elem)))

    def saving(self):
        current_db_path = "function_db.sqlite"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить базу данных как",
            "function_database.sqlite",
            "SQLite Files (*.sqlite *.db);;All Files (*)"
        )

        if file_path:
            try:
                shutil.copy(current_db_path, file_path)
                QMessageBox.information(self, "Успех", "Файл успешно сохранен!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {e}")

    def opening(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл SQLite",
            "",
            "SQLite Databases (*.sqlite *.db);;All Files (*)"
        )

        if file_path:
            try:
                conn = sqlite3.Connection(file_path)
                cursor = conn.cursor()
                data = cursor.execute("""select function, type from functions""").fetchall()
                for func, type in data:
                    if str(type).strip() == 'f(x)':
                        if not str(func).strip().startswith('y = ') or str(func).count('y') > 1:
                            raise ValueError('f(x)')
                    elif str(type).strip() == 'f(y)':
                        if not str(func).strip().startswith('x = ') or str(func).count('x') > 1:
                            raise ValueError('f(y)')
                    elif str(type).strip() == 'f(x, y)':
                        if not str(func).strip().startswith('0 = '):
                            raise ValueError('f(x ,y)')
                    else:
                        raise TypeError(str(type))

                cursor.execute("""delete from last""")
                conn.commit()

                self.sort_type = '*'
                shutil.copy2(file_path, 'function_db.sqlite')
                self.load()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл: {e}")

    def change_mode(self):
        if self.sender() is self.choose_mode:
            text = 'Режим выбора'
            self.is_choose_mode = True
        else:
            text = 'Режим удаления'
            self.is_choose_mode = False
        self.mode.setText(f'<html><head/><body><p><span style=" font-size:10pt; font-weight:600;"'
                          f'>{text}</span></p></body></html>')

    def interaction(self, item):
        row = item.row()
        try:
            type = self.table.item(row, 1).text()
            text = self.table.item(row, 0).text()
        except Exception:
            self.connection.commit()
            self.table.setRowCount(0)
            self.load()
            return None

        self.parent.function.setText('')

        if self.is_choose_mode:
            if type == 'f(x)':
                self.parent.Fx.click()
            elif type == 'f(y)':
                self.parent.Fy.click()
            else:
                self.parent.Fxy.click()
            self.parent.function.setText(text[4:])
            self.parent.paint()

            self.close()

        else:
            if text in ('y = x',
                        'y = abs(x)',
                        'y = x ** 2',
                        'y = x ** 0.5',
                        'y = x ** 3',
                        'y = 1 / x',
                        'y = sin(x)',
                        'y = cos(x)',
                        'y = e ** x'):
                return None

            self.cursor.execute("""delete from last""")
            try:
                self.cursor.execute("""
                insert into last(function, type)
                values(?, ?)
                """, (text, type))
            except sqlite3.IntegrityError:
                self.connection.commit()
            self.cursor.execute("""
            delete from functions
            where function = ?
            """, (text, ))
            self.connection.commit()
            self.table.setRowCount(0)
            self.load()

    def clearing(self):
        self.cursor.execute("""delete from last""")
        funcs = self.cursor.execute("""
        select function, type
        from functions
        where id > 9
        """).fetchall()
        for function, type in funcs:
            self.cursor.execute("""
            insert into last(function, type)
            values (?, ?)
            """, (function, type))
        self.cursor.execute("""
        delete from functions
        where id > 9
        """)
        self.connection.commit()
        self.table.setRowCount(0)
        self.load()

    def backing(self):
        elems = self.cursor.execute("""
        select function, type
        from last
        """).fetchall()
        for elem in elems:
            try:
                self.cursor.execute("""
                insert into functions(function, type)
                values (?, ?)
                """, elem)
            except sqlite3.IntegrityError:
                self.connection.commit()
        self.cursor.execute("""delete from last""")
        self.connection.commit()
        self.table.setRowCount(0)
        self.load()

    def sorting(self):
        if self.sender() is self.all:
            self.sort_type = '*'
        else:
            self.sort_type = self.sender().text()
        self.table.setRowCount(0)
        self.load()

    def resizeEvent(self, event):
        x_center = self.size().width() // 2
        y_center = self.size().height() // 2

        self.scroll_area.move(x_center - 275, y_center - 300)

        self.mode.move(x_center - 325, y_center - 340)
