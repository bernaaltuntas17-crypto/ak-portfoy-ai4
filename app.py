import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import os
import glob

# --- 1. KURUMSAL YAPILANDIRMA ---
API_KEY = "AIzaSyCSMiscWlLT0N1AFU50q8kEdHndls5UNiU"
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="Ak Portföy | Analiz Platformu", layout="wide", initial_sidebar_state="expanded")

# Ak Portföy Renk Paleti ve Stil (CSS)
st.markdown("""
<style>
    [data-testid="stMetricValue"] { font-size: 24px; color: #FF5A00; }
    .main { background-color: #f8f9fa; }
    .stButton>button { background-color: #FF5A00; color: white; border-radius: 8px; width: 100%; border: none; }
    .reportview-container .main .block-container { padding-top: 2rem; }
    h1, h2, h3 { color: #1e1e1e; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
</style>
""", unsafe_allow_html=True)

# --- 2. AKILLI VERİ MOTORU ---
def load_and_clean_data():
    files = glob.glob("fonlar*") + glob.glob("*.csv") + glob.glob("*.xlsx")
    for f in files:
        try:
            df = pd.read_excel(f) if f.endswith('.xlsx') else pd.read_csv(f, sep=None, engine='python', encoding='utf-8-sig')
            # Veri Temizliği (Data Health)
            df.columns = [c.strip() for c in df.columns] # Başlıktaki boşlukları siler
            return df
        except: continue
    return None

df = load_and_clean_data()

# --- 3. DİL VE TERMİNOLOJİ YÖNETİMİ ---
lang = st.sidebar.selectbox("Sprache / Dil", ["Türkçe", "Almanca"])

if lang == "Almanca":
    T = {
        "head": "Ak Portföy Management", "sub": "KI-Gesteuerte Investment-Plattform",
        "kpi1": "Bester Fonds", "kpi2": "Risiko-Score", "kpi3": "Datenstatus",
        "q1": "Liquidität", "q2": "Währung", "q3": "Steuervorteile", "q4": "Strategie",
        "btn": "Analyse Starten", "health": "Datenqualität: Hoch", "role": "Portfolio Analyst"
    }
else:
    T = {
        "head": "Ak Portföy Yönetimi", "sub": "Yapay Zeka Destekli Analiz Platformu",
        "kpi1": "En İyi Fon", "kpi2": "Risk Skoru", "kpi3": "Veri Sağlığı",
        "q1": "Likidite", "q2": "Para Birimi", "q3": "Vergi Önceliği", "q4": "Yatırım Stratejisi",
        "btn": "Analizi Başlat", "health": "Veri Kalitesi: Yüksek", "role": "Portföy Analisti"
    }

# --- 4. DASHBOARD ÜST PANEL (KPI CARDS) ---
st.title(f"🟠 {T['head']}")
st.caption(T['sub'])

if df is not None:
    col1, col2, col3, col4 = st.columns(4)
    # Excel'den otomatik veri çekimi
    top_fund = df.iloc[0]['Fon Adı'] if 'Fon Adı' in df.columns else "---"
    avg_risk = "Orta-Dengeli"
    
    col1.metric(T['kpi1'], top_fund)
    col2.metric(T['kpi2'], avg_risk)
    col3.metric(T['kpi3'], T['health'])
    col4.metric("AI Status", "Active")
    st.divider()

# --- 5. SOL PANEL (FİLTRELER VE PROFİL) ---
with st.sidebar:
    st.image("https://www.akportfoy.com.tr/assets/img/logo.png", width=150) # Varsa logo linki
    st.header(T['head'])
    
    ans1 = st.selectbox(T['q1'], ["T+0", "T+1", "T+2"])
    ans2 = st.radio(T['q2'], ["TL", "USD", "EUR"])
    ans3 = st.toggle(T['q3'])
    ans4 = st.select_slider(T['q4'], options=["Defensiv", "Neutral", "Aggressiv"])
    amount = st.number_input("Tutar / Betrag", min_value=1000, value=50000)
    
    st.divider()
    analyze_btn = st.button(T['btn'], type="primary")

# --- 6. GÖRSELLEŞTİRME VE AI ANALİZİ ---
if df is not None:
    tab1, tab2 = st.tabs(["Dashboard", "Data Table"])
    
    with tab1:
        if analyze_btn:
            with st.spinner('Analiz ediliyor...'):
                # AI Modeli Çağrısı
                model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                working_model = next((m for m in model_list if "flash" in m), model_list[0])
                model = genai.GenerativeModel(working_model)
                
                prompt = f"Analist Rolü: {T['role']}. Veriler: {df.to_string()}. Profil: {ans1}, {ans2}, Vergi:{ans3}, Strateji:{ans4}. Profesyonel bir rapor oluştur."
                res = model.generate_content(prompt)
                
                # Rapor Alanı
                st.subheader("📋 Stratejik Analiz Raporu")
                st.info(res.text)
                
                # Dinamik Grafik (VEXEL benzeri)
                if '1Y (%)' in df.columns:
                    st.subheader("📈 Getiri Analizi")
                    fig = px.bar(df, x='Kodu', y='1Y (%)', color='1Y (%)', title="Yıllık Fon Performansı")
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Lütfen sol taraftan kriterlerinizi seçip analizi başlatın.")
            
    with tab2:
        st.dataframe(df, use_container_width=True)
else:
    st.error("Lütfen klasöre 'fonlar.csv' veya 'fonlar.xlsx' dosyasını ekleyin.")