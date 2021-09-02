# Load libraries
from bs4 import BeautifulSoup
import pandas as pd
import requests
import smtplib
import datetime
import csv
import json
import os
import locale
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# -------------------------------------------------------------------------

try:
    locale.setlocale(locale.LC_NUMERIC, "de")

    # Load config.json
    print("Loading config. \n")
    path = os.path.dirname(os.path.realpath(__file__))
    with open(path + '\config.json') as config_file:
        data = json.load(config_file)

    _file_      = data['file']
    _url_       = data['url']
    _sender_    = data['sender']
    _recipient_ = data['recipient']
    _password_  = data['password']
    _smtp_      = data['smtp']
    _port_      = data['port']
    _lower_     = data['lower']
    _upper_     = data['upper']

    # -------------------------------------------------------------------------

    def get_product_info():
        # Define variables
        now = datetime.datetime.now()
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0", "X-Amzn-Trace-Id": "Root=1-612654ea-73fbcbc35fda58ec6038f08e"}

        # Get webscraping response
        print("Get webscraping response. \n")
        site = requests.get(_url_, headers=headers)
        response = BeautifulSoup(site.content, "html.parser")
        response2 = BeautifulSoup(response.prettify(), "html.parser")
        #print(response)

        # Get description and price of product
        description = response2.find(id='productTitle').get_text()
        price =       response2.find(id='priceblock_ourprice')
        description = description.strip()
        if (price != None):
            price = price.get_text()
            price = price.strip()
        
        # Write data to csv
        print("Write data to csv. \n")
        heading = ['ARTICLE','PRICE', 'DATE']
        data = [description, price, now]
        with open(_file_, 'a+', newline='', encoding='UTF8') as f:
            out = csv.writer(f, delimiter=';')
            out.writerow(data)
        df = pd.read_csv(_file_, sep=';')
        print(df)
        print("\n")
        
        # Set condition(s)
        if (price != None):
            price = locale.atof(price[:-2])
            if (price > _lower_ and price < _upper_):

                # Mail config
                msg = MIMEMultipart()
                msg['From'] = _sender_
                msg['To'] = _recipient_
                msg['Subject'] = description + " is now available at https://www.amazon.de for " + str(price) + "(Euros)"
                emailText = 'Webscraping check with Python: <b>' + description + ' is now available</b> at a price of <b>' + str(price) + ' €</b>. </br></br>See: <a href="' + _url_ + '">' + _url_ + '</a>'
                msg.attach(MIMEText(emailText, 'html'))

                # SMTP
                server = smtplib.SMTP(_smtp_, _port_) 
                server.starttls()
                server.login(_sender_, _password_)
                text = msg.as_string()

                # Send mail
                print('Send mail. \n')
                server.sendmail(_sender_, _recipient_, text)
                print('Email send to ' + _recipient_ + '\n')
                server.quit() 
        else:
            print('No condition was met and therefore no email was sent. \n')

        print('End of processing. \n') 

    # -------------------------------------------------------------------------

    # Call function to get product info and availability 
    get_product_info()

except NameError:
    print("An exception occurred during processing!")
