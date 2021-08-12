# Задание 1
# Написать программу, которая собирает входящие письма из своего или тестового почтового ящика
# и сложить данные о письмах в базу данных (от кого, дата отправки, тема письма,
# текст письма полный)
# Логин тестового ящика: study.ai_172@mail.ru
# Пароль тестового ящика: NextPassword172!?
import datetime
import os
import time
import locale
from pprint import pprint

from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

chrome_options = Options()
chrome_options.add_argument("start-maximized")
driver = webdriver.Chrome(os.path.join(os.getcwd(), 'chromedriver'), options=chrome_options)
driver.get('https://mail.ru')

login_input = driver.find_element_by_class_name('email-input')
login_input.send_keys('study.ai_172')
button_pass = driver.find_element_by_xpath("//button[@data-testid='enter-password']")
button_pass.click()
time.sleep(1)
pass_input = driver.find_element_by_xpath("//input[@data-testid='password-input']")
pass_input.send_keys("NextPassword172!?")
button_pass = driver.find_element_by_xpath("//button[@data-testid='login-to-mail']")
button_pass.click()
time.sleep(5)
letter_links = set()
first_iter = True
last_link = ''
# i = 0
while True:
    # i += 1
    wait = WebDriverWait(driver, 10)
    links = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='dataset__items']/a")))
    # links = driver.find_elements_by_xpath("//div[@class='dataset__items']/a")
    if last_link == links[-1].get_attribute('href') and not first_iter:
        break
    else:
        first_iter = False
    for ln in links:
        letter_links.add(ln.get_attribute('href'))
    last_link = links[-1].get_attribute('href')
    actions = ActionChains(driver)
    actions.move_to_element(links[-1])
    actions.perform()

client = MongoClient('localhost', 27017)
db = client['scraping_db']
collection = db.letters_collection

chrome_options.add_argument("--headless")
driver = webdriver.Chrome(os.path.join(os.getcwd(), 'chromedriver'), options=chrome_options)
for link in letter_links:
    letter_info = {}
    try:
        driver.get(link)
        body = wait.until(EC.presence_of_all_elements_located((By.ID, 'email_content_mr_css_attr')))

        letter_info['subject'] = driver.find_element_by_xpath("//h2[@class='thread__subject']").text
        letter_info['link'] = link
        letter_info['from'] = driver.find_element_by_xpath("//div[@class='letter__author']/span").text
        # str_date = driver.find_element_by_xpath("//div[@class='letter__date']")
        str_date = driver.find_element_by_class_name('letter__date').text
        letter_info['date'] = datetime.datetime.strptime(str_date, '%d %B, %H:%M')
        letter_info['body'] = body
    except Exception as err:
        print(str(err))
        continue

    collection.update_one({'link': link}, {'$set': letter_info}, upsert=True)


print(len(letter_links))
for i, item in enumerate(collection.find({})):
    pprint(i, item)
