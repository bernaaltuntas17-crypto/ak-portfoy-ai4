import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import glob

# --- 1. KURUMSAL YAPILANDIRMA ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("⚠️ API Anahtarı Ayarlanmamış!")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

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
    "sub": "Yapay Zeka Destekli Gelecek Nesil Portföy Yönetimi" if lang == "Türkçe" else "KI-Gesteuerte Investment-Plattform",
    "btn": "Analizi Başlat" if lang == "Türkçe" else "Analyse Starten",
    "wait": "Yapay Zeka Analiz Yapıyor..." if lang == "Türkçe" else "KI analysiert...",
    "report_head": "📋 Kişiselleştirilmiş Stratejik Analiz Raporu" if lang == "Türkçe" else "📋 Personalisierter Strategischer Analysebericht",
    "info": "Lütfen kriterlerinizi belirleyip Analizi Başlat'a tıklayın." if lang == "Türkçe" else "Bitte wählen Sie Ihre Kriterien.",
    "prompt_lang": "TÜRKÇE" if lang == "Türkçe" else "ALMANCA"
}

sektor_options = ["Teknoloji ve Yapay Zeka", "Sürdürülebilirlik ve Yeşil Enerji", "Değerli Madenler ve Emtialar", "Gayrimenkul Yatırım Fonları", "Tercih Ettiğim Bir Sektör Yok"] if lang == "Türkçe" else ["Technologie & KI", "Nachhaltigkeit & Grüne Energie", "Edelmetalle & Rohstoffe", "Immobilienfonds", "Keine Präferenz"]
para_options = ["TL", "USD", "EUR", "GBP"]
faiz_options = ["Faizsiz", "Faizli"] if lang == "Türkçe" else ["Zinsfrei", "Zinsbasiert"]
risk_options = ["Korumalı", "Dengeli", "Agresif"] if lang == "Türkçe" else ["Konservativ", "Ausgewogen", "Aggressiv"]

col_l, col_m, col_r = st.columns([1, 2, 1])
with col_m:
    try: st.image("logo.png", width=300)
    except: st.write("")

st.markdown(f"<div style='text-align:center; padding-bottom: 20px;'><h1 style='color:#D8232A; font-weight:bold; margin-bottom:0;'>{T['head']}</h1><p style='color:#666; font-style:italic;'>{T['sub']}</p><hr style='width:50%; margin:auto;'></div>", unsafe_allow_html=True)

# --- 4. YATIRIM TERCİHLERİ ---
with st.sidebar:
    st.header("Yatırım Tercihleri" if lang == "Türkçe" else "Anlagepräferenzen")
    ans_likidite = st.selectbox("Likidite Tercihi" if lang == "Türkçe" else "Liquiditätspräferenz", ["T+0", "T+1", "T+2", "T+3"])
    ans_para = st.radio("Para Birimi" if lang == "Türkçe" else "Währung", para_options)
    ans_faiz = st.radio("Faiz Hassasiyeti" if lang == "Türkçe" else "Zinssensitivität", faiz_options)
    ans_vade = st.selectbox("Vade Süresi Tercihi" if lang == "Türkçe" else "Laufzeit", ["0-1 yıl", "2-5 yıl", "10+ yıl"] if lang == "Türkçe" else ["0-1 Jahr", "2-5 Jahre", "10+ Jahre"])
    ans_risk = st.select_slider("Risk Tercihi" if lang == "Türkçe" else "Risikopräferenz", options=risk_options)
    ans_sektor = st.selectbox("Yatırım için Tercih Edilecek Sektör" if lang == "Türkçe" else "Bevorzugter Sektor", sektor_options)
    amount = st.number_input("Yatırım Tutarı" if lang == "Türkçe" else "Investitionsbetrag", min_value=1000, value=50000)
    st.divider()
    analyze_btn = st.button(T['btn'], type="primary")

# --- 6. ANALİZ VE RAPOR ---
if df is not None:
    if analyze_btn:
        with st.spinner(T['wait']):
            try:
                # KESİN ÇÖZÜM: Kütüphane sürümüyle uyumsuzluk yaşamamak için eski ve stabil modele geçildi
                model = genai.GenerativeModel('gemini-pro')
                
                # YAPAY ZEKAYA GİDEN ÇOK DETAYLI ANALİZ TALİMATI
                prompt = f"""
                Sen Ak Portföy'de çalışan Kıdemli bir Portföy Yöneticisisin. Aşağıdaki müşteri profiline ve sağlanan fon verilerine dayanarak ÇOK DETAYLI, profesyonel ve analitik bir yatırım raporu hazırla. 
                Rapor dili kesinlikle {T['prompt_lang']} olmalıdır.
                
                MÜŞTERİ PROFİLİ:
                - Yatırım Tutarı: {amount} {ans_para}
                - Likidite İhtiyacı: {ans_likidite}
                - Faiz Hassasiyeti: {ans_faiz}
                - Vade Beklentisi: {ans_vade}
                - Risk Tercihi: {ans_risk}
                - İlgilendiği Sektör: {ans_sektor}
                
                MEVCUT FON VERİLERİ:
                {df.to_string()}
                
                RAPORDA ŞU BAŞLIKLAR KESİNLİKLE OLMALIDIR:
                1. Müşteri Profili ve Strateji Özeti
                2. Önerilen Fonlar
                3. Neden Bu Fonlar Seçildi?
                4. Neden Bu Fonlara Yatırım Yapılmalı?
                """
                
                res = model.generate_content(prompt)
                
                if res.text:
                    st.subheader(T['report_head'])
                    st.markdown(res.text)
                else:
                    st.warning("⚠️ Yapay zeka şu an cevap üretemedi, lütfen tekrar deneyin.")

            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower():
                    st.warning("⚠️ Sunucu çok yoğun! Lütfen 30 saniye bekleyip tekrar Analizi Başlat'a tıklayın.")
                else:
                    st.error(f"📡 Teknik Hata Detayı: {error_str}")
    else:
        st.info(T['info'])
else:
    st.error("⚠️ Veri dosyası bulunamadı!")
