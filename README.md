# ikea-stock-notifier
A notifier that lets users subscribe to their favorite IKEA products which are out of stock. This notifier will crawl the stock status every hour and notify users immediately once the product is back in stock.
![demo1.png](https://github.com/lanlanblue/ikea-stock-notifier/blob/master/demo1.png)

## Usage
Subscribe to be notified when the product is in stock by pasting the product URL and providing your email address. You can unsubscribe from the notifications using the provided link in the email notification.
![demo3.png](https://github.com/lanlanblue/ikea-stock-notifier/blob/master/demo3.png)

## Features
- Crawler for crawling data from the stock database
- RESTful API
  - Insert subscribed items into the database
  - Remove items based on _id

## Deployment Guide
- Platform: Heroku
- Database: Mongodb at mLab

1. Clone this project to your local workspace
   ```
   $ git clone https://github.com/lanlanblue/ikea-stock-notifier.git
   ```
2. Create your Heroku account and download Heroku CLI

   Please follow this guide [The Heroku CLI \| Heroku Dev Center](https://devcenter.heroku.com/articles/heroku-cli)

   For MacOS
   ```
   $ brew tap heroku/brew && brew install heroku
   ```
3. Create a DB on mLab
   - Register on [MongoDB Hosting: Database-as-a-Service by mLab](https://mlab.com/home)
   - Create a DB called "ikea_products"
   - Add 2 collections under this DB
     - users
     - stocks
   - Setup DB user & password
   
   You can find your MongoDB link on the top of page.
4. Setup your gmail for notification
   
   Please follow the steps in the link below, and copy the password that gmail service generates for you.
   
   [How to Use Your Gmail Account as Your Email Sender via SMTP](https://www.jotform.com/help/392-How-to-Use-Your-Gmail-Account-as-Your-Email-Sender-via-SMTP)

5. Create 2 apps on Heroku

   Create apps with app names. The app name will be part of domain name used in later step.
   ```
   $ cd ikea-stock-notifier
   $ heroku create ikea-crawler --buildpack heroku/python --remote ikea-crawler
   $ heroku create ikea-notifier --buildpack heroku/python --remote ikea-notifier
   ```

6. Set config vars for both apps

   You can either set config vars by following commands or set them on Heroku Dashboard
   https://devcenter.heroku.com/articles/config-vars
   
   ```
   # set up for ikea-crawler app
   $ heroku config:set DATABASEURL="<your MongoDB link>/ikea_products?retryWrites=false" --app=ikea-crawler
   $ heroku config:set DOMAIN="<the domain name of ikea-notifier>" --app=ikea-crawler
   $ heroku config:set MAILACCOUNT="<your gmail account>" --app=ikea-crawler
   $ heroku config:set MAILPASSWD="<the app password generated from step4>" --app=ikea-crawler
   
   #setup for ikea-notifier app
   $ heroku config:set DATABASEURL="<your MongoDB link>/ikea_products?retryWrites=false" --app=ikea-notifier
   $ heroku config:set DOMAIN="<the domain name of ikea-notifier>" --app=ikea-notifier
   ```
   
   \<your MongoDB link\>: Please find the MongoDB link on mlab
   ex. mongodb://<your account>:<your password>@XXX.mlab.com:port#
  
   \<the domain name of ikea-notifier\>: The domain name of ikea-notifier can be found by the following command
   ```
   $ heroku domains --app ikea-notifier
   ```
   
7. Deploy the code

   ```
   # under ikea-stock-notifier
   $ git subtree push --prefix crawler ikea-crawler master
   $ git subtree push --prefix notifier ikea-notifier master
   $ heroku ps:scale clock=1 --app ikea-crawler1
   ```
