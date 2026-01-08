from flask import Flask, render_template, request
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from scipy.optimize import curve_fit

app = Flask(__name__, template_folder='../templates')

# --- RUMUS DARI PAPER ---
# Persamaan 4: Solusi Analitik Tanpa Hujan
def model_analitik(t, m0, k_base, k_solar):
    return m0 * np.exp(-(k_base + 0.5 * k_solar) * t + (k_solar / (4 * np.pi)) * np.sin(2 * np.pi * t))

# Persamaan 5: Net Calorific Value
def calculate_enet(m_t):
    cv_dry = 20  # MJ/kg
    lv = 2.26    # MJ/kg
    return cv_dry - (lv * m_t)

@app.route('/', methods=['GET', 'POST'])
def index():
    graph_url = None
    results = None
    
    # Default data (Dari Tabel 1 Paper kamu)
    d_t = "0, 1, 2"
    d_m = "81.68, 68.92, 41.16"
    
    if request.method == 'POST':
        try:
            # 1. Ambil Input User
            t_obs = np.array([float(x) for x in request.form.get('t_array').split(',')])
            m_obs = np.array([float(x) for x in request.form.get('m_array').split(',')])
            r_in = float(request.form.get('r_in', 0)) # Parameter Hujan Baru
            t_hujan = float(request.form.get('t_hujan', 5)) # Hari terjadinya hujan

            # 2. Kalibrasi Otomatis (Mencari k_base & k_solar terbaik untuk data user)
            popt, _ = curve_fit(lambda t, kb, ks: model_analitik(t, m_obs[0], kb, ks), t_obs, m_obs, p0=[0.3, 0.1])
            kb_opt, ks_opt = popt

            # 3. Simulasi Masa Depan (14 Hari) dengan Parameter Hujan
            t_sim = np.linspace(0, 14, 500)
            m_sim = []
            m_current = m_obs[0]
            
            # Simulasi langkah per langkah untuk mengakomodasi hujan (Numerical approach based on your ODE)
            dt = t_sim[1] - t_sim[0]
            for t in t_sim:
                # Tambahkan hujan jika pada hari yang ditentukan
                if abs(t - t_hujan) < 0.1:
                    m_current += r_in 
                
                # Update M berdasarkan k_total (Persamaan 1 & 3)
                k_t = kb_opt + ks_opt * (np.sin(np.pi * t)**2)
                m_current -= k_t * m_current * dt
                m_sim.append(max(0, m_current))
            
            m_sim = np.array(m_sim)
            enet_sim = calculate_enet(m_sim)

            # 4. Cari Waktu Kritis (t_crit saat Enet > 0)
            t_crit = "Tidak tercapai dalam 14 hari"
            for i in range(len(enet_sim)):
                if enet_sim[i] > 0:
                    t_crit = f"{t_sim[i]:.2f} Hari"
                    break

            # 5. Plotting
            plt.figure(figsize=(10, 6))
            plt.plot(t_sim, m_sim, label='Prediksi Kadar Air (M)', color='blue')
            plt.scatter(t_obs, m_obs, color='red', label='Data Input User')
            plt.axhline(y=8.85, color='orange', linestyle='--', label='Ambang Batas Kritis (M ≈ 8.85%)')
            
            if r_in > 0:
                plt.annotate('Terjadi Hujan', xy=(t_hujan, m_sim[int(t_hujan*35)]), arrowprops=dict(facecolor='black', shrink=0.05))

            plt.title("Dinamika Energi Lahan Gambut")
            plt.xlabel("Waktu (Hari)")
            plt.ylabel("Kadar Air (%)")
            plt.legend()
            plt.grid(True, alpha=0.3)

            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            graph_url = base64.b64encode(img.getvalue()).decode()
            plt.close()

            results = {
                "kb": round(kb_opt, 4),
                "ks": round(ks_opt, 4),
                "tcrit": t_crit
            }

        except Exception as e:
            results = {"error": str(e)}

    return render_template('index.html', graph_url=graph_url, results=results, d_t=d_t, d_m=d_m)