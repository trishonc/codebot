from functions import *
from threading import Thread
from dotenv import load_dotenv
load_dotenv()

user = os.getenv("user")
password = os.getenv("password")
host = os.getenv("host")
database = os.getenv("database")

cnx = mysql.connector.connect(user=user, password=password, host=host, database=database)
cursor = cnx.cursor()
cursor.execute("SELECT page_count FROM settings")
page_count = cursor.fetchone()[0]

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


t1=ResultThread(target=get_phone, args=(page_count,))
t2=ResultThread(target=get_email)

t1.start()
t2.start()
t1.join()
t2.join()


phone_number=str(t1.result)
email=str(t2.result)

num=phone_number[2:]
open_ta(phone_number,email)
#receiver = input("enter your email adress: ")
receiver = email
while True:
    voucher = get_voucher(num)
    if voucher is not None:
        send_code(voucher,receiver)
        break
    else: continue
try:
    os.system("taskkill /F /IM firefox.exe")
except Exception as e:
    print("An error occurred: ", e)






    










   


