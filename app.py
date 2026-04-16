import streamlit as st
import pandas as pd
import glob
import requests
import json
import os

# --- 1. KURUMSAL YAPILANDIRMA ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("⚠️ API Anahtarı Secrets kısmında bulunamadı!")
    st.stop()

API_KEY = st.secrets["GEMINI_API_KEY"]

st.set_page_config(page_title="Ak Portföy | Akıllı Yatırım Tavsiyesi", layout="wide")

# Ak Portföy Kurumsal Teması
st.markdown("""
<style>
    .main { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #1e1e1e; }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 { color: #ffffff !important; }
    .stButton>button { background-color: #D8232A; color: white; border-radius: 8px; width: 100%; border: none; font-weight: bold; height: 3em; }
    hr { border: 1px solid #D8232A !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. VERİ YÜKLEME ---
def load_data():
    # Veri dosyalarını bulma (fonlar.csv veya fonlar.xlsx)
    files = glob.glob("fonlar*") + glob.glob("*.csv") + glob.glob("*.xlsx")
    for f in files:
        try:
            return pd.read_excel(f) if f.endswith('.xlsx') else pd.read_csv(f, sep=None, engine='python', encoding='utf-8-sig')
        except: continue
    return None

df = load_data()

# --- 3. LOGO VE BAŞLIK ALANI (HATA DÜZELTİLDİ) ---
col_l, col_m, col_r = st.columns([1, 2, 1])
with col_m:
    # Az önceki DeltaGenerator hatasını bu blokla kökten çözüyoruz
    if os.path.exists("logo.png"):
        st.image("logo.png", width=300)
    else:
        st.markdown("<h2 style='text-align:center; color:#D8232A;'>AK Portföy</h2>", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:#D8232A; margin-top:0;'>AKILLI YATIRIM TAVSİYESİ</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#666; font-style:italic;'>Yapay Zeka Destekli Gelecek Nesil Portföy Yönetimi</p><hr>", unsafe_allow_html=True)

# --- 4. YATIRIM TERCİHLERİ ---
with st.sidebar:
    st.header("Yatırım Tercihleri")
    lang = st.selectbox("Dil Seçimi", ["Türkçe", "Almanca"])
    st.divider()
    ans_risk = st.select_slider("Risk Tercihi", options=["Korumalı", "Dengeli", "Agresif"])
    ans_sektor = st.selectbox("Odak Sektör", ["Teknoloji ve Yapay Zeka", "Sürdürülebilirlik", "Emtia ve Değerli Madenler", "Gayrimenkul"])
    ans_vade = st.selectbox("Vade Beklentisi", ["0-1 yıl", "2-5 yıl", "10+ yıl"])
    amount = st.number_input("Yatırım Tutarı (TL)", min_value=1000, value=50000)
    st.divider()
    analyze_btn = st.button("Analizi Başlat", type="primary")

# --- 5. GERÇEK ANALİZ MOTORU ---
if df is not None:
    if analyze_btn:
        with st.spinner("Yatırım Uzmanı Verileri İnceliyor..."):
            
            # SENİN İSTEDİĞİN DERİN ANALİZ TALİMATI
            prompt = f"""
            Sen Ak Portföy'de Kıdemli Yatırım Uzmanısın. Müşteri için fon bazlı, profesyonel bir rapor hazırla.
            Dil: {lang}
            
            MÜŞTERİ TERCİHLERİ:
            - Yatırım: {amount} TL | Vade: {ans_vade} | Risk: {ans_risk} | Sektör: {ans_sektor}
            
            ELİNDEKİ GERÇEK FON VERİLERİ:
            {df.to_string()}
            
            RAPORDA ŞUNLARI DETAYLI ŞEKİLDE AÇIKLA:
            1. Seçilen Ak Portföy fonlarının '{ans_risk}' risk profiline neden tam uyduğunu teknik olarak anlat.
            2. '{ans_sektor}' sektörü neden seçildi ve bu fonların içindeki ağırlığı ne olmalı?
            3. Seçilen her bir fonun avantajını, eldeki getiri/risk verilerine dayanarak kanıtla.
            4. Bu portföyün '{ans_vade}' vadede sağlayacağı stratejik avantajı profesyonelce yorumla.
            """

            # 404 HATASINI ENGELLEYEN EN STABİL ADRES (v1)
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
            headers = {'Content-Type': 'application/json'}
            payload = {"contents": [{"parts": [{"text": prompt}]}]}

            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    ai_text = response.json()['candidates'][0]['content']['parts'][0]['text']
                    st.subheader("📋 Kişiselleştirilmiş Stratejik Yatırım Raporu")
                    st.info(ai_text)
                    st.balloons()
                else:
                    # Alternatif Beta kanalı (Eğer v1 yanıt vermezse)
                    url_beta = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
                    response_beta = requests.post(url_beta, headers=headers, json=payload)
                    if response_beta.status_code == 200:
                        st.info(response_beta.json()['candidates'][0]['content']['parts'][0]['text'])
                    else:
                        st.error(f"📡 API Bağlantı Hatası: {response_beta.status_code}. Lütfen API anahtarınızı (AIzaSy ile başlamalı) kontrol edin.")
            
            except Exception as e:
                st.error(f"Bağlantı koptu: {e}")
else:
    st.error("⚠️ Veri dosyası (fonlar.xlsx) bulunamadı!")
