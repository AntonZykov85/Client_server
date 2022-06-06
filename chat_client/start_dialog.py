from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, QApplication, QLabel, qApp
from PyQt5.QtCore import QEvent


class UserNameDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.ok_pressed = False

        self.setWindowTitle('Hello!')
        self.setFixedSize(220, 93)

        self.label = QLabel('input username: ', self)
        self.label.setFixedSize(220, 20)
        self.move(10, 10)

        self.client_name = QLineEdit(self)
        self.client_name.setFixedSize(170, 20)
        self.client_name.move(10, 30)

        self.btn_ok = QPushButton('Start ', self)
        self.btn_ok.move(10, 60)
        self.btn_ok.clicked.connect(self.click)

        self.btn_cancel = QPushButton('Exit', self)
        self.btn_cancel.move(100, 60)
        self.btn_cancel.clicked.connect(qApp.exit)

        self.show()

    def click(self):
        if self.client_name.text():
            self.ok_pressed = True
            qApp.exit()


if __name__ == '__main__':
    app = QApplication([])
    dial = UserNameDialog()
    app.exec_()
