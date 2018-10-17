from PyQt5 import QtGui  # (the example applies equally well to PySide)
from PyQt5.QtCore import Qt
import pyqtgraph as pg
from Bittrex import Bittrex

## Always start by initializing Qt (only once per application)
app = QtGui.QApplication([])

## Define a top-level widget to hold everything
w = QtGui.QWidget()

bittrex = Bittrex(APIKey='', Secret='')

def test():
    color_green = QtGui.QColor(40,167,69)
    color_red = QtGui.QColor(220,53,69)
    align_right = Qt.AlignRight

    results = bittrex.load_order_book("BTC-XRP")
    for cell_index in range(2 * table_rows_one_direction):
        tableWidget.setItem(cell_index,0, QtGui.QTableWidgetItem(""))
        tableWidget.setItem(cell_index,1, QtGui.QTableWidgetItem(""))
    sum_bid = 0
    sum_bid_base = 0
    for bid in results['Bid']:
        tableWidget.setItem(table_rows_one_direction + bid, 0, QtGui.QTableWidgetItem("{0:.8f}".format(results['Bid'][bid]['Price'])))
        tableWidget.setItem(table_rows_one_direction + bid, 1, QtGui.QTableWidgetItem("{0:.8f}".format(results['Bid'][bid]['Quantity'])))
        sum_bid += results['Bid'][bid]['Quantity']
        sum_bid_base += results['Bid'][bid]['Quantity'] * results['Bid'][bid]['Price']
        tableWidget.setItem(table_rows_one_direction + bid, 2, QtGui.QTableWidgetItem("{0:.8f}".format(sum_bid)))
        tableWidget.setItem(table_rows_one_direction + bid, 3, QtGui.QTableWidgetItem("{0:.8f}".format(sum_bid_base)))
        for i in range(4):
            tableWidget.item(table_rows_one_direction + bid, i).setBackground(color_green)
            tableWidget.item(table_rows_one_direction + bid, i).setTextAlignment(align_right)

    sum_ask = 0
    sum_ask_base = 0
    for ask in results['Ask']:
        tableWidget.setItem(table_rows_one_direction - 1 - ask, 0, QtGui.QTableWidgetItem("{0:.8f}".format(results['Ask'][ask]['Price'])))
        tableWidget.setItem(table_rows_one_direction - 1 - ask, 1, QtGui.QTableWidgetItem("{0:.8f}".format(results['Ask'][ask]['Quantity'])))
        sum_ask += results['Ask'][ask]['Quantity']
        sum_ask_base += results['Ask'][ask]['Quantity'] * results['Ask'][ask]['Price']
        tableWidget.setItem(table_rows_one_direction - 1 - ask, 2, QtGui.QTableWidgetItem("{0:.8f}".format(sum_ask)))
        tableWidget.setItem(table_rows_one_direction - 1 - ask, 3, QtGui.QTableWidgetItem("{0:.8f}".format(sum_ask_base)))
        for i in range(4):
            tableWidget.item(table_rows_one_direction - 1 - ask, i).setBackground(color_red)
            tableWidget.item(table_rows_one_direction - 1 - ask, i).setTextAlignment(align_right)

## Create some widgets to be placed inside
btn = QtGui.QPushButton('press me')
btn.clicked.connect(test)

table_rows_one_direction = 5
tableWidget = QtGui.QTableWidget()
tableWidget.setRowCount(2 * table_rows_one_direction)
tableWidget.setColumnCount(4)
tableWidget.setHorizontalHeaderLabels(['Price','Quantity','XRP sum','BTC sum'])
test()

plot = pg.PlotWidget()

## Create a grid layout to manage the widgets size and position
layout = QtGui.QGridLayout()
w.setLayout(layout)

## Add widgets to the layout in their proper positions
layout.addWidget(btn, 0, 0)   # button goes in upper-left
layout.addWidget(tableWidget, 1, 0)   # text edit goes in middle-left
layout.addWidget(plot, 0, 1, 2, 1)  # plot goes on right side, spanning 3 rows

## Display the widget as a new window
w.show()

## Start the Qt event loop
app.exec_()
