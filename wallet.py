"""
This is the people module and supports all the REST actions for the
people data
"""

from flask import make_response, abort, jsonify
from config import db, connex_app
from models import Wallet, WalletSchema, Account, AccountSchema \
    # , ConnectedAccount, ConnectedAccountSchema


def read_all():
    """
    This function responds to a request for /api/people
    with the complete lists of people

    :return:        json string of list of people
    """
    # Create the list of people from our data
    thewallet = Wallet.query.order_by(Wallet.name).all()
    print(thewallet)
    # Serialize the data for the response
    Wallet_schema = WalletSchema(many=True)
    data = Wallet_schema.dump(thewallet)
    return data


def read_one(wallet_id):
    """
    This function responds to a request for /api/wallet/{wallet_id}
    with one matching Wallet from people

    :param wallet_id:   Id of Wallet to find
    :return:            Wallet matching id
    """
    # Get the Wallet requested
    wallet = Wallet.query.filter(Wallet.wallet_id == wallet_id).one_or_none()

    # Did we find a Wallet?
    if wallet is not None:
        print(wallet)
        # Serialize the data for the response
        Wallet_schema = WalletSchema()
        data = Wallet_schema.dump(wallet)
        return data

    # Otherwise, nope, didn't find that Wallet
    else:
        abort(
            404,
            "Wallet not found for Id: {wallet_id}".format(wallet_id=wallet_id),
        )


def create(Wallet):
    """
    This function creates a new Wallet in the people structure
    based on the passed in Wallet data

    :param Wallet:  Wallet to create in people structure
    :return:        201 on success, 406 on Wallet exists
    """
    fname = Wallet.get("fname")
    lname = Wallet.get("lname")

    existing_Wallet = (
        Wallet.query.filter(Wallet.fname == fname)
        .filter(Wallet.lname == lname)
        .one_or_none()
    )

    # Can we insert this Wallet?
    if existing_Wallet is None:

        # Create a Wallet instance using the schema and the passed in Wallet
        schema = WalletSchema()
        new_Wallet = schema.load(Wallet, session=db.session)

        # Add the Wallet to the database
        db.session.add(new_Wallet)
        db.session.commit()

        # Serialize and return the newly created Wallet in the response
        data = schema.dump(new_Wallet)

        return data, 201

    # Otherwise, nope, Wallet exists already
    else:
        abort(
            409,
            "Wallet {fname} {lname} exists already".format(
                fname=fname, lname=lname
            ),
        )


def update(wallet_id, wallet_data):
    """
    This function updates an existing Wallet in the people structure
    Throws an error if a Wallet with the name we want to update to
    already exists in the database.

    :param wallet_id:   Id of the Wallet to update in the people structure
    :param Wallet:      Wallet to update
    :return:            updated Wallet structure
    """
    # Get the Wallet requested from the db into session
    update_Wallet = Wallet.query.filter(
        Wallet.wallet_id == wallet_id
    ).one_or_none()

    # Try to find an existing Wallet with the same name as the update
    name = wallet_data.get("name")
    address = wallet_data.get("address")

    existing_Wallet = (
        Wallet.query.filter(Wallet.name == name)
        .filter(Wallet.address == address)
        .one_or_none()
    )

    # Are we trying to find a Wallet that does not exist?
    if update_Wallet is None:
        abort(
            404,
            "Wallet not found for Id: {wallet_id}".format(wallet_id=wallet_id),
        )

    # Would our update create a duplicate of another Wallet already existing?
    elif (
        existing_Wallet is not None and existing_Wallet.wallet_id != wallet_id
    ):
        abort(
            409,
            "Wallet {name} {address} exists already".format(
                name=name, address=address
            ),
        )

    # Otherwise go ahead and update!
    else:

        # turn the passed in Wallet into a db object
        schema = WalletSchema()
        update = schema.load(Wallet, session=db.session)

        # Set the id to the Wallet we want to update
        update.wallet_id = update_Wallet.wallet_id

        # merge the new object into the old and commit it to the db
        db.session.merge(update)
        db.session.commit()

        # return updated Wallet in the response
        data = schema.dump(update_Wallet)

        return data, 200


def delete(wallet_id):
    """
    This function deletes a Wallet from the people structure

    :param wallet_id:   Id of the Wallet to delete
    :return:            200 on successful delete, 404 if not found
    """
    # Get the Wallet requested
    wallet = Wallet.query.filter(Wallet.wallet_id == wallet_id).one_or_none()

    # Did we find a Wallet?
    if wallet is not None:
        db.session.delete(Wallet)
        db.session.commit()
        return make_response(
            "Wallet {wallet_id} deleted".format(wallet_id=wallet_id), 200
        )

    # Otherwise, nope, didn't find that Wallet
    else:
        abort(
            404,
            "Wallet not found for Id: {wallet_id}".format(wallet_id=wallet_id),
        )



def addaccount(wallet_id, account_id):
    """
    This function updates an existing Wallet in the people structure
    Throws an error if a Wallet with the name we want to update to
    already exists in the database.

    :param wallet_id:   Id of the Wallet to update in the people structure
    :param Wallet:      Wallet to update
    :return:            updated Wallet structure
    """
    # Get the Wallet requested from the db into session
    update_Wallet = Wallet.query.filter(
        Wallet.wallet_id == wallet_id
    ).one_or_none()


    account = Account.query.filter(
        Account.account_id == account_id
    ).one_or_none()




    # Are we trying to find a Wallet that does not exist?
    if update_Wallet is None :
        abort(
            404,
            "Wallet not found for Id: {wallet_id}".format(wallet_id=wallet_id),
        )


    # Would our update create a duplicate of another Wallet already existing?
    elif ( account is None):
        abort(
            409,
            "account  {account_id} not found ".format(
                account_id=account_id
            ),
        )

    # Otherwise go ahead and update!
    else:



        # # turn the passed in Wallet into a db object
        schema = WalletSchema()
        # update = schema.load(jsonify(('wallet_id' ,wallet_id)), session=db.session)

        # Set the id to the Wallet we want to update
        # update.wallet_id = update_Wallet.wallet_id
        # update.accounts = update_Wallet.accounts
        # update_Wallet.addAccount(account)
        # update.name = update_Wallet.name
        # update.address = update_Wallet.address

        update_Wallet.addAccount(account)

        # merge the new object into the old and commit it to the db
        db.session.merge(update_Wallet)
        db.session.commit()

        # return updated Wallet in the response
        data = schema.dump(update_Wallet)

        return data, 200


def removeaccount(wallet_id, account_id):
    """
    This function updates an existing Wallet in the people structure
    Throws an error if a Wallet with the name we want to update to
    already exists in the database.

    :param wallet_id:   Id of the Wallet to update in the people structure
    :param Wallet:      Wallet to update
    :return:            updated Wallet structure
    """
    # Get the Wallet requested from the db into session
    update_Wallet = Wallet.query.filter(
        Wallet.wallet_id == wallet_id
    ).one_or_none()

    account = Account.query.filter(
        Account.account_id == account_id
    ).one_or_none()

    # Are we trying to find a Wallet that does not exist?
    if update_Wallet is None:
        abort(
            404,
            "Wallet not found for Id: {wallet_id}".format(wallet_id=wallet_id),
        )


    # Would our update create a duplicate of another Wallet already existing?
    elif (account is None) or (account not in update_Wallet.accounts) :
        abort(
            409,
            "account  {account_id} not found ".format(
                account_id=account_id
            ),
        )

    # Otherwise go ahead and update!
    else:

        # turn the passed in Wallet into a db object
        schema = WalletSchema()
        # update = schema.load(Wallet, session=db.session)

        # Set the id to the Wallet we want to update
        # update.wallet_id = update_Wallet.wallet_id
        # update.accounts = update_Wallet.accounts
        update_Wallet.removeAccount(account)
        # update.name = update_Wallet.name
        # update.address = update_Wallet.address

        # merge the new object into the old and commit it to the db
        db.session.merge(update_Wallet)
        db.session.commit()

        # return updated Wallet in the response
        data = schema.dump(update_Wallet)

        return data, 200


def getaccounts(wallet_id):
    """
    This function responds to a request for /api/wallet/{wallet_id}
    with one matching Wallet from people

    :param wallet_id:   Id of Wallet to find
    :return:            Wallet matching id
    """
    # Get the Wallet requested
    wallet = Wallet.query.filter(Wallet.wallet_id == wallet_id).one_or_none()

    # Did we find a Wallet?
    if wallet is not None:
        print('accounts:',wallet.accounts)
        # Serialize the data for the response
        wallet_schema = WalletSchema()
        data = wallet_schema.dump(wallet.accounts)
        return data
        # return jsonify({wallet.accounts})

    # Otherwise, nope, didn't find that Wallet
    else:
        abort(
            404,
            "Wallet not found for Id: {wallet_id}".format(wallet_id=wallet_id),
        )


