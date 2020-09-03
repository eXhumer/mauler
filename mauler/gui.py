from pathlib import Path
from mauler import config
from mauler import titles
from mauler.updates import get_all_title_version_info
from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, \
    QVBoxLayout, QDesktopWidget, QHBoxLayout, QLineEdit, QPushButton, \
    QHeaderView, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, Qt


class AppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('images/icon.jpg'))
        self.setWindowTitle('Mauler')

        screen = QDesktopWidget().screenGeometry()
        left = int(screen.width() / 4)
        top = int(screen.height() / 4)
        width = int(screen.width() / 2)
        height = int(screen.height() / 2)
        self.setGeometry(left, top, width, height)

        self.layout = AppWindowLayout(self)

    @pyqtSlot()
    def on_scan(self):
        scan_path = Path(self.layout.header.textbox.text()).resolve()

        if scan_path.is_dir():
            if str(scan_path) not in config.paths.scan:
                config.paths.scan.append(str(scan_path))
                config.save()

            scan_res = titles.scan(str(scan_path))

            if scan_res > 0:
                self.layout.table.refresh_table()

        else:
            QMessageBox.information(self, 'Error processing scan path',
                                    'The path specified to scan is not a ' +
                                    'valid directory!')


class AppWindowHeader(QHBoxLayout):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.textbox = QLineEdit(parent)
        self.textbox.setMinimumWidth(25)
        self.textbox.setAlignment(Qt.AlignLeft)
        self.textbox.setText(str(Path(config.paths.scan[0]).resolve()))
        self.addWidget(self.textbox)

        self.scan = QPushButton('Scan', parent)
        self.scan.clicked.connect(parent.on_scan)
        self.addWidget(self.scan)


class AppWindowLayout(QVBoxLayout):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.header = AppWindowHeader(parent)
        self.addLayout(self.header)

        self.table = AppWindowTable(parent)
        self.addWidget(self.table)


class AppWindowTable(QTableWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setColumnCount(3)

        headers = [
            QTableWidgetItem('Title ID'),
            QTableWidgetItem('Available Version'),
            QTableWidgetItem('Latest Version')
        ]

        for idx, header_item in enumerate(headers):
            self.setHorizontalHeaderItem(idx, header_item)

        header = self.horizontalHeader()

        for idx, header_item in enumerate(headers):
            header.setSectionResizeMode(idx, QHeaderView.Stretch if idx == 0
                                        else QHeaderView.ResizeToContents)

        self.setSortingEnabled(True)
        self.refresh_table()

    @pyqtSlot()
    def refresh_table(self):
        self.setRowCount(0)

        title_version_info = get_all_title_version_info()
        self.setRowCount(len(title_version_info))

        rowIdx = 0
        for title_id, version_info in title_version_info.items():
            available = version_info['available']
            latest = version_info['latest']
            self.setItem(rowIdx, 0, QTableWidgetItem(title_id))
            self.setItem(rowIdx, 1, QTableWidgetItem(str(available)))
            self.setItem(rowIdx, 2, QTableWidgetItem(str(latest)))
            rowIdx += 1

        self.setRowCount(rowIdx)
