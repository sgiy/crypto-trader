# Crypto-Trader

The goal of this project is to create an open, usable interface enabling simultaneous trading on multiple exchanges, aggregation of personal balances, and calculation of realized gains (this does not constitute legal or tax advise. Make sure that calculation makes sense to you before using it).

Using the GUI requires user to create API keys for each of the exchanges and to input them in program's configuration. The source code of the program has to be open to enable user to audit the code before using it to make sure that the api keys and the secrets are used only in the manner specified by the relevant exchange and are not accessible to third parties. It is recommended that the exchange API keys are created only with access to trading capabilities, but are not allowed to withdraw currency in order to limit user's exposure in case the keys compromised. Additionally, it is recommended limiting api access to user's ip address if possible in exchange account - this provides additional protection to the funds.

The project is currently far from the release, but you are welcome to try what is already written and to submit your suggestions.
