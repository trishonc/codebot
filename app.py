from flask import Flask, render_template, request
from functions import *
from dotenv import load_dotenv
load_dotenv()

user = os.getenv("user")
password = os.getenv("password")
host = os.getenv("host")
database = os.getenv("database")



app = Flask(__name__)


@app.route('/', methods = ['POST', 'GET'])
def hello():
    if request.method == "POST":
        page_count = get_page()
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
        receiver = request.form['email']
        while True:
            voucher = get_voucher(num)
            if voucher is not None:
                send_code(voucher,receiver)
                driver.quit()
                return render_template('success.html')
            else: continue
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(port=5000,debug=True)
