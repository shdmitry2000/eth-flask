import json
# from eth_account import Account

import secrets

import eth_account

import models
from config import db

from flask import make_response, abort, jsonify
# from config import db
# from models import ERC20Token, ERC20TokenSchema
from numpy.lib.format import magic

from config import w3
from models import AccountSchema,Account


def check():
    block=w3.eth.get_block('latest')
    # print(block)

    return  str(block)


def read_all():
    """
   This function responds to a request for /api/people
   with the complete lists of people

   :return:        json string of list of people
   """
    # Create the list of people from our data


    accounts = Account.query.order_by(Account.account_id).all()

    # Serialize the data for the response
    accounts_schema = AccountSchema(many=True)
    data = accounts_schema.dump(accounts)
    return data

def read_one(account_id):
    """
    This function responds to a request for /api/people/{person_id}
    with one matching person from people

    :param person_id:   Id of person to find
    :return:            person matching id
    """
    # Get the person requested
    account = Account.query.filter(Account.account_id == account_id).one_or_none()

    # Did we find a person?
    if account is not None:

        # Serialize the data for the response
        account_schema = AccountSchema()
        data = account_schema.dump(account)
        return data

    # Otherwise, nope, didn't find that person
    else:
        abort(
            404,
            "Account not found for Id: {Account_id}".format(Account_id=account_id),
        )


def eth_get_all():
    """
    This function responds to a request for /api/accounts
    with the complete lists of token

    :return:        json string of list of acounts
    """
    accounts = w3.eth.accounts
    print(accounts)
    return accounts

def createprkey():
    priv = secrets.token_hex(32)
    return  "0x" + priv


def create():
    private_key = createprkey()
    print("SAVE BUT DO NOT SHARE THIS:", private_key)
    newaccount = eth_account.Account.from_key(private_key)
    print("Address:", newaccount.address)

    existing_account = (
        Account.query.filter(Account.address == newaccount.address)
            .one_or_none()
    )

    # Can we insert this account?
    if existing_account is None:

        schema = AccountSchema()

        # Create a person instance using the schema and the passed in person
        new_Account = Account(newaccount.address,
                               newaccount.privateKey)

        # Add the account to the database
        db.session.add(new_Account)
        db.session.commit()

        # Serialize and return the newly created person in the response
        data = schema.dump(new_Account)

        return data, 201

    # Otherwise, nope, person exists already
    else:
        abort(
            409,
            "Person {address}  exists already".format(
                address=newaccount.address
            ),
        )

    return newaccount.address

def getAddress(account_id):
    sellected_account =read_one(account_id)
    return sellected_account.address



def delete(account_id):
    """
    This function deletes a person from the people structure

    :param person_id:   Id of the person to delete
    :return:            200 on successful delete, 404 if not found
    """
    # Get the person requested
    sellected_account = Account.query.filter(Account.account_id == account_id).one_or_none()

    # Did we find a person?
    if sellected_account is not None:
        db.session.delete(sellected_account)
        db.session.commit()
        return make_response(
            "account {account_id} deleted".format(account_id=account_id), 200
        )

    # Otherwise, nope, didn't find that person
    else:
        abort(
            404,
            "Account not found for Id: {Account_id}".format(Account_id=account_id),
        )

def balance(account_address):
    # account_id='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
    balance=w3.eth.get_balance(account_address)
    # w3.toWei(Decimal('0.000000005'), 'ether')

    return  balance

def balancebyid(account_id):
    sellected_account =read_one(account_id)
    account_address = sellected_account.get('address')
    return  balance(account_address)

def transaction(payer_address,payer_private_key,reciver_address,ammount):

    # get the nonce.  Prevents one from sending the transaction twice
    nonce = w3.eth.getTransactionCount(payer_address)

    # build a transaction in a dictionary
    tx = {
        'nonce': nonce,
        'to': reciver_address,
        'value': w3.toWei(ammount, 'ether'),
        'gas': 2000000,
        'gasPrice': w3.toWei('50', 'gwei')
    }

    # sign the transaction
    signed_tx = w3.eth.account.sign_transaction(tx, payer_private_key)

    # send transaction
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

    # get transaction hash
    return w3.toHex(tx_hash)


def transactionbyid(payer_id,recipient_id,ammount=0):
    sellected_payer_account = read_one(payer_id)
    sellected_recipient_account = read_one(recipient_id)

    payer_address = sellected_payer_account.get('address')
    payer_pk = sellected_payer_account.get('pk')
    recipient_address=sellected_recipient_account.get('address')
    return transaction( payer_address, payer_pk, recipient_address, ammount)
