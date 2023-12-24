"""
Crawling brands links and inserting them into the brands table...
"""

import cloudscraper
from bs4 import BeautifulSoup
import string
import mysql.connector
 

cnx = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='Mr@1374',
    database='perfume'
)


Alphabet_plus_hashtag = list(string.ascii_lowercase)
Alphabet_plus_hashtag.append('0')

scraper = cloudscraper.create_scraper(delay=10, browser='chrome')

for each_word in Alphabet_plus_hashtag:
    response = scraper.get('https://www.parfumo.com/Brands/%s' % each_word)
    soup = BeautifulSoup(response.text , "html.parser")
    brand_links = soup.find_all('a', {'class': 'p-box mb-1 pl-1 pr-1'})
    for each_link in brand_links:
        link = each_link.get('href')
        cursor = cnx.cursor(buffered=True)
        query = "INSERT INTO brands (link) VALUES (\'%s\');" % link
        cursor.execute(query)
        cnx.commit()
