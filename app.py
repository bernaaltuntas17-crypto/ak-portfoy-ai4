import streamlit as st
import pandas as pd
import glob
import requests
import json
import os

# --- 1. AYARLAR VE GÜVENLİK ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("⚠️ API Anahtarı Secrets kısmında bulunamadı! Lütfen AIzaSy ile başlayan anahtarı ekleyin.")
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
    .stButton>button:hover { background-color: #ffffff; color: #D8232A; border: 1px solid #D8232A; }
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

if lang == "Almanca":
    T = {"head": "AK PORTFÖY ANLAGEEMPFEHLUNG", "btn": "Analyse Starten", "wait": "Strategie wird erstellt...", "report": "📋 Strategischer Rapor"}
    sektor_opt = ["Technologie", "Nachhaltigkeit", "Rohstoffe", "Immobilien", "Egal"]
    risk_opt = ["Konservativ", "Ausgewogen", "Aggressiv"]
else:
    T = {"head": "AK PORTFÖY AKILLI YATIRIM TAVSİYESİ", "btn": "Analizi Başlat", "wait": "Analiz Yapılıyor...", "report": "📋 Stratejik Yatırım Raporu"}
    sektor_opt = ["Teknoloji ve Yapay Zeka", "Sürdürülebilirlik", "Değerli Madenler", "Gayrimenkul", "Farketmez"]
    risk_opt = ["Korumalı", "Dengeli", "Agresif"]

# Logo ve Başlık Alanı
col_l, col_m, col_r = st.columns([1, 2, 1])
with col_m:
    if os.path.exists("logo.png"): st.image("logo.png", width=300)
    else: st.markdown("<h2 style='text-align:center; color:#D8232A;'>AK Portföy</h2>", unsafe_allow_html=True)

st.markdown(f"<h1 style='text-align:center; color:#D8232A;'>{T['head']}</h1><hr>", unsafe_allow_html=True)

# --- 4. YATIRIM TERCİHLERİ (İSTEDİĞİN TÜM ALANLAR) ---
with st.sidebar:
    st.header("Yatırım Tercihleri")
    ans_likidite = st.selectbox("Likidite Tercihi", ["T+0", "T+1", "T+2", "T+3"])
    ans_para = st.radio("Para Birimi", ["TL", "USD", "EUR", "GBP"])
    ans_faiz = st.radio("Faiz Hassasiyeti", ["Faizsiz", "Faizli"])
    ans_vade = st.selectbox("Vade Beklentisi", ["0-1 yıl", "2-5 yıl", "10+ yıl"])
    ans_risk = st.select_slider("Risk Tercihi", options=risk_opt)
    ans_sektor = st.selectbox("Odak Sektör", sektor_opt)
    amount_val = st.number_input("Yatırım Tutarı (TL)", min_value=1000, value=50000)
    st.divider()
    analyze_btn = st.button(T['btn'], type="primary")

# --- 5. HATA GEÇİRMEZ ANALİZ MOTORU ---
if df is not None:
    if analyze_btn:
        with st.spinner(T['wait']):
            prompt = f"""
            Sen Ak Portföy Kıdemli Yatırım Uzmanısın. Müşterinin {amount_val} TL yatırımı için rapor hazırla.
            Dil: {lang} | Risk: {ans_risk} | Sektör: {ans_sektor} | Vade: {ans_vade} | Likidite: {ans_likidite} | Faiz: {ans_faiz}
            ELİNDEKİ FON VERİLERİ: {df.to_string()}
            
            GÖREVİN: 
            1. Bu tercihlere en uygun fonu neden seçtiğini detaylıca açıkla.
            2. Seçtiğin fonun getiri/risk oranının müşterinin '{ans_risk}' profiline neden tam uyduğunu kanıtla.
            3. Piyasa koşullarına göre sektörel analizini yap.
            """

            # HATA ENGELLEYİCİ: Üç farklı adresi de tek tek deneyecek
            endpoints = [
                f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}",
                f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={API_KEY}",
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
            ]
            
            success = False
            for url in endpoints:
                try:
                    response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
                    if response.status_code == 200:
                        ai_text = response.json()['candidates'][0]['content']['parts'][0]['text']
                        st.subheader(T['report'])
                        st.info(ai_text)
                        st.balloons()
                        success = True
                        break
                except: continue
            
            if not success:
                st.error("📡 Tüm bağlantı yolları denendi ama sonuç alınamadı. Lütfen API anahtarının doğruluğunu ve internetini kontrol et.")
else:
    st.error("⚠️ Veri dosyası bulunamadı!")
