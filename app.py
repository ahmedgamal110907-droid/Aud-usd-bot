import streamlit as st
import yfinance as tf
import pandas as pd
import streamlit.components.v1 as components

# إعدادات الصفحة الواسعة والمظهر الداكن الافتراضي
st.set_page_config(page_title="مستشار AUD/USD الاحترافي", page_icon="🎯", layout="wide")

st.title("🎯 نظام الإشارات المتقدم لزوج AUD/USD")
st.write("تحليل رقمي حقيقي - محدث لحظة بلحظة مع أسعار السوق الحية")

st.markdown("---")

# --- 1. جلب البيانات الحية وحساب المؤشرات ---
@st.cache_data(ttl=60) # تحديث البيانات تلقائياً كل دقيقة
def get_live_data():
    # سحب بيانات الساعة لحساب RSI حقيقي ونقاط الدخول
    ticker = tf.Ticker("AUDUSD=X")
    df = ticker.history(period="2mo", interval="1h")
    
    # حساب مؤشر RSI مبسط
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # حساب المتوسطات المتحركة
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    
    return df

try:
    data = get_live_data()
    current_price = data['Close'].iloc[-1]
    current_rsi = data['RSI'].iloc[-1]
    ema_20 = data['EMA_20'].iloc[-1]
    ema_50 = data['EMA_50'].iloc[-1]
    
    # --- 2. منطق الإشارات ونقاط الدخول والخروج ---
    is_strong_buy = current_rsi < 35 and current_price > ema_50
    is_strong_sell = current_rsi > 65 and current_price < ema_50
    
    if is_strong_buy:
        signal_text = "🚨 تنبيه: فرصة شراء قوية جداً"
        bg_color = "#155724"
        text_color = "#d4edda"
        entry_price = current_price
        tp = entry_price + 0.0060 # هدف 60 نقطة
        sl = entry_price - 0.0030 # ستوب 30 نقطة
        # إضافة صوت تنبيه عبر الـ HTML
        st.components.v1.html('<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-84.wav" type="audio/wav"></audio>', height=0)
        
    elif is_strong_sell:
        signal_text = "🚨 تنبيه: فرصة بيع قوية جداً"
        bg_color = "#721c24"
        text_color = "#f8d7da"
        entry_price = current_price
        tp = entry_price - 0.0060
        sl = entry_price + 0.0030
        st.components.v1.html('<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-84.wav" type="audio/wav"></audio>', height=0)
        
    else:
        signal_text = "⏳ الوضع الحالي: انتظار ومراقبة السلوك السعري"
        bg_color = "#333333"
        text_color = "#ffffff"
        entry_price, tp, sl = "لا يوجد", "لا يوجد", "لا يوجد"

    # --- 3. عرض التنبيهات ونقاط التداول في الواجهة ---
    st.markdown(f'<div style="background-color:{bg_color}; padding:20px; border-radius:10px; text-align:center;"><h2 style="color:{text_color};">{signal_text}</h2></div>', unsafe_allow_html=True)
    
    st.markdown("### 📊 تفاصيل التوصية الرقمية الحالية")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="💵 سعر السعر الحالي", value=f"{current_price:.5f}")
    with col2:
        st.metric(label="📥 سعر الدخول المقترح", value=f"{entry_price:.5f}" if isinstance(entry_price, float) else entry_price)
    with col3:
        st.metric(label="🎯 أخذ الربح (TP)", value=f"{tp:.5f}" if isinstance(tp, float) else tp, delta="➕ 60 Pips" if isinstance(tp, float) else None)
    with col4:
        st.metric(label="🛑 وقف الخسارة (SL)", value=f"{sl:.5f}" if isinstance(sl, float) else sl, delta="➖ 30 Pips" if isinstance(sl, float) else None)

except Exception as e:
    st.error("جاري تحميل البيانات الحية من السيرفر المالي... يرجى تحديث الصفحة بعد ثوانٍ.")

st.markdown("---")

# --- 4. دمج شارت TradingView الحي للفريمات الثلاثة ---
st.markdown("### 📈 الرسوم البيانية الحية (TradingView)")
tab1, tab2, tab3 = st.tabs(["🕒 شارت 1 ساعة (1H)", "⏳ شارت 4 ساعات (4H)", "📅 شارت يومي (1D)"])

def generate_tradingview_widget(interval):
    return f"""
    <div class="tradingview-widget-container" style="height:500px;">
      <div id="tradingview_{interval}" style="height:500px;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "FX:AUDUSD",
        "interval": "{interval}",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "ar",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_{interval}"
      }});
      </script>
    </div>
    """

with tab1:
    components.html(generate_tradingview_widget("60"), height=520)
with tab2:
    components.html(generate_tradingview_widget("240"), height=520)
with tab3:
    components.html(generate_tradingview_widget("D"), height=520)

st.caption("تنبيه مخاطر: البيانات تحدث تلقائياً. تأكد من إدارة رأس مالك بصرامة.")
