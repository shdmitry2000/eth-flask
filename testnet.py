import asyncio
import json
from web3 import Web3
from web3.auto import w3
from eth_account import Account
import secrets
import json
from pprint import pprint
import sys

network='5777'

def printkeyfile(file):
    json_data = open(file).read()
    data = json.loads(json_data)
    print('data', data['addresses'])
    for a in data['addresses']:
        prkeyArray = data['addresses'][a]['secretKey']['data']
        pubkeyArray = data['addresses'][a]['publicKey']['data']
        prKey=""
        pubkey = ""
        for prk in prkeyArray:
            prKey = "%s%02x" % (prKey, prk)
        print
        for pbk in pubkeyArray:
            pubkey = "%s%02x" % (pubkey, pbk)
        print
        print("Address:%s" % a)

        print("Public Key:0x%s" % pubkey)


        print("Private Key:0x%s" % prKey)

        # "Private Key:0x%s" % data['private_keys'][a]


def use_erc20_tocken(tockenaddress=None):
    with open("./abis/BnhpTokenMock.json") as f:
        info_json = json.load(f)
    abi = info_json["abi"]
    tockenaddress = info_json["networks"][network]['address']
    print(tockenaddress)
    escrow = w3.eth.contract(address=tockenaddress, abi=abi)
    return escrow

def read_all():
    """
    This function responds to a request for /api/accounts
    with the complete lists of token

    :return:        json string of list of acounts
    """
    accounts = w3.eth.accounts
    return accounts

def balance(account_address):
    # account_id='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
    balance=w3.eth.get_balance(account_address)
    # w3.toWei(Decimal('0.000000005'), 'ether')
    return  balance

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


# define function to handle events and print to the console
def handle_event(event):
    evjson=w3.toJSON(event)
    print(evjson)
    return evjson


# asynchronous defined function to loop
# this loop sets up an event filter and is looking for new entires for the "PairCreated" event
# this loop runs on a poll interval
async def log_loop(event_filter, poll_interval):
    while True:
        for PairCreated in event_filter.get_new_entries():
            handle_event(PairCreated)
        await asyncio.sleep(poll_interval)



def events(token_id,account_address):

        events_filter = use_erc20_tocken().events.Transfer.createFilter(fromBlock=0, toBlock='latest',
                                                      argument_filters={"from":  account_address})

        # for event in events.get_new_entries():
        #     print('event',handle_event(event))
        print('events')
        print(w3.eth.get_filter_logs(events_filter.filter_id))
        # for event in events.get_all_entries():
        #     handle_event(event)

        return w3.eth.get_filter_logs(events_filter.filter_id)
def createprkey():
    priv = secrets.token_hex(32)
    return  "0x" + priv


def createaccount():
    private_key=createprkey()
    print("SAVE BUT DO NOT SHARE THIS:", private_key)
    acct = Account.from_key(private_key)
    print("Address:", acct.address)
    return acct.address


def transaction(account_1='',private_key1='',account_2='',ammount=1):
    # account_1 = 'INPUTACCOUNT1'
    # private_key1 = 'INPUTPRIVATEKEY'
    # account_2 = 'INPUTACCOUNT2'

    # get the nonce.  Prevents one from sending the transaction twice
    nonce = w3.eth.getTransactionCount(account_1)

    # build a transaction in a dictionary
    tx = {
        'nonce': nonce,
        'to': account_2,
        'value': w3.toWei(ammount, 'ether'),
        'gas': 2000000,
        'gasPrice': w3.toWei('50', 'gwei')
    }

    # sign the transaction
    signed_tx = w3.eth.account.sign_transaction(tx, private_key1)

    # send transaction
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

    # get transaction hash
    return w3.toHex(tx_hash)
def tokenbalance(token_id,account_address):
    my_token_contract = use_erc20_tocken()

    try:
        return my_token_contract.functions.balanceOf(account_address).call({"from": account_address});
    except:
        print("An exception occurred")

def balance(account_address):
    # account_id='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
    balance=w3.eth.get_balance(account_address)
    # w3.toWei(Decimal('0.000000005'), 'ether')

    return  balance

if __name__ == '__main__':
    # (0)
    # 0x4942023A414DD30D95130bc624b8bc44bCEDB7c0(100000000000000000000
    # ETH)
    # (1)
    # 0x8b8Ce14490057e48f4f5bf315aAf41A4edd53C30(100000000000000000000
    # ETH)
    # (2)
    # 0xE03B905d149A536Ecec1d957C21d1426CbC7f3D5(100000000000000000000
    # ETH)
    # (3)
    # 0x29aB465D7131f7F7409A12457048b6542F1cB165(100000000000000000000
    # ETH)
    # (4)
    # 0x793fFAa313A2c1E061E81f1593088E592e993092(100000000000000000000
    # ETH)
    # (5)
    # 0x2078f1144A29A84B5a26d5bEeF6C5f3b5E112603(100000000000000000000
    # ETH)
    # (6)
    # 0x336bb81d2753793454785b3243F497fc0a7Feba1(100000000000000000000
    # ETH)
    # (7)
    # 0xB0e8Ec60CCc64748a26a81c9d3110489Ec472897(100000000000000000000
    # ETH)
    # (8)
    # 0xd418efc638d58Dc50338409DfEa06f9278f62B1C(100000000000000000000
    # ETH)
    # (9)
    # 0xc8d7ba1B7dFFab638F6C04800dbd4418395c51B0(100000000000000000000
    # ETH)
    #
    # Private
    # Keys
    # == == == == == == == == ==
    # (0)
    # 0x24833e072def790b5351c48bcc6ec724509bcb1f7d9786f536821aed6fd45bf6
    # (1)
    # 0x83603e3b938f0c47b59b007d10ee488f4b9af82a6708441ae2d49d0653381915
    # (2)
    # 0x77f852bd11d5dde51e1dcb05e1a77fca82e5bf5874dd7c6cd521e39d1370c102
    # (3)
    # 0x3f879352b7347d47fa3cb92113d3a938a47cfed1cadf3ba9a21fabafd6b7a2bb
    # (4)
    # 0x7c9a194faa5e6274a12241e03432b92cc2cd10cdbc08afa822bcefae5a45264e
    # (5)
    # 0xd2051d64914fa436f2c4b704e338fc428d089ac590033eb129cd284478e21f00
    # (6)
    # 0x22ec9d67b9f6fdc783dd1d19d03955f7ea1921ca80c48e6630ad17891594cbca
    # (7)
    # 0x6f6490d1b691371ee2595431e86147de40be386deac71cfdf135f8cca166b666
    # (8)
    # 0x3c393ad535938d5bc75a1966bfc3b358eea89cadf4852f434f90ecabcc5f9dab
    # (9)
    # 0x3cffcb4ffc5ac1f04b9087bcf7c6c0ca5e48f68bac5821de552e55565a708380

    account='0x4942023A414DD30D95130bc624b8bc44bCEDB7c0'
    account_pk='0x24833e072def790b5351c48bcc6ec724509bcb1f7d9786f536821aed6fd45bf6'
    print('account balance ',balance(w3.toChecksumAddress (account)))

    print(transaction(w3.toChecksumAddress(account),
                      account_pk,
                      w3.toChecksumAddress('0x8b8Ce14490057e48f4f5bf315aAf41A4edd53C30'), 15))

    print('account balance ', balance(w3.toChecksumAddress(account)))


    # tockenaddress='0x1C1D2F7f7865178dc9086399dcE23bc10d1E00D2'
    # print (events(tockenaddress,account))
    # print('tockenaddress', tockenaddress)
    # my_token_contract = use_erc20_tocken(tockenaddress)
    # # account = '0x9bcf0dfF6b395520609384e48e28Ea845Cb98f0F'
    # print('token_contract', my_token_contract)
    # print('tokenbalance',tokenbalance(1,account))
    # events = my_token_contract.events.Transfer.createFilter(fromBlock=0, toBlock='latest',
    #                                               argument_filters={"from": account})
    #
    # # print(createaccount())
    # print(read_all())
    # printkeyfile('/Users/dmitryshlymovich/workspace/ethereum-bnhp-wallet/ganache-accounts.json')
    # print('accountbalance', balance(w3.toChecksumAddress ("0xfb83e3f60b39b1b96c18bb7b195ad3db3d9f4f5e")))

# print(transaction('0x761C302a73BE6a883b1693D04fEA1a0f8759BFF3','0x5dee75052c8c2e2c5ba017282c84b6696643e286dd2d33179c709d6fe1b540f5','0x9bcf0dfF6b395520609384e48e28Ea845Cb98f0F',1))


    # allacc=read_all()
    # for account in allacc:


    # print(balance(account))
    # transfer_filter = my_token_contract.events.Transfer.createFilter(fromBlock="0x0", argument_filters={'from': account})
    # print('events', transfer_filter.get_new_entries())


