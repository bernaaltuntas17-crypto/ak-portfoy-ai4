import streamlit as st
import pandas as pd
import glob
import requests
import json
import os

# --- 1. AYARLAR VE GÜVENLİK ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("⚠️ API Anahtarı Bulunamadı! Streamlit Secrets kısmına anahtarı ekleyin.")
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

# --- 3. DİL DESTEĞİ VE SÖZLÜK ---
lang = st.sidebar.selectbox("Sprache / Dil", ["Türkçe", "Almanca"])

if lang == "Almanca":
    T = {
        "head": "AK PORTFÖY INTELLIGENTE ANLAGEEMPFEHLUNG",
        "sub": "KI-Gesteuerte Investment-Plattform der nächsten Generation",
        "sidebar_h": "Anlagepräferenzen",
        "risk": "Risikopräferenz",
        "sektor": "Bevorzugter Sektor",
        "vade": "Anlagehorizont",
        "amount": "Investitionsbetrag (TL)",
        "btn": "Analyse Starten",
        "wait": "Strategie wird erstellt...",
        "report": "📋 Strategischer Analysebericht",
        "prompt_lang": "ALMANCA",
        "error": "📡 Verbindungsfehler. Bitte versuchen Sie es erneut."
    }
    sektor_opt = ["Technologie & KI", "Nachhaltigkeit", "Rohstoffe", "Immobilien", "Keine Präferenz"]
    risk_opt = ["Konservativ", "Ausgewogen", "Aggressiv"]
else:
    T = {
        "head": "AK PORTFÖY AKILLI YATIRIM TAVSİYESİ",
        "sub": "Yapay Zeka Destekli Gelecek Nesil Portföy Yönetimi",
        "sidebar_h": "Yatırım Tercihleri",
        "risk": "Risk Tercihi",
        "sektor": "Odak Sektör",
        "vade": "Vade Beklentisi",
        "amount": "Yatırım Tutarı (TL)",
        "btn": "Analizi Başlat",
        "wait": "Yatırım Stratejisi Oluşturuluyor...",
        "report": "📋 Stratejik Yatırım Raporu",
        "prompt_lang": "TÜRKÇE",
        "error": "📡 Bağlantı sorunu oluştu. Lütfen tekrar deneyin."
    }
    sektor_opt = ["Teknoloji ve Yapay Zeka", "Sürdürülebilirlik", "Değerli Madenler", "Gayrimenkul Yatırım Fonları", "Tercih Ettiğim Bir Sektör Yok"]
    risk_opt = ["Korumalı", "Dengeli", "Agresif"]

# --- 4. ARAYÜZ ---
col_l, col_m, col_r = st.columns([1, 2, 1])
with col_m:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=300)
    else:
        st.markdown("<h2 style='text-align:center; color:#D8232A;'>AK Portföy</h2>", unsafe_allow_html=True)

st.markdown(f"<h1 style='text-align:center; color:#D8232A;'>{T['head']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:#666; font-style:italic;'>{T['sub']}</p><hr>", unsafe_allow_html=True)

with st.sidebar:
    st.header(T['sidebar_h'])
    ans_risk = st.select_slider(T['risk'], options=risk_opt)
    ans_sektor = st.selectbox(T['sektor'], sektor_opt)
    ans_vade = st.selectbox(T['vade'], ["0-1 yıl/Jahr", "2-5 yıl/Jahre", "10+ yıl/Jahre"])
    amount_val = st.number_input(T['amount'], min_value=1000, value=50000)
    st.divider()
    analyze_btn = st.button(T['btn'], type="primary")

# --- 5. GERÇEK VE DERİN ANALİZ MOTORU ---
if df is not None:
    if analyze_btn:
        with st.spinner(T['wait']):
            # SENİN İSTEDİĞİN O DERİN VE TEKNİK ANALİZ TALİMATI
            prompt = f"""
            Sen Ak Portföy'de Kıdemli Yatırım Uzmanısın. Rapor dili {T['prompt_lang']} olmalıdır.
            Aşağıdaki verilere dayanarak, demo veya sahte metin olmadan GERÇEK bir analiz yap.
            
            MÜŞTERİ VERİLERİ:
            - Yatırım: {amount_val} TL | Risk: {ans_risk} | Sektör: {ans_sektor} | Vade: {ans_vade}
            
            ELİNDEKİ FON LİSTESİ:
            {df.to_string()}
            
            RAPORDA ŞUNLARI DETAYLI ŞEKİLDE AÇIKLA:
            1. Seçilen Ak Portföy fonlarının '{ans_risk}' risk profiline neden %100 uyduğunu teknik verilerle açıkla.
            2. '{ans_sektor}' sektöründeki fırsatların bu fonlar üzerinden nasıl değerlendirildiğini anlat.
            3. Seçilen her bir fonun diğerlerine göre avantajını getiri/risk puanı üzerinden kanıtla.
            4. Bu portföyün '{ans_vade}' sonunda yatırımcıya sağlayacağı stratejik katma değeri profesyonelce yorumla.
            """

            # 404 HATASINI ÇÖZEN EN GÜNCEL "V1" ENDPOINT'İ
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
            headers = {'Content-Type': 'application/json'}
            payload = {"contents": [{"parts": [{"text": prompt}]}]}

            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                if response.status_code == 200:
                    ai_text = response.json()['candidates'][0]['content']['parts'][0]['text']
                    st.subheader(T['report'])
                    st.info(ai_text)
                    st.balloons()
                else:
                    st.error(f"{T['error']} (Hata Kodu: {response.status_code})")
            except Exception as e:
                st.error(f"Bağlantı koptu: {e}")
else:
    st.error("⚠️ Veri dosyası (fonlar.xlsx) bulunamadı! Lütfen GitHub'a yükleyin.")
