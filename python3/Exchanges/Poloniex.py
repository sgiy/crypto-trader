import time
import json
from datetime import datetime
import hmac
import hashlib
import urllib
import requests
import websocket
from PyQt5.QtCore import QThreadPool
from Worker import CTWorker

from Exchange import Exchange

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

        self._ws_currency_id_map = {
            1:'1CR',
            2:'ABY',
            3:'AC',
            4:'ACH',
            5:'ADN',
            6:'AEON',
            7:'AERO',
            8:'AIR',
            275:'AMP',
            9:'APH',
            258:'ARCH',
            285:'ARDR',
            10:'AUR',
            11:'AXIS',
            12:'BALLS',
            13:'BANK',
            302:'BAT',
            14:'BBL',
            15:'BBR',
            16:'BCC',
            292:'BCH',
            308:'BCHABC',
            309:'BCHSV',
            17:'BCN',
            269:'BCY',
            18:'BDC',
            19:'BDG',
            20:'BELA',
            273:'BITCNY',
            21:'BITS',
            272:'BITUSD',
            22:'BLK',
            23:'BLOCK',
            24:'BLU',
            25:'BNS',
            305:'BNT',
            26:'BONES',
            27:'BOST',
            28:'BTC',
            29:'BTCD',
            30:'BTCS',
            31:'BTM',
            32:'BTS',
            33:'BURN',
            34:'BURST',
            35:'C2',
            36:'CACH',
            37:'CAI',
            38:'CC',
            39:'CCN',
            40:'CGA',
            41:'CHA',
            42:'CINNI',
            43:'CLAM',
            44:'CNL',
            45:'CNMT',
            46:'CNOTE',
            47:'COMM',
            48:'CON',
            49:'CORG',
            50:'CRYPT',
            51:'CURE',
            294:'CVC',
            52:'CYC',
            279:'DAO',
            60:'DASH',
            277:'DCR',
            53:'DGB',
            54:'DICE',
            55:'DIEM',
            56:'DIME',
            57:'DIS',
            58:'DNS',
            59:'DOGE',
            61:'DRKC',
            62:'DRM',
            63:'DSH',
            64:'DVK',
            65:'EAC',
            66:'EBT',
            67:'ECC',
            68:'EFL',
            69:'EMC2',
            70:'EMO',
            71:'ENC',
            298:'EOS',
            283:'ETC',
            267:'ETH',
            72:'eTOK',
            73:'EXE',
            270:'EXP',
            74:'FAC',
            75:'FCN',
            271:'FCT',
            76:'FIBRE',
            77:'FLAP',
            78:'FLDC',
            254:'FLO',
            79:'FLT',
            307:'FOAM',
            80:'FOX',
            81:'FRAC',
            82:'FRK',
            83:'FRQ',
            84:'FVZ',
            85:'FZ',
            86:'FZN',
            93:'GAME',
            87:'GAP',
            296:'GAS',
            88:'GDN',
            89:'GEMZ',
            90:'GEO',
            91:'GIAR',
            92:'GLB',
            94:'GML',
            291:'GNO',
            95:'GNS',
            290:'GNT',
            96:'GOLD',
            97:'GPC',
            98:'GPUC',
            261:'GRC',
            99:'GRCX',
            314:'GRIN',
            100:'GRS',
            101:'GUE',
            102:'H2O',
            103:'HIRO',
            104:'HOT',
            105:'HUC',
            260:'HUGE',
            106:'HVC',
            107:'HYP',
            108:'HZ',
            109:'IFC',
            265:'INDEX',
            263:'IOC',
            110:'ITC',
            111:'IXC',
            112:'JLH',
            113:'JPC',
            114:'JUG',
            115:'KDC',
            116:'KEY',
            301:'KNC',
            280:'LBC',
            117:'LC',
            118:'LCL',
            119:'LEAF',
            120:'LGC',
            121:'LOL',
            303:'LOOM',
            122:'LOVE',
            312:'LPT',
            123:'LQD',
            278:'LSK',
            124:'LTBC',
            125:'LTC',
            126:'LTCX',
            127:'MAID',
            306:'MANA',
            128:'MAST',
            129:'MAX',
            130:'MCN',
            131:'MEC',
            132:'METH',
            133:'MIL',
            134:'MIN',
            135:'MINT',
            136:'MMC',
            137:'MMNXT',
            138:'MMXIV',
            139:'MNTA',
            140:'MON',
            141:'MRC',
            142:'MRS',
            144:'MTS',
            145:'MUN',
            146:'MYR',
            147:'MZC',
            148:'N5X',
            149:'NAS',
            150:'NAUT',
            151:'NAV',
            152:'NBT',
            153:'NEOS',
            154:'NL',
            155:'NMC',
            310:'NMR',
            156:'NOBL',
            157:'NOTE',
            158:'NOXT',
            159:'NRS',
            160:'NSR',
            161:'NTX',
            288:'NXC',
            162:'NXT',
            163:'NXTI',
            295:'OMG',
            143:'OMNI',
            164:'OPAL',
            165:'PAND',
            289:'PASC',
            166:'PAWN',
            167:'PIGGY',
            168:'PINK',
            169:'PLX',
            170:'PMC',
            311:'POLY',
            171:'POT',
            172:'PPC',
            173:'PRC',
            174:'PRT',
            175:'PTS',
            176:'Q2C',
            177:'QBK',
            178:'QCN',
            179:'QORA',
            180:'QTL',
            304:'QTUM',
            274:'RADS',
            181:'RBY',
            182:'RDD',
            284:'REP',
            183:'RIC',
            184:'RZR',
            282:'SBD',
            268:'SC',
            185:'SDC',
            186:'SHIBE',
            187:'SHOPX',
            188:'SILK',
            189:'SJCX',
            190:'SLR',
            191:'SMC',
            300:'SNT',
            192:'SOC',
            193:'SPA',
            194:'SQL',
            195:'SRCC',
            196:'SRG',
            197:'SSD',
            281:'STEEM',
            297:'STORJ',
            198:'STR',
            287:'STRAT',
            199:'SUM',
            200:'SUN',
            201:'SWARM',
            202:'SXC',
            203:'SYNC',
            204:'SYS',
            205:'TAC',
            206:'TOR',
            207:'TRUST',
            208:'TWE',
            209:'UIS',
            210:'ULTC',
            211:'UNITY',
            212:'URO',
            299:'USDC',
            213:'USDE',
            214:'USDT',
            215:'UTC',
            216:'UTIL',
            217:'UVC',
            218:'VIA',
            219:'VOOT',
            276:'VOX',
            220:'VRC',
            221:'VTC',
            222:'WC',
            223:'WDC',
            224:'WIKI',
            225:'WOLF',
            226:'X13',
            227:'XAI',
            228:'XAP',
            229:'XBC',
            230:'XC',
            231:'XCH',
            232:'XCN',
            233:'XCP',
            234:'XCR',
            235:'XDN',
            236:'XDP',
            256:'XEM',
            237:'XHC',
            238:'XLB',
            239:'XMG',
            240:'XMR',
            241:'XPB',
            242:'XPM',
            243:'XRP',
            244:'XSI',
            245:'XST',
            246:'XSV',
            247:'XUSD',
            253:'XVC',
            248:'XXC',
            249:'YACC',
            250:'YANG',
            251:'YC',
            252:'YIN',
            286:'ZEC',
            293:'ZRX',
        }
        self._ws_currency_pair_map = {
            7:'BTC_BCN',
            14:'BTC_BTS',
            15:'BTC_BURST',
            20:'BTC_CLAM',
            24:'BTC_DASH',
            25:'BTC_DGB',
            27:'BTC_DOGE',
            38:'BTC_GAME',
            43:'BTC_HUC',
            50:'BTC_LTC',
            51:'BTC_MAID',
            58:'BTC_OMNI',
            61:'BTC_NAV',
            64:'BTC_NMC',
            69:'BTC_NXT',
            75:'BTC_PPC',
            89:'BTC_STR',
            92:'BTC_SYS',
            97:'BTC_VIA',
            100:'BTC_VTC',
            108:'BTC_XCP',
            112:'BTC_XEM',
            114:'BTC_XMR',
            116:'BTC_XPM',
            117:'BTC_XRP',
            121:'USDT_BTC',
            122:'USDT_DASH',
            123:'USDT_LTC',
            124:'USDT_NXT',
            125:'USDT_STR',
            126:'USDT_XMR',
            127:'USDT_XRP',
            129:'XMR_BCN',
            132:'XMR_DASH',
            137:'XMR_LTC',
            138:'XMR_MAID',
            140:'XMR_NXT',
            148:'BTC_ETH',
            149:'USDT_ETH',
            150:'BTC_SC',
            155:'BTC_FCT',
            162:'BTC_DCR',
            163:'BTC_LSK',
            166:'ETH_LSK',
            167:'BTC_LBC',
            168:'BTC_STEEM',
            169:'ETH_STEEM',
            170:'BTC_SBD',
            171:'BTC_ETC',
            172:'ETH_ETC',
            173:'USDT_ETC',
            174:'BTC_REP',
            175:'USDT_REP',
            176:'ETH_REP',
            177:'BTC_ARDR',
            178:'BTC_ZEC',
            179:'ETH_ZEC',
            180:'USDT_ZEC',
            181:'XMR_ZEC',
            182:'BTC_STRAT',
            184:'BTC_PASC',
            185:'BTC_GNT',
            186:'ETH_GNT',
            189:'BTC_BCH',
            190:'ETH_BCH',
            191:'USDT_BCH',
            192:'BTC_ZRX',
            193:'ETH_ZRX',
            194:'BTC_CVC',
            195:'ETH_CVC',
            196:'BTC_OMG',
            197:'ETH_OMG',
            198:'BTC_GAS',
            199:'ETH_GAS',
            200:'BTC_STORJ',
            201:'BTC_EOS',
            202:'ETH_EOS',
            203:'USDT_EOS',
            204:'BTC_SNT',
            205:'ETH_SNT',
            206:'USDT_SNT',
            207:'BTC_KNC',
            208:'ETH_KNC',
            209:'USDT_KNC',
            210:'BTC_BAT',
            211:'ETH_BAT',
            212:'USDT_BAT',
            213:'BTC_LOOM',
            214:'ETH_LOOM',
            215:'USDT_LOOM',
            216:'USDT_DOGE',
            217:'USDT_GNT',
            218:'USDT_LSK',
            219:'USDT_SC',
            220:'USDT_ZRX',
            221:'BTC_QTUM',
            222:'ETH_QTUM',
            223:'USDT_QTUM',
            224:'USDC_BTC',
            225:'USDC_ETH',
            226:'USDC_USDT',
            229:'BTC_MANA',
            230:'ETH_MANA',
            231:'USDT_MANA',
            232:'BTC_BNT',
            233:'ETH_BNT',
            234:'USDT_BNT',
            235:'USDC_BCH',
            236:'BTC_BCHABC',
            237:'USDC_BCHABC',
            238:'BTC_BCHSV',
            239:'USDC_BCHSV',
            240:'USDC_XRP',
            241:'USDC_XMR',
            242:'USDC_STR',
            243:'USDC_DOGE',
            244:'USDC_LTC',
            245:'USDC_ZEC',
            246:'BTC_FOAM',
            247:'USDC_FOAM',
            248:'BTC_NMR',
            249:'BTC_POLY',
            250:'BTC_LPT',
            251:'BTC_GRIN',
            252:'USDC_GRIN',
        }

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

    def private_request(self, command, req={}):
        try:
            req['command'] = command
            req['nonce'] = int(time.time()*1000000)
            post_data = urllib.parse.urlencode(req)
            sign = hmac.new(self._API_SECRET.encode(), post_data.encode(), hashlib.sha512).hexdigest()

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
        return self.private_request("cancelOrder",{'orderNumber':orderNumber})

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
            on_message = self.ws_on_message,
            on_error = self.ws_on_error,
            on_close = self.ws_on_close
        )
        self._ws.run_forever()
        self.ws_subscribe(1002)

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
            Debug: ct['Poloniex'].ws_subscribe("BTC_XMR")
        """
        self._ws.send(json.dumps({"command": "subscribe", "channel": channel }))

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
        self._ws.send(json.dumps({"command": "unsubscribe", "channel": channel }))

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
                    market_symbol = self._ws_currency_pair_map[payload[0]]
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
            if msg_code in self._ws_currency_pair_map:
                market_symbol = self._ws_currency_pair_map[msg_code]
                payload = parsed_message[2]
                if payload[0][0] == 'i':
                    self._order_book[market_symbol] = {
                        'Bids': {},
                        'Asks': {},
                    }
                    for book_update in payload[0][1]['orderBook'][1]:
                        self._order_book[market_symbol]['Bids'][float(book_update[0])] = float(book_update[1])
                    for book_update in payload[0][1]['orderBook'][0]:
                        self._order_book[market_symbol]['Asks'][float(book_update[0])] = float(book_update[1])
                    return
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
                        # best_bid = max(self._order_book[market_symbol]['Bids'].keys())
                        # best_ask = min(self._order_book[market_symbol]['Asks'].keys())
                        # if best_bid == float(book_update[2]):
                        #     print("Best Bid: {0:.8f}, {1:.8f}; Best Ask: {2:.8f}, {3:.8f}".format(
                        #         best_bid,
                        #         self._order_book[market_symbol]['Bids'][best_bid],
                        #         best_ask,
                        #         self._order_book[market_symbol]['Asks'][best_ask]
                        #     ))
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
                        print("Latest trade: ", self._recent_market_trades[market_symbol][-1])
                    return
        print(message)

    def ws_on_error(ws, error):
        print("*** Poloniex ERROR: ", error)

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
        return self._complete_balances_btc
