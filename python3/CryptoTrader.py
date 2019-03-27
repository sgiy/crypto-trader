import threading

from pydoc import locate


class CryptoTrader:
    def __init__(self, API_KEYS={}, SETTINGS={}):
        self.trader = {}
        self._map_currency_code_to_exchange_code = {}
        self._map_exchange_code_to_currency_code = {}
        self._active_markets = {}
        self._API_KEYS = API_KEYS
        self._SETTINGS = SETTINGS
        self.init_exchanges()
        self.update_api_keys()

    def init_exchanges(self):
        for exchange in self._SETTINGS.get('Exchange Classes to Initialize', []):
            exchange_file = locate('Exchanges.' + exchange)
            exchange_class = getattr(exchange_file, exchange)
            self.trader[exchange] = exchange_class()
        print('Initializing Currencies')
        self.init_currencies()
        print('Loading Active Markets')
        self.init_markets()

    def update_api_keys(self):
        self._SETTINGS['Exchanges with API Keys'] = []
        for exchange in self._API_KEYS.keys():
            self.trader[exchange].update_api_keys(
                self._API_KEYS[exchange].get('APIKey', ''),
                self._API_KEYS[exchange].get('Secret', ''),
                self._API_KEYS[exchange].get('APIPassword', '')
            )
            if self._API_KEYS[exchange].get('APIKey', '') != '':
                self._SETTINGS['Exchanges with API Keys'].append(exchange)

    def init_currencies(self):
        self._map_currency_code_to_exchange_code = {}
        self._map_exchange_code_to_currency_code = {}
        for exchange in self._SETTINGS.get('Exchanges to Load', []):
            print('Loading currencies for ' + exchange)
            t = threading.Thread(target=self.trader[exchange].update_currency_definitions)
            t.start()
            t.join(2)

        for exchange in self._SETTINGS.get('Exchanges to Load', []):
            currencies = self.trader[exchange]._currencies
            self.trader[exchange]._map_currency_code_to_exchange_code = {}
            self._map_exchange_code_to_currency_code[exchange] = {}
            for currency in currencies:
                try:
                    code = currency
                    if exchange in self._SETTINGS.get('Exchange Currency Rename Map', {}):
                        if currency in self._SETTINGS['Exchange Currency Rename Map'][exchange]:
                            code = self._SETTINGS['Exchange Currency Rename Map'][exchange][currency]

                    currency_name = currencies[currency]['Name']
                    exchange_name_column = exchange + 'Name'

                    if code not in self._map_currency_code_to_exchange_code:
                        self._map_currency_code_to_exchange_code[code] = {
                            'Name': code
                        }

                    # Populate maps on the exchange object
                    self.trader[exchange]._map_exchange_code_to_currency_code[currency] = code
                    self.trader[exchange]._map_currency_code_to_exchange_code[code] = currency

                    # Populate maps on the CryptoTrader object
                    self._map_exchange_code_to_currency_code[exchange][currency] = code
                    self._map_currency_code_to_exchange_code[code][exchange] = currency
                    self._map_currency_code_to_exchange_code[code][exchange_name_column] = currency_name

                    if code == self._map_currency_code_to_exchange_code[code]['Name']:
                        self._map_currency_code_to_exchange_code[code]['Name'] = currency_name

                except Exception as e:
                    print(str(e))

    def init_markets(self):
        for exchange in self._SETTINGS.get('Exchanges to Load', []):
            print('Loading market definitions for ' + exchange)
            t = threading.Thread(target=self.trader[exchange].update_market_definitions)
            t.start()
            t.join(5)

    def refresh_agg_active_markets(self):
        for exchange in self._SETTINGS.get('Exchanges to Load', []):
            for code_base in self.trader[exchange]._active_markets:
                if code_base not in self._active_markets:
                    self._active_markets[code_base] = {}
                for code_curr in self.trader[exchange]._active_markets[code_base]:
                    if code_curr not in self._active_markets[code_base]:
                        self._active_markets[code_base][code_curr] = {}
                    self._active_markets[code_base][code_curr][exchange] = \
                        self.trader[exchange]._active_markets[code_base][code_curr]

    def load_active_markets(self):
        for exchange in self._SETTINGS.get('Exchanges to Load', []):
            if not self.trader[exchange].has_implementation('ws_all_markets_best_bid_ask'):
                print('Loading active markets for ' + exchange)
                t = threading.Thread(target=self.trader[exchange].update_market_quotes)
                t.start()
                t.join(5)

        self.refresh_agg_active_markets()

        return self._active_markets

    def load_24hour_moves(self):
        for exchange in self._SETTINGS.get('Exchanges to Load', []):
            if not self.trader[exchange].has_implementation('ws_24hour_market_moves'):
                print('Loading active markets for ' + exchange)
                t = threading.Thread(target=self.trader[exchange].update_market_24hrs)
                t.start()
                t.join(5)

        self.refresh_agg_active_markets()

        return self._active_markets

    def get_currency_code(self, exchange, exchange_code):
        if exchange in self._map_exchange_code_to_currency_code:
            return self._map_exchange_code_to_currency_code[exchange].get(exchange_code, exchange_code)
        else:
            print('ERROR CryptoTrader get_currency_code on {} code: '.format(exchange, exchange_code))
            return None

    def get_market_symbol(self, exchange, code_base, code_curr):
        return self.trader[exchange].get_market_symbol(code_base, code_curr)

    def get_arbitrage_possibilities(self, required_rate_of_return):
        self.load_active_markets()
        self._arbitrage_possibilities = {}
        for code_base in self._active_markets:
            for code_curr in self._active_markets[code_base]:
                markets = self._active_markets[code_base][code_curr]
                best_bid = None
                best_ask = None
                if len(markets) > 1:
                    for exchange in markets:
                        if not markets[exchange]['BestBid'] is None:
                            if best_bid is None or best_bid < markets[exchange]['BestBid']:
                                best_bid = markets[exchange]['BestBid']
                        if not markets[exchange]['BestAsk'] is None:
                            if best_ask is None or best_ask > markets[exchange]['BestAsk']:
                                best_ask = markets[exchange]['BestAsk']
                    if best_bid is not None and best_ask is not None and best_bid > best_ask * required_rate_of_return:
                        if code_base not in self._arbitrage_possibilities:
                            self._arbitrage_possibilities[code_base] = {}
                        self._arbitrage_possibilities[code_base][code_curr] = markets
        return self._arbitrage_possibilities

    def get_arbitrage_possibilities_circle(self, required_rate_of_return):
        self.load_active_markets()
        self._arbitrage_possibilities = []
        for code_base1 in self._active_markets:
            for code_curr in self._active_markets[code_base1]:
                for code_base2 in self._active_markets:
                    if code_base1 != code_base2:
                        for exchange in self._active_markets[code_base1][code_curr]:
                            if code_curr in self._active_markets[code_base2]:
                                if exchange in self._active_markets[code_base2][code_curr]:
                                    if code_base2 in self._active_markets[code_base1]:
                                        if exchange in self._active_markets[code_base1][code_base2]:
                                            market1 = self._active_markets[code_base1][code_curr][exchange]
                                            market2 = self._active_markets[code_base2][code_curr][exchange]
                                            market3 = self._active_markets[code_base1][code_base2][exchange]
                                            if market3['BestAsk'] is not None and market2['BestAsk'] is not None and market1['BestBid'] is not None and market3['BestAsk'] * market2['BestAsk'] > 0 and market3['BestAsk'] * market2['BestAsk'] * required_rate_of_return < market1['BestBid']:
                                                self._arbitrage_possibilities.append(
                                                    {
                                                        'exchange': exchange,
                                                        'market1': market1,
                                                        'action1': 'sell',
                                                        'market2': market2,
                                                        'action2': 'buy',
                                                        'market3': market3,
                                                        'action3': 'buy',
                                                        'return': 100.0 * (market1['BestBid'] / (market3['BestAsk'] * market2['BestAsk']) - 1)
                                                    }
                                                )
                                            if market1['BestAsk'] is not None and market3['BestBid'] is not None and market2['BestBid'] is not None and market1['BestAsk'] > 0 and market3['BestBid'] * market2['BestBid'] > market1['BestAsk'] * required_rate_of_return:
                                                self._arbitrage_possibilities.append(
                                                    {
                                                        'exchange': exchange,
                                                        'market1': market1,
                                                        'action1': 'buy',
                                                        'market2': market2,
                                                        'action2': 'sell',
                                                        'market3': market3,
                                                        'action3': 'sell',
                                                        'return': 100.0 * (market3['BestBid'] * market2['BestBid'] / market1['BestAsk'] - 1)
                                                    }
                                                )

        return self._arbitrage_possibilities

    def calculate_balances_btc(self):
        """
            Load balances from exchanges in BTC terms
            Debug: self._CTMain._Crypto_Trader.calculate_balances_btc()
        """
        self._balances_btc = {}
        self.load_active_markets()
        for exchange in self._SETTINGS.get('Exchanges with API Keys', []):
            self.trader[exchange].load_balances_btc()
            for currency in self.trader[exchange]._complete_balances_btc:
                try:
                    if self.trader[exchange]._complete_balances_btc[currency]['Total'] > 0:
                        code = self.get_currency_code(exchange, currency)
                        if 'BtcValue' not in self.trader[exchange]._complete_balances_btc[currency]:
                            if code == 'BTC':
                                btc_rate = 1
                            else:
                                if code in ['USD', 'USDT']:
                                    btc_rate = 2.0 / (self._active_markets[code]['BTC'][exchange]['BestBid'] + self._active_markets[code]['BTC'][exchange]['BestAsk'])
                                else:
                                    if code in self._active_markets['BTC']:
                                        btc_rate = (self._active_markets['BTC'][code][exchange]['BestBid'] + self._active_markets['BTC'][code][exchange]['BestAsk']) / 2.0
                                    else:
                                        btc_rate = 0
                            self.trader[exchange]._complete_balances_btc[currency]['BtcValue'] = self.trader[exchange]._complete_balances_btc[currency]['Total'] * btc_rate
                        if code not in self._balances_btc:
                            self._balances_btc[code] = {
                                'TotalBtcValue': 0.0
                            }
                        self._balances_btc[code][exchange] = self.trader[exchange]._complete_balances_btc[currency]
                        self._balances_btc[code]['TotalBtcValue'] += self._balances_btc[code][exchange]['BtcValue']
                except Exception as e:
                    print("Error in load_balances_btc for currency " + currency + ": " + str(e))
        return self._balances_btc

    def calculate_balances_btc_totals(self, btc_usd_price=None):
        """
            Load total balances from exchanges
            Debug: self._CTMain._Crypto_Trader.calculate_balances_btc_totals()
        """
        results = {}
        self.calculate_balances_btc()
        for code in self._balances_btc:
            for exchange in self._balances_btc[code]:
                if exchange != 'TotalBtcValue':
                    if exchange not in results:
                        results[exchange] = {'BTC': 0.0}
                    results[exchange]['BTC'] += self._balances_btc[code][exchange]['BtcValue']

        if btc_usd_price is None:
            btc_usd_price = self.trader['Coinbase'].get_btc_usd_price()
        for exchange in results:
            results[exchange]['USD'] = results[exchange]['BTC'] * btc_usd_price
        return results
