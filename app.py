import streamlit as st
import pandas as pd
import glob
import requests
import json

# --- 1. KURUMSAL YAPILANDIRMA ---
# Güvenlik için anahtarı Secrets'tan çekiyoruz
if "GEMINI_API_KEY" not in st.secrets:
    st.error("⚠️ API Anahtarı bulunamadı! Lütfen Streamlit ayarlarındaki Secrets kısmına GEMINI_API_KEY ekleyin.")
    st.stop()

API_KEY = st.secrets["GEMINI_API_KEY"]

st.set_page_config(page_title="Ak Portföy | Akıllı Yatırım Tavsiyesi", layout="wide")

# Ak Portföy KURUMSAL TEMA (Kırmızı & Siyah)
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

# --- 3. DİL DESTEĞİ ---
lang = st.sidebar.selectbox("Sprache / Dil", ["Türkçe", "Almanca"])

T = {
    "head": "AK PORTFÖY AKILLI YATIRIM TAVSİYESİ" if lang == "Türkçe" else "AK PORTFÖY INTELLIGENTE ANLAGEEMPFEHLUNG",
    "sub": "Yapay Zeka Destekli Gelecek Nesil Portföy Yönetimi",
    "btn": "Analizi Başlat",
    "wait": "Yatırım Uzmanı Verileri İnceliyor...",
    "report": "📋 Stratejik Yatırım Raporu",
    "prompt_lang": "TÜRKÇE" if lang == "Türkçe" else "ALMANCA"
}

# --- 4. YATIRIM TERCİHLERİ ---
with st.sidebar:
    st.header("Yatırım Tercihleri")
    ans_risk = st.select_slider("Risk Tercihi", options=["Korumalı", "Dengeli", "Agresif"])
    ans_sektor = st.selectbox("Sektör", ["Teknoloji ve Yapay Zeka", "Sürdürülebilirlik", "Emtia ve Değerli Madenler", "Gayrimenkul"])
    ans_vade = st.selectbox("Vade Beklentisi", ["0-1 yıl", "2-5 yıl", "10+ yıl"])
    amount = st.number_input("Yatırım Tutarı", min_value=1000, value=50000)
    st.divider()
    analyze_btn = st.button(T['btn'], type="primary")

# Logo ve Başlık
col_l, col_m, col_r = st.columns([1, 2, 1])
with col_m:
    st.image("logo.png", width=300) if glob.glob("logo.png") else st.write("## AK Portföy")
st.markdown(f"<h1 style='text-align:center; color:#D8232A;'>{T['head']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:#666;'>{T['sub']}</p><hr>", unsafe_allow_html=True)

# --- 5. PROFESYONEL ANALİZ MOTORU ---
if df is not None:
    if analyze_btn:
        with st.spinner(T['wait']):
            # DETAYLI ANALİZ TALİMATI
            prompt = f"""
            Sen Ak Portföy'de Kıdemli Yatırım Uzmanısın. Aşağıdaki verilere dayanarak DERİN bir analiz yap.
            Dil: {T['prompt_lang']}
            
            MÜŞTERİ TERCİHLERİ:
            - Tutar: {amount} TL
            - Risk Profili: {ans_risk}
            - Odak Sektör: {ans_sektor}
            - Vade: {ans_vade}
            
            ELİNDEKİ FON VERİLERİ:
            {df.to_string()}
            
            RAPORDA ŞUNLARI DETAYLI ŞEKİLDE AÇIKLA:
            1. Neden '{ans_risk}' risk profili için veri setindeki bu spesifik fonları seçtin? 
            2. '{ans_sektor}' sektöründeki büyüme potansiyeli bu fonlara nasıl yansıyor?
            3. Seçilen her bir fonun diğerlerine göre avantajı nedir? (Verilerdeki getiri veya risk değerlerine atıf yap).
            4. Yatırımcıya bu fonları neden 'Ak Portföy' bünyesinde tutması gerektiğini profesyonelce açıkla.
            """

            # 404 HATASINI ÇÖZEN EN GÜNCEL ADRES
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
            headers = {'Content-Type': 'application/json'}
            data = {"contents": [{"parts": [{"text": prompt}]}]}

            try:
                response = requests.post(url, headers=headers, json=data, timeout=30)
                
                if response.status_code == 200:
                    ai_text = response.json()['candidates'][0]['content']['parts'][0]['text']
                    st.subheader(T['report'])
                    st.info(ai_text)
                    st.balloons()
                else:
                    # Alternatif model denemesi (Eğer Flash bulunamazsa Pro dene)
                    url_pro = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"
                    response_pro = requests.post(url_pro, headers=headers, json=data, timeout=30)
                    if response_pro.status_code == 200:
                        st.info(response_pro.json()['candidates'][0]['content']['parts'][0]['text'])
                    else:
                        st.error(f"⚠️ Bağlantı Sorunu ({response_pro.status_code}). Lütfen API anahtarını kontrol edin.")
            except Exception as e:
                st.error(f"📡 Bağlantı koptu: {e}")
else:
    st.error("⚠️ Veri dosyası bulunamadı! Lütfen fonlar.csv veya fonlar.xlsx dosyasını yükleyin.")
