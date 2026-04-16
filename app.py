import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import os
import glob

# --- 1. KURUMSAL YAPILANDIRMA ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="Ak Portföy | Akıllı Yatırım Tavsiyesi", layout="wide", initial_sidebar_state="expanded")

# Ak Portföy KIRMIZI VE KOYU PANEL Teması (CSS)
st.markdown("""
<style>
    .main { background-color: #ffffff; }
    [data-testid="stSidebar"] {
        background-color: #1e1e1e; 
    }
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2 {
        color: #ffffff !important;
    }
    .stButton>button {
        background-color: #D8232A;
        color: white;
        border-radius: 8px;
        width: 100%;
        border: none;
        font-weight: bold;
        height: 3em;
    }
    .stButton>button:hover {
        background-color: #ffffff;
        color: #D8232A;
        border: 1px solid #D8232A;
    }
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

# --- 3. DİL VE LOGO ---
lang = st.sidebar.selectbox("Sprache / Dil", ["Türkçe", "Almanca"])
T = {
    "head": "AK PORTFÖY AKILLI YATIRIM TAVSİYESİ" if lang == "Türkçe" else "AK PORTFÖY INTELLIGENTE ANLAGEEMPFEHLUNG",
    "sub": "Yapay Zeka Destekli Gelecek Nesil Portföy Yönetimi" if lang == "Türkçe" else "KI-Gesteuerte Investment-Plattform",
    "btn": "Analizi Başlat" if lang == "Türkçe" else "Analyse Starten"
}

col_l, col_m, col_r = st.columns([1, 2, 1])
with col_m:
    try: st.image("logo.png", width=300)
    except: st.write("Logo Yükleniyor...")

st.markdown(f"""
    <div style="text-align: center; padding-bottom: 20px;">
        <h1 style="color: #D8232A; font-weight: bold; margin-bottom: 0;">{T['head']}</h1>
        <p style="color: #666; font-size: 1.1em; font-style: italic;">{T['sub']}</p>
        <hr style="width: 50%; margin: auto;">
    </div>
    """, unsafe_allow_html=True)

# --- 4. YATIRIM TERCİHLERİ (SOL PANEL) ---
with st.sidebar:
    st.header("Yatırım Tercihleri")
    ans_likidite = st.selectbox("Likidite Tercihi", ["T+0", "T+1", "T+2", "T+3"])
    ans_para = st.radio("Para Birimi", ["Türk Lirası (TL)", "ABD Doları (USD)", "Euro (EUR)", "Pound (GBP)"])
    ans_faiz = st.radio("Faiz Hassasiyeti", ["Faizsiz", "Faizli"])
    ans_vade = st.selectbox("Vade Süresi Tercihi", ["0-1 yıl", "2-5 yıl", "10+ yıl"])
    ans_risk = st.select_slider("Risk Tercihi", options=["Korumalı", "Dengeli", "Agresif"])
    
    sektor_options = [
        "Teknoloji ve Yapay Zeka (Yüksek büyüme odaklı)",
        "Sürdürülebilirlik ve Yeşil Enerji (ESG)",
        "Değerli Madenler ve Emtialar (Altın, Gümüş, Petrol)",
        "Gayrimenkul Yatırım Fonları (GYF)",
        "Tercih Ettiğim Bir Sektör Yok"
    ]
    ans_sektor = st.selectbox("Yatırım için Tercih Edilecek Sektör", sektor_options)
    amount = st.number_input("Yatırım Tutarı", min_value=1000, value=50000)
    
    st.divider()
    analyze_btn = st.button(T['btn'], type="primary")

# --- 5. ANALİZ VE RAPOR ---
if df is not None:
    if analyze_btn:
        with st.spinner('Strateji Oluşturuluyor...'):
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""Bir Analist olarak profesyonel rapor yaz:
            Tutar: {amount} {ans_para}, Likidite: {ans_likidite}, Faiz: {ans_faiz}, 
            Vade: {ans_vade}, Risk: {ans_risk}, Sektör: {ans_sektor}.
            Veriler: {df.to_string()}"""
            
            res = model.generate_content(prompt)
            st.subheader("📋 Kişiselleştirilmiş Stratejik Analiz Raporu")
            st.info(res.text)
            
            if '1Y (%)' in df.columns:
                fig = px.bar(df, x='Kodu', y='1Y (%)', color='1Y (%)', color_continuous_scale=['#FFCCCC', '#D8232A'])
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("")
        st.info("Lütfen kriterlerinizi belirledikten sonra sol taraftaki 'Analizi Başlat' butonuna tıklayın.")
