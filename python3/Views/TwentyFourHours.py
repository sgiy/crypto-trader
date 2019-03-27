from operator import itemgetter

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem)


class CTTwentyFourHours(QWidget):
    def __init__(self, CTMain=None):
        super().__init__()

        self._CTMain = CTMain

        self._tableWidget = QTableWidget()
        self._layout = QVBoxLayout()
        self._layout.addWidget(self._tableWidget)
        self.show_moves()
        self.setLayout(self._layout)

    def show_moves(self):
        exchanges = sorted(self._CTMain._Crypto_Trader._map_exchange_code_to_currency_code.keys())
        column_names = ['BaseCode', 'CurrencyCode'] + exchanges + ['Average 24-Hour Move']
        markets = self._CTMain._Crypto_Trader.load_24hour_moves()

        moves = []
        for code_base in markets:
            for code_curr in markets[code_base]:
                total_move = 0
                exchange_counter = 0
                entry = {
                    'BaseCode': code_base,
                    'CurrencyCode': code_curr
                }
                for exchange in markets[code_base][code_curr].keys():
                    entry[exchange] = markets[code_base][code_curr][exchange].get('24HrPercentMove', 0)
                    total_move += entry[exchange]
                    exchange_counter += 1

                if exchange_counter > 0:
                    entry['Avg_24HrPercentMove'] = total_move / exchange_counter
                    moves.append(entry)

        ordered_market_moves = sorted(moves, key=itemgetter('Avg_24HrPercentMove'), reverse=True)
        n_columns = len(column_names)

        self._tableWidget.setRowCount(len(ordered_market_moves))
        self._tableWidget.setColumnCount(n_columns)
        self._tableWidget.verticalHeader().hide()
        self._tableWidget.setHorizontalHeaderLabels(column_names)

        cell_index = 0
        for move in ordered_market_moves:
            self._tableWidget.setItem(cell_index, 0, QTableWidgetItem(move['BaseCode']))
            self._tableWidget.setItem(cell_index, 1, QTableWidgetItem(move['CurrencyCode']))
            for exchange_i in range(len(exchanges)):
                if exchanges[exchange_i] in move:
                    self._tableWidget.setItem(
                        cell_index,
                        exchange_i + 2,
                        QTableWidgetItem('{:.2f}%'.format(move[exchanges[exchange_i]]))
                    )
                    if move[exchanges[exchange_i]] > 0:
                        self._tableWidget.item(cell_index, exchange_i + 2).setForeground(
                            self._CTMain._Parameters.Color['green_bold']
                        )
                    else:
                        self._tableWidget.item(cell_index, exchange_i + 2).setForeground(
                            self._CTMain._Parameters.Color['red_bold']
                        )
            self._tableWidget.setItem(
                cell_index,
                n_columns - 1,
                QTableWidgetItem('{:.2f}%'.format(move['Avg_24HrPercentMove']))
            )
            if move['Avg_24HrPercentMove'] > 0:
                self._tableWidget.item(cell_index, n_columns - 1).setForeground(
                    self._CTMain._Parameters.Color['green_bold']
                )
            else:
                self._tableWidget.item(cell_index, n_columns - 1).setForeground(
                    self._CTMain._Parameters.Color['red_bold']
                )
            cell_index += 1
