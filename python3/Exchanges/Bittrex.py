import time
import hmac
import hashlib
import urllib
import requests
import pprint
import pandas as pd

from Exchange import Exchange

class Bittrex(Exchange):
    def __init__(self, APIKey='', Secret=''):
        super().__init__(APIKey, Secret)
        self.BASE_URL = 'https://bittrex.com/api/v1.1/'

    def get_request(self, url, base_url_override = None):
        # print('Requesting url ' + url)
        if base_url_override is None:
            base_url_override = self.BASE_URL
        try:
            result = requests.get(base_url_override + url).json()
            if result.get('success', None) == True:
                return result['result']
            else:
                return self.get_request(url)
        except Exception as e:
            self.print_exception(base_url_override + url + ". " + str(e))
            return self.get_request(url)

    def trading_api_request(self, command, extra=''):
        try:
            nonce = str(int(time.time()*1000))
            request_url = self.BASE_URL + command + '?' + 'apikey=' + self.APIKey + "&nonce=" + nonce + extra
            result = requests.get(
                request_url,
                headers={"apisign": hmac.new(self.Secret.encode(), request_url.encode(), hashlib.sha512).hexdigest()}
            ).json()
            if result.get('success', None) == True:
                return result['result']
            else:
                print('**** ERROR **** Bittrex trading_api_request:',result.get('success'))
                return self.trading_api_request(command,extra)

        except Exception as e:
            self.print_exception(str(e))
            return {}

    #################################
    ### Exchange specific methods ###
    #################################

    ## Public API
    def get_all_currencies(self):
        return self.get_request('public/getcurrencies')

    def get_market_summaries(self):
        return self.get_request('public/getmarketsummaries')

    def get_order_book(self, market, type = 'both'):
        return self.get_request('public/getorderbook?market=' + market + '&type=' + type)

    ## Private API
    def get_balances(self):
        return self.trading_api_request('account/getbalances')

    def get_balances_in_btc(self):
        balances = self.get_balances()['result']
        markets = self.get_market_summaries()['result']

        result = 0
        for balance in range(len(balances)):
            currency = balances[balance]['Currency']
            if currency == 'BTC':
                btc_rate = 1
            else:
                for market in range(len(markets)):
                    if markets[market]['MarketName'] == 'BTC-' + currency:
                        btc_rate = (markets[market]['Bid'] + markets[market]['Ask']) / 2
            result = result + balances[balance]['Balance'] * btc_rate
        return result

    def get_open_orders_in_market(self,market):
        return self.trading_api_request('market/getopenorders','&market='+market)

    def cancel_order(self,order_uuid):
        return self.trading_api_request('market/cancel','&uuid='+order_uuid)

    def get_ticks(self, market, interval = 'fiveMin'):
        return self.get_request('https://bittrex.com/Api/v2.0/pub/market/GetTicks?marketName=' + market + '&tickInterval=' + interval, '')

    #######################
    ### Generic methods ###
    #######################
    def load_currencies(self):
        currencies = self.get_all_currencies()
        self._currencies = {}
        for currency in currencies:
            try:
                if currency['IsActive']:
                    enabled = 1
                else:
                    enabled = 0

                self._currencies[currency['Currency']] = {
                    'Name': currency['CurrencyLong'],
                    'Enabled': enabled
                }
            except Exception as e:
                self.print_exception(str(e))

        return self._currencies

    def load_markets(self):
        self._markets = {}
        self._active_markets = {}
        all_markets = self.get_market_summaries()

        for entry in all_markets:
            try:
                market_symbol = entry['MarketName']
                local_base = market_symbol[0:market_symbol.find('-')]
                local_curr = market_symbol[market_symbol.find('-')+1:]

                self.update_market(market_symbol, local_base, local_curr, entry['Bid'], entry['Ask'], True)
            except Exception as e:
                self.print_exception(str(entry) + ". " + str(e))
        return self._active_markets

    def load_available_balances(self):
        available_balances = self.get_balances()
        self._available_balances = {}
        for balance in available_balances:
            currency = balance['Currency']
            self._available_balances[currency] = balance["Available"]
        return self._available_balances

    def load_balances_btc(self):
        balances = self.get_balances()
        self._complete_balances_btc = {}
        for balance in balances:
            try:
                currency = balance['Currency']
                self._complete_balances_btc[currency] = {
                    'Available': balance["Available"],
                    'OnOrders': balance["Balance"] - balance["Available"],
                    'Total': balance["Balance"]
                }
            except Exception as e:
                self.print_exception(str(e))
        return self._complete_balances_btc

    def load_order_book(self, market, depth = 5):
        raw_results = self.get_order_book(market,'both')
        take_bid = min(depth, len(raw_results['buy']))
        take_ask = min(depth, len(raw_results['sell']))

        if take_bid == 0 and take_ask == 0:
            results = { 'Tradeable': 0, 'Bid': {}, 'Ask': {} }
        else:
            results = { 'Tradeable': 1, 'Bid': {}, 'Ask': {} }
        for i in range(take_bid):
            results['Bid'][i] = {
                'Price': raw_results['buy'][i]['Rate'],
                'Quantity': raw_results['buy'][i]['Quantity'],
            }
        for i in range(take_ask):
            results['Ask'][i] = {
                'Price': raw_results['sell'][i]['Rate'],
                'Quantity': raw_results['sell'][i]['Quantity'],
            }

        return results

    def submit_trade(self, direction, market, price, amount, trade_type):
        request = '&market=' + market + "&quantity={0:.8f}&rate={1:.8f}".format(amount, price)
        order_kind = 'market/buylimit'
        if direction == 'sell':
            order_kind = 'market/selllimit'
        trade = self.trading_api_request(order_kind,request)
        amount_traded = amount

        if trade_type == 'ImmediateOrCancel':
            time.sleep(.5)
            open_orders = self.get_open_orders_in_market(market)
            for open_order in open_orders:
                if open_order['OrderUuid'] == trade['uuid']:
                    self.cancel_order(trade['uuid'])
                    amount_traded = open_order['Quantity'] - open_order['QuantityRemaining']

        return {
                'Amount': amount_traded,
                'OrderNumber': trade['uuid']
            }
