import streamlit as st
import pandas as pd
import glob
import requests
import json
import os

# --- 1. AYARLAR VE GÜVENLİK ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("⚠️ API Anahtarı Secrets kısmında bulunamadı!")
    st.stop()

API_KEY = st.secrets["GEMINI_API_KEY"]

st.set_page_config(page_title="Ak Portföy | Akıllı Yatırım Tavsiyesi", layout="wide")

# Ak Portföy Kurumsal Kırmızı & Siyah Teması
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
    files = glob.glob("fonlar*") + glob.glob("*.csv") + glob.glob("*.xlsx")
    for f in files:
        try:
            return pd.read_excel(f) if f.endswith('.xlsx') else pd.read_csv(f, sep=None, engine='python', encoding='utf-8-sig')
        except: continue
    return None

df = load_data()

# --- 3. DİL DESTEĞİ ---
lang = st.sidebar.selectbox("Sprache / Dil", ["Türkçe", "Almanca"])
T = {
    "head": "AK PORTFÖY AKILLI YATIRIM TAVSİYESİ" if lang == "Türkçe" else "AK PORTFÖY INTELLIGENTE ANLAGEEMPFEHLUNG",
    "btn": "Analizi Başlat" if lang == "Türkçe" else "Analyse Starten",
    "wait": "Yatırım Uzmanı Analiz Yapıyor..." if lang == "Türkçe" else "KI analysiert...",
    "report": "📋 Stratejik Yatırım Raporu" if lang == "Türkçe" else "📋 Strategischer Bericht"
}

# Logo ve Başlık
col_l, col_m, col_r = st.columns([1, 2, 1])
with col_m:
    if os.path.exists("logo.png"): st.image("logo.png", width=300)
    else: st.markdown("<h2 style='text-align:center; color:#D8232A;'>AK Portföy</h2>", unsafe_allow_html=True)
st.markdown(f"<h1 style='text-align:center; color:#D8232A;'>{T['head']}</h1><hr>", unsafe_allow_html=True)

# --- 4. YATIRIM TERCİHLERİ ---
with st.sidebar:
    st.header("Yatırım Tercihleri")
    ans_likidite = st.selectbox("Likidite Tercihi", ["T+0", "T+1", "T+2", "T+3"])
    ans_para = st.radio("Para Birimi", ["TL", "USD", "EUR", "GBP"])
    ans_faiz = st.radio("Faiz Hassasiyeti", ["Faizsiz", "Faizli"])
    ans_vade = st.selectbox("Vade Beklentisi", ["0-1 yıl", "2-5 yıl", "10+ yıl"])
    ans_risk = st.select_slider("Risk Tercihi", options=["Korumalı", "Dengeli", "Agresif"])
    ans_sektor = st.selectbox("Odak Sektör", ["Teknoloji ve Yapay Zeka", "Sürdürülebilirlik", "Değerli Madenler", "Gayrimenkul"])
    amount_val = st.number_input("Yatırım Tutarı", min_value=1000, value=50000)
    st.divider()
    analyze_btn = st.button(T['btn'], type="primary")

# --- 5. HATA GEÇİRMEZ ANALİZ MOTORU ---
if df is not None:
    if analyze_btn:
        with st.spinner(T['wait']):
            # DETAYLI ANALİZ TALİMATI
            prompt = f"""
            Sen Ak Portföy Kıdemli Yatırım Uzmanısın. Müşterinin {amount_val} {ans_para} tutarındaki yatırımı için, 
            {ans_risk} risk profili ve {ans_sektor} sektörüne özel GERÇEK bir analiz yap.
            Likidite: {ans_likidite}, Faiz Hassasiyeti: {ans_faiz}, Vade: {ans_vade}.
            
            ELİNDEKİ FON VERİLERİ (SADECE BUNLARI KULLAN):
            {df.to_string()}
            
            RAPORDA ŞUNLARI AÇIKLA:
            1. Bu fonları NEDEN seçtiğini teknik (getiri/risk) verileriyle kanıtla.
            2. Seçilen sektörün piyasa avantajlarını anlat.
            3. Ak Portföy'ün bu stratejisindeki farkını vurgula.
            """

            # HATA ENGELLEYİCİ: 3 farklı yolu da otomatik dener
            endpoints = [
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}",
                f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}",
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"
            ]
            
            success = False
            for url in endpoints:
                try:
                    response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=25)
                    if response.status_code == 200:
                        res_json = response.json()
                        ai_text = res_json['candidates'][0]['content']['parts'][0]['text']
                        st.subheader(T['report'])
                        st.info(ai_text)
                        st.balloons()
                        success = True
                        break
                except: continue
            
            if not success:
                st.error("📡 Sunucu bağlantısı kurulamadı. Lütfen API anahtarınızı (AIzaSy...) tekrar kontrol edin.")
else:
    st.error("⚠️ Veri dosyası (fonlar.xlsx) bulunamadı!")
