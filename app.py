import streamlit as st
import yfinance as yf
import pandas as pd

# إعدادات الصفحة والمظهر
st.set_page_config(page_title="منصة استخبارات AUD/USD", page_icon="💎", layout="wide")

# تقليص حجم الخط ليناسب شاشة الموبايل تماماً
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-size: 13px !important;
    }
    h1 {
        font-size: 1.5rem !important;
    }
    h3 {
        font-size: 1.1rem !important;
    }
    .stMetric {
        padding: 5px !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("💎 منصة استخبارات وتداول زوج AUD/USD")
st.write("تحليل رقمي داخلي ومباشر - خفيف وسريع جداً للموبايل")

st.markdown("---")

# --- دالة جلب البيانات الأساسية للزوج وحجم التداول ---
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

# --- دالة حساب قوة العملات برمجياً (جدول الكروسات الداخلي) ---
@st.cache_data(ttl=60)
def get_currency_strength():
    # العملات المقارنة بالدولار
    tickers = {
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "USD/JPY": "JPY=X",
        "AUD/USD": "AUDUSD=X",
        "USD/CAD": "CAD=X",
        "USD/CHF": "CHF=X"
    }
    
    strength_data = []
    for name, sym in tickers.items():
        try:
            t = yf.Ticker(sym)
            h = t.history(period="2d")
            if len(h) >= 2:
                close_today = h['Close'].iloc[-1]
                close_yesterday = h['Close'].iloc[-2]
                change = ((close_today - close_yesterday) / close_yesterday) * 100
                strength_data.append({"الزوج": name, "السعر الحالي": f"{close_today:.4f}", "التغير اليومي": round(change, 2)})
        except:
            continue
    return pd.DataFrame(strength_data)

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

    # عرض التنبيه
    st.markdown(f'<div style="background-color:{bg_color}; padding:10px; border-radius:8px; text-align:center;"><h3 style="color:{text_color}; margin:0;">{signal_text}</h3></div>', unsafe_allow_html=True)
    
    # تنبيه حجم التداول
    if current_volume > (avg_volume * 1.5):
        st.markdown(f'<div style="background-color:#854d0e; padding:6px; border-radius:6px; text-align:center; margin-top:5px;"><p style="color:#fef08a; margin:0; font-size:11px;">🔥 سيولة عالية: دخول مؤسسات وحيتان في السوق حالياً!</p></div>', unsafe_allow_html=True)

    # تقسيم الشاشة
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("### 📊 تفاصيل الإشارة الحالية")
        st.metric(label="💵 السعر الحالي", value=f"{current_price:.5f}")
        st.metric(label="📥 سعر الدخول المقترح", value=f"{entry_price:.5f}")
        st.metric(label="🎯 الهدف (TP)", value=f"{tp:.5f}", delta=f"+{tp_pips} Pips")
        st.metric(label="🛑 الاستوب (SL)", value=f"{sl:.5f}", delta=f"-{sl_pips} Pips")

    with col_right:
        st.markdown("### 🧮 حاسبة اللوت الآمن")
        balance = st.number_input("💰 رأس المال ($):", min_value=10, value=1000, step=100)
        risk_percent = st.slider("⚠️ نسبة المخاطرة (%):", min_value=0.5, max_value=5.0, value=1.0, step=0.5)
        
        risk_amount = balance * (risk_percent / 100)
        pip_value_needed = risk_amount / sl_pips
        lot_size = pip_value_needed / 10.0
        
        st.success(f"المبلغ المخاطر به: {risk_amount:.2f} $")
        st.info(f"حجم العقد الآمن: {lot_size:.2f} Lot")

    st.markdown("---")

    # --- الجزء المصلح: جدول قوة العملات المبني داخلياً ---
    st.markdown("### ⚖️ جدول حركة وقوة أزواج العملات اليوم (%)")
    df_strength = get_currency_strength()
    
    if not df_strength.empty:
        # تلوين الجدول وتنسيقه ليكون جذاباً وسهل القراءة
        def color_change(val):
            try:
                val_float = float(val)
                if val_float > 0: return 'color: #22c55e; font-weight: bold;'
                elif val_float < 0: return 'color: #ef4444; font-weight: bold;'
            except:
                pass
            return ''
            
        st.dataframe(df_strength.style.applymap(color_change, subset=['التغير اليومي']), use_container_width=True, hide_index=True)
        st.caption("💡 طريقة القراءة: إذا كان زوج AUD/USD وزوج EUR/USD باللون الأخضر، فالـ USD ضعيف والـ AUD قوي (فرصة شراء قوية للـ AUD).")
    else:
        st.warning("جاري سحب التغيرات اليومية للعملات...")

except Exception as e:
    st.error("السوق مغلق أو جاري تحديث اتصال السيرفر المالي...")

st.markdown("---")

# روابط سريعة معربة للأخبار والشارت لمنع المشاكل الأمنية على الموبايل
st.markdown("### 🔗 روابط سريعة معربة ومستقرة")
b1, b2 = st.columns(2)
with b1:
    st.link_button("📅 افتح المفكرة الاقتصادية المعربة (موقع خارجي)", "https://ar.tradingview.com/economic-calendar/")
with b2:
    st.link_button("📈 افتح شارت AUD/USD التفاعلي الكامل", "https://ar.tradingview.com/chart/?symbol=FX%3AAUDUSD")
