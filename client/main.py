import os
import sys

from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QPixmap, Qt
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit, QMessageBox
from qt_material import apply_stylesheet

from client import communication

app = QtWidgets.QApplication(sys.argv)


class Checker:
    def __init__(self, color, x, y, image, parent):
        self.color = color
        self.king = False

        self.obj = QLabel(parent)
        self.obj.setPixmap(image)
        self.obj.setGeometry(x * 75, y * 75, 100, 100)


class User:
    def __init__(self):
        self.authorized = False
        self.username = None

    def toggle_authorized(self):
        self.authorized = not self.authorized

    def sign_out(self):
        self.toggle_authorized()
        self.username = None

    # def sign_in(self):


class BaseWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Checkers')
        self.setFixedSize(800, 600)


class UserWindow(BaseWindow):
    def __init__(self, user):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.user = user
        self.is_sign_in = False
        self.is_sign_up = False
        self.buttons = None
        self.init_ui()

    def init_ui(self):
        if self.user.authorized:
            self.buttons = {
                'name': QLabel(self.user.username),
                'sign_out': QPushButton('Sign out'),
                'back': QPushButton('Back')
            }
            self.buttons['sign_out'].clicked.connect(self.sign_out)
            self.buttons['back'].clicked.connect(lambda: self.close())
        elif self.is_sign_in or self.is_sign_up:
            self.buttons = {
                'username': QLineEdit(),
                'password': QLineEdit(),
                'ok': QPushButton('OK'),
                'back': QPushButton('Back')
            }
            self.buttons['username'].setPlaceholderText('Username')
            self.buttons['password'].setPlaceholderText('Password')
            if self.is_sign_in:
                self.buttons['ok'].clicked.connect(self.sign_in)
            elif self.is_sign_up:
                self.buttons['ok'].clicked.connect(self.sign_up)
            self.buttons['back'].clicked.connect(self.back_from_sign_in_or_our)
        else:
            self.buttons = {
                'sign_in': QPushButton('Sign in'),
                'sign_up': QPushButton('Sign up'),
                'back': QPushButton('Back')
            }
            self.buttons['sign_in'].clicked.connect(self.start_sign_in)
            self.buttons['sign_up'].clicked.connect(self.start_sign_up)
            self.buttons['back'].clicked.connect(lambda: self.close())

        for button in self.buttons.values():
            button.setFixedWidth(300)
            self.layout.addWidget(button, alignment=Qt.AlignCenter)

    def start_sign_in(self):
        self.is_sign_in = True
        for item in self.buttons.values():
            item.deleteLater()
        self.init_ui()

    def start_sign_up(self):
        self.is_sign_up = True
        for item in self.buttons.values():
            item.deleteLater()
        self.init_ui()

    def sign_up(self):
        username = self.buttons['username'].text()
        password = self.buttons['password'].text()
        is_exit = False
        message = None
        if username and password:
            resp = communication.sign_up(username, password)
            if resp.status_code == 409:
                message = 'Invalid username or password'
            elif resp.status_code == 201:
                self.user.toggle_authorized()
                self.user.username = username
                self.is_sign_up = False
                is_exit = True
                message = 'Sign Up successful.'
        else:
            message = 'Username or password are empty'
        if message:
            msg = QMessageBox()
            msg.setText(message)
            msg.exec()
            if is_exit:
                self.close()

    def sign_in(self):
        username = self.buttons['username'].text()
        password = self.buttons['password'].text()
        is_exit = False
        if username and password:
            resp = communication.sign_in(username, password)
            if resp.status_code == 404:
                message = 'Invalid username or password'
            elif resp.status_code == 200:
                self.user.toggle_authorized()
                self.user.username = username
                self.is_sign_in = False
                is_exit = True
                message = 'Sign In successful.'
            else:
                message = 'Something went wrong. Please, try again later'
        else:
            message = 'Username or password are empty'
        if message:
            msg = QMessageBox()
            msg.setText(message)
            msg.exec()
            if is_exit:
                self.close()

    def sign_out(self):
        self.user.sign_out()
        for item in self.buttons.values():
            item.deleteLater()
        self.init_ui()

    def back_from_sign_in_or_our(self):
        self.is_sign_up = False
        self.is_sign_in = False
        self.close()


class MenuWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        self.user = User()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.user_window = None
        self.buttons = {
            'account': QPushButton('Account'),
            'new': QPushButton('Start new game'),
            'join': QPushButton('Join to existing game'),
            'exit': QPushButton('Exit')
        }

        self.init_ui()

    def init_ui(self):
        for name, button in self.buttons.items():
            if name in ('new', 'join') and not self.user.authorized:
                continue
            button.setFixedWidth(300)
            self.layout.addWidget(button, alignment=Qt.AlignCenter)

        self.buttons['account'].clicked.connect(self.init_user_window)
        self.buttons['exit'].clicked.connect(lambda: self.close())

    def init_user_window(self):
        self.user_window = UserWindow(self.user)
        self.user_window.show()


class CheckersWindow(BaseWindow):
    def __init__(self):
        super().__init__()

        self.field = None
        self._field = None
        self.checkers = []
        self.resources = self._load_resources()
        self._create_field()

    def _load_resources(self):
        resources = {}
        path = 'resources'
        for _file in os.listdir(path):
            file = os.path.join(path, _file)
            image = QPixmap(file).scaled(75, 75, QtCore.Qt.KeepAspectRatio)
            resources[os.path.splitext(_file)[0]] = image
        return resources

    def _create_field(self):
        field = []
        _field = []
        for i in range(8):
            row = []
            _row = []
            for j in range(8):
                square_obj = QLabel(self)
                if (i + j) % 2:
                    square_image = 'black_marble'
                    if i < 3:
                        checker = Checker(False, j, i, self.resources['black_checker'], self)
                    elif i > 4:
                        checker = Checker(True, j, i, self.resources['white_checker'], self)
                    else:
                        checker = None
                else:
                    square_image = 'white_marble'
                    checker = None
                square_obj.setPixmap(self.resources[square_image])
                square_obj.setGeometry(j * 75, i * 75, 100, 100)
                row.append(square_obj)
                _row.append(checker)
            field.append(row)
            _field.append(_row)
        self.field = field
        self._field = _field

    def mousePressEvent(self, event):
        print(event.position())


def main():
    apply_stylesheet(app, theme='dark_teal.xml')

    # checkers_window = CheckersWindow()
    # checkers_window.show()

    menu_window = MenuWindow()
    menu_window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
