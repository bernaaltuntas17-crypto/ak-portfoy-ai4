import streamlit as st
import pandas as pd
import glob
import requests
import json

# --- 1. KURUMSAL YAPILANDIRMA ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("⚠️ API Anahtarı Bulunamadı! Streamlit Secrets ayarlarını kontrol edin.")
    st.stop()

API_KEY = st.secrets["GEMINI_API_KEY"]

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
    "sub": "Yapay Zeka Destekli Gelecek Nesil Portföy Yönetimi" if lang == "Türkçe" else "KI-Investment-Plattform",
    "btn": "Analizi Başlat" if lang == "Türkçe" else "Analyse Starten",
    "wait": "Yatırım Uzmanı Verileri İnceliyor..." if lang == "Türkçe" else "KI analysiert...",
    "report_head": "📋 Kişiselleştirilmiş Stratejik Yatırım Raporu",
    "prompt_lang": "TÜRKÇE" if lang == "Türkçe" else "ALMANCA"
}

sektor_options = ["Teknoloji ve Yapay Zeka", "Sürdürülebilirlik ve Yeşil Enerji", "Değerli Madenler ve Emtialar", "Gayrimenkul Yatırım Fonları", "Tercih Ettiğim Bir Sektör Yok"]
para_options = ["TL", "USD", "EUR", "GBP"]
faiz_options = ["Faizsiz", "Faizli"]
risk_options = ["Korumalı", "Dengeli", "Agresif"]

col_l, col_m, col_r = st.columns([1, 2, 1])
with col_m:
    try: st.image("logo.png", width=300)
    except: st.write("")

st.markdown(f"<div style='text-align:center; padding-bottom: 20px;'><h1 style='color:#D8232A; font-weight:bold; margin-bottom:0;'>{T['head']}</h1><p style='color:#666; font-style:italic;'>{T['sub']}</p><hr style='width:50%; margin:auto;'></div>", unsafe_allow_html=True)

# --- 4. YATIRIM TERCİHLERİ ---
with st.sidebar:
    st.header("Yatırım Tercihleri")
    ans_likidite = st.selectbox("Likidite Tercihi", ["T+0", "T+1", "T+2", "T+3"])
    ans_para = st.radio("Para Birimi", para_options)
    ans_faiz = st.radio("Faiz Hassasiyeti", faiz_options)
    ans_vade = st.selectbox("Vade Süresi", ["0-1 yıl", "2-5 yıl", "10+ yıl"])
    ans_risk = st.select_slider("Risk Tercihi", options=risk_options)
    ans_sektor = st.selectbox("Sektör", sektor_options)
    amount = st.number_input("Yatırım Tutarı", min_value=1000, value=50000)
    st.divider()
    analyze_btn = st.button(T['btn'], type="primary")

# --- 5. PROFESYONEL ANALİZ MOTORU ---
if df is not None:
    if analyze_btn:
        with st.spinner(T['wait']):
            
            # DERİN ANALİZ PROMPT'U (Berna'nın istediği detay seviyesi)
            prompt = f"""
            Sen Ak Portföy'de görevli profesyonel bir Kıdemli Yatırım Uzmanısın. Aşağıdaki verileri kullanarak müşteriye özel çok kapsamlı bir analiz hazırla. 
            Dil: {T['prompt_lang']}.
            
            MÜŞTERİ VERİLERİ:
            Tutar: {amount} {ans_para} | Vade: {ans_vade} | Risk: {ans_risk} | Faiz: {ans_faiz} | Sektör: {ans_sektor} | Likidite: {ans_likidite}
            
            FON LİSTESİ:
            {df.to_string()}
            
            ANALİZ ŞU KRİTERLERE GÖRE YAPILMALI:
            1. Seçilen her fonun müşterinin '{ans_risk}' risk profiline neden %100 uyduğunu teknik olarak açıkla.
            2. '{ans_sektor}' sektöründeki güncel piyasa fırsatlarını Ak Portföy fonları üzerinden gerekçelendir.
            3. '{ans_vade}' vadede neden bu fonların seçildiğini, vade sonunda beklenen stratejik avantajları anlat.
            4. Neden başka bir fon değil de 'ÖZELLİKLE BU' fonun seçildiğini (getiri potansiyeli, risk puanı vb.) kanıtlarıyla yaz.
            """

            # 404 HATASINI ÇÖZEN "V1" ENDPOINT'İ
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
            headers = {'Content-Type': 'application/json'}
            payload = {"contents": [{"parts": [{"text": prompt}]}]}

            try:
                response = requests.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    ai_response = response.json()
                    ai_text = ai_response['candidates'][0]['content']['parts'][0]['text']
                    st.subheader(T['report_head'])
                    st.info(ai_text)
                    st.balloons() # Başarı kutlaması!
                elif response.status_code == 404:
                    # EĞER V1 DE 404 VERİRSE (ÇOK DÜŞÜK İHTİMAL), V1BETA İLE TEKRAR DENE
                    url_beta = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
                    response = requests.post(url_beta, headers=headers, json=payload)
                    if response.status_code == 200:
                        st.info(response.json()['candidates'][0]['content']['parts'][0]['text'])
                    else:
                        st.error(f"Sistem şu an meşgul (Hata: {response.status_code}). Lütfen 1 dakika sonra tekrar deneyin.")
                else:
                    st.error(f"API Hatası ({response.status_code}): Lütfen API anahtarınızı Google AI Studio'dan kontrol edin.")
            
            except Exception as e:
                st.error(f"Bağlantı Sorunu: {e}")
else:
    st.error("⚠️ fonlar.csv veya fonlar.xlsx dosyası bulunamadı!")
