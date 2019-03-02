import base64
import time
import hmac
import hashlib
import requests
import uuid
import json

from Exchange import Exchange

class Kucoin(Exchange):
    def __init__(self, APIKey='', Secret='', PassPhrase=''):
        super().__init__(APIKey, Secret, PassPhrase)
        """
            For API details see https://docs.kucoin.com/
        """
        self._BASE_URL = 'https://openapi-v2.kucoin.com'
        self._exchangeInfo = None

    def get_request(self, url):
        try:
            result = requests.get(self._BASE_URL + url).json()
            if result.get('code', None) == '200000':
                return result['data']
            else:
                print(self._BASE_URL + url + ". " + str(result.get('msg')))
                #return self.get_request(url)
        except Exception as e:
            print(self._BASE_URL + url + ". " + str(e))
            #return self.get_request(url)

    def trading_api_sign(self, method, endpoint, body, nonce):
        """
            curl -H "Content-Type:application/json"
                 -H "KC-API-KEY:5c2db93503aa674c74a31734"
                 -H "KC-API-TIMESTAMP:1547015186532"
                 -H "KC-API-PASSPHRASE:Abc123456"
                 -H "KC-API-SIGN:7QP/oM0ykidMdrfNEUmng8eZjg/ZvPafjIqmxiVfYu4="
                 -X POST -d '{"currency":"BTC"}' http://openapi-v2.kucoin.com/api/v1/deposit-addresses

            KC-API-KEY = 5c2db93503aa674c74a31734
            KC-API-SECRET = f03a5284-5c39-4aaa-9b20-dea10bdcf8e3
            KC-API-PASSPHRASE = Abc123456
            TIMESTAMP = 1547015186532
            METHOD = POST
            ENDPOINT = /api/v1/deposit-addresses
            STRING-TO-SIGN = 1547015186532POST/api/v1/deposit-addresses{"currency":"BTC"}
            KC-API-SIGN = 7QP/oM0ykidMdrfNEUmng8eZjg/ZvPafjIqmxiVfYu4=
        """
        strForSign = nonce + method.upper() + endpoint + body
        return base64.b64encode(hmac.new(self._API_SECRET.encode(), strForSign.encode(), hashlib.sha256).digest()).decode()

    def trading_api_request(self, method, endpoint, body={}):
        """
            endpoint = '/v1/KCS-BTC/order',
            command = 'amount=10&price=1.1&type=BUY'

            "KC-API-KEY":           "5c2db93503aa674c74a31734" //The api key as a string.
            "KC-API-SIGN":          "f03a5284-5c39-4aaa-9b20-dea10bdcf8e3" //The base64-encoded signature (see Signing a Message).
            "KC-API-TIMESTAMP":     1547015186532   //A timestamp for your request.
            "KC-API-PASSPHRASE":    "Abc123456"   //The passphrase you specified when creating the API key.
        """
        try:
            nonce = str(int(time.time()*1000))
            request_url = self._BASE_URL + endpoint

            body_str = ''
            if any(body):
                body_str = json.dumps(body, sort_keys=True, separators=(',',':'))

            signature = self.trading_api_sign(method, endpoint, body_str, nonce)

            request = {}
            if method == 'get':
                request['params'] = body
            else:
                request['data'] = body_str
            request['headers'] =   {
                                        'Content-Type': 'application/json',
                                        "KC-API-KEY": self._API_KEY,
                                        "KC-API-TIMESTAMP": nonce,
                                        "KC-API-PASSPHRASE": self._API_PASSPHRASE,
                                        "KC-API-SIGN": signature
                                    }
            result = getattr(requests,method)(request_url, **request).json()

            if result.get('code', None) == '200000':
                return result['data']
            else:
                print(request_url + ". " + str(result))
                #return self.trading_api_request(method,endpoint,body)

        except Exception as e:
            print(str(e))
            return {}

    ########################################
    ### Exchange specific public methods ###
    ########################################

    def get_market_list(self):
        """
            Get base currencies.
            GET /api/v1/markets
            ct['Kucoin'].get_market_list()
            [
                "BTC",
                "ETH",
                "USDT"
            ]
        """
        return self.get_request('/api/v1/markets')

    def get_symbols(self):
        """
            Get a list of available currency pairs for trading.
            GET /api/v1/symbols
            [{'quoteCurrency': 'BTC',
              'symbol': 'KCS-BTC',
              'quoteMaxSize': '9999999',
              'quoteIncrement': '0.000001',
              'baseMinSize': '0.01',
              'quoteMinSize': '0.00001',
              'enableTrading': True,
              'priceIncrement': '0.00000001',
              'name': 'KCS-BTC',
              'baseIncrement': '0.01',
              'baseMaxSize': '9999999',
              'baseCurrency': 'KCS'},
             {'quoteCurrency': 'BTC',
              'symbol': 'ETH-BTC',
              'quoteMaxSize': '9999999',
              'quoteIncrement': '0.000001',
              'baseMinSize': '0.0001',
              'quoteMinSize': '0.00001',
              'enableTrading': True,
              'priceIncrement': '0.000001',
              'name': 'ETH-BTC',
              'baseIncrement': '0.0001',
              'baseMaxSize': '1000000000',
              'baseCurrency': 'ETH'}]
        """
        return self.get_request('/api/v1/symbols')

    def get_ticker(self, symbol):
        """
            Ticker include only the inside (i.e. best) bid and ask data , last
            price and last trade size.
            GET /api/v1/market/orderbook/level1?symbol=<symbol>
            {'sequence': '1547728715485',
             'bestAsk': '0.00013',
             'size': '0.351',
             'price': '0.00012',
             'bestBidSize': '2.77587',
             'bestBid': '0.00012',
             'bestAskSize': '2.05255'}
        """
        return self.get_request('/api/v1/market/orderbook/level1?symbol=' + symbol)

    def get_part_order_book_agg(self, symbol):
        """
            Get a list of open orders for a symbol.
            Level-2 order book includes all bids and asks (aggregated by price),
            this level return only one size for each active price (as if there
            was only a single order for that size at the level). This API will
            return a part of Order Book within 100 depth for each side(ask or bid).
            It is recommended to use in most cases, it is the fastest Order
            Book API, and reduces traffic usage.
            GET /api/v1/market/orderbook/level2_100?symbol=<symbol>
            {'sequence': '1547728715649',
             'asks': [['0.000129', '0.01'],
              ['0.00013', '1.96012'],
              ['0.00014', '23.92009'],
              ['0.000141', '0.01'],
              ['0.000143', '0.01'],
              ['0.5', '0.98608393'],
              ['0.9', '0.12']],
             'bids': [['0.00012', '0.30662'],
              ['0.00011', '18.95473'],
              ['0.000107', '0.00999'],
              ['0.000106', '0.00999']]}
        """
        return self.get_request('/api/v1/market/orderbook/level2_100?symbol=' + symbol)

    def get_full_order_book_agg(self, symbol):
        """
            Get a list of open orders for a symbol.
            Level-2 order book includes all bids and asks (aggregated by price),
            this level return only one size for each active price (as if there
            was only a single order for that size at the level). This API will
            return data with full depth. It is generally used by professional
            traders because it uses more server resources and traffic, and we
            have strict access frequency control.
            GET /api/v1/market/orderbook/level2?symbol=<symbol>
            {'sequence': '1547728716185',
             'asks': [['0.9', '0.12'],
              ['0.5', '0.98608393'],
              ['0.000144', '0.01'],
              ['0.000143', '0.01'],
              ['0.000141', '0.01'],
              ['0.00014', '23.52082'],
              ['0.00013', '0.69795'],
              ['0.00012', '0.47062']],
             'bids': [['0.00011', '16.60746'], ['0.000107', '0.00999']]}
        """
        return self.get_request('/api/v1/market/orderbook/level2?symbol=' + symbol)

    def get_full_order_book_atomic(self, symbol):
        """
            Get a list of open orders for a symbol. Level-3 order book includes
            all bids and asks (non-aggregated, each item in Level-3 means a
            single order). Level 3 is non-aggregated and returns the entire
            order book. This API is generally used by professional traders
            because it uses more server resources and traffic, and we have
            strict access frequency control.
            GET /api/v1/market/orderbook/level3?symbol=<symbol>
            {'sequence': '1547728716310',
             'asks': [['5c419328ef83c75456bd615c', '0.9', '0.09'],
              ['5c419938ef83c75456bda415', '0.9', '0.03'],
              ['5c429820ef83c766e41096f0', '0.5', '0.98608393'],
              ...
              ['5c436fdfef83c766e43071a8', '0.00014', '0.58'],
              ['5c436fe1ef83c766e430722b', '0.00013', '0.15015'],
              ['5c436fe5ef83c766e43072a0', '0.00013', '0.88']],
             'bids': [['5c436fe8ef83c766e4307302', '0.00012', '0.37962'],
              ['5c436fe7ef83c766e43072d4', '0.00011', '0.00999'],
              ['5c436fe5ef83c766e4307298', '0.00012', '0.85914'],
              ...
              ['5c436c8bef83c766e4300479', '0.00011', '0.05994'],
              ['5c436c7cef83c766e43002be', '0.00011', '0.3837'],
              ['5c43275fef83c766e42729cf', '0.000107', '0.00999']]}
        """
        return self.get_request('/api/v1/market/orderbook/level3?symbol=' + symbol)

    def get_trade_histories(self, symbol):
        """
            List the latest trades for a symbol.
            GET /api/v1/market/histories?symbol=<symbol>
            [{'sequence': '1547728716599',
              'side': 'sell',
              'size': '0.10327',
              'price': '0.00012',
              'time': 1547923496182500913},
             {'sequence': '1547728716606',
              'side': 'buy',
              'size': '0.26145',
              'price': '0.00013',
              'time': 1547923497366885430},
             {'sequence': '1547728716608',
              'side': 'buy',
              'size': '0.24',
              'price': '0.00013',
              'time': 1547923497366885430},
             {'sequence': '1547728716610',
              'side': 'buy',
              'size': '0.04',
              'price': '0.00013',
              'time': 1547923497366885430},
             {'sequence': '1547728716612',
              'side': 'buy',
              'size': '0.33767',
              'price': '0.00013',
              'time': 1547923497366885430}]]
        """
        return self.get_request('/api/v1/market/histories?symbol=' + symbol)

    def get_historic_rates(self, symbol, startAt, endAt, pattern_type='5min'):
        """
            Historic rates for a symbol. Rates are returned in grouped buckets
            based on requested type.

            startAt  - Start time, unix timestamp calculated in seconds not millisecond
            endAt    - End time, unix timestamp calculated in seconds not millisecond
            type     - Type of candlestick patterns
            DETAILS
            For each query, the system would return at most 1500 pieces of data.
            To obtain more data, please page the data by time.

            The type field must be one of the following values: {"1min","3min",
                "5min","15min","30min","1hour","2hour","4hour","6hour","8hour",
                "12hour", "1day","1week"}.

            The json data format is as shown below.

            [
              [
                  "1545904980",             //Start time of the candle cycle
                  "0.058",                  //opening price
                  "0.049",                  //closing price
                  "0.058",                  //highest price
                  "0.049",                  //lowest price
                  "0.018",                  //Transaction amount
                  "0.000945"                //Transaction volume
              ],
              [
                  "1545904920",
                  "0.058",
                  "0.072",
                  "0.072",
                  "0.058",
                  "0.103",
                  "0.006986"
              ]
            ]
            RESPONSE ITEMS
            Each bucket is an array of the following information:

            time bucket start time
            open opening price (first trade) in the bucket interval
            close closing price (last trade) in the bucket interval
            high highest price during the bucket interval
            low lowest price during the bucket interval
            volume volume of trading activity during the bucket interval
            turnover Turnover of a period of time. The turnover is the sum of
            the transaction volumes of all orders
            (Turnover of each order=price*quantity).
            GET /api/v1/market/candles?symbol=<symbol>

        """
        return self.get_request('/api/v1/market/candles?symbol={0}&begin={1}&end={2}&type={3}'.format(symbol, startAt, endAt, pattern_type))

    def get_24hr_stats(self, symbol):
        """
            Get 24 hr stats for the symbol. volume is in base currency units.
            open, high, low are in quote currency units.
            GET /api/v1/market/stats
            {'symbol': 'KCS-BTC',
             'high': '0.5',
             'vol': '23207.79102607',
             'low': '0.00009',
             'changePrice': '-0.00001',
             'changeRate': '-0.0769',
             'volValue': '2.95767623942'}
        """
        return self.get_request('/api/v1/market/stats/' + symbol)

    def get_currencies(self):
        """
            List known currencies.
            GET /api/v1/currencies
            [{'precision': 8, 'name': 'BTC', 'fullName': 'Bitcoin', 'currency': 'BTC'},
             {'precision': 8, 'name': 'ETH', 'fullName': 'Ethereum', 'currency': 'ETH'},
             {'precision': 10, 'name': 'KCS', 'fullName': 'KCS shares', 'currency': 'KCS'},
             {'precision': 8, 'name': 'USDT', 'fullName': 'USDT', 'currency': 'USDT'}]
        """
        return self.get_request('/api/v1/currencies')

    def get_currency_detail(self, currency):
        """
            Get single currency detail
            GET /api/v1/currencies/{currency}
            {'withdrawalMinFee': '0.001',
             'precision': 10,
             'name': 'KCS',
             'fullName': 'KCS shares',
             'currency': 'KCS',
             'withdrawalMinSize': '0.001',
             'isWithdrawEnabled': False,
             'isDepositEnabled': False}
        """
        return self.get_request('/api/v1/currencies/' + currency)

    def get_time(self):
        """
            Get the API server time.
            GET /api/v1/timestamp
            1547924920579
        """
        return self.get_request('/api/v1/timestamp')

    def get_all_tickers(self):
        """
            Get all tickers
            Debug: ct['Kucoin'].get_all_tickers()
        """
        return self.get_request('/api/v1/market/allTickers')

    #########################################
    ### Exchange specific private methods ###
    #########################################

    def get_accounts(self, currency = None, account_type = None):
        """
            Get a list of accounts.
            GET /api/v1/accounts?currency=<currency>&type=<type>
            [{'balance': '0.1',
              'available': '0.1',
              'holds': '0',
              'currency': 'BTC',
              'id': '5c435fc9ef83c7101c96f216',
              'type': 'main'},
             {'balance': '500',
              'available': '500',
              'holds': '0',
              'currency': 'KCS',
              'id': '5c435fcaef83c7101c96f261',
              'type': 'main'},
             {'balance': '1',
              'available': '1',
              'holds': '0',
              'currency': 'ETH',
              'id': '5c435fc9ef83c7101c96f215',
              'type': 'main'}]
        """
        request = ''
        if currency is not None:
            request += 'currency=' + currency
        if account_type is not None:
            request += 'type=' + account_type
        if request != '':
            request = '?' + request
        return self.trading_api_request('get', '/api/v1/accounts' + request)

    def get_account(self, accountId):
        """
            Information for a single account. Use this endpoint when you know the accountId.
            GET /api/v1/accounts/<accountId>
            {'balance': '0.1',
             'available': '0.1',
             'holds': '0',
             'currency': 'BTC'}
        """
        return self.trading_api_request('get', '/api/v1/accounts/' + accountId)

    def create_account(self, account_type, currency):
        """
            Create an Account.
            POST /api/v1/accounts
            'Internal Server Error!'
        """
        return self.trading_api_request('post', '/api/v1/accounts', {
                    'type': account_type,
                    'currency': currency
                })

    def get_account_history(self, accountId, startAt, endAt, pageSize= 100, currentPage = 1):
        """
            List account activity. Account activity either increases or decreases
            your account balance. Items are paginated and sorted latest first.
            See the Pagination section for retrieving additional entries after the first page.
            GET /api/v1/accounts/<accountId>/ledgers
            {'totalNum': 1,
             'totalPage': 1,
             'pageSize': 100,
             'currentPage': 1,
             'items': [{'createdAt': 1547919305000,
                       'amount': '0.1',
                       'bizType': 'Deposit',
                       'balance': '0.1',
                       'fee': '0',
                       'context': '',
                       'currency': 'BTC',
                       'direction': 'in'}]}
        """
        return self.trading_api_request('get',
                                        '/api/v1/accounts/{}/ledgers?startAt={}&endAt={}&pageSize={}&currentPage={}'.format(
                                                accountId, startAt, endAt, pageSize, currentPage
                                            ))

    def get_account_holds(self, accountId):
        """
            Holds are placed on an account for any active orders or pending
            withdraw requests. As an order is filled, the hold amount is updated.
            If an order is canceled, any remaining hold is removed. For a withdraw,
            once it is completed, the hold is removed.
            GET /api/v1/accounts/<accountId>/holds
        """
        return self.trading_api_request('get', '/api/v1/accounts/' + accountId + '/holds')

    def post_inner_transfer(self, clientOid, payAccountId, recAccountId, amount):
        """
            The inner transfer interface is used for assets transfer among the
            accounts of a user and is free of charges on the platform. For example,
            a user could transfer assets for free form the main account to the
            trading account on the platform.
            POST /api/v1/accounts/inner-transfer
        """
        return self.trading_api_request('post', '/api/v1/accounts/inner-transfer', {
                    'clientOid': clientOid,
                    'payAccountId': payAccountId,
                    'recAccountId': recAccountId,
                    'amount': amount,
                })

    def post_new_order(self, side, symbol, price, size, timeInForce, order_type = 'limit'):
        """
            You can place two types of orders: limit and market. Orders can only
            be placed if your account has sufficient funds. Once an order is placed,
            your account funds will be put on hold for the duration of the order.
            How much and which funds are put on hold depends on the order type
            and parameters specified. See the Holds details below. The maximum
            matching orders for a single trading pair in one account is 50
            (stop limit order included).
            POST /api/v1/orders
            Param	type	Description
            clientOid	string	Unique order id selected by you to identify your order e.g. UUID
            type	string	[optional] limit or market (default is limit)
            side	string	buy or sell
            symbol	string	a valid trading symbol code. e.g. ETH-BTC
            remark	string	[optional] remark for the order, length cannot exceed 100 utf8 characters
            stop	string	[optional] Either loss or entry. Requires stopPrice to be defined
            stopPrice	string	[optional] Only if stop is defined. Sets trigger price for stop order
            stp	string	[optional] self trade protect , CN, CO, CB or DC
            LIMIT ORDER PARAMETERS
            Param	type	Description
            price	string	price per base currency
            size	string	amount of base currency to buy or sell
            timeInForce	string	[optional] GTC, GTT, IOC, or FOK (default is GTC)
            cancelAfter	long	[optional] * cancel after n seconds
            postOnly	boolean	[optional] ** Post only flag
            * Requires timeInForce to be GTT
            ** Invalid when timeInForce is GTC, IOC or FOK
            MARKET ORDER PARAMETERS
            Param	type	Description
            size	string	[optional] Desired amount in base currency
            funds	string	[optional] Desired amount of quote currency to use
        """
        clientOid = str(uuid.uuid4())
        request = {
                    'clientOid': clientOid,
                    'type': order_type,
                    'side': side,
                    'symbol': symbol,
                }
        if price is not None:
            request['price'] = price
        if size is not None:
            request['size'] = size
        if timeInForce is not None:
            request['timeInForce'] = timeInForce
        return self.trading_api_request('post', '/api/v1/orders', request)

    #######################
    ### Generic methods ###
    #######################
    def get_formatted_currencies(self):
        """
            Loading currencies
            Debug: ct['Kucoin'].get_formatted_currencies()
            Example:
                {
                    'BTC': {
                                'Name': 'Bitcoin',
                                'DepositEnabled': True,
                                'WithdrawalEnabled': True,
                                'Notice': '',
                                'ExchangeBaseAddress': 'address',
                                'MinConfirmation': 2,
                                'WithdrawalFee': 0.001,
                                'WithdrawalMinAmount': 0.001,
                                'Precision': 0.00000001
                            },
                    ...
                }
        """
        currencies = self.get_currencies()
        results = {}
        if isinstance(currencies, list):
            for currency in currencies:
                try:
                    results[currency['currency']] = {
                        'Name': currency['fullName'],
                        'DepositEnabled': currency['isDepositEnabled'],
                        'WithdrawalEnabled': currency['isWithdrawEnabled'],
                        'Notice': '',
                        'ExchangeBaseAddress': '',
                        'MinConfirmation': 0,
                        'WithdrawalFee': float(currency.get('withdrawalMinFee', 0)),
                        'WithdrawalMinAmount': float(currency.get('withdrawalMinSize', 0)),
                        'Precision': pow(10,-currency['precision'])
                    }
                except Exception as e:
                    self.log_request_error(str(e))

        return results




    def load_markets(self):
        self._markets = {}
        self._active_markets = {}
        all_markets = self.get_all_tickers()['ticker']

        for market in all_markets:
            try:
                symbol = market['symbol']
                local_curr = symbol[0:symbol.find('-')]
                local_base = symbol[symbol.find('-')+1:]

                self.update_market(
                    symbol,
                    local_base,
                    local_curr,
                    float(market['buy']),
                    float(market['sell'])
                )
            except Exception as e:
                self.log_request_error(str(market) + ". " + str(e))
        return self._active_markets

    def load_ticks(self, market_name, interval = 'fiveMin', lookback = None):
        pass

    def load_available_balances(self):
        """
            ct['Kucoin'].load_available_balances()
        """
        available_balances = self.get_accounts()
        self._available_balances = {}
        for balance in available_balances:
            currency = balance['currency']
            if currency not in self._available_balances:
                self._available_balances[currency] = 0
            self._available_balances[currency] += float(balance["available"])
        return self._available_balances

    def load_balances_btc(self):
        """
            ct['Kucoin'].load_balances_btc()
        """
        available_balances = self.get_accounts()
        self._complete_balances_btc = {}
        for balance in available_balances:
            currency = balance['currency']
            if currency not in self._complete_balances_btc:
                self._complete_balances_btc[currency] = {
                    'Available': 0,
                    'OnOrders': 0,
                    'Total': 0
                }
            self._complete_balances_btc[currency]['Available'] += float(balance['available'])
            self._complete_balances_btc[currency]['OnOrders'] += float(balance['balance']) - float(balance['available'])
            self._complete_balances_btc[currency]['Total'] += float(balance['balance'])
        return self._complete_balances_btc

    def load_order_book(self, market, depth = 5):
        pass

    def submit_trade(self, direction, market, price, amount, trade_type):
        pass
