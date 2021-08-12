# Задание 1
# Написать программу, которая собирает входящие письма из своего или тестового почтового ящика
# и сложить данные о письмах в базу данных (от кого, дата отправки, тема письма,
# текст письма полный)
# Логин тестового ящика: study.ai_172@mail.ru
# Пароль тестового ящика: NextPassword172!?

import os
import time

from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


chrome_options = Options()
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("--headless")
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
wait = WebDriverWait(driver, 10)
while True:
    links = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='dataset__items']/a")))
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

for link in letter_links:
    print(link)
    letter_info = {}
    try:
        driver.get(link)
        wait_body = WebDriverWait(driver, 20)
        body = wait_body.until(EC.presence_of_element_located((By.CLASS_NAME, 'letter-body__body')))
        letter_info['subject'] = driver.find_element_by_xpath("//h2[@class='thread__subject']").text
        letter_info['link'] = link
        letter_info['from'] = driver.find_element_by_xpath("//div[@class='letter__author']/span").text
        str_date = driver.find_element_by_class_name('letter__date').text
        letter_info['date'] = str_date
        letter_info['body'] = body.text
    except Exception as err:
        print(str(err))
        continue

    collection.update_one({'link': link}, {'$set': letter_info}, upsert=True)

print(len(collection.find({})))
