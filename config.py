import os
from web3 import Web3
from web3.auto import w3
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import connexion

basedir = os.path.abspath(os.path.dirname(__file__))

# Create the connexion application instance
connex_app = connexion.App(__name__, specification_dir=basedir)

# Get the underlying Flask app instance
app = connex_app.app

# Build the Sqlite ULR for SqlAlchemy
sqlite_url = "sqlite:///" + os.path.join(basedir, "people.db")
w3etherprovider='http://127.0.0.1:8545'
network='5777'

# Configure the SqlAlchemy part of the app instance
app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = sqlite_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Create the SqlAlchemy db instance
db = SQLAlchemy(app)

# Initialize Marshmallow
ma = Marshmallow(app)

# initilize blockchain
w3 = Web3(Web3.HTTPProvider(w3etherprovider))
