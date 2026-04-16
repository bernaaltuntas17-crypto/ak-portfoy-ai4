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
    T = {"head": "AK PORTFÖY INTELLIGENTE ANLAGEEMPFEHLUNG", "sub": "KI-Gesteuerte Investment-Plattform", "btn": "Analyse Starten", "wait": "Strategie wird erstellt...", "report": "📋 Strategischer Analysebericht"}
    sektor_opt = ["Technologie & KI", "Nachhaltigkeit", "Rohstoffe", "Immobilien", "Keine Präferenz"]
else:
    T = {"head": "AK PORTFÖY AKILLI YATIRIM TAVSİYESİ", "sub": "Yapay Zeka Destekli Gelecek Nesil Portföy Yönetimi", "btn": "Analizi Başlat", "wait": "Yatırım Stratejisi Oluşturuluyor...", "report": "📋 Kişiselleştirilmiş Stratejik Analiz Raporu"}
    sektor_opt = ["Teknoloji ve Yapay Zeka", "Sürdürülebilirlik", "Değerli Madenler", "Gayrimenkul Yatırım Fonları", "Farketmez"]

# --- 4. ARAYÜZ VE EKSİK KALAN TÜM ALANLAR (GERİ GELDİ) ---
col_l, col_m, col_r = st.columns([1, 2, 1])
with col_m:
    if os.path.exists("logo.png"): st.image("logo.png", width=300)
    else: st.markdown("<h2 style='text-align:center; color:#D8232A;'>AK Portföy</h2>", unsafe_allow_html=True)

st.markdown(f"<h1 style='text-align:center; color:#D8232A;'>{T['head']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:#666; font-style:italic;'>{T['sub']}</p><hr>", unsafe_allow_html=True)

with st.sidebar:
    st.header("Yatırım Tercihleri")
    ans_likidite = st.selectbox("Likidite Tercihi", ["T+0", "T+1", "T+2", "T+3"])
    ans_para = st.radio("Para Birimi", ["TL", "USD", "EUR", "GBP"])
    ans_faiz = st.radio("Faiz Hassasiyeti", ["Faizsiz", "Faizli"])
    ans_vade = st.selectbox("Vade Beklentisi", ["0-1 yıl", "2-5 yıl", "10+ yıl"])
    ans_risk = st.select_slider("Risk Tercihi", options=["Korumalı", "Dengeli", "Agresif"])
    ans_sektor = st.selectbox("Odak Sektör", sektor_opt)
    amount_val = st.number_input("Yatırım Tutarı (TL)", min_value=1000, value=50000)
    st.divider()
    analyze_btn = st.button(T['btn'], type="primary")

# --- 5. GERÇEK VE DERİN ANALİZ MOTORU ---
if df is not None:
    if analyze_btn:
        with st.spinner(T['wait']):
            prompt = f"""
            Sen Ak Portföy'de Kıdemli Yatırım Uzmanısın. Müşterinin {amount_val} TL tutarındaki yatırımı için, 
            {ans_risk} risk profili, {ans_sektor} sektörü, {ans_likidite} likidite ve {ans_faiz} tercihlerine özel DERİN ANALİZ yap. 
            RAPORDA ŞUNLARI AÇIKLA:
            1. Veri setindeki fonlardan hangisini NEDEN seçtin?
            2. Bu fonun müşterinin risk ve vade ({ans_vade}) tercihiyle nasıl örtüştüğünü kanıtla.
            3. Seçtiğin sektörün ({ans_sektor}) Ak Portföy stratejisindeki önemini anlat.
            Veriler: {df.to_string()}
            """
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
            try:
                response = requests.post(url, headers={'Content-Type': 'application/json'}, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
                if response.status_code == 200:
                    ai_text = response.json()['candidates'][0]['content']['parts'][0]['text']
                    st.
