import streamlit as st
import yfinance as yf
import pandas as pd
import streamlit.components.v1 as components
from datetime import datetime
import pytz

# إعدادات الصفحة والمظهر الداكن المتناسق للموبايل
st.set_page_config(page_title="منصة التداول والاستخبارات المتكاملة", page_icon="🎯", layout="wide")

# تقليص حجم الخط وتحسين مظهر عناصر الموبايل عبر CSS
st.markdown("""
    <style>
    html, body, [class*="css"] { font-size: 13px !important; }
    h1 { font-size: 1.6rem !important; }
    h2 { font-size: 1.3rem !important; }
    h3 { font-size: 1.1rem !important; }
    .stMetric { padding: 4px !important; }
    .market-box { padding: 8px; border-radius: 6px; margin-bottom: 5px; text-align: center; font-size: 11px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 منصة الاستخبارات والتداول الرقمي المتكاملة")

# --- 1. قسم الوقت ومواعيد البورصات بتوقيت مصر وحالتها الحالية ---
st.markdown("### 🕒 التوقيت الحالي ومراقبة الجلسات العالمية (بتوقيت مصر)")

# جلب توقيت القاهرة الحالي
cairo_tz = pytz.timezone('Africa/Cairo')
cairo_now = datetime.now(cairo_tz)
current_hour = cairo_now.hour

col_time, col_sessions = st.columns([1, 2])

with col_time:
    st.metric(label="📅 تاريخ اليوم", value=cairo_now.strftime("%Y-%m-%d"))
    st.metric(label="⏰ الساعة الآن في مصر", value=cairo_now.strftime("%I:%M %p"))

with col_sessions:
    # تحديد حالة الجلسات برمجياً بناءً على توقيت مصر الفعلي
    # (مواعيد تقريبية عامة بتوقيت القاهرة)
    sydney_open = "🟢 مفتوحة الآن" if (current_hour >= 23 or current_hour < 8) else "🔴 مغلقة"
    tokyo_open = "🟢 مفتوحة الآن" if (current_hour >= 2 or current_hour < 11) else "🔴 مغلقة"
    london_open = "🟢 مفتوحة الآن" if (current_hour >= 9 and current_hour < 18) else "🔴 مغلقة"
    newyork_open = "🟢 مفتوحة الآن" if (current_hour >= 15 and current_hour < 24) else "🔴 مغلقة"
    
    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown(f"<div class='market-box' style='background-color:#1e293b; color:#ffffff;'>🇦🇺 بورصة سيدني (11 م - 8 ص)<br>{sydney_open}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='market-box' style='background-color:#1e293b; color:#ffffff;'>🇯🇵 بورصة طوكيو (2 ص - 11 ص)<br>{tokyo_open}</div>", unsafe_allow_html=True)
    with sc2:
        st.markdown(f"<div class='market-box' style='background-color:#1e293b; color:#ffffff;'>🇬🇧 بورصة لندن (9 ص - 6 م)<br>{london_open}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='market-box' style='background-color:#1e293b; color:#ffffff;'>🇺🇸 بورصة نيويورك (3 م - 12 منتصف الليل)<br>{newyork_open}</div>", unsafe_allow_html=True)

st.markdown("---")

# --- 2. مؤشر الدولار الاسترشادي USDX ---
@st.cache_data(ttl=60)
def get_usdx_change():
    try:
        usdx = yf.Ticker("DX-Y.NYB")
        h = usdx.history(period="2d")
        if len(h) >= 2:
            change = ((h['Close'].iloc[-1] - h['Close'].iloc[-2]) / h['Close'].iloc[-2]) * 100
            return h['Close'].iloc[-1], change
    except:
        pass
    return 100.0, 0.0

usdx_price, usdx_pct = get_usdx_change()
usdx_color = "#22c55e" if usdx_pct >= 0 else "#ef4444"

st.markdown(f"""
<div style="background-color:#1e293b; padding:8px; border-radius:8px; text-align:center; border-left: 5px solid {usdx_color};">
    <span style="color:#94a3b8; font-weight:bold;">💵 مؤشر الدولار الأمريكي الاسترشادي (USDX): </span>
    <span style="color:#ffffff; font-weight:bold;">{usdx_price:.2f}</span> 
    <span style="color:{usdx_color}; font-weight:bold;">({usdx_pct:+.2f}%)</span>
</div>
""", unsafe_allow_html=True)

st.markdown(" ")

# --- 3. قائمة اختيار الأصول الموسعة (13 أصل) ---
assets_dict = {
    "الدولار الأسترالي (AUD/USD)": {"symbol": "AUDUSD=X", "tv_symbol": "FX:AUDUSD", "pips": 30, "factor": 0.0001, "pip_mult": 10.0},
    "الذهب (GOLD / XAUUSD)": {"symbol": "GC=F", "tv_symbol": "OANDA:XAUUSD", "pips": 50, "factor": 0.1, "pip_mult": 1.0},
    "اليورو (EUR/USD)": {"symbol": "EURUSD=X", "tv_symbol": "FX:EURUSD", "pips": 20, "factor": 0.0001, "pip_mult": 10.0},
    "الجنيه الإسترليني (GBP/USD)": {"symbol": "GBPUSD=X", "tv_symbol": "FX:GBPUSD", "pips": 25, "factor": 0.0001, "pip_mult": 10.0},
    "الين الياباني (USD/JPY)": {"symbol": "JPY=X", "tv_symbol": "FX:USDJPY", "pips": 30, "factor": 0.01, "pip_mult": 9.0},
    "الدولار الكندي (USD/CAD)": {"symbol": "CAD=X", "tv_symbol": "FX:USDCAD", "pips": 25, "factor": 0.0001, "pip_mult": 10.0},
    "الفرنك السويسري (USD/CHF)": {"symbol": "CHF=X", "tv_symbol": "FX:USDCHF", "pips": 25, "factor": 0.0001, "pip_mult": 10.0},
    "الدولار النيوزيلندي (NZD/USD)": {"symbol": "NZDUSD=X", "tv_symbol": "FX:NZDUSD", "pips": 30, "factor": 0.0001, "pip_mult": 10.0},
    "اليورو مقابل الجنيه الإسترليني (EUR/GBP)": {"symbol": "EURGBP=X", "tv_symbol": "FX:EURGBP", "pips": 20, "factor": 0.0001, "pip_mult": 12.0},
    "اليورو مقابل الين (EUR/JPY)": {"symbol": "EURJPY=X", "tv_symbol": "FX:EURJPY", "pips": 35, "factor": 0.01, "pip_mult": 9.0},
    "الباوند مقابل الين (GBP/JPY)": {"symbol": "GBPJPY=X", "tv_symbol": "FX:GBPJPY", "pips": 40, "factor": 0.01, "pip_mult": 9.0},
    "الالنفط الخام الأمريكي (CRUDE OIL)": {"symbol": "CL=F", "tv_symbol": "NYMEX:CL1!", "pips": 40, "factor": 0.01, "pip_mult": 10.0},
    "البيتكوين (BTC/USD)": {"symbol": "BTC-USD", "tv_symbol": "BINANCE:BTCUSDT", "pips": 500, "factor": 1.0, "pip_mult": 0.1}
}

selected_asset_name = st.selectbox("🗂️ اختر العملة أو الأصل المراد تحليله وتداوله الآن:", list(assets_dict.keys()))
asset = assets_dict[selected_asset_name]

# --- 4. جلب المؤشرات والبيانات الحية للأصل المختار ---
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

    st.markdown(f'<div style="background-color:{bg_color}; padding:10px; border-radius:8px; text-align:center;"><h3 style="color:{text_color}; margin:0;">{signal_text}</h3></div>', unsafe_allow_html=True)

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
        pip_value_needed = risk_amount / sl_pips
        lot_size = pip_value_needed / asset["pip_mult"]
        
        st.success(f"المبلغ المعرض للمخاطرة: {risk_amount:.2f} $")
        st.info(f"حجم العقد المقترح: {abs(lot_size):.2f} Lot")

except Exception as e:
    st.warning("السوق مغلق لعطلة نهاية الأسبوع حالياً. ستعمل الأرقام الفنية فور الافتتاح تلقائياً.")

st.markdown("---")

# --- 5. جدول قوة وتقاطعات العملات الكبرى الداخلي والمضمون للموبايل ---
st.markdown("### ⚖️ جدول حركة وتقاطعات أزواج العملات اليوم (%)")

@st.cache_data(ttl=60)
def get_currency_strength():
    tickers = {
        "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X",
        "AUD/USD": "AUDUSD=X", "USD/CAD": "CAD=X", "USD/CHF": "CHF=X", "NZD/USD": "NZDUSD=X"
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
    df_strength = get_currency_strength()
    if not df_strength.empty:
        def color_change(val):
            try:
                val_float = float(val)
                if val_float > 0: return 'color: #22c55e; font-weight: bold;'
                elif val_float < 0: return 'color: #ef4444; font-weight: bold;'
            except: pass
            return ''
        st.dataframe(df_strength.style.applymap(color_change, subset=['التغير اليومي']), use_container_width=True, hide_index=True)
    else:
        st.warning("جاري سحب التغيرات اليومية للعملات...")
except:
    st.info("الجدول بانتظار حركة تداولات السوق الجديدة...")

st.markdown("---")

# --- 6. عرض الشارت المنفصل والمفكرة المنفصلة بالكامل تحت بعضها ---
st.markdown("### 📈 الرسوم البيانية الحية (مباشر ومدمج)")
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
components.html(chart_js, height=390)

st.markdown("---")

st.markdown("### 📅 المفكرة الاقتصادية والبيانات الاقتصادية (منفصلة ومعربة بالكامل)")
news_js = """
<div class="tradingview-widget-container" style="height:420px;">
  <div class="tradingview-widget-container__widget"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget/events.js" async>
  {
  "width": "100%",
  "height": 420,
  "colorTheme": "dark",
  "isTransparent": false,
  "locale": "ar",
  "importanceFilter": "0,1"
}
  </script>
</div>
"""
components.html(news_js, height=430)

st.caption("تنبيه مخاطر: تم تهيئة النظام والمواعيد تلقائياً وفقاً لتوقيت جمهورية مصر العربية وجلسات التداول العالمية.")
