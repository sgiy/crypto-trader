import base64
import time
import hmac
import hashlib
import requests

from Exchange import Exchange

class Kucoin(Exchange):
    def __init__(self, APIKey='', Secret=''):
        super().__init__(APIKey, Secret)
        """
            https://kucoinapidocs.docs.apiary.io
        """
        self.BASE_URL = 'https://api.kucoin.com'
        self._exchangeInfo = None

    def get_request(self, url):
        try:
            result = requests.get(self.BASE_URL + url).json()
            if result.get('success', None) == True:
                self.log_request_success()
                return result['data']
            else:
                self.log_request_error(results['msg'])
                if self.retry_count_not_exceeded():
                    return self.get_request(url)
                else:
                    return {}
        except Exception as e:
            self.log_request_error(self.BASE_URL + url + ". " + str(e))
            if self.retry_count_not_exceeded():
                return self.get_request(url)
            else:
                return {}

    def trading_api_request(self, method, endpoint = '', req = {}):
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

            kwargs = {}
            kwargs['timeout'] = 10
            kwargs['data'] = req

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
                self.log_request_success()
                return results['data']
            else:
                self.log_request_error(results['msg'])
                if self.retry_count_not_exceeded():
                    return self.trading_api_request(method, endpoint, req)
                else:
                    return {}

        except Exception as e:
            self.log_request_error(request_url + ". " + str(e))
            if self.retry_count_not_exceeded():
                return self.trading_api_request(method, endpoint, req)
            else:
                return {}

    ########################################
    ### Exchange specific public methods ###
    ########################################

    def get_fiat_rates_of_coins(self):
        """
            Currencies Plugin / List exchange rate of coins(Open)
            Debug: ct['Kucoin'].get_fiat_rates_of_coins()
        """
        return self.get_request('/v1/open/currencies')

    def get_list_of_languages(self):
        """
            Language / List languages(Open)
            Debug: ct['Kucoin'].get_list_of_languages()
        """
        return self.get_request('/v1/open/lang-list')

    def get_tick(self, market = None):
        """
            Public Market Data / Tick(Open)
            Debug: ct['Kucoin'].get_tick('KCS-BTC')
        """
        url = '/v1/open/tick'
        if market is not None:
            url += '?symbol=' + market
        return self.get_request(url)

    def get_order_book(self, market, depth = '5', type = None):
        """
            Public Market Data / Order books(Open)
            Debug: ct['Kucoin'].get_order_book('KCS-BTC')
        """
        url = "/v1/open/orders?symbol={}&limit={}".format(market, depth)
        if type is not None:
            url += '?direction=' + type
        return self.get_request(url)

    def get_recent_trades(self, market, limit=10):
        """
            Public Market Data / Recently deal orders(Open)
            Debug: ct['Kucoin'].get_recent_trades('KCS-BTC')
        """
        url = "/v1/open/deal-orders?symbol={}&limit={}".format(market, limit)
        return self.get_request(url)

    def get_base_currencies(self):
        """
            Public Market Data / List trading markets(Open)
            Debug: ct['Kucoin'].get_base_currencies()
        """
        return self.get_request("/v1/open/markets")

    def get_open_trading_symbols(self):
        """
            Public Market Data / List trading symbols tick (Open)
            Debug: ct['Kucoin'].get_open_trading_symbols()
        """
        return self.get_request('/v1/market/open/symbols')

    # def get_candles_data(self, market, resolution, from, to):
    #     """
    #         Public Market Data / Get kline data(Open, TradingView Version)
    #         resolution: '1','5','15','30','60','480','D','W'
    #         Debug: ct['Kucoin'].get_candles_data('KCS-BTC', '15', 1507479171, 1507479171)
    #     """
    #     url = "/v1/open/chart/history?symbol={}&resolution={}&from={}&to={}".format(market, resolution, from, to)
    #     return self.get_request(url)

    def get_market_tick(self, market = None):
        """
            Public Market Data / Get symbol tick(Open, TradingView Version)
            Debug: ct['Kucoin'].get_market_tick('KCS-BTC')
        """
        url = "/v1/open/chart/symbols"
        if market is not None:
            url += '?symbol=' + market
        return self.get_request(url)

    # def get_latest_prices(self):
    #     url = "/api/v3/ticker/price"
    #     return self.get_request(url)

    def get_coins(self):
        return self.get_request('/v1/market/open/coins')





    ########################################
    ### Exchange specific private methods ##
    ########################################

    def set_default_fiat(self, currency):
        """
            Currencies Plugin / List exchange rate of coins(Open)
            Debug: ct['Kucoin'].set_default_fiat('USD')
        """
        return self.trading_api_request('post', '/v1/user/change-currency', {
            'currency': currency
        })

    def set_language(self, language):
        """
            Currencies Plugin / List exchange rate of coins(Open)
            Debug: ct['Kucoin'].set_language('English')
        """
        return self.trading_api_request('post', '/v1/user/change-lang', {
            'lang': language
        })

    def get_user_info(self):
        """
            User / Get user info
            Debug: ct['Kucoin'].get_user_info()
        """
        return self.trading_api_request('get', '/v1/user/info')

    def get_coin_deposit_address(self, coin):
        """
            Assets Operation / Get coin deposit address
            Debug: ct['Kucoin'].get_coin_deposit_address('BTC')
        """
        return self.trading_api_request('get', '/v1/account/{}/wallet/address'.format(coin))

    def withdraw(self, coin, amount, address):
        """
            Assets Operation / Create withdrawal apply
            Debug: ct['Kucoin'].withdraw('BTC', 1, '1234567891011tHeReGuLaRsIzEaDdRess')
        """
        return self.trading_api_request('post', '/v1/account/{}/withdraw/apply'.format(coin), {
            'coin': coin,
            'amount': '{.8f}'.format(amount),
            'address': address
        })

    def cancel_withdrawal(self, coin, txOid):
        """
            Assets Operation / Cancel withdrawal
            Debug: ct['Kucoin'].cancel_withdrawal('BTC', 'tx0123456789')
        """
        return self.trading_api_request('post', '/v1/account/{}/withdraw/apply'.format(coin), {
            'coin': coin,
            'txOid': txOid
        })

    def get_deposits_and_withdrawals(self, coin, move_type, status = 'FINISHED', page = None):
        """
            Assets Operation / List deposit & withdrawal records
            type: DEPOSIT,WITHDRAW
            status: FINISHED,CANCEL,PENDING
            page: number
            Debug: ct['Kucoin'].get_deposits_and_withdrawals('BTC', 'DEPOSIT')
        """
        request = {
                'type': move_type,
                'status': status
            }
        if page is not None:
            request['page'] = page
        return self.trading_api_request('get', '/v1/account/{}/wallet/records'.format(coin), request)

    def get_balance_of_coin(self, coin):
        """
            Assets Operation / Get balance of coin
            Debug: ct['Kucoin'].get_balance_of_coin('BTC')
        """
        return self.trading_api_request('get', '/v1/account/{}/balance'.format(coin))

    def get_balances(self):
        return self.trading_api_request('get', '/v1/account/balance')

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

    def get_active_orders(self, market, type = None):
        """
            Trading / List active orders in kv format
            Debug: ct['Kucoin'].get_active_orders('KCS-BTC')
        """
        request = {
            'symbol': market
        }
        if type is not None:
            request['type'] = type
        return self.trading_api_request('get', '/v1/order/active-map', request)

    def cancel_order(self, market, orderId, type):
        """
            Trading / Cancel orders
            type: BUY,SELL
            Debug: ct['Kucoin'].cancel_order('KCS-BTC', '5969ddc96732d54312eb960e', 'BUY')
        """
        return self.trading_api_request('get', '/v1/cancel-order?symbol=' + market, {
            'orderOid': orderId,
            'type': type
        })

    def cancel_all_orders_per_market(self, market, type = None):
        """
            Trading / Cancel all orders
            Debug: ct['Kucoin'].cancel_all_orders_per_market('KCS-BTC')
        """
        request = {}
        if type is not None:
            request['type'] = type
        return self.trading_api_request('get', '/v1/cancel-all?symbol=' + market, request)

    def get_order_history_merged(self, market = None, type = None, limit = None,
            page = None, since = None, before = None):
        """
            Trading / List dealt orders(merged)
            Debug: ct['Kucoin'].get_order_history_merged('KCS-BTC')
        """
        request = {}
        if market is not None:
            request['symbol'] = market
        if type is not None:
            request['type'] = type
        if limit is not None:
            request['limit'] = limit
        if page is not None:
            request['page'] = page
        if since is not None:
            request['since'] = since
        if before is not None:
            request['before'] = before
        return self.trading_api_request('get', '/v1/order/dealt', request)

    def get_order_history_per_market(self, market, type = None, limit = None, page = None):
        """
            Trading / List dealt orders(specific symbol)
            Debug: ct['Kucoin'].get_order_history_per_market('KCS-BTC')
        """
        request = {
            'symbol': market
        }
        if type is not None:
            request['type'] = type
        if limit is not None:
            request['limit'] = limit
        if page is not None:
            request['page'] = page
        return self.trading_api_request('get', '/v1/deal-orders', request)

    def get_all_orders(self, market, type, active = False,
            limit = None, page = None, since = None, before = None):
        """
            Trading / List all orders
            type: BUY,SELL
            Debug: ct['Kucoin'].get_all_orders('KCS-BTC', 'BUY')
        """
        request = {
            'symbol': market,
            'direction': type,
            'active': active
        }
        if limit is not None:
            request['limit'] = limit
        if page is not None:
            request['page'] = page
        if since is not None:
            request['since'] = since
        if before is not None:
            request['before'] = before
        return self.trading_api_request('get', '/v1/orders', request)

    def get_order_detail(self, market, type, orderId, limit = None, page = None):
        """
            Trading / Order details
            Debug: ct['Kucoin'].get_order_detail('KCS-BTC', 'BUY', '5969ddc96732d54312eb960e')
        """
        request = {
            'symbol': market,
            'type': type,
            'orderOid': orderId
        }
        if limit is not None:
            request['limit'] = limit
        if page is not None:
            request['page'] = page
        return self.trading_api_request('get', '/v1/order/detail', request)

    # #######################
    # ### Generic methods ###
    # #######################
    def load_currencies(self):
        """
            Loading currencies
            Debug: ct['Kucoin'].load_currencies()
        """
        self._currencies = {}
        coins = self.get_coins()
        for coin in coins:
            try:
                enabled = 0
                if coin.get('enable',False):
                    enabled = 1
                self._currencies[coin['coin']] = {
                    'Name': coin['name'],
                    'Enabled': enabled
                }
            except Exception as e:
                self.log_request_error(str(e))

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
                self.log_request_error(str(market_symbol) + ". " + str(e))
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
