import base64
import time
import hmac
import hashlib
import urllib
import requests
import pprint

from Exchange import Exchange

import ipdb

class Hotbit(Exchange):
    def __init__(self, APIKey='', Secret=''):
        super().__init__(APIKey, Secret)
        self.BASE_URL = 'https://api.hotbit.io/api'

    def get_request(self, url):
        try:
            result = requests.get(self.BASE_URL + url).json()
            return result
        except Exception as e:
            self.print_exception(self.BASE_URL + url + ". " + str(e))
            return self.get_request(url)

    # def trading_api_request(self, method, endpoint = '', **kwargs):
    #     """
    #         endpoint = '/v1/KCS-BTC/order',
    #         command = 'amount=10&price=1.1&type=BUY'

    #         "KC-API-KEY": "59c5ecfe18497f5394ded813",
    #         "KC-API-NONCE" : 1506219855000   //Client timestamp (exact to milliseconds), before using the calibration time, the server does not accept calls with a time difference of more than 3 seconds
    #         "KC-API-SIGNATURE" : "fd83147802c361575bbe72fef32ba90dcb364d388d05cb909c1a6e832f6ca3ac"   //signature after client encryption
    #     """
    #     try:
    #         nonce = str(int(time.time()*1000))
    #         request_url = self.BASE_URL + endpoint

    #         kwargs['timeout'] = 10
    #         kwargs['data'] = kwargs.get('data', {})

    #         query_string = self.order_params_for_sig(kwargs['data'])
    #         strForSign = ("{}/{}/{}".format(endpoint, nonce, query_string)).encode('utf-8')
    #         signature = hmac.new(self.Secret.encode('utf-8'), base64.b64encode(strForSign), hashlib.sha256).hexdigest()
    #         kwargs['headers'] = {
    #                                 "KC-API-KEY": self.APIKey,
    #                                 "KC-API-NONCE": nonce,
    #                                 "KC-API-SIGNATURE": signature
    #                             }
    #         if kwargs['data'] and method == 'get':
    #             kwargs['params'] = kwargs['data']
    #             del(kwargs['data'])

    #         results = getattr(requests,method)(request_url, **kwargs).json()
    #         if results.get('success', None) == True:
    #             return results['data']
    #         else:
    #             ipdb.set_trace()
    #             print('**** ERROR **** Kucoin trading_api_request:',results.get('success'))
    #             return self.trading_api_request(method,endpoint,req)

    #     except Exception as e:
    #         self.print_exception(str(e))
    #         return {}

    #################################
    ### Exchange specific methods ###
    #################################
    def get_markets(self):
        return requests.get('https://www.hotbit.io/public/markets').json()['Content']

    def get_open_trading_symbols(self):
        return self.get_request('/v1/allticker')['ticker']

    # def get_balances(self):
    #     return self.trading_api_request('get', '/v1/account/balance')

    # def get_latest_prices(self):
    #     url = "/api/v3/ticker/price"
    #     return self.get_request(url)

    def get_order_book(self, market, depth = '5'):
        url = "/v1/open/orders?symbol=" + market + "&limit=" + depth
        return self.get_request(url)

    # #######################
    # ### Generic methods ###
    # #######################
    def load_currencies(self):
        self._currencies = {}
        markets = self.get_markets()
        for market in markets:
            try:
                market_name = market['name']
                coins = market_name.split('/')
                self._currencies[coins[0]] = {
                    'Name': market['coin1Name'],
                    'Enabled': 1
                }
                self._currencies[coins[1]] = {
                    'Name': market['coin2Name'],
                    'Enabled': 1
                }
            except Exception as e:
                self.print_exception(str(e))

        return self._currencies

    def load_markets(self):
        self._markets = {}
        self._active_markets = {}
        open_trading_symbols = self.get_open_trading_symbols()

        for symbol in open_trading_symbols:
            try:
                market_symbol = symbol['symbol']
                local_base = market_symbol.split('_')[1]
                local_curr = market_symbol.split('_')[0]
                self.update_market( market_symbol,
                                    local_base,
                                    local_curr,
                                    float(symbol['buy']),
                                    float(symbol['sell'])
                                    )
            except Exception as e:
                self.print_exception(str(market_symbol) + ". " + str(e))
        return self._active_markets

    def load_available_balances(self):
        available_balances = self.get_balances()
        self._available_balances = {}
        for balance in available_balances:
            currency = balance['coinType']
            self._available_balances[currency] = balance["balance"]
        return self._available_balances

    def load_balances_btc(self):
        balances = self.get_balances()
        self._complete_balances_btc = {}
        for balance in balances:
            currency = balance['coinType']
            self._complete_balances_btc[currency] = {
                'Available': float(balance["balance"]),
                'OnOrders': float(balance["freezeBalance"]),
                'Total': float(balance["balance"]) + float(balance["freezeBalance"])
            }
        return self._complete_balances_btc

    def load_order_book(self, market, depth = 5):
        raw_results = self.get_order_book(market, str(depth))
        take_bid = min(depth, len(raw_results['BUY']))
        take_ask = min(depth, len(raw_results['SELL']))

        results = { 'Tradeable': 1, 'Bid': {}, 'Ask': {} }
        for i in range(take_bid):
            results['Bid'][i] = {
                'Price': float(raw_results['BUY'][i][0]),
                'Quantity': float(raw_results['BUY'][i][1]),
            }
        for i in range(take_ask):
            results['Ask'][i] = {
                'Price': float(raw_results['SELL'][i][0]),
                'Quantity': float(raw_results['SELL'][i][1]),
            }

        return results

    # def submit_trade(self, direction, market, price, amount, trade_type):
    #     if direction == 'buy':
    #         side = 'BUY'
    #     if direction == 'sell':
    #         side = 'SELL'

    #     request = {
    #             'amount': "{0:.8f}".format(amount),
    #             'price': "{0:.8f}".format(price),
    #             'symbol': market,
    #             'type': side
    #         }

    #     results = self.trading_api_request('post', '/v1/order', data = request)
    #     return {
    #             'Amount': amount,
    #             'OrderNumber': results['orderOid']
    #         }
