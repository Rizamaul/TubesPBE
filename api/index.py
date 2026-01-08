from flask import Flask, render_template, request
import pandas as pd
import numpy as np

# Inisialisasi Flask
app = Flask(__name__, template_folder='../templates')

@app.route('/', methods=['GET', 'POST'])
def index():
    prediction = None
    if request.method == 'POST':
        try:
            # AMBIL INPUT DARI USER
            # Contoh: jika di HTML name="suhu"
            val1 = float(request.form.get('variabel_1', 0))
            val2 = float(request.form.get('variabel_2', 0))
            
            # --- MASUKKAN LOGIKA MODEL DARI COLAB KAMU DI SINI ---
            # Contoh sederhana:
            hasil = val1 * val2 * 1.5 
            # ----------------------------------------------------
            
            prediction = f"{hasil:.2f}"
        except Exception as e:
            prediction = f"Error: {str(e)}"

    return render_template('index.html', prediction=prediction)

# Penting untuk Vercel
app.debug = True