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
    [data-testid="stSidebar"] { background-color: #1e1e1e; }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
        color: #ffffff !important;
    }
    .stButton>button {
        background-color: #D8232A; color: white; border-radius: 8px; width: 100%; border: none; font-weight: bold; height: 3em;
    }
    .stButton>button:hover { background-color: #ffffff; color: #D8232A; border: 1px solid #D8232A; }
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

# --- 3. TAM DİL DESTEĞİ ---
lang = st.sidebar.selectbox("Sprache / Dil", ["Türkçe", "Almanca"])

if lang == "Almanca":
    T = {
        "head": "AK PORTFÖY INTELLIGENTE ANLAGEEMPFEHLUNG",
        "sub": "KI-Gesteuerte Investment-Plattform der nächsten Generation",
        "btn": "Analyse Starten",
        "sidebar_head": "Anlagepräferenzen",
        "likidite": "Liquiditätspräferenz",
        "para": "Währung",
        "faiz": "Zinssensitivität",
        "vade": "Laufzeit",
        "risk": "Risikopräferenz",
        "sektor": "Bevorzugter Sektor",
        "tutar": "Investitionsbetrag",
        "wait": "Strategie wird erstellt...",
        "report_head": "📋 Strategischer Analysebericht",
        "info": "Bitte wählen Sie Ihre Kriterien.",
        "prompt_lang": "Write the entire report in GERMAN."
    }
    sektor_options = ["Technologie & KI", "Nachhaltigkeit", "Rohstoffe", "Immobilienfonds", "Keine Präferenz"]
    para_options = ["Türkische Lira (TL)", "US-Dollar (USD)", "Euro (EUR)", "Pound (GBP)"]
    faiz_options = ["Zinsfrei", "Zinsbasiert"]
    risk_options = ["Konservativ", "Ausgewogen", "Aggressiv"]
else:
    T = {
        "head": "AK PORTFÖY AKILLI YATIRIM TAVSİYESİ",
        "sub": "Yapay Zeka Destekli Gelecek Nesil Portföy Yönetimi",
        "btn": "Analizi Başlat",
        "sidebar_head": "Yatırım Tercihleri",
        "likidite": "Likidite Tercihi",
        "para": "Para Birimi",
        "faiz": "Faiz Hassasiyeti",
        "vade": "Vade Süresi Tercihi",
        "risk": "Risk Tercihi",
        "sektor": "Yatırım için Tercih Edilecek Sektör",
        "tutar": "Yatırım Tutarı",
        "wait": "Strateji Oluşturuluyor...",
        "report_head": "📋 Kişiselleştirilmiş Stratejik Analiz Raporu",
        "info": "Lütfen sol taraftan kriterlerinizi belirleyip Analizi Başlat'a tıklayın.",
        "prompt_lang": "Raporun tamamını TÜRKÇE yaz."
    }
    sektor_options = ["Teknoloji ve Yapay Zeka", "Sürdürülebilirlik", "Değerli Madenler", "Gayrimenkul Fonları", "Tercih Ettiğim Bir Sektör Yok"]
    para_options = ["Türk Lirası (TL)", "ABD Doları (USD)", "Euro (EUR)", "Pound (GBP)"]
    faiz_options = ["Faizsiz", "Faizli"]
    risk_options = ["Korumalı", "Dengeli", "Agresif"]

# --- 4. LOGO VE BAŞLIK ---
col_l, col_m, col_r = st.columns([1, 2, 1])
with col_m:
    try: st.image("logo.png", width=300)
    except: st.write("")

st.markdown(f"""
    <div style="text-align: center; padding-bottom: 20px;">
        <h1 style="color: #D8232A; font-weight: bold; margin-bottom: 0;">{T['head']}</h1>
        <p style="color: #666; font-size: 1.1em; font-style: italic;">{T['sub']}</p>
        <hr style="width: 50%; margin: auto;">
    </div>
    """, unsafe_allow_html=True)

# --- 5. YATIRIM TERCİHLERİ ---
with st.sidebar:
    st.header(T['sidebar_head'])
    ans_likidite = st.selectbox(T['likidite'], ["T+0", "T+1", "T+2", "T+3"])
    ans_para = st.radio(T['para'], para_options)
    ans_faiz = st.radio(T['faiz'], faiz_options)
    ans_vade = st.selectbox(T['vade'], ["0-1 yıl/Jahr", "2-5 yıl/Jahre", "10+ yıl/Jahre"])
    ans_risk = st.select_slider(T['risk'], options=risk_options)
    ans_sektor = st.selectbox(T['sektor'], sektor_options)
    amount = st.number_input(T['tutar'], min_value=1000, value=50000)
    
    st.divider()
    analyze_btn = st.button(T['btn'], type="primary")

# --- 6. ANALİZ VE RAPOR (HATA GİDERİLMİŞ KISIM) ---
if df is not None:
    if analyze_btn:
        with st.spinner(T['wait']):
            try:
                # Modeli daha sağlam bir şekilde seçiyoruz
                model = genai.GenerativeModel('models/gemini-1.5-flash') 
                
                prompt = f"""
                {T['prompt_lang']}
                Role: Financial Analyst. 
                Data: {df.to_string()}
                User Profile: Amount: {amount}, Currency: {ans_para}, Liquidity: {ans_likidite}, 
                Interest: {ans_faiz}, Period: {ans_vade}, Risk: {ans_risk}, Sector: {ans_sektor}.
                Provide a professional investment strategy.
                """
                res = model.generate_content(prompt)
                st.subheader(T['report_head'])
                st.info(res.text)
            except Exception as e:
                # Eğer hala bulamazsa alternatif isim dene
                try:
                    model = genai.GenerativeModel('gemini-pro')
                    res = model.generate_content(prompt)
                    st.info(res.text)
                except:
                    st.error("Yapay zeka servisinde geçici bir yoğunluk var, lütfen tekrar deneyin.")
    else:
        st.info(T['info'])
