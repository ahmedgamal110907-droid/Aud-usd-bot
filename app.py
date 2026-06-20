import streamlit as st
import yfinance as yf
import pandas as pd
import streamlit.components.v1 as components

# إعدادات الصفحة والمظهر الداكن المتناسق
st.set_page_config(page_title="منصة التداول والاستخبارات المتكاملة", page_icon="🎯", layout="wide")

# تقليص حجم الخط وتحسين مظهر عناصر الموبايل عبر CSS
st.markdown("""
    <style>
    html, body, [class*="css"] { font-size: 13px !important; }
    h1 { font-size: 1.6rem !important; }
    h3 { font-size: 1.1rem !important; }
    .stMetric { padding: 4px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 منصة الاستخبارات والتداول الرقمي المتكاملة")

# --- دالة حساب مؤشر الدولار استرشادياً USDX ---
@st.cache_data(ttl=60)
def get_usdx_change():
    try:
        usdx = yf.Ticker("DX-Y.NYB") # رمز مؤشر الدولار في ياهو فاينانشال
        h = usdx.history(period="2d")
        if len(h) >= 2:
            change = ((h['Close'].iloc[-1] - h['Close'].iloc[-2]) / h['Close'].iloc[-2]) * 100
            return h['Close'].iloc[-1], change
    except:
        pass
    return 100.0, 0.0

usdx_price, usdx_pct = get_usdx_change()
usdx_color = "#22c55e" if usdx_pct >= 0 else "#ef4444"

# عرض شريط مؤشر الدولار الاسترشادي في الأعلى
st.markdown(f"""
<div style="background-color:#1e293b; padding:8px; border-radius:8px; text-align:center; border-left: 5px solid {usdx_color};">
    <span style="color:#94a3b8; font-weight:bold;">💵 مؤشر الدولار الأمريكي الاسترشادي (USDX): </span>
    <span style="color:#ffffff; font-weight:bold;">{usdx_price:.2f}</span> 
    <span style="color:{usdx_color}; font-weight:bold;">({usdx_pct:+.2f}%)</span>
</div>
""", unsafe_allow_html=True)

st.markdown(" ")

# --- 1. قائمة اختيار الأصول الديناميكية (الأصل المختار يغير كل شيء) ---
assets_dict = {
    "الدولار الأسترالي (AUD/USD)": {"symbol": "AUDUSD=X", "tv_symbol": "FX:AUDUSD", "pips": 30, "factor": 0.0001, "pip_mult": 10.0},
    "الذهب (GOLD / XAUUSD)": {"symbol": "GC=F", "tv_symbol": "OANDA:XAUUSD", "pips": 50, "factor": 0.1, "pip_mult": 1.0},
    "اليورو (EUR/USD)": {"symbol": "EURUSD=X", "tv_symbol": "FX:EURUSD", "pips": 20, "factor": 0.0001, "pip_mult": 10.0},
    "الجنيه الإسترليني (GBP/USD)": {"symbol": "GBPUSD=X", "tv_symbol": "FX:GBPUSD", "pips": 25, "factor": 0.0001, "pip_mult": 10.0},
    "الين الياباني (USD/JPY)": {"symbol": "JPY=X", "tv_symbol": "FX:USDJPY", "pips": 30, "factor": 0.01, "pip_mult": 9.0},
}

selected_asset_name = st.selectbox("🗂️ اختر العملة أو الأصل المراد تحليله وتداوله الآن:", list(assets_dict.keys()))
asset = assets_dict[selected_asset_name]

# --- 2. جلب المؤشرات والبيانات الحية للأصل المختار ---
@st.cache_data(ttl=60) 
def get_asset_data(symbol):
    ticker = yf.Ticker(symbol)
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
    data = get_asset_data(asset["symbol"])
    current_price = data['Close'].iloc[-1]
    current_rsi = data['RSI'].iloc[-1]
    ema_50 = data['EMA_50'].iloc[-1]
    current_volume = data['Volume'].iloc[-1]
    avg_volume = data['Vol_Avg_24h'].iloc[-1]
    
    sl_pips = asset["pips"]
    
    # منطق الإشارات الفنية وحساب الأهداف تلقائياً
    is_strong_buy = current_rsi < 35 and current_price > ema_50
    is_strong_sell = current_rsi > 65 and current_price < ema_50
    
    if is_strong_buy:
        signal_text = f"🚨 تنبيه: فرصة شراء قوية على {selected_asset_name}"
        bg_color = "#155724"
        text_color = "#d4edda"
        entry_price = current_price
        tp = entry_price + ((sl_pips * 2) * asset["factor"])
        sl = entry_price - (sl_pips * asset["factor"])
    elif is_strong_sell:
        signal_text = f"🚨 تنبيه: فرصة بيع قوية على {selected_asset_name}"
        bg_color = "#721c24"
        text_color = "#f8d7da"
        entry_price = current_price
        tp = entry_price - ((sl_pips * 2) * asset["factor"])
        sl = entry_price + (sl_pips * asset["factor"])
    else:
        signal_text = f"⏳ {selected_asset_name} : انتظار ومراقبة السلوك السعري"
        bg_color = "#333333"
        text_color = "#ffffff"
        entry_price, tp, sl = current_price, current_price + (sl_pips * asset["factor"]), current_price - (sl_pips * asset["factor"])

    # عرض مربع الإشارة التفاعلي
    st.markdown(f'<div style="background-color:{bg_color}; padding:10px; border-radius:8px; text-align:center;"><h3 style="color:{text_color}; margin:0;">{signal_text}</h3></div>', unsafe_allow_html=True)
    
    # تنبيه حجم التداول والسيولة الفوري للأصل
    if current_volume > (avg_volume * 1.5):
        st.markdown(f'<div style="background-color:#854d0e; padding:6px; border-radius:6px; text-align:center; margin-top:5px;"><p style="color:#fef08a; margin:0; font-size:11px;">🔥 تنبيه سيولة: دخول غير طبيعي للمؤسسات والحيتان على هذا الأصل الآن!</p></div>', unsafe_allow_html=True)

    # تفاصيل الأرقام وإدارة المخاطر
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("### 📊 المستويات الرقمية المقترحة")
        st.metric(label="💵 السعر المباشر", value=f"{current_price:.4f}")
        st.metric(label="📥 نقطة الدخول", value=f"{entry_price:.4f}")
        st.metric(label="🎯 أخذ الربح (TP)", value=f"{tp:.4f}")
        st.metric(label="🛑 وقف الخسارة (SL)", value=f"{sl:.4f}", delta=f"المخاطرة: {sl_pips} نقطة")

    with col_right:
        st.markdown("### 🧮 حاسبة اللوت الذكية")
        balance = st.number_input("💰 رأس مال الحساب ($):", min_value=10, value=1000, step=100)
        risk_percent = st.slider("⚠️ حدد نسبة مخاطرتك (%):", min_value=0.5, max_value=5.0, value=1.0, step=0.5)
        
        risk_amount = balance * (risk_percent / 100)
        # حساب حجم اللوت الدقيق حسب نوع الأصل ونقاط الستوب
        pip_value_needed = risk_amount / sl_pips
        lot_size = pip_value_needed / asset["pip_mult"]
        
        st.success(f"المبلغ المالي المعرض للمخاطرة: {risk_amount:.2f} $")
        st.info(f"حجم العقد المقترح: {abs(lot_size):.2f} Lot")

except Exception as e:
    st.warning("السوق مغلق لعطلة نهاية الأسبوع حالياً. ستعمل الأرقام والجداول تلقائياً فور الافتتاح.")

st.markdown("---")

# --- 3. لسان الشاشات المدمجة داخل التطبيق (دون روابط خارجية) وبكود جافاسكريبت متوافق للموبايل ---
st.markdown("### 📈 الرسوم البيانية الحية والمفكرة الاقتصادية المعربة")

tab_chart, tab_news = st.tabs(["📊 الشارت الحي المباشر للأصل", "📅 المفكرة الاقتصادية والبيانات الاقتصادية"])

with tab_chart:
    # الشارت الحي يتغير تلقائياً بتغير الأصل المختار من الأعلى
    chart_js = f"""
    <div class="tradingview-widget-container" style="height:380px;">
      <div id="tv_chart_container" style="height:380px;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "{asset['tv_symbol']}",
        "interval": "60",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "ar",
        "container_id": "tv_chart_container"
      }});
      </script>
    </div>
    """
    components.html(chart_chart_js:=chart_js, height=390)

with tab_news:
    # المفكرة الاقتصادية معربة ومدمجة لتعمل على متصفحات الموبايل دون اختفاء
    news_js = """
    <div class="tradingview-widget-container" style="height:380px;">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget/events.js" async>
      {
      "width": "100%",
      "height": 380,
      "colorTheme": "dark",
      "isTransparent": false,
      "locale": "ar",
      "importanceFilter": "0,1"
    }
      </script>
    </div>
    """
    components.html(news_js, height=390)

st.caption("تنبيه مخاطر: تم تهيئة الأكواد لتعمل بشكل مدمج ومتوافق مع شاشات الهواتف ومتصفحاتها.")
