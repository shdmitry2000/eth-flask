from datetime import datetime

from marshmallow import fields
from sqlalchemy import PrimaryKeyConstraint
from config import db, ma


import datetime
from werkzeug.security import generate_password_hash, \
     check_password_hash


class Account(db.Model):
    __tablename__ = "account"
    account_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    address = db.Column(db.String(42))
    pk = db.Column(db.String(60))
    timestamp = db.Column(
        db.DateTime, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow()
    )

    # wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.wallet_id'))
    PrimaryKeyConstraint('address', name='address_pk')

    def __init__(self, address, pk):
        self.address = address
        self.pk=pk

    def __repr__(self):
        return '<account %r>' % self.address

    # def setwalletid(self,wallet_id):
    #     self.wallet_id = wallet_id


class AccountSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Account
        # sqla_session = db.session
        load_instance = True


ConnectedAccount = db.Table('association', db.metadata, #Base.metadata,
    db.Column('wallet_id', db.ForeignKey('wallet.wallet_id')),
    db.Column('account_id', db.ForeignKey('account.account_id'))
)
# class ConnectedAccount(db.Model):
#     __tablename__ = "connectedaccount"
#     id = db.Column(db.Integer, primary_key=True)
#     wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.wallet_id'))
#     account_id = db.Column(db.Integer, db.ForeignKey('account.account_id'))
#
#
#     def __init__(self, wallet_id, account_id):
#         self.wallet_id = wallet_id
#         self.account_id = account_id
#
#     def __repr__(self):
#         return '<ConnectedAccount id: %r wallet id: %r account id: %r>' % (self.id , self.wallet_id,self.account_id)
#
# class ConnectedAccountSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = ConnectedAccount
#         # sqla_session = db.session
#         load_instance = True
#



class Wallet(db.Model):
    __tablename__ = "wallet"
    wallet_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32))
    address = db.Column(db.String(32))

    # account_id = db.Column(db.Integer, db.ForeignKey('account.account_id'))
    # backref="wallet"
    #back_populates = "wallet",
    accounts = db.relationship("Account",secondary=ConnectedAccount, uselist=True)

    timestamp = db.Column(
        db.DateTime, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow()
    )



    # # person = db.relationship("Person", back_populates="wallet")
    # # accounts = db.relationship('Account', cascade="all,delete", backref=db.backref('account', lazy='joined'), lazy='dynamic')
    # PrimaryKeyConstraint('wallet_id', 'name', name='Wallet_pk')

    def __init__(self, name,accounts=None, *args, **kwargs):
        super(Wallet, self).__init__(*args, **kwargs)
        self.name = name
        accounts = accounts or []
        for account in accounts:
            self.addAccount(account)
            # self.accounts.append(account)

    # def __init__(self, name,account_id=None):
    #     self.name = name
    #     self.account_id=account_id

    def addAccount(self,account):
        self.accounts.append(account)

    def removeAccount(self,account):
        self.accounts.remove(account)

    def __repr__(self):
        return '<wallet %r account %r>' % (self.name,self.accounts)


class WalletSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Wallet
        # sqla_session = db.session
        load_instance = True

    accounts = fields.Nested(AccountSchema, many=True)

class Person(db.Model):
    __tablename__ = "person"
    person_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lname = db.Column(db.String(32))
    fname = db.Column(db.String(32))
    timestamp = db.Column(
        db.DateTime, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow()
    )
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.wallet_id'))

    # wallet_id = db.Column(db.Integer)

    wallets = fields.Nested(WalletSchema, many=True)
    # wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.wallet_id'))

    # wallet = db.relationship("Wallet", back_populates="person")

    PrimaryKeyConstraint('lname', 'fname', name='person_names_pk')
    PrimaryKeyConstraint('person_id', 'wallet_id', name='persone_wallets_pk')

    def __init__(self, lname, fname):
        self.lname = lname
        self.fname=fname

    def __repr__(self):
        return '<person %r %r %r >' % (self.lname ,self.fname,self.wallets)

    def setWallet(self, wallet_id):
        self.wallet_id=wallet_id

class PersonSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Person
        # sqla_session = db.session
        load_instance = True

    wallets = fields.Nested(WalletSchema, many=True)


class ERC20Token(db.Model):
    __tablename__ = "ERC20Token"
    token_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    address = db.Column(db.String(42))
    symbol = db.Column(db.String(16))
    decimal = db.Column(db.Integer, default=18)
    PrimaryKeyConstraint('symbol', name='address_pk')

    def __init__(self, address, symbol,decimal):
        self.address = address
        self.symbol = symbol
        self.decimal = decimal



class ERC20TokenSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ERC20Token
        # sqla_session = db.session
        load_instance = True



class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(80), index=True, unique=True)
    display_name = db.Column(db.String(80), default="A Rhymecraft User")
    password_hash = db.Column(db.String(200))
    datetime_subscription_valid_until = db.Column(db.DateTime, default=datetime.datetime.utcnow() - datetime.timedelta(days=1))
    datetime_joined = db.Column(db.DateTime, default=datetime.datetime.utcnow()),
    PrimaryKeyConstraint('id', 'email', name='mytable_pk')
    # songs = db.relationship('Song', cascade="all,delete", backref=db.backref('user', lazy='joined'), lazy='dynamic')

    def __init__(self, email, password):
        self.email = email
        self.set_password(password)

    def __repr__(self):
        return '<User %r>' % self.email

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.email)


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        # sqla_session = db.session
        load_instance = True

def init_db():
    db.create_all()

    # Create a test user
    new_user = User('a@a.com', 'aaaaaaaa')
    new_user.display_name = 'Nathan'

    new_erctoken = ERC20Token('0xc1fEFF7f984B5e00d10465286f3AC6D9dEa69Ef5', 'BNHPC',18)

    new_account1 = Account('0x4942023A414DD30D95130bc624b8bc44bCEDB7c0', '0x24833e072def790b5351c48bcc6ec724509bcb1f7d9786f536821aed6fd45bf6')
    new_account2 = Account('0x8b8Ce14490057e48f4f5bf315aAf41A4edd53C30', '0x83603e3b938f0c47b59b007d10ee488f4b9af82a6708441ae2d49d0653381915')
    new_account3 = Account('0xE03B905d149A536Ecec1d957C21d1426CbC7f3D5',
                           '0x77f852bd11d5dde51e1dcb05e1a77fca82e5bf5874dd7c6cd521e39d1370c102')


    db.session.add(new_account1)
    db.session.add(new_account2)
    db.session.add(new_account3)
    new_wallet = Wallet('test',[new_account1,new_account2])
    db.session.add(new_wallet)
    db.session.commit()
    print(new_wallet)
    # new_connectedAccount1=ConnectedAccount(new_wallet.wallet_id,new_account1.account_id)
    # new_connectedAccount2 = ConnectedAccount(new_wallet.wallet_id, new_account2.account_id)
    # db.session.add(new_connectedAccount1)
    # db.session.add(new_connectedAccount2)
    new_person=Person('Dmitry','test')
    new_person.setWallet(new_wallet.wallet_id)
    db.session.add(new_user)
    db.session.add(new_erctoken)

    new_person2 = Person('Dmitry2', 'test2')
    db.session.add(new_person2)
    db.session.add(new_person)
    db.session.commit()
    print(new_person)

    new_user.datetime_subscription_valid_until = datetime.datetime(2023, 1, 1)
    db.session.commit()

    # Create a test user

    new_user.display_name = 'Nathan'
    db.session.add(new_user)
    db.session.commit()



if __name__ == '__main__':
    init_db()