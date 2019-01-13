import base64
import time
import hmac
import hashlib
import urllib
import requests
import pprint

from Exchange import Exchange

class Kucoin(Exchange):
    def __init__(self, APIKey='', Secret=''):
        super().__init__(APIKey, Secret)
        self.BASE_URL = 'https://api.kucoin.com'
        self._exchangeInfo = None

    def get_request(self, url):
        try:
            result = requests.get(self.BASE_URL + url).json()
            if result.get('success', None) == True:
                return result['data']
            else:
                return self.get_request(url)
        except Exception as e:
            self.print_exception(self.BASE_URL + url + ". " + str(e))
            return self.get_request(url)

    def trading_api_request(self, method, endpoint = '', **kwargs):
        """
            endpoint = '/v1/KCS-BTC/order',
            command = 'amount=10&price=1.1&type=BUY'

            "KC-API-KEY": "59c5ecfe18497f5394ded813",
            "KC-API-NONCE" : 1506219855000   //Client timestamp (exact to milliseconds), before using the calibration time, the server does not accept calls with a time difference of more than 3 seconds
            "KC-API-SIGNATURE" : "fd83147802c361575bbe72fef32ba90dcb364d388d05cb909c1a6e832f6ca3ac"   //signature after client encryption
        """
        try:
            nonce = str(int(time.time()*1000))
            request_url = self.BASE_URL + endpoint

            kwargs['timeout'] = 10
            kwargs['data'] = kwargs.get('data', {})

            query_string = self.order_params_for_sig(kwargs['data'])
            strForSign = ("{}/{}/{}".format(endpoint, nonce, query_string)).encode('utf-8')
            signature = hmac.new(self.Secret.encode('utf-8'), base64.b64encode(strForSign), hashlib.sha256).hexdigest()
            kwargs['headers'] = {
                                    "KC-API-KEY": self.APIKey,
                                    "KC-API-NONCE": nonce,
                                    "KC-API-SIGNATURE": signature
                                }
            if kwargs['data'] and method == 'get':
                kwargs['params'] = kwargs['data']
                del(kwargs['data'])

            results = getattr(requests,method)(request_url, **kwargs).json()
            if results.get('success', None) == True:
                import ipdb
                ipdb.set_trace()
                return results['data']
            else:
                print('**** ERROR **** Kucoin trading_api_request:',results.get('success'))
                return self.trading_api_request(method,endpoint,req)

        except Exception as e:
            self.print_exception(str(e))
            return {}

    #################################
    ### Exchange specific methods ###
    #################################
    def get_coins(self):
        return self.get_request('/v1/market/open/coins')

    def get_open_trading_symbols(self):
        return self.get_request('/v1/market/open/symbols')

    def get_balances(self):
        return self.trading_api_request('get', '/v1/account/balance')

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
        coins = self.get_coins()
        for coin in coins:
            try:
                self._currencies[coin['coin']] = {
                    'Name': coin['name'],
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
                local_base = symbol['coinTypePair']
                local_curr = symbol['coinType']

                if 'buy' in symbol:
                    buy_price = float(symbol['buy'])
                else:
                    buy_price = 0.0

                if 'sell' in symbol:
                    sell_price = float(symbol['sell'])
                else:
                    sell_price = None

                self.update_market( market_symbol,
                                    local_base,
                                    local_curr,
                                    buy_price,
                                    sell_price,
                                    symbol['trading']
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

    def submit_trade(self, direction, market, price, amount, trade_type):
        if direction == 'buy':
            side = 'BUY'
        if direction == 'sell':
            side = 'SELL'

        request = {
                'amount': "{0:.8f}".format(amount),
                'price': "{0:.8f}".format(price),
                'symbol': market,
                'type': side
            }

        results = self.trading_api_request('post', '/v1/order', data = request)
        return {
                'Amount': amount,
                'OrderNumber': results['orderOid']
            }


    def get_deposits_and_withdrawals(self, coin, move_type):
        request = {
                'type': move_type,
                'status': 'FINISHED'
            }
        return self.trading_api_request('get', '/v1/account/' + coin + '/wallet/records', data = request)
