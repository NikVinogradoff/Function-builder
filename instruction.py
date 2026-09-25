from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QPolygonF
from PyQt6.QtWidgets import QWidget, QLabel, QRadioButton


class Instruction(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Инструкция')
        self.setGeometry(400, 400, 400, 350)
        self.setMinimumSize(400, 350)

        self.instr = QLabel(self)
        self.instr.setText('В поле ввода использовать только\nвыбранные переменные.\n'
                           'Разрешено использование символов\n"+"  "-"  "*"  "/"  "**"  "(...)",\nфункций '
                           'из библиотеки math\nиз списка в виде: "function(...)"\nи функции abs() в виде: "abs(...)".'
                           '\nИсключения: "pi", "e", "log(a, x)".')
        self.instr.move(30, 10)
        self.instr.resize(270, 160)

        self.yes = '"(a)sin(h)", "(a)cos(h)",\n"(a)tan(h)", "pi", "e",\n"log", "gamma".'
        self.funcs = QLabel(f'Список разрешённых\nфункций из math:\n{self.yes}', self)
        self.funcs.move(270, 12)
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

    def resizeEvent(self, event):
        x_center = self.size().width() // 2
        y_center = self.size().height() // 2

        self.instr.move(x_center - 170, y_center - 165)
        self.funcs.move(x_center + 70, y_center - 163)

        self.instr2.move(x_center - 150, y_center + 10)

        self.fx.move(x_center - 170, y_center + 45)
        self.fy.move(x_center - 110, y_center + 45)
        self.fxy.move(x_center - 50, y_center + 45)

        self.example1.move(x_center - 160, y_center + 75)
        self.example2.move(x_center - 160, y_center + 95)
        self.example3.move(x_center - 160, y_center + 115)

        self.please.move(x_center + 20, y_center - 25)
        self.pict.move(x_center + 25, y_center)

    def paintEvent(self, event):
        x_center = self.size().width() // 2
        y_center = self.size().height() // 2

        qp = QPainter()
        qp.begin(self)

        qp.setPen(QPen(QColor('grey'), 3))
        qp.drawPolygon(QPolygonF([QPointF((x_center - 202), (y_center - 177)),
                                  QPointF((x_center + 202), (y_center - 177)),
                                  QPointF((x_center + 202), (y_center + 177)),
                                  QPointF((x_center - 202), (y_center + 177))]))

        qp.end()
