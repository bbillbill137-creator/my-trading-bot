import os
import json
import time
import datetime
import threading
import requests
import telebot
from telebot import types
from flask import Flask
from google import genai
from google.genai import types as genai_types

# التوكن الخاص ببوت تليجرام ومفتاح Gemini API
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "9152369678:AAGK3TtJ7Z3qD_z3LI7ytdX9TPno1MBhl18")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6IZF5jcSZeaMnqPf9UN0mhrsaeCf09SRjczs8ReNs2KcA")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# خادم Flask لإبقاء البوت نشطاً 24/7 على منصة Render ومنع توقفه
app = Flask(__name__)

@app.route("/")
def health_check():
    return "Sultan Master Trading Bot is Alive and Running 24/7!", 200

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

MEMORY_FILE = "memory.json"

def load_memory():
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {"trades": [], "wins": 0, "losses": 0}

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_win_rate():
    m = load_memory()
    total = m["wins"] + m["losses"]
    return 0.0 if total == 0 else round((m["wins"] / total) * 100, 1)

MASTER_TRADING_PROMPT = """
You are an elite, institutional-grade Quantitative & Technical Analyst with mastery across ALL global financial markets (Forex, Binary Options/Quotex OTC & Live, Crypto, Indices, Commodities) on all timeframes (1M, 5M, 15M, 1H, 4H).

Analyze the provided chart image by synthesizing ALL major schools of technical analysis simultaneously:
1. ICT & Smart Money Concepts (SMC):
   - Market Structure: Identify clear Break of Structure (BOS) or Change of Character (CHoCH).
   - Liquidity: Detect Buy-Side Liquidity (BSL), Sell-Side Liquidity (SSL), Equal Highs/Lows (EQH/EQL), and recent Liquidity Sweeps / Stop Hunts.
   - Institutional PD Arrays: Locate valid Order Blocks (OB), Breaker Blocks, Fair Value Gaps (FVG / Imbalance), and Optimal Trade Entry (OTE 0.618 - 0.786 Fibonacci).
   - Context: Check Premium vs. Discount zones, Psychological Round Numbers, and London/New York Killzone timing if visible.
2. Supply & Demand + Price Action:
   - Identify fresh Rally-Base-Rally (RBR), Drop-Base-Drop (DBD), Drop-Base-Rally (DBR), and Rally-Base-Drop (RBD) zones with strong Extended Range Candles (ERC).
   - Confirm entry triggers via Candlestick Price Action (Engulfing, Pin Bar/Rejection wicks, Morning/Evening Star).
3. Classical, Geometric & Wave Analysis:
   - Check major Support/Resistance levels, Trendlines, Channels, Chart Patterns (Head & Shoulders, Double Top/Bottom, Wedges), Harmonic completions, and Elliott Wave impulse/correction phase.

DECISION & RISK MANAGEMENT RULES:
- Calculate a strict Confluence Score (0% to 100%) based on how many schools agree on the same direction.
- If Confluence Score is LESS than 75%, or the market is choppy/ranging with no clear liquidity sweep, you MUST output: NO TRADE.
- Specify exact Entry Timing (e.g., Immediate on candle close / At pullback to FVG-OB) and recommended Expiry/Duration (e.g., 15-30 min for 5M chart, or SL/TP levels for Forex/Crypto).

STRICT OUTPUT FORMAT (Reply ONLY in clear, professional Arabic using this exact structure):
📊 **الزوج / الأصل:** [اسم الزوج والإطار الزمني]
📈 **الاتجاه العام (الهيكل):** [صاعد / هابط / عرضي + ذكر BOS أو CHoCH]
🎯 **القرار النهائي:** [شراء UP 🟢 / بيع DOWN 🔴 / ممنوع التداول NO TRADE ⛔]
⏱️ **توقيت الدخول والمدة:** [نقطة الدخول الدقيقة + مدة الصفقة المقترحة]
🔥 **نسبة الثقة والتوافق:** [النسبة المئوية %]
🧠 **التحليل الشامل (دمج المدارس):**
- **السيولة و SMC:** [شرح سحب السيولة، الأوردر بلوك، أو الفجوة FVG]
- **العرض والطلب والبرايس أكشن:** [شرح المنطقة وسلوك الشموع]
- **الدعوم والمؤشرات الهندسية:** [المستويات المحورية والفيبوناتشي]
⚠️ **ملاحظة إدارة المخاطر:** [سبب التوصية أو سبب رفض الصفقة]
"""

def analyze_chart_with_gemini(image_path, history_context=""):
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            genai_types.Part.from_bytes(
                data=image_bytes,
                mime_type="image/jpeg",
            ),
            MASTER_TRADING_PROMPT + "\n" + history_context
        ]
    )
    return response.text

@bot.message_handler(commands=["start"])
def handle_start(message):
    welcome_text = (
        "🏛️ **أهلاً بك في منظومة التحليل المؤسسي الشاملة (Bot Sultan)**\n\n"
        "أرسل لي لقطة شاشة (صورة) لأي شارت وسأقوم بتحليله فوراً عبر دمج:\n"
        "• مدارس **ICT & Smart Money** (السيولة، الأوردر بلوك، FVG)\n"
        "• مناطق **العرض والطلب** والبرايس أكشن\n"
        "• التحليل الكلاسيكي والفيبوناتشي وموجات إليوت\n\n"
        f"📊 **نسبة نجاحك الحالية:** `{get_win_rate()}%`\n"
        "📌 أرسل `/stats` لعرض سجل الصفقات الكامل."
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(commands=["stats"])
def handle_stats(message):
    m = load_memory()
    total = m["wins"] + m["losses"]
    stats_text = (
        "📈 **إحصائيات الأداء المحفوظة:**\n\n"
        f"✅ **الصفقات الرابحة (WIN):** `{m['wins']}`\n"
        f"❌ **الصفقات الخاسرة (LOSS):** `{m['losses']}`\n"
        f"🔢 **إجمالي الصفقات:** `{total}`\n"
        f"🏆 **نسبة النجاح (Win Rate):** `{get_win_rate()}%`"
    )
    bot.reply_to(message, stats_text, parse_mode="Markdown")

@bot.message_handler(content_types=["photo"])
def handle_chart_photo(message):
    wait_msg = bot.reply_to(message, "⏳ **جاري فحص هيكل السوق، السيولة، ومناطق العرض والطلب... انتظر قليلاً**")
    temp_image = f"chart_{message.chat.id}_{int(time.time())}.jpg"
    
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open(temp_image, "wb") as new_file:
            new_file.write(downloaded_file)
        
        m = load_memory()
        history_context = f"User Historical Performance: {m['wins']} Wins, {m['losses']} Losses (Win Rate: {get_win_rate()}%)."
        analysis_result = analyze_chart_with_gemini(temp_image, history_context)
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_win = types.InlineKeyboardButton("✅ WIN (ربح)", callback_data="win")
        btn_loss = types.InlineKeyboardButton("❌ LOSS (خسارة)", callback_data="loss")
        markup.add(btn_win, btn_loss)
        
        bot.delete_message(message.chat.id, wait_msg.message_id)
        bot.send_message(
            message.chat.id,
            f"{analysis_result}\n\n━━━━━━━━━━━━━━━━━━\n📌 **بعد انتهاء الصفقة، سجل النتيجة لتحديث الذاكرة:**",
            reply_markup=markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.edit_message_text(
            f"⚠️ **حدث خطأ أثناء قراءة الشارت، تأكد من مفتاح Gemini API أو أعد إرسال الصورة:**\n`{e}`",
            message.chat.id,
            wait_msg.message_id,
            parse_mode="Markdown"
        )
    finally:
        if os.path.exists(temp_image):
            os.remove(temp_image)

@bot.callback_query_handler(func=lambda call: call.data in ["win", "loss"])
def handle_trade_result(call):
    m = load_memory()
    if call.data == "win":
        m["wins"] += 1
        status_msg = "✅ **تم تسجيل الصفقة كـ ربح (WIN)**"
    else:
        m["losses"] += 1
        status_msg = "❌ **تم تسجيل الصفقة كـ خسارة (LOSS)**"
    
    m["trades"].append({
        "result": call.data.upper(),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_memory(m)
    
    bot.answer_callback_query(call.id, "تم تحديث الذاكرة بنجاح!")
    original_text = call.message.text.split("━━━━━━━━━━━━━━━━━━")
    bot.edit_message_text(
        f"{original_text}\n━━━━━━━━━━━━━━━━━━\n{status_msg}\n🏆 **نسبة النجاح المحدثة:** `{get_win_rate()}%`",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )

def start_bot():
    try:
        requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook", timeout=10)
    except Exception:
        pass
    print("Bot Sultan is running 24/7 with Flask & Gemini...")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Polling error, restarting in 5s: {e}")
            time.sleep(5)

if __name__ == "__main__":
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    start_bot()
