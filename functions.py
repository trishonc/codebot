import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
load_dotenv()
import ssl
import smtplib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import os
import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from threading import Thread

class ResultThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._result = None

    def run(self):
        if self._target is not None:
            self._result = self._target(*self._args, **self._kwargs)

    @property
    def result(self):
        return self._result

user = os.getenv("user")
password = os.getenv("password")
host = os.getenv("host")
database = os.getenv("database")

pool = MySQLConnectionPool(
    pool_name="mypool",
    pool_size=20,
    user=user,
    password=password,
    host=host,
    database=database
)

options = webdriver.FirefoxOptions()
options.add_argument('--headless')
driver = webdriver.Firefox(options=options)

def get_page():
    cnx = pool.get_connection()
    cursor = cnx.cursor()
    cursor.execute("SELECT page_count FROM settings")
    page_count = cursor.fetchone()[0]
    cursor.close()
    cnx.close()
    return page_count

def insert_phone_number(phone_number):
    
    cnx = pool.get_connection()
    cursor = cnx.cursor()
    add_phone = "INSERT INTO phones(phonenum) VALUES (%s)"
    cursor.execute(add_phone, (phone_number,))
    cnx.commit()
    cursor.close()
    cnx.close()

def db_check(x):

    cnx = pool.get_connection()
    cursor = cnx.cursor()
    sql = f"SELECT * FROM phones WHERE phonenum = '{x}'"
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    cnx.close()
    if result:
        return True
    else: return False


def get_phone(page_count):
    phone_count=0
    cnx = mysql.connector.connect(user=user, password=password, host=host, database=database)
    cursor = cnx.cursor()

    driver.get(f"https://www.temp-number.com/countries/?country=United%20Kingdom&page={page_count}")
    wait = WebDriverWait(driver, 10)
    links = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'h4')))
    for link in links:
        num = link.get_attribute('innerHTML')
        phone_count += 1
        if "+44" in num and not db_check(num):
            insert_phone_number(num)
            return num
        elif phone_count>=12:
            cursor.execute(f"UPDATE settings SET page_count = {page_count + 1}")
            cnx.commit()
            cursor.close()
            cnx.close()
            return get_phone(page_count)
        else: continue
def get_email():
    driver.get("https://tempail.com//")
    email = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'eposta_adres')))
    return email.get_attribute('value')
    

def get_voucher(x):
    driver.get(f'https://temp-number.com/inbox.php?country=United%20Kingdom&no={x}&in=Uk')  
    wait = WebDriverWait(driver, 10)
    msgs = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'sms-text')))
    for msg in msgs:
        text = msg.get_attribute('innerHTML')
        if 'при плащане' in text:
            sms = text.split()[1]
            driver.quit()
            return sms
        else: continue

    
def open_ta(phone_number,email):
    driver1=webdriver.Firefox()
    driver1.get("https://www.takeaway.com/bg/voucher/nov-klient")
    wait = WebDriverWait(driver1, 10)
    tel_field = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="tel"]')))
    email_field = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="email"]')))
    tel_field.send_keys(phone_number)
    email_field.send_keys(email)
    
def send_code(body,receiver):
    sender  = 'teo307852@gmail.com'
    password = os.getenv("code")
    subject = 'Your code!'

    msg=MIMEMultipart()
    msg['from'] = sender
    msg['to'] = receiver
    msg['subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(sender,password)
        smtp.sendmail(sender,receiver, msg.as_string())



   