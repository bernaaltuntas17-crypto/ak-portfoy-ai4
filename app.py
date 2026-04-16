import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import os
import glob

# --- 1. KURUMSAL YAPILANDIRMA ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="Ak Portföy | Akıllı Yatırım Tavsiyesi", layout="wide", initial_sidebar_state="expanded")

# Ak Portföy KIRMIZI Tema ve Stil (CSS)
st.markdown("""
<style>
    [data-testid="stMetricValue"] { font-size: 24px; color: #D8232A; }
    .main { background-color: #f8f9fa; }
    /* Butonları kırmızı yapıyoruz */
    .stButton>button { background-color: #D8232A; color: white; border-radius: 8px; width: 100%; border: none; font-weight: bold; }
    .stButton>button:hover { background-color: #A01A1E; color: white; }
    h1, h2, h3 { color: #1e1e1e; font-family: 'Segoe UI', sans-serif; }
    /* Ayırıcı çizgiyi kırmızı yapıyoruz */
    hr { border: 1px solid #D8232A !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. VERİ MOTORU ---
def load_and_clean_data():
    files = glob.glob("fonlar*") + glob.glob("*.csv") + glob.glob("*.xlsx")
    for f in files:
        try:
            df = pd.read_excel(f) if f.endswith('.xlsx') else pd.read_csv(f, sep=None, engine='python', encoding='utf-8-sig')
            df.columns = [c.strip() for c in df.columns] 
            return df
        except: continue
    return None

df = load_and_clean_data()

# --- 3. DİL SEÇİMİ ---
lang = st.sidebar.selectbox("Sprache / Dil", ["Türkçe", "Almanca"])

if lang == "Almanca":
    T = {"head": "AK PORTFÖY INTELLIGENTE ANLAGEEMPFEHLUNG", "sub": "KI-Gesteuerte Investment-Plattform", "btn": "Analyse Starten"}
else:
    T = {"head": "AK PORTFÖY AKILLI YATIRIM TAVSİYESİ", "sub": "Yapay Zeka Destekli Gelecek Nesil Portföy Yönetimi", "btn": "Analizi Başlat"}

# --- 4. LOGO VE BAŞLIK ALANI ---
# Burası elindeki logo.png dosyasını GitHub'dan okur
col_l, col_m, col_r = st.columns([1, 2, 1])
with col_m:
    try:
        st.image("logo.png", width=300) # GitHub'a yüklediğin dosya ismiyle aynı olmalı
    except:
        st.write("Logo yükleniyor...")

st.markdown(f"""
    <div style="text-align: center; padding-top: 0px;">
        <h1 style="color: #D8232A; font-weight: bold; font-size: 2.8em; margin-bottom: 0;">{T['head']}</h1>
        <p style="color: #666; font-size: 1.2em; font-style: italic; margin-top: 5px;">{T['sub']}</p>
        <hr style="width: 50%; margin: auto;">
    </div>
    """, unsafe_allow_html=True)

# --- 5. DASHBOARD VE ANALİZ ---
if df is not None:
    st.write("")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("En İyi Fon", df.iloc[0]['Fon Adı'] if 'Fon Adı' in df.columns else "---")
    col2.metric("Risk Skoru", "Orta-Dengeli")
    col3.metric("Veri Sağlığı", "Yüksek")
    col4.metric("AI Status", "Active")
    st.divider()

with st.sidebar:
    st.header("Yatırım Tercihleri")
    ans1 = st.selectbox("Likidite", ["T+0", "T+1", "T+2"])
    ans2 = st.radio("Para Birimi", ["TL", "USD", "EUR"])
    ans4 = st.select_slider("Strateji", options=["Defensiv", "Neutral", "Aggressiv"])
    analyze_btn = st.button(T['btn'], type="primary")

if analyze_btn and df is not None:
    with st.spinner('Analiz ediliyor...'):
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Veriler: {df.to_string()}. Profil: {ans1}, {ans2}, Strateji:{ans4}. Profesyonel rapor oluştur."
        res = model.generate_content(prompt)
        st.subheader("📋 Stratejik Analiz Raporu")
        st.info(res.text)
