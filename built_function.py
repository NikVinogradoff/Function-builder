from math import sin, cos, tan, pi, e, gamma, asin, acos, atan, sinh, cosh, tanh, asinh, acosh, atanh, log

from PyQt6 import uic
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QPolygonF
from PyQt6.QtWidgets import QWidget, QColorDialog, QInputDialog


with open('style.css', 'r') as css:
    style = css.read()


class BuiltFunction(QWidget):
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
        self.setMinimumSize(900, 900)

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
        x_center = self.width() // 2 + 50
        y_center = self.height() // 2 - 50

        qp.setPen(QPen(QColor('grey'), 3))
        qp.drawPolygon(QPolygonF([QPointF((x_center - 502), (y_center - 402)),
                                  QPointF((x_center + 402), (y_center - 402)),
                                  QPointF((x_center + 402), (y_center + 502)),
                                  QPointF((x_center - 502), (y_center + 502))]))

        qp.setPen(QPen(QColor('grey'), 1))
        qp.drawPolygon(QPolygonF([QPointF((x_center - 300), (y_center - 300)),
                                  QPointF((x_center + 300), (y_center - 300)),
                                  QPointF((x_center + 300), (y_center + 300)),
                                  QPointF((x_center - 300), (y_center + 300))]))

        if self.border_radio.isChecked():
            if self.parent.isdotted:
                qp.setPen(self.parent.dotted_pen)
                for i in range(1, 10):
                    qp.drawLine(QPointF((x_center - 300) + i * 60, (y_center - 300)),
                                QPointF((x_center - 300) + i * 60, (y_center + 300)))
                    qp.drawLine(QPointF((x_center - 300), (y_center - 300) + i * 60),
                                QPointF((x_center + 300), (y_center - 300) + 60 * i))

            qp.setPen(self.parent.axis_pen)
            if abs(self.center[1]) <= self.delta * 5:
                qp.drawLine(QPointF((x_center - 300), y_center - (-self.center[1] / self.delta * 60)),
                            QPointF((x_center + 300), y_center - (-self.center[1] / self.delta * 60)))
            if abs(self.center[0]) <= self.delta * 5:
                qp.drawLine(QPointF(x_center + (-self.center[0] / self.delta * 60), (y_center - 300)),
                            QPointF(x_center + (-self.center[0] / self.delta * 60), (y_center + 300)))

            for i in range(1, 10):
                if abs(self.center[1]) <= self.delta * 5:
                    qp.drawLine(QPointF((x_center - 300) + i * 60, y_center - 5 - (-self.center[1] / self.delta * 60)),
                                QPointF((x_center - 300) + i * 60, y_center + 5 - (-self.center[1] / self.delta * 60)))
                    qp.setPen(self.parent.text_pen)
                    qp.drawText(QPointF((x_center - 300) + i * 60 + 3, y_center + 5 + self.center[1] / self.delta * 60 + 10),
                                str(round((i - 5 + self.center[0] / self.delta) * self.delta, 2)))
                    qp.setPen(self.parent.axis_pen)
                if abs(self.center[0]) <= self.delta * 5:
                    qp.drawLine(QPointF(x_center - 5 + (-self.center[0] / self.delta * 60), (y_center + 300) - i * 60),
                                QPointF(x_center + 5 + (-self.center[0] / self.delta * 60), (y_center + 300) - i * 60))
                    if i - 5 + self.center[1] / self.delta != 0:
                        qp.setPen(self.parent.text_pen)
                        qp.drawText(QPointF(x_center + 5 + (-self.center[0] / self.delta * 60),
                                            (y_center + 300) - 8 - i * 60),
                                    str(round((i - 5 + self.center[1] / self.delta) * self.delta, 2)))
                        qp.setPen(self.parent.axis_pen)

            if abs(self.center[0]) <= self.delta * 5:
                qp.drawLine(QPointF(x_center - 4 + (-self.center[0] / self.delta * 60), (y_center - 300) + 6),
                            QPointF(x_center + 1 + (-self.center[0] / self.delta * 60), (y_center - 300) + 1))
                qp.drawLine(QPointF(x_center + 5 + (-self.center[0] / self.delta * 60), (y_center - 300) + 6),
                            QPointF(x_center + (-self.center[0] / self.delta * 60), (y_center - 300) + 1))
                qp.setPen(self.parent.text_pen)
                qp.drawText(QPointF(x_center + 10 + (-self.center[0] / self.delta * 60), (y_center - 300) + 6), 'y')
                qp.setPen(self.parent.axis_pen)
            if abs(self.center[1]) <= self.delta * 5:
                qp.drawLine(QPointF((x_center + 300) - 5, y_center - 4 - (-self.center[1] / self.delta * 60)),
                            QPointF((x_center + 300), y_center + 1 - (-self.center[1] / self.delta * 60)))
                qp.drawLine(QPointF((x_center + 300) - 5, y_center + 5 - (-self.center[1] / self.delta * 60)),
                            QPointF((x_center + 300), y_center - (-self.center[1] / self.delta * 60)))
                qp.setPen(self.parent.text_pen)
                qp.drawText(QPointF((x_center + 300) - 10, y_center + 15 - (-self.center[1] / self.delta * 60)), 'x')
                qp.setPen(self.parent.axis_pen)
            qp.setPen(self.parent.text_pen)

            for i in range(1, 10):
                if abs(-self.center[1]) > self.delta * 5:
                    qp.drawText(QPointF((x_center - 300) - 20 + i * 60, (y_center + 300)),
                                str(round(self.center[0] + (i - 5) * self.delta, 2)))
                if abs(-self.center[0]) > self.delta * 5:
                    qp.drawText(QPointF((x_center + 300) - 20, (y_center + 300) - 3 - i * 60),
                                str(round(self.center[1] + (i - 5) * self.delta, 2)))
        else:
            if self.parent.isdotted:
                qp.setPen(self.parent.dotted_pen)
                for i in range(15):
                    qp.drawLine(QPointF((x_center - 300) + 20 + i * 40, (y_center - 300)),
                                QPointF((x_center - 300) + 20 + i * 40, (y_center + 300)))
                    qp.drawLine(QPointF((x_center - 300), (y_center - 300) + 20 + i * 40),
                                QPointF((x_center + 300), (y_center - 300) + 20 + 40 * i))

            qp.setPen(self.parent.axis_pen)
            if abs(self.center[1]) <= self.delta * 7.5:
                qp.drawLine(QPointF((x_center - 300), y_center - (-self.center[1] / self.delta * 40)),
                            QPointF((x_center + 300), y_center - (-self.center[1] / self.delta * 40)))
            if abs(self.center[0]) <= self.delta * 7.5:
                qp.drawLine(QPointF(x_center + (-self.center[0] / self.delta * 40), (y_center - 300)),
                            QPointF(x_center + (-self.center[0] / self.delta * 40), (y_center + 300)))

            for i in range(15):
                if abs(self.center[1]) <= self.delta * 7.5:
                    qp.drawLine(QPointF((x_center - 300) + 20 + i * 40,
                                        y_center - 5 - (-self.center[1] / self.delta * 40)),
                                QPointF((x_center - 300) + 20 + i * 40,
                                        y_center + 5 - (-self.center[1] / self.delta * 40)))
                    qp.setPen(self.parent.text_pen)
                    qp.drawText(QPointF((x_center - 300) + i * 40 + 3,
                                        y_center + 5 + self.center[1] / self.delta * 40 + 15),
                                str(round((i - 7 + self.center[0] / self.delta) * self.delta, 2)))
                    qp.setPen(self.parent.axis_pen)
                if abs(self.center[0]) <= self.delta * 7.5:
                    qp.drawLine(QPointF(x_center - 5 + (-self.center[0] / self.delta * 40),
                                        (y_center + 300) - 20 - i * 40),
                                QPointF(x_center + 5 + (-self.center[0] / self.delta * 40),
                                        (y_center + 300) - 20 - i * 40))
                    if i - 7 + self.center[1] / self.delta != 0:
                        qp.setPen(self.parent.text_pen)
                        qp.drawText(QPointF(x_center + 10 + (-self.center[0] / self.delta * 40),
                                            (y_center + 300) - 13 - i * 40),
                                    str(round((i - 7 + self.center[1] / self.delta) * self.delta, 2)))
                        qp.setPen(self.parent.axis_pen)

            if abs(self.center[0]) <= self.delta * 7.5:
                qp.drawLine(QPointF(x_center - 4 + (-self.center[0] / self.delta * 40), (y_center - 300) + 6),
                            QPointF(x_center + 1 + (-self.center[0] / self.delta * 40), (y_center - 300) + 1))
                qp.drawLine(QPointF(x_center + 5 + (-self.center[0] / self.delta * 40), (y_center - 300) + 6),
                            QPointF(x_center + (-self.center[0] / self.delta * 40), (y_center - 300) + 1))
                qp.setPen(self.parent.text_pen)
                qp.drawText(QPointF(x_center + 10 + (-self.center[0] / self.delta * 40), (y_center - 300) + 6), 'y')
                qp.setPen(self.parent.axis_pen)
            if abs(self.center[1]) <= self.delta * 7.5:
                qp.drawLine(QPointF((x_center + 300) - 5, y_center - 4 - (-self.center[1] / self.delta * 40)),
                            QPointF((x_center + 300), y_center + 1 - (-self.center[1] / self.delta * 40)))
                qp.drawLine(QPointF((x_center + 300) - 5, y_center + 1 - (-self.center[1] / self.delta * 40)),
                            QPointF((x_center + 300), y_center - (-self.center[1] / self.delta * 40)))
                qp.setPen(self.parent.text_pen)
                qp.drawText(QPointF((x_center + 300) - 10, y_center + 15 - (-self.center[1] / self.delta * 40)), 'x')
                qp.setPen(self.parent.axis_pen)

            qp.setPen(self.parent.text_pen)
            for i in range(1, 16):
                if abs(-self.center[1]) > self.delta * 7.5:
                    qp.drawText(QPointF((x_center - 300) - 40 + i * 40, (y_center + 300)),
                                str(round(self.center[0] + (i - 8) * self.delta, 2)))
                if abs(-self.center[0]) > self.delta * 7.5:
                    qp.drawText(QPointF((x_center + 300) - 20, (y_center + 300) + 14 - i * 40),
                                str(round(self.center[1] + (i - 8) * self.delta, 2)))

    def build(self, qp):
        self.build_base(qp)
        points = []

        x_center = self.width() // 2 + 50
        y_center = self.height() // 2 - 50

        if self.border_radio.isChecked() and self.build_checkbox.isChecked():
            if self.do_x_line and self.x_line.text().strip() != '':
                try:
                    value = eval(self.x_line.text())
                except Exception:
                    pass
                if self.center[0] - self.delta * 5 <= value <= self.center[0] + self.delta * 5:
                    qp.setPen(self.line_pen)
                    qp.drawLine(QPointF((value - self.center[0]) / self.delta * 60 + x_center, (y_center - 300)),
                                QPointF((value - self.center[0]) / self.delta * 60 + x_center, (y_center + 300)))

            if self.do_y_line and self.y_line.text().strip() != '':
                try:
                    value = eval(self.y_line.text())
                except Exception:
                    pass
                if self.center[1] - self.delta * 5 <= value <= self.center[1] + self.delta * 5:
                    qp.setPen(self.line_pen)
                    qp.drawLine(QPointF((x_center - 300), -(value - self.center[1]) / self.delta * 60 + y_center),
                                QPointF((x_center + 300), -(value - self.center[1]) / self.delta * 60 + y_center))

            qp.setPen(self.parent.func_pen)
            if self.parent.Fx.isChecked():
                for i in range((x_center - 300), (x_center + 300) + 1):
                    try:
                        points.append(QPointF(i, -self.get_arg((i - x_center) / 60 * self.delta + self.center[0]) *
                                              60 / self.delta + y_center + self.center[1] * 60 / self.delta))
                    except Exception:
                        points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if ((y_center - 300) <= points[i].y() < (y_center + 300) + 1 and
                            (y_center - 300) <= points[i + 1].y() < (y_center + 300) + 1):
                        qp.drawLine(points[i], points[i + 1])
                    elif ((y_center - 300) <= points[i].y() < (y_center + 300) + 1 and
                          points[i + 1].y() < (y_center + 300) + 1):
                        qp.drawLine(points[i], QPointF(i + (x_center - 300), (y_center - 300)))
                    elif ((y_center - 300) <= points[i].y() < (y_center + 300) + 1 and
                          points[i + 1].y() >= (y_center - 300)):
                        qp.drawLine(points[i], QPointF(i + (x_center - 300), (y_center + 300)))
                    elif ((y_center - 300) <= points[i + 1].y() < (y_center + 300) + 1 and
                          points[i].y() < (y_center + 300) + 1):
                        qp.drawLine(QPointF(i + 1 + (x_center - 300), (y_center - 300)), points[i + 1])
                    elif ((y_center - 300) <= points[i + 1].y() < (y_center + 300) + 1 and
                          points[i].y() >= (y_center - 300)):
                        qp.drawLine(QPointF(i + 1 + (x_center - 300), (y_center + 300)), points[i + 1])

            elif self.parent.Fy.isChecked():
                for i in range((y_center - 300), (y_center + 300) + 1):
                    i = (y_center + 300) - i + (y_center - 300)
                    try:
                        points.append(QPointF(self.get_arg((i - y_center) / 60 * self.delta + self.center[1]) * 60 /
                                              self.delta + x_center - self.center[0] * 60 / self.delta,
                                              (y_center + 300) - i + (y_center - 300)))
                    except Exception:
                        points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if ((x_center - 300) <= points[i].x() < (x_center + 300) + 1 and
                            (x_center - 300) <= points[i + 1].x() < (x_center + 300) + 1):
                        qp.drawLine(points[i], points[i + 1])
                    elif ((x_center - 300) <= points[i].x() < (x_center + 300) + 1 and
                          points[i + 1].x() < (x_center + 300) + 1):
                        qp.drawLine(points[i], QPointF((x_center - 300), (y_center - 300) + i))
                    elif ((x_center - 300) <= points[i].x() < (x_center + 300) + 1 and
                          points[i + 1].x() >= (x_center - 300)):
                        qp.drawLine(points[i], QPointF((x_center + 300), (y_center - 300) + i))
                    elif ((x_center - 300) <= points[i + 1].x() < (x_center + 300) + 1 and
                          points[i].x() < (x_center + 300) + 1):
                        qp.drawLine(QPointF((x_center - 300), (y_center - 300) + i + 1), points[i + 1])
                    elif ((x_center - 300) <= points[i + 1].x() < (x_center + 300) + 1 and
                          points[i].x() >= (x_center - 300)):
                        qp.drawLine(QPointF((x_center + 300), (y_center - 300) + i + 1), points[i + 1])

        elif self.build_checkbox.isChecked():
            if self.do_x_line and self.x_line.text().strip() != '':
                try:
                    value = eval(self.x_line.text())
                except Exception:
                    pass
                if self.center[0] - self.delta * 7.5 <= value <= self.center[0] + self.delta * 7.5:
                    qp.setPen(self.line_pen)
                    qp.drawLine(QPointF((value - self.center[0]) / self.delta * 40 + x_center, (y_center - 300)),
                                QPointF((value - self.center[0]) / self.delta * 40 + x_center, (y_center + 300)))

            if self.do_y_line and self.y_line.text().strip() != '':
                try:
                    value = eval(self.y_line.text())
                except Exception:
                    pass
                if self.center[1] - self.delta * 7.5 <= value <= self.center[1] + self.delta * 7.5:
                    qp.setPen(self.line_pen)
                    qp.drawLine(QPointF((x_center - 300), -(value - self.center[1]) / self.delta * 40 + y_center),
                                QPointF((x_center + 300), -(value - self.center[1]) / self.delta * 40 + y_center))

            qp.setPen(self.parent.func_pen)
            if self.parent.Fx.isChecked():
                for i in range((x_center - 300), (x_center + 300) + 1):
                    try:
                        points.append(QPointF(i, -self.get_arg((i - x_center) / 40 * self.delta + self.center[0]) *
                                              40 / self.delta + y_center + self.center[1] * 40 / self.delta))
                    except Exception:
                        points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if ((y_center - 300) <= points[i].y() < (y_center + 300) + 1 and
                            (y_center - 300) <= points[i + 1].y() < (y_center + 300) + 1):
                        qp.drawLine(points[i], points[i + 1])
                    elif ((y_center - 300) <= points[i].y() < (y_center + 300) + 1 and
                          points[i + 1].y() < (y_center + 300) + 1):
                        qp.drawLine(points[i], QPointF(i + (x_center - 300), (y_center - 300)))
                    elif ((y_center - 300) <= points[i].y() < (y_center + 300) + 1 and
                          points[i + 1].y() >= (y_center - 300)):
                        qp.drawLine(points[i], QPointF(i + (x_center - 300), (y_center + 300)))
                    elif ((y_center - 300) <= points[i + 1].y() < (y_center + 300) + 1 and
                          points[i].y() < (y_center + 300) + 1):
                        qp.drawLine(QPointF(i + 1 + (x_center - 300), (y_center - 300)), points[i + 1])
                    elif ((y_center - 300) <= points[i + 1].y() < (y_center + 300) + 1 and
                          points[i].y() >= (y_center - 300)):
                        qp.drawLine(QPointF(i + 1 + (x_center - 300), (y_center + 300)), points[i + 1])

            elif self.parent.Fy.isChecked():
                for i in range((y_center - 300), (y_center + 300) + 1):
                    i = (y_center + 300) - i + (y_center - 300)
                    try:
                        points.append(QPointF(self.get_arg((i - y_center) / 40 * self.delta + self.center[1]) * 40 /
                                              self.delta + x_center - self.center[0] * 40 / self.delta,
                                              (y_center + 300) - i + (y_center - 300)))
                    except Exception:
                        points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if ((x_center - 300) <= points[i].x() < (x_center + 300) + 1 and
                            (x_center - 300) <= points[i + 1].x() < (x_center + 300) + 1):
                        qp.drawLine(points[i], points[i + 1])
                    elif ((x_center - 300) <= points[i].x() < (x_center + 300) + 1 and
                          points[i + 1].x() < (x_center + 300) + 1):
                        qp.drawLine(points[i], QPointF((x_center - 300), (y_center - 300) + i))
                    elif ((x_center - 300) <= points[i].x() < (x_center + 300) + 1 and
                          points[i + 1].x() >= (x_center - 300)):
                        qp.drawLine(points[i], QPointF((x_center + 300), (y_center - 300) + i))
                    elif ((x_center - 300) <= points[i + 1].x() < (x_center + 300) + 1 and
                          points[i].x() < (x_center + 300) + 1):
                        qp.drawLine(QPointF((x_center - 300), (y_center - 300) + i + 1), points[i + 1])
                    elif ((x_center - 300) <= points[i + 1].x() < (x_center + 300) + 1 and
                          points[i].x() >= (x_center - 300)):
                        qp.drawLine(QPointF((x_center + 300), (y_center - 300) + i + 1), points[i + 1])

        if self.build_derivative_checkbox.isChecked():
            self.build_derivative(qp)

        if self.build_integral_checkbox.isChecked():
            self.build_integral(qp)

        if self.build_reversed_checkbox.isChecked():
            self.build_reversed(qp)

    def build_reversed(self, qp):
        qp.setPen(self.rev_pen)
        points = []

        x_center = self.width() // 2 + 50
        y_center = self.height() // 2 - 50

        if self.border_radio.isChecked():
            if self.parent.Fy.isChecked():
                for i in range((x_center - 300), (x_center + 300)  + 1):
                    try:
                        points.append(QPointF(i, -self.get_arg((i - x_center) / 60 * self.delta + self.center[0]) *
                                              60 / self.delta + y_center + self.center[1] * 60 / self.delta))
                    except Exception:
                        points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if ((y_center - 300) <= points[i].y() < (y_center + 300) + 1 and
                            (y_center - 300) <= points[i + 1].y() < (y_center + 300) + 1):
                        qp.drawLine(points[i], points[i + 1])
                    elif ((y_center - 300) <= points[i].y() < (y_center + 300) + 1 and
                          points[i + 1].y() < (y_center + 300) + 1):
                        qp.drawLine(points[i], QPointF(i + (x_center - 300), (y_center - 300)))
                    elif ((y_center - 300) <= points[i].y() < (y_center + 300) + 1 and
                          points[i + 1].y() >= (y_center - 300)):
                        qp.drawLine(points[i], QPointF(i + (x_center - 300), (y_center + 300)))
                    elif ((y_center - 300) <= points[i + 1].y() < (y_center + 300) + 1 and
                          points[i].y() < (y_center + 300) + 1):
                        qp.drawLine(QPointF(i + 1 + (x_center - 300), (y_center - 300)), points[i + 1])
                    elif ((y_center - 300) <= points[i + 1].y() < (y_center + 300) + 1 and
                          points[i].y() >= (y_center - 300)):
                        qp.drawLine(QPointF(i + 1 + (x_center - 300), (y_center + 300)), points[i + 1])

            elif self.parent.Fx.isChecked():
                for i in range((y_center - 300), (y_center + 300) + 1):
                    i = (y_center + 300) - i + (y_center - 300)
                    try:
                        points.append(QPointF(self.get_arg((i - y_center) / 60 * self.delta + self.center[1]) * 60 /
                                              self.delta + x_center - self.center[0] * 60 / self.delta,
                                              (y_center + 300) - i + (y_center - 300)))
                    except Exception:
                        points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if ((x_center - 300) <= points[i].x() < (x_center + 300) + 1 and
                            (x_center - 300) <= points[i + 1].x() < (x_center + 300) + 1):
                        qp.drawLine(points[i], points[i + 1])
                    elif ((x_center - 300) <= points[i].x() < (x_center + 300) + 1 and
                          points[i + 1].x() < (x_center + 300) + 1):
                        qp.drawLine(points[i], QPointF((x_center - 300), (y_center - 300) + i))
                    elif ((x_center - 300) <= points[i].x() < (x_center + 300) + 1 and
                          points[i + 1].x() >= (x_center - 300)):
                        qp.drawLine(points[i], QPointF((x_center + 300), (y_center - 300) + i))
                    elif ((x_center - 300) <= points[i + 1].x() < (x_center + 300) + 1 and
                          points[i].x() < (x_center + 300) + 1):
                        qp.drawLine(QPointF((x_center - 300), (y_center - 300) + i + 1), points[i + 1])
                    elif ((x_center - 300) <= points[i + 1].x() < (x_center + 300) + 1 and
                          points[i].x() >= (x_center - 300)):
                        qp.drawLine(QPointF((x_center + 300), (y_center - 300) + i + 1), points[i + 1])

        else:
            if self.parent.Fy.isChecked():
                for i in range((x_center - 300), (x_center + 300) + 1):
                    try:
                        points.append(QPointF(i, -self.get_arg((i - x_center) / 40 * self.delta + self.center[0]) *
                                              40 / self.delta + y_center + self.center[1] * 40 / self.delta))
                    except Exception:
                        points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if ((y_center - 300) <= points[i].y() < (y_center + 300) + 1 and
                            (y_center - 300) <= points[i + 1].y() < (y_center + 300) + 1):
                        qp.drawLine(points[i], points[i + 1])
                    elif ((y_center - 300) <= points[i].y() < (y_center + 300) + 1 and
                          points[i + 1].y() < (y_center + 300) + 1):
                        qp.drawLine(points[i], QPointF(i + (x_center - 300), (y_center - 300)))
                    elif ((y_center - 300) <= points[i].y() < (y_center + 300) + 1 and
                          points[i + 1].y() >= (y_center - 300)):
                        qp.drawLine(points[i], QPointF(i + (x_center - 300), (y_center + 300)))
                    elif ((y_center - 300) <= points[i + 1].y() < (y_center + 300) + 1 and
                          points[i].y() < (y_center + 300) + 1):
                        qp.drawLine(QPointF(i + 1 + (x_center - 300), (y_center - 300)), points[i + 1])
                    elif ((y_center - 300) <= points[i + 1].y() < (y_center + 300) + 1 and
                          points[i].y() >= (y_center - 300)):
                        qp.drawLine(QPointF(i + 1 + (x_center - 300), (y_center + 300)), points[i + 1])

            elif self.parent.Fx.isChecked():
                for i in range((y_center - 300), (y_center + 300) + 1):
                    i = (y_center + 300) - i + (y_center - 300)
                    try:
                        points.append(QPointF(self.get_arg((i - y_center) / 40 * self.delta + self.center[1]) * 40 /
                                              self.delta + x_center - self.center[0] * 40 / self.delta,
                                              (y_center + 300) - i + (y_center - 300)))
                    except Exception:
                        points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if ((x_center - 300) <= points[i].x() < (x_center + 300) + 1 and
                            (x_center - 300) <= points[i + 1].x() < (x_center + 300) + 1):
                        qp.drawLine(points[i], points[i + 1])
                    elif ((x_center - 300) <= points[i].x() < (x_center + 300) + 1 and
                          points[i + 1].x() < (x_center + 300) + 1):
                        qp.drawLine(points[i], QPointF((x_center - 300), (y_center - 300) + i))
                    elif ((x_center - 300) <= points[i].x() < (x_center + 300) + 1 and
                          points[i + 1].x() >= (x_center - 300)):
                        qp.drawLine(points[i], QPointF((x_center + 300), (y_center - 300) + i))
                    elif ((x_center - 300) <= points[i + 1].x() < (x_center + 300) + 1 and
                          points[i].x() < (x_center + 300) + 1):
                        qp.drawLine(QPointF((x_center - 300), (y_center - 300) + i + 1), points[i + 1])
                    elif ((x_center - 300) <= points[i + 1].x() < (x_center + 300) + 1 and
                          points[i].x() >= (x_center - 300)):
                        qp.drawLine(QPointF((x_center + 300), (y_center - 300) + i + 1), points[i + 1])

    def build_derivative(self, qp):
        x_center = self.width() // 2 + 50
        y_center = self.height() // 2 - 50

        qp.setPen(self.der_pen)
        points = []

        if self.border_radio.isChecked():
            if self.parent.Fx.isChecked():
                for i in range((x_center - 300), (x_center + 300) + 1):
                    try:
                        points.append(QPointF(i,
                                              -self.get_derivative((i - x_center) / 60 * self.delta + self.center[0]) *
                                              60 / self.delta + y_center + self.center[1] * 60 / self.delta))
                    except Exception:
                        points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if ((y_center - 300) <= points[i].y() < (y_center + 300) + 1 and
                            (y_center - 300) <= points[i + 1].y() < (y_center + 300) + 1):
                        qp.drawLine(points[i], points[i + 1])
                    elif ((y_center - 300) <= points[i].y() < (y_center + 300) + 1 and
                          points[i + 1].y() < (y_center + 300) + 1):
                        qp.drawLine(points[i], QPointF(i + (x_center - 300), (y_center - 300)))
                    elif ((y_center - 300) <= points[i].y() < (y_center + 300) + 1 and
                          points[i + 1].y() >= (y_center - 300)):
                        qp.drawLine(points[i], QPointF(i + (x_center - 300), (y_center + 300) + 1))
                    elif ((y_center - 300) <= points[i + 1].y() < (y_center + 300) + 1 and
                          points[i].y() < (y_center + 300) + 1):
                        qp.drawLine(QPointF(i + 1 + (x_center - 300), (y_center - 300)), points[i + 1])
                    elif ((y_center - 300) <= points[i + 1].y() < (y_center + 300) + 1 and
                          points[i].y() >= (y_center - 300)):
                        qp.drawLine(QPointF(i + 1 + (x_center - 300), (y_center + 300)), points[i + 1])

            elif self.parent.Fy.isChecked():
                for i in range((y_center - 300), (y_center + 300) + 1):
                    i = (y_center + 300) - i + (y_center - 300)
                    try:
                        points.append(QPointF(self.get_derivative((i - y_center) / 60 * self.delta + self.center[1]) *
                                              60 / self.delta + x_center - self.center[0] * 60 / self.delta,
                                              (y_center + 300) - i + (y_center - 300)))
                    except Exception:
                        points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if ((x_center - 300) <= points[i].x() < (x_center + 300) + 1 and
                            (x_center - 300) <= points[i + 1].x() < (x_center + 300) + 1):
                        qp.drawLine(points[i], points[i + 1])
                    elif ((x_center - 300) <= points[i].x() < (x_center + 300) + 1 and
                          points[i + 1].x() < (x_center + 300) + 1):
                        qp.drawLine(points[i], QPointF((x_center - 300), (y_center - 300) + i))
                    elif ((x_center - 300) <= points[i].x() < (x_center + 300) + 1 and
                          points[i + 1].x() >= (x_center - 300)):
                        qp.drawLine(points[i], QPointF((x_center + 300), (y_center - 300) + i))
                    elif ((x_center - 300) <= points[i + 1].x() < (x_center + 300) + 1 and
                          points[i].x() < (x_center + 300) + 1):
                        qp.drawLine(QPointF((x_center - 300), (y_center - 300) + i + 1), points[i + 1])
                    elif ((x_center - 300) <= points[i + 1].x() < (x_center + 300) + 1 and
                          points[i].x() >= (x_center - 300)):
                        qp.drawLine(QPointF((x_center + 300), (y_center - 300) + i + 1), points[i + 1])

        else:
            if self.parent.Fx.isChecked():
                for i in range((x_center - 300), (x_center + 300) + 1):
                    try:
                        points.append(QPointF(i,
                                              -self.get_derivative((i - x_center) / 40 * self.delta + self.center[0]) *
                                              40 / self.delta + y_center + self.center[1] * 40 / self.delta))
                    except Exception:
                        points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if ((y_center - 300) <= points[i].y() < (y_center + 300) + 1 and
                            (y_center - 300) <= points[i + 1].y() < (y_center + 300) + 1):
                        qp.drawLine(points[i], points[i + 1])
                    elif ((y_center - 300) <= points[i].y() < (y_center + 300) + 1 and
                          points[i + 1].y() < (y_center + 300) + 1):
                        qp.drawLine(points[i], QPointF(i + (x_center - 300), (y_center - 300)))
                    elif ((y_center - 300) <= points[i].y() < (y_center + 300) + 1 and
                          points[i + 1].y() >= (y_center - 300)):
                        qp.drawLine(points[i], QPointF(i + (x_center - 300), (y_center + 300)))
                    elif ((y_center - 300) <= points[i + 1].y() < (y_center + 300) + 1 and
                          points[i].y() < (y_center + 300) + 1):
                        qp.drawLine(QPointF(i + 1 + (x_center - 300), (y_center - 300)), points[i + 1])
                    elif ((y_center - 300) <= points[i + 1].y() < (y_center + 300) + 1 and
                          points[i].y() >= (y_center - 300)):
                        qp.drawLine(QPointF(i + 1 + (x_center - 300), (y_center + 300)), points[i + 1])

            elif self.parent.Fy.isChecked():
                for i in range((y_center - 300), (y_center + 300) + 1):
                    i = (y_center + 300) - i + (y_center - 300)
                    try:
                        points.append(QPointF(self.get_derivative((i - y_center) / 40 * self.delta + self.center[1]) *
                                              40 / self.delta + x_center - self.center[0] * 40 / self.delta,
                                              (y_center + 300) - i + (y_center - 300)))
                    except Exception:
                        points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if ((x_center - 300) <= points[i].x() < (x_center + 300) + 1 and
                            (x_center - 300) <= points[i + 1].x() < (x_center + 300) + 1):
                        qp.drawLine(points[i], points[i + 1])
                    elif ((x_center - 300) <= points[i].x() < (x_center + 300) + 1 and
                          points[i + 1].x() < (x_center + 300) + 1):
                        qp.drawLine(points[i], QPointF((x_center - 300), (y_center - 300) + i))
                    elif ((x_center - 300) <= points[i].x() < (x_center + 300) + 1 and
                          points[i + 1].x() >= (x_center - 300)):
                        qp.drawLine(points[i], QPointF((x_center + 300), (y_center - 300) + i))
                    elif ((x_center - 300) <= points[i + 1].x() < (x_center + 300) + 1 and
                          points[i].x() < (x_center + 300) + 1):
                        qp.drawLine(QPointF((x_center - 300), (y_center - 300) + i + 1), points[i + 1])
                    elif ((x_center - 300) <= points[i + 1].x() < (x_center + 300) + 1 and
                          points[i].x() >= (x_center - 300)):
                        qp.drawLine(QPointF((x_center + 300), (y_center - 300) + i + 1), points[i + 1])

    def build_integral(self, qp):
        x_center = self.width() // 2 + 50
        y_center = self.height() // 2 - 50

        qp.setPen(self.int_pen)
        points = []

        if self.border_radio.isChecked():
            if self.parent.Fx.isChecked():
                if -5 * self.delta <= self.center[0] <= 5 * self.delta:
                    pre_int = 0
                    for i in range((x_center - 300), int(x_center - self.center[0] / self.delta * 60)):
                        i = (x_center - 300) + int(x_center - self.center[0] / self.delta * 60) - i - 1
                        try:
                            points.append(QPointF(i, -self.get_integral((i - x_center) / 60 * self.delta + self.center[0],
                                                                        pre_int)
                                                  * 60 / self.delta + y_center + self.center[1] * 60 / self.delta))
                            pre_int = self.get_integral((i - x_center) / 60 * self.delta + self.center[0], pre_int)
                        except Exception:
                            points.append(-1)
                    points.reverse()
                    points.append(QPointF(x_center - self.center[0] * 60 / self.delta,
                                          y_center + self.center[1] * 60 / self.delta))
                    pre_int = 0
                    for i in range(int(x_center + 1 - self.center[0] / self.delta * 60), (x_center + 300) + 1):
                        try:
                            points.append(QPointF(i, -self.get_integral((i - x_center) / 60 * self.delta + self.center[0],
                                                                        pre_int)
                                                  * 60 / self.delta + y_center + self.center[1] * 60 / self.delta))
                            pre_int = self.get_integral((i - x_center) / 60 * self.delta + self.center[0], pre_int)
                        except Exception:
                            points.append(-1)

                elif self.center[0] > 5 * self.delta:
                    pre_int = 0
                    for i in range(1, int(-(-self.center[0] + 5 * self.delta) * 60 // self.delta)):
                        pre_int = self.get_integral(i / 60 * self.delta, pre_int)

                    for i in range((x_center - 300), (x_center + 300) + 1):
                        try:
                            points.append(QPointF(i, -self.get_integral((i - x_center) / 60 * self.delta + self.center[0],
                                                                        pre_int)
                                                  * 60 / self.delta + y_center + self.center[1] * 60 / self.delta))
                            pre_int = self.get_integral((i - x_center) / 60 * self.delta + self.center[0], pre_int)
                        except Exception:
                            points.append(-1)

                else:
                    pre_int = 0
                    for i in range(-1, int((-self.center[0] - 5 * self.delta) * 60 // self.delta)):
                        pre_int = self.get_integral(i / 60 * self.delta, pre_int)

                    for i in range((x_center - 300), (x_center + 300) + 1):
                        i = 2 * x_center - i
                        try:
                            points.append(QPointF(i, -self.get_integral((i - x_center) / 60 * self.delta + self.center[0],
                                                                        pre_int)
                                                  * 60 / self.delta + y_center + self.center[1] * 60 / self.delta))
                            pre_int = self.get_integral((i - x_center) / 60 * self.delta + self.center[0], pre_int)
                        except Exception:
                            points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if ((y_center - 300) <= points[i].y() < (y_center + 300) + 1 and
                            (y_center - 300) <= points[i + 1].y() < (y_center + 300) + 1):
                        qp.drawLine(points[i], points[i + 1])
                    elif ((y_center - 300) <= points[i].y() < (y_center + 300) + 1 and
                          points[i + 1].y() < (y_center + 300) + 1):
                        qp.drawLine(points[i], QPointF(i + (x_center - 300), (y_center - 300)))
                    elif ((y_center - 300) <= points[i].y() < (y_center + 300) + 1 and
                          points[i + 1].y() >= (y_center - 300)):
                        qp.drawLine(points[i], QPointF(i + (x_center - 300), (y_center + 300)))
                    elif ((y_center - 300) <= points[i + 1].y() < (y_center + 300) + 1 and
                          points[i].y() < (y_center + 300) + 1):
                        qp.drawLine(QPointF(i + 1 + (x_center - 300), (y_center - 300)), points[i + 1])
                    elif ((y_center - 300) <= points[i + 1].y() < (y_center + 300) + 1 and
                          points[i].y() >= (y_center - 300)):
                        qp.drawLine(QPointF(i + 1 + (x_center - 300), (y_center + 300)), points[i + 1])

            elif self.parent.Fy.isChecked():
                if -5 * self.delta <= self.center[1] <= 5 * self.delta:
                    pre_int = 0
                    for i in range((y_center - 300), int(y_center + self.center[1] / self.delta * 60)):
                        i = int(y_center + self.center[1] / self.delta * 60) - i - 1 + (y_center - 300)
                        try:
                            points.append(QPointF(self.get_integral((y_center - i) / 60 * self.delta + self.center[1],
                                                                    pre_int) * 60 /
                                                  self.delta + x_center - self.center[0] * 60 / self.delta, i))
                            pre_int = self.get_integral((y_center - i) / 60 * self.delta + self.center[1], pre_int)
                        except Exception:
                            points.append(-1)
                    points.reverse()
                    points.append(QPointF(x_center - self.center[0] * 60 / self.delta,
                                          y_center + self.center[1] * 60 / self.delta))
                    pre_int = 0
                    for i in range(int(y_center + 1 + self.center[1] / self.delta * 60), (y_center + 300) + 1):
                        try:
                            points.append(QPointF(self.get_integral((y_center - i) / 60 * self.delta + self.center[1],
                                                                    pre_int) * 60 /
                                                  self.delta + x_center - self.center[0] * 60 / self.delta, i))
                            pre_int = self.get_integral((y_center - i) / 60 * self.delta + self.center[1], pre_int)
                        except Exception:
                            points.append(-1)

                elif self.center[1] > 5 * self.delta:
                    pre_int = 0
                    for i in range(1, int(-(-self.center[1] + 5 * self.delta) * 60 // self.delta)):
                        pre_int = self.get_integral(i / 60 * self.delta, pre_int)

                    for i in range((y_center - 300), (y_center + 300) + 1):
                        i = 2 * y_center - i
                        try:
                            points.append(QPointF(self.get_integral((y_center - i) / 60 * self.delta + self.center[1],
                                                                    pre_int)
                                                  * 60 / self.delta + x_center - self.center[0] * 60 / self.delta, i))
                            pre_int = self.get_integral((y_center - i) / 60 * self.delta + self.center[1], pre_int)
                        except Exception:
                            points.append(-1)

                else:
                    pre_int = 0
                    for i in range(-1, int((-self.center[1] - 5 * self.delta) * 60 // self.delta)):
                        pre_int = self.get_integral(i / 60 * self.delta, pre_int)

                    for i in range((y_center - 300), (y_center + 300) + 1):
                        try:
                            points.append(QPointF(self.get_integral((y_center - i) / 60 * self.delta + self.center[1],
                                                                    pre_int)
                                                  * 60 / self.delta + x_center - self.center[0] * 60 / self.delta, i))
                            pre_int = self.get_integral((y_center - i) / 60 * self.delta + self.center[1], pre_int)
                        except Exception:
                            points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if ((x_center - 300) <= points[i].x() < (x_center + 300) + 1 and
                            (x_center - 300) <= points[i + 1].x() < (x_center + 300) + 1):
                        qp.drawLine(points[i], points[i + 1])
                    elif ((x_center - 300) <= points[i].x() < (x_center + 300) + 1 and
                          points[i + 1].x() < (x_center + 300) + 1):
                        qp.drawLine(points[i], QPointF((x_center - 300), (y_center - 300) + i))
                    elif ((x_center - 300) <= points[i].x() < (x_center + 300) + 1 and
                          points[i + 1].x() >= (x_center - 300)):
                        qp.drawLine(points[i], QPointF((x_center + 300), (y_center - 300) + i))
                    elif ((x_center - 300) <= points[i + 1].x() < (x_center + 300) + 1 and
                          points[i].x() < (x_center + 300) + 1):
                        qp.drawLine(QPointF((x_center - 300), (y_center - 300) + i + 1), points[i + 1])
                    elif ((x_center - 300) <= points[i + 1].x() < (x_center + 300) + 1 and
                          points[i].x() >= (x_center - 300)):
                        qp.drawLine(QPointF((x_center + 300), (y_center - 300) + i + 1), points[i + 1])

        else:
            if self.parent.Fx.isChecked():
                if -7.5 * self.delta <= self.center[0] <= 7.5 * self.delta:
                    pre_int = 0
                    for i in range((x_center - 300), int(x_center - self.center[0] / self.delta * 40)):
                        i = (x_center - 300) + int(x_center - self.center[0] / self.delta * 40) - i - 1
                        try:
                            points.append(QPointF(i, -self.get_integral((i - x_center) / 40 * self.delta + self.center[0],
                                                                        pre_int)
                                                  * 40 / self.delta + y_center + self.center[1] * 40 / self.delta))
                            pre_int = self.get_integral((i - x_center) / 40 * self.delta + self.center[0], pre_int)
                        except Exception:
                            points.append(-1)
                    points.reverse()
                    points.append(QPointF(x_center - self.center[0] * 40 / self.delta,
                                          y_center + self.center[1] * 40 / self.delta))
                    pre_int = 0
                    for i in range(int(x_center + 1 - self.center[0] / self.delta * 40), (x_center + 300) + 1):
                        try:
                            points.append(QPointF(i, -self.get_integral((i - x_center) / 40 * self.delta + self.center[0],
                                                                        pre_int)
                                                  * 40 / self.delta + y_center + self.center[1] * 40 / self.delta))
                            pre_int = self.get_integral((i - x_center) / 40 * self.delta + self.center[0], pre_int)
                        except Exception:
                            points.append(-1)

                elif self.center[0] > 7.5 * self.delta:
                    pre_int = 0
                    for i in range(1, int(-(-self.center[0] + 7.5 * self.delta) * 40 // self.delta)):
                        pre_int = self.get_integral(i / 40 * self.delta, pre_int)

                    for i in range((x_center - 300), (x_center + 300) + 1):
                        try:
                            points.append(QPointF(i, -self.get_integral((i - x_center) / 40 * self.delta + self.center[0],
                                                                        pre_int)
                                                  * 40 / self.delta + y_center + self.center[1] * 40 / self.delta))
                            pre_int = self.get_integral((i - x_center) / 40 * self.delta + self.center[0], pre_int)
                        except Exception:
                            points.append(-1)

                else:
                    pre_int = 0
                    for i in range(-1, int((-self.center[0] - 7.5 * self.delta) * 40 // self.delta)):
                        pre_int = self.get_integral(i / 40 * self.delta, pre_int)

                    for i in range((x_center - 300), (x_center + 300) + 1):
                        i = 2 * x_center - i
                        try:
                            points.append(QPointF(i, -self.get_integral((i - x_center) / 40 * self.delta + self.center[0],
                                                                        pre_int)
                                                  * 40 / self.delta + y_center + self.center[1] * 40 / self.delta))
                            pre_int = self.get_integral((i - x_center) / 40 * self.delta + self.center[0], pre_int)
                        except Exception:
                            points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if ((y_center - 300) <= points[i].y() < (y_center + 300) + 1 and
                            (y_center - 300) <= points[i + 1].y() < (y_center + 300) + 1):
                        qp.drawLine(points[i], points[i + 1])
                    elif ((y_center - 300) <= points[i].y() < (y_center + 300) + 1 and
                          points[i + 1].y() < (y_center + 300) + 1):
                        qp.drawLine(points[i], QPointF(i + (x_center - 300), (y_center - 300)))
                    elif ((y_center - 300) <= points[i].y() < (y_center + 300) + 1 and
                          points[i + 1].y() >= (y_center - 300)):
                        qp.drawLine(points[i], QPointF(i + (x_center - 300), (y_center + 300)))
                    elif ((y_center - 300) <= points[i + 1].y() < (y_center + 300) + 1 and
                          points[i].y() < (y_center + 300) + 1):
                        qp.drawLine(QPointF(i + 1 + (x_center - 300), (y_center - 300)), points[i + 1])
                    elif ((y_center - 300) <= points[i + 1].y() < (y_center + 300) + 1 and
                          points[i].y() >= (y_center - 300)):
                        qp.drawLine(QPointF(i + 1 + (x_center - 300), (y_center + 300)), points[i + 1])

            elif self.parent.Fy.isChecked():
                if -7.5 * self.delta <= self.center[1] <= 7.5 * self.delta:
                    pre_int = 0
                    for i in range((y_center - 300), int(y_center + self.center[1] / self.delta * 40)):
                        i = int(y_center + self.center[1] / self.delta * 40) - i - 1 + (y_center - 300)
                        try:
                            points.append(QPointF(self.get_integral((y_center - i) / 40 * self.delta + self.center[1],
                                                                    pre_int) * 40 /
                                                  self.delta + x_center - self.center[0] * 40 / self.delta, i))
                            pre_int = self.get_integral((y_center - i) / 40 * self.delta + self.center[1], pre_int)
                        except Exception:
                            points.append(-1)
                    points.reverse()
                    points.append(QPointF(x_center - self.center[0] * 40 / self.delta,
                                          y_center + self.center[1] * 40 / self.delta))
                    pre_int = 0
                    for i in range(int(y_center + 1 + self.center[1] / self.delta * 40), (y_center + 300) + 1):
                        try:
                            points.append(QPointF(self.get_integral((y_center - i) / 40 * self.delta + self.center[1],
                                                                    pre_int) * 40 /
                                                  self.delta + x_center - self.center[0] * 40 / self.delta, i))
                            pre_int = self.get_integral((y_center - i) / 40 * self.delta + self.center[1], pre_int)
                        except Exception:
                            points.append(-1)

                elif self.center[1] > 7.5 * self.delta:
                    pre_int = 0
                    for i in range(1, int(-(-self.center[1] + 7.5 * self.delta) * 40 // self.delta)):
                        pre_int = self.get_integral(i / 40 * self.delta, pre_int)

                    for i in range((y_center - 300), (y_center + 300) + 1):
                        i = 2 * y_center - i
                        try:
                            points.append(QPointF(self.get_integral((y_center - i) / 40 * self.delta + self.center[1],
                                                                    pre_int)
                                                  * 40 / self.delta + x_center - self.center[0] * 40 / self.delta, i))
                            pre_int = self.get_integral((y_center - i) / 40 * self.delta + self.center[1], pre_int)
                        except Exception:
                            points.append(-1)

                else:
                    pre_int = 0
                    for i in range(-1, int((-self.center[1] - 7.5 * self.delta) * 40 // self.delta)):
                        pre_int = self.get_integral(i / 40 * self.delta, pre_int)

                    for i in range((y_center - 300), (y_center + 300) + 1):
                        try:
                            points.append(QPointF(self.get_integral((y_center - i) / 40 * self.delta + self.center[1],
                                                                    pre_int)
                                                  * 40 / self.delta + x_center - self.center[0] * 40 / self.delta, i))
                            pre_int = self.get_integral((y_center - i) / 40 * self.delta + self.center[1], pre_int)
                        except Exception:
                            points.append(-1)

                for i in range(599):
                    if points[i] == -1 or points[i + 1] == -1:
                        continue
                    if ((x_center - 300) <= points[i].x() < (x_center + 300) + 1 and
                            (x_center - 300) <= points[i + 1].x() < (x_center + 300) + 1):
                        qp.drawLine(points[i], points[i + 1])
                    elif ((x_center - 300) <= points[i].x() < (x_center + 300) + 1 and
                          points[i + 1].x() < (x_center + 300) + 1):
                        qp.drawLine(points[i], QPointF((x_center - 300), (y_center - 300) + i))
                    elif ((x_center - 300) <= points[i].x() < (x_center + 300) + 1 and
                          points[i + 1].x() >= (x_center - 300)):
                        qp.drawLine(points[i], QPointF((x_center + 300), (y_center - 300) + i))
                    elif ((x_center - 300) <= points[i + 1].x() < (x_center + 300) + 1 and
                          points[i].x() < (x_center + 300) + 1):
                        qp.drawLine(QPointF((x_center - 300), (y_center - 300) + i + 1), points[i + 1])
                    elif ((x_center - 300) <= points[i + 1].x() < (x_center + 300) + 1 and
                          points[i].x() >= (x_center - 300)):
                        qp.drawLine(QPointF((x_center + 300), (y_center - 300) + i + 1), points[i + 1])

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

    def resizeEvent(self, event):
        x_center = self.size().width() // 2
        y_center = self.size().height() // 2

        self.left.move(x_center - 290, y_center - 65)
        self.too_left.move(x_center - 330, y_center - 65)
        self.up.move(x_center + 36, y_center - 390)
        self.too_up.move(x_center + 36, y_center - 430)
        self.right.move(x_center + 368, y_center - 65)
        self.too_right.move(x_center + 398, y_center - 65)
        self.down.move(x_center + 36, y_center + 268)
        self.too_down.move(x_center + 36, y_center + 298)

        self.verticalSlider.move(x_center - 430, y_center - 290)

        self.build_reversed_checkbox.move(x_center - 420, y_center + 260)
        self.change_revcolor_btn.move(x_center - 210, y_center + 260)

        self.x_line.move(x_center - 350, y_center + 380)
        self.label.move(x_center - 390, y_center + 380)
        self.build_x_btn.move(x_center - 250, y_center + 380)

        self.y_line.move(x_center - 350, y_center + 410)
        self.label_2.move(x_center - 390, y_center + 410)
        self.build_y_btn.move(x_center - 250, y_center + 410)

        self.label_3.move(x_center - 440, y_center + 350)
        self.label_4.move(x_center - 420, y_center - 420)
        self.label_5.move(x_center - 150, y_center + 420)

        self.change_linecolor_btn.move(x_center - 300, y_center + 350)

        self.label_6.move(x_center + 180, y_center + 300)
        self.argument.move(x_center + 250, y_center + 340)
        self.arg_label.move(x_center + 190, y_center + 340)
        self.value_label.move(x_center + 210, y_center + 380)
        self.find_btn.move(x_center + 350, y_center + 340)

        self.border_radio.move(x_center - 420, y_center - 380)
        self.size_radio.move(x_center - 420, y_center - 350)

        self.return_to_zero_btn.move(x_center + 240, y_center - 400)
        self.moving_btn.move(x_center + 240, y_center - 438)

        self.change_dercolor_btn.move(x_center - 210, y_center + 290)
        self.build_derivative_checkbox.move(x_center - 420, y_center + 290)

        self.build_integral_checkbox.move(x_center - 420, y_center + 320)
        self.change_intcolor_btn.move(x_center - 190, y_center + 320)

        self.build_checkbox.move(x_center - 420, y_center + 230)
