import re
from bs4 import BeautifulSoup
import os

def get_order_number(soup):
    '''This function extracts the order number from the HTML file using Beautiful Soup and a regular expression.'''
    
    # get the order number from the HTML and extract only the digits
    order_number = soup.find_all('h2', class_='vmarg16x')[-1].get_text(strip = True)
    order_number = re.search(r'\d+', order_number).group()
    return {'Order Number': order_number}

def get_customer_info(soup):
    '''This function extracts the customer information (name, address, city, postal code, and phone number) from the HTML file using Beautiful Soup.'''
    
    # extract the customer information from the HTML and store in a dictionary
    keys = ['Name', 'Address', 'City', 'PostalCode', 'PhoneNumber']
    customer_info = []
    text_customer_details = soup.find_all('p' , class_ = 'alignleft')
    for item in text_customer_details:
        customer_info.append(item.get_text(strip = True))
    customer_dict = dict(zip(keys, customer_info))
    return {'Customer': customer_dict}

def get_restaurant_info(soup):
    '''This function extracts the restaurant information (name, address, city, postal code, and phone number) from the HTML file using Beautiful Soup.'''
    
    # extract the restaurant information from the HTML and store in a dictionary
    keys = ['Name', 'Address', 'City', 'PostalCode', 'PhoneNumber']
    restaurant_info = []
    restaurant_info_text = soup.find_all('table' , class_ = 'fluid')[0].find_all('p')
    for item in restaurant_info_text:
        restaurant_info.append(item.get_text(strip = True))
    restaurant_info_dict = dict(zip(keys, restaurant_info))
    return {'Restaurant': restaurant_info_dict}

def get_item_details(soup):
    '''This function extracts the item details (quantity, name, type, and price) from the HTML file using Beautiful Soup.'''
    
    # extract the list of items and their details from the HTML and store in a list of dictionaries
    text_item = soup.find('table' , role = "listitem").find_all('tr')
    items = []
    for text in text_item:
        td_tags = text.find_all('td')
        if td_tags:
            item_info_dict = {}
            quantity = td_tags[0].text.strip().replace("x","")
            item_info_dict['Quantity'] = float(quantity)
            item_info = td_tags[1].text
            items_list = [item.strip() for item in item_info.split('\n') if item.strip()]
            item_name = items_list[0]
            item_info_dict['Item Name'] = item_name
            item_type_list = items_list[1:]
            if len(item_type_list) != 0:
                item_info_dict['Item List'] = item_type_list
            price = td_tags[2].get_text(strip = True)
            price = price.replace(',','.')[:-2] #Remove euro and get price as float
            item_info_dict['Price'] = float(price)
            items.append(item_info_dict)
    return {'Items': items}

def get_totals(soup):
    '''This function extracts the total cost and all subtotals (delivery, discount, subtotal, tip, total) from the HTML file using Beautiful Soup and regular expressions.'''
    
    
    # extract the total amounts for each category (e.g. subtotal, delivery fee) from the HTML and store in a dictionary
    total_dict = {}
    comment_1 = soup.find(text= ' Subtotal ')
    for i in range(len(comment_1.findNextSiblings('tr'))):
        td_list = comment_1.findNextSiblings('tr')[i].find_all('td')
        amount_str = td_list[1].text.strip()  
        amount_match = re.search(r'\d+\.\d+', amount_str)  # find the float value using a regular expression and remove euro symbol
        if amount_match:
            amount = float(amount_match.group())
        else:
            amount = amount_str  # keep the 'free' or any other string as is
        total_dict[td_list[0].text.strip()] = amount #td_list[0] has he respective amount category like delivery or tip e.t.c
    return {'Total': total_dict}

def parse_html_file(soup):
    '''This function combines the above functions to extract all relevant information from the HTML file and return it as a dictionary.'''
    
    order_data = {}
    order_data.update(get_order_number(soup))
    order_data.update(get_customer_info(soup))
    order_data.update(get_restaurant_info(soup))
    order_data.update(get_item_details(soup))
    order_data.update(get_totals(soup))
    
    return order_data



directory = r'C:\Users\kingr\Documents\GitHub\Group-2-Head-of-data\deliveroo-emails\deliveroo'

# create an empty list to hold all the parsed HTML files as BeautifulSoup objects
soups = []


# loop through all the files in the directory with a '.html' extension
for filename in os.listdir(directory):
    if filename.endswith('.html'):
        # create the full file path for the current file
        filepath = os.path.join(directory, filename)
        # open the file and parse its contents as a BeautifulSoup object, then append to the soups list
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            soups.append(BeautifulSoup(f, 'html.parser'))

#Create empty list to store all the dictionaries of each HTML file
order_data_list = []

for soup in soups:
    order_data_list.append(parse_html_file(soup))

import json
orders_data = {}
orders_data['Orders'] = order_data_list

with open('orders_data_parsed.json', 'w', encoding='utf-8') as f:
    # Write the list of order dictionaries to the file as JSON, with ensure_ascii=False
    f.write(json.dumps(orders_data, indent=4, ensure_ascii=False))

