from app import app
from flask import render_template, request, url_for, redirect
from bs4 import BeautifulSoup
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import requests
import os

db_url = os.environ['DATABASEURL']
client = MongoClient(db_url)
db = client['ikea_products']
stocks_table = db.stocks
users_table = db.users

@app.route('/')
def index():
    return render_template('public/index.html') #will lookup file under templates directory

@app.route('/products', methods=['POST'])
def addProducts():
    ikea_url = request.form.get('URL')
    user_name = request.form.get('name')
    user_email = request.form.get('email')
    stores = request.form.getlist('store')
    #validate url
    try:
        r = requests.get(ikea_url)
    except:
        return 'Your IKEA URL is invalid. Please try again!'
    if r.status_code != 200:
        return 'Your IKEA URL is not available. Please try again!'
    #get product_id
    url_suffix = ikea_url.split('/')[6] #item_name+item_id
    product_id = url_suffix.split('-')[-1].upper()

    soup = BeautifulSoup(r.content, 'html.parser')
    product_name = soup.find('div', {'class': 'range-revamp-header-section__title--big'}).string
    product_desc = soup.find('span', {'class': 'range-revamp-header-section__description-text'}).string
    
    print('Add new request...')
    print('product_id: '+product_id)
    print('product_name: '+ product_name)
    print('product_desc: '+ product_desc)

    #get store id
    store_info = list()
    for store in stores:
        store_info.append({'store_id': int(store), 'quantity': 0})

    #update user table
    user = {
        'user_name': user_name,
        'user_email': user_email
    }
    user_id = users_table.insert(user)
    #update stock table
    stock = {
        'product_id': product_id,
        'product_name': product_name,
        'product_desc': product_desc,
        'product_url': ikea_url,
        'user_id': user_id,
        'stock_info': store_info,
        'update_time': datetime.utcnow(),
        'last_notify_time': None
    }
    stocks_table.insert(stock)
    return render_template('public/subscribe.html') #will lookup file under templates directory

@app.route('/products/<crawl_id>', methods=['GET','DELETE'])
def unsubscribe(crawl_id):
    if request.method == 'GET':
        return render_template('public/unsubscribe.html') #will lookup file under templates directory
    else:
        # find product by crawl_id
        print('delete item ' + crawl_id + ' ...')
        user_id = stocks_table.find_one({'_id': ObjectId(crawl_id)})['user_id']
        users_table.delete_one({'_id': ObjectId(user_id)})
        stocks_table.delete_one({'_id': ObjectId(crawl_id)})
        print('delete successfully!')
        return 'You have unsubscribed your item!'
