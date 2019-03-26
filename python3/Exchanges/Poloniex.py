import hashlib
import hmac
import json
import time
import urllib
from datetime import datetime

import requests
import websocket
from PyQt5.QtCore import QThreadPool

from Exchange import Exchange
from Worker import CTWorker


class Poloniex(Exchange):
    def __init__(self, APIKey='', Secret=''):
        super().__init__(APIKey, Secret)
        """
            For API details see https://docs.poloniex.com
        """
        self._BASE_URL = 'https://poloniex.com/'
        self._precision = 8
        self._tick_intervals = {
            '300':     300 / 60,
            '900':     900 / 60,
            '1800':    1800 / 60,
            '7200':    7200 / 60,
            '14400':   14400 / 60,
            '86400':   86400 / 60,
        }
        self._thread_pool = QThreadPool()
        self._thread_pool.start(CTWorker(self.ws_init))

        self._implements = {
            'ws_24hour_market_moves',
            'ws_account_balances',
            'ws_all_markets_best_bid_ask',
            'ws_order_book',
        }

        self._currency_id_map = {}
        self._currency_pair_map = {}

    def public_get_request(self, url):
        try:
            result = requests.get(self._BASE_URL + url).json()
            if 'error' in result:
                self.log_request_error(result['error'])
                if self.retry_count_not_exceeded():
                    return self.public_get_request(url)
                else:
                    return {}
            else:
                self.log_request_success()
                return result
        except Exception as e:
            self.log_request_error(str(e))
            if self.retry_count_not_exceeded():
                return self.public_get_request(url)
            else:
                return {}

    def private_sign_request(self, string_to_sign):
        return hmac.new(self._API_SECRET.encode(), string_to_sign.encode(), hashlib.sha512).hexdigest()

    def private_request(self, command, req={}):
        try:
            req['command'] = command
            req['nonce'] = int(time.time()*1000000)
            post_data = urllib.parse.urlencode(req)
            sign = self.private_sign_request(post_data)

            headers = {
                'Sign': sign,
                'Key': self._API_KEY
            }

            result = requests.post(self._BASE_URL + 'tradingApi', data = req, headers = headers).json()
            if 'error' in result:
                self.log_request_error(result['error'])
                if self.retry_count_not_exceeded():
                    return self.private_request(command, req)
                else:
                    return {}
            else:
                self.log_request_success()
                return result
        except Exception as e:
            self.log_request_error(str(e))
            if self.retry_count_not_exceeded():
                return self.private_request(command, req)
            else:
                return {}

    ########################################
    ### Exchange specific public methods ###
    ########################################

    def public_get_all_markets(self):
        """
            Call: https://poloniex.com/public?command=returnTicker
            Debug: ct['Poloniex'].public_get_all_markets()
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
        return self.public_get_request('public?command=returnTicker')

    def public_get_all_markets_24h_volume(self):
        """
            Call: https://poloniex.com/public?command=return24hVolume
            Debug: ct['Poloniex'].public_get_all_markets_24h_volume()
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
        return self.public_get_request('public?command=return24hVolume')

    def public_get_order_book(self, market, depth = '5'):
        """
            Call: https://poloniex.com/public?command=returnOrderBook&currencyPair=BTC_NXT&depth=3
            Debug: ct['Poloniex'].public_get_order_book('BTC_ETH','2')
            {'asks': [['0.03000002', 100.00000000], ['0.03000003', 100.00000000]],
             'bids': [['0.03000001', 100.00000000], ['0.03000000', 100.00000000]],
             'isFrozen': '0',
             'seq': 123456789}
        """
        url = "public?command=returnOrderBook&currencyPair={}&depth={}".format(market, depth)
        return self.public_get_request(url)

    def public_get_all_order_books(self, depth = '5'):
        """
            Call: https://poloniex.com/public?command=returnOrderBook&currencyPair=all&depth=2
            Debug: ct['Poloniex'].public_get_all_order_books('2')
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
        return self.public_get_order_book('all',depth)

    def public_get_market_history(self, market, start = None, end = None):
        """
            Returns the past 200 trades for a given market, or up to 50,000
            trades between a range specified in UNIX timestamps by the "start"
            and "end" GET parameters.

            Call: https://poloniex.com/public?command=returnTradeHistory&currencyPair=BTC_NXT&start=1410158341&end=1410499372
            Debug: ct['Poloniex'].public_get_market_history('USDT_BTC', '1540000000','1540000000')
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
        if start is None:
            url = "public?command=returnTradeHistory&currencyPair={}".format(market)
        else:
            url = "public?command=returnTradeHistory&currencyPair={}&start={}&end={}".format(market, start, end)
        return self.public_get_request(url)

    def public_get_chart_data(self, market, start, end, period):
        """
            Returns candlestick chart data. Required GET parameters are
            "currencyPair", "period" (candlestick period in seconds; valid
            values are 300, 900, 1800, 7200, 14400, and 86400), "start", and
            "end". "Start" and "end" are given in UNIX timestamp format and used
            to specify the date range for the data returned.

            Call: https://poloniex.com/public?command=returnChartData&currencyPair=BTC_XMR&start=1405699200&end=9999999999&period=14400
            Debug: ct['Poloniex'].public_get_chart_data('BTC_ETH', '1540000000','1540000000', '300')
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
        return self.public_get_request(url)

    def public_get_currencies(self):
        """
            Returns information about currencies.

            Call: https://poloniex.com/public?command=returnCurrencies
            Debug: ct['Poloniex'].public_get_currencies()
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
        return self.public_get_request('public?command=returnCurrencies')

    def public_get_loan_orders(self, currency):
        """
            Returns the list of loan offers and demands for a given currency,
            specified by the "currency" GET parameter.

            Call: https://poloniex.com/public?command=returnLoanOrders&currency=BTC
            Debug: ct['Poloniex'].public_get_loan_orders('BTC')
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
        return self.public_get_request('public?command=returnLoanOrders&currency={}'.format(currency))

    ########################################
    ### Exchange specific private methods ##
    ########################################

    def private_get_balances(self):
        """
            Returns all of your available balances.
            Debug: ct['Poloniex'].private_get_balances()
            {'1CR': '0.00000000',
             'ABY': '0.00000000',
             'AC': '0.00000000',
             ...
             'eTOK': '0.00000000'}
        """
        return self.private_request("returnBalances")

    def private_get_available_balances(self, account = 'all'):
        """
            Returns your balances sorted by account. You may optionally specify
            the "account" POST parameter if you wish to fetch only the balances
            of one account.
            Debug: ct['Poloniex'].private_get_available_balances()
            {'exchange': {'ARDR': '123.12345678',
                          'BAT': '123.12345678',
                          ...
                          'ZRX': '123.12345678'}}
        """
        return self.private_request("returnAvailableAccountBalances",{'account': account})

    def private_get_complete_balances(self, account = None):
        """
            Returns all of your balances, including available balance, balance
            on orders, and the estimated BTC value of your balance.
            Debug: ct['Poloniex'].private_get_complete_balances()
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
        return self.private_request("returnCompleteBalances", request)

    def private_get_deposit_addresses(self):
        """
            Returns all of your available balances.
            Debug: ct['Poloniex'].private_get_deposit_addresses()
            {'BTC': '1234567891011tHeReGuLaRsIzEaDdRess',
            ...
            'XMR': 'aLoNgEnOuGhAdDrEsStOcOnTaInBaDwOrDz1aLoNgEnOuGhAdDrEsStOcOnTaInBaDwOrDz2aLoNgEnOuGhAdDrEsStOcOnTaInBaDwOrDz3'
        """
        return self.private_request("returnDepositAddresses")

    def private_generate_deposit_address(self, currency):
        """
            Generates a new deposit address for the currency specified by the
            "currency" POST parameter.
            Debug: ct['Poloniex'].private_generate_deposit_address('BAT')
            {'response': '0xSoMeAlPhAnUmEr1c',
             'success': 1}
        """
        return self.private_request("generateNewAddress",{'currency':currency})

    def private_get_deposits_and_withdrawals(self, start, end):
        """
            Returns your deposit and withdrawal history within a range,
            specified by the "start" and "end" POST parameters, both of which
            should be given as UNIX timestamps.
            Debug: ct['Poloniex'].private_get_deposits_and_withdrawals(1540000000, 1540000000)
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
        return self.private_request("returnDepositsWithdrawals",{'start':start,'end':end})

    def private_get_open_orders_in_market(self, market):
        """
            Returns your open orders for a given market, specified by the
            "currencyPair" POST parameter, e.g. "BTC_XCP". Set "currencyPair"
            to "all" to return open orders for all markets.
            Debug: ct['Poloniex'].private_get_all_open_orders('USDT_BTC')
            [{'amount': '123.12345678',
              'date': '2019-01-20 01:23:45',
              'margin': 0,
              'orderNumber': '12345678910',
              'rate': '10.00000000',
              'startingAmount': '20.00000000',
              'total': '200.00000000',
              'type': 'buy'}]
        """
        if self.has_api_keys():
            return self.private_request("returnOpenOrders",{'currencyPair':market})
        else:
            return []

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
        return self.private_get_open_orders_in_market('all')

    def private_get_trade_history_in_market(self, market, start, end, limit = '10000'):
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
            Debug: ct['Poloniex'].private_get_trade_history_in_market('USDT_BTC', 1540000000, 1540000000)
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

        return self.private_request("returnTradeHistory", parameters)

    def private_get_all_trade_history(self, start, end, limit = '10000'):
        """
            Debug: ct['Poloniex'].private_get_all_trade_history(1540000000, 1540000000)
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
        return self.private_get_trade_history_in_market('all', start, end, limit)

    def private_get_order_trades(self, orderNumber):
        """
            Returns all trades involving a given order, specified by the
            "orderNumber" POST parameter. If no trades for the order have
            occurred or you specify an order that does not belong to you, you
            will receive an error. See the documentation here for how to use the
            information from returnOrderTrades and returnOrderStatus to
            determine various status information about an order.
            Debug: ct['Poloniex'].private_get_order_trades(12345678910)
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
        return self.private_request("returnOrderTrades",{'orderNumber':orderNumber})

    def private_get_order_status(self, orderNumber):
        """
            Returns the status of a given order, specified by the "orderNumber"
            POST parameter. If the specified orderNumber is not open, or it is
            not yours, you will receive an error.
            Debug: ct['Poloniex'].private_get_order_status(12345678910)
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
        return self.private_request("returnOrderStatus",{'orderNumber':orderNumber})

    def private_submit_new_order(self, direction, market, price, amount, trade_type):
        """
            Debug: ct['Poloniex'].private_submit_new_order('buy','USDT_BTC',1.00000000,100,'GTC')
            {'Amount': 0, 'OrderNumber': '12345678910'}
        """
        request =   {
                        'currencyPair': market,
                        'rate': "{0:.8f}".format(price),
                        'amount': "{0:.8f}".format(amount)
                    }
        if trade_type == 'ImmediateOrCancel':
            request['immediateOrCancel'] = '1'

        results = self.private_request(direction, request)

        amount_traded = 0
        for trade in results['resultingTrades']:
            amount_traded += float(trade['amount'])
        return {
                'Amount': amount_traded,
                'OrderNumber': results['orderNumber']
            }

    def private_cancel_order(self, orderNumber):
        """
            Cancels an order you have placed in a given market. Required POST
            parameter is "orderNumber".
            Debug: ct['Poloniex'].private_cancel_order(12345678910)
            {'amount': '0.00010000',
             'message': 'Order #12345678910 canceled.',
             'success': 1}
        """
        return self.private_request("cancelOrder", {'orderNumber': orderNumber})

    def private_move_order(self, orderNumber, rate, amount = None):
        """
            Cancels an order and places a new one of the same type in a single
            atomic transaction, meaning either both operations will succeed or
            both will fail. Required POST parameters are "orderNumber" and
            "rate"; you may optionally specify "amount" if you wish to change
            the amount of the new order. "postOnly" or "immediateOrCancel" may
            be specified for exchange orders.
            Debug: ct['Poloniex'].private_move_order(12345678910,1.00000000)
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
        return self.private_request("moveOrder", request)

    def private_submit_withdrawal_request(self, currency, amount, address, paymentId = None):
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
        return self.private_request("withdraw", request)

    def private_get_fees(self):
        """
            If you are enrolled in the maker-taker fee schedule, returns your
            current trading fees and trailing 30-day volume in USD (API doc
            says BTC, but the output is actually in USD terms). This
            information is updated once every 24 hours.
            Debug: ct['Poloniex'].private_get_fees()
            {'makerFee': '0.00100000',
             'nextTier': 500000,
             'takerFee': '0.00200000',
             'thirtyDayVolume': '1.00000000'}
        """
        return self.private_request("returnFeeInfo")

    ########################################
    ### Exchange specific websockets API ###
    ########################################

    def ws_init(self):
        self._ws = websocket.WebSocketApp("wss://api2.poloniex.com",
                                          on_message=self.ws_on_message,
                                          on_error=self.ws_on_error,
                                          on_close=self.ws_on_close
                                          )
        self._ws.run_forever()
        self.ws_subscribe(1002)
        self.ws_subscribe(1000)

    def ws_subscribe(self, channel):
        """
            Subscibe to a channel
            The following <channel> values are supported:

            Channel	Type	Name
            1000	Private	Account Notifications (Beta)
            1002	Public	Ticker Data
            1003	Public	24 Hour Exchange Volume
            1010	Public	Heartbeat
            <currency pair>	Public	Price Aggregated Book
            Debug: ct['Poloniex'].ws_subscribe(1000)
        """
        if channel == 1000:
            nonce = int(time.time()*1000000)
            self._ws.send(json.dumps({
                "command": "subscribe",
                "channel": 1000,
                "key": self._API_KEY,
                "payload": "nonce={}".format(nonce),
                "sign": self.private_sign_request("nonce={}".format(nonce))
            }))
        else:
            self._ws.send(json.dumps({"command": "subscribe", "channel": channel}))

    def ws_unsubscribe(self, channel):
        """
            Unsubscibe from a channel
            The following <channel> values are supported:

            Channel	Type	Name
            1000	Private	Account Notifications (Beta)
            1002	Public	Ticker Data
            1003	Public	24 Hour Exchange Volume
            1010	Public	Heartbeat
            <currency pair>	Public	Price Aggregated Book
        """
        self._ws.send(json.dumps({"command": "unsubscribe", "channel": channel}))

    def ws_on_message(self, message):
        parsed_message = json.loads(message)
        if len(parsed_message) > 0:
            msg_code = parsed_message[0]
            if msg_code == 1010:
                """
                    Heartbeats
                """
                self._ws_heartbeat = datetime.now().timestamp()
                return
            if msg_code == 1002:
                """
                    Ticker Data
                    [ <id>, null, [
                        <currency pair id>,
                        "<last trade price>",
                        "<lowest ask>",
                        "<highest bid>",
                        "<percent change in last 24 hours>",
                        "<base currency volume in last 24 hours>",
                        "<quote currency volume in last 24 hours>",
                        <is frozen>,
                        "<highest trade price in last 24 hours>",
                        "<lowest trade price in last 24 hours>"
                        ], ... ]
                """
                if len(parsed_message) > 1:
                    payload = parsed_message[2]
                    market_symbol = self._currency_pair_map[payload[0]]
                    self.update_market(
                        market_symbol,
                        {
                            'IsActive':         1-payload[7],
                            'IsRestricted':     payload[7],
                            'BaseVolume':       float(payload[5]),
                            'CurrVolume':       float(payload[6]),
                            'BestBid':          float(payload[3]),
                            'BestAsk':          float(payload[2]),
                            '24HrHigh':         float(payload[8]),
                            '24HrLow':          float(payload[9]),
                            '24HrPercentMove':  100 * float(payload[4]),
                            'LastTradedPrice':  float(payload[1]),
                        }
                    )
                return
            if msg_code == 1000:
                """
                    Account notification
                """
                for account_update in parsed_message[2]:
                    print(account_update)
                    if account_update[0] == 'b':
                        currency = self._currency_id_map.get(account_update[1], None)
                        if currency is not None:
                            self._available_balances[currency] = self._available_balances.get(currency, 0) + \
                                                                 float(account_update[3])
                    if account_update[0] == 'n':
                        market_symbol = self._currency_pair_map[account_update[1]]
                        if market_symbol not in self._open_orders:
                            self._open_orders[market_symbol] = []
                        if account_update[3] == 1:
                            order_type = 'Buy'
                        else:
                            order_type = 'Sell'
                        self._open_orders[market_symbol].append(
                            {
                                'OrderId': account_update[2],
                                'OrderType': order_type,
                                'OpderOpenedAt': datetime.strptime(account_update[6], "%Y-%m-%d %H:%M:%S"),
                                'Price': float(account_update[4]),
                                'Amount': float(account_update[5]),
                                'Total': float(account_update[4]) * float(account_update[5]),
                                'AmountRemaining': float(account_update[5]),
                            }
                        )
                    if account_update[0] == 'o':
                        order_id = account_update[1]
                        for market_symbol in self._open_orders:
                            for order_ix in range(self._open_orders[market_symbol]):
                                if order_id == self._open_orders[market_symbol][order_ix]['OrderId']:
                                    if float(account_update[2]) == 0:
                                        self._open_orders[market_symbol].pop(order_ix)
                                    else:
                                        self._open_orders[market_symbol][order_ix]['AmountRemaining'] = float(account_update[2])
                    if account_update[0] == 't':
                        print('Trade:', account_update)
                return
            if msg_code in self._currency_pair_map:
                """
                    Public market order book update
                """
                market_symbol = self._currency_pair_map[msg_code]
                sequence_id = parsed_message[1]
                payload = parsed_message[2]
                if payload[0][0] == 'i':
                    self._order_book[market_symbol] = {
                        'Bids': {},
                        'Asks': {},
                        'Sequence_Id': sequence_id
                    }
                    for price, amount in payload[0][1]['orderBook'][1].items():
                        self._order_book[market_symbol]['Bids'][float(price)] = float(amount)
                    for price, amount in payload[0][1]['orderBook'][0].items():
                        self._order_book[market_symbol]['Asks'][float(price)] = float(amount)
                    return
                if sequence_id < self._order_book[market_symbol]['Sequence_Id']:
                    print("Wrong ws message order: ", sequence_id, self._order_book[market_symbol]['Sequence_Id'])
                self._order_book[market_symbol]['Sequence_Id'] = max(sequence_id,
                                                                     self._order_book[market_symbol]['Sequence_Id'])
                for book_update in payload:
                    if book_update[0] == 'o':
                        if book_update[1] == 0:
                            if float(book_update[3]) == 0:
                                self._order_book[market_symbol]['Asks'].pop(float(book_update[2]), None)
                            else:
                                self._order_book[market_symbol]['Asks'][float(book_update[2])] = float(book_update[3])
                        if book_update[1] == 1:
                            if float(book_update[3]) == 0:
                                self._order_book[market_symbol]['Bids'].pop(float(book_update[2]), None)
                            else:
                                self._order_book[market_symbol]['Bids'][float(book_update[2])] = float(book_update[3])
                    if book_update[0] == 't':
                        if book_update[2] == 1:
                            order_type = 'Buy'
                        else:
                            order_type = 'Sell'
                        self._recent_market_trades[market_symbol].append(
                            {
                                'TradeId': book_update[1],
                                'TradeType': order_type,
                                'TradeTime': datetime.fromtimestamp(book_update[5]),
                                'Price': float(book_update[3]),
                                'Amount': float(book_update[4]),
                                'Total': float(book_update[3] * book_update[4])
                            }
                        )
                return
        print(message)

    def ws_on_error(self, error):
        print("*** Poloniex websocket ERROR: ", error)

    def ws_on_close(self):
        print("### Poloniex websocket is closed ###")

    #######################
    ### Generic methods ###
    #######################
    def get_consolidated_currency_definitions(self):
        """
            Loading currencies
            Debug: ct['Poloniex'].get_consolidated_currency_definitions()
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
        currencies = self.public_get_currencies()
        results = {}
        if isinstance(currencies, dict):
            for currency_key in currencies.keys():
                try:
                    currency = currencies[currency_key]
                    if currency['delisted'] == 0:
                        enabled = currency['disabled'] == 0 and currency['frozen'] == 0
                        if currency.get('depositAddress', '') is None:
                            address = ''
                        else:
                            address = currency.get('depositAddress', '')
                        results[currency_key] = {
                            'Name': currency['name'],
                            'DepositEnabled': enabled,
                            'WithdrawalEnabled': enabled,
                            'Notice': '',
                            'ExchangeBaseAddress': address,
                            'MinConfirmation': currency.get('minConf', 0),
                            'WithdrawalFee': float(currency.get('TxFee', 0)),
                            'WithdrawalMinAmount': 0,
                            'Precision': 0.00000001
                        }
                    self._currency_id_map[currency['id']] = currency_key
                except Exception as e:
                    self.log_request_error(str(e))

        return results

    def update_market_definitions(self):
        """
            Used to get the open and available trading markets at Bittrex along
            with other meta data.
            * Assumes that currency mappings are already available
            Debug: ct['Poloniex'].update_market_definitions()
        """
        markets = self.public_get_all_markets()
        if isinstance(markets, dict):
            for market_symbol in markets:
                try:
                    entry = markets[market_symbol]
                    local_base = market_symbol[0:market_symbol.find('_')]
                    local_curr = market_symbol[market_symbol.find('_')+1:]
                    is_frozen = entry.get('isFrozen', '1')
                    is_active = is_frozen == '0'
                    is_restricted = is_frozen == '1'
                    self.update_market(
                        market_symbol,
                        {
                            'LocalBase':        local_base,
                            'LocalCurr':        local_curr,
                            'BaseMinAmount':    0,
                            'BaseIncrement':    0.00000001,
                            'CurrMinAmount':    0,
                            'CurrIncrement':    0.00000001,
                            'PriceMin':         0,
                            'PriceIncrement':   0.00000001,
                            'IsActive':         is_active,
                            'IsRestricted':     is_restricted,
                            'BaseVolume':       float(entry['baseVolume']),
                            'CurrVolume':       float(entry['quoteVolume']),
                            'BestBid':          float(entry['highestBid']),
                            'BestAsk':          float(entry['lowestAsk']),
                            '24HrHigh':         float(entry['high24hr']),
                            '24HrLow':          float(entry['low24hr']),
                            '24HrPercentMove':  100 * float(entry['percentChange']),
                            'LastTradedPrice':  float(entry['last']),
                        }
                    )
                    self._currency_pair_map[entry['id']] = market_symbol
                except Exception as e:
                    self.log_request_error(str(e))

    def update_market_quotes(self):
        self.update_market_definitions()

    def update_market_24hrs(self):
        self.update_market_definitions()

    def get_consolidated_open_user_orders_in_market(self, market):
        """
            Used to retrieve outstanding orders
            Debug: ct['Poloniex'].get_consolidated_open_user_orders_in_market('LTCBTC')
        """
        open_orders = self.private_get_open_orders_in_market(market)
        results = []
        for order in open_orders:
            if order['type'] == 'buy':
                order_type = 'Buy'
            else:
                order_type = 'Sell'

            results.append({
                'OrderId': order['orderNumber'],
                'OrderType': order_type,
                'OpderOpenedAt': datetime.strptime(order['date'], "%Y-%m-%d %H:%M:%S"),
                'Price': float(order['rate']),
                'Amount': float(order['startingAmount']),
                'Total': float(order['total']),
                'AmountRemaining': float(order['amount']),
            })
        return results

    def get_consolidated_recent_market_trades_per_market(self, market):
        """
            Used to update recent market trades at a given market
            Debug: ct['Poloniex'].update_recent_market_trades_per_market('LTCBTC')
        """
        trades = self.public_get_market_history(market)
        results = []
        for trade in trades:
            if trade['type'] == 'buy':
                order_type = 'Buy'
            else:
                order_type = 'Sell'

            if float(trade['rate']) > 0 and float(trade['amount']) > 0:
                results.append({
                    'TradeId': trade['globalTradeID'],
                    'TradeType': order_type,
                    'TradeTime': datetime.strptime(trade['date'], "%Y-%m-%d %H:%M:%S"),
                    'Price': float(trade['rate']),
                    'Amount': float(trade['amount']),
                    'Total': float(trade['total'])
                })
        return results

    def get_consolidated_klines(self, market_symbol, interval = '300', lookback = None, startAt = None, endAt = None):
        """
            Returns candlestick chart data. Required GET parameters are
            "currencyPair", "period" (candlestick period in seconds; valid
            values are 300, 900, 1800, 7200, 14400, and 86400), "start", and
            "end". "Start" and "end" are given in UNIX timestamp format and used
            to specify the date range for the data returned. Fields include:
            Field	Description
            currencyPair	The currency pair of the market being requested.
            period	Candlestick period in seconds. Valid values are 300, 900,
                1800, 7200, 14400, and 86400.
            start	The start of the window in seconds since the unix epoch.
            end	The end of the window in seconds since the unix epoch.
            [ { date: 1539864000,
                high: 0.03149999,
                low: 0.031,
                open: 0.03144307,
                close: 0.03124064,
                volume: 64.36480422,
                quoteVolume: 2055.56810329,
                weightedAverage: 0.03131241 },
            ]
        """
        if lookback is None:
            lookback = 24 * 60
        if startAt is None:
            endAt = int(datetime.now().timestamp())
            startAt = endAt - lookback * 60

        load_chart = self. public_get_chart_data(market_symbol, startAt, endAt, interval)
        results = []
        for i in load_chart:
            new_row = i['date'], i['open'], i['high'], i['low'], i['close'], i['quoteVolume'], i['weightedAverage'] * i['quoteVolume']
            results.append(new_row)
        return results

    def get_consolidated_order_book(self, market, depth = 5):
        raw_results = self.public_get_order_book(market, str(depth))
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





    def load_available_balances(self):
        available_balances = self.private_get_balances()
        self._available_balances = {}
        for currency in available_balances:
            self._available_balances[currency] = float(available_balances[currency])
        return self._available_balances

    def load_balances_btc(self):
        balances = self.private_get_complete_balances()
        self._complete_balances_btc = {}
        for currency in balances:
            self._complete_balances_btc[currency] = {
                'Available': float(balances[currency]['available']),
                'OnOrders': float(balances[currency]['onOrders']),
                'Total': float(balances[currency]['available']) + float(balances[currency]['onOrders']),
                'BtcValue': float(balances[currency]['btcValue'])
            }
            self._available_balances[currency] = float(balances[currency]['available'])
        return self._complete_balances_btc
