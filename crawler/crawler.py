import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime
import calendar
from datetime import timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
import os
import yagmail
import json

db_url = os.environ['DATABASEURL']
client = MongoClient(db_url)
db = client['ikea_products']
stocks_table = db.stocks
users_table = db.users
scheduler = BlockingScheduler()

print("start crawler schduler...")

@scheduler.scheduled_job('interval', hours=1)
def crawl_data():
    print("Starting reading from DB...")
    #read from database
    for item in stocks_table.find():
        print("Crawling product: "+str(item['_id']))
        store_list = list()
        
        for store in item['stock_info']:
            store_list.append(store['store_id'])
        updated_info = get_stock_info(item['product_id'], store_list)
        stocks_table.update_one(
            {'_id': item['_id']},
            {'$set':
                {'stock_info': updated_info, 'update_time': datetime.utcnow()}
            }
        )
        #Notify user
        notify = False
        for info in updated_info:
            #if this product is back in stock and we haven't notified user within 12 hours
            if (info['quantity'] > 0) and (item['last_notify_time'] == None or ((datetime.utcnow() - item['last_notify_time']).seconds / 3600 > 12)):
                notify = True
        if notify:
            #get email of receiver
            receiver = users_table.find_one({'_id': item['user_id']})
            print('send to: ' + receiver['user_email'])
            #generate email content
            content = generate_email_content(receiver['user_name'], item['_id'], item['product_name'], item['product_desc'], item['product_url'], updated_info)
            #send email
            yag = yagmail.SMTP(user=os.environ['MAILACCOUNT'], password=os.environ['MAILPASSWD'])
            yag.send(to=receiver['user_email'], newline_to_break=False , subject='Your IKEA product ' + str(item['product_name']) + ' is back in stock!', contents=content)
            print("Email sent successfully")
            #update notify time
            stocks_table.update_one(
                {'_id': item['_id']},
                {'$set':
                    {'last_notify_time': datetime.utcnow()}
                }
            )
    print("Finished updating DB...")
    

def get_stock_info(product_id, store_list):
    ## database API
    stock_url = "https://www.ikea.com/us/en/iows/catalog/availability/" + str(product_id)
    req = requests.get(stock_url)
    soup = BeautifulSoup(req.content, 'xml')
    #print(soup.prettify())
    res = list()
    for store_id in store_list:
        stock = soup.find('localStore', {"buCode": store_id})
        res.append({'store_id': stock['buCode'], 'quantity': int(stock.availableStock.string)})
    return res

def generate_email_content(receiver_name, crawl_id, product_name, product_desc, product_url, stocks_info):
    f = open('./assets/email_template.html', 'r')
    content = f.read()
    #get images
    req = requests.get(product_url)
    soup = BeautifulSoup(req.content, 'html.parser')
    images = soup.find_all('div', {'class': 'range-revamp-media-grid__media-container'})
    if len(images) > 1:
        main_image = images[1]
    else:
        main_image = image[0]
    #get stoock info
    with open('assets/store.json') as f:
        store_data = json.load(f)
    store_dict = dict()
    for store in store_data:
        store_city = store['storeCity']
        store_number = store['storeNumber']
        if store_city != "" and store_number != "":
            store_dict[store_number] = store_city
    
    store_info = ''
    for info in stocks_info:
        store_info += store_dict[info['store_id']] + ' has ' + str(info['quantity']) + " left!<br>" 

    unsubscribe_url = os.environ['DOMAIN'] + 'products/' + str(crawl_id)
    date = calendar.month_name[datetime.today().month] + ' ' + str(datetime.today().day) + '.' + str(datetime.today().year)
    content = content.replace('user_name', receiver_name)
    content = content.replace('product_name', product_name)
    content = content.replace('date', date)
    content = content.replace('product_image', main_image.img['src'])
    content = content.replace('product_url', product_url)
    content = content.replace('store_infos', store_info)
    content = content.replace('unsubscribe_url', unsubscribe_url)
    #for info in stocks_info:
        #content += 'store: ' + info['store_id'] + ' quantity: ' + str(info['quantity']) + '\n'
    return content
 
if 'DEBUG' in os.environ:
    print('DEBUG MODE: ON')
    crawl_data()
else:
    scheduler.start()
    