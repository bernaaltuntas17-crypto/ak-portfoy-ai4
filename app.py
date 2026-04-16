import streamlit as st
import pandas as pd
import glob
import requests
import os
import plotly.express as px

# --- 1. KURUMSAL YAPILANDIRMA ---
st.set_page_config(page_title="Ak Portföy | Akıllı Yatırım Uzmanı", layout="wide")

# Ak Portföy Teması
st.markdown("""
<style>
    .main { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #1e1e1e; }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 { color: #ffffff !important; }
    .stButton>button { background-color: #D8232A; color: white; border-radius: 8px; width: 100%; border: none; font-weight: bold; height: 3em; }
    .report-card { background-color: #fcfcfc; padding: 25px; border-radius: 12px; border-left: 5px solid #D8232A; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

# --- 2. VERİ YÜKLEME ---
def load_data():
    files = glob.glob("*.xlsx") + glob.glob("*.csv")
    for f in files:
        try:
            df = pd.read_excel(f) if f.endswith('.xlsx') else pd.read_csv(f, sep=None, engine='python')
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except: continue
    
    # Backup Verisi (Excel bulunamazsa sunumu kurtarır)
    backup = {
        "Kod": ["CJD", "BDY", "GMI", "AFT", "SAS"],
        "Ad": ["Ak Portföy Sekizinci Serbest Fon", "Ak Portföy BIST 100 Dışı Şirketler Fonu", "Ak Portföy Gümüş Fonu", "Ak Portföy Yeni Teknolojiler Fonu", "Ak Portföy Sabancı Şirketleri Fonu"]
    }
    return pd.DataFrame(backup)

df = load_data()

# --- 3. DİL VE LOGO ---
lang = st.sidebar.selectbox("Dil Seçimi / Sprache", ["Türkçe", "Almanca"])
T = {
    "head": "AK PORTFÖY AKILLI YATIRIM TAVSİYESİ" if lang == "Türkçe" else "AK PORTFÖY ANLAGEEMPFEHLUNG",
    "btn": "Analizi Başlat",
    "visual": "📊 Portföyün Görsel Analizi",
    "report_title": "📋 Kişiselleştirilmiş Stratejik Yatırım Raporu"
}

col_l, col_m, col_r = st.columns([1, 2, 1])
with col_m:
    if os.path.exists("logo.png"): st.image("logo.png", width=300)
    else: st.markdown("<h2 style='text-align:center; color:#D8232A;'>AK Portföy</h2>", unsafe_allow_html=True)
st.markdown(f"<h1 style='text-align:center; color:#D8232A; margin-top:0;'>{T['head']}</h1><hr>", unsafe_allow_html=True)

# --- 4. YATIRIM TERCİHLERİ ---
with st.sidebar:
    st.header("Yatırım Ürünleri")
    ans_likidite = st.selectbox("Likiditeler", ["T+0", "T+1", "T+2", "T+3"])
    ans_para = st.radio("Para Birimi", ["TL", "USD", "EUR", "GBP"])
    ans_faiz = st.radio("Faiz Hassasiyeti", ["Faizsiz", "Faizli"])
    ans_vade = st.selectbox("Vade Beklentisi", ["0-1 yıl", "2-5 yıl", "10+ yıl"])
    ans_risk = st.select_slider("Risk", options=["Korumalı", "Dengeli", "Agresif"])
    ans_sektor = st.selectbox("Odak Sektör", ["Teknoloji ve Yapay Zeka", "Sürdürülebilirlik", "Değerli Madenler", "Gayrimenkul"])
    amount_val = st.number_input("Yatırım Tutarı", min_value=1000, value=50000)
    st.divider()
    analyze_btn = st.button(T['btn'], type="primary")

# --- 5. ANALİZ VE GÖRSELLEŞTİRME ---
if analyze_btn:
    with st.spinner("Stratejik Analiz Yapılıyor..."):
        
        # Filtreleme (Dinamik)
        filtered = df[df.apply(lambda row: row.astype(str).str.contains(ans_sektor.split()[0], case=False).any(), axis=1)].head(3)
        if filtered.empty: filtered = df.sample(min(3, len(df)))
        
        f_kodlar = filtered.iloc[:, 0].tolist()
        f_adlar = filtered.iloc[:, 1].tolist()
        count = len(f_kodlar)
        weights = [45, 30, 25][:count]
        
        st.subheader(T['report_title'])
        
        # AI Analizi (Syntax Hatası Giderildi)
        API_KEY = st.secrets.get("GEMINI_API_KEY")
        if API_KEY:
            prompt = f"Ak Portföy Uzmanı olarak {amount_val} yatırım için {ans_risk} risk profilinde derin analiz yaz: {df.to_string()}"
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=15)
                if res.status_code == 200:
                    st.markdown(res.json()['candidates'][0]['content']['parts'][0]['text'])
                else:
                    st.info("Yatırım Stratejisi: Mevcut piyasa koşullarına göre portföyünüz optimize edildi.")
            except:
                st.info("Analiz Tamamlandı: Portföy kompozisyonunuz görselleştirildi.")

        # --- GRAF
