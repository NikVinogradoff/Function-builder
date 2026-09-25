import sys
import sqlite3
from random import choice
from math import sin, cos, tan, pi, e, gamma, asin, acos, atan, sinh, cosh, tanh, asinh, acosh, atanh, log

from PyQt6 import uic
from PyQt6.QtCore import QPointF, Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QPolygonF
from PyQt6.QtWidgets import QApplication, QMainWindow, QColorDialog

from built_function import BuiltFunction
from instruction import Instruction
from function_base import FunctionBase


with open('style.css', 'r') as css:
    style = css.read()


class FunctionBuilder(QMainWindow):
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

        self.do_commit = False
        self.do_build = True

        self.isdotted = True
        self.isaxis = True

        self.resize_timer = QTimer(self)
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.on_resize_finished)

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Функциональный строитель')
        self.setMinimumSize(810, 728)

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

        functions = ('x', 'abs(x)', 'x ** 2', 'x ** 0.5', 'x ** 3', '1 / x', 'sin(x)', 'cos(x)', 'e ** x')
        self.function.setText(choice(functions))

        self.paint()

    def instructor(self):
        self.instruct = Instruction()
        self.instruct.show()

    def new_window(self):
        self.built = BuiltFunction(self)
        self.built.show()

    def func_db(self):
        self.db = FunctionBase(self)
        self.db.show()

    def paintEvent(self, event):
        if not self.Fxy.isChecked():
            self.do_build = True
        self.updater()
        qp = QPainter()
        qp.begin(self)
        self.build(qp, self.do_build)
        qp.end()

    def paint(self):
        self.do_build = True
        self.update()
        self.do_commit = True

    def updater(self):
        if self.function.text().strip() != '':
            if self.Fx.isChecked():
                func = 'f(x)'
                label = 'y = '
                self.new_window_btn.show()
            elif self.Fy.isChecked():
                func = 'f(y)'
                label = 'x = '
                self.new_window_btn.show()
            else:
                func = 'f(x, y)'
                label = '0 = '

            if self.do_commit:
                try:
                    self.cursor.execute("""
                            insert into functions(function, type)
                            values(?, ?)
                            """, (label + self.function.text(), func))
                    self.connection.commit()
                except sqlite3.IntegrityError:
                    self.connection.commit()
                self.do_commit = False
        else:
            self.do_build = False
            self.new_window_btn.hide()

    def is_point_valid(self, x, y, radius=1):
        text = self.function.text()
        func_x_max, func_x_min, func_y_max, func_y_min, func_x, func_y = '', '', '', '', '', ''
        delta = self.delta / 80

        for elem in text:
            if elem == 'x':
                func_x_max += f'({x + radius * delta})'
                func_x_min += f'({x - radius * delta})'
                func_x += f'({x})'
                func_y += f'({x})'
                func_y_max += f'({x})'
                func_y_min += f'({x})'
            elif elem == 'y':
                func_x_max += f'({y})'
                func_x_min += f'({y})'
                func_x += f'({y})'
                func_y += f'({y})'
                func_y_max += f'({y + radius * delta})'
                func_y_min += f'({y - radius * delta})'
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

        x_center = self.size().width() // 2 - 15
        y_center = self.size().height() // 2 + 6

        qp.setPen(QPen(QColor('grey'), 1))
        qp.drawPolygon(QPolygonF([QPointF(x_center - 200, y_center - 200),
                                  QPointF(x_center + 200, y_center - 200),
                                  QPointF(x_center + 200, y_center + 200),
                                  QPointF(x_center - 200, y_center + 200)]))

        qp.setPen(QPen(QColor('grey'), 3))
        qp.drawPolygon(QPolygonF([QPointF(x_center - 392, y_center - 372),
                                  QPointF(x_center - 392, y_center + 360),
                                  QPointF(x_center + 422, y_center + 360),
                                  QPointF(x_center + 422, y_center - 372)]))

        if self.isdotted:
            qp.setPen(self.dotted_pen)
            for i in range(1, 10):
                qp.drawLine(QPointF((x_center - 200) + i * 40, (y_center - 200)),
                            QPointF((x_center - 200) + i * 40, (y_center + 200)))
                qp.drawLine(QPointF((x_center - 200), (y_center - 200) + i * 40),
                            QPointF((x_center + 200), (y_center - 200) + 40 * i))

        qp.setPen(self.axis_pen)
        if abs(self.center[1]) <= self.delta * 5:
            qp.drawLine(QPointF((x_center - 200), y_center - (-self.center[1] / self.delta * 40)),
                        QPointF((x_center + 200), y_center - (-self.center[1] / self.delta * 40)))
        if abs(self.center[0]) <= self.delta * 5:
            qp.drawLine(QPointF(x_center + (-self.center[0] / self.delta * 40), (y_center - 200)),
                        QPointF(x_center + (-self.center[0] / self.delta * 40), (y_center + 200)))

        for i in range(1, 10):
            if abs(self.center[1]) <= self.delta * 5:
                qp.drawLine(QPointF((x_center - 200) + i * 40, y_center - 5 - (-self.center[1] / self.delta * 40)),
                            QPointF((x_center - 200) + i * 40, y_center + 5 - (-self.center[1] / self.delta * 40)))
                qp.setPen(self.text_pen)
                qp.drawText(QPointF((x_center - 200) + i * 40 + 3, y_center + 5 + self.center[1] / self.delta * 40 + 10),
                            str(round((i - 5 + self.center[0] / self.delta) * self.delta, 2)))
                qp.setPen(self.axis_pen)
            if abs(self.center[0]) <= self.delta * 5:
                qp.drawLine(QPointF(x_center - 5 + (-self.center[0] / self.delta * 40), (y_center + 200) - i * 40),
                            QPointF(x_center + 5 + (-self.center[0] / self.delta * 40), (y_center + 200) - i * 40))
                if i - 5 + self.center[1] / self.delta != 0:
                    qp.setPen(self.text_pen)
                    qp.drawText(QPointF(x_center + 5 + (-self.center[0] / self.delta * 40),
                                        (y_center + 200) + 12 - i * 40),
                                str(round((i - 5 + self.center[1] / self.delta) * self.delta, 2)))
                    qp.setPen(self.axis_pen)

        if abs(self.center[0]) <= self.delta * 5:
            qp.drawLine(QPointF(x_center - 4 + (-self.center[0] / self.delta * 40), (y_center - 200) + 6),
                        QPointF(x_center + 1 + (-self.center[0] / self.delta * 40), (y_center - 200) + 1))
            qp.drawLine(QPointF(x_center + 5 + (-self.center[0] / self.delta * 40), (y_center - 200) + 6),
                        QPointF(x_center + (-self.center[0] / self.delta * 40), (y_center - 200) + 1))
            qp.setPen(self.text_pen)
            qp.drawText(QPointF(x_center + 10 + (-self.center[0] / self.delta * 40), (y_center - 200) + 6), 'y')
            qp.setPen(self.axis_pen)
        if abs(self.center[1]) <= self.delta * 5:
            qp.drawLine(QPointF((x_center + 200) - 5, y_center - 4 - (-self.center[1] / self.delta * 40)),
                        QPointF((x_center + 200), y_center + 1 - (-self.center[1] / self.delta * 40)))
            qp.drawLine(QPointF((x_center + 200) - 5, y_center + 5 - (-self.center[1] / self.delta * 40)),
                        QPointF((x_center + 200), y_center - (-self.center[1] / self.delta * 40)))
            qp.setPen(self.text_pen)
            qp.drawText(QPointF((x_center + 200) - 10, y_center + 15 - (-self.center[1] / self.delta * 40)), 'x')
            qp.setPen(self.axis_pen)

        qp.setPen(self.text_pen)
        for i in range(1, 10):
            if abs(-self.center[1]) > self.delta * 5:
                qp.drawText(QPointF((x_center - 200) - 20 + i * 40, (y_center + 200)),
                            str(round(self.center[0] + (i - 5) * self.delta, 2)))
            if abs(-self.center[0]) > self.delta * 5:
                qp.drawText(QPointF((x_center + 200) - 20, (y_center + 200) - 3 - i * 40),
                            str(round(self.center[1] + (i - 5) * self.delta, 2)))

    def build(self, qp, do_build=True):
        self.build_base(qp)

        if not do_build:
            return None
        self.do_build = False

        x_center = self.size().width() // 2 - 15
        y_center = self.size().height() // 2 + 6

        if self.isaxis:
            self.func_pen.setWidth(2)
        else:
            self.func_pen.setWidth(1)
        qp.setPen(self.func_pen)
        points = []

        if self.Fx.isChecked():
            for i in range((x_center - 200), (x_center + 200) + 1):
                try:
                    points.append(QPointF(i, -self.get_arg((i - x_center) / 40 * self.delta + self.center[0]) *
                                          40 / self.delta + y_center + self.center[1] * 40 / self.delta))
                except Exception:
                    points.append(-1)

            for i in range(399):
                if points[i] == -1 or points[i + 1] == -1:
                    continue
                if ((y_center - 200) <= points[i].y() < (y_center + 200) + 1 and
                        (y_center - 200) <= points[i + 1].y() < (y_center + 200) + 1):
                    qp.drawLine(points[i], points[i + 1])
                elif ((y_center - 200) <= points[i].y() < (y_center + 200) + 1 and
                      points[i + 1].y() < (y_center + 200) + 1):
                    qp.drawLine(points[i], QPointF(i + (x_center - 200), (y_center - 200)))
                elif (y_center - 200) <= points[i].y() < (y_center + 200) + 1 and points[i + 1].y() >= (y_center - 200):
                    qp.drawLine(points[i], QPointF(i + (x_center - 200), (y_center + 200)))
                elif ((y_center - 200) <= points[i + 1].y() < (y_center + 200) + 1 and
                      points[i].y() < (y_center + 200) + 1):
                    qp.drawLine(QPointF(i + 1 + (x_center - 200), (y_center - 200)), points[i + 1])
                elif (y_center - 200) <= points[i + 1].y() < (y_center + 200) + 1 and points[i].y() >= (y_center - 200):
                    qp.drawLine(QPointF(i + 1 + (x_center - 200), (y_center + 200)), points[i + 1])

        elif self.Fy.isChecked():
            for i in range((y_center - 200), (y_center + 200) + 1):
                i = (y_center + 200) - i + (y_center - 200)
                try:
                    points.append(QPointF(self.get_arg((i - y_center) / 40 * self.delta + self.center[1]) *
                                          40 / self.delta + x_center - self.center[0] * 40 / self.delta,
                                          (y_center + 200) - i + (y_center - 200)))
                except Exception:
                    points.append(-1)

            for i in range(399):
                if points[i] == -1 or points[i + 1] == -1:
                    continue
                if ((x_center - 200) <= points[i].x() < (x_center + 200) + 1 and
                        (x_center - 200) <= points[i + 1].x() < (x_center + 200) + 1):
                    qp.drawLine(points[i], points[i + 1])
                elif ((x_center - 200) <= points[i].x() < (x_center + 200) + 1 and
                      points[i + 1].x() < (x_center + 200) + 1):
                    qp.drawLine(points[i], QPointF((x_center - 200), (y_center - 200) + i))
                elif (x_center - 200) <= points[i].x() < (x_center + 200) + 1 and points[i + 1].x() >= (x_center - 200):
                    qp.drawLine(points[i], QPointF((x_center + 200), (y_center - 200) + i))
                elif ((x_center - 200) <= points[i + 1].x() < (x_center + 200) + 1 and
                      points[i].x() < (x_center + 200) + 1):
                    qp.drawLine(QPointF((x_center - 200), (y_center - 200) + i + 1), points[i + 1])
                elif (x_center - 200) <= points[i + 1].x() < (x_center + 200) + 1 and points[i].x() >= (x_center - 200):
                    qp.drawLine(QPointF((x_center + 200), (y_center - 200) + i + 1), points[i + 1])

        else:
            self.func_pen.setWidth(3)
            for x in range((x_center - 200), (x_center + 200) + 1, 2):
                for y in range((y_center - 200), (y_center + 200) + 1, 2):
                    point = QPointF(x, y)
                    if self.is_point_valid((x - x_center) / 40 * self.delta + self.center[0],
                                           (y_center - y) / 40 * self.delta + self.center[1],
                                           radius=2):
                        points.append(point)
            qp.drawPoints(points)

    def change_argument(self):
        if self.Fxy.isChecked():
            arg = 'x'
            arg2 = '0'
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
                if self.Fxy.isChecked() and func_text[i] == 'y':
                    func_text[i] = 'x'
                elif func_text[i] == arg2:
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
        else:
            self.axis_btn.setText('убрать акцентирование')
            self.isaxis = True
            self.axis_pen.setWidth(3)
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
    
    def resizeEvent(self, event):
        self.resize_timer.start(200)

        x_center = self.size().width() // 2 - 15
        y_center = self.size().height() // 2 + 6

        self.Fx.move(x_center + 80, y_center - 360)
        self.Fy.move(x_center + 140, y_center - 360)
        self.Fxy.move(x_center + 200, y_center - 360)

        self.label.move(x_center - 70, y_center - 322)
        self.label_3.move(x_center + 270, y_center + 40)
        self.label_4.move(x_center - 350, y_center + 190)

        self.function.move(x_center - 30, y_center - 320)

        self.build_btn.move(x_center + 240, y_center - 280)
        self.new_window_btn.move(x_center + 250, y_center - 150)
        self.instruction_btn.move(x_center - 320, y_center - 350)
        self.open_bd_btn.move(x_center - 320, y_center - 280)

        self.change_color_btn.move(x_center - 360, y_center + 220)
        self.dotted_line_btn.move(x_center - 360, y_center + 250)
        self.axis_btn.move(x_center - 360, y_center + 280)
        self.return_to_zero_btn.move(x_center - 360, y_center + 310)

        self.lineal_func_btn.move(x_center + 250, y_center + 70)
        self.module_func_btn.move(x_center + 250, y_center + 100)
        self.quadratic_func_btn.move(x_center + 250, y_center + 130)
        self.radical_func_btn.move(x_center + 250, y_center + 160)
        self.cube_func_btn.move(x_center + 250, y_center + 190)
        self.hyperbolic_func_btn.move(x_center + 250, y_center + 220)
        self.sinus_func_btn.move(x_center + 250, y_center + 250)
        self.cosine_func_btn.move(x_center + 250, y_center + 280)
        self.exponent_func_btn.move(x_center + 250, y_center + 310)

        self.verticalSlider.move(x_center - 360, y_center - 210)

        self.too_up.move(x_center - 14, y_center - 270)
        self.up.move(x_center - 14, y_center - 230)
        self.too_left.move(x_center - 270, y_center - 15)
        self.left.move(x_center - 230, y_center - 15)
        self.too_down.move(x_center - 14, y_center + 242)
        self.down.move(x_center - 14, y_center + 210)
        self.too_right.move(x_center + 240, y_center - 15)
        self.right.move(x_center + 210, y_center - 15)

    def on_resize_finished(self):
        self.paint()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FunctionBuilder()
    ex.show()
    sys.exit(app.exec())
