# Crypto-Trader

The goal of this project is to create an open, usable interface enabling
simultaneous trading on multiple exchanges, aggregation of personal balances,
and calculation of realized gains (this does not constitute legal or tax advise.
Make sure that calculation makes sense to you before using it).

Using the GUI for trading on exchanges requires user to create API keys for
those exchanges and to input them in program's configuration. The source code of
the program has to be open to enable user code audit to make sure that the api
keys and the secrets are used only in the manner specified by the relevant
exchange and are not accessible to third parties. If you do not plan to use the
GUI to submit withdrawal request, then is recommended that the exchange API keys
are created with access only to trading. Additionally, it is recommended
limiting api access to user's ip address if possible in exchange account - this
provides additional protection to the funds.

The project is currently not ready for release, but you are welcome to try what
is already written (real-time arbitrage checks) and to submit your suggestions.
