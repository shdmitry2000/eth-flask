"""
This is the token module and supports all the REST actions for the
token data
"""
import asyncio
import json

from web3._utils.filters import LogFilter

import accounts
from config import w3, network

from flask import make_response, abort
from config import db
from models import ERC20Token, ERC20TokenSchema, Account


def use_erc20_tocken(token_address=None):
    abis = "./abis/BnhpTokenMock.json"
    with open(abis) as f:
        info_json = json.load(f)
    abi = info_json["abi"]
    if (token_address is None):
        # print(info_json["networks"])
        token_address = info_json["networks"][network]['address']

    try:
        escrow = w3.eth.contract(address=token_address, abi=abi)
        return escrow
    except:
        raise Exception("Sorry, can't load erc20 token propertly!")



def read_all():
    """
    This function responds to a request for /api/token
    with the complete lists of token

    :return:        json string of list of token
    """
    # Create the list of token from our data
    token = ERC20Token.query.order_by(ERC20Token.address).all()

    # Serialize the data for the response
    token_schema = ERC20TokenSchema(many=True)
    data = token_schema.dump(token)
    return data


def read_one(token_id):
    """
    This function responds to a request for /api/token/{token_id}
    with one matching token from tokens

    :param token_id:   Id of token to find
    :return:            token matching id
    """
    # Get the token requested
    token = ERC20Token.query.filter(ERC20Token.token_id == token_id).one_or_none()

    # Did we find a token?
    if token is not None:

        # Serialize the data for the response
        token_schema = ERC20TokenSchema()
        data = token_schema.dump(token)
        return data

    # Otherwise, nope, didn't find that token
    else:
        abort(
            404,
            "Token not found for Id: {token_id}".format(token_id=token_id),
        )


def create(token):
    """
    This function creates a new token in the token structure
    based on the passed in token data

    :param token:  token to create in token structure
    :return:        201 on success, 406 on token exists
    """
    address = token.get("address")
    symbol = token.get("symbol")
    decimal=token.get("decimal")

    existing_token = (
        ERC20Token.query.filter(ERC20Token.address == address)
        .filter(ERC20Token.address == address)
        .one_or_none()
    )

    # Can we insert this token?
    if existing_token is None:

        # Create a token instance using the schema and the passed in token
        schema = ERC20TokenSchema()
        new_token = schema.load(token, session=db.session)

        # Add the token to the database
        db.session.add(new_token)
        db.session.commit()

        # Serialize and return the newly created token in the response
        data = schema.dump(new_token)

        return data, 201

    # Otherwise, nope, token exists already
    else:
        abort(
            409,
            "Token {address}  exists already".format(
                address=address
            ),
        )


def update(token_id, token):
    """
    This function updates an existing token in the token structure
    Throws an error if a token with the name we want to update to
    already exists in the database.

    :param tokenn_id:   Id of the token to update in the token structure
    :param token:      token to update
    :return:            updated token structure
    """
    # Get the token requested from the db into session
    update_token = ERC20Token.query.filter(
        ERC20Token.token_id == token_id
    ).one_or_none()

    # Try to find an existing token with the same name as the update
    address = token.get("address")
    symbol = token.get("symbol")
    decimal = token.get("decimal")

    existing_token = (
        ERC20Token.query.filter(ERC20Token.address == address)
        .one_or_none()
    )

    # Are we trying to find a token that does not exist?
    if update_token is None:
        abort(
            404,
            "Token not found for Id: {token_id}".format(tokenn_id=token_id),
        )

    # Would our update create a duplicate of another token already existing?
    elif (
        existing_token is not None and existing_token.token_id != token_id
    ):
        abort(
            409,
            "token {address}  exists already".format(
                address=address
            ),
        )

    # Otherwise go ahead and update!
    else:

        # turn the passed in token into a db object
        schema = ERC20TokenSchema()
        update = schema.load(token, session=db.session)

        # Set the id to the token we want to update
        update.token_id = update_token.token_id

        # merge the new object into the old and commit it to the db
        db.session.merge(update)
        db.session.commit()

        # return updated token in the response
        data = schema.dump(update_token)

        return data, 200


def delete(token_id):
    """
    This function deletes a token from the token structure

    :param token_id:   Id of the token to delete
    :return:            200 on successful delete, 404 if not found
    """
    # Get the token requested
    token = ERC20Token.query.filter(ERC20Token.token_id == token_id).one_or_none()

    # Did we find a token?
    if token is not None:
        db.session.delete(token)
        db.session.commit()
        return make_response(
            "token {token_id} deleted".format(token_id=token_id), 200
        )

    # Otherwise, nope, didn't find that token
    else:
        abort(
            404,
            "token not found for Id: {token_id}".format(token_id=token_id),
        )


# define function to handle events and print to the console
def handle_event(event):
    evjson=w3.toJSON(event)
    return evjson


# asynchronous defined function to loop
# this loop sets up an event filter and is looking for new entires for the "PairCreated" event
# this loop runs on a poll interval
async def log_loop(event_filter, poll_interval):
    while True:
        for PairCreated in event_filter.get_new_entries():
            handle_event(PairCreated)
        await asyncio.sleep(poll_interval)



def events(token_address,account_address):


        events_filter = use_erc20_tocken().events.Transfer.createFilter(fromBlock=0, toBlock='latest',
                                                      argument_filters={"from":  account_address})

        filterlog= w3.eth.get_filter_logs(events_filter.filter_id)
        return str(filterlog)


def eventsbyid(token_id, account_id):
    tocken_address = read_one(token_id).get('address')
    payyer_acount = accounts.read_one(account_id)

    return events(tocken_address,payyer_acount.get('address'))


def balance(token_address,account_address):
    my_token_contract = use_erc20_tocken()

    try:
        return my_token_contract.functions.balanceOf(account_address).call({"from": account_address});
    except:
        print("An exception occurred")


def balancebyid(token_id,account_id):
    tocken_address = read_one(token_id).get('address')
    account_address=accounts.read_one(account_id).get('address')

    return balance(tocken_address,account_address)

def transfer(tocken_address, payer_address, private_key_from_account, recipient_address, ammount):
    # When running locally, execute the statements found in the file linked below to load the EIP20_ABI variable.
    # See: https://github.com/carver/ethtoken.py/blob/v0.0.1-alpha.4/ethtoken/abi.py
    unicorns = use_erc20_tocken()

    nonce = w3.eth.getTransactionCount(payer_address)

    tx = unicorns.functions.transfer(recipient_address, ammount).buildTransaction(
        {'from': payer_address, 'gas': 70000, 'gasPrice': w3.toWei('1', 'gwei'), 'nonce': nonce})

    # sign the transaction
    signed_tx = w3.eth.account.sign_transaction(tx, private_key_from_account)

    # send transaction
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

    # get transaction hash
    return w3.toHex(tx_hash)




def transferbyid(token_id,payer_id,recipient_id,ammount):
    # When running locally, execute the statements found in the file linked below to load the EIP20_ABI variable.
    # See: https://github.com/carver/ethtoken.py/blob/v0.0.1-alpha.4/ethtoken/abi.py
    tocken_address = read_one(token_id).get('address')
    payyer_acount=accounts.read_one(payer_id)
    recipient_account=accounts.read_one(recipient_id)
    return transfer(tocken_address, payyer_acount.get('address'), payyer_acount.get('pk'), recipient_account.get('address'), ammount)





def transferNode(tocken_address, payer_address, recipient_address, amount):

    unicorns = use_erc20_tocken()

    tx_hash = unicorns.functions.transfer(recipient_address, amount).transact({'from': payer_address})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash

def transferNodebyid(tocken_id, payer_id, recipient_id, amount):
    tocken_address = read_one(tocken_id).get('address')
    payyer_acount = accounts.read_one(payer_id)
    recipient_account = accounts.read_one(recipient_id)

    return transferNode(tocken_address,payyer_acount.get('address'),recipient_account.get('address'),amount)

def allowance(tocken_address,payer_address='',recipient_address=''):

    my_token_contract = use_erc20_tocken()
    return my_token_contract.functions.allowance(recipient_address, payer_address).call({'from': payer_address})

def allowancebyid(tocken_id,payer_id,recipient_id):
    tocken_address = read_one(tocken_id).get('address')
    payyer_acount = accounts.read_one(payer_id)
    recipient_account = accounts.read_one(recipient_id)


    return allowance(tocken_address, payyer_acount.get('address'), recipient_account.get('address'))






def approve(tocken_address, payer_address, private_key_from_account, recipient_address, ammount):
    # When running locally, execute the statements found in the file linked below to load the EIP20_ABI variable.
    # See: https://github.com/carver/ethtoken.py/blob/v0.0.1-alpha.4/ethtoken/abi.py
    unicorns = use_erc20_tocken()

    nonce = w3.eth.getTransactionCount(payer_address)

    tx = unicorns.functions.approve(recipient_address, ammount).buildTransaction(
        {'from': payer_address, 'gas': 70000, 'gasPrice': w3.toWei('1', 'gwei'), 'nonce': nonce})

    # sign the transaction
    signed_tx = w3.eth.account.sign_transaction(tx, private_key_from_account)

    # send transaction
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

    # get transaction hash
    return w3.toHex(tx_hash)

def approvebyid(tocken_id,payer_id,recipient_id,ammount=0):
    tocken_address = read_one(tocken_id).get('address')
    payyer_acount = accounts.read_one(payer_id)
    recipient_account = accounts.read_one(recipient_id)

    return approve(tocken_address,payyer_acount.get('address'), payyer_acount.get('pk'),recipient_account.get('address') ,ammount)


def approveNode(tocken_address,payer_address='',recipient_address='',amount=0):

    my_token_contract = use_erc20_tocken()
    tx_hash = my_token_contract.functions.approve(recipient_address, amount).transact({'from': payer_address})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt


def externaltransfer(token_address, payer_address='', private_key_from_account='', recipient_address='', ammount=0):
    # When running locally, execute the statements found in the file linked below to load the EIP20_ABI variable.
    # See: https://github.com/carver/ethtoken.py/blob/v0.0.1-alpha.4/ethtoken/abi.py
    unicorns = use_erc20_tocken()

    nonce = w3.eth.getTransactionCount(payer_address)

    tx = unicorns.functions.transferFrom(payer_address, recipient_address, ammount).buildTransaction(
        {'from': payer_address, 'gas': 70000, 'gasPrice': w3.toWei('1', 'gwei'), 'nonce': nonce})

    # sign the transaction
    signed_tx = w3.eth.account.sign_transaction(tx, private_key_from_account)

    # send transaction
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

    # get transaction hash
    return w3.toHex(tx_hash)



def externaltransferNode(token_address,payer_address='',recipient_address='',ammount=0):

    my_token_contract = use_erc20_tocken()
    tx_hash = my_token_contract.functions.transferFrom(payer_address, recipient_address, ammount)\
        .transact({'from': recipient_address})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt





def externaltransferbyid(token_id,payer_id,recipient_id,ammount):
    tocken_address = read_one(token_id).get('address')
    payyer_acount = accounts.read_one(payer_id)
    recipient_account = accounts    .read_one(recipient_id)

    return externaltransfer(tocken_address,payyer_acount.get('address'), payyer_acount.get('pk'),recipient_account.get('address'),ammount)
