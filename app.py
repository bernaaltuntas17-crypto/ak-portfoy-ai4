import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import os
import glob

# --- 1. KURUMSAL YAPILANDIRMA ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="Ak Portföy | Akıllı Yatırım Tavsiyesi", layout="wide", initial_sidebar_state="expanded")

# Ak Portföy KIRMIZI Tema ve Stil
st.markdown("""
<style>
    [data-testid="stMetricValue"] { font-size: 24px; color: #D8232A; }
    .main { background-color: #f8f9fa; }
    .stButton>button { background-color: #D8232A; color: white; border-radius: 8px; width: 100%; border: none; font-weight: bold; height: 3em; }
    .stButton>button:hover { background-color: #A01A1E; color: white; }
    h1, h2, h3 { color: #1e1e1e; font-family: 'Segoe UI', sans-serif; }
    hr { border: 1px solid #D8232A !important; }
    .stRadio > label, .stSelectbox > label { font-weight: bold; color: #1e1e1e; }
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
T = {
    "head": "AK PORTFÖY AKILLI YATIRIM TAVSİYESİ" if lang == "Türkçe" else "AK PORTFÖY INTELLIGENTE ANLAGEEMPFEHLUNG",
    "sub": "Yapay Zeka Destekli Gelecek Nesil Portföy Yönetimi" if lang == "Türkçe" else "KI-Gesteuerte Investment-Plattform",
    "btn": "Analizi Başlat" if lang == "Türkçe" else "Analyse Starten"
}

# --- 4. LOGO VE BAŞLIK ---
col_l, col_m, col_r = st.columns([1, 2, 1])
with col_m:
    try:
        st.image("logo.png", width=300)
    except:
        st.write("Logo Yükleniyor...")

st.markdown(f"""
    <div style="text-align: center;">
        <h1 style="color: #D8232A; font-weight: bold; margin-bottom: 0;">{T['head']}</h1>
        <p style="color: #666; font-size: 1.1em; font-style: italic;">{T['sub']}</p>
        <hr style="width: 50%; margin: auto;">
    </div>
    """, unsafe_allow_html=True)

# --- 5. YENİ YATIRIM TERCİHLERİ (SOL PANEL) ---
with st.sidebar:
    st.header("Yatırım Tercihleri")
    
    # 1. Likidite
    ans_likidite = st.selectbox("Likidite Tercihi", ["T+0", "T+1", "T+2", "T+3"])
    
    # 2. Para Birimi
    ans_para = st.radio("Para Birimi", ["Türk Lirası (TL)", "ABD Doları (USD)", "Euro (EUR)", "Pound (GBP)"])
    
    # 3. Faiz Hassasiyeti
    ans_faiz = st.radio("Faiz Hassasiyeti", ["Faizsiz", "Faizli"])
    
    # 4. Vade Süresi
    ans_vade = st.selectbox("Vade Süresi Tercihi", ["0-1 yıl", "2-5 yıl", "10+ yıl"])
    
    # 5. Risk Tercihi
    ans_risk = st.select_slider("Risk Tercihi", options=["Korumalı", "Dengeli", "Agresif"])
    
    # 6. Sektör Tercihi
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

# --- 6. KPI VE ANALİZ ---
if df is not None:
    st.write("")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("En İyi Fon", df.iloc[0]['Fon Adı'] if 'Fon Adı' in df.columns else "---")
    c2.metric("Risk Skoru", ans_risk)
    c3.metric("Vade", ans_vade)
    c4.metric("Sektör", "Seçildi")
    st.divider()

if analyze_btn and df is not None:
    with st.spinner('Yapay Zeka Strateji Oluşturuyor...'):
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Yapay zekaya gönderilen detaylı komut (Prompt)
        prompt = f"""
        Bir Portföy Analisti olarak şu kriterlere göre profesyonel rapor oluştur:
        Yatırım Tutarı: {amount} {ans_para}
        Likidite: {ans_likidite}
        Vade: {ans_vade}
        Risk Seviyesi: {ans_risk}
        Faiz Hassasiyeti: {ans_faiz}
        Tercih Edilen Sektör: {ans_sektor}
        
        Mevcut Fon Verileri: {df.to_string()}
        
        Lütfen bu kriterlere en uygun Ak Portföy fonlarını öner ve nedenlerini açıkla.
        """
        
        res = model.generate_content(prompt)
        st.subheader("📋 Kişiselleştirilmiş Stratejik Analiz Raporu")
        st.info(res.text)

        # Grafik
        if '1Y (%)' in df.columns:
            fig = px.bar(df, x='Kodu', y='1Y (%)', color='1Y (%)', color_continuous_scale=['#FFCCCC', '#D8232A'])
            st.plotly_chart(fig, use_container_width=True)
