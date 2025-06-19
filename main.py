import logging
import random
from telegram import ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, CallbackQueryHandler, ConversationHandler
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Dhikr collection based on your document
DHIKR_COLLECTION = [

    {
        "arabic": "سبحان الله",
        "benefit": "جزء من الكلمات الأربع الأحب إلى الله، ثقيلة في الميزان، وغراس للجنة",
        "reference": "رواه مسلم، وأحمد، والترمذي",
        "category": "الكلمات الأربع الأحب إلى الله"
    },
    {
        "arabic": "الحمد لله",
        "benefit": "جزء من الكلمات الأربع الأحب إلى الله، ثقيلة في الميزان، وغراس للجنة. وتملأ الميزان",
        "reference": "رواه مسلم، والترمذي، والطبراني",
        "category": "الكلمات الأربع الأحب إلى الله"
    },
    {
        "arabic": "لا إله إلا الله",
        "benefit": "أفضل الذكر، وتزن السماوات السبع والأرضين السبع، وغراس للجنة، وثقيلة في الميزان",
        "reference": "رواه مسلم، وأحمد",
        "category": "الكلمات الأربع الأحب إلى الله"
    },
    {
        "arabic": "الله أكبر",
        "benefit": "جزء من أحبّ الكلمات إلى الله، ثقيلة في الميزان، وغراس للجنة",
        "reference": "رواه مسلم، وأحمد",
        "category": "الكلمات الأربع الأحب إلى الله"
    },
    {
        "arabic": "سبحان الله وبحمده",
        "benefit": "من قالها ١٠٠ مرة في اليوم غُفرت ذنوبه وإن كانت مثل زبد البحر. وهي أحب الكلام إلى الله",
        "reference": "رواه البخاري، ومسلم، والترمذي، والطبراني",
        "category": "أذكار التسبيح والحمد"
    },
    {
        "arabic": "سبحان الله العظيم وبحمده",
        "benefit": "من قالها غُرست له نخلة في الجنة",
        "reference": "رواه الترمذي",
        "category": "أذكار التسبيح والحمد"
    },
    {
        "arabic": "سبحان اللهِ عدَدَ ما خلق ، سبحان اللهِ مِلْءَ ما خلَق ، سبحان اللهِ عدَدَ ما في الأرضِ [والسماءِ] سبحان اللهِ مِلْءَ ما في الأرضِ والسماءِ ، سبحان اللهِ عدَدَ ما أحصى كتابُه ، سبحان اللهِ مِلْءَ ما أحصى كتابُه ، سبحان اللهِ عددَ كلِّ شيءٍ ، سبحانَ اللهِ مِلْءَ كلِّ شيءٍ ، الحمدُ للهِ عددَ ما خلق ، والحمدُ لله مِلْءَ ما خلَق ، والحمدُ لله عدَدَ ما في الأرضِ والسماءِ ، والحمدُ لله مِلْءَ ما في الأرضِ والسماءِ ، والحمدُ للهِ عدَدَ ما أحصى كتابُه ، والحمدُ لله مِلْءَ ما أحصى كتابُه ، والحمدُ للهِ عدَدَ كلِّ شيءٍ ، والحمدُ للهِ مِلْءَ كلِّ شيءٍ",
        "benefit": " أفضل وأكثر من ذكر الذاكر ليلاً ونهارًا",
        "reference": "📜 رواه النسائي، وصححه الألباني",
        "category": "الذكر المضاعف"
    },
    {
        "arabic": "سبحان الله وبحمده، سبحان الله العظيم",
        "benefit": "كلمتان خفيفتان على اللسان، ثقيلتان في الميزان، حبيبتان إلى الرحمن",
        "reference": "رواه البخاري، ومسلم",
        "category": "الكلمتان الخفيفتان على اللسان"
    },
    {
        "arabic": "سبحان الله وبحمده، عدد خلقه، ورضا نفسه، وزنة عرشه، ومداد كلماته",
        "benefit": "إذا قيلت ثلاث مرات، ترجح جميع الأذكار الأخرى في اليوم",
        "reference": "رواه مسلم، والنسائي",
        "category": "الذكر الذي يرجح جميع الأذكار"
    },
    {
        "arabic": "لا إله إلا الله وحده لا شريك له، له الملك وله الحمد، وهو على كل شيء قدير",
        "benefit": "من قالها ١٠٠ مرة في اليوم: كُتب له ١٠٠ حسنة، مُحي عنه ١٠٠ سيئة، وكانت حرزاً من الشيطان",
        "reference": "رواه البخاري، ومسلم، والترمذي، وأحمد",
        "category": "التوحيد الكامل"
    },
    {
        "arabic": "لا حول ولا قوة إلا بالله",
        "benefit": "كنز من كنوز الجنة، وباب من أبوابها، ودواء من ٩٩ داء أيسرها الهم",
        "reference": "رواه البخاري، ومسلم، وأحمد، والترمذي، وأبو يعلى، والطبراني، وابن حبان، والحاكم",
        "category": "كنز من كنوز الجنة"
    },
    {
        "arabic": "أستغفر الله العظيم الذي لا إله إلا هو الحي القيوم وأتوب إليه",
        "benefit": "من قالها ثلاث مرات غُفرت ذنوبه وإن كان فارًّا من الزحف. ومن لزم الاستغفار جعل الله له من كل هم فرجًا ومن كل ضيق مخرجًا",
        "reference": "رواه الترمذي، وأبو داود، والحاكم، وصححه الألباني",
        "category": "الاستغفار الكامل"
    },
    {
        "arabic": "اللهم صل وسلم على محمد",
        "benefit": "من صلى على النبي مرة، صلى الله عليه بها عشرًا، وحُطت عنه عشر خطيئات، ورفعت له عشر درجات",
        "reference": "رواه النسائي، وأحمد، والترمذي، وصححه الألباني",
        "category": "الصلاة على النبي"
    },
    {
        "arabic": "لا إله إلا الله، والله أكبر، وسبحان الله، والحمد لله، ولا حول ولا قوة إلا بالله",
        "benefit": "لا يقولها أحد إلا غُفرت ذنوبه وإن كانت أكثر من زبد البحر",
        "reference": "رواه أحمد، وصححه الألباني",
        "category": "الذكر الذي يغفر الذنوب"
    },
    {
        "arabic": "الحمد لله كثيرًا",
        "benefit": "قال الملك: لا أستطيع أن أكتبها، فرفعها إلى الله، فقال: اكتبوها كما قال عبدي \"كثيرًا\"",
        "reference": "رواه الطبراني",
        "category": "الحمد الكثير"
    },
    {
        "arabic": "الله أكبر كبيرًا، والحمد لله كثيرًا، وسبحان الله بكرة وأصيلًا",
        "benefit": "تعجب النبي ﷺ منها، وفتحت لها أبواب السماء",
        "reference": "رواه مسلم",
        "category": "الذكر الذي فتحت له أبواب السماء"
    },
    {
        "arabic": "رضيت بالله ربًّا، وبالإسلام دينًا، وبمحمد ﷺ رسولًا",
        "benefit": "إقرار بالرضا عن أصول الدين، يجلب الطمأنينة والقبول",
        "reference": "رواه مسلم",
        "category": "إقرار الرضا"
    },
    {
        "arabic": "قل هو الله أحد",
        "benefit": "تعدل ثلث القرآن",
        "reference": "رواه البخاري، ومسلم، والترمذي، وأحمد",
        "category": "سورة الإخلاص"
    },
    {
        "arabic": "قل هو الله أحد",
        "benefit": "، من قرأها عشر مرات بُني له قصر في الجنة",
        "reference": "رواه البخاري، ومسلم، والترمذي، وأحمد",
        "category": "سورة الإخلاص"
    },
    {
        "arabic": "قل يا أيها الكافرون",
        "benefit": "تعدل ربع القرآن",
        "reference": "رواه الترمذي، والطبراني",
        "category": "سورة الكافرون"
    },
    {
        "arabic": "رب اغفر لي وتب علي، إنك أنت التواب الغفور",
        "benefit": "كان النبي ﷺ يقولها في المجلس الواحد مائة مرة",
        "reference": "رواه أحمد، والترمذي",
        "category": "دعاء الاستغفار"
    },
    {
        "arabic": "سُبحانَ اللهِ والحَمدُ للهِ ولا إلهَ إلَّا اللهُ واللهُ أكبَرُ وتَبارَكَ اللهُ",
        "benefit": "تلقّاها ملك فعرج بها إلى الله، وكلما مرّ على ملأ من الملائكة استغفروا لقائلها، حتى يُحيي بها وجه الرحمن",
        "reference": "رواه الذهبي في العلو، وصححه الألباني في مختصر العلو",
        "category": "الذكر الذي يُحيي وجه الرحمن"
    }
]

# قائمة الأذكار المقترحة بانتظار موافقة الأدمن
PENDING_DHIKR = []

# عرّف معرف الأدمن (يمكنك تغييره لاحقاً)
ADMIN_ID = 5137387873  # ضع هنا معرفك كأدمن

# حالة انتظار اقتراح ذكر من المستخدم
awaiting_suggestion = set()

# حالة انتظار إضافة ذكر من الأدمن
awaiting_admin_add = set()

# تعريف pending_counts في أعلى الملف لتفادي الخطأ عند استخدامه في الدوال.
current_dhikr_data = {}  # dhikr_id -> {arabic, message_id, chat_id, count (optional)}
pending_counts = {}      # user_id -> (dhikr_id, message_id, chat_id)

# أمر حذف ذكر من طرف الأدمن فقط (قائمة كباقي الأوامر)
async def delete_dhikr_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ هذا الأمر للأدمن فقط.")
        return
    if not DHIKR_COLLECTION:
        await update.message.reply_text("لا توجد أذكار حالياً.")
        return
    keyboard = []
    for idx, entry in enumerate(DHIKR_COLLECTION):
        label = entry["arabic"]
        # إذا كان هناك عدد محدد لهذا الذكر، أضف العدد في الزر
        if "count" in entry and entry["count"]:
            label += f" (عدد: {entry['count']})"
        keyboard.append([
            InlineKeyboardButton(f"🗑️ {label}", callback_data=f"del_{idx}")
        ])
    await update.message.reply_text(
        "اختر الذكر الذي تريد حذفه:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# زر حذف الذكر للأدمن (يحذف رسالة القائمة بعد الحذف)
async def delete_dhikr_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    if user_id != ADMIN_ID:
        await query.edit_message_text("❌ هذا الأمر للأدمن فقط.")
        return
    if data.startswith("del_"):
        idx = int(data.split("_", 1)[1])
        if idx >= len(DHIKR_COLLECTION):
            await query.edit_message_text("❌ الذكر غير موجود أو تم حذفه مسبقاً.")
            return
        removed = DHIKR_COLLECTION.pop(idx)
        # حذف كل dhikr_id من current_dhikr_data المرتبط بهذا الذكر
        to_remove = [k for k, v in current_dhikr_data.items() if v["arabic"] == removed["arabic"]]
        for k in to_remove:
            del current_dhikr_data[k]
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(chat_id=query.message.chat_id, text=f"🗑️ تم حذف الذكر: {removed['arabic']}")
    else:
        await review_callback(update, context)

# Format dhikr + count with Arabic grammar
def get_count_text(dhikr: str, count: int | None) -> str:
    if count is None:
        return f"{dhikr}"
    elif 2 <= count <= 10:
        return f"{dhikr} {count} مرات"
    else:
        return f"{dhikr} {count} مرة"

# Inline buttons
def create_keyboard(dhikr_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("المرجع", callback_data=f"ref_{dhikr_id}"),
            InlineKeyboardButton("الفضل", callback_data=f"benefit_{dhikr_id}"),
            InlineKeyboardButton("🔢 العدد", callback_data=f"count_{dhikr_id}")
        ]
    ])

def split_text(text, max_length=4096):
    # تقسيم النص الطويل إلى أجزاء لا تتجاوز max_length
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

async def send_long_message(message_func, text, **kwargs):
    # يرسل النص الطويل على عدة رسائل
    chunks = split_text(text)
    sent_msgs = []
    for chunk in chunks:
        msg = await message_func(chunk, **kwargs)
        sent_msgs.append(msg)
    return sent_msgs

# Random dhikr
async def get_random_dhikr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    dhikr = random.choice(DHIKR_COLLECTION)
    dhikr_id = str(random.randint(10000, 99999))
    dhikr_entry = {
        "arabic": dhikr["arabic"],
        "benefit": dhikr["benefit"],
        "reference": dhikr["reference"]
    }
    current_dhikr_data[dhikr_id] = dhikr_entry

    text = f"📿 `{get_count_text(dhikr['arabic'], None)}`"
    keyboard = create_keyboard(dhikr_id)
    # استخدم send_long_message
    msgs = await send_long_message(
        update.message.reply_text, text, parse_mode="Markdown", reply_markup=keyboard
    )
    # Store message info for later editing (أول رسالة فقط)
    dhikr_entry["message_id"] = msgs[0].message_id
    dhikr_entry["chat_id"] = msgs[0].chat.id

# Button handling
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("select_"):
        idx = int(data.split("_", 1)[1])
        dhikr = DHIKR_COLLECTION[idx]
        dhikr_id = str(random.randint(10000, 99999))
        dhikr_entry = {
            "arabic": dhikr["arabic"],
            "benefit": dhikr["benefit"],
            "reference": dhikr["reference"]
        }
        current_dhikr_data[dhikr_id] = dhikr_entry
        text = f"📿 `{get_count_text(dhikr['arabic'], None)}`"
        keyboard = create_keyboard(dhikr_id)
        # استخدم send_long_message
        msgs = await send_long_message(
            query.message.reply_text, text, parse_mode="Markdown", reply_markup=keyboard
        )
        dhikr_entry["message_id"] = msgs[0].message_id
        dhikr_entry["chat_id"] = msgs[0].chat.id
        try:
            await query.message.delete()
        except Exception:
            pass
        return

    action, dhikr_id = data.split("_", 1)

    if dhikr_id not in current_dhikr_data:
        await query.edit_message_text("❌ الذكر غير متاح.")
        return

    dhikr = current_dhikr_data[dhikr_id]

    if action == "ref":
        await query.edit_message_text(f"📚 المرجع:\n{dhikr['reference']}", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 العودة", callback_data=f"back_{dhikr_id}")]
        ]))
    elif action == "benefit":
        await query.edit_message_text(f" الفضل:\n{dhikr['benefit']}", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 العودة", callback_data=f"back_{dhikr_id}")]
        ]))
    elif action == "count":
        # Await user input
        user_id = query.from_user.id
        pending_counts[user_id] = (dhikr_id, query.message.message_id, query.message.chat.id)
        await query.edit_message_text("🔢 *أدخل العدد:*", parse_mode="Markdown")
    elif action == "back":
        count = dhikr.get("count")
        text = f"📿 `{get_count_text(dhikr['arabic'], count)}`"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=create_keyboard(dhikr_id))

# Handle user input for count
async def handle_number_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    if user_id not in pending_counts:
        return

    if not text.isdigit():
        await update.message.reply_text("⚠️ الرجاء إدخال رقم صحيح.")
        return

    count = int(text)
    dhikr_id, msg_id, chat_id = pending_counts.pop(user_id)

    if dhikr_id not in current_dhikr_data:
        await update.message.reply_text("❌ الذكر لم يعد متاحاً.")
        return

    dhikr = current_dhikr_data[dhikr_id]
    dhikr["count"] = count

    new_text = f"📿 `{get_count_text(dhikr['arabic'], count)}`"
    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=msg_id,
        text=new_text,
        parse_mode="Markdown",
        reply_markup=create_keyboard(dhikr_id)
    )
    await update.message.delete()

# أمر اقتراح ذكر جديد
async def suggest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    awaiting_suggestion.add(user_id)
    await update.message.reply_text("✍️ أرسل الذكر الذي تريد اقتراحه (مثال: سبحان الله):")

# استقبال نص الذكر المقترح بدون دعم العدد
async def handle_suggestion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id in awaiting_suggestion:
        if len(text) < 3:
            await update.message.reply_text("⚠️ الذكر المقترح قصير جداً.")
            return

        dhikr_text = text
        user_info = update.effective_user
        username = f"@{user_info.username}" if user_info.username else user_info.first_name

        if user_id == ADMIN_ID:
            # إذا كان الأدمن، يتم الإضافة مباشرة بدون مراجعة
            new_entry = {
                "arabic": dhikr_text,
                "benefit": "(مضاف من الأدمن)",
                "reference": "(لم يُحدد)",
                "category": "مضاف من الأدمن"
            }
            DHIKR_COLLECTION.append(new_entry)
            awaiting_suggestion.remove(user_id)
            await update.message.reply_text(f"✅ تم إضافة الذكر مباشرة: {dhikr_text}")
            return

        # المستخدم العادي → إرسال للإدارة للمراجعة
        entry = {"arabic": dhikr_text, "user_id": user_id}
        PENDING_DHIKR.append(entry)
        awaiting_suggestion.remove(user_id)

        await update.message.reply_text("✅ تم إرسال اقتراحك للأدمن للمراجعة.")

        admin_message = (
            f"📩 *اقتراح ذكر جديد*\n\n"
            f"🧑‍💻 *من المستخدم:* {username}\n"
            f"🆔 *معرف المستخدم:* `{user_id}`\n"
            f"📿 *الذكر المقترح:* {dhikr_text}\n\n"
            f"*اختر الإجراء المناسب:*"
        )

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ قبول", callback_data=f"accept_{len(PENDING_DHIKR)-1}"),
                InlineKeyboardButton("❌ رفض", callback_data=f"reject_{len(PENDING_DHIKR)-1}")
            ]
        ])

        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=admin_message,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"خطأ في إرسال رسالة للأدمن: {e}")


# زر القبول/الرفض للأدمن
async def review_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("accept_") or data.startswith("reject_"):
        action, idx = data.split("_", 1)
        idx = int(idx)
        if idx >= len(PENDING_DHIKR):
            await query.edit_message_text("❌ هذا المقترح لم يعد متاحاً.")
            return
        item = PENDING_DHIKR.pop(idx)
        if action == "accept":
            new_entry = {
                "arabic": item["arabic"],
                "benefit": "(مقترح من المستخدم)",
                "reference": "(لم يُحدد)",
                "category": "مقترحات"
            }
            if "count" in item:
                new_entry["count"] = item["count"]
            DHIKR_COLLECTION.append(new_entry)
            await query.edit_message_text(f"✅ تم قبول الذكر وإضافته: {item['arabic']}")
        else:
            await query.edit_message_text("❌ تم رفض الذكر.")
    else:
        await button_callback(update, context)


# Router for all callback queries
async def button_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data.startswith("del_"):
        await delete_dhikr_callback(update, context)
    elif data.startswith("accept_") or data.startswith("reject_"):
        await review_callback(update, context)
    else:
        await button_callback(update, context)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    count = len(DHIKR_COLLECTION)
    text = (
        "🧭 مرحباً بك في بوت الأذكار!\n\n"
        "يقدم لك هذا البوت أذكارًا مأثورة من السنة النبوية، مع بيان فضلها ومصدرها.\n\n"
        "📌 اختر أمراً من الأزرار التالية:\n"
        f"\n📚 يحتوي البوت حالياً على {count} ذكرًا مختلفًا.\n"
        "\n✨ لا تنس مشاركة الأجر بنشر البوت!"
    )

    keyboard = [
        ["📿 ذكر عشوائي", "📋 كل الأذكار"],
        ["🗂 اختر ذكرًا", "➕ اقترح ذكرًا"],
        ["🗑 حذف ذكر"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )

    await update.message.reply_text(text, reply_markup=reply_markup)

# Show all dhikr in one message
async def show_all_dhikr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    dhikr_texts = [f"📿 {entry['arabic']}" for entry in DHIKR_COLLECTION]
    text = "\n\n".join(dhikr_texts)

    # Telegram message limit is 4096 characters
    if len(text) <= 4096:
        await update.message.reply_text(text)
    else:
        # Split into multiple messages if too long
        chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for chunk in chunks:
            await update.message.reply_text(chunk)

# Choose dhikr
async def choose_dhikr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # عرض قائمة أذكار مختصرة (أول 8 أذكار مثلاً)
    keyboard = []
    for idx, entry in enumerate(DHIKR_COLLECTION[:]):
        keyboard.append([
            InlineKeyboardButton(entry["arabic"], callback_data=f"select_{idx}")
        ])
    await update.message.reply_text(
        "اختر الذكر الذي تريده:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # 1) If user is awaiting to enter the number for a dhikr:
    if user_id in pending_counts:
        return await handle_number_reply(update, context)

    # 2) If user just issued /suggest and is awaiting input:
    if user_id in awaiting_suggestion:
        return await handle_suggestion(update, context)

    # 4) Otherwise, treat as one of the menu text commands:
    if text == "📿 ذكر عشوائي":
        return await get_random_dhikr(update, context)
    if text == "📋 كل الأذكار":
        return await show_all_dhikr(update, context)
    if text == "🗂 اختر ذكرًا":
        return await choose_dhikr(update, context)
    if text == "➕ اقترح ذكرًا":
        return await suggest_command(update, context)
    if text == "🗑 حذف ذكر":
        return await delete_dhikr_command(update, context)

    # else: ignore or send a help prompt
    # await update.message.reply_text("❔ استخدم الأزرار أو /help لمعرفة الأوامر.")


# Main bot entry
def main():
    TOKEN = "7631271424:AAGI-pAitzEwMSMkZNT9QRuhWWxH_2mx5NE"
    app = Application.builder().token(TOKEN).build()

    # إضافة أوامر البوت (commands) لتسهيل الاستخدام بدون الحاجة لكتابة / يدوياً
    commands = [
        BotCommand("start", "بدء المحادثة مع البوت"),
        BotCommand("dhikr", "احصل على ذكر عشوائي"),
        BotCommand("all", "عرض جميع الأذكار بدون شروحات"),
        BotCommand("choose", "اختر ذكرًا من القائمة"),
        BotCommand("suggest", "اقترح ذكرًا جديدًا (بانتظار موافقة الأدمن)"),
        BotCommand("delete_dhikr", "حذف ذكر (للأدمن)"),
    ]
    async def set_commands(app):
        await app.bot.set_my_commands(commands)
    app.post_init = set_commands

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dhikr", get_random_dhikr))
    app.add_handler(CommandHandler("all", show_all_dhikr))
    app.add_handler(CommandHandler("choose", choose_dhikr))
    app.add_handler(CommandHandler("suggest", suggest_command))
    app.add_handler(CommandHandler("delete_dhikr", delete_dhikr_command))
    app.add_handler(CallbackQueryHandler(button_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

