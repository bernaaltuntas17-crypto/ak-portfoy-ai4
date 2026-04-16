import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import os
import glob

# --- 1. KURUMSAL YAPILANDIRMA ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="Ak Portföy | Akıllı Yatırım Tavsiyesi", layout="wide", initial_sidebar_state="expanded")

# Ak Portföy Kırmızı Tema ve Stil (CSS)
st.markdown("""
<style>
    /* Metrik değerlerini ve butonları kırmızı yapıyoruz */
    [data-testid="stMetricValue"] { font-size: 24px; color: #D8232A; }
    .main { background-color: #f8f9fa; }
    .stButton>button { background-color: #D8232A; color: white; border-radius: 8px; width: 100%; border: none; font-weight: bold; }
    .stButton>button:hover { background-color: #A01A1E; color: white; }
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
            df.columns = [c.strip() for c in df.columns] 
            return df
        except: continue
    return None

df = load_and_clean_data()

# --- 3. DİL VE TERMİNOLOJİ YÖNETİMİ ---
lang = st.sidebar.selectbox("Sprache / Dil", ["Türkçe", "Almanca"])

if lang == "Almanca":
    T = {
        "head": "AK PORTFÖY INTELLIGENTE ANLAGEEMPFEHLUNG", 
        "sub": "KI-Gesteuerte Investment- und Analyseplattform",
        "kpi1": "Bester Fonds", "kpi2": "Risiko-Score", "kpi3": "Datenstatus",
        "q1": "Liquidität", "q2": "Währung", "q3": "Steuervorteile", "q4": "Strategie",
        "btn": "Analyse Starten", "health": "Datenqualität: Hoch", "role": "Portfolio Analyst"
    }
else:
    T = {
        "head": "AK PORTFÖY AKILLI YATIRIM TAVSİYESİ", 
        "sub": "Yapay Zeka Destekli Gelecek Nesil Portföy Yönetimi",
        "kpi1": "En İyi Fon", "kpi2": "Risk Skoru", "kpi3": "Veri Sağlığı",
        "q1": "Likidite", "q2": "Para Birimi", "q3": "Vergi Önceliği", "q4": "Yatırım Stratejisi",
        "btn": "Analizi Başlat", "health": "Veri Kalitesi: Yüksek", "role": "Portföy Analisti"
    }

# --- 4. LOGO VE BAŞLIK TASARIMI (KIRMIZI TEMA) ---
# Logoyu ve başlığı merkeze alıyoruz
col_l, col_m, col_r = st.columns([1, 2, 1])
with col_m:
    # Ak Portföy Logosu (Resmi web sitesinden çekiyoruz)
    st.image("https://www.akportfoy.com.tr/assets/img/logo.png", width=250)
    
st.markdown(f"""
    <div style="text-align: center; padding-top: 10px;">
        <h1 style="color: #D8232A; font-family: 'Segoe UI'; margin-bottom: 0; font-weight: bold; font-size: 2.5em;">
            {T['head']}
        </h1>
        <p style="color: #666; font-size: 1.2em; font-style: italic; margin-top: 5px;">
            {T['sub']}
        </p>
        <hr style="border: 1px solid #D8232A; width: 50%; margin: auto;">
    </div>
    """, unsafe_allow_html=True)

if df is not None:
    st.write("") # Boşluk
    col1, col2, col3, col4 = st.columns(4)
    top_fund = df.iloc[0]['Fon Adı'] if 'Fon Adı' in df.columns else "---"
    avg_risk = "Orta-Dengeli"
    
    col1.metric(T['kpi1'], top_fund)
    col2.metric(T['kpi2'], avg_risk)
    col3.metric(T['kpi3'], T['health'])
    col4.metric("AI Status", "Active")
    st.divider()

# --- 5. SOL PANEL ---
with st.sidebar:
    st.header("Yatırım Tercihleri")
    
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
            with st.spinner('Yapay zeka verileri analiz ediyor...'):
                model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                working_model = next((m for m in model_list if "flash" in m), model_list[0])
                model = genai.GenerativeModel(working_model)
                
                prompt = f"Analist Rolü: {T['role']}. Veriler: {df.to_string()}. Profil: {ans1}, {ans2}, Vergi:{ans3}, Strateji:{ans4}. Profesyonel bir rapor oluştur."
                res = model.generate_content(prompt)
                
                st.subheader("📋 Stratejik Analiz Raporu")
                st.info(res.text)
                
                if '1Y (%)' in df.columns:
                    st.subheader("📈 Getiri Analizi")
                    fig = px.bar(df, x='Kodu', y='1Y (%)', color='1Y (%)', 
                                 color_continuous_scale=['#FFCCCC', '#D8232A'], # Grafiği de kırmızı tonlu yaptık
                                 title="Yıllık Fon Performansı")
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Lütfen sol taraftan kriterlerinizi seçip analizi başlatın.")
    
    with tab2:
        st.dataframe(df, use_container_width=True)
else:
    st.error("Veri dosyası bulunamadı.")
