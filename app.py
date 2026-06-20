import streamlit as st
import yfinance as yf
import pandas as pd
import streamlit.components.v1 as components

# إعدادات الصفحة الواسعة والمظهر الداكن الافتراضي
st.set_page_config(page_title="منصة استخبارات AUD/USD", page_icon="💎", layout="wide")

st.title("💎 منصة استخبارات وتداول زوج AUD/USD المتكاملة")
st.write("تحليل فني + سيولة وحجم + مفكرة اقتصادية + جدول تقاطعات العملات + إدارة مخاطر آمنة")

st.markdown("---")

# --- 1. جلب البيانات الحية وحساب المؤشرات الفنية والسيولة ---
@st.cache_data(ttl=60) # تحديث البيانات تلقائياً كل دقيقة
def get_live_data():
    ticker = yf.Ticker("AUDUSD=X")
    df = ticker.history(period="2mo", interval="1h")
    
    # حساب مؤشر RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # حساب المتوسطات المتحركة
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    
    # حساب متوسط حجم التداول لآخر 24 ساعة
    df['Vol_Avg_24h'] = df['Volume'].rolling(window=24).mean()
    
    return df

try:
    data = get_live_data()
    current_price = data['Close'].iloc[-1]
    current_rsi = data['RSI'].iloc[-1]
    ema_50 = data['EMA_50'].iloc[-1]
    current_volume = data['Volume'].iloc[-1]
    avg_volume = data['Vol_Avg_24h'].iloc[-1]
    
    # منطق الإشارات ونقاط الدخول والخروج
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

    # عرض التنبيه الرئيسي للإشارة
    st.markdown(f'<div style="background-color:{bg_color}; padding:20px; border-radius:10px; text-align:center;"><h2 style="color:{text_color};">{signal_text}</h2></div>', unsafe_allow_html=True)
    
    # تنبيه مراقبة حجم التداول (Volume Alert)
    st.markdown(" ")
    if current_volume > (avg_volume * 1.5):
        st.markdown(f'<div style="background-color:#854d0e; padding:12px; border-radius:8px; text-align:center; border: 1px solid #fef08a;"><h4 style="color:#fef08a; margin:0;">🔥 تنبيه سيولة: حجم التداول الحالي ({current_volume:,.0f}) أعلى من المتوسط اليومي ({avg_volume:,.0f}) بنسبة 150%+ (دخول حيتان ومؤسسات!)</h4></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="background-color:#1e293b; padding:12px; border-radius:8px; text-align:center;"><p style="color:#94a3b8; margin:0;">ℹ️ حجم التداول مستقر وحركة السيولة طبيعية حالياً ({current_volume:,.0f} / المتوسط: {avg_volume:,.0f})</p></div>', unsafe_allow_html=True)

    # تقسيم الشاشة إلى جزأين: الأول للتوصية والأدوات، والثاني للكروسات المتقدمة
    main_col1, main_col2 = st.columns([1, 1])

    with main_col1:
        st.markdown("### 📊 تفاصيل التوصية الرقمية الحالية")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="💵 السعر الحالي", value=f"{current_price:.5f}")
            st.metric(label="🎯 أخذ الربح المقترح (TP)", value=f"{tp:.5f}", delta=f"➕ {tp_pips} Pips")
        with col2:
            st.metric(label="📥 سعر الدخول المقترح", value=f"{entry_price:.5f}")
            st.metric(label="🛑 وقف الخسارة المقترح (SL)", value=f"{sl:.5f}", delta=f"➖ {sl_pips} Pips")
        
        st.markdown("---")
        # حاسبة حجم اللوت وإدارة المخاطر
        st.markdown("### 🧮 حاسبة حجم اللوت الآمن (إدارة مخاطر)")
        balance = st.number_input("💰 أدخل حجم حسابك المالي ($):", min_value=10, value=1000, step=100)
        risk_percent = st.slider("⚠️ حدد نسبة المخاطرة المقبولة في الصفقة (%):", min_value=0.5, max_value=5.0, value=1.0, step=0.5)
        
        risk_amount = balance * (risk_percent / 100)
        pip_value_needed = risk_amount / sl_pips
        lot_size = pip_value_needed / 10.0
        
        st.success(f"💵 المبلغ المعرض للمخاطرة في هذه الصفقة: **{risk_amount:.2f} $**")
        st.info(f"👔 حجم العقد (Lot Size) الموصى به لصفقتك: **{lot_size:.2f}** لوت ستاندرد")

    with main_col2:
        # --- الإضافة المطلوبة: جدول الـ Cross الحقيقي من TradingView لمقارنة قوتهم ضد كل العملات ---
        st.markdown("### 🔀 جدول تقاطعات وقوة العملات الكبرى اليوم (Cross Rates)")
        cross_widget = """
        <div class="tradingview-widget-container">
          <iframe src="https://s.tradingview.com/embed-widget/forex-cross-rates/?locale=ar&width=100%25&height=380&currencies=AUD%2CUSD%2CEUR%2CGBP%2CJPY%2CCHF%2CCAD&theme=dark" width="100%" height="380" frameborder="0" allowtransparency="true" scrolling="no"></iframe>
        </div>
        """
        components.html(cross_widget, height=390)

except Exception as e:
    st.error("جاري تحميل البيانات الحية من السيرفر المالي... يرجى تحديث الصفحة.")

st.markdown("---")

# تقسيم الفريمات والأخبار أسفل المنصة
st.markdown("### 📈 التحليل البصري والمفكرة الاقتصادية")
bot_col1, bot_col2 = st.columns([2, 1])

with bot_col1:
    tab1, tab2, tab3 = st.tabs(["🕒 شارت 1 ساعة (1H)", "⏳ شارت 4 ساعات (4H)", "📅 شارت يومي (1D)"])
    
    def generate_tradingview_widget(interval):
        return f"""
        <div class="tradingview-widget-container" style="height:450px;">
          <div id="tradingview_{interval}" style="height:450px;"></div>
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
        components.html(generate_tradingview_widget("60"), height=470)
    with tab2:
        components.html(generate_tradingview_widget("240"), height=470)
    with tab3:
        components.html(generate_tradingview_widget("D"), height=470)

with bot_col2:
    st.markdown("📅 **أخبار الاقتصاد اليومية القوية**")
    cal_widget = """
    <div class="tradingview-widget-container">
      <iframe src="https://s.tradingview.com/embed-widget/events/?locale=ar&width=100%25&height=450&theme=dark&importanceFilter=-1%2C0%2C1" width="100%" height="450" frameborder="0" allowtransparency="true" scrolling="no"></iframe>
    </div>
    """
    components.html(cal_widget, height=470)

st.caption("تنبيه مخاطر: هذه المنصة مطورة برمجياً للمساعدة التقنية ولا تعتبر توصية استثمارية مطلقة.")
