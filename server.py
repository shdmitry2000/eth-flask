"""
Main module of the server file
"""
# 3rd party moudles
from flask import render_template, abort

# local modules
import config

# Get the application instance
from models import ERC20Token
from tokens import use_erc20_tocken

connex_app = config.connex_app

# Read the swagger.yml file to configure the endpoints
connex_app.add_api("swagger.yml")


# create a URL route in our application for "/"
@connex_app.route("/")
def home():
    """
    This function just responds to the browser URL
    localhost:5000/

    :return:        the rendered template "home.html"
    """
    return render_template("home.html")




if __name__ == "__main__":
    connex_app.run(debug=True)