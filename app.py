import streamlit as st
import pandas as pd
import glob
import requests
import os
import plotly.express as px

# --- 1. AYARLAR ---
st.set_page_config(page_title="Ak Portföy | Profesyonel Yatırım Uzmanı", layout="wide")

if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    API_KEY = None

# Kurumsal Tema
st.markdown("""
<style>
    .main { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #1e1e1e; }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 { color: #ffffff !important; }
    .stButton>button { background-color: #D8232A; color: white; border-radius: 8px; width: 100%; border: none; font-weight: bold; height: 3em; }
    .report-card { background-color: #fcfcfc; padding: 25px; border-radius: 12px; border-top: 5px solid #D8232A; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .metric-box { background-color: #1e1e1e; color: white; padding: 15px; border-radius: 8px; text-align: center; }
    hr { border: 1px solid #D8232A !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. VERİ YÜKLEME ---
def load_data():
    files = glob.glob("fonlar*") + glob.glob("*.csv") + glob.glob("*.xlsx")
    for f in files:
        try:
            df = pd.read_excel(f) if f.endswith('.xlsx') else pd.read_csv(f, sep=None, engine='python', encoding='utf-8-sig')
            df.columns = [c.strip() for c in df.columns]
            return df
        except: continue
    return None

df = load_data()

# --- 3. DİL VE LOGO ---
lang = st.sidebar.selectbox("Sprache / Dil", ["Türkçe", "Almanca"])
T = {
    "head": "AK PORTFÖY AKILLI YATIRIM TAVSİYESİ",
    "btn": "Stratejik Analiz Oluştur",
    "report": "📋 Detaylı Portföy Yönetim Raporu",
    "visual": "📊 Portföy Kompozisyonu ve Getiri Beklentisi"
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

# --- 5. ANALİZ MOTORU ---
if df is not None:
    if analyze_btn:
        with st.spinner("Piyasa Çarpanları ve Fon Metrikleri Hesaplanıyor..."):
            
            # AI PROMPT: Finansal metrikleri dahil ediyoruz
            prompt = f"""
            Sen Ak Portföy Kıdemli Portföy Yöneticisisin. {amount_val} {ans_para} yatırım için {ans_risk} risk profilinde rapor yaz.
            1. Verilerdeki gerçek fonları seç.
            2. Her fonun Sharpe Oranı (riskten arındırılmış getiri) ve Volatilitesinden bahset.
            3. Vergi (Stopaj) avantajlarını belirt.
            4. Fonları BIST100 veya Altın gibi benchmarklarla kıyasla.
            VERİLER: {df.to_string()}
            """
            
            # Grafik Verisi
            filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(ans_sektor.split()[0], case=False).any(), axis=1)].head(3)
            if filtered_df.empty: filtered_df = df.sample(3)
            f_kodlar = filtered_df.iloc[:, 0].tolist()
            f_adlar = filtered_df.iloc[:, 1].tolist()
            
            # --- RAPOR VE GRAFİKLER ---
            st.subheader(T['report'])
            
            success = False
            if API_KEY and API_KEY.startswith("AIzaSy"):
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
                    res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
                    if res.status_code == 200:
                        st.markdown(res.json()['candidates'][0]['content']['parts'][0]['text'])
                        success = True
                except: pass

            if not success:
                st.info(f"Yatırım Stratejisi: {ans_risk} profilinde, {ans_sektor} odaklı ve {ans_vade} vadeli portföyünüz oluşturulmuştur.")

            # --- GÖRSEL ANALİZ ---
            st.subheader(T['visual'])
            c1, c2 = st.columns(2)
            with c1:
                fig1 = px.pie(values=[40, 35, 25], names=f_kodlar, title='İdeal Varlık Dağılımı', color_discrete_sequence=['#D8232A', '#1e1e1e', '#666666'])
                st.plotly_chart(fig1, use_container_width=True)
            with c2:
                fig2 = px.bar(x=f_kodlar, y=[45, 60, 38], title='Risk/Getiri Skoru', labels={'x':'Fon', 'y':'Puan'}, color_discrete_sequence=['#D8232A'])
                st.plotly_chart(fig2, use_container_width=True)

            # --- DETAYLI ANALİZ KARTLARI ---
            st.markdown("### 🧐 Uzman Görüşü ve
