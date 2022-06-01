import sys
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QLabel, QTableView, QDialog, QPushButton, \
    QLineEdit, QFileDialog, QMessageBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt

def gui_create_model(database):
    users_list = database.active_users_list()
    list_ = QStandardItemModel()
    list_.setHorizontalHeaderLabels(['Username', 'IP address', 'Port', 'Connection time'])
    for row in users_list:
        user, ip, port, time = row
        user = QStandardItem(user)
        user.setEditable(False)
        ip = QStandardItem(ip)
        ip.setEditable(False)
        port = QStandardItem(str(port))
        port.setEditable(False)
        time = QStandardItem(str(time.replace(microsecond=0)))
        time.setEditable(False)
        list_.appendRow([user, ip, port, time])
    return list_


def create_statistic_model(database):
    history_list = database.message_history()

    list = QStandardItemModel()
    list.setHorizontalHeaderLabels(
        ['Username', 'Last entrance', 'Message send', 'Get message'])
    for row in history_list:
        user, last_seen, sent, recvd = row
        user = QStandardItem(user)
        user.setEditable(False)
        last_seen = QStandardItem(str(last_seen.replace(microsecond=0)))
        last_seen.setEditable(False)
        sent = QStandardItem(str(sent))
        sent.setEditable(False)
        recvd = QStandardItem(str(recvd))
        recvd.setEditable(False)
        list.appendRow([user, last_seen, sent, recvd])
    return list

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        exitAction = QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(qApp.quit)

        self.refresh_button = QAction('Refresh list', self)
        self.config_btn = QAction('Server config', self)
        self.show_history_button = QAction('Users history', self)
        self.statusBar()
        self.toolbar = self.addToolBar('MainBar')
        self.toolbar.addAction(exitAction)
        self.toolbar.addAction(self.refresh_button)
        self.toolbar.addAction(self.show_history_button)
        self.toolbar.addAction(self.config_btn)
        self.setFixedSize(900, 750)
        self.setWindowTitle('Messaging Server alpha release')
        self.label = QLabel('Connected users list:', self)
        self.label.setFixedSize(300, 20)
        self.label.move(15, 35)
        self.active_clients_table = QTableView(self)
        self.active_clients_table.move(15, 50)
        self.active_clients_table.setFixedSize(765, 425)
        self.show()


class HistoryWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Users statistics')
        self.setFixedSize(625, 725)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.close_button = QPushButton('Close', self)
        self.close_button.move(255, 675)
        self.close_button.clicked.connect(self.close)
        self.history_table = QTableView(self)
        self.history_table.move(15, 15)
        self.history_table.setFixedSize(585, 625)
        self.show()


class ConfigWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setFixedSize(360, 250)
        self.setWindowTitle('Server config')
        self.db_path_label = QLabel('Path for BD: ', self)
        self.db_path_label.move(15, 15)
        self.db_path_label.setFixedSize(245, 20)
        self.db_path = QLineEdit(self)
        self.db_path.setFixedSize(255, 25)
        self.db_path.move(15, 35)
        self.db_path.setReadOnly(True)
        self.db_path_select = QPushButton('View...', self)
        self.db_path_select.move(270, 25)

        def open_file_dialog():
            global dialog
            dialog = QFileDialog(self)
            path = dialog.getExistingDirectory()
            path = path.replace('/', '\\')
            self.db_path.insert(path)

        self.db_path_select.clicked.connect(open_file_dialog)
        self.db_file_label = QLabel('BD filename: ', self)
        self.db_file_label.move(10, 70)
        self.db_file_label.setFixedSize(180, 15)
        self.db_file = QLineEdit(self)
        self.db_file.move(200, 70)
        self.db_file.setFixedSize(150, 20)
        self.port_label = QLabel('Port number for connect:', self)
        self.port_label.move(10, 110)
        self.port_label.setFixedSize(180, 15)
        self.port = QLineEdit(self)
        self.port.move(200, 108)
        self.port.setFixedSize(150, 20)
        self.ip_label = QLabel('Input IP connection:', self)
        self.ip_label.move(10, 150)
        self.ip_label.setFixedSize(180, 15)
        self.ip_label_note = QLabel(' Take this field false\n take connection frome any address.', self)
        self.ip_label_note.move(10, 170)
        self.ip_label_note.setFixedSize(500, 30)
        self.ip = QLineEdit(self)
        self.ip.move(200, 150)
        self.ip.setFixedSize(150, 20)
        self.save_btn = QPushButton('Save', self)
        self.save_btn.move(190, 220)
        self.close_button = QPushButton('Close', self)
        self.close_button.move(275, 220)
        self.close_button.clicked.connect(self.close)
        self.show()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.statusBar().showMessage('Test Statusbar Message')
    test_list = QStandardItemModel(ex)
    test_list.setHorizontalHeaderLabels(['Username', 'IP adress', 'Port', 'Connection time'])
    test_list.appendRow([QStandardItem('1'), QStandardItem('2'), QStandardItem('3')])
    test_list.appendRow([QStandardItem('4'), QStandardItem('5'), QStandardItem('6')])
    ex.active_clients_table.setModel(test_list)
    ex.active_clients_table.resizeColumnsToContents()
    print('JKJKJK')
    app.exec_()
    print('END')
    # app = QApplication(sys.argv)
    # message = QMessageBox
    # dial = ConfigWindow()
    #
    # app.exec_()