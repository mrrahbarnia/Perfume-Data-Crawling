"""
Crawling perfume links from brands table and inserting them into the perfume_links table...
"""
import cloudscraper
from bs4 import BeautifulSoup
import mysql.connector


cnx = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='Mr@1374',
    database='perfume'
)

scraper = cloudscraper.create_scraper(delay=10, browser='chrome')


cursor = cnx.cursor(buffered=True)
query = "SELECT * FROM brands;"
cursor.execute(query)
for (id, link) in cursor:
    response = scraper.get(str(link))
    soup = BeautifulSoup(response.text , "html.parser")
    links = soup.find_all('div', {'class': 'name'})
    for link in links:
        perfume_link = link.find('a').get('href')
        cursor = cnx.cursor(buffered=True)
        query = "INSERT INTO perfume_links (name) VALUES (\'%s\');" % perfume_link
        cursor.execute(query)
        cnx.commit()
