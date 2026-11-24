import os
import json
import datetime
import base64
import requests
import telebot
from telebot import types

# التوكن الخاص بك (تذكر تغييره من @BotFather عبر /revoke بعد التجربة)
TOKEN = "9152369678:AAGK3TtJ7Z3qD_z3LI7ytdX9TPno1MBhl18"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"
bot = telebot.TeleBot(TOKEN)

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
You are an elite, institutional-grade Quantitative & Technical Analyst with mastery across ALL global financial markets (Forex, Binary Options/Quotex OTC & Live, Crypto, Indices, Commodities) on all timeframes (especially 1M, 5M, 15M, 1H).

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

def analyze_chart(image_path, history_context=""):
    with open(image_path, "rb") as f:
        b64_image = base64.b64encode(f.read()).decode("utf-8")
    
    url = "https://text.pollinations.ai/openai"
    payload = {
        "model": "openai",
        "messages": [
            {
                "role": "system",
                "content": "You are a master financial market analyst. Never guess blindly; prioritize capital preservation."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": MASTER_TRADING_PROMPT + "\n" + history_context},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                ]
            }
        ]
    }
    
    response = requests.post(url, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

@bot.message_handler(commands=["start"])
def handle_start(message):
    welcome_text = (
        "🏛️ **أهلاً بك في منظومة التحليل المؤسسي الشاملة**\n\n"
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
    temp_image = f"chart_{message.chat.id}.jpg"
    
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open(temp_image, "wb") as new_file:
            new_file.write(downloaded_file)
        
        m = load_memory()
        history_context = f"User Historical Performance: {m['wins']} Wins, {m['losses']} Losses (Win Rate: {get_win_rate()}%)."
        analysis_result = analyze_chart(temp_image, history_context)
        
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
        bot.edit_message_text(f"⚠️ **حدث خطأ أثناء قراءة الشارت، أعد إرسال الصورة:**\n`{e}`", message.chat.id, wait_msg.message_id, parse_mode="Markdown")
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
    
    bot.answer_callback_query(call.id, "تم تحديث الذاكرة!")
    base_text = call.message.text.split("━━━━━━━━━━━━━━━━━━")[0]
    bot.edit_message_text(
        f"{base_text}━━━━━━━━━━━━━━━━━━\n{status_msg}\n🏆 **نسبة النجاح المحدثة:** `{get_win_rate()}%`",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )

if __name__ == "__main__":
    # حذف أي Webhook قديم تلقائياً قبل بدء التشغيل
    requests.get(f"{TELEGRAM_API_URL}/deleteWebhook")
    print("Master Institutional Trading Bot is running...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
