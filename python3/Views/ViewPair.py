from datetime import datetime

from PyQt5.QtChart import (QChartView, QCandlestickSet, QCandlestickSeries, QDateTimeAxis, QValueAxis)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import (QWidget, QStyleFactory, QGridLayout, QLabel, QHBoxLayout, QApplication, QSplitter,
                             QPushButton, QGraphicsLineItem, QGraphicsTextItem)

from Views.Dropdown import Dropdown
from Views.OpenOrdersWidget import CTOpenOrdersWidget
from Views.OrderBook import CTOrderBook
from Views.RecentTradesWidget import CTRecentTradesWidget
from Views.TradeWidget import CTTradeWidget


class CTChartView(QChartView):
    def __init__(self, parent):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.chart = self.chart()
        self.chart.legend().setVisible(False)
        self._chart_loaded = False

        self._chart_horizontal_line = QGraphicsLineItem(0, 0, 0, 0)
        pen = self._chart_horizontal_line.pen()
        pen.setStyle(Qt.DashLine)
        self._chart_horizontal_line.setPen(pen)
        self.scene().addItem(self._chart_horizontal_line)
        self._chart_vertical_line = QGraphicsLineItem(0, 0, 0, 0)
        self._chart_vertical_line.setPen(pen)
        self.scene().addItem(self._chart_vertical_line)

        self._chart_tooltip = QGraphicsTextItem("")
        self._chart_tooltip.setPos(100, 20)
        self.scene().addItem(self._chart_tooltip)

        self._chart_crosshair = QGraphicsTextItem("")
        self._chart_crosshair.setPos(600, 20)
        self.scene().addItem(self._chart_crosshair)

        margins = self.chart.margins()
        margins.setTop(margins.top() + 80)
        self.chart.setMargins(margins)

    def mouseMoveEvent(self, event):
        self._chart_horizontal_line.setLine(0, event.pos().y(), self.width(), event.pos().y())
        self._chart_vertical_line.setLine(event.pos().x(), 0, event.pos().x(), self.height())

        self._crosshair_coords = self.chart.mapToValue(event.pos(), self.chart.series()[0])

        self._chart_crosshair.setPlainText(" time:\t{0}\n level:\t{1:.8f}".format(
            datetime.fromtimestamp(int(self._crosshair_coords.x()/1000)).strftime('%Y-%m-%d %H:%M:%S'),
            self._crosshair_coords.y()
        ))

        return QChartView.mouseMoveEvent(self, event)


class CTCandlestickSet(QCandlestickSet):
    def __init__(self, timestamp, c_open, c_high, c_low, c_close, volume, base_volume, parent):
        super().__init__(c_open, c_high, c_low, c_close, timestamp, parent)
        self._volume = volume
        self._base_volume = base_volume
        self._base_curr = parent._base_curr
        self._curr_curr = parent._curr_curr
        self.hovered[bool].connect(self.draw_tool_tip)

    def draw_tool_tip(self, status):
        if status:
            self.parent()._chart_view._chart_tooltip.setPlainText(
                " time:\t{0}\n open:\t{1:.8f}, close: {2:.8f}\n high:\t{3:.8f}, low:   {4:.8f}\n volume {5}: {6:,.2f}, volume {7}: {8:,.2f}".format(
                    datetime.fromtimestamp(int(self.timestamp()/1000)).strftime('%Y-%m-%d %H:%M:%S'),
                    self.open(),
                    self.close(),
                    self.high(),
                    self.low(),
                    self._curr_curr,
                    self._volume,
                    self._base_curr,
                    self._base_volume
            ))


class CTViewPair(QWidget):
    def __init__(self, CTMain=None, exchange='', base_code='', curr_code='', chart_lookback='', chart_interval='',
                 order_book_depth=5):
        super().__init__()
        self._CTMain = CTMain
        self._exchange = exchange
        self._base_curr = base_code
        self._curr_curr = curr_code
        self._chart_lookback = chart_lookback
        self._chart_interval = chart_interval
        self._order_book_depth = order_book_depth

        if 'Fusion' in QStyleFactory.keys():
            self.change_style('Fusion')

        self._layout = QGridLayout()
        self.setLayout(self._layout)

        self.draw_view()
        self.show()

    def refresh_dropdown_exchange_change(self, exchange, default_base=None, default_curr=None):
        self._exchange = exchange
        if default_base is None:
            default_base = self._dropdown_base_curr.currentText
        if default_curr is None:
            default_curr = self._dropdown_curr_curr.currentText
        base_codes = sorted(list(self._CTMain._Crypto_Trader.trader[exchange]._active_markets))
        self._dropdown_base_curr.clear()
        self._dropdown_base_curr.addItems(base_codes)
        if default_base not in base_codes:
            default_base = base_codes[0]
        self._dropdown_base_curr.setCurrentText(default_base)
        self.refresh_dropdown_base_change(default_base, default_curr)

    def refresh_dropdown_base_change(self, base_curr, default_curr=None):
        self._base_curr = base_curr
        if default_curr is None:
            default_curr = self._dropdown_curr_curr.currentText
        curr_codes = sorted(list(self._CTMain._Crypto_Trader.trader[self._exchange]._active_markets[base_curr]))
        self._dropdown_curr_curr.clear()
        self._dropdown_curr_curr.addItems(curr_codes)
        if default_curr not in curr_codes:
            default_curr = curr_codes[0]
        self._dropdown_curr_curr.setCurrentText(default_curr)
        self.refresh_dropdown_curr_change(default_curr)

    def refresh_dropdown_curr_change(self, curr_curr):
        self._curr_curr = curr_curr
        self._market_symbol = self._CTMain._Crypto_Trader.get_market_symbol(
            self._exchange,
            self._base_curr,
            curr_curr
        )

        self.initiate_widgets()

    def draw_view(self):
        self._order_book_widget = CTOrderBook(
            self._CTMain,
            None,
            None,
            None,
            None,
            self._order_book_depth
            )

        self.CandlestickSeries = QCandlestickSeries()
        self.CandlestickSeries.setIncreasingColor(Qt.green)
        self.CandlestickSeries.setDecreasingColor(Qt.red)

        self.VolumeBarSeries = QCandlestickSeries()
        self.VolumeBarSeries.setBodyWidth(1.0)
        self.VolumeBarSeries.setIncreasingColor(Qt.green)
        self.VolumeBarSeries.setDecreasingColor(Qt.red)

        self._chart_view = CTChartView(self)
        self._chart_view_volume = QChartView(self)
        self._chart_view_volume.chart().legend().setVisible(False)

        exchanges = self._CTMain._Crypto_Trader.trader.keys()
        self._dropdown_exchange = Dropdown(exchanges, self._exchange)
        self._dropdown_exchange.activated[str].connect(self.refresh_dropdown_exchange_change)

        base_codes = sorted(self._CTMain._Crypto_Trader.trader[self._exchange]._active_markets.keys())
        self._dropdown_base_curr = Dropdown(base_codes, self._base_curr)
        self._dropdown_base_curr.activated[str].connect(self.refresh_dropdown_base_change)

        curr_codes = sorted(self._CTMain._Crypto_Trader.trader[self._exchange]._active_markets[self._base_curr].keys())
        self._dropdown_curr_curr = Dropdown(curr_codes, self._curr_curr)
        self._dropdown_curr_curr.activated[str].connect(self.refresh_dropdown_curr_change)

        label_lookback = QLabel("Lookback:")
        self._chart_dropdown_lookback = Dropdown(
            self._CTMain._Parameters.get_chart_lookback_windows(),
            self._chart_lookback
        )
        self._chart_dropdown_lookback.currentTextChanged.connect(self.draw_chart)
        label_interval = QLabel("Interval:")
        self._chart_dropdown_interval = Dropdown(
            self._CTMain._Parameters.get_chart_intervals(),
            self._chart_interval
        )
        self._chart_dropdown_interval.currentTextChanged.connect(self.draw_chart)

        self._market_symbol = self._CTMain._Crypto_Trader.get_market_symbol(
            self._exchange,
            self._base_curr,
            self._curr_curr
        )
        self._trade_widget = CTTradeWidget(
            self._CTMain,
            self._exchange,
            self._base_curr,
            self._curr_curr,
            self._market_symbol
        )
        self._open_orders_widget = CTOpenOrdersWidget(
            self._CTMain,
            self._exchange,
            self._market_symbol
        )
        self._recent_trades_widget = CTRecentTradesWidget(
            self._CTMain,
            self._exchange,
            self._base_curr,
            self._curr_curr,
            self._market_symbol
        )
        self.refresh_dropdown_exchange_change(
            self._exchange,
            self._base_curr,
            self._curr_curr
        )

        label_exchange = QLabel("&Exchange:")
        label_exchange.setBuddy(self._dropdown_exchange)
        label_base_curr = QLabel("&Base:")
        label_base_curr.setBuddy(self._dropdown_base_curr)
        label_curr_curr = QLabel("&Currency:")
        label_curr_curr.setBuddy(self._dropdown_curr_curr)

        self._debug_button = QPushButton()
        self._debug_button.setText("Debug")
        self._debug_button.clicked.connect(self.debug)

        top_layout = QHBoxLayout()
        top_layout.addWidget(label_exchange)
        top_layout.addWidget(self._dropdown_exchange)
        top_layout.addWidget(label_base_curr)
        top_layout.addWidget(self._dropdown_base_curr)
        top_layout.addWidget(label_curr_curr)
        top_layout.addWidget(self._dropdown_curr_curr)
        top_layout.addWidget(label_lookback)
        top_layout.addWidget(self._chart_dropdown_lookback)
        top_layout.addWidget(label_interval)
        top_layout.addWidget(self._chart_dropdown_interval)
        top_layout.addWidget(self._debug_button)
        top_layout.addStretch(1)

        self._layout.addLayout(top_layout, 0, 0, 1, 10)
        self._splitter_top = QSplitter(Qt.Horizontal)
        self._splitter_left = QSplitter(Qt.Vertical)
        self._splitter_left.addWidget(self._order_book_widget)
        self._splitter_left.addWidget(self._recent_trades_widget)
        self._splitter_left.addWidget(self._trade_widget)
        self._splitter_left.setSizes([500,100,100])

        self._splitter_right = QSplitter(Qt.Vertical)
        self._splitter_right.addWidget(self._chart_view)
        self._splitter_right.addWidget(self._chart_view_volume)
        self._splitter_right.addWidget(self._open_orders_widget)
        self._splitter_right.setSizes([500,100,100])

        self._splitter_top.addWidget(self._splitter_left)
        self._splitter_top.addWidget(self._splitter_right)
        window_width = self._CTMain.frameGeometry().width()
        self._splitter_top.setSizes([round(0.3*window_width), round(0.7 * window_width)])
        self._layout.addWidget(self._splitter_top, 1, 0, 9, 10)

        # self._CTMain._Timer.start(1000)
        # self._CTMain._Timer.timeout.connect(self.refresh)

    @staticmethod
    def change_style(style_name):
        QApplication.setStyle(QStyleFactory.create(style_name))

    @staticmethod
    def debug():
        import ipdb
        ipdb.set_trace()

    # def refresh(self):
    #     t = threading.Thread(target = self.refresh_widgets)
    #     t.start()
    #     t.join(1)

    def initiate_widgets(self):
        self._order_book_widget.refresh_order_book(
            self._exchange,
            self._market_symbol,
            self._base_curr,
            self._curr_curr
            )
        self._trade_widget.update_currencies(
            self._exchange,
            self._base_curr,
            self._curr_curr,
            self._market_symbol
            )
        self._open_orders_widget.update_market(
            self._exchange,
            self._market_symbol
        )
        self._recent_trades_widget.update_market(
            self._exchange,
            self._base_curr,
            self._curr_curr,
            self._market_symbol
        )
        self.draw_chart()

    def draw_chart(self):
        exchange = self._exchange
        market_symbol = self._market_symbol
        interval_name = self._chart_dropdown_interval.currentText()
        lookback_name = self._chart_dropdown_lookback.currentText()
        interval = self._CTMain._Parameters.ChartInterval[interval_name]
        lookback = self._CTMain._Parameters.ChartLookbackWindow[lookback_name]

        load_chart = self._CTMain._Crypto_Trader.trader[exchange].load_chart_data(
            market_symbol,
            interval,
            lookback
        )

        self.CandlestickSeries.clear()
        self.VolumeBarSeries.clear()
        ch_min = load_chart[0][3]
        ch_max = load_chart[0][2]
        t_min = load_chart[0][0]
        t_max = load_chart[0][0]
        v_max = load_chart[0][6]

        for point in load_chart:
            candle = CTCandlestickSet(point[0] * 1000, point[1], point[2], point[3], point[4], point[5], point[6], self)
            self.CandlestickSeries.append(candle)
            ch_min = min(ch_min, point[3])
            ch_max = max(ch_max, point[2])
            t_min = min(t_min, point[0])
            t_max = max(t_max, point[0])
            v_max = max(v_max, point[6])

        min_y = max(0, ch_min - 0.15 * (ch_max - ch_min))
        max_y = ch_max + 0.1 * (ch_max - ch_min)

        max_volume = 0
        for point in load_chart:
            # high = min_y + 0.1 * (max_y - min_y)  * point[6] / v_max
            # low = min_y
            v_low = 0
            v_high = point[6]
            max_volume = max(max_volume, point[6])
            if point[4] >= point[1]:
                v_open = v_low
                v_close = v_high
            else:
                v_open = v_high
                v_close = v_low
            volume_candle = QCandlestickSet(v_open, v_high, v_low, v_close, point[0] * 1000, self)
            self.VolumeBarSeries.append(volume_candle)

        if not self._chart_view._chart_loaded:
            self._chart_view.chart.addSeries(self.CandlestickSeries)
            self._chart_view_volume.chart().addSeries(self.VolumeBarSeries)
            self._chart_view._chart_loaded = True

        axis_x = QDateTimeAxis()
        axis_x.setFormat("dd-MM-yyyy h:mm")
        axis_x.setRange(
            datetime.fromtimestamp(int(t_min) - 30 * interval),
            datetime.fromtimestamp(int(t_max) + 30 * interval)
        )
        self._chart_view.chart.setAxisX(axis_x, self.CandlestickSeries)

        axis_y = QValueAxis()
        axis_y.setRange(min_y, max_y)
        self._chart_view.chart.setAxisY(axis_y, self.CandlestickSeries)

        axis_x2 = QDateTimeAxis()
        axis_x2.setFormat("dd-MM-yyyy h:mm")
        axis_x2.setRange(
            datetime.fromtimestamp(int(t_min) - 30 * interval),
            datetime.fromtimestamp(int(t_max) + 30 * interval)
        )
        self._chart_view_volume.chart().setAxisX(axis_x2, self.VolumeBarSeries)

        axis_y2 = QValueAxis()
        axis_y2.setRange(0, max_volume)
        self._chart_view_volume.chart().setAxisY(axis_y2, self.VolumeBarSeries)
        # self.VolumeBarSeries.attachAxis(axis_x)
        # self.VolumeBarSeries.attachAxis(axis_y)
