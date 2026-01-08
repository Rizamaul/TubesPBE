from flask import Flask, render_template, request
import pandas as pd
import numpy as np

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    prediction = None
    if request.method == 'POST':
        # 1. Ambil data dari form input di website
        # Ganti variabel ini sesuai dengan variabel di paper/colab kamu
        try:
            val1 = float(request.form['variabel_1'])
            val2 = float(request.form['variabel_2'])
            
            # 2. LOGIKA MODEL KAMU (Copy paste logika dari Colab ke sini)
            # Contoh sederhana:
            hasil = val1 * val2 * 0.85 
            prediction = round(hasil, 2)
        except:
            prediction = "Error: Pastikan input berupa angka"

    return render_template('index.html', prediction=prediction)

if __name__ == '__main__':
    app.run(debug=True)