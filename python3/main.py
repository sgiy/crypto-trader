import sys

from PyQt5.QtWidgets import (QApplication, QWidget, QComboBox, QStyleFactory,
    QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QButtonGroup)
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QTimer

import pyqtgraph as pg

from config import *

from CryptoTrader import CryptoTrader

import ipdb

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Crypto Trader'
        self.left = WINDOW_SIZE['left']
        self.top = WINDOW_SIZE['top']
        self.width = WINDOW_SIZE['width']
        self.height = WINDOW_SIZE['height']
        self.table_rows_one_direction = DISPLAY_BOOK_DEPTH
        self.crypto_trader = CryptoTrader(API_KEYS)
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        if 'Fusion' in QStyleFactory.keys():
            self.changeStyle('Fusion')

        self.buttons_nav_home = QPushButton('Home', self)
        self.buttons_nav_home.clicked.connect(self.draw_view_home)
        self.buttons_nav_compare = QPushButton('Compare', self)
        self.buttons_nav_compare.clicked.connect(self.draw_view_home)
        self.buttons_nav_settings = QPushButton('Settings', self)
        self.buttons_nav_settings.clicked.connect(self.draw_view_settings)

        self.nav_bar = QVBoxLayout()
        self.nav_bar.addWidget(self.buttons_nav_home)
        self.nav_bar.addWidget(self.buttons_nav_compare)
        self.nav_bar.addWidget(self.buttons_nav_settings)
        self.nav_bar.addStretch(1)

        top_level_layout = QGridLayout()
        self.view_layout = QGridLayout()
        top_level_layout.addLayout(self.nav_bar, 1, 0)
        top_level_layout.addLayout(self.view_layout, 1, 1, 1, 4)

        self.setLayout(top_level_layout)
        self.draw_view_home()
        self.show()

    def clear_view(self):
        # for i in reversed(range(self.view_layout.count())):
            # ipdb.set_trace()
            # widget = self.view_layout.takeAt(i).widget()
            # if widget is not None:
            #     widget.setParent(None)
        def deleteItems(layout):
            if layout is not None:
                while layout.count():
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
                    else:
                        deleteItems(item.layout())

        deleteItems(self.view_layout)

    def draw_view_home(self):
        dropdown_base_curr = QComboBox()
        dropdown_base_curr.addItems(['BTC'])

        label_base_curr = QLabel("&Base:")
        label_base_curr.setBuddy(dropdown_base_curr)

        dropdown_curr_curr = QComboBox()
        dropdown_curr_curr.addItems(['XRP', 'SALT'])

        label_curr_curr = QLabel("&Currency:")
        label_curr_curr.setBuddy(dropdown_curr_curr)

        topLayout = QHBoxLayout()
        topLayout.addWidget(label_base_curr)
        topLayout.addWidget(dropdown_base_curr)
        topLayout.addWidget(label_curr_curr)
        topLayout.addWidget(dropdown_curr_curr)
        topLayout.addStretch(1)

        self.tableWidget = QtGui.QTableWidget()
        self.tableWidget.setRowCount(2 * self.table_rows_one_direction)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(['Price','Quantity','XRP sum','BTC sum'])
        self.test()

        plot = pg.PlotWidget()

        self.clear_view()
        self.view_layout.addLayout(topLayout, 0, 0, 1, 2)
        self.view_layout.addWidget(self.tableWidget, 2, 0)
        self.view_layout.addWidget(plot, 2, 1)

        timer = QTimer(self)
        timer.timeout.connect(self.test)
        timer.start(1000)

    def draw_view_settings(self):
        styleComboBox = QComboBox()
        styleComboBox.addItems(QStyleFactory.keys())
        styleComboBox.activated[str].connect(self.changeStyle)

        self.clear_view()
        self.view_layout.addWidget(styleComboBox, 1, 1)

    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))

    def test(self):
        color_green = QtGui.QColor(40,167,69)
        color_red = QtGui.QColor(220,53,69)
        align_right = Qt.AlignRight

        results = self.crypto_trader.trader['Bittrex'].load_order_book("BTC-SALT")
        for cell_index in range(2 * self.table_rows_one_direction):
            self.tableWidget.setItem(cell_index,0, QtGui.QTableWidgetItem(""))
            self.tableWidget.setItem(cell_index,1, QtGui.QTableWidgetItem(""))
        sum_bid = 0
        sum_bid_base = 0
        for bid in results['Bid']:
            self.tableWidget.setItem(self.table_rows_one_direction + bid, 0, QtGui.QTableWidgetItem("{0:.8f}".format(results['Bid'][bid]['Price'])))
            self.tableWidget.setItem(self.table_rows_one_direction + bid, 1, QtGui.QTableWidgetItem("{0:.8f}".format(results['Bid'][bid]['Quantity'])))
            sum_bid += results['Bid'][bid]['Quantity']
            sum_bid_base += results['Bid'][bid]['Quantity'] * results['Bid'][bid]['Price']
            self.tableWidget.setItem(self.table_rows_one_direction + bid, 2, QtGui.QTableWidgetItem("{0:.8f}".format(sum_bid)))
            self.tableWidget.setItem(self.table_rows_one_direction + bid, 3, QtGui.QTableWidgetItem("{0:.8f}".format(sum_bid_base)))
            for i in range(4):
                self.tableWidget.item(self.table_rows_one_direction + bid, i).setBackground(color_green)
                self.tableWidget.item(self.table_rows_one_direction + bid, i).setTextAlignment(align_right)

        sum_ask = 0
        sum_ask_base = 0
        for ask in results['Ask']:
            self.tableWidget.setItem(self.table_rows_one_direction - 1 - ask, 0, QtGui.QTableWidgetItem("{0:.8f}".format(results['Ask'][ask]['Price'])))
            self.tableWidget.setItem(self.table_rows_one_direction - 1 - ask, 1, QtGui.QTableWidgetItem("{0:.8f}".format(results['Ask'][ask]['Quantity'])))
            sum_ask += results['Ask'][ask]['Quantity']
            sum_ask_base += results['Ask'][ask]['Quantity'] * results['Ask'][ask]['Price']
            self.tableWidget.setItem(self.table_rows_one_direction - 1 - ask, 2, QtGui.QTableWidgetItem("{0:.8f}".format(sum_ask)))
            self.tableWidget.setItem(self.table_rows_one_direction - 1 - ask, 3, QtGui.QTableWidgetItem("{0:.8f}".format(sum_ask_base)))
            for i in range(4):
                self.tableWidget.item(self.table_rows_one_direction - 1 - ask, i).setBackground(color_red)
                self.tableWidget.item(self.table_rows_one_direction - 1 - ask, i).setTextAlignment(align_right)

if __name__ == '__main__':
    app = QApplication([])
    ex = App()
    sys.exit(app.exec_())
