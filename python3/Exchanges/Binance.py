import time
import hmac
import hashlib
import urllib
import requests
import pprint

from Exchange import Exchange

import ipdb

class Binance(Exchange):
    def __init__(self, APIKey='', Secret=''):
        super().__init__(APIKey, Secret)
        self.BASE_URL = 'https://api.binance.com'
        self._exchangeInfo = None
        self._tick_intervals = {
            '1m':   1,
            '3m':   3,
            '5m':   5,
            '15m':  15,
            '30m':  30,
            '1h':   60,
            '2h':   2*60,
            '4h':   4*60,
            '6h':   6*60,
            '8h':   8*60,
            '12h':  12*60,
            '1d':   24*60,
            '3d':   3*24*60,
            '1w':   7*24*60,
            '1M':   30*24*60
        }

    def get_request(self, url):
        try:
            return requests.get(self.BASE_URL + url).json()
        except Exception as e:
            print('ERROR getting URL: ',self.BASE_URL + url)
            return self.get_request(url)

    def trading_api_request(self, method, url, req={}):
        try:
            req['timestamp'] = int(time.time()*1000)
            query_string = '&'.join(["{}={}".format(k, v) for k, v in req.items()])
            signature = hmac.new(self.Secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()
            query_string = query_string + '&signature=' + signature

            headers = { 'X-MBX-APIKEY': self.APIKey }

            req_url = self.BASE_URL + url + '?' + query_string
            results = getattr(requests,method)(req_url, headers = headers).json()
            return results
        except Exception as e:
            print('ERROR Binance trading_api_request',str(e))
            return {}

    #################################
    ### Exchange specific methods ###
    #################################
    def load_exchangeInfo(self):
        self._exchangeInfo = self.get_request('/api/v1/exchangeInfo')
        return self._exchangeInfo

    def get_book_ticker(self, market = ""):
        url = "/api/v3/ticker/bookTicker"
        if market != "":
            url += "?symbol=" + market
        return self.get_request(url)

    def get_formatted_best_books(self):
        book_ticker = self.get_book_ticker()
        results = {}
        for ticker in book_ticker:
            results[ticker["symbol"]] = {
                "Bid": ticker["bidPrice"],
                "BidQty": ticker["bidQty"],
                "Ask": ticker["askPrice"],
                "AskQty": ticker["askQty"]
            }
        return results

    def get_balances(self):
        balances = self.trading_api_request('get', '/api/v3/account')
        return balances['balances']

    def get_latest_prices(self):
        url = "/api/v3/ticker/price"
        return self.get_request(url)

    def get_order_book(self, market, depth = '5'):
        url = "/api/v1/depth?symbol=" + market + "&limit=" + depth
        return self.get_request(url)

    def get_ticks(self, market, interval = '5m'):
        return self.get_request('/api/v1/klines?symbol=' + market + '&interval=' + interval)

    #######################
    ### Generic methods ###
    #######################
    def load_currencies(self):
        self._currencies = {}
        self.load_exchangeInfo()
        for symbol in self._exchangeInfo['symbols']:
            try:
                if symbol['status'] == 'TRADING':
                    enabled = 1
                else:
                    enabled = 0

                self._currencies[symbol['baseAsset']] = {
                    'Name': symbol['baseAsset'],
                    'Enabled': enabled
                }

                if not symbol['quoteAsset'] in self._currencies:
                    self._currencies[symbol['quoteAsset']] = {
                        'Name': symbol['quoteAsset'],
                        'Enabled': 1
                    }
            except Exception as e:
                self.print_exception(str(e))

        return self._currencies

    def load_markets(self):
        self._markets = {}
        self._active_markets = {}
        best_books = self.get_formatted_best_books()

        for symbol in self._exchangeInfo['symbols']:
            try:
                market_symbol = symbol['symbol']
                local_base = symbol['quoteAsset']
                local_curr = symbol['baseAsset']

                self.update_market( market_symbol,
                                    local_base,
                                    local_curr,
                                    float(best_books[market_symbol]['Bid']),
                                    float(best_books[market_symbol]['Ask']),
                                    symbol['status'] == 'TRADING',
                                    float(best_books[market_symbol]['BidQty']),
                                    float(best_books[market_symbol]['AskQty'])
                                    )
            except Exception as e:
                self.print_exception(str(market_symbol) + ". " + str(e))
        return self._active_markets

    def load_ticks(self, market_name, interval = '5m', lookback = None):
        load_chart = self.get_ticks(market_name, interval)
        """
            https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md
            [
              [
                1499040000000,      // Open time
                "0.01634790",       // Open
                "0.80000000",       // High
                "0.01575800",       // Low
                "0.01577100",       // Close
                "148976.11427815",  // Volume
                1499644799999,      // Close time
                "2434.19055334",    // Quote asset volume
                308,                // Number of trades
                "1756.87402397",    // Taker buy base asset volume
                "28.46694368",      // Taker buy quote asset volume
                "17928899.62484339" // Ignore.
              ]
            ]
        """

        times = []
        opens = []
        closes = []
        highs = []
        lows = []
        volumes = []
        baseVolumes = []
        for i in load_chart:
            times.append(i[0])
            opens.append(i[1])
            closes.append(i[4])
            highs.append(i[2])
            lows.append(i[3])
            volumes.append(i[5])
            baseVolumes.append(i[7])
        return {
            'times': times,
            'opens': opens,
            'closes': closes,
            'highs': highs,
            'lows': lows,
            'volumes': volumes,
            'baseVolumes': baseVolumes
        }

    def load_available_balances(self):
        available_balances = self.get_balances()
        self._available_balances = {}
        for balance in available_balances:
            currency = balance['asset']
            self._available_balances[currency] = float(balance["free"])
        return self._available_balances

    def load_balances_btc(self):
        balances = self.get_balances()
        self._complete_balances_btc = {}
        for balance in balances:
            currency = balance['asset']
            self._complete_balances_btc[currency] = {
                'Available': float(balance["free"]),
                'OnOrders': float(balance["locked"]),
                'Total': float(balance["free"]) + float(balance["locked"])
            }
        return self._complete_balances_btc

    def load_order_book(self, market):
        raw_results = self.get_order_book(market,'5')
        take_bid = min(5, len(raw_results['bids']))
        take_ask = min(5, len(raw_results['asks']))

        results = { 'Tradeable': 1, 'Bid': {}, 'Ask': {} }
        for i in range(take_bid):
            results['Bid'][i] = {
                'Price': float(raw_results['bids'][i][0]),
                'Quantity': float(raw_results['bids'][i][1]),
            }
        for i in range(take_ask):
            results['Ask'][i] = {
                'Price': float(raw_results['asks'][i][0]),
                'Quantity': float(raw_results['asks'][i][1]),
            }

        return results

    def submit_trade(self, direction, market, price, amount, trade_type):
        if direction == 'buy':
            side = 'BUY'
        if direction == 'sell':
            side = 'SELL'

        timeInForce = 'GTC'
        if trade_type == 'ImmediateOrCancel':
            timeInForce = 'IOC'

        request = {
                'symbol': market,
                'side': side,
                'type': 'LIMIT',
                'timeInForce': timeInForce,
                'quantity': "{0:.8f}".format(amount),
                'price': "{0:.8f}".format(price),
                'newOrderRespType': 'RESULT'
            }

        results = self.trading_api_request('post', '/api/v3/order', request)
        return {
                'Amount': float(results['executedQty']),
                'OrderNumber': results['clientOrderId']
            }
