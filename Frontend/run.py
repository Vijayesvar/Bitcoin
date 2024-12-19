import sys
import os

# Add the absolute path of the project to sys.path dynamically
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, request
from client.btc import SendBTC
from backend.core.transaction import Tx

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def wallet():
    message = ""
    if request.method == "POST":
        FromAddress = request.form.get("fromAddress")
        ToAddress = request.form.get("toAddress")
        Amount = request.form.get("Amount", type=int)
        sendCoin = SendBTC(FromAddress, ToAddress, Amount, UTXOS)
        TxObj = sendCoin.prepareTransaction()

        script_pubkey = sendCoin.scriptPubKey(FromAddress)
        verified = True

        if not TxObj:
           message = "Invalid Transaction"

        if isinstance(TxObj,Tx):
            for index, tx in enumerate(TxObj.tx_ins):
                if not TxObj.verify_input(index, script_pubkey):
                    verified = False

            if verified:
                Mempool[TxObj.TxId] = TxObj
                message = "Transaction added in mempool"             

    return render_template("wallet.html", message=message)


def main(utxos, mempool ):
    global UTXOS
    global Mempool
    Mempool = mempool
    UTXOS = utxos
    app.run()
