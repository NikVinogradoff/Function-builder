import sys
import sqlite3

from math import sin, cos, tan, log10, log2, pi, e, gamma, asin, acos, atan, erf, sinh, cosh, tanh, asinh, acosh, atanh

from PyQt6 import uic
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QPolygonF, QPixmap
from PyQt6.QtWidgets import QWidget, QApplication, QMainWindow, QColorDialog, QLabel, QRadioButton, QInputDialog, \
    QTableWidget, QScrollArea, QMenuBar, QTableWidgetItem, QSizePolicy

style = '''QPushButton:hover {
                    border: 2px solid #3498db;
                }

                QPushButton:pressed {
                    border: 2px solid #2980b9;
                }

                QLineEdit {
                    border: 1px solid #5ab2db;
                }

                QLineEdit:hover {
                    border: 2px solid #3498db;
                }

                QLineEdit:focus {
                    border: 2px solid #3498db;
                }'''


class Function_builder(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("Function_builder.ui", self)

        self.connection = sqlite3.Connection("function_db.sqlite")
        self.cursor = self.connection.cursor()

        self.setStyleSheet(style)

        self.func_color = QColor('red')
        self.func_pen = QPen(self.func_color, 2)

        self.axis_color = QColor('black')
        self.axis_pen = QPen(self.axis_color, 3)

        self.dotted_color = QColor(190, 190, 190)
        self.dotted_pen = QPen(self.dotted_color)
        self.dotted_pen.setStyle(Qt.PenStyle.DashLine)

        self.text_color = QColor('black')
        self.text_pen = QPen(self.text_color)

        self.center = [0, 0]
        self.delta = 1

        self.isdotted = True
        self.isaxis = True

        self.do_it = True

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Функциональный строитель')

        self.do_paint = False

        self.new_window_btn.setEnabled(False)
        self.new_window_btn.clicked.connect(self.new_window)

        self.instruction_btn.clicked.connect(self.instructor)

        self.open_bd_btn.clicked.connect(self.func_db)

        self.build_btn.clicked.connect(self.paint)

        self.Fx.click()
        self.Fx.clicked.connect(self.change_argument)
        self.Fy.clicked.connect(self.change_argument)
        self.Fxy.clicked.connect(self.change_argument)

        self.verticalSlider.setMinimum(0)
        self.verticalSlider.setMaximum(8)
        self.verticalSlider.setValue(3)
        self.verticalSlider.valueChanged.connect(self.change_size)

        self.up.clicked.connect(self.move_up)
        self.too_up.clicked.connect(self.move_too_up)

        self.down.clicked.connect(self.move_down)
        self.too_down.clicked.connect(self.move_too_down)

        self.left.clicked.connect(self.move_left)
        self.too_left.clicked.connect(self.move_too_left)

        self.right.clicked.connect(self.move_right)
        self.too_right.clicked.connect(self.move_too_right)

        self.change_color_btn.clicked.connect(self.change_color)
        self.dotted_line_btn.clicked.connect(self.dotted_line)
        self.axis_btn.clicked.connect(self.axis)
        self.return_to_zero_btn.clicked.connect(self.return_to_zero)

        self.lineal_func_btn.clicked.connect(self.base_func)
        self.module_func_btn.clicked.connect(self.base_func)
        self.quadratic_func_btn.clicked.connect(self.base_func)
        self.radical_func_btn.clicked.connect(self.base_func)
        self.cube_func_btn.clicked.connect(self.base_func)
        self.hyperbolic_func_btn.clicked.connect(self.base_func)
        self.sinus_func_btn.clicked.connect(self.base_func)
        self.cosine_func_btn.clicked.connect(self.base_func)
        self.exponent_func_btn.clicked.connect(self.base_func)

        self.function.setPlaceholderText("Введите f(x)...")
        self.function.setClearButtonEnabled(True)

    def instructor(self):
        self.instruct = Instruction()
        self.instruct.show()

    def new_window(self):
        self.built = Built_function(self)
        self.built.show()

    def func_db(self):
        self.db = Function_base(self)
        self.db.show()

    def paintEvent(self, event):
        if self.function.text().strip() != '' and not self.do_paint:
            self.function.setStyleSheet("background-color: white")
        elif self.function.text().strip() != '' and self.do_paint:
            if self.Fx.isChecked():
                func = 'f(x)'
                label = 'y = '
            elif self.Fy.isChecked():
                func = 'f(y)'
                label = 'x = '
            else:
                func = 'f(x, y)'
                label = '0 = '

            try:
                self.cursor.execute("""
                insert into functions(function, type)
                values(?, ?)
                """, (label + self.function.text(), func))
                self.connection.commit()
            except sqlite3.IntegrityError:
                self.connection.commit()

            qp = QPainter()
            qp.begin(self)
            self.build(qp)
            qp.end()
        elif self.do_paint and self.do_it:
            self.function.setStyleSheet(f"background-color: {QColor(255, 75, 60).name()}")
            self.new_window_btn.setEnabled(False)
        self.do_paint = False
        self.do_it = True

    def paint(self):
        self.update()
        self.do_paint = True

    def is_point_valid(self, x, y):
        text = self.function.text()
        func_x_max, func_x_min, func_y_max, func_y_min, func_x, func_y = '', '', '', '', '', ''
        delta = self.delta / 80

        for elem in text:
            if elem == 'x':
                func_x_max += f'({x + delta})'
                func_x_min += f'({x - delta})'
                func_x += f'({x})'
                func_y += f'({x})'
                func_y_max += f'({x})'
                func_y_min += f'({x})'
            elif elem == 'y':
                func_x_max += f'({y})'
                func_x_min += f'({y})'
                func_x += f'({y})'
                func_y += f'({y})'
                func_y_max += f'({y + delta})'
                func_y_min += f'({y - delta})'
            else:
                func_x_max += elem
                func_x_min += elem
                func_x += elem
                func_y += elem
                func_y_max += elem
                func_y_min += elem

        try:
            func_x_max = eval(func_x_max)
            func_x_min = eval(func_x_min)
            func_x = eval(func_x)
            func_y = eval(func_y)
            func_y_max = eval(func_y_max)
            func_y_min = eval(func_y_min)
        except Exception:
            return False

        is_complex = any((isinstance(func_x, complex),
                          isinstance(func_x_min, complex),
                          isinstance(func_x_max, complex),
                          isinstance(func_y, complex),
                          isinstance(func_y_max, complex),
                          isinstance(func_y_min, complex)))
        if is_complex:
            return False

        condition1 = func_x_max <= 0 <= func_x_min or func_x_max <= 0 <= func_x or func_x <= 0 <= func_x_min
        condition2 = func_x_max >= 0 >= func_x_min or func_x_max >= 0 >= func_x or func_x >= 0 >= func_x_min
        condition3 = func_y_max <= 0 <= func_y_min or func_y_max <= 0 <= func_y or func_y <= 0 <= func_y_min
        condition4 = func_y_max >= 0 >= func_y_min or func_y_max >= 0 >= func_y or func_y >= 0 >= func_y_min
        conditions = (condition1, condition2, condition3, condition4)
        if any(conditions):
            return True
        return False

    def get_arg(self, arg):
        function = list(self.function.text().lower())
        if self.Fx.isChecked():
            root = 'x'
        elif self.Fy.isChecked():
            root = 'y'
        for i in range(len(function)):
            if function[i] == root:
                function[i] = f'({str(arg)})'
        try:
            result = eval(''.join(function))
        except Exception:
            result = None
        return result

    def build_base(self, qp):
        if self.Fxy.isChecked():
            self.new_window_btn.setEnabled(False)
        else:
            self.new_window_btn.setEnabled(True)

        qp.setPen(QPen(QColor('grey'), 1))
        qp.drawPolygon(QPolygonF([QPointF(190, 170), QPointF(590, 170), QPointF(590, 570), QPointF(190, 570)]))

        if self.isdotted:
            qp.setPen(self.dotted_pen)
            for i in range(1, 10):
                qp.drawLine(QPointF(190 + i * 40, 170), QPointF(190 + i * 40, 570))
                qp.drawLine(QPointF(190, 170 + i * 40), QPointF(590, 170 + 40 * i))

        qp.setPen(self.axis_pen)
        if abs(self.center[1]) <= self.delta * 5:
            qp.drawLine(QPointF(190, 370 - (-self.center[1] / self.delta * 40)),
                        QPointF(590, 370 - (-self.center[1] / self.delta * 40)))
        if abs(self.center[0]) <= self.delta * 5:
            qp.drawLine(QPointF(390 + (-self.center[0] / self.delta * 40), 170),
                        QPointF(390 + (-self.center[0] / self.delta * 40), 570))

        for i in range(1, 10):
            if abs(self.center[1]) <= self.delta * 5:
                qp.drawLine(QPointF(190 + i * 40, 365 - (-self.center[1] / self.delta * 40)),
                            QPointF(190 + i * 40, 375 - (-self.center[1] / self.delta * 40)))
                qp.setPen(self.text_pen)
                qp.drawText(QPointF(190 + i * 40 + 3, 375 + self.center[1] / self.delta * 40 + 10),
                            str(round((i - 5 + self.center[0] / self.delta) * self.delta, 2)))
                qp.setPen(self.axis_pen)
            if abs(self.center[0]) <= self.delta * 5:
                qp.drawLine(QPointF(385 + (-self.center[0] / self.delta * 40), 570 - i * 40),
                            QPointF(395 + (-self.center[0] / self.delta * 40), 570 - i * 40))
                if i - 5 + self.center[1] / self.delta != 0:
                    qp.setPen(self.text_pen)
                    qp.drawText(QPointF(395 + (-self.center[0] / self.delta * 40), 582 - i * 40),
                                str(round((i - 5 + self.center[1] / self.delta) * self.delta, 2)))
                    qp.setPen(self.axis_pen)

        if abs(self.center[0]) <= self.delta * 5:
            qp.drawLine(QPointF(386 + (-self.center[0] / self.delta * 40), 176),
                        QPointF(391 + (-self.center[0] / self.delta * 40), 171))
            qp.drawLine(QPointF(395 + (-self.center[0] / self.delta * 40), 176),
                        QPointF(390 + (-self.center[0] / self.delta * 40), 171))
            qp.setPen(self.text_pen)
            qp.drawText(QPointF(400 + (-self.center[0] / self.delta * 40), 176), 'y')
            qp.setPen(self.axis_pen)
        if abs(self.center[1]) <= self.delta * 5:
            qp.drawLine(QPointF(585, 366 - (-self.center[1] / self.delta * 40)),
                        QPointF(590, 371 - (-self.center[1] / self.delta * 40)))
            qp.drawLine(QPointF(585, 375 - (-self.center[1] / self.delta * 40)),
                        QPointF(590, 370 - (-self.center[1] / self.delta * 40)))
            qp.setPen(self.text_pen)
            qp.drawText(QPointF(580, 385 - (-self.center[1] / self.delta * 40)), 'x')
            qp.setPen(self.axis_pen)

        qp.setPen(self.text_pen)
        for i in range(1, 10):
            if abs(-self.center[1]) > self.delta * 5:
                qp.drawText(QPointF(170 + i * 40, 570), str(round(self.center[0] + (i - 5) * self.delta, 2)))
            if abs(-self.center[0]) > self.delta * 5:
                qp.drawText(QPointF(570, 567 - i * 40), str(round(self.center[1] + (i - 5) * self.delta, 2)))

    def build(self, qp):
        self.build_base(qp)

        qp.setPen(self.func_pen)
        points = []

        if self.Fx.isChecked():
            for i in range(190, 591):
                try:
                    points.append(QPointF(i, -self.get_arg((i - 390) / 40 * self.delta + self.center[0]) *
                                          40 / self.delta + 370 + self.center[1] * 40 / self.delta))
                except Exception:
                    points.append(-1)

            for i in range(399):
                if points[i] == -1 or points[i + 1] == -1:
                    continue
                if 170 <= points[i].y() < 571 and 170 <= points[i + 1].y() < 571:
                    qp.drawLine(points[i], points[i + 1])
                elif 170 <= points[i].y() < 571 and points[i + 1].y() < 571:
                    qp.drawLine(points[i], QPointF(i + 190, 170))
                elif 170 <= points[i].y() < 571 and points[i + 1].y() >= 170:
                    qp.drawLine(points[i], QPointF(i + 190, 570))
                elif 170 <= points[i + 1].y() < 571 and points[i].y() < 571:
                    qp.drawLine(QPointF(i + 1 + 190, 170), points[i + 1])
                elif 170 <= points[i + 1].y() < 571 and points[i].y() >= 170:
                    qp.drawLine(QPointF(i + 1 + 190, 570), points[i + 1])

        elif self.Fy.isChecked():
            for i in range(170, 571):
                i = 571 - i - 1 + 170
                try:
                    points.append(QPointF(self.get_arg((i - 370) / 40 * self.delta + self.center[1]) *
                                          40 / self.delta + 390 - self.center[0] * 40 / self.delta, 571 - i - 1 + 170))
                except Exception:
                    points.append(-1)

            for i in range(399):
                if points[i] == -1 or points[i + 1] == -1:
                    continue
                if 190 <= points[i].x() < 591 and 190 <= points[i + 1].x() < 591:
                    qp.drawLine(points[i], points[i + 1])
                elif 190 <= points[i].x() < 591 and points[i + 1].x() < 591:
                    qp.drawLine(points[i], QPointF(190, 170 + i))
                elif 190 <= points[i].x() < 591 and points[i + 1].x() >= 190:
                    qp.drawLine(points[i], QPointF(590, 170 + i))
                elif 190 <= points[i + 1].x() < 591 and points[i].x() < 591:
                    qp.drawLine(QPointF(190, 170 + i + 1), points[i + 1])
                elif 190 <= points[i + 1].x() < 591 and points[i].x() >= 190:
                    qp.drawLine(QPointF(590, 170 + i + 1), points[i + 1])

        else:
            for x in range(190, 591):
                for y in range(170, 571):
                    point = QPointF(x, y)
                    if self.is_point_valid((x - 390) / 40 * self.delta + self.center[0],
                                           (370 - y) / 40 * self.delta + self.center[1]):
                        qp.drawPoint(point)

    def change_argument(self):
        self.do_it = False
        if self.Fxy.isChecked():
            arg = 'x'
            arg2 = 'y'
            self.function.setPlaceholderText(f"Введите f(x, y)...")
            self.label.setText(
                f'<html><head/><body><p><span style=" font-size:12pt;">0 = </span></p></body></html>')
            self.new_window_btn.hide()
        else:
            arg = self.sender().text()[2]
            args = ('x', 'y', 'x')
            arg2 = args[args.index(arg) + 1]
            self.function.setPlaceholderText(f"Введите f({arg})...")
            self.label.setText(
                f'<html><head/><body><p><span style=" font-size:12pt;">{arg2} = </span></p></body></html>')
            self.new_window_btn.show()

        if self.function.text().strip() != '' and not self.Fxy.isChecked():
            func = list(self.function.text().lower())
            for i in range(len(func)):
                if func[i] == arg2:
                    func[i] = arg
                elif func[i] == arg2.upper():
                    func[i] = arg.upper()
            self.function.setText(''.join(func))

        base_funcs = [self.lineal_func_btn, self.module_func_btn, self.quadratic_func_btn, self.radical_func_btn,
                      self.cube_func_btn, self.hyperbolic_func_btn,
                      self.sinus_func_btn, self.cosine_func_btn, self.exponent_func_btn]
        for function in base_funcs:
            func_text = list(function.text())[1:]
            for i in range(len(func_text)):
                if func_text[i] == arg2:
                    func_text[i] = arg
            function.setText(arg2 + ''.join(func_text))

        self.paint()

    def move_up(self):
        self.center[1] += self.delta
        self.paint()

    def move_too_up(self):
        self.center[1] += 5 * self.delta
        self.paint()

    def move_down(self):
        self.center[1] -= self.delta
        self.paint()

    def move_too_down(self):
        self.center[1] -= 5 * self.delta
        self.paint()

    def move_left(self):
        self.center[0] -= self.delta
        self.paint()

    def move_too_left(self):
        self.center[0] -= 5 * self.delta
        self.paint()

    def move_right(self):
        self.center[0] += self.delta
        self.paint()

    def move_too_right(self):
        self.center[0] += 5 * self.delta
        self.paint()

    def change_size(self):
        n = self.verticalSlider.value()
        sizes = (0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50)

        self.delta = sizes[n]
        self.paint()

    def return_to_zero(self):
        self.center = [0, 0]
        self.paint()

    def change_color(self):
        new_color = QColorDialog(self).getColor()
        if new_color.isValid():
            self.func_pen.setColor(new_color)
        self.paint()

    def dotted_line(self):
        if self.isdotted:
            self.dotted_line_btn.setText('вернуть пунктир')
            self.isdotted = False
        else:
            self.dotted_line_btn.setText('убрать пунктир')
            self.isdotted = True
        self.paint()

    def axis(self):
        if self.isaxis:
            self.axis_btn.setText('вернуть акцентирование')
            self.isaxis = False
            self.axis_pen.setWidth(1)
            self.func_pen.setWidth(1)
        else:
            self.axis_btn.setText('убрать акцентирование')
            self.isaxis = True
            self.axis_pen.setWidth(3)
            self.func_pen.setWidth(2)
        self.paint()

    def base_func(self):
        if self.Fxy.isChecked():
            self.function.setText(self.sender().text()[4:] + ' - y')
        else:
            self.function.setText(self.sender().text()[4:])
        self.paint()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_W:
            self.up.click()
        elif event.key() == Qt.Key.Key_S:
            self.down.click()
        elif event.key() == Qt.Key.Key_D:
            self.right.click()
        elif event.key() == Qt.Key.Key_A:
            self.left.click()

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0 and self.verticalSlider.value() != 8:
            self.verticalSlider.setValue(self.verticalSlider.value() + 1)
        elif event.angleDelta().y() < 0 and self.verticalSlider.value() != 0:
            self.verticalSlider.setValue(self.verticalSlider.value() - 1)
        event.accept()


class Instruction(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Инструкция')
        self.setGeometry(400, 400, 400, 350)

        self.instr = QLabel(self)
        self.instr.setText('В поле ввода использовать только\nвыбранные переменные.\n'
                           'Разрешено использование символов\n"+"  "-"  "*"  "/"  "**"  "(...)",\nфункций '
                           'из библиотеки math\nиз списка в виде: "function(...)"\nи функции abs() в виде: "abs(...)".'
                           '\nИсключения: "pi", "e".')
        self.instr.move(30, 10)
        self.instr.resize(270, 160)

        self.yes = '"sin", "cos", "tan",\n"log10", "log2",\n"pi", "e".\n   И другие'
        self.funcs = QLabel(f'Список \nразрешённых\nфункций из math:\n{self.yes}', self)
        self.funcs.move(280, 12)
        self.funcs.resize(120, 150)

        self.instr2 = QLabel('<html><head/><body><p><span style=" font-weight:600;">'
                             'Принцип работы</span></p></body></html>', self)
        self.instr2.move(50, 185)
        self.instr2.resize(105, 20)

        self.fx = QRadioButton('f(x)', self)
        self.fx.move(30, 220)
        self.fx.resize(40, 20)
        self.fx.click()
        self.fx.clicked.connect(self.example)

        self.fy = QRadioButton('f(y)', self)
        self.fy.move(90, 220)
        self.fy.resize(40, 20)
        self.fy.clicked.connect(self.example)

        self.fxy = QRadioButton('f(x, y)', self)
        self.fxy.move(150, 220)
        self.fxy.resize(50, 20)
        self.fxy.clicked.connect(self.example)

        self.example1 = QLabel('y = x ** 2 + 1    - можно', self)
        self.example1.move(40, 250)
        self.example1.resize(150, 20)

        self.example2 = QLabel('y = y ** 2 + 1    - нельзя', self)
        self.example2.move(40, 270)
        self.example2.resize(150, 20)

        self.example3 = QLabel('y = x ** 2 + y    - нельзя', self)
        self.example3.move(40, 290)
        self.example3.resize(150, 20)

        self.please = QLabel('<html><head/><body><p><span style=" font-size:11pt; font-weight:600;">'
                             'Убедительная просьба</span></p></body></html>', self)
        self.please.move(220, 150)

        self.pict = QLabel(self)
        self.pict.move(225, 175)
        self.pict.resize(170, 150)

        self.im = QPixmap('pishite_gramotno.jpg')
        self.pict.setPixmap(self.im)

    def example(self):
        if self.sender() is self.fy:
            self.example1.setText('x = x ** 2 + 1    - нельзя')
            self.example2.setText('x = y ** 2 + 1    - можно')
            self.example3.setText('x = x ** 2 + y    - нельзя')
        elif self.sender() is self.fx:
            self.example1.setText('y = x ** 2 + 1    - можно')
            self.example2.setText('y = y ** 2 + 1    - нельзя')
            self.example3.setText('y = x ** 2 + y    - нельзя')
        else:
            self.example1.setText('0 = x ** 2 + 1    - можно')
            self.example2.setText('0 = y ** 2 + 1    - можно')
            self.example3.setText('0 = x ** 2 + y    - можно')


class Built_function(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        uic.loadUi("built_function.ui", self)

        self.setStyleSheet(style)

        self.center = [self.parent.center[0], self.parent.center[1]]
        self.delta = self.parent.delta

        self.rev_color = QColor('blue')
        self.rev_pen = QPen(self.rev_color, self.parent.func_pen.width())

        self.line_color = QColor('grey')
        self.line_pen = QPen(self.line_color, self.parent.func_pen.width())

        self.der_color = QColor('#84101b')
        self.der_pen = QPen(self.der_color, self.parent.func_pen.width())

        self.int_color = QColor('#2caa61')
        self.int_pen = QPen(self.int_color, self.parent.func_pen.width())

        self.paint()

        self.do_x_line = False
        self.do_y_line = False

        self.initUI()

    def initUI(self):
        if self.parent.Fx.isChecked():
            self.setWindowTitle(f'y = {self.parent.function.text()}')
            self.arg_label.setText('при x = ')
            self.value_label.setText('y = ')
        elif self.parent.Fy.isChecked():
            self.setWindowTitle(f'x = {self.parent.function.text()}')
            self.arg_label.setText('при y = ')
            self.value_label.setText('x = ')
        self.setGeometry(400, 80, 900, 900)

        self.verticalSlider.setMinimum(0)
        self.verticalSlider.setMaximum(8)
        self.verticalSlider.setValue(self.parent.verticalSlider.value())
        self.verticalSlider.valueChanged.connect(self.change_size)

        self.border_radio.click()
        self.size_radio.clicked.connect(self.paint)
        self.border_radio.clicked.connect(self.paint)

        self.up.clicked.connect(self.move_up)
        self.too_up.clicked.connect(self.move_too_up)

        self.down.clicked.connect(self.move_down)
        self.too_down.clicked.connect(self.move_too_down)

        self.left.clicked.connect(self.move_left)
        self.too_left.clicked.connect(self.move_too_left)

        self.right.clicked.connect(self.move_right)
        self.too_right.clicked.connect(self.move_too_right)

        self.value_label.hide()

        self.change_revcolor_btn.clicked.connect(self.change_revcolor)

        self.change_dercolor_btn.clicked.connect(self.change_dercolor)

        self.change_intcolor_btn.clicked.connect(self.change_intcolor)

        self.return_to_zero_btn.clicked.connect(self.return_to_zero)

        self.build_checkbox.click()
        self.build_checkbox.clicked.connect(self.paint)

        self.build_reversed_checkbox.clicked.connect(self.paint)

        self.build_derivative_checkbox.clicked.connect(self.paint)

        self.build_integral_checkbox.clicked.connect(self.paint)

        self.change_linecolor_btn.clicked.connect(self.change_linecolor)

        self.build_x_btn.clicked.connect(self.build_x_line)
        self.build_y_btn.clicked.connect(self.build_y_line)

        self.find_btn.clicked.connect(self.get_value)
        self.value_begin = self.value_label.text()

        self.x_line.setClearButtonEnabled(True)
        self.y_line.setClearButtonEnabled(True)
        self.argument.setClearButtonEnabled(True)

        self.moving_btn.clicked.connect(self.moving)

    def paintEvent(self, event):
        if self.argument.text().strip() != '':
            self.argument.setStyleSheet("background-color: white")
        qp = QPainter()
        qp.begin(self)
        self.build(qp)
        qp.end()

    def paint(self):
        self.update()

    def get_arg(self, arg):
        function = list(self.parent.function.text().lower())
        if self.parent.Fx.isChecked():
            root = 'x'
        elif self.parent.Fy.isChecked():
            root = 'y'
        for i in range(len(function)):
            if function[i] == root:
                function[i] = f'({str(arg)})'
        try:
            result = eval(''.join(function))
        except Exception:
            result = None
        return result

    def get_derivative(self, arg):
        if self.border_radio.isChecked():
            delta = self.delta / 240
        else:
            delta = self.delta / 160

        x0, x1, x2 = arg, arg - delta, arg + delta
        y0, y1, y2 = self.get_arg(x0), self.get_arg(x1), self.get_arg(x2)

        if not all((x0, x1, x2, y0, y1, y2)):
            return None

        if (y0 - y1) / (x0 - x1) == -(self.get_arg(x2 + delta) - y0) / (x2 + delta - x0) != 0:
            return None

        return (y2 - y1) / (x2 - x1)

    def get_integral(self, arg, pre_int):
        if self.border_radio.isChecked():
            k = 120
        else:
            k = 80
        if arg == 0:
            return 0
        elif arg > 0:
            delta = self.get_arg(arg - self.delta / k) * self.delta / k * 2
            return pre_int + delta
        else:
            delta = self.get_arg(arg + self.delta / k) * self.delta / k * 2
            return pre_int - delta

    def build_base(self, qp):
        qp.setPen(QPen(QColor('grey'), 1))
        qp.drawPolygon(QPolygonF([QPointF(200, 100), QPointF(800, 100), QPointF(800, 700), QPointF(200, 700)]))

        if self.border_radio.isChecked():
            if self.parent.isdotted:
                qp.setPen(self.parent.dotted_pen)
                for i in range(1, 10):
                    qp.drawLine(QPointF(200 + i * 60, 100), QPointF(200 + i * 60, 700))
                    qp.drawLine(QPointF(200, 100 + i * 60), QPointF(800, 100 + 60 * i))

            qp.setPen(self.parent.axis_pen)
            if abs(self.center[1]) <= self.delta * 5:
                qp.drawLine(QPointF(200, 400 - (-self.center[1] / self.delta * 60)),
                            QPointF(800, 400 - (-self.center[1] / self.delta * 60)))
            if abs(self.center[0]) <= self.delta * 5:
                qp.drawLine(QPointF(500 + (-self.center[0] / self.delta * 60), 100),
                            QPointF(500 + (-self.center[0] / self.delta * 60), 700))

            for i in range(1, 10):
                if abs(self.center[1]) <= self.delta * 5:
                    qp.drawLine(QPointF(200 + i * 60, 395 - (-self.center[1] / self.delta * 60)),
                                QPointF(200 + i * 60, 405 - (-self.center[1] / self.delta * 60)))
                    qp.setPen(self.parent.text_pen)
                    qp.drawText(QPointF(200 + i * 60 + 3, 405 + self.center[1] / self.delta * 60 + 10),
                                str(round((i - 5 + self.center[0] / self.delta) * self.delta, 2)))
                    qp.setPen(self.parent.axis_pen)
                if abs(self.center[0]) <= self.delta * 5:
                    qp.drawLine(QPointF(495 + (-self.center[0] / self.delta * 60), 700 - i * 60),
                                QPointF(505 + (-self.center[0] / self.delta * 60), 700 - i * 60))
                    if i - 5 + self.center[1] / self.delta != 0:
                        qp.setPen(self.parent.text_pen)
                        qp.drawText(QPointF(505 + (-self.center[0] / self.delta * 60), 692 - i * 60),
                                    str(round((i - 5 + self.center[1] / self.delta) * self.delta, 2)))
                        qp.setPen(self.parent.axis_pen)

            if abs(self.center[0]) <= self.delta * 5:
                qp.drawLine(QPointF(496 + (-self.center[0] / self.delta * 60), 106),
                            QPointF(501 + (-self.center[0] / self.delta * 60), 101))
                qp.drawLine(QPointF(505 + (-self.center[0] / self.delta * 60), 106),
                            QPointF(500 + (-self.center[0] / self.delta * 60), 101))
                qp.setPen(self.parent.text_pen)
                qp.drawText(QPointF(510 + (-self.center[0] / self.delta * 60), 106), 'y')
                qp.setPen(self.parent.axis_pen)
            if abs(self.center[1]) <= self.delta * 5:
                qp.drawLine(QPointF(795, 396 - (-self.center[1] / self.delta * 60)),
                            QPointF(800, 401 - (-self.center[1] / self.delta * 60)))
                qp.drawLine(QPointF(795, 405 - (-self.center[1] / self.delta * 60)),
                            QPointF(800, 400 - (-self.center[1] / self.delta * 60)))
                qp.setPen(self.parent.text_pen)
                qp.drawText(QPointF(790, 415 - (-self.center[1] / self.delta * 60)), 'x')
                qp.setPen(self.parent.axis_pen)
            qp.setPen(self.parent.text_pen)

            for i in range(1, 10):
                if abs(-self.center[1]) > self.delta * 5:
                    qp.drawText(QPointF(180 + i * 60, 700), str(round(self.center[0] + (i - 5) * self.delta, 2)))
                if abs(-self.center[0]) > self.delta * 5:
                    qp.drawText(QPointF(780, 697 - i * 60), str(round(self.center[1] + (i - 5) * self.delta, 2)))
        else:
            if self.parent.isdotted:
                qp.setPen(self.parent.dotted_pen)
                for i in range(15):
                    qp.drawLine(QPointF(220 + i * 40, 100), QPointF(220 + i * 40, 700))
                    qp.drawLine(QPointF(200, 120 + i * 40), QPointF(800, 120 + 40 * i))

            qp.setPen(self.parent.axis_pen)
            if abs(self.center[1]) <= self.delta * 7.5:
                qp.drawLine(QPointF(200, 400 - (-self.center[1] / self.delta * 40)),
                            QPointF(800, 400 - (-self.center[1] / self.delta * 40)))
            if abs(self.center[0]) <= self.delta * 7.5:
                qp.drawLine(QPointF(500 + (-self.center[0] / self.delta * 40), 100),
                            QPointF(500 + (-self.center[0] / self.delta * 40), 700))

            for i in range(15):
                if abs(self.center[1]) <= self.delta * 7.5:
                    qp.drawLine(QPointF(220 + i * 40, 395 - (-self.center[1] / self.delta * 40)),
                                QPointF(220 + i * 40, 405 - (-self.center[1] / self.delta * 40)))
                    qp.setPen(self.parent.text_pen)
                    qp.drawText(QPointF(200 + i * 40 + 3, 405 + self.center[1] / self.delta * 40 + 15),
                                str(round((i - 7 + self.center[0] / self.delta) * self.delta, 2)))
                    qp.setPen(self.parent.axis_pen)
                if abs(self.center[0]) <= self.delta * 7.5:
                    qp.drawLine(QPointF(495 + (-self.center[0] / self.delta * 40), 680 - i * 40),
                                QPointF(505 + (-self.center[0] / self.delta * 40), 680 - i * 40))
                    if i - 7 + self.center[1] / self.delta != 0:
                        qp.setPen(self.parent.text_pen)
                        qp.drawText(QPointF(510 + (-self.center[0] / self.delta * 40), 687 - i * 40),
                                    str(round((i - 7 + self.center[1] / self.delta) * self.delta, 2)))
                        qp.setPen(self.parent.axis_pen)

            if abs(self.center[0]) <= self.delta * 7.5:
                qp.drawLine(QPointF(496 + (-self.center[0] / self.delta * 40), 106),
                            QPointF(501 + (-self.center[0] / self.delta * 40), 101))
                qp.drawLine(QPointF(505 + (-self.center[0] / self.delta * 40), 106),
                            QPointF(500 + (-self.center[0] / self.delta * 40), 101))
                qp.setPen(self.parent.text_pen)
                qp.drawText(QPointF(510 + (-self.center[0] / self.delta * 40), 106), 'y')
                qp.setPen(self.parent.axis_pen)
            if abs(self.center[1]) <= self.delta * 7.5:
                qp.drawLine(QPointF(795, 396 - (-self.center[1] / self.delta * 40)),
                            QPointF(800, 401 - (-self.center[1] / self.delta * 40)))
                qp.drawLine(QPointF(795, 405 - (-self.center[1] / self.delta * 40)),
                            QPointF(800, 400 - (-self.center[1] / self.delta * 40)))
                qp.setPen(self.parent.text_pen)
                qp.drawText(QPointF(790, 415 - (-self.center[1] / self.delta * 40)), 'x')
                qp.setPen(self.parent.axis_pen)

            qp.setPen(self.parent.text_pen)
            for i in range(1, 16):
                if abs(-self.center[1]) > self.delta * 7.5:
                    qp.drawText(QPointF(160 + i * 40, 700), str(round(self.center[0] + (i - 8) * self.delta, 2)))
                if abs(-self.center[0]) > self.delta * 7.5:
                    qp.drawText(QPointF(780, 714 - i * 40), str(round(self.center[1] + (i - 8) * self.delta, 2)))

    def build(self, qp):
        self.build_base(qp)
        points = []

        if self.border_radio.isChecked() and self.build_checkbox.isChecked():
            if self.do_x_line and self.x_line.text().strip() != '':
                try:
                    value = eval(self.x_line.text())
                except Exception:
                    pass
                if self.center[0] - self.delta * 5 <= value <= self.center[0] + self.delta * 5:
                    qp.setPen(self.line_pen)
                    qp.drawLine(QPointF((value - self.center[0]) / self.delta * 60 + 500, 100),
                                QPointF((value - self.center[0]) / self.delta * 60 + 500, 700))

            if self.do_y_line and self.y_line.text().strip() != '':
                try:
                    value = eval(self.y_line.text())
                except Exception:
                    pass
                if self.center[1] - self.delta * 5 <= value <= self.center[1] + self.delta * 5:
                    qp.setPen(self.line_pen)
                    qp.drawLine(QPointF(200, -(value - self.center[1]) / self.delta * 60 + 400),
                                QPointF(800, -(value - self.center[1]) / self.delta * 60 + 400))

            qp.setPen(self.parent.func_pen)
            if self.parent.Fx.isChecked():
                for i in range(200, 801):
                    try:
                        points.append(QPointF(i, -self.get_arg((i - 500) / 60 * self.delta + self.center[0]) *
                                              60 / self.delta + 400 + self.center[1] * 60 / self.delta))
                    except Exception:
                        points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if 100 <= points[i].y() < 701 and 100 <= points[i + 1].y() < 701:
                        qp.drawLine(points[i], points[i + 1])
                    elif 100 <= points[i].y() < 701 and points[i + 1].y() < 701:
                        qp.drawLine(points[i], QPointF(i + 200, 100))
                    elif 100 <= points[i].y() < 701 and points[i + 1].y() >= 100:
                        qp.drawLine(points[i], QPointF(i + 200, 700))
                    elif 100 <= points[i + 1].y() < 701 and points[i].y() < 701:
                        qp.drawLine(QPointF(i + 1 + 200, 100), points[i + 1])
                    elif 100 <= points[i + 1].y() < 701 and points[i].y() >= 100:
                        qp.drawLine(QPointF(i + 1 + 200, 700), points[i + 1])

            elif self.parent.Fy.isChecked():
                for i in range(100, 701):
                    i = 701 - i - 1 + 100
                    try:
                        points.append(QPointF(self.get_arg((i - 400) / 60 * self.delta + self.center[1]) * 60 /
                                              self.delta + 500 - self.center[0] * 60 / self.delta, 701 - i - 1 + 100))
                    except Exception:
                        points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if 200 <= points[i].x() < 801 and 200 <= points[i + 1].x() < 801:
                        qp.drawLine(points[i], points[i + 1])
                    elif 200 <= points[i].x() < 801 and points[i + 1].x() < 801:
                        qp.drawLine(points[i], QPointF(200, 100 + i))
                    elif 200 <= points[i].x() < 801 and points[i + 1].x() >= 200:
                        qp.drawLine(points[i], QPointF(800, 100 + i))
                    elif 200 <= points[i + 1].x() < 801 and points[i].x() < 801:
                        qp.drawLine(QPointF(200, 100 + i + 1), points[i + 1])
                    elif 200 <= points[i + 1].x() < 801 and points[i].x() >= 200:
                        qp.drawLine(QPointF(800, 100 + i + 1), points[i + 1])

        elif self.build_checkbox.isChecked():
            if self.do_x_line and self.x_line.text().strip() != '':
                try:
                    value = eval(self.x_line.text())
                except Exception:
                    pass
                if self.center[0] - self.delta * 7.5 <= value <= self.center[0] + self.delta * 7.5:
                    qp.setPen(self.line_pen)
                    qp.drawLine(QPointF((value - self.center[0]) / self.delta * 40 + 500, 100),
                                QPointF((value - self.center[0]) / self.delta * 40 + 500, 700))

            if self.do_y_line and self.y_line.text().strip() != '':
                try:
                    value = eval(self.y_line.text())
                except Exception:
                    pass
                if self.center[1] - self.delta * 7.5 <= value <= self.center[1] + self.delta * 7.5:
                    qp.setPen(self.line_pen)
                    qp.drawLine(QPointF(200, -(value - self.center[1]) / self.delta * 40 + 400),
                                QPointF(800, -(value - self.center[1]) / self.delta * 40 + 400))

            qp.setPen(self.parent.func_pen)
            if self.parent.Fx.isChecked():
                for i in range(200, 801):
                    try:
                        points.append(QPointF(i, -self.get_arg((i - 500) / 40 * self.delta + self.center[0]) *
                                              40 / self.delta + 400 + self.center[1] * 40 / self.delta))
                    except Exception:
                        points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if 100 <= points[i].y() < 701 and 100 <= points[i + 1].y() < 701:
                        qp.drawLine(points[i], points[i + 1])
                    elif 100 <= points[i].y() < 701 and points[i + 1].y() < 701:
                        qp.drawLine(points[i], QPointF(i + 200, 100))
                    elif 100 <= points[i].y() < 701 and points[i + 1].y() >= 100:
                        qp.drawLine(points[i], QPointF(i + 200, 700))
                    elif 100 <= points[i + 1].y() < 701 and points[i].y() < 701:
                        qp.drawLine(QPointF(i + 1 + 200, 100), points[i + 1])
                    elif 100 <= points[i + 1].y() < 701 and points[i].y() >= 100:
                        qp.drawLine(QPointF(i + 1 + 200, 700), points[i + 1])

            elif self.parent.Fy.isChecked():
                for i in range(100, 701):
                    i = 701 - i - 1 + 100
                    try:
                        points.append(QPointF(self.get_arg((i - 400) / 40 * self.delta + self.center[1]) * 40 /
                                              self.delta + 500 - self.center[0] * 40 / self.delta, 701 - i - 1 + 100))
                    except Exception:
                        points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if 200 <= points[i].x() < 801 and 200 <= points[i + 1].x() < 801:
                        qp.drawLine(points[i], points[i + 1])
                    elif 200 <= points[i].x() < 801 and points[i + 1].x() < 801:
                        qp.drawLine(points[i], QPointF(200, 100 + i))
                    elif 200 <= points[i].x() < 801 and points[i + 1].x() >= 200:
                        qp.drawLine(points[i], QPointF(800, 100 + i))
                    elif 200 <= points[i + 1].x() < 801 and points[i].x() < 801:
                        qp.drawLine(QPointF(200, 100 + i + 1), points[i + 1])
                    elif 200 <= points[i + 1].x() < 801 and points[i].x() >= 200:
                        qp.drawLine(QPointF(800, 100 + i + 1), points[i + 1])

        if self.build_derivative_checkbox.isChecked():
            self.build_derivative(qp)

        if self.build_integral_checkbox.isChecked():
            self.build_integral(qp)

        if self.build_reversed_checkbox.isChecked():
            self.build_reversed(qp)

    def build_reversed(self, qp):
        qp.setPen(self.rev_pen)
        points = []

        if self.border_radio.isChecked():
            if self.parent.Fy.isChecked():
                for i in range(200, 801):
                    try:
                        points.append(QPointF(i, -self.get_arg((i - 500) / 60 * self.delta + self.center[0]) *
                                              60 / self.delta + 400 + self.center[1] * 60 / self.delta))
                    except Exception:
                        points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if 100 <= points[i].y() < 701 and 100 <= points[i + 1].y() < 701:
                        qp.drawLine(points[i], points[i + 1])
                    elif 100 <= points[i].y() < 701 and points[i + 1].y() < 701:
                        qp.drawLine(points[i], QPointF(i + 200, 100))
                    elif 100 <= points[i].y() < 701 and points[i + 1].y() >= 100:
                        qp.drawLine(points[i], QPointF(i + 200, 700))
                    elif 100 <= points[i + 1].y() < 701 and points[i].y() < 701:
                        qp.drawLine(QPointF(i + 1 + 200, 100), points[i + 1])
                    elif 100 <= points[i + 1].y() < 701 and points[i].y() >= 100:
                        qp.drawLine(QPointF(i + 1 + 200, 700), points[i + 1])

            elif self.parent.Fx.isChecked():
                for i in range(100, 701):
                    i = 701 - i - 1 + 100
                    try:
                        points.append(QPointF(self.get_arg((i - 400) / 60 * self.delta + self.center[1]) * 60 /
                                              self.delta + 500 - self.center[0] * 60 / self.delta, 701 - i - 1 + 100))
                    except Exception:
                        points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if 200 <= points[i].x() < 801 and 200 <= points[i + 1].x() < 801:
                        qp.drawLine(points[i], points[i + 1])
                    elif 200 <= points[i].x() < 801 and points[i + 1].x() < 801:
                        qp.drawLine(points[i], QPointF(200, 100 + i))
                    elif 200 <= points[i].x() < 801 and points[i + 1].x() >= 200:
                        qp.drawLine(points[i], QPointF(800, 100 + i))
                    elif 200 <= points[i + 1].x() < 801 and points[i].x() < 801:
                        qp.drawLine(QPointF(200, 100 + i + 1), points[i + 1])
                    elif 200 <= points[i + 1].x() < 801 and points[i].x() >= 200:
                        qp.drawLine(QPointF(800, 100 + i + 1), points[i + 1])

        else:
            if self.parent.Fy.isChecked():
                for i in range(200, 801):
                    try:
                        points.append(QPointF(i, -self.get_arg((i - 500) / 40 * self.delta + self.center[0]) *
                                              40 / self.delta + 400 + self.center[1] * 40 / self.delta))
                    except Exception:
                        points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if 100 <= points[i].y() < 701 and 100 <= points[i + 1].y() < 701:
                        qp.drawLine(points[i], points[i + 1])
                    elif 100 <= points[i].y() < 701 and points[i + 1].y() < 701:
                        qp.drawLine(points[i], QPointF(i + 200, 100))
                    elif 100 <= points[i].y() < 701 and points[i + 1].y() >= 100:
                        qp.drawLine(points[i], QPointF(i + 200, 700))
                    elif 100 <= points[i + 1].y() < 701 and points[i].y() < 701:
                        qp.drawLine(QPointF(i + 1 + 200, 100), points[i + 1])
                    elif 100 <= points[i + 1].y() < 701 and points[i].y() >= 100:
                        qp.drawLine(QPointF(i + 1 + 200, 700), points[i + 1])

            elif self.parent.Fx.isChecked():
                for i in range(100, 701):
                    i = 701 - i - 1 + 100
                    try:
                        points.append(QPointF(self.get_arg((i - 400) / 40 * self.delta + self.center[1]) * 40 /
                                              self.delta + 500 - self.center[0] * 40 / self.delta, 701 - i - 1 + 100))
                    except Exception:
                        points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if 200 <= points[i].x() < 801 and 200 <= points[i + 1].x() < 801:
                        qp.drawLine(points[i], points[i + 1])
                    elif 200 <= points[i].x() < 801 and points[i + 1].x() < 801:
                        qp.drawLine(points[i], QPointF(200, 100 + i))
                    elif 200 <= points[i].x() < 801 and points[i + 1].x() >= 200:
                        qp.drawLine(points[i], QPointF(800, 100 + i))
                    elif 200 <= points[i + 1].x() < 801 and points[i].x() < 801:
                        qp.drawLine(QPointF(200, 100 + i + 1), points[i + 1])
                    elif 200 <= points[i + 1].x() < 801 and points[i].x() >= 200:
                        qp.drawLine(QPointF(800, 100 + i + 1), points[i + 1])

    def build_derivative(self, qp):
        qp.setPen(self.der_pen)
        points = []

        if self.border_radio.isChecked():
            if self.parent.Fx.isChecked():
                for i in range(200, 801):
                    try:
                        points.append(QPointF(i, -self.get_derivative((i - 500) / 60 * self.delta + self.center[0]) *
                                              60 / self.delta + 400 + self.center[1] * 60 / self.delta))
                    except Exception:
                        points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if 100 <= points[i].y() < 701 and 100 <= points[i + 1].y() < 701:
                        qp.drawLine(points[i], points[i + 1])
                    elif 100 <= points[i].y() < 701 and points[i + 1].y() < 701:
                        qp.drawLine(points[i], QPointF(i + 200, 100))
                    elif 100 <= points[i].y() < 701 and points[i + 1].y() >= 100:
                        qp.drawLine(points[i], QPointF(i + 200, 700))
                    elif 100 <= points[i + 1].y() < 701 and points[i].y() < 701:
                        qp.drawLine(QPointF(i + 1 + 200, 100), points[i + 1])
                    elif 100 <= points[i + 1].y() < 701 and points[i].y() >= 100:
                        qp.drawLine(QPointF(i + 1 + 200, 700), points[i + 1])

            elif self.parent.Fy.isChecked():
                for i in range(100, 701):
                    i = 701 - i - 1 + 100
                    try:
                        points.append(QPointF(self.get_derivative((i - 400) / 60 * self.delta + self.center[1]) * 60 /
                                              self.delta + 500 - self.center[0] * 60 / self.delta, 701 - i - 1 + 100))
                    except Exception:
                        points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if 200 <= points[i].x() < 801 and 200 <= points[i + 1].x() < 801:
                        qp.drawLine(points[i], points[i + 1])
                    elif 200 <= points[i].x() < 801 and points[i + 1].x() < 801:
                        qp.drawLine(points[i], QPointF(200, 100 + i))
                    elif 200 <= points[i].x() < 801 and points[i + 1].x() >= 200:
                        qp.drawLine(points[i], QPointF(800, 100 + i))
                    elif 200 <= points[i + 1].x() < 801 and points[i].x() < 801:
                        qp.drawLine(QPointF(200, 100 + i + 1), points[i + 1])
                    elif 200 <= points[i + 1].x() < 801 and points[i].x() >= 200:
                        qp.drawLine(QPointF(800, 100 + i + 1), points[i + 1])

        else:
            if self.parent.Fx.isChecked():
                for i in range(200, 801):
                    try:
                        points.append(QPointF(i, -self.get_derivative((i - 500) / 40 * self.delta + self.center[0]) *
                                              40 / self.delta + 400 + self.center[1] * 40 / self.delta))
                    except Exception:
                        points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if 100 <= points[i].y() < 701 and 100 <= points[i + 1].y() < 701:
                        qp.drawLine(points[i], points[i + 1])
                    elif 100 <= points[i].y() < 701 and points[i + 1].y() < 701:
                        qp.drawLine(points[i], QPointF(i + 200, 100))
                    elif 100 <= points[i].y() < 701 and points[i + 1].y() >= 100:
                        qp.drawLine(points[i], QPointF(i + 200, 700))
                    elif 100 <= points[i + 1].y() < 701 and points[i].y() < 701:
                        qp.drawLine(QPointF(i + 1 + 200, 100), points[i + 1])
                    elif 100 <= points[i + 1].y() < 701 and points[i].y() >= 100:
                        qp.drawLine(QPointF(i + 1 + 200, 700), points[i + 1])

            elif self.parent.Fy.isChecked():
                for i in range(100, 701):
                    i = 701 - i - 1 + 100
                    try:
                        points.append(QPointF(self.get_derivative((i - 400) / 40 * self.delta + self.center[1]) * 40 /
                                              self.delta + 500 - self.center[0] * 40 / self.delta, 701 - i - 1 + 100))
                    except Exception:
                        points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if 200 <= points[i].x() < 801 and 200 <= points[i + 1].x() < 801:
                        qp.drawLine(points[i], points[i + 1])
                    elif 200 <= points[i].x() < 801 and points[i + 1].x() < 801:
                        qp.drawLine(points[i], QPointF(200, 100 + i))
                    elif 200 <= points[i].x() < 801 and points[i + 1].x() >= 200:
                        qp.drawLine(points[i], QPointF(800, 100 + i))
                    elif 200 <= points[i + 1].x() < 801 and points[i].x() < 801:
                        qp.drawLine(QPointF(200, 100 + i + 1), points[i + 1])
                    elif 200 <= points[i + 1].x() < 801 and points[i].x() >= 200:
                        qp.drawLine(QPointF(800, 100 + i + 1), points[i + 1])

    def build_integral(self, qp):
        qp.setPen(self.int_pen)
        points = []

        if self.border_radio.isChecked():
            if self.parent.Fx.isChecked():
                if -5 * self.delta <= self.center[0] <= 5 * self.delta:
                    pre_int = 0
                    for i in range(200, int(500 - self.center[0] / self.delta * 60)):
                        i = 200 + int(500 - self.center[0] / self.delta * 60) - i - 1
                        try:
                            points.append(QPointF(i, -self.get_integral((i - 500) / 60 * self.delta + self.center[0],
                                                                        pre_int)
                                                  * 60 / self.delta + 400 + self.center[1] * 60 / self.delta))
                            pre_int = self.get_integral((i - 500) / 60 * self.delta + self.center[0], pre_int)
                        except Exception:
                            points.append(-1)
                    points.reverse()
                    points.append(QPointF(500 - self.center[0] * 60 / self.delta,
                                          400 + self.center[1] * 60 / self.delta))
                    pre_int = 0
                    for i in range(int(501 - self.center[0] / self.delta * 60), 801):
                        try:
                            points.append(QPointF(i, -self.get_integral((i - 500) / 60 * self.delta + self.center[0],
                                                                        pre_int)
                                                  * 60 / self.delta + 400 + self.center[1] * 60 / self.delta))
                            pre_int = self.get_integral((i - 500) / 60 * self.delta + self.center[0], pre_int)
                        except Exception:
                            points.append(-1)

                elif self.center[0] > 5 * self.delta:
                    pre_int = 0
                    for i in range(1, int(-(-self.center[0] + 5 * self.delta) * 60 // self.delta)):
                        pre_int = self.get_integral(i / 60 * self.delta, pre_int)

                    for i in range(200, 801):
                        try:
                            points.append(QPointF(i, -self.get_integral((i - 500) / 60 * self.delta + self.center[0],
                                                                        pre_int)
                                                  * 60 / self.delta + 400 + self.center[1] * 60 / self.delta))
                            pre_int = self.get_integral((i - 500) / 60 * self.delta + self.center[0], pre_int)
                        except Exception:
                            points.append(-1)

                else:
                    pre_int = 0
                    for i in range(-1, int((-self.center[0] - 5 * self.delta) * 60 // self.delta)):
                        pre_int = self.get_integral(i / 60 * self.delta, pre_int)

                    for i in range(200, 801):
                        i = 1000 - i
                        try:
                            points.append(QPointF(i, -self.get_integral((i - 500) / 60 * self.delta + self.center[0],
                                                                        pre_int)
                                                  * 60 / self.delta + 400 + self.center[1] * 60 / self.delta))
                            pre_int = self.get_integral((i - 500) / 60 * self.delta + self.center[0], pre_int)
                        except Exception:
                            points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if 100 <= points[i].y() < 701 and 100 <= points[i + 1].y() < 701:
                        qp.drawLine(points[i], points[i + 1])
                    elif 100 <= points[i].y() < 701 and points[i + 1].y() < 701:
                        qp.drawLine(points[i], QPointF(i + 200, 100))
                    elif 100 <= points[i].y() < 701 and points[i + 1].y() >= 100:
                        qp.drawLine(points[i], QPointF(i + 200, 700))
                    elif 100 <= points[i + 1].y() < 701 and points[i].y() < 701:
                        qp.drawLine(QPointF(i + 1 + 200, 100), points[i + 1])
                    elif 100 <= points[i + 1].y() < 701 and points[i].y() >= 100:
                        qp.drawLine(QPointF(i + 1 + 200, 700), points[i + 1])

            elif self.parent.Fy.isChecked():
                if -5 * self.delta <= self.center[1] <= 5 * self.delta:
                    pre_int = 0
                    for i in range(100, int(400 + self.center[1] / self.delta * 60)):
                        i = int(400 + self.center[1] / self.delta * 60) - i - 1 + 100
                        try:
                            points.append(QPointF(self.get_integral((400 - i) / 60 * self.delta + self.center[1],
                                                                    pre_int) * 60 /
                                                  self.delta + 500 - self.center[0] * 60 / self.delta, i))
                            pre_int = self.get_integral((400 - i) / 60 * self.delta + self.center[1], pre_int)
                        except Exception:
                            points.append(-1)
                    points.reverse()
                    points.append(QPointF(500 - self.center[0] * 60 / self.delta,
                                          400 + self.center[1] * 60 / self.delta))
                    pre_int = 0
                    for i in range(int(401 + self.center[1] / self.delta * 60), 701):
                        try:
                            points.append(QPointF(self.get_integral((400 - i) / 60 * self.delta + self.center[1],
                                                                    pre_int) * 60 /
                                                  self.delta + 500 - self.center[0] * 60 / self.delta, i))
                            pre_int = self.get_integral((400 - i) / 60 * self.delta + self.center[1], pre_int)
                        except Exception:
                            points.append(-1)

                elif self.center[1] > 5 * self.delta:
                    pre_int = 0
                    for i in range(1, int(-(-self.center[1] + 5 * self.delta) * 60 // self.delta)):
                        pre_int = self.get_integral(i / 60 * self.delta, pre_int)

                    for i in range(100, 701):
                        i = 800 - i
                        try:
                            points.append(QPointF(self.get_integral((400 - i) / 60 * self.delta + self.center[1],
                                                                    pre_int)
                                                  * 60 / self.delta + 500 - self.center[0] * 60 / self.delta, i))
                            pre_int = self.get_integral((400 - i) / 60 * self.delta + self.center[1], pre_int)
                        except Exception:
                            points.append(-1)

                else:
                    pre_int = 0
                    for i in range(-1, int((-self.center[1] - 5 * self.delta) * 60 // self.delta)):
                        pre_int = self.get_integral(i / 60 * self.delta, pre_int)

                    for i in range(100, 701):
                        try:
                            points.append(QPointF(self.get_integral((400 - i) / 60 * self.delta + self.center[1],
                                                                    pre_int)
                                                  * 60 / self.delta + 500 - self.center[0] * 60 / self.delta, i))
                            pre_int = self.get_integral((400 - i) / 60 * self.delta + self.center[1], pre_int)
                        except Exception:
                            points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if 200 <= points[i].x() < 801 and 200 <= points[i + 1].x() < 801:
                        qp.drawLine(points[i], points[i + 1])
                    elif 200 <= points[i].x() < 801 and points[i + 1].x() < 801:
                        qp.drawLine(points[i], QPointF(200, 100 + i))
                    elif 200 <= points[i].x() < 801 and points[i + 1].x() >= 200:
                        qp.drawLine(points[i], QPointF(800, 100 + i))
                    elif 200 <= points[i + 1].x() < 801 and points[i].x() < 801:
                        qp.drawLine(QPointF(200, 100 + i + 1), points[i + 1])
                    elif 200 <= points[i + 1].x() < 801 and points[i].x() >= 200:
                        qp.drawLine(QPointF(800, 100 + i + 1), points[i + 1])

        else:
            if self.parent.Fx.isChecked():
                if -7.5 * self.delta <= self.center[0] <= 7.5 * self.delta:
                    pre_int = 0
                    for i in range(200, int(500 - self.center[0] / self.delta * 40)):
                        i = 200 + int(500 - self.center[0] / self.delta * 40) - i - 1
                        try:
                            points.append(QPointF(i, -self.get_integral((i - 500) / 40 * self.delta + self.center[0],
                                                                        pre_int)
                                                  * 40 / self.delta + 400 + self.center[1] * 40 / self.delta))
                            pre_int = self.get_integral((i - 500) / 40 * self.delta + self.center[0], pre_int)
                        except Exception:
                            points.append(-1)
                    points.reverse()
                    points.append(QPointF(500 - self.center[0] * 40 / self.delta,
                                          400 + self.center[1] * 40 / self.delta))
                    pre_int = 0
                    for i in range(int(501 - self.center[0] / self.delta * 40), 801):
                        try:
                            points.append(QPointF(i, -self.get_integral((i - 500) / 40 * self.delta + self.center[0],
                                                                        pre_int)
                                                  * 40 / self.delta + 400 + self.center[1] * 40 / self.delta))
                            pre_int = self.get_integral((i - 500) / 40 * self.delta + self.center[0], pre_int)
                        except Exception:
                            points.append(-1)

                elif self.center[0] > 7.5 * self.delta:
                    pre_int = 0
                    for i in range(1, int(-(-self.center[0] + 7.5 * self.delta) * 40 // self.delta)):
                        pre_int = self.get_integral(i / 40 * self.delta, pre_int)

                    for i in range(200, 801):
                        try:
                            points.append(QPointF(i, -self.get_integral((i - 500) / 40 * self.delta + self.center[0],
                                                                        pre_int)
                                                  * 40 / self.delta + 400 + self.center[1] * 40 / self.delta))
                            pre_int = self.get_integral((i - 500) / 40 * self.delta + self.center[0], pre_int)
                        except Exception:
                            points.append(-1)

                else:
                    pre_int = 0
                    for i in range(-1, int((-self.center[0] - 7.5 * self.delta) * 40 // self.delta)):
                        pre_int = self.get_integral(i / 40 * self.delta, pre_int)

                    for i in range(200, 801):
                        i = 1000 - i
                        try:
                            points.append(QPointF(i, -self.get_integral((i - 500) / 40 * self.delta + self.center[0],
                                                                        pre_int)
                                                  * 40 / self.delta + 400 + self.center[1] * 40 / self.delta))
                            pre_int = self.get_integral((i - 500) / 40 * self.delta + self.center[0], pre_int)
                        except Exception:
                            points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if 100 <= points[i].y() < 701 and 100 <= points[i + 1].y() < 701:
                        qp.drawLine(points[i], points[i + 1])
                    elif 100 <= points[i].y() < 701 and points[i + 1].y() < 701:
                        qp.drawLine(points[i], QPointF(i + 200, 100))
                    elif 100 <= points[i].y() < 701 and points[i + 1].y() >= 100:
                        qp.drawLine(points[i], QPointF(i + 200, 700))
                    elif 100 <= points[i + 1].y() < 701 and points[i].y() < 701:
                        qp.drawLine(QPointF(i + 1 + 200, 100), points[i + 1])
                    elif 100 <= points[i + 1].y() < 701 and points[i].y() >= 100:
                        qp.drawLine(QPointF(i + 1 + 200, 700), points[i + 1])

            elif self.parent.Fy.isChecked():
                if -7.5 * self.delta <= self.center[1] <= 7.5 * self.delta:
                    pre_int = 0
                    for i in range(100, int(400 + self.center[1] / self.delta * 40)):
                        i = int(400 + self.center[1] / self.delta * 40) - i - 1 + 100
                        try:
                            points.append(QPointF(self.get_integral((400 - i) / 40 * self.delta + self.center[1],
                                                                    pre_int) * 40 /
                                                  self.delta + 500 - self.center[0] * 40 / self.delta, i))
                            pre_int = self.get_integral((400 - i) / 40 * self.delta + self.center[1], pre_int)
                        except Exception:
                            points.append(-1)
                    points.reverse()
                    points.append(QPointF(500 - self.center[0] * 40 / self.delta,
                                          400 + self.center[1] * 40 / self.delta))
                    pre_int = 0
                    for i in range(int(401 + self.center[1] / self.delta * 40), 701):
                        try:
                            points.append(QPointF(self.get_integral((400 - i) / 40 * self.delta + self.center[1],
                                                                    pre_int) * 40 /
                                                  self.delta + 500 - self.center[0] * 40 / self.delta, i))
                            pre_int = self.get_integral((400 - i) / 40 * self.delta + self.center[1], pre_int)
                        except Exception:
                            points.append(-1)

                elif self.center[1] > 7.5 * self.delta:
                    pre_int = 0
                    for i in range(1, int(-(-self.center[1] + 7.5 * self.delta) * 40 // self.delta)):
                        pre_int = self.get_integral(i / 40 * self.delta, pre_int)

                    for i in range(100, 701):
                        i = 800 - i
                        try:
                            points.append(QPointF(self.get_integral((400 - i) / 40 * self.delta + self.center[1],
                                                                    pre_int)
                                                  * 40 / self.delta + 500 - self.center[0] * 40 / self.delta, i))
                            pre_int = self.get_integral((400 - i) / 40 * self.delta + self.center[1], pre_int)
                        except Exception:
                            points.append(-1)

                else:
                    pre_int = 0
                    for i in range(-1, int((-self.center[1] - 7.5 * self.delta) * 40 // self.delta)):
                        pre_int = self.get_integral(i / 40 * self.delta, pre_int)

                    for i in range(100, 701):
                        try:
                            points.append(QPointF(self.get_integral((400 - i) / 40 * self.delta + self.center[1],
                                                                    pre_int)
                                                  * 40 / self.delta + 500 - self.center[0] * 40 / self.delta, i))
                            pre_int = self.get_integral((400 - i) / 40 * self.delta + self.center[1], pre_int)
                        except Exception:
                            points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if 200 <= points[i].x() < 801 and 200 <= points[i + 1].x() < 801:
                        qp.drawLine(points[i], points[i + 1])
                    elif 200 <= points[i].x() < 801 and points[i + 1].x() < 801:
                        qp.drawLine(points[i], QPointF(200, 100 + i))
                    elif 200 <= points[i].x() < 801 and points[i + 1].x() >= 200:
                        qp.drawLine(points[i], QPointF(800, 100 + i))
                    elif 200 <= points[i + 1].x() < 801 and points[i].x() < 801:
                        qp.drawLine(QPointF(200, 100 + i + 1), points[i + 1])
                    elif 200 <= points[i + 1].x() < 801 and points[i].x() >= 200:
                        qp.drawLine(QPointF(800, 100 + i + 1), points[i + 1])

    def move_up(self):
        self.center[1] += self.delta
        self.paint()

    def move_too_up(self):
        if self.border_radio.isChecked():
            self.center[1] += 5 * self.delta
        else:
            self.center[1] += 7.5 * self.delta
        self.paint()

    def move_down(self):
        self.center[1] -= self.delta
        self.paint()

    def move_too_down(self):
        if self.border_radio.isChecked():
            self.center[1] -= 5 * self.delta
        else:
            self.center[1] -= 7.5 * self.delta
        self.paint()

    def move_left(self):
        self.center[0] -= self.delta
        self.paint()

    def move_too_left(self):
        if self.border_radio.isChecked():
            self.center[0] -= 5 * self.delta
        else:
            self.center[0] -= 7.5 * self.delta
        self.paint()

    def move_right(self):
        self.center[0] += self.delta
        self.paint()

    def move_too_right(self):
        if self.border_radio.isChecked():
            self.center[0] += 5 * self.delta
        else:
            self.center[0] += 7.5 * self.delta
        self.paint()

    def change_size(self):
        n = self.verticalSlider.value()
        sizes = (0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50)

        self.delta = sizes[n]
        self.paint()

    def change_revcolor(self):
        new_color = QColorDialog(self).getColor()
        if new_color.isValid():
            self.rev_pen.setColor(new_color)
        self.paint()

    def change_dercolor(self):
        new_color = QColorDialog(self).getColor()
        if new_color.isValid():
            self.der_pen.setColor(new_color)
        self.paint()

    def change_intcolor(self):
        new_color = QColorDialog(self).getColor()
        if new_color.isValid():
            self.int_pen.setColor(new_color)
        self.paint()

    def return_to_zero(self):
        self.center = [0, 0]
        self.paint()

    def change_linecolor(self):
        new_color = QColorDialog(self).getColor()
        if new_color.isValid():
            self.line_pen.setColor(new_color)
        self.paint()

    def build_x_line(self):
        if self.x_line.text().strip() == '':
            self.do_x_line = False
        else:
            self.do_x_line = True
        self.paint()

    def build_y_line(self):
        if self.y_line.text().strip() == '':
            self.do_y_line = False
        else:
            self.do_y_line = True
        self.paint()

    def get_value(self):
        if self.argument.text().strip() == '':
            self.argument.setStyleSheet(f"background-color: {QColor(255, 75, 60).name()}")
            self.value_label.hide()
        else:
            self.value_label.setText(f'{self.value_begin}{str(round(self.get_arg(eval(self.argument.text())), 4))}')
            self.value_label.show()

    def moving(self):
        num_x, ok1 = QInputDialog.getDouble(self, "Перемещение по x", "Введите абсциссу точки перемещения:", 0)
        if ok1:
            num_y, ok2 = QInputDialog.getDouble(self, "Перемещение по y", "Введите ординату точки перемещения:", 0)
            if ok2:
                self.center = [num_x, num_y]
                self.paint()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_W:
            self.up.click()
        elif event.key() == Qt.Key.Key_S:
            self.down.click()
        elif event.key() == Qt.Key.Key_D:
            self.right.click()
        elif event.key() == Qt.Key.Key_A:
            self.left.click()

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0 and self.verticalSlider.value() != 8:
            self.verticalSlider.setValue(self.verticalSlider.value() + 1)
        elif event.angleDelta().y() < 0 and self.verticalSlider.value() != 0:
            self.verticalSlider.setValue(self.verticalSlider.value() - 1)
        event.accept()


class Function_base(QWidget):
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
        self.mode.move(50, 30)
        self.mode.resize(120, 20)

        self.menu = QMenuBar(self)

        self.mode_menu = self.menu.addMenu('Режим')
        self.choose_mode = self.mode_menu.addAction('Выбор  👈')
        self.choose_mode.triggered.connect(self.change_mode)
        self.remove_mode = self.mode_menu.addAction('Удаление  🗑️')
        self.remove_mode.triggered.connect(self.change_mode)

        self.actions_menu = self.menu.addMenu('Инструменты')
        self.clear_funcs = self.actions_menu.addAction('Очистить  🆑')
        self.clear_funcs.triggered.connect(self.clearing)
        self.back = self.actions_menu.addAction('Вернуть последнее действие  🔙')
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
        for i, row in enumerate(res):
            self.table.setRowCount(
                self.table.rowCount() + 1)
            for j, elem in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(elem)))

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Function_builder()
    ex.show()
    sys.exit(app.exec())
