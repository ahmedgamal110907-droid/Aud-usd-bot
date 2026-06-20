import streamlit as st
import yfinance as yf
import pandas as pd
import streamlit.components.v1 as components

# إعدادات الصفحة الواسعة والمظهر الداكن الافتراضي
st.set_page_config(page_title="منصة استخبارات AUD/USD", page_icon="💎", layout="wide")

# تقليص حجم الخط الرئيسي عبر CSS مدمج
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-size: 14px !important;
    }
    h1 {
        font-size: 1.8rem !important;
    }
    h2 {
        font-size: 1.4rem !important;
    }
    h3 {
        font-size: 1.2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("💎 منصة استخبارات وتداول زوج AUD/USD")
st.write("تحليل فني + سيولة وحجم + مفكرة اقتصادية معربة + جدول تقاطعات العملات + إدارة مخاطر")

st.markdown("---")

# --- 1. جلب البيانات الحية وحساب المؤشرات الفنية والسيولة ---
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
        st.components.v1.html('<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-84.wav" type="audio/wav"></audio>', height=0)
    elif is_strong_sell:
        signal_text = "🚨 تنبيه: فرصة بيع قوية جداً"
        bg_color = "#721c24"
        text_color = "#f8d7da"
        entry_price = current_price
        tp = entry_price - (tp_pips * pips_factor)
        sl = entry_price + (sl_pips * pips_factor)
        st.components.v1.html('<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-84.wav" type="audio/wav"></audio>', height=0)
    else:
        signal_text = "⏳ الوضع الحالي: انتظار ومراقبة السلوك السعري"
        bg_color = "#333333"
        text_color = "#ffffff"
        entry_price, tp, sl = current_price, current_price + (tp_pips * pips_factor), current_price - (sl_pips * pips_factor)

    st.markdown(f'<div style="background-color:{bg_color}; padding:12px; border-radius:8px; text-align:center;"><h3 style="color:{text_color}; margin:0;">{signal_text}</h3></div>', unsafe_allow_html=True)
    
    st.markdown(" ")
    if current_volume > (avg_volume * 1.5):
        st.markdown(f'<div style="background-color:#854d0e; padding:8px; border-radius:6px; text-align:center; border: 1px solid #fef08a;"><p style="color:#fef08a; margin:0; font-size:12px;">🔥 تنبيه سيولة: دخول حيتان ومؤسسات! الحجم الحالي أعلى بـ 150% من المتوسط.</p></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="background-color:#1e293b; padding:8px; border-radius:6px; text-align:center;"><p style="color:#94a3b8; margin:0; font-size:12px;">ℹ️ حجم التداول والسيولة ضمن المعدلات الطبيعية اليوم.</p></div>', unsafe_allow_html=True)

    main_col1, main_col2 = st.columns([1, 1])

    with main_col1:
        st.markdown("### 📊 تفاصيل التوصية الرقمية")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="💵 السعر الحالي", value=f"{current_price:.5f}")
            st.metric(label="🎯 أخذ الربح (TP)", value=f"{tp:.5f}", delta=f"➕ {tp_pips} Pips")
        with col2:
            st.metric(label="📥 سعر الدخول", value=f"{entry_price:.5f}")
            st.metric(label="🛑 وقف الخسارة (SL)", value=f"{sl:.5f}", delta=f"➖ {sl_pips} Pips")
        
        st.markdown("---")
        st.markdown("### 🧮 حاسبة حجم اللوت الآمن")
        balance = st.number_input("💰 رأس المال ($):", min_value=10, value=1000, step=100)
        risk_percent = st.slider("⚠️ نسبة المخاطرة (%):", min_value=0.5, max_value=5.0, value=1.0, step=0.5)
        
        risk_amount = balance * (risk_percent / 100)
        pip_value_needed = risk_amount / sl_pips
        lot_size = pip_value_needed / 10.0
        
        st.success(f"المبلغ المخاطر به: **{risk_amount:.2f} $**")
        st.info(f"حجم العقد الموصى به: **{lot_size:.2f}** Lot")

    with main_col2:
        st.markdown("### 🔀 جدول تقاطعات وقوة العملات الكبرى (Cross Rates)")
        cross_js_code = """
        <div class="tradingview-widget-container" style="height:340px;">
          <div class="tradingview-widget-container__widget"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget/forex-cross-rates.js" async>
          {
          "width": "100%",
          "height": 340,
          "currencies": ["AUD", "USD", "EUR", "GBP", "JPY", "CHF", "CAD"],
          "isTransparent": false,
          "colorTheme": "dark",
          "locale": "ar"
        }
          </script>
        </div>
        """
        components.html(cross_js_code, height=350)

except Exception as e:
    st.error("جاري تحميل البيانات الحية من السيرفر المالي... يرجى تحديث الصفحة.")

st.markdown("---")

st.markdown("### 📈 التحليل البصري والمفكرة الاقتصادية المعربة")
bot_col1, bot_col2 = st.columns([1.8, 1.2])

with bot_col1:
    tab1, tab2, tab3 = st.tabs(["🕒 1 ساعة (1H)", "⏳ 4 ساعات (4H)", "📅 يومي (1D)"])
    
    def generate_tradingview_widget(interval):
        return f"""
        <div class="tradingview-widget-container" style="height:400px;">
          <div id="tradingview_{interval}" style="height:400px;"></div>
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
            "container_id": "tradingview_{interval}"
          }});
          </script>
        </div>
        """
    with tab1:
        components.html(generate_tradingview_widget("60"), height=410)
    with tab2:
        components.html(generate_tradingview_widget("240"), height=410)
    with tab3:
        components.html(generate_tradingview_widget("D"), height=410)

with bot_col2:
    # --- تعريب وضبط المفكرة الاقتصادية لتظهر باللغة العربية بالكامل ---
    st.markdown("📅 **المفكرة الاقتصادية اليومية**")
    cal_js_code = """
    <div class="tradingview-widget-container" style="height:400px;">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget/events.js" async>
      {
      "width": "100%",
      "height": 400,
      "colorTheme": "dark",
      "isTransparent": false,
      "locale": "ar",
      "importanceFilter": "0,1",
      "currencyFilter": "USD,AUD"
    }
      </script>
    </div>
    """
    components.html(cal_js_code, height=410)

st.caption("تنبيه مخاطر: هذه المنصة مطورة برمجياً للمساعدة التقنية ولا تعتبر توصية استثمارية مطلقة.")
