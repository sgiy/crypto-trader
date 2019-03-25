# Crypto-Trader

The goal of this project is to create an intuitive interface simplifying
simultaneous usage of multiple crypto exchanges. For example, it shows
aggregated balances across exchanges. As an additional benefit (that is
already available), you can monitor arbitrage opportunities across exchanges.
This project and information obtained using it does not constitute an investment
advise. Use at your own risk.

Using the GUI for trading on exchanges requires user to create API keys for
those exchanges and to input them in program's configuration. The API keys are
then stored in an encrypted file on user's computer and not in any third-party
database. The source code of the program has to be open to enable user code
audit to make sure that the api keys are used only in the manner specified by
the relevant exchange and are not accessible to any third parties.

* If you do not plan to use the GUI to submit withdrawal requests, then is
recommended that the exchange API keys are created with access only to trading.
Additionally, it is recommended limiting api access to user's ip address if
possible in exchange account - this provides additional protection to the funds
in case user's computer is compromised.

The project is not yet ready for release, but you are welcome to use what is
already written and to submit your suggestions.

## If you like the project, please consider participating and/or donating:

**BTC**: 39qHV6AVQMxynRx6kRQVD9R4PrkyQKxPhK

**XMR**: 47ovgSMzsfQhhcTANJ6pPQfES2MrPG6btU4KY3fBo89q2qVkc1AGy8jFHUMxv9qjzPWkaWEywfgtWKV5katXJLapM5CHuhC

## Currently implemented views:
- Balances - Shows aggregate balances in BTC and USD terms across exchanges.
- Market - shows exchange order book, chart, and allows trade execution
- 24-Hour Market Moves - shows sorted currency moves over past 24 hours
- Cross Exchange Arbitrage - Shows current cross exchange arbitrage
    opportunities (Cross exchange arbitrage represents cases where one can buy
    pair on one exchange at a lower price than they can sell on another
    exchange).
- Circle Exchange Arbitrage - Shows current circle arbitrage opportunities
    (Circle arbitrage represents cases where on the same exchange one can
    use currency A to buy currency B, then use currency B to buy currency C,
    only to then buy currency A with currency C in a way that results in a
    greater amount of currency A than the user started with).

## To run the project
Make sue you have pipenv installed (it's a python packaging suite)
```
pip install pipenv
```

Run in the project's python3 directory the following command that installs a
separate virtual environment for packages needed by this project in a way that
does not interfere with your current python installation.
```
pipenv install
```

Execute the following command line to run the project.
```
pipenv run python main.py
```

## Current Status of Exchange API Wrappers

| Exchange | Public REST API | Private REST API | Websockets | Comments |
| -------- | --------------- | ---------------- | ---------- | -------- |
| Binance  | Good            | Good             | NI         | -------- |
| Bittrex  | Good            | Good             | NI         | -------- |
| Hotbit   | Good            | NA               | NI         | -------- |
| Kucoin   | Good            | Good             | NI         | -------- |
| Poloniex | Good            | Good             | Good       | -------- |

- NR - Needs review (and development)
- NI - Not implemented (yet)
- NA - Not Available. Exchange does not have specific API (e.g. websockets)
