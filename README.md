# ikea-stock-notifier
A notifier that lets users subscribe to their favorite IKEA products which are unavailable. This notifier will crawl the stock status every hour and notify users immediately once the products are back to the stock.
[!demo1.png](https://github.com/lanlanblue/ikea-stock-notifier/blob/master/demo1.png)

## Usage
Subscribe the product by pasting the product URL and register with your email address. You can unsubscribe the product from the link of email notification.
[!demo3.png] (https://github.com/lanlanblue/ikea-stock-notifier/blob/master/demo3.png)

## Features
- Crawler for crawling data from the stock database
- RESTful API
  - Insert subscribed items into the database
  - Remove items based on _id

## Deployment Platform
- Application: Heroku
- Mongodb: mLab
