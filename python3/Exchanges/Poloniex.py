import time
import hmac
import hashlib
import urllib
import requests

from Exchange import Exchange

class Poloniex(Exchange):
    def __init__(self, APIKey='', Secret=''):
        super().__init__(APIKey, Secret)
        """
            For API details see https://docs.poloniex.com
        """
        self.BASE_URL = 'https://poloniex.com/'
        self._precision = 8

    def get_request(self, url):
        try:
            result = requests.get(self.BASE_URL + url).json()
            if 'error' in result:
                self.log_request_error(result['error'])
                if self.retry_count_not_exceeded():
                    return self.get_request(url)
                else:
                    return {}
            else:
                self.log_request_success()
                return result
        except Exception as e:
            self.log_request_error(str(e))
            if self.retry_count_not_exceeded():
                return self.get_request(url)
            else:
                return {}

    def trading_api_request(self, command, req={}):
        try:
            req['command'] = command
            req['nonce'] = int(time.time()*1000000)
            post_data = urllib.parse.urlencode(req)
            sign = hmac.new(self.Secret.encode(), post_data.encode(), hashlib.sha512).hexdigest()

            headers = {
                'Sign': sign,
                'Key': self.APIKey
            }

            result = requests.post(self.BASE_URL + 'tradingApi', data = req, headers = headers).json()
            if 'error' in result:
                self.log_request_error(result['error'])
                if self.retry_count_not_exceeded():
                    return self.trading_api_request(command, req)
                else:
                    return {}
            else:
                self.log_request_success()
                return result
        except Exception as e:
            self.log_request_error(str(e))
            if self.retry_count_not_exceeded():
                return self.trading_api_request(command, req)
            else:
                return {}

    ########################################
    ### Exchange specific public methods ###
    ########################################

    def get_all_markets(self):
        """
            Call: https://poloniex.com/public?command=returnTicker
            Debug: ct['Poloniex'].get_all_markets()
            {'BTC_ARDR': {'baseVolume': '1.00000000',
                          'high24hr': '0.00001600',
                          'highestBid': '0.00001500',
                          'id': 177,
                          'isFrozen': '0',
                          'last': '0.00001500',
                          'low24hr': '0.00001500',
                          'lowestAsk': '0.00001550',
                          'percentChange': '0.00000000',
                          'quoteVolume': '400000.00000000'},
                ...
             'XMR_ZEC': {'baseVolume': '1.00000000',
                         'high24hr': '0.00001600',
                         'highestBid': '0.00001500',
                         'id': 179,
                         'isFrozen': '0',
                         'last': '0.00001500',
                         'low24hr': '0.00001500',
                         'lowestAsk': '0.00001550',
                         'percentChange': '0.00000000',
                         'quoteVolume': '400000.00000000'}}
        """
        return self.get_request('public?command=returnTicker')

    def get_all_markets_24h_volume(self):
        """
            Call: https://poloniex.com/public?command=return24hVolume
            Debug: ct['Poloniex'].get_all_markets_24h_volume()
            { 'BTC_ARDR': {'ARDR': '400000.00000000', 'BTC': '1.00000000'},
              'BTC_BAT':  {'BAT': '400000.00000000', 'BTC': '1.00000000'},
              ...
              'XMR_ZEC':  {'XMR': '1.00000000', 'ZEC': '1.00000000'},
              'totalBTC': '1000.00000000',
              'totalETH': '1000.00000000',
              'totalUSDC': '2000000.00000000',
              'totalUSDT': '3000000.00000000',
              'totalXMR': '300.00000000',
              'totalXUSD': '0.00000000'}
        """
        return self.get_request('public?command=return24hVolume')

    def get_order_book(self, market, depth = '5'):
        """
            Call: https://poloniex.com/public?command=returnOrderBook&currencyPair=BTC_NXT&depth=3
            Debug: ct['Poloniex'].get_order_book('BTC_ETH','2')
            {'asks': [['0.03000002', 100.00000000], ['0.03000003', 100.00000000]],
             'bids': [['0.03000001', 100.00000000], ['0.03000000', 100.00000000]],
             'isFrozen': '0',
             'seq': 123456789}
        """
        url = "public?command=returnOrderBook&currencyPair={}&depth={}".format(market, depth)
        return self.get_request(url)

    def get_all_order_books(self, depth = '5'):
        """
            Call: https://poloniex.com/public?command=returnOrderBook&currencyPair=all&depth=2
            Debug: ct['Poloniex'].get_all_order_books('2')
            {'BTC_ARDR': {'asks': [['0.03000002', 100.00000000], ['0.03000003', 100.00000000]],
                          'bids': [['0.03000001', 100.00000000], ['0.03000000', 100.00000000]],
                          'isFrozen': '0',
                          'seq': 123456789},
             'BTC_BAT': {'asks': [['0.03000002', 100.00000000], ['0.03000003', 100.00000000]],
                         'bids': [['0.03000001', 100.00000000], ['0.03000000', 100.00000000]],
                         'isFrozen': '0',
                         'seq': 123456789},
             ...
              'XMR_ZEC': {'asks': [['0.03000002', 100.00000000], ['0.03000003', 100.00000000]],
                          'bids': [['0.03000001', 100.00000000], ['0.03000000', 100.00000000]],
                          'isFrozen': '0',
                          'seq': 123456789}}
        """
        return self.get_order_book('all',depth)

    def get_trade_history(self, market, start, end):
        """
            Returns the past 200 trades for a given market, or up to 50,000
            trades between a range specified in UNIX timestamps by the "start"
            and "end" GET parameters.

            Call: https://poloniex.com/public?command=returnTradeHistory&currencyPair=BTC_NXT&start=1410158341&end=1410499372
            Debug: ct['Poloniex'].get_trade_history('USDT_BTC', '1540000000','1540000000')
            [{'amount': '1.00000000',
              'date': '2019-01-20 01:23:45',
              'globalTradeID': 123456789,
              'rate': '1.00000000',
              'total': '1.00000000',
              'tradeID': 123456789,
              'type': 'buy'},
              ...
             {'amount': '1.00000000',
              'date': '2019-01-20 01:23:44',
              'globalTradeID': 123456789,
              'rate': '1.00000000',
              'total': '1.00000000',
              'tradeID': 123456789,
              'type': 'buy'}]
        """
        url = "public?command=returnTradeHistory&currencyPair={}&start={}&end={}".format(market, start, end)
        return self.get_request(url)

    def get_chart_data(self, market, start, end, period):
        """
            Returns candlestick chart data. Required GET parameters are
            "currencyPair", "period" (candlestick period in seconds; valid
            values are 300, 900, 1800, 7200, 14400, and 86400), "start", and
            "end". "Start" and "end" are given in UNIX timestamp format and used
            to specify the date range for the data returned.

            Call: https://poloniex.com/public?command=returnChartData&currencyPair=BTC_XMR&start=1405699200&end=9999999999&period=14400
            Debug: ct['Poloniex'].get_chart_data('BTC_ETH', '1540000000','1540000000', '300')
            [{'close': 0.03000000,
              'date': 1540000000,
              'high': 0.03000000,
              'low': 0.03000000,
              'open': 0.03000000,
              'quoteVolume': 0.03000000,
              'volume': 0.00090000,
              'weightedAverage': 0.03000000},
             ...
             {'close': 0.03000000,
              'date': 1550000000,
              'high': 0.03000000,
              'low': 0.03000000,
              'open': 0.03000000,
              'quoteVolume': 0.03000000,
              'volume': 0.00090000,
              'weightedAverage': 0.03000000}]
        """
        url = "public?command=returnChartData&currencyPair={}&start={}&end={}&period={}".format(market, start, end, period)
        return self.get_request(url)

    def get_all_currencies(self):
        """
            Returns information about currencies.

            Call: https://poloniex.com/public?command=returnCurrencies
            Debug: ct['Poloniex'].get_all_currencies()
            {'1CR': {'delisted': 1,
                     'depositAddress': None,
                     'disabled': 1,
                     'frozen': 0,
                     'humanType': 'BTC Clone',
                     'id': 1,
                     'minConf': 10000,
                     'name': '1CRedit',
                     'txFee': '0.01000000'},
            ...
             'eTOK': {'delisted': 1,
                      'depositAddress': None,
                      'disabled': 1,
                      'frozen': 0,
                      'humanType': 'BTC Clone',
                      'id': 72,
                      'minConf': 10000,
                      'name': 'eToken',
                      'txFee': '0.00100000'}}
        """
        return self.get_request('public?command=returnCurrencies')

    def get_loan_orders(self, currency):
        """
            Returns the list of loan offers and demands for a given currency,
            specified by the "currency" GET parameter.

            Call: https://poloniex.com/public?command=returnLoanOrders&currency=BTC
            Debug: ct['Poloniex'].get_loan_orders('BTC')
            {'demands': [{'amount': '1.00000000',
                          'rangeMax': 2,
                          'rangeMin': 2,
                          'rate': '0.00002000'},
                          ...
                         {'amount': '1.00000000',
                          'rangeMax': 2,
                          'rangeMin': 2,
                          'rate': '0.00000100'}],
             'offers': [{'amount': '1.00000000',
                         'rangeMax': 2,
                         'rangeMin': 2,
                         'rate': '0.00003000'},
                         ...
                        {'amount': '1.00000000',
                         'rangeMax': 2,
                         'rangeMin': 2,
                         'rate': '0.00004000'}]}
        """
        return self.get_request('public?command=returnLoanOrders&currency={}'.format(currency))

    ########################################
    ### Exchange specific private methods ##
    ########################################

    def get_balances(self):
        """
            Returns all of your available balances.
            Debug: ct['Poloniex'].get_balances()
            {'1CR': '0.00000000',
             'ABY': '0.00000000',
             'AC': '0.00000000',
             ...
             'eTOK': '0.00000000'}
        """
        return self.trading_api_request("returnBalances")

    def get_available_balances(self, account = 'all'):
        """
            Returns your balances sorted by account. You may optionally specify
            the "account" POST parameter if you wish to fetch only the balances
            of one account.
            Debug: ct['Poloniex'].get_available_balances()
            {'exchange': {'ARDR': '123.12345678',
                          'BAT': '123.12345678',
                          ...
                          'ZRX': '123.12345678'}}
        """
        return self.trading_api_request("returnAvailableAccountBalances",{'account': account})

    def get_complete_balances(self, account = None):
        """
            Returns all of your balances, including available balance, balance
            on orders, and the estimated BTC value of your balance.
            Debug: ct['Poloniex'].get_complete_balances()
            {'1CR': {'available': '0.00000000',
                     'btcValue': '0.00000000',
                     'onOrders': '0.00000000'},
            ...
             'eTOK': {'available': '0.00000000',
                      'btcValue': '0.00000000',
                      'onOrders': '0.00000000'}}
        """
        request = {}
        if account is not None:
            request['account'] = account
        return self.trading_api_request("returnCompleteBalances", request)

    def get_deposit_addresses(self):
        """
            Returns all of your available balances.
            Debug: ct['Poloniex'].get_deposit_addresses()
            {'BTC': '1234567891011tHeReGuLaRsIzEaDdRess',
            ...
            'XMR': 'aLoNgEnOuGhAdDrEsStOcOnTaInBaDwOrDz1aLoNgEnOuGhAdDrEsStOcOnTaInBaDwOrDz2aLoNgEnOuGhAdDrEsStOcOnTaInBaDwOrDz3'
        """
        return self.trading_api_request("returnDepositAddresses")

    def generate_deposit_address(self, currency):
        """
            Generates a new deposit address for the currency specified by the
            "currency" POST parameter.
            Debug: ct['Poloniex'].generate_deposit_address('BAT')
            {'response': '0xSoMeAlPhAnUmEr1c',
             'success': 1}
        """
        return self.trading_api_request("generateNewAddress",{'currency':currency})

    def get_deposits_and_withdrawals(self, start, end):
        """
            Returns your deposit and withdrawal history within a range,
            specified by the "start" and "end" POST parameters, both of which
            should be given as UNIX timestamps.
            Debug: ct['Poloniex'].get_deposits_and_withdrawals(1540000000, 1540000000)
            {'deposits': [{'address': '1234567891011tHeReGuLaRsIzEaDdReSs',
                           'amount': '0.00000001',
                           'confirmations': 2,
                           'currency': 'BTC',
                           'status': 'COMPLETE',
                           'timestamp': 1540000000,
                           'txid': 'r3gulartransact1on1d'},
                           ...
                           {'address': '1234567891011tHeReGuLaRsIzEaDdReSs',
                            'amount': '0.00000001',
                            'confirmations': 2,
                            'currency': 'BTC',
                            'status': 'COMPLETE',
                            'timestamp': 1540000000,
                            'txid': 'r3gulartransact1on1d1'}],
             'withdrawals': [{'address': '1234567891012tHeReGuLaRsIzEaDdReSs',
                              'amount': '0.00000001',
                              'currency': 'BTC',
                              'fee': '0.00000000',
                              'ipAddress': '127.0.0.1',
                              'status': 'COMPLETE: '
                                        'r3gulartransact1on1d2',
                              'timestamp': 1540000000,
                              'withdrawalNumber': 12345678},
                              ...
                              {'address': '1234567891012tHeReGuLaRsIzEaDdReSs',
                              'amount': '0.00000001',
                              'currency': 'BTC',
                              'fee': '0.00000000',
                              'ipAddress': '127.0.0.1',
                              'status': 'COMPLETE: '
                                        'r3gulartransact1on1d3',
                              'timestamp': 1540000000,
                              'withdrawalNumber': 12345679}]}
        """
        return self.trading_api_request("returnDepositsWithdrawals",{'start':start,'end':end})

    def get_open_orders(self, market):
        """
            Returns your open orders for a given market, specified by the
            "currencyPair" POST parameter, e.g. "BTC_XCP". Set "currencyPair"
            to "all" to return open orders for all markets.
            Debug: ct['Poloniex'].get_open_orders('USDT_BTC')
            [{'amount': '123.12345678',
              'date': '2019-01-20 01:23:45',
              'margin': 0,
              'orderNumber': '12345678910',
              'rate': '10.00000000',
              'startingAmount': '20.00000000',
              'total': '200.00000000',
              'type': 'buy'}]
        """
        return self.trading_api_request("returnOpenOrders",{'currencyPair':market})

    def get_all_open_orders(self):
        """
            Returns your open orders for a given market, specified by the
            "currencyPair" POST parameter, e.g. "BTC_XCP". Set "currencyPair" to
            "all" to return open orders for all markets.
            Debug: ct['Poloniex'].get_all_open_orders()
            {'BTC_ARDR': [],
            ...
             'XMR_ZEC': []}
        """
        return self.get_open_orders('all')

    def get_private_trade_history(self, market, start, end, limit = '10000'):
        """
            Returns your trade history for a given market, specified by the
            "currencyPair" POST parameter. You may specify "all" as the
            currencyPair to receive your trade history for all markets. You may
            optionally specify a range via "start" and/or "end" POST parameters,
            given in UNIX timestamp format; if you do not specify a range, it
            will be limited to one day. You may optionally limit the number of
            entries returned using the "limit" parameter, up to a maximum of
            10,000. If the "limit" parameter is not specified, no more than 500
            entries will be returned.
            Debug: ct['Poloniex'].get_private_trade_history('USDT_BTC', 1540000000, 1540000000)
            [{'amount': '0.00010000',
              'category': 'exchange',
              'date': '2019-01-20 01:23:45',
              'fee': '0.00000000',
              'globalTradeID': 123456789,
              'orderNumber': '12345678910',
              'rate': '1000.00000000',
              'total': '0.10000000',
              'tradeID': '123456789',
              'type': 'buy'},
              ...
             {'amount': '0.00010000',
              'category': 'exchange',
              'date': '2019-01-20 01:23:44',
              'fee': '0.00000000',
              'globalTradeID': 123456790,
              'orderNumber': '12345678911',
              'rate': '1000.00000000',
              'total': '0.10000000',
              'tradeID': '123456790',
              'type': 'buy'}]
        """
        parameters = {
            'currencyPair': market,
            'limit':        limit,
        }
        if start is not None and end is not None:
            parameters['start'] = start
            parameters['end'] = end

        return self.trading_api_request("returnTradeHistory", parameters)

    def get_private_all_trade_history(self, start, end, limit = '10000'):
        """
            Debug: ct['Poloniex'].get_private_all_trade_history(1540000000, 1540000000)
            {'BTC_BAT': [{'amount': '0.00010000',
                          'category': 'exchange',
                          'date': '2019-01-20 01:23:45',
                          'fee': '0.00000000',
                          'globalTradeID': 123456789,
                          'orderNumber': '12345678910',
                          'rate': '1000.00000000',
                          'total': '0.10000000',
                          'tradeID': '123456789',
                          'type': 'buy'},
                         ...
                         {'amount': '0.00010000',
                          'category': 'exchange',
                          'date': '2019-01-20 01:23:44',
                          'fee': '0.00000000',
                          'globalTradeID': 123456790,
                          'orderNumber': '12345678911',
                          'rate': '1000.00000000',
                          'total': '0.10000000',
                          'tradeID': '123456790',
                          'type': 'buy'}
                         ],
                          ...
               'XMR_ZEC': [{'amount': '0.00010000',
                            'category': 'exchange',
                            'date': '2019-01-20 01:23:45',
                            'fee': '0.00000000',
                            'globalTradeID': 123456789,
                            'orderNumber': '12345678910',
                            'rate': '1000.00000000',
                            'total': '0.10000000',
                            'tradeID': '123456789',
                            'type': 'buy'},
                            ...
                           {'amount': '0.00010000',
                            'category': 'exchange',
                            'date': '2019-01-20 01:23:45',
                            'fee': '0.00000000',
                            'globalTradeID': 123456789,
                            'orderNumber': '12345678910',
                            'rate': '1000.00000000',
                            'total': '0.10000000',
                            'tradeID': '123456789',
                            'type': 'buy'}
                        ]
                }
        """
        return self.get_private_trade_history('all', start, end, limit)

    def get_order_trades(self, orderNumber):
        """
            Returns all trades involving a given order, specified by the
            "orderNumber" POST parameter. If no trades for the order have
            occurred or you specify an order that does not belong to you, you
            will receive an error. See the documentation here for how to use the
            information from returnOrderTrades and returnOrderStatus to
            determine various status information about an order.
            Debug: ct['Poloniex'].get_order_trades(12345678910)
            [{'amount': '0.00010000',
              'currencyPair': 'BTC_BAT',
              'date': '2019-01-20 01:23:45',
              'fee': '0.00000000',
              'globalTradeID': 123456789,
              'rate': '1000.00000000',
              'total': '0.10000000',
              'tradeID': '123456789',
              'type': 'buy'},
             {'amount': '0.00010000',
              'currencyPair': 'BTC_BAT',
              'date': '2019-01-20 01:23:45',
              'fee': '0.00000000',
              'globalTradeID': 123456789,
              'rate': '1000.00000000',
              'total': '0.10000000',
              'tradeID': '123456789',
              'type': 'buy'}]
        """
        return self.trading_api_request("returnOrderTrades",{'orderNumber':orderNumber})

    def get_order_status(self, orderNumber):
        """
            Returns the status of a given order, specified by the "orderNumber"
            POST parameter. If the specified orderNumber is not open, or it is
            not yours, you will receive an error.
            Debug: ct['Poloniex'].get_order_status(12345678910)
            {'result': {'12345678910': {'amount': '0.00010000',
                                        'currencyPair': 'BTC_BAT',
                                        'date': '2019-01-20 01:23:45',
                                        'rate': '10.00000000',
                                        'startingAmount': '20.00000000',
                                        'status': 'Open',
                                        'total': '200.00000000',
                                        'type': 'buy'}},
             'success': 1}
        """
        return self.trading_api_request("returnOrderStatus",{'orderNumber':orderNumber})

    def submit_trade(self, direction, market, price, amount, trade_type):
        """
            Debug: ct['Poloniex'].submit_trade('buy','USDT_BTC',1.00000000,100,'GTC')
            {'Amount': 0, 'OrderNumber': '12345678910'}
        """
        request =   {
                        'currencyPair': market,
                        'rate': "{0:.8f}".format(price),
                        'amount': "{0:.8f}".format(amount)
                    }
        if trade_type == 'ImmediateOrCancel':
            request['immediateOrCancel'] = '1'

        results = self.trading_api_request(direction, request)

        amount_traded = 0
        for trade in results['resultingTrades']:
            amount_traded += float(trade['amount'])
        return {
                'Amount': amount_traded,
                'OrderNumber': results['orderNumber']
            }

    def cancel_order(self, orderNumber):
        """
            Cancels an order you have placed in a given market. Required POST
            parameter is "orderNumber".
            Debug: ct['Poloniex'].cancel_order(12345678910)
            {'amount': '0.00010000',
             'message': 'Order #12345678910 canceled.',
             'success': 1}
        """
        return self.trading_api_request("cancelOrder",{'orderNumber':orderNumber})

    def move_order(self, orderNumber, rate, amount = None):
        """
            Cancels an order and places a new one of the same type in a single
            atomic transaction, meaning either both operations will succeed or
            both will fail. Required POST parameters are "orderNumber" and
            "rate"; you may optionally specify "amount" if you wish to change
            the amount of the new order. "postOnly" or "immediateOrCancel" may
            be specified for exchange orders.
            Debug: ct['Poloniex'].move_order(12345678910,1.00000000)
            {'orderNumber': '12345678910',
             'resultingTrades': {'USDT_BTC': []
                                },
             'success': 1}
        """
        request =   {
                        'orderNumber': orderNumber,
                        'rate': "{0:.8f}".format(rate)
                    }
        if amount is not None:
            request['amount'] = "{0:.8f}".format(amount)
        return self.trading_api_request("moveOrder", request)

    def withdraw(self, currency, amount, address, paymentId = None):
        """
            Immediately places a withdrawal for a given currency, with no email
            confirmation. In order to use this method, the withdrawal privilege
            must be enabled for your API key. Required POST parameters are
            "currency", "amount", and "address". For XMR withdrawals, you may
            optionally specify "paymentId".
        """
        request =   {
                        'currency': currency,
                        'amount': "{0:.8f}".format(amount),
                        'address': address
                    }
        if paymentId is not None:
            request['paymentId'] = paymentId
        return self.trading_api_request("withdraw", request)

    def get_fees(self):
        """
            If you are enrolled in the maker-taker fee schedule, returns your
            current trading fees and trailing 30-day volume in USD (API doc
            says BTC, but the output is actually in USD terms). This
            information is updated once every 24 hours.
            Debug: ct['Poloniex'].get_fees()
            {'makerFee': '0.00100000',
             'nextTier': 500000,
             'takerFee': '0.00200000',
             'thirtyDayVolume': '1.00000000'}
        """
        return self.trading_api_request("returnFeeInfo")

    #######################
    ### Generic methods ###
    #######################
    def load_currencies(self):
        currencies = self.get_all_currencies()
        self._currencies = {}
        for currency in currencies:
            try:
                self._currencies[currency] = {
                    'Name': currencies[currency]['name'],
                    'Enabled': 1 - max( currencies[currency]['delisted'],
                                        currencies[currency]['frozen'])
                }
            except Exception as e:
                self.log_request_error(str(e))

        return self._currencies

    def load_markets(self):
        self._markets = {}
        self._active_markets = {}
        all_markets = self.get_all_markets()

        for entry in all_markets:
            try:
                local_base = entry[0:entry.find('_')]
                local_curr = entry[entry.find('_')+1:]

                self.update_market(
                        entry,
                        local_base,
                        local_curr,
                        float(all_markets[entry]['highestBid']),
                        float(all_markets[entry]['lowestAsk']),
                        all_markets[entry]['isFrozen'] == '0'
                    )
            except Exception as e:
                self.log_request_error(str(entry) + ". " + str(e))
        return self._active_markets

    def load_available_balances(self):
        available_balances = self.get_balances()
        self._available_balances = {}
        for currency in available_balances:
            self._available_balances[currency] = float(available_balances[currency])
        return self._available_balances

    def load_balances_btc(self):
        balances = self.get_complete_balances()
        self._complete_balances_btc = {}
        for currency in balances:
            self._complete_balances_btc[currency] = {
                'Available': float(balances[currency]['available']),
                'OnOrders': float(balances[currency]['onOrders']),
                'Total': float(balances[currency]['available']) + float(balances[currency]['onOrders']),
                'BtcValue': float(balances[currency]['btcValue'])
            }
        return self._complete_balances_btc

    def load_order_book(self, market, depth = 5):
        raw_results = self.get_order_book(market, str(depth))
        take_bid = min(depth, len(raw_results['bids']))
        take_ask = min(depth, len(raw_results['asks']))

        results = {
            'Tradeable': 1-float(raw_results['isFrozen']),
            'Bid': {},
            'Ask': {}
        }
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

    def load_ticks(self, market_name, interval, lookback):
        # TODO:
        pass
