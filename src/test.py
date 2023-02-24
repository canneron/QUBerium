from wallet import Wallet
from transaction import Transaction
import requests

if __name__ == '__main__':

    bob = Wallet()
    bob.balance = 1000
    alice = Wallet()
    exchange = Wallet()

    transaction = exchange.createTransaction(
        alice.pubKey, 10, 'RECORD')

    url = "http://localhost:5004/transaction"
    t = Transaction(bob.pubKey, alice.pubKey, 10, "RECORD")
    tmsh = t.toJson()
    package = {'transaction': tmsh}
    request = requests.post(url, json=package)
    print(request.text)