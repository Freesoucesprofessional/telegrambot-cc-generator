import os
import json
import random
import asyncio
import threading
import re
import requests
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, ContextTypes, filters
)
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
BOT_TOKEN = os.environ.get("BOT_TOKEN")
PORT      = int(os.environ.get("PORT", 8080))
MONGO_URI = os.environ.get("MONGO_URI")

# ── ADMIN CONFIG ──────────────────────────────────────────────────────────────
ADMIN_IDS = [1793697840]
# ─────────────────────────────────────────────────────────────────────────────

# ── CONFIG ────────────────────────────────────────────────────────────────────
CHANNEL_URL  = "https://t.me/danger_boy_op1"
OWNER_URL    = "https://t.me/danger_boy_op"
CHANNEL_NAME = "𒆜ﮩ٨ـﮩ٨ـ𝐉𝐎𝐈𝐍 𝐂𝐇𝐀𝐍𝐍𝐄𝐋ﮩ٨ـﮩ٨ـ𒆜"
OWNER_NAME   = "𒆜ﮩ٨ـﮩ٨ـ𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑ﮩ٨ـﮩ٨ـ𒆜"
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────

# ── MongoDB Setup ─────────────────────────────────────────────────────────────
_mongo_client = None
_mongo_db     = None

def get_db():
    global _mongo_client, _mongo_db
    if _mongo_client is None:
        _mongo_client = MongoClient(MONGO_URI)
        _mongo_db     = _mongo_client["telegram_bot"]
        _mongo_db.users.create_index("user_id", unique=True)
        print("[✓] MongoDB connected")
    return _mongo_db

def store_user(user_id: int, username: str = None, first_name: str = None, last_name: str = None):
    db = get_db()
    db.users.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "username":   username,
                "first_name": first_name,
                "last_name":  last_name,
            },
            "$setOnInsert": {
                "user_id":       user_id,
                "joined_at":     datetime.now(timezone.utc),
                "registered":    False,
                "registered_at": None,
            }
        },
        upsert=True
    )

def register_user(user_id: int) -> bool:
    db = get_db()
    result = db.users.update_one(
        {"user_id": user_id, "registered": False},
        {"$set": {"registered": True, "registered_at": datetime.now(timezone.utc)}}
    )
    return result.modified_count == 1

def get_all_users(registered_only: bool = False):
    db = get_db()
    query = {"registered": True} if registered_only else {}
    return list(db.users.find(query, {"_id": 0}))

def get_all_user_ids() -> list:
    db = get_db()
    return [u["user_id"] for u in db.users.find({}, {"user_id": 1, "_id": 0})]

def get_stats() -> dict:
    db    = get_db()
    total = db.users.count_documents({})
    reg   = db.users.count_documents({"registered": True})
    return {"total": total, "registered": reg}

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS
# ─────────────────────────────────────────────────────────────────────────────

# ── Load JSON databases ───────────────────────────────────────────────────────
_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database")

with open(os.path.join(_DIR, "bins.json"),    "r", encoding="utf-8") as _f: BIN_DB: dict       = json.load(_f)
with open(os.path.join(_DIR, "country.json"), "r", encoding="utf-8") as _f: COUNTRY_DATA: dict = json.load(_f)
with open(os.path.join(_DIR, "names.json"),   "r", encoding="utf-8") as _f: NAMES_DATA: dict   = json.load(_f)
# ─────────────────────────────────────────────────────────────────────────────

COUNTRY_ALIASES = {
    "al":"Albania","dz":"Algeria","ar":"Argentina","am":"Armenia","au":"Australia",
    "at":"Austria","az":"Azerbaijan","bs":"Bahamas","bh":"Bahrain","bd":"Bangladesh",
    "bb":"Barbados","by":"Belarus","be":"Belgium","bo":"Bolivia","bw":"Botswana",
    "br":"Brazil","bn":"Brunei","kh":"Cambodia","cm":"Cameroon","ca":"Canada",
    "ky":"Cayman Islands","cl":"Chile","cn":"China","co":"Colombia","cr":"Costa Rica",
    "hr":"Croatia","cu":"Cuba","cy":"Cyprus","dk":"Denmark","do":"Dominican Republic",
    "cd":"DR Congo","ec":"Ecuador","eg":"Egypt","sv":"El Salvador","ae":"United Arab Emirates",
    "ee":"Estonia","et":"Ethiopia","fj":"Fiji","fi":"Finland","fr":"France","de":"Germany",
    "gh":"Ghana","gt":"Guatemala","hn":"Honduras","hk":"Hong Kong","hu":"Hungary",
    "in":"India","id":"Indonesia","ir":"Iran","ie":"Ireland","il":"Israel","it":"Italy",
    "ci":"Ivory Coast","jm":"Jamaica","jp":"Japan","jo":"Jordan","kz":"Kazakhstan",
    "ke":"Kenya","kr":"South Korea","kw":"Kuwait","lv":"Latvia","lb":"Lebanon",
    "ls":"Lesotho","ly":"Libya","lt":"Lithuania","lu":"Luxembourg","mg":"Madagascar",
    "mw":"Malawi","my":"Malaysia","ml":"Mali","mt":"Malta","mu":"Mauritius","mx":"Mexico",
    "md":"Moldova","ma":"Morocco","mm":"Myanmar","na":"Namibia","np":"Nepal",
    "nl":"Netherlands","nz":"New Zealand","ni":"Nicaragua","ng":"Nigeria","no":"Norway",
    "om":"Oman","pk":"Pakistan","pa":"Panama","pg":"Papua New Guinea","py":"Paraguay",
    "pe":"Peru","ph":"Philippines","pl":"Poland","pt":"Portugal","pr":"Puerto Rico",
    "qa":"Qatar","ro":"Romania","ru":"Russia","rw":"Rwanda","sa":"Saudi Arabia",
    "sn":"Senegal","sg":"Singapore","sk":"Slovakia","si":"Slovenia","za":"South Africa",
    "es":"Spain","lk":"Sri Lanka","sr":"Suriname","se":"Sweden","ch":"Switzerland",
    "tw":"Taiwan","tz":"Tanzania","th":"Thailand","cz":"Czech Republic","is":"Iceland",
    "tt":"Trinidad and Tobago","tn":"Tunisia","tr":"Turkey","ug":"Uganda","ua":"Ukraine",
    "gb":"United Kingdom","us":"United States","uy":"Uruguay","uz":"Uzbekistan",
    "ve":"Venezuela","vn":"Vietnam","ye":"Yemen","zm":"Zambia","zw":"Zimbabwe","kg":"Kyrgyzstan",
}

COUNTRY_DISPLAY = {
    "al":"Albania","dz":"Algeria","ar":"Argentina","am":"Armenia","au":"Australia",
    "at":"Austria","az":"Azerbaijan","bs":"Bahamas","bh":"Bahrain","bd":"Bangladesh",
    "bb":"Barbados","by":"Belarus","be":"Belgium","bo":"Bolivia","bw":"Botswana",
    "br":"Brazil","bn":"Brunei","kh":"Cambodia","cm":"Cameroon","ca":"Canada",
    "ky":"Cayman Is.","cl":"Chile","cn":"China","co":"Colombia","cr":"Costa Rica",
    "hr":"Croatia","cu":"Cuba","cy":"Cyprus","dk":"Denmark","do":"Dominican Rep.",
    "cd":"DR Congo","ec":"Ecuador","eg":"Egypt","sv":"El Salvador","ae":"UAE",
    "ee":"Estonia","et":"Ethiopia","fj":"Fiji","fi":"Finland","fr":"France","de":"Germany",
    "gh":"Ghana","gt":"Guatemala","hn":"Honduras","hk":"Hong Kong","hu":"Hungary",
    "in":"India","id":"Indonesia","ir":"Iran","ie":"Ireland","il":"Israel","it":"Italy",
    "ci":"Ivory Coast","jm":"Jamaica","jp":"Japan","jo":"Jordan","kz":"Kazakhstan",
    "ke":"Kenya","kr":"S. Korea","kw":"Kuwait","lv":"Latvia","lb":"Lebanon","ls":"Lesotho",
    "ly":"Libya","lt":"Lithuania","lu":"Luxembourg","mg":"Madagascar","mw":"Malawi",
    "my":"Malaysia","ml":"Mali","mt":"Malta","mu":"Mauritius","mx":"Mexico","md":"Moldova",
    "ma":"Morocco","mm":"Myanmar","na":"Namibia","np":"Nepal","nl":"Netherlands",
    "nz":"New Zealand","ni":"Nicaragua","ng":"Nigeria","no":"Norway","om":"Oman",
    "pk":"Pakistan","pa":"Panama","pg":"Papua NG","py":"Paraguay","pe":"Peru",
    "ph":"Philippines","pl":"Poland","pt":"Portugal","pr":"Puerto Rico","qa":"Qatar",
    "ro":"Romania","ru":"Russia","rw":"Rwanda","sa":"Saudi Arabia","sn":"Senegal",
    "sg":"Singapore","sk":"Slovakia","si":"Slovenia","za":"South Africa","es":"Spain",
    "lk":"Sri Lanka","sr":"Suriname","se":"Sweden","ch":"Switzerland","tw":"Taiwan",
    "tz":"Tanzania","th":"Thailand","cz":"Czech Rep.","is":"Iceland","tt":"Trinidad",
    "tn":"Tunisia","tr":"Turkey","ug":"Uganda","ua":"Ukraine","gb":"UK","us":"USA",
    "uy":"Uruguay","uz":"Uzbekistan","ve":"Venezuela","vn":"Vietnam","ye":"Yemen",
    "zm":"Zambia","zw":"Zimbabwe","kg":"Kyrgyzstan",
}

COUNTRY_EMOJI = {
    "al":"🇦🇱","dz":"🇩🇿","ar":"🇦🇷","am":"🇦🇲","au":"🇦🇺","at":"🇦🇹","az":"🇦🇿",
    "bs":"🇧🇸","bh":"🇧🇭","bd":"🇧🇩","bb":"🇧🇧","by":"🇧🇾","be":"🇧🇪","bo":"🇧🇴",
    "bw":"🇧🇼","br":"🇧🇷","bn":"🇧🇳","kh":"🇰🇭","cm":"🇨🇲","ca":"🇨🇦","ky":"🇰🇾",
    "cl":"🇨🇱","cn":"🇨🇳","co":"🇨🇴","cr":"🇨🇷","hr":"🇭🇷","cu":"🇨🇺","cy":"🇨🇾",
    "dk":"🇩🇰","do":"🇩🇴","cd":"🇨🇩","ec":"🇪🇨","eg":"🇪🇬","sv":"🇸🇻","ae":"🇦🇪",
    "ee":"🇪🇪","et":"🇪🇹","fj":"🇫🇯","fi":"🇫🇮","fr":"🇫🇷","de":"🇩🇪","gh":"🇬🇭",
    "gt":"🇬🇹","hn":"🇭🇳","hk":"🇭🇰","hu":"🇭🇺","in":"🇮🇳","id":"🇮🇩","ir":"🇮🇷",
    "ie":"🇮🇪","il":"🇮🇱","it":"🇮🇹","ci":"🇨🇮","jm":"🇯🇲","jp":"🇯🇵","jo":"🇯🇴",
    "kz":"🇰🇿","ke":"🇰🇪","kr":"🇰🇷","kw":"🇰🇼","lv":"🇱🇻","lb":"🇱🇧","ls":"🇱🇸",
    "ly":"🇱🇾","lt":"🇱🇹","lu":"🇱🇺","mg":"🇲🇬","mw":"🇲🇼","my":"🇲🇾","ml":"🇲🇱",
    "mt":"🇲🇹","mu":"🇲🇺","mx":"🇲🇽","md":"🇲🇩","ma":"🇲🇦","mm":"🇲🇲","na":"🇳🇦",
    "np":"🇳🇵","nl":"🇳🇱","nz":"🇳🇿","ni":"🇳🇮","ng":"🇳🇬","no":"🇳🇴","om":"🇴🇲",
    "pk":"🇵🇰","pa":"🇵🇦","pg":"🇵🇬","py":"🇵🇾","pe":"🇵🇪","ph":"🇵🇭","pl":"🇵🇱",
    "pt":"🇵🇹","pr":"🇵🇷","qa":"🇶🇦","ro":"🇷🇴","ru":"🇷🇺","rw":"🇷🇼","sa":"🇸🇦",
    "sn":"🇸🇳","sg":"🇸🇬","sk":"🇸🇰","si":"🇸🇮","za":"🇿🇦","es":"🇪🇸","lk":"🇱🇰",
    "sr":"🇸🇷","se":"🇸🇪","ch":"🇨🇭","tw":"🇹🇼","tz":"🇹🇿","th":"🇹🇭","cz":"🇨🇿",
    "is":"🇮🇸","tt":"🇹🇹","tn":"🇹🇳","tr":"🇹🇷","ug":"🇺🇬","ua":"🇺🇦","gb":"🇬🇧",
    "us":"🇺🇸","uy":"🇺🇾","uz":"🇺🇿","ve":"🇻🇪","vn":"🇻🇳","ye":"🇾🇪","zm":"🇿🇲",
    "zw":"🇿🇼","kg":"🇰🇬",
}

_FAKE_SORTED    = sorted(COUNTRY_ALIASES.items(), key=lambda x: x[1])
_FAKE_PAGE_SIZE = 42
_FAKE_PAGES     = [_FAKE_SORTED[i:i+_FAKE_PAGE_SIZE] for i in range(0, len(_FAKE_SORTED), _FAKE_PAGE_SIZE)]

# ── Health Check Server ───────────────────────────────────────────────────────
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.send_header("Content-Type","text/plain"); self.end_headers()
        self.wfile.write(b"Bot is running.")
    def do_HEAD(self):
        self.send_response(200); self.send_header("Content-Type","text/plain"); self.end_headers()
    def log_message(self, format, *args): pass

def run_health_server():
    HTTPServer(("0.0.0.0", PORT), HealthHandler).serve_forever()
# ─────────────────────────────────────────────────────────────────────────────

def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(CHANNEL_NAME, url=CHANNEL_URL)],
        [InlineKeyboardButton(OWNER_NAME,   url=OWNER_URL)],
    ])

def e(t: str) -> str:
    for c in r"\_*[]()~`>#+-=|{}.!":
        t = t.replace(c, "\\" + c)
    return t

# ── BIN formatter ─────────────────────────────────────────────────────────────
def fmt_bin(bin_number: str, data: dict) -> str:
    brand=str(data.get("brand","N/A")); bank=str(data.get("bank","N/A"))
    typ=str(data.get("type","N/A")); level=str(data.get("level","N/A"))
    country=str(data.get("country","N/A")); emoji=str(data.get("emoji",""))
    no_vbv=str(data.get("no_vbv","TRUE")); novbv_icon="✅" if no_vbv=="TRUE" else "❌"
    return (
        "💳 *BIN RESULT*\n\n"
        "📌 *BIN:* `"+bin_number+"`\n"
        "🏦 *Bank:* "+e(bank)+"\n"
        "📳 *Brand:* "+e(brand)+"\n"
        "💴 *Type:* "+e(typ)+"\n"
        "⭐ *Level:* "+e(level)+"\n"
        "🌍 *Country:* "+emoji+" "+e(country)+"\n"
        "🔐 *NO VBV:* "+novbv_icon+" *"+e(no_vbv)+"*"
    )

ALPHA3 = {
    "US":"USA","GB":"GBR","AU":"AUS","CA":"CAN","DE":"DEU","FR":"FRA","IN":"IND",
    "BR":"BRA","MX":"MEX","JP":"JPN","CN":"CHN","RU":"RUS","SG":"SGP","NL":"NLD",
    "ES":"ESP","IT":"ITA","SE":"SWE","NO":"NOR","FI":"FIN","BE":"BEL","AT":"AUT",
    "CH":"CHE","NZ":"NZL","ZA":"ZAF","PT":"PRT","PL":"POL","TW":"TWN","TT":"TTO",
    "DO":"DOM","AR":"ARG","VE":"VEN","IL":"ISR","KZ":"KAZ","BN":"BRN","JO":"JOR",
    "AE":"ARE","PE":"PER","NG":"NGA","TR":"TUR","MY":"MYS","EG":"EGY","HN":"HND",
    "CR":"CRI","CO":"COL","EC":"ECU","GT":"GTM","CL":"CHL","TN":"TUN","MT":"MLT",
    "PA":"PAN","HK":"HKG","SA":"SAU","IE":"IRL","DK":"DNK",
}

async def fetch_bin(bin_number: str) -> dict | None:
    try:
        resp = requests.get("https://binlist.io/lookup/"+bin_number+"/",
                            headers={"Accept":"application/json"}, timeout=8)
        if resp.status_code == 200:
            d=resp.json(); bank=d.get("bank",{}); country=d.get("country",{})
            alpha2=country.get("alpha2","N/A").upper() if isinstance(country,dict) else "N/A"
            return {
                "brand":   str(d.get("scheme",d.get("brand","N/A"))).upper(),
                "bank":    str(bank.get("name","N/A") if isinstance(bank,dict) else bank).upper(),
                "type":    str(d.get("type","N/A")).upper(),
                "level":   str(d.get("brand",d.get("tier","N/A"))).upper(),
                "country": str(country.get("name","N/A") if isinstance(country,dict) else country).upper(),
                "alpha2":  alpha2, "alpha3": ALPHA3.get(alpha2,alpha2),
                "numeric": str(country.get("numeric","N/A") if isinstance(country,dict) else "N/A"),
                "emoji":   str(country.get("emoji","") if isinstance(country,dict) else ""),
                "no_vbv":  "TRUE" if not d.get("prepaid",False) else "FALSE",
            }
    except Exception as ex: print("[BIN] error:",ex)
    return None

# ═══════════════════════════════════════════════════════════════════════════════
# ── BROADCAST HELPERS ────────────────────────────────────────────────────────

def build_keyboard(buttons: list):
    """buttons = [{"text": ..., "url": ...}, ...]  — supports any number"""
    rows = [[InlineKeyboardButton(b["text"], url=b["url"])] for b in buttons if b.get("text") and b.get("url")]
    return InlineKeyboardMarkup(rows) if rows else None

def extract_content(message) -> dict | None:
    if message.text and not message.document:
        return {"type": "text", "text": message.text}
    elif message.photo:
        return {"type":"photo",     "file_id":message.photo[-1].file_id, "caption":message.caption or ""}
    elif message.video:
        return {"type":"video",     "file_id":message.video.file_id,     "caption":message.caption or ""}
    elif message.document:
        return {"type":"document",  "file_id":message.document.file_id,  "caption":message.caption or ""}
    elif message.audio:
        return {"type":"audio",     "file_id":message.audio.file_id,     "caption":message.caption or ""}
    elif message.sticker:
        return {"type":"sticker",   "file_id":message.sticker.file_id}
    elif message.animation:
        return {"type":"animation", "file_id":message.animation.file_id, "caption":message.caption or ""}
    elif message.voice:
        return {"type":"voice",     "file_id":message.voice.file_id,     "caption":message.caption or ""}
    elif message.video_note:
        return {"type":"video_note","file_id":message.video_note.file_id}
    return None

async def send_content(bot, chat_id: int, content: dict, keyboard=None) -> bool:
    try:
        k   = content["type"]
        cap = content.get("caption","")
        fid = content.get("file_id")
        if   k == "text":       await bot.send_message(   chat_id=chat_id, text=content["text"], parse_mode="Markdown", reply_markup=keyboard)
        elif k == "photo":      await bot.send_photo(     chat_id=chat_id, photo=fid,      caption=cap, parse_mode="Markdown", reply_markup=keyboard)
        elif k == "video":      await bot.send_video(     chat_id=chat_id, video=fid,      caption=cap, parse_mode="Markdown", reply_markup=keyboard)
        elif k == "document":   await bot.send_document(  chat_id=chat_id, document=fid,   caption=cap, parse_mode="Markdown", reply_markup=keyboard)
        elif k == "audio":      await bot.send_audio(     chat_id=chat_id, audio=fid,      caption=cap, parse_mode="Markdown", reply_markup=keyboard)
        elif k == "sticker":    await bot.send_sticker(   chat_id=chat_id, sticker=fid)
        elif k == "animation":  await bot.send_animation( chat_id=chat_id, animation=fid,  caption=cap, parse_mode="Markdown", reply_markup=keyboard)
        elif k == "voice":      await bot.send_voice(     chat_id=chat_id, voice=fid,      caption=cap, parse_mode="Markdown", reply_markup=keyboard)
        elif k == "video_note": await bot.send_video_note(chat_id=chat_id, video_note=fid)
        return True
    except Exception:
        return False

# ═══════════════════════════════════════════════════════════════════════════════
# ── DOT-COMMAND DISPATCHER ────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

async def dot_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles .admin .stats .users .regusers .broadcast"""
    if not update.message or not update.message.text:
        return
    if not is_admin(update.effective_user.id):
        return

    cmd = update.message.text.strip().lower()
    try:
        await update.message.delete()
    except Exception:
        pass

    chat_id = update.effective_chat.id

    # ── .admin ────────────────────────────────────────────────────────────────
    if cmd == ".admin":
        msg = (
            "🔐 *ADMIN PANEL*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📊 *Statistics*\n"
            "`.stats` — Total vs registered users\n\n"
            "👥 *User Management*\n"
            "`.users` — List all users \\(latest 50\\)\n"
            "`.regusers` — Registered users only\n\n"
            "📢 *Broadcasting*\n"
            "`.broadcast` — Interactive broadcast wizard\n"
            "Supports: text, photo, video, APK, audio,\n"
            "sticker, GIF, voice \\+ *unlimited URL buttons*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 *Your ID:* `{update.effective_user.id}`\n"
            "👑 *Role:* Admin"
        )
        await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="MarkdownV2")

    # ── .stats ────────────────────────────────────────────────────────────────
    elif cmd == ".stats":
        stats = get_stats()
        msg = (
            "📊 *Bot Statistics*\n\n"
            f"👥 *Total Users:* `{stats['total']}`\n"
            f"✅ *Registered:* `{stats['registered']}`\n"
            f"🔓 *Unregistered:* `{stats['total'] - stats['registered']}`"
        )
        await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="MarkdownV2")

    # ── .users ────────────────────────────────────────────────────────────────
    elif cmd == ".users":
        rows = get_all_users()
        if not rows:
            await context.bot.send_message(chat_id=chat_id, text="No users yet\\.", parse_mode="MarkdownV2")
            return
        lines = ["👥 *All Users \\(latest 50\\):*\n"]
        for u in rows[-50:]:
            uid    = u.get("user_id","?")
            uname  = u.get("username")
            fname  = u.get("first_name")
            status = "✅" if u.get("registered", False) else "🔓"
            name   = f"@{uname}" if uname else (fname or "Unknown")
            lines.append(f"{status} `{uid}` — {e(str(name))}")
        await context.bot.send_message(chat_id=chat_id, text="\n".join(lines), parse_mode="MarkdownV2")

    # ── .regusers ─────────────────────────────────────────────────────────────
    elif cmd == ".regusers":
        rows = get_all_users(registered_only=True)
        if not rows:
            await context.bot.send_message(chat_id=chat_id, text="No registered users yet\\.", parse_mode="MarkdownV2")
            return
        lines = ["✅ *Registered Users \\(latest 50\\):*\n"]
        for u in rows[-50:]:
            uid    = u.get("user_id","?")
            uname  = u.get("username")
            fname  = u.get("first_name")
            reg_at = u.get("registered_at","")
            name   = f"@{uname}" if uname else (fname or "Unknown")
            date   = str(reg_at)[:10] if reg_at else "N/A"
            lines.append(f"`{uid}` — {e(str(name))} \\| {e(date)}")
        await context.bot.send_message(chat_id=chat_id, text="\n".join(lines), parse_mode="MarkdownV2")

    # ── .broadcast → start wizard ─────────────────────────────────────────────
    elif cmd == ".broadcast":
        context.user_data.clear()
        context.user_data["bc_active"] = True
        context.user_data["bc_step"]   = "wait_content"
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "📤 *Step 1 — Content*\n\n"
                "Forward or send anything you want to broadcast\\.\n"
                "Supports: *text, photo, video, APK, audio, sticker, GIF, voice*\n\n"
                "Send your content now 👇\n\n"
                "_Type_ `.cancel` _to abort at any time\\._"
            ),
            parse_mode="MarkdownV2"
        )

# ═══════════════════════════════════════════════════════════════════════════════
# ── BROADCAST WIZARD FLOW ─────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

async def broadcast_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """State-machine handler for all broadcast wizard steps."""
    if not update.message:
        return
    if not is_admin(update.effective_user.id):
        return
    if not context.user_data.get("bc_active"):
        return

    step    = context.user_data.get("bc_step", "")
    chat_id = update.effective_chat.id

    # ── .cancel anytime ───────────────────────────────────────────────────────
    if update.message.text and update.message.text.strip().lower() == ".cancel":
        context.user_data.clear()
        try: await update.message.delete()
        except: pass
        await context.bot.send_message(chat_id=chat_id, text="❌ *Broadcast cancelled\\.*", parse_mode="MarkdownV2")
        return

    # ── Step 1: receive content ───────────────────────────────────────────────
    if step == "wait_content":
        content = extract_content(update.message)
        if not content:
            await update.message.reply_text("⚠️ Unsupported format\\. Try again:", parse_mode="MarkdownV2")
            return
        context.user_data["bc_content"] = content
        context.user_data["bc_step"]    = "wait_btn_count"
        await update.message.reply_text(
            f"✅ *Content received\\!* \\(type: `{content['type']}`\\)\n\n"
            "📎 *Step 2 — How many URL buttons?*\n\n"
            "Send a number \\(0 for no buttons, max 10\\):",
            parse_mode="MarkdownV2",
            reply_markup=ForceReply(selective=True)
        )

    # ── Step 2: receive button count ─────────────────────────────────────────
    elif step == "wait_btn_count":
        txt = update.message.text.strip() if update.message.text else ""
        if not txt.isdigit():
            await update.message.reply_text("⚠️ Please send a valid number like `0`, `1`, `3` etc:", parse_mode="MarkdownV2")
            return
        count = int(txt)
        if count < 0 or count > 10:
            await update.message.reply_text("⚠️ Please send a number between `0` and `10`:", parse_mode="MarkdownV2")
            return
        context.user_data["bc_btn_total"]   = count
        context.user_data["bc_btn_current"] = 0
        context.user_data["bc_buttons"]     = []

        if count == 0:
            await _bc_show_confirm(update, context)
        else:
            context.user_data["bc_step"] = "wait_btn_text"
            await update.message.reply_text(
                f"🔘 *Button 1 of {count} — Label*\n\nSend the button text:",
                parse_mode="MarkdownV2",
                reply_markup=ForceReply(selective=True)
            )

    # ── Step 3: receive button label ─────────────────────────────────────────
    elif step == "wait_btn_text":
        txt = update.message.text.strip() if update.message.text else ""
        if not txt:
            await update.message.reply_text("⚠️ Button label can\'t be empty\\. Send the label text:", parse_mode="MarkdownV2")
            return
        context.user_data["bc_current_btn_text"] = txt
        context.user_data["bc_step"] = "wait_btn_url"
        current = context.user_data["bc_btn_current"] + 1
        total   = context.user_data["bc_btn_total"]
        await update.message.reply_text(
            f"🔗 *Button {current} of {total} — URL*\n\nSend the button URL:",
            parse_mode="MarkdownV2",
            reply_markup=ForceReply(selective=True)
        )

    # ── Step 4: receive button URL ────────────────────────────────────────────
    elif step == "wait_btn_url":
        url = update.message.text.strip() if update.message.text else ""

        # Validate: must start with http and have something after the scheme
        if not re.match(r"^https?://[^\s/$.?#].[^\s]*$", url):
            await update.message.reply_text(
                "\u26a0\ufe0f Invalid URL\\. Must start with https:// Try again:",
                parse_mode="MarkdownV2"
            )
            return

        # Save completed button
        context.user_data["bc_buttons"].append({
            "text": context.user_data.pop("bc_current_btn_text"),
            "url":  url
        })
        context.user_data["bc_btn_current"] += 1

        current = context.user_data["bc_btn_current"]
        total   = context.user_data["bc_btn_total"]

        if current < total:
            context.user_data["bc_step"] = "wait_btn_text"
            await update.message.reply_text(
                f"🔘 *Button {current + 1} of {total} — Label*\n\nSend the button text:",
                parse_mode="MarkdownV2",
                reply_markup=ForceReply(selective=True)
            )
        else:
            await _bc_show_confirm(update, context)

async def _bc_show_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show content preview + confirm/cancel buttons."""
    content  = context.user_data["bc_content"]
    buttons  = context.user_data.get("bc_buttons", [])
    keyboard = build_keyboard(buttons)
    user_ids = get_all_user_ids()
    context.user_data["bc_user_ids"] = user_ids
    context.user_data["bc_step"]     = "wait_confirm"

    await update.message.reply_text(
        f"👁 *Step 3 — Preview \\& Confirm*\n\n"
        f"📦 Content type: `{content['type']}`\n"
        f"🔘 Buttons: `{len(buttons)}`\n"
        f"👥 Will send to: `{len(user_ids)}` users\n\n"
        f"Here's the preview 👇",
        parse_mode="MarkdownV2"
    )
    # Live preview to admin
    await send_content(context.bot, update.effective_chat.id, content, keyboard)

    await update.message.reply_text(
        "Confirm broadcast to all users?",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Yes, Send Now", callback_data="bc_confirm:yes"),
                InlineKeyboardButton("❌ Cancel",        callback_data="bc_confirm:no"),
            ]
        ])
    )

async def broadcast_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles confirm/cancel inline button."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        return

    if query.data == "bc_confirm:no":
        await query.edit_message_text("❌ *Broadcast cancelled\\.*", parse_mode="MarkdownV2")
        context.user_data.clear()
        return

    if query.data == "bc_confirm:yes":
        await query.edit_message_text("🚀 *Broadcasting\\.\\.\\.*", parse_mode="MarkdownV2")

        content  = context.user_data.get("bc_content", {})
        buttons  = context.user_data.get("bc_buttons", [])
        keyboard = build_keyboard(buttons)
        user_ids = context.user_data.get("bc_user_ids", get_all_user_ids())
        total    = len(user_ids)
        sent     = 0
        failed   = 0

        progress = await query.message.reply_text(f"📤 Sending: 0 / {total}")

        for i, uid in enumerate(user_ids, 1):
            ok = await send_content(context.bot, uid, content, keyboard)
            if ok: sent += 1
            else:  failed += 1
            if i % 10 == 0 or i == total:
                try: await progress.edit_text(f"📤 Sending: {i} / {total}")
                except: pass
            await asyncio.sleep(0.05)

        await progress.edit_text(
            f"✅ *Broadcast Complete*\n\n"
            f"📨 Sent:   `{sent}`\n"
            f"❌ Failed: `{failed}`\n"
            f"👥 Total:  `{total}`",
            parse_mode="MarkdownV2"
        )
        context.user_data.clear()


# ── USER COMMANDS ─────────────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    store_user(user_id=user.id, username=user.username, first_name=user.first_name, last_name=user.last_name)
    register_user(user.id)
    first = user.first_name if user.first_name else "there"
    msg = (
        f"👋 Welcome, *{e(first)}*\\!\n\n"
        "🤖 I'm all\\-in\\-one carding bot\\.\n"
        "Fast\\. Smart\\. Reliable\\.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ *Quick Commands*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "💳 /gen — Generate CC numbers\n"
        "🔍 /chkbin — Lookup a BIN\n"
        "🎲 /genbin — Random BIN info\n"
        "🪪 /fake — Fake identity\n"
        "❓ /help — Full command list\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )
    await update.message.reply_text(msg, parse_mode="MarkdownV2", reply_markup=main_keyboard())

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "📖 *HELP \\& COMMANDS*\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "💳 *CC GENERATOR*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "`/gen BIN` — Random exp \\+ cvv\n"
        "`/gen BIN EXP` — Fixed exp\n"
        "`/gen BIN EXP CVV` — Fixed all\n"
        "`/gen BIN\\|EXP\\|CVV` — Pipe format\n\n"
        "📌 *Examples:*\n"
        "`/gen 498416`\n"
        "`/gen 498416 05/28`\n"
        "`/gen 498416 05/28 999`\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔍 *BIN LOOKUP*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "`/chkbin 440769` — Lookup BIN info\n"
        "`/genbin` — Random BIN from database\n"
        "`/genbin us` — Random US BIN\n"
        "`/genbin gb` — Random UK BIN\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🪪 *FAKE IDENTITY*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "`/fake` — Random country identity\n"
        "`/fake us` — USA identity\n"
        "`/fake gb` — UK identity\n"
        "`/fake in` — India identity\n\n"
        "🌍 *128 countries supported*\n"
        "Just `/fake` to open the country picker menu"
    )
    await update.message.reply_text(msg, parse_mode="MarkdownV2", reply_markup=main_keyboard())

async def bin_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usage = "❌ Invalid usage\\!\n\n✅ Usage: `/chkbin 440769`\n📌 Example: `/chkbin 521234`"
    if not context.args:
        await update.message.reply_text(usage, parse_mode="MarkdownV2", reply_markup=main_keyboard()); return
    bin_number = context.args[0].strip()[:6]
    if not bin_number.isdigit() or len(bin_number) < 6:
        await update.message.reply_text(usage, parse_mode="MarkdownV2", reply_markup=main_keyboard()); return
    if bin_number in BIN_DB:
        await update.message.reply_text(fmt_bin(bin_number, BIN_DB[bin_number]), parse_mode="MarkdownV2", reply_markup=main_keyboard()); return
    loading = await update.message.reply_text("🔍 Looking up BIN...")
    async def do_animate(msg):
        for frame in ["🔍 Looking up BIN ⬜⬜⬜","🔍 Looking up BIN 🟦⬜⬜","🔍 Looking up BIN 🟦🟦⬜","🔍 Looking up BIN 🟦🟦🟦","🔍 Looking up BIN ⬜⬜⬜"]:
            try: await msg.edit_text(frame); await asyncio.sleep(0.7)
            except: pass
    anim = asyncio.create_task(do_animate(loading))
    data = await fetch_bin(bin_number)
    anim.cancel()
    try: await anim
    except asyncio.CancelledError: pass
    try: await loading.delete()
    except: pass
    if not data:
        await update.message.reply_text("⚠️ BIN not found\\. Please check the number and try again\\.", parse_mode="MarkdownV2", reply_markup=main_keyboard()); return
    await update.message.reply_text(fmt_bin(bin_number, data), parse_mode="MarkdownV2", reply_markup=main_keyboard())

async def genbin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    arg = context.args[0].lower() if context.args else ""
    if arg:
        alpha2 = arg.upper()
        if len(arg) != 2:
            alpha2 = next((v["alpha2"] for v in BIN_DB.values() if v.get("country","").lower()==arg), None)
        if not alpha2:
            await update.message.reply_text("⚠️ Unknown country code\\. Use ISO 2\\-letter code like `us`, `gb`, `au`", parse_mode="MarkdownV2", reply_markup=main_keyboard()); return
        pool = {k:v for k,v in BIN_DB.items() if v.get("alpha2","").upper()==alpha2}
        if not pool:
            await update.message.reply_text("⚠️ No BINs found for that country in the database\\.", parse_mode="MarkdownV2", reply_markup=main_keyboard()); return
    else:
        pool = BIN_DB
    bin_number = random.choice(list(pool.keys()))
    await update.message.reply_text(fmt_bin(bin_number, pool[bin_number]), parse_mode="MarkdownV2", reply_markup=main_keyboard())

def fake_country_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    items=_FAKE_PAGES[page]; rows=[]; row=[]
    for i,(code,_) in enumerate(items):
        flag=COUNTRY_EMOJI.get(code,"🌐"); display=COUNTRY_DISPLAY.get(code,code.upper())
        row.append(InlineKeyboardButton(f"{flag} {display}", callback_data=f"fake:{code}"))
        if len(row)==3: rows.append(row); row=[]
    if row: rows.append(row)
    nav=[]
    if page>0: nav.append(InlineKeyboardButton("◀ Prev", callback_data=f"fake_page:{page-1}"))
    nav.append(InlineKeyboardButton(f"📄 {page+1}/{len(_FAKE_PAGES)}", callback_data="fake_noop"))
    if page<len(_FAKE_PAGES)-1: nav.append(InlineKeyboardButton("Next ▶", callback_data=f"fake_page:{page+1}"))
    rows.append(nav)
    rows.append([InlineKeyboardButton("🎲 Random Country", callback_data="fake:random")])
    return InlineKeyboardMarkup(rows)

def build_fake_identity(country_key: str) -> str:
    addresses=COUNTRY_DATA.get(country_key,[])
    if not addresses: return None
    addr=random.choice(addresses); country_names=NAMES_DATA.get(country_key,{})
    first_pool=country_names.get("first") or [n for v in NAMES_DATA.values() for n in v.get("first",[])]
    last_pool=country_names.get("last")  or [n for v in NAMES_DATA.values() for n in v.get("last",[])]
    first=random.choice(first_pool); last=random.choice(last_pool)
    code=next((k for k,v in COUNTRY_ALIASES.items() if v==country_key),"")
    flag=COUNTRY_EMOJI.get(code,"🌐")
    address1=addr.get("address1","N/A"); address2=addr.get("address2","")
    city=addr.get("city","N/A"); state=addr.get("state","N/A")
    postcode=addr.get("postcode","N/A"); phone=addr.get("phone","N/A")
    msg=(f"{flag} *Fake Identity* — {country_key}\n\n▸ *Name:* `{first} {last}`\n▸ *Phone:* `{phone}`\n▸ *Address 1:* `{address1}`\n")
    if address2: msg+=f"▸ *Address 2:* `{address2}`\n"
    msg+=(f"▸ *City:* `{city}`\n▸ *State:* `{state}`\n▸ *Postcode:* `{postcode}`\n▸ *Country:* `{country_key}`")
    return msg

async def fake(update: Update, context: ContextTypes.DEFAULT_TYPE):
    arg = context.args[0].lower() if context.args else ""
    if arg:
        country_key=COUNTRY_ALIASES.get(arg)
        if not country_key:
            for k in COUNTRY_DATA:
                if k.lower()==arg: country_key=k; break
        if not country_key or country_key not in COUNTRY_DATA:
            await update.message.reply_text("⚠️ Unknown country code\\. Use `/fake` to open the country picker\\.", parse_mode="MarkdownV2", reply_markup=main_keyboard()); return
        await update.message.reply_text(build_fake_identity(country_key), parse_mode="Markdown", reply_markup=main_keyboard())
    else:
        await update.message.reply_text("🌍 *Select a country* to generate a fake identity:", parse_mode="MarkdownV2", reply_markup=fake_country_keyboard(0))

async def fake_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query=update.callback_query; await query.answer(); data=query.data
    if data=="fake_noop": return
    if data.startswith("fake_page:"):
        page=int(data.split(":")[1])
        try: await query.edit_message_text("🌍 *Select a country* to generate a fake identity:", parse_mode="MarkdownV2", reply_markup=fake_country_keyboard(page))
        except: pass
        return
    if data.startswith("fake:"):
        code=data.split(":")[1]
        if code=="random":
            country_key=random.choice(list(COUNTRY_DATA.keys()))
            back_code=next((k for k,v in COUNTRY_ALIASES.items() if v==country_key),"")
        else:
            country_key=COUNTRY_ALIASES.get(code); back_code=code
        if not country_key or country_key not in COUNTRY_DATA:
            await query.answer("Country not found.", show_alert=True); return
        msg=build_fake_identity(country_key)
        result_kb=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Regenerate", callback_data=f"fake:{back_code}"),
             InlineKeyboardButton("🌍 Pick Country", callback_data="fake_page:0")],
            [InlineKeyboardButton("🎲 Random", callback_data="fake:random")],
        ])
        try: await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=result_kb)
        except: await context.bot.send_message(chat_id=query.message.chat_id, text=msg, parse_mode="Markdown", reply_markup=result_kb)

def luhn_complete(prefix: str) -> str:
    digits=[int(d) for d in str(prefix)]; digits.append(0); total=0
    for i,d in enumerate(reversed(digits)):
        if i%2==1: d*=2;
        if d>9: d-=9
        total+=d
    return str(prefix)+str((10-(total%10))%10)

async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    USAGE=("❌ *No BIN provided\\!*\n\nℹ️ *Usage:*\n`/gen BIN`\n`/gen BIN EXP`\n`/gen BIN EXP CVV`\n`/gen BIN\\|EXP\\|CVV`\n\n📌 *Examples:*\n`/gen 498416`\n`/gen 49841612345`\n`/gen 498416 05/28`\n`/gen 498416 05/28 999`\n`/gen 498416\\|05\\|2028\\|999`")
    if not context.args:
        await update.message.reply_text(USAGE, parse_mode="MarkdownV2", reply_markup=main_keyboard()); return
    raw=" ".join(context.args).strip()
    parts=[p.strip() for p in raw.split("|")] if "|" in raw else raw.split()
    bin_number=parts[0] if parts else ""
    if not bin_number.isdigit() or len(bin_number)<6 or len(bin_number)>15:
        await update.message.reply_text(USAGE, parse_mode="MarkdownV2", reply_markup=main_keyboard()); return
    fixed_exp=None
    if len(parts)>=2:
        exp_raw=parts[1].strip().replace("/","")
        if len(exp_raw)==4 and exp_raw.isdigit(): fixed_exp=(exp_raw[:2],"20"+exp_raw[2:])
        elif len(exp_raw)==6 and exp_raw.isdigit(): fixed_exp=(exp_raw[:2],exp_raw[2:])
        elif len(exp_raw)==2 and exp_raw.isdigit(): fixed_exp=(str(random.randint(1,12)).zfill(2),"20"+exp_raw)
    fixed_cvv=None
    if len(parts)>=3:
        cvv_raw=parts[2].strip()
        if cvv_raw.isdigit() and 2<=len(cvv_raw)<=4: fixed_cvv=cvv_raw
    bin_info=BIN_DB.get(bin_number[:6]); cards=[]
    for _ in range(10):
        pad=15-len(bin_number); middle="".join([str(random.randint(0,9)) for _ in range(pad)])
        cc_num=luhn_complete(bin_number+middle)
        mm,yyyy=(fixed_exp if fixed_exp else (str(random.randint(1,12)).zfill(2),str(random.randint(2026,2030))))
        cvv=fixed_cvv if fixed_cvv else str(random.randint(100,999))
        cards.append(cc_num+"|"+mm+"|"+yyyy+"|"+cvv)
    exp_label=(fixed_exp[0]+"/"+fixed_exp[1]) if fixed_exp else "RAND"
    cvv_label=fixed_cvv if fixed_cvv else "RAND"
    header=("💳 *Generated CC*\n🔹 BIN: `"+bin_number+"` \\| EXP: `"+exp_label+"` \\| CVV: `"+cvv_label+"`\n")
    if bin_info:
        vbv_icon="✅" if bin_info.get("no_vbv","TRUE")=="TRUE" else "❌"
        header+=("🏦 *Bank:* "+e(str(bin_info.get("bank","N/A")))+"\n📳 *Brand:* "+e(str(bin_info.get("brand","N/A")))+"\n🌍 *Country:* "+str(bin_info.get("emoji",""))+" "+e(str(bin_info.get("country","N/A")))+"\n🔐 *NO VBV:* "+vbv_icon+"\n")
    body="\n".join("`"+cc+"`" for cc in cards)
    await update.message.reply_text(header+"\n"+body, parse_mode="MarkdownV2", reply_markup=main_keyboard())

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    get_db()
    threading.Thread(target=run_health_server, daemon=True).start()
    print(f"[✓] Health server running on port {PORT}")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # User commands
    app.add_handler(CommandHandler("start",  start))
    app.add_handler(CommandHandler("help",   help_cmd))
    app.add_handler(CommandHandler("chkbin", bin_lookup))
    app.add_handler(CommandHandler("genbin", genbin))
    app.add_handler(CommandHandler("fake",   fake))
    app.add_handler(CommandHandler("gen",    gen))

    # Fake country picker callbacks
    app.add_handler(CallbackQueryHandler(fake_callback, pattern="^fake"))

    # Broadcast inline button callbacks
    app.add_handler(CallbackQueryHandler(broadcast_callback, pattern="^bc_confirm:"))

    # Dot-command dispatcher (.admin .stats .users .regusers .broadcast)
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r"^\.(admin|stats|users|regusers|broadcast)$"),
        dot_command_handler
    ))

    # Broadcast flow — handles content + button text/url steps
    app.add_handler(MessageHandler(
        filters.ALL & ~filters.COMMAND,
        broadcast_flow
    ))

    print("[✓] Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()