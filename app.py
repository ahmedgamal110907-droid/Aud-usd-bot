import streamlit as st
import yfinance as yf
import pandas as pd

# إعدادات الصفحة والمظهر
st.set_page_config(page_title="منصة استخبارات AUD/USD", page_icon="💎", layout="wide")

# تقليص حجم الخط ليناسب شاشة الموبايل
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-size: 13px !important;
    }
    h1 {
        font-size: 1.6rem !important;
    }
    h3 {
        font-size: 1.1rem !important;
    }
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("💎 منصة استخبارات وتداول زوج AUD/USD")
st.write("تحليل فني + سيولة وحجم + إدارة مخاطر + أدوات حية للموبايل")

st.markdown("---")

# --- 1. جلب البيانات الحية وحساب المؤشرات ---
@st.cache_data(ttl=60) 
def get_live_data():
    ticker = yf.Ticker("AUDUSD=X")
    df = ticker.history(period="2mo", interval="1h")
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['Vol_Avg_24h'] = df['Volume'].rolling(window=24).mean()
    
    return df

try:
    data = get_live_data()
    current_price = data['Close'].iloc[-1]
    current_rsi = data['RSI'].iloc[-1]
    ema_50 = data['EMA_50'].iloc[-1]
    current_volume = data['Volume'].iloc[-1]
    avg_volume = data['Vol_Avg_24h'].iloc[-1]
    
    pips_factor = 0.0001
    sl_pips = 30
    tp_pips = 60
    
    is_strong_buy = current_rsi < 35 and current_price > ema_50
    is_strong_sell = current_rsi > 65 and current_price < ema_50
    
    if is_strong_buy:
        signal_text = "🚨 تنبيه: فرصة شراء قوية جداً"
        bg_color = "#155724"
        text_color = "#d4edda"
        entry_price = current_price
        tp = entry_price + (tp_pips * pips_factor)
        sl = entry_price - (sl_pips * pips_factor)
    elif is_strong_sell:
        signal_text = "🚨 تنبيه: فرصة بيع قوية جداً"
        bg_color = "#721c24"
        text_color = "#f8d7da"
        entry_price = current_price
        tp = entry_price - (tp_pips * pips_factor)
        sl = entry_price + (sl_pips * pips_factor)
    else:
        signal_text = "⏳ الوضع الحالي: انتظار ومراقبة السلوك السعري"
        bg_color = "#333333"
        text_color = "#ffffff"
        entry_price, tp, sl = current_price, current_price + (tp_pips * pips_factor), current_price - (sl_pips * pips_factor)

    st.markdown(f'<div style="background-color:{bg_color}; padding:10px; border-radius:8px; text-align:center;"><h3 style="color:{text_color}; margin:0;">{signal_text}</h3></div>', unsafe_allow_html=True)
    
    st.markdown(" ")
    if current_volume > (avg_volume * 1.5):
        st.markdown(f'<div style="background-color:#854d0e; padding:8px; border-radius:6px; text-align:center;"><p style="color:#fef08a; margin:0; font-size:11px;">🔥 سيولة عالية: دخول حيتان ومؤسسات! حجم التداول الحالي أعلى من المتوسط بـ 150%+.</p></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="background-color:#1e293b; padding:8px; border-radius:6px; text-align:center;"><p style="color:#94a3b8; margin:0; font-size:11px;">ℹ️ حجم التداول والسيولة ضمن المعدلات الطبيعية الهادئة.</p></div>', unsafe_allow_html=True)

    # تقسيم الشاشة
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("### 📊 تفاصيل التوصية")
        st.metric(label="💵 السعر الحالي", value=f"{current_price:.5f}")
        st.metric(label="📥 سعر الدخول", value=f"{entry_price:.5f}")
        st.metric(label="🎯 أخذ الربح (TP)", value=f"{tp:.5f}", delta=f"➕ {tp_pips} Pips")
        st.metric(label="🛑 وقف الخسارة (SL)", value=f"{sl:.5f}", delta=f"➖ {sl_pips} Pips")

    with col_right:
        st.markdown("### 🧮 حاسبة حجم اللوت")
        balance = st.number_input("💰 رأس المال ($):", min_value=10, value=1000, step=100)
        risk_percent = st.slider("⚠️ نسبة المخاطرة (%):", min_value=0.5, max_value=5.0, value=1.0, step=0.5)
        
        risk_amount = balance * (risk_percent / 100)
        pip_value_needed = risk_amount / sl_pips
        lot_size = pip_value_needed / 10.0
        
        st.success(f"المبلغ المخاطر به: {risk_amount:.2f} $")
        st.info(f"حجم العقد الآمن: {lot_size:.2f} Lot")

except Exception as e:
    st.error("جاري تحديث البيانات المالية... يرجى إعادة المحاولة.")

st.markdown("---")

# --- 2. قسم الأدوات الذكية المصلح للموبايل (روابط صاروخية مباشرة) ---
st.markdown("### 🛠️ أدوات التداول الحية الفورية (عربي)")
st.write("اضغط على أي أداة لفتحها فوراً باللغة العربية وبشكل صحيح دون حظر من المتصفح:")

btn_col1, btn_col2, btn_col3 = st.columns(3)

with btn_col1:
    # رابط جدول تقاطعات وقوة العملات الكبرى
    st.link_button("🔀 افتح جدول قوة العملات (Cross Rates)", "https://ar.tradingview.com/markets/currencies/cross-rates-overview/")

with btn_col2:
    # رابط المفكرة الاقتصادية المعربة بالكامل
    st.link_button("📅 افتح المفكرة الاقتصادية (الأخبار اليومية)", "https://ar.tradingview.com/economic-calendar/")

with btn_col3:
    # رابط الشارت المباشر لزوج AUD/USD بكامل أدوات التحليل
    st.link_button("📈 افتح الشارت التفاعلي المباشر (AUD/USD)", "https://ar.tradingview.com/chart/?symbol=FX%3AAUDUSD")

st.caption("ملاحظة للموبايل: تم تحويل الشاشات المعطلة برمجياً إلى أزرار ربط مباشر لضمان استقرار عمل التطبيق وسرعة تحديث البيانات الاقتصادية.")
