###########################################################
# Proje Akışı
############################################################
# 1. "Travel" ve "Nonfiction" kategorilerine ait kitapların yer aldığı
# sayfa linklerini ana sayfa içerisinden almak.
# 2. İlk kategoriye ait ürünlerin bulunduğu sayfa
# görüntülenerek, tüm kitapların detay sayfalarına erişmek için linkler kazınmalı.
# 3. Kazınan linkler kullanılarak o kategoriye ait tüm kitapların detay bilgileri kazınmalı.
# 4. Adım 2 ve 3’ü diğer kategori için de yapabilmek adına sistem
# otomatize edilmeli.
############################################################

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import re
import requests

############################################################
# Görev 1: Tarayıcıyı Konfigüre Etme ve Başlatma
############################################################

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options)

#############################################################
# Görev 2: Ana Sayfanın İncelenmesi ve Kazınması
#############################################################

# Ana Sayfayı driver ile açıp ve inceleyelim
sleep_time = 2
driver.get("https://books.toscrape.com/")
time.sleep(sleep_time)

# "Travel" ile "Nonfiction" kategori sayfalarının linklerini tutan elementleri tek seferde bulan XPath sorgusunu yazalım
category_elements_xpath = "//a[contains(text(),'Travel') or contains(text(),'Nonfiction')]"

# XPath sorgusu ile yakaladığımız elementleri, driver'ı kullanarak bulalım ve kategori detay linklerini kazıyalım
elements = driver.find_elements(By.XPATH, category_elements_xpath)
category_urls = [element.get_attribute('href') for element in elements]
print(category_urls)

#############################################################
# Görev 3: Kategori Sayfasının İncelenmesi ve Kazınması
#############################################################
# Herhangi bir detay sayfasına girip o sayfadaki kitapların detay linkini tutan elementleri yakalayan
# XPath sorgusunu yazalım
driver.get(category_urls[0])
time.sleep(sleep_time)

# driver ile XPath sorgusunu kullanarak elementleri yakalayınız ve detay linklerini çıkarınız.
book_detail_xpath= "//ol[contains(@class, 'row')]//a"
book_detail_elements = driver.find_elements(By.XPATH, book_detail_xpath)
book_urls = [element.get_attribute("href") for element in book_detail_elements]
print(book_urls)
print(len(book_urls))

# Sayfalandırma (Pagination) için butonlara tıklamak yerine sayfa linkini manipüle etme yöntemini
# kullalım ve döngü kullanarak sayfalandırma sistemi ekleyelim

max_pagination = 3
url = category_urls[0]
book_urls = []
for i in max_pagination:
    update_url = url if i == 1 else url.replace("index",f"page-{1}")
    driver.get(update_url)
    book_elements = driver.find_elements(By.XPATH, book_detail_xpath)

    temp_urls = [element.get_attribute("href") for element in book_elements]
    book_urls.append(temp_urls)

print(book_urls)
print(len(book_urls))

# Sayfalandırmanın sonuna geldiğimizi anlamak adına kategorinin
# 999. sayfasına giderek karşımıza çıkan sayfayı inceleyelim.
# İpucu: ..../category/books/nonfiction_13/page-999.html

# Sayfalandırmada sonsuz döngüye girmemek adına bu durumu kontrol edelim.
# İpucu: text'inde 404 içeren bir h1 var mı?) veya (if not product_list) ya da (len(product_list) <= 0 gibi

max_pagination = 3
url = category_urls[0]
book_urls = []
for i in max_pagination:
    update_url = url if i == 1 else url.replace("index", f"page-{1}")
    driver.get(update_url)
    book_elements = driver.find_elements(By.XPATH, book_detail_xpath)

    temp_urls = [element.get_attribute("href") for element in book_elements]
    book_urls.append(temp_urls)

    if not book_elements:  # len(course_elements) <= 0
        break

print(book_urls)
print(len(book_urls))

#############################################################
# Görev 4: Ürün Detay Sayfasının Kazınması
#############################################################

# Herhangi bir ürünün detay sayfasına girip class attribute'ı content olan div elementini yakalayalım
content_xpath = "//div[contains(@class, 'content')]"
driver.get(book_urls[0])
time.sleep(sleep_time)
content_div = driver.find_elements(By.XPATH, content_xpath)

# Yakaladığımız divin html'ini alalım ve inner_html adlı değişkene atayalım.
inner_html = content_div[0].get_attribute("innerHTML")

# inner_html ile soup objesi oluşturunuz.
soup = BeautifulSoup(inner_html, "html.parser")

# Oluşturduğumuz soup objesi ile aşağıdaki bilgileri kazıyalım:
# ▪ Kitap Adı
book_name = soup.find("h1").text

# ▪ Kitap Fiyatı
price_text = soup.find("p", class_="price_color").text

# ▪ Kitap Yıldız Sayısı
rating = soup.find("p", class_="star-rating")
rating_value = [cls for cls in rating["class"] if cls != "star-rating"][0]

# Alternatif çözüm
regex = re.compile("^star-rating ")  # star-rating ile başlayanı getirir
star_element= soup.find("p", attrs={"class": regex})
print(star_element)
book_star_count = star_element['class'][-1]

# ▪ Kitap Açıklaması
description_div = soup.find("div", id="product_description")
description_paragraph = description_div.find_next_sibling("p").text

# ▪ Product Information Başlığı altında kalan tablodaki bilgiler
product_info = {}
table_rows = soup.find("table").find_all('tr')
for row in table_rows:
    header = row.find('th').text
    value = row.find('td').text
    product_info[header] = value

# Sonuçları yazdırma
for header, value in product_info.items():
    print(f"{header}: {value}")

#############################################################
# Görev 5: Fonksiyonlaştırma ve Tüm Süreci Otomatize Etme
#############################################################

# Adım 1: İşlemleri fonksiyonlaştıralım.
def get_book_detail(driver, url):
    driver.get(url)
    time.sleep(sleep_time)
    content_xpath = "//div[contains(@class, 'content')]"
    content_div = driver.find_elements(By.XPATH, content_xpath)

    inner_html = content_div[0].get_attribute("innerHTML")
    soup = BeautifulSoup(inner_html, "html.parser")

    # ▪ Kitap Adı
    book_name = soup.find("h1").text
    # ▪ Kitap Fiyatı
    book_price = soup.find("p", class_="price_color").text

    # ▪ Kitap Yıldız Sayısı
    reregex = re.compile("^star-rating ")  # star-rating ile başlayanı getirir
    star_element = soup.find("p", attrs={"class": reregex})
    book_star_count = star_element['class'][-1]

    # ▪ Kitap Açıklaması
    description_div = soup.find("div", attrs={"id": "product_description"})
    book_desc = description_div.find_next_sibling().text

    product_info = {}
    table_rows = soup.find("table").find_all('tr')
    for row in table_rows:
        key = row.find('th').text
        value = row.find('td').text
        product_info[key] = value

    return {'book_name': book_name, 'book_price': book_price,
            'book_star_count': book_star_count, 'book_desc': book_desc}

def get_book_urls(driver, url):
    max_pagination = 3
    book_elements_xpath = "//ol[contains(@class, 'row')]//a"
    #"//div[@class, 'image_container']//a"
    book_urls = []
    for i in range(1,max_pagination):
        update_url = url if i == 1 else url.replace("index", f"page-{i}")
        driver.get(update_url)
        time.sleep(sleep_time)
        book_elements = driver.find_elements(By.XPATH, book_elements_xpath)

        if not book_elements:
            break

        temp_urls = [element.get_attribute("href") for element in book_elements]
        book_urls.extend(temp_urls)

    return book_urls

def get_travel_and_nonfiction_categor_url(driver, url):
    driver.get(url)
    time.sleep(sleep_time)
    category_elements_xpath = "//a[contains(text(),'Travel') or contains(text(),'Nonfiction')]"
    category_elements = driver.find_elements(By.XPATH, category_elements_xpath)
    category_urls = [element.get_attribute("href") for element in category_elements]
    return category_urls

def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options)
    return driver

# Adım 2: Süreci otomatize ederek, Travel ile Nonfiction kategorilerine ait
# tüm kitapların detaylarını alacak şekilde kodu düzenleyelim.
sleep_time = 0.5
def main():
    base_url = "https://books.toscrape.com/"
    driver = initialize_driver()
    category_urls = get_travel_and_nonfiction_categor_url(driver,base_url)
    data=[]
    for cat_url in category_urls:
        book_urls = get_book_urls(driver,cat_url)
        for b_url in book_urls:
            book_data = get_book_detail(driver,b_url)
            book_data['cat_url'] = cat_url
            data.append(book_data)
    len(data)

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', 40)
    pd.set_option('display.width', 2000)
    df = pd.DataFrame(data)
    return df

df = main()
print(df.head())
print(df.shape)

