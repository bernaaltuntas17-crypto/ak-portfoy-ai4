import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import glob
import random

# --- 1. KURUMSAL YAPILANDIRMA ---
st.set_page_config(page_title="Ak Portföy | Akıllı Yatırım Tavsiyesi", layout="wide", initial_sidebar_state="expanded")

# Ak Portföy KIRMIZI VE KOYU PANEL Teması
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

# API Ayarı
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.sidebar.error("⚠️ API Anahtarı Ayarlanmamış!")

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
demo_mode = st.sidebar.toggle("Sunum Kurtarıcı (Demo Modu)", help="API hata verirse bunu açarak sunuma devam edin.")

T = {
    "head": "AK PORTFÖY AKILLI YATIRIM TAVSİYESİ" if lang == "Türkçe" else "AK PORTFÖY INTELLIGENTE ANLAGEEMPFEHLUNG",
    "sub": "Yapay Zeka Destekli Gelecek Nesil Portföy Yönetimi" if lang == "Türkçe" else "KI-Gesteuerte Investment-Plattform",
    "btn": "Analizi Başlat" if lang == "Türkçe" else "Analyse Starten",
    "wait": "Analiz Yapılıyor..." if lang == "Türkçe" else "Wird analysiert...",
}

col_l, col_m, col_r = st.columns([1, 2, 1])
with col_m:
    try: st.image("logo.png", width=300)
    except: st.write("")

st.markdown(f"<div style='text-align:center;'><h1 style='color:#D8232A;'>{T['head']}</h1><p style='color:#666;'>{T['sub']}</p><hr style='width:50%; margin:auto;'></div>", unsafe_allow_html=True)

# --- 4. YATIRIM TERCİHLERİ ---
with st.sidebar:
    st.header("Yatırım Tercihleri")
    ans_likidite = st.selectbox("Likidite", ["T+0", "T+1", "T+2"])
    ans_para = st.radio("Para Birimi", ["TL", "USD", "EUR"])
    ans_vade = st.selectbox("Vade", ["0-1 yıl", "2-5 yıl", "10+ yıl"])
    ans_risk = st.select_slider("Risk", options=["Korumalı", "Dengeli", "Agresif"])
    ans_sektor = st.selectbox("Sektör", ["Teknoloji", "Sürdürülebilirlik", "Emtia", "GYF"])
    amount = st.number_input("Tutar", min_value=1000, value=50000)
    analyze_btn = st.button(T['btn'], type="primary")

# --- 5. ANALİZ VE RAPOR ---
if df is not None:
    if analyze_btn:
        with st.spinner(T['wait']):
            if demo_mode:
                # SUNUMU KURTARAN SAHTE RAPOR
                st.subheader("📋 Stratejik Analiz Raporu (Demo)")
                demo_text = f"Analiz tamamlandı. Seçmiş olduğunuz {ans_risk} risk profili ve {ans_sektor} sektörü odağında, portföyünüzün %40'ı hisse senedi fonları, %30'u değerli madenler ve %30'u likit fonlardan oluşacak şekilde bir Ak Portföy stratejisi önerilmektedir."
                st.info(demo_text)
            else:
                try:
                    # Kota yememek için modelleri her seferinde listelemiyoruz, doğrudan deniyoruz
                    try:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                    except:
                        model = genai.GenerativeModel('gemini-pro')
                    
                    prompt = f"Analist olarak profesyonel rapor yaz: {amount} {ans_para}, Vade: {ans_vade}, Risk: {ans_risk}, Sektör: {ans_sektor}. Veriler: {df.to_string()}"
                    res = model.generate_content(prompt)
                    st.subheader("📋 Kişiselleştirilmiş Stratejik Analiz Raporu")
                    st.info(res.text)
                except Exception as e:
                    if "429" in str(e):
                        st.warning("⚠️ Sunucu şu an yoğun. Lütfen 30 saniye bekleyin veya yan menüden 'Sunum Kurtarıcı'yı açın.")
                    else:
                        st.error(f"Bağlantı sorunu: {str(e)[:50]}")
    else:
        st.info("Lütfen kriterlerinizi belirleyip Analizi Başlat'a tıklayın.")
