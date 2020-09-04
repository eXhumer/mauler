#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# mauler - Shows outdated Nintendo Switch titles
# Copyright (C) 2020 eXhumer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from pathlib import Path
from mauler import config
from mauler import titles
from mauler.updates import get_all_title_version_info
from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, \
    QVBoxLayout, QDesktopWidget, QHBoxLayout, QLineEdit, QPushButton, \
    QHeaderView, QMessageBox, QAbstractItemView
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import pyqtSlot, Qt, QRunnable, QObject, pyqtSignal, \
    QThreadPool


class ScanWorkerSignals(QObject):
    finished = pyqtSignal()


class ScanWorker(QRunnable):
    def __init__(self, scan_path: Path):
        super().__init__()
        self.scan_path = scan_path
        self.signals = ScanWorkerSignals()

    @pyqtSlot()
    def run(self):
        if self.scan_path.is_dir():
            already_exists = False

            for exist_scan_path in config.paths.scan:
                if self.scan_path == exist_scan_path:
                    already_exists = True
                    break

            if not already_exists:
                config.paths.scan.append(self.scan_path)
                config.save()

            try:
                titles.scan(self.scan_path)
            finally:
                self.signals.finished.emit()

        else:
            QMessageBox.information(self, 'Error processing scan path',
                                    'The path specified to scan is not a ' +
                                    'valid directory!')


class AppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()

        self.setWindowIcon(QIcon('images/icon.jpg'))
        self.setWindowTitle('Mauler')

        screen = QDesktopWidget().screenGeometry()
        left = int(screen.width() / 4)
        top = int(screen.height() / 4)
        width = int(screen.width() / 2)
        height = int(screen.height() / 2)
        self.setGeometry(left, top, width, height)

        self.layout = AppWindowLayout(self)

    def on_scan(self):
        scan_path = Path(self.layout.header.textbox.text()).resolve()
        scan_worker = ScanWorker(scan_path)
        scan_worker.signals.finished.connect(self.layout.table.refresh_table)
        self.threadpool.start(scan_worker)


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
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

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
            if latest > available:
                red_color = QColor('red')
                self.item(rowIdx, 0).setBackground(red_color)
                self.item(rowIdx, 1).setBackground(red_color)
                self.item(rowIdx, 2).setBackground(red_color)
            rowIdx += 1

        self.setRowCount(rowIdx)
