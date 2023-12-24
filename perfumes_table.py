"""
Crawling every required attributes from two websites and combining them into a table..."""
import cloudscraper
from bs4 import BeautifulSoup
import mysql.connector

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

options = webdriver.ChromeOptions()
options.add_argument("user-data-dir=/Users/mohammadreza/Library/Application Support/Google/Chrome/Default")
driver = webdriver.Chrome(options=options)

cnx = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='Mr@1374',
    database='perfume'
)

cursor = cnx.cursor(buffered=True)
query = "SELECT * FROM perfume_links;"
cursor.execute(query)
scraper = cloudscraper.create_scraper(delay=10, browser='chrome')


for (id, link) in cursor:
    try:
        response = scraper.get(str(link))
        soup = BeautifulSoup(response.text, 'html.parser')
        year = soup.find('span', {'class': 'label_a'})
        if  year:
            year = year.string
        else:
            year = None

        brand = soup.find('span', {'itemprop': 'name'})
        if  brand:
            brand = brand.string
        else:
            brand = None

        english_name = soup.find('h1', {'class': 'p_name_h1'})
        english_name = str(english_name.contents[0])

        bottle_img = soup.find('img', {'itemprop': 'image'})
        if  bottle_img:
            bottle_img = bottle_img['src']
        else:
            box_img = None

        box_img = soup.find('a', {'class': 'imagery_item imagery_item_size75'})
        if  box_img:
            box_img = box_img.get('href')
        else:
            box_img = None

        perfumer = soup.find('div', {'class': 'w-100 mt-0-5 mb-3'})
        if  perfumer:
            perfumer = perfumer.find('a', href=True)
            perfumer = perfumer.string
        else:
            perfumer = None

        scent_rating =  soup.find('span', {'class': 'pr-1 text-lg bold blue'})
        if  scent_rating:
            scent_rating = scent_rating.string
        else:
            scent_rating = None

        longevity_rating = soup.find('span', {'class', 'pr-1 text-lg bold pink'})
        if  longevity_rating:
                longevity_rating = longevity_rating.string
        else:
            longevity_rating = None

        sillage_rating = soup.find('span', {'class', 'pr-1 text-lg bold purple'})
        if  sillage_rating:
            sillage_rating = sillage_rating.string
        else:
            sillage_rating = None

        bottle_rating = soup.find('span', {'class', 'pr-1 text-lg bold green'})
        if  bottle_rating:
            bottle_rating = bottle_rating.string
        else:
            bottle_rating = None


        main_accords = soup.find_all('div', {'class': 'text-xs grey'})
        if main_accords:
            try:
                for each_accords in main_accords:
                    cursor = cnx.cursor(buffered=True)
                    query = 'INSERT INTO main_accords(name) VALUES(\'%s\') ON DUPLICATE KEY UPDATE name=(\'%s\')' % (each_accords.string, each_accords.string)
                    cursor.execute(query)
                    cnx.commit()
            except Exception:
                pass

        driver.get(link)
        type = ''
        audience = ''
        season = ''
        occasion = ''
        try:
            wait = WebDriverWait(driver, 2)
            charts = wait.until(
                EC.element_to_be_clickable((By.ID, 'classi_li'))
            )
            charts.click()
            wait = WebDriverWait(driver, 10)
            html = wait.until(
                EC.presence_of_element_located((By.ID, 'classification_community'))
            )
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            charts = soup.find_all('div', {'class': 'col mb-2'})
            for i in charts:
                if (i.find('span', {'class': 'black bold'}).string) == 'Type':
                    for x in (i.find_all('tspan')[:-1]):
                        type += f'{x.string},'
                elif (i.find('span', {'class': 'black bold'}).string) == 'Audience':
                    for x in (i.find_all('tspan')[:-1]):
                        audience += f'{x.string},'
                elif (i.find('span', {'class': 'black bold'}).string) == 'Season':
                    for x in (i.find_all('tspan')[:-1]):
                        season += f'{x.string},'
                elif (i.find('span', {'class': 'black bold'}).string) == 'Occasion':
                    for x in (i.find_all('tspan')[:-1]):
                        occasion += f'{x.string},'
        except Exception:
            pass
        
        try:
            driver.get('https://www.******.ir/')
            persian_name = None
            temper = None
            wait = WebDriverWait(driver, 20)
            search_bar = wait.until(
                EC.element_to_be_clickable((By.ID, 'search-handler'))
            )
            search_bar.click()
            wait = WebDriverWait(driver, 20)
            search_bar2 = wait.until(
                EC.element_to_be_clickable((By.NAME, 'q'))
            )
            search_bar2.send_keys(f'{brand} {english_name}')
            search_bar2.send_keys(Keys.ENTER)

            wait = WebDriverWait(driver, 20)
            html = wait.until(
                EC.presence_of_element_located((By.TAG_NAME, 'html'))
            )
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            product_name = soup.find('a', {'class': 'link-dark en mb-2 d-block product-url text-truncate'}, href=True)
            product_brand = soup.find('a', {'class': 'link-secondary en d-block text-truncate'}, href=True)
            if product_name and product_brand:
                if english_name.casefold() in f'{product_name.string.casefold()} ' and brand.casefold() == product_brand.string.casefold():
                    data_id = product_name.parent.parent.parent.parent.parent['data-id']
                    response = scraper.get(f'https://www.atrafshan.ir/perfume/{data_id}')
                    soup = BeautifulSoup(response.text, 'html.parser')
                    persian_name = (soup.find('h2', {'class': 'fs-14 fs-md-20 text-secondary'}).string).rsplit()
                    persian_name = ' '.join(persian_name)
                    temper = soup.find_all('a', {'class': 'divider-comma'}, href=True, style=True)[1]
                    temper = temper.string
                    primary_essence = soup.find('td', string='اسانس اولیه').parent
                    primary_essence = primary_essence.find_all('td')[1].string
                    if primary_essence:
                        primary_essence = primary_essence.split('،')
                        for each_essence in primary_essence:
                            cursor = cnx.cursor(buffered=True)
                            query = 'INSERT INTO primary_essence(name) VALUES(\'%s\') ON DUPLICATE KEY UPDATE name=(\'%s\')' %(each_essence, each_essence)
                            cursor.execute(query)
                            cnx.commit()
                    mid_essence = soup.find('td', string='اسانس میانی').parent
                    mid_essence = mid_essence.find_all('td')[1].string
                    if mid_essence:
                        mid_essence = mid_essence.split('،')
                        for each_essence in mid_essence:
                            cursor = cnx.cursor(buffered=True)
                            query = 'INSERT INTO mid_essence(name) VALUES(\'%s\') ON DUPLICATE KEY UPDATE name=(\'%s\')' % (each_essence, each_essence)
                            cursor.execute(query)
                            cnx.commit()
                    basic_essence = soup.find('td', string='اسانس پایه').parent
                    basic_essence = basic_essence.find_all('td')[1].string
                    if basic_essence:
                        basic_essence = basic_essence.split('،')
                        for each_essence in basic_essence:
                            cursor = cnx.cursor(buffered=True)
                            query = 'INSERT INTO basic_essence(name) VALUES(\'%s\') ON DUPLICATE KEY UPDATE name=(\'%s\')' % (each_essence, each_essence)
                            cursor.execute(query)
                            cnx.commit()
        except Exception:
            pass
        
        try:
            cursor = cnx.cursor(buffered=True)
            query = 'INSERT INTO perfumes(english_name, persian_name, brand, year, bottle_image, box_image, type, audience,\
                    season, ocassion, perfumer, scent_rating, longevity_rating, sillage_rating, bottle_rating, temper) \
                    VALUES(\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')' % (
                english_name, persian_name, brand, year, bottle_img, box_img, str(type), str(audience), str(season),
                str(occasion), perfumer, scent_rating, longevity_rating, sillage_rating, bottle_rating, temper
            )
            cursor.execute(query)
            cnx.commit()
        except Exception:
            pass

        cursor_perfume = cnx.cursor(buffered=True)
        query_perfume = 'SELECT id FROM perfumes WHERE english_name=\'%s\'' % (english_name)
        cursor_perfume.execute(query_perfume)
        x = cursor_perfume.fetchone()

        try:
            if main_accords:
                for each_accords in main_accords:
                    cursor_main_accord = cnx.cursor(buffered=True)
                    query_main_accord = 'SELECT id FROM main_accords WHERE name=\'%s\'' % each_accords.string
                    cursor_main_accord.execute(query_main_accord)
                    y = cursor_main_accord.fetchone()
                    cursor = cnx.cursor(buffered=True)
                    query_link_accords = 'INSERT INTO perfume_main_accords(perfume_id,main_accord_id) VALUES(%i, %i)' %(int(x[0]), int(y[0]))
                    cursor.execute(query_link_accords)
                    cnx.commit()
        except Exception:
            pass

        try:
            if primary_essence:
                for each_essence in primary_essence:
                    cursor_primary_essence= cnx.cursor(buffered=True)
                    query_primary_essence = 'SELECT id FROM primary_essence WHERE name=\'%s\'' % each_essence
                    cursor_primary_essence.execute(query_primary_essence)
                    y = cursor_primary_essence.fetchone()
                    cursor = cnx.cursor(buffered=True)
                    query_link_primary = 'INSERT INTO perfume_primary_essence(perfume_id,primary_essence_id) VALUES(%i, %i)' %(int(x[0]), int(y[0]))
                    cursor.execute(query_link_primary)
                    cnx.commit()
        except Exception:
            pass

        try:
            if mid_essence:
                for each_essence in mid_essence:
                    cursor_mid_essence= cnx.cursor(buffered=True)
                    query_mid_essence = 'SELECT id FROM mid_essence WHERE name=\'%s\'' % each_essence
                    cursor_mid_essence.execute(query_mid_essence)
                    y = cursor_mid_essence.fetchone()
                    cursor = cnx.cursor(buffered=True)
                    query_link_mid = 'INSERT INTO perfume_mid_essence(perfume_id,mid_essence_id) VALUES(%i, %i)' %(int(x[0]), int(y[0]))
                    cursor.execute(query_link_mid)
                    cnx.commit()
        except Exception:
            pass

        try:
            if basic_essence:
                for each_essence in basic_essence:
                    cursor_basic_essence= cnx.cursor(buffered=True)
                    query_basic_essence = 'SELECT id FROM basic_essence WHERE name=\'%s\'' % each_essence
                    cursor_basic_essence.execute(query_basic_essence)
                    y = cursor_basic_essence.fetchone()
                    cursor = cnx.cursor(buffered=True)
                    query_link_basic = 'INSERT INTO perfume_basic_essence(perfume_id,basic_essence_id) VALUES(%i, %i)' %(int(x[0]), int(y[0]))
                    cursor.execute(query_link_basic)
                    cnx.commit()
        except Exception:
            pass

    except Exception:
        pass
