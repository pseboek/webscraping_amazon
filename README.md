# Webscraping Amazon

In order to get information about a product on amazon, it is possible to use **BeautifulSoup** in **Python** to webscrape the website.

## config.json

In the config file all parameters are listed in order to scrape the amazon website. For instance, the **url** of the product or the **smtp** values of a mail provider are necessary. With **upper and lower** one can specify the price range of a product in order to set a filter.

```json
{
    "file": "C:\\Users\\[XXX]\\Desktop\\webscraping_amazon\\webscraping_amazon.csv",
    "url": "https://www.amazon.de/Sony-Interactive-Entertainment-PlayStation-5/dp/B08H93ZRK9/",
    "sender": "SENDER_MAIL",
    "recipient": "RECIPIENT_MAIL",
    "password": "YOUR_PASSWORD",
    "smtp": "mail.gmx.net",
    "port": 587,
    "lower": 100,
    "upper": 750
}
```

---

## script.py

First, all needed **libraries** are loaded. BeautifulSoup is necessary for webscraping the website, and MIMEMultipart as well as MIMEText are used for formatting the email message.

Afterwards the **config values** are set by reading in the config.json. The routine **get_product_info()** defines the variable **headers** that contains information about the user agent. This is browser specific and can be looked up at [http://httpbin.org/get](http://httpbin.org/get).

The **response** is parsed and some elements are assigned to their values (i.e. price, desciption). After that the results are written to a **csv file** and an **email** is sent if the set condition is true.

```python
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

```

---

## webscraping_amazon.csv

In the **example** at hand the price of the Playstation 5 was webscraped. Since the console was out of stock during that time, no price was stored and therefore no email notification was sent.


    ARTICLE;PRICE;DATE
    Sony PlayStation 5;;2021-08-26 17:48:31.041767
    Sony PlayStation 5;;2021-08-26 18:38:33.401934
    Sony PlayStation 5;;2021-08-27 06:38:35.305395
    ...

---

## webscraping_amazon.xml

In order to execute the python routine regularly, a windows task is defined that runs the script at a random time every other hour so that amazon does not detect and defines it as a bot request.

```xml
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>2021-08-26T17:41:54.9747599</Date>
    <Author>DESKTOP\[XXX]</Author>
    <URI>\Webscraping_Amazon</URI>
  </RegistrationInfo>
  <Triggers>
    <TimeTrigger>
      <Repetition>
        <Interval>PT1H</Interval>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
      <StartBoundary>2021-08-26T17:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <RandomDelay>PT1H</RandomDelay>
    </TimeTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>XXX</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>true</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>true</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>false</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>true</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT72H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>C:\Users\[XXX]\AppData\Local\Programs\Python\Python37\python.exe</Command>
      <Arguments>"C:\Users\[XXX]\Desktop\webscraping_amazon\script.py"</Arguments>
    </Exec>
  </Actions>
</Task>
```

---
