import os
import json
import random
import asyncio
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8080))

# ── CONFIG ────────────────────────────────────────────────────────────────────
CHANNEL_URL  = "https://t.me/danger_boy_op1"
OWNER_URL    = "https://t.me/danger_boy_op"
CHANNEL_NAME = "𒆜ﮩ٨ـﮩ٨ـ𝐉𝐎𝐈𝐍 𝐂𝐇𝐀𝐍𝐍𝐄𝐋ﮩ٨ـﮩ٨ـ𒆜"
OWNER_NAME   = "𒆜ﮩ٨ـﮩ٨ـ𝐂𝐎𝐍𝐓𝐄𝐂𝐓 𝐎𝐖𝐍𝐄𝐑ﮩ٨ـﮩ٨ـ𒆜"
# ─────────────────────────────────────────────────────────────────────────────

# ── Load JSON databases ───────────────────────────────────────────────────────
_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database")

with open(os.path.join(_DIR, "bins.json"), "r", encoding="utf-8") as _f:
    BIN_DB: dict = json.load(_f)

with open(os.path.join(_DIR, "country.json"), "r", encoding="utf-8") as _f:
    COUNTRY_DATA: dict = json.load(_f)

with open(os.path.join(_DIR, "names.json"), "r", encoding="utf-8") as _f:
    NAMES_DATA: dict = json.load(_f)
# ─────────────────────────────────────────────────────────────────────────────

# ── ISO code → country key in country.json ────────────────────────────────────
COUNTRY_ALIASES = {
    "al":"Albania",       "dz":"Algeria",        "ar":"Argentina",
    "am":"Armenia",       "au":"Australia",       "at":"Austria",
    "az":"Azerbaijan",    "bs":"Bahamas",         "bh":"Bahrain",
    "bd":"Bangladesh",    "bb":"Barbados",        "by":"Belarus",
    "be":"Belgium",       "bo":"Bolivia",         "bw":"Botswana",
    "br":"Brazil",        "bn":"Brunei",          "kh":"Cambodia",
    "cm":"Cameroon",      "ca":"Canada",          "ky":"Cayman Islands",
    "cl":"Chile",         "cn":"China",           "co":"Colombia",
    "cr":"Costa Rica",    "hr":"Croatia",         "cu":"Cuba",
    "cy":"Cyprus",        "dk":"Denmark",         "do":"Dominican Republic",
    "cd":"DR Congo",      "ec":"Ecuador",         "eg":"Egypt",
    "sv":"El Salvador",   "ae":"United Arab Emirates","ee":"Estonia",
    "et":"Ethiopia",      "fj":"Fiji",            "fi":"Finland",
    "fr":"France",        "de":"Germany",         "gh":"Ghana",
    "gt":"Guatemala",     "hn":"Honduras",        "hk":"Hong Kong",
    "hu":"Hungary",       "in":"India",           "id":"Indonesia",
    "ir":"Iran",          "ie":"Ireland",         "il":"Israel",
    "it":"Italy",         "ci":"Ivory Coast",     "jm":"Jamaica",
    "jp":"Japan",         "jo":"Jordan",          "kz":"Kazakhstan",
    "ke":"Kenya",         "kr":"South Korea",     "kw":"Kuwait",
    "lv":"Latvia",        "lb":"Lebanon",         "ls":"Lesotho",
    "ly":"Libya",         "lt":"Lithuania",       "lu":"Luxembourg",
    "mg":"Madagascar",    "mw":"Malawi",          "my":"Malaysia",
    "ml":"Mali",          "mt":"Malta",           "mu":"Mauritius",
    "mx":"Mexico",        "md":"Moldova",         "ma":"Morocco",
    "mm":"Myanmar",       "na":"Namibia",         "np":"Nepal",
    "nl":"Netherlands",   "nz":"New Zealand",     "ni":"Nicaragua",
    "ng":"Nigeria",       "no":"Norway",          "om":"Oman",
    "pk":"Pakistan",      "pa":"Panama",          "pg":"Papua New Guinea",
    "py":"Paraguay",      "pe":"Peru",            "ph":"Philippines",
    "pl":"Poland",        "pt":"Portugal",        "pr":"Puerto Rico",
    "qa":"Qatar",         "ro":"Romania",         "ru":"Russia",
    "rw":"Rwanda",        "sa":"Saudi Arabia",    "sn":"Senegal",
    "sg":"Singapore",     "sk":"Slovakia",        "si":"Slovenia",
    "za":"South Africa",  "es":"Spain",           "lk":"Sri Lanka",
    "sr":"Suriname",      "se":"Sweden",          "ch":"Switzerland",
    "tw":"Taiwan",        "tz":"Tanzania",        "th":"Thailand",
    "cz":"Czech Republic","is":"Iceland",         "tt":"Trinidad and Tobago",
    "tn":"Tunisia",       "tr":"Turkey",          "ug":"Uganda",
    "ua":"Ukraine",       "gb":"United Kingdom",  "us":"United States",
    "uy":"Uruguay",       "uz":"Uzbekistan",      "ve":"Venezuela",
    "vn":"Vietnam",       "ye":"Yemen",           "zm":"Zambia",
    "zw":"Zimbabwe",      "kg":"Kyrgyzstan",
}

# ── Country display names (short for buttons) ─────────────────────────────────
COUNTRY_DISPLAY = {
    "al":"Albania","dz":"Algeria","ar":"Argentina","am":"Armenia","au":"Australia",
    "at":"Austria","az":"Azerbaijan","bs":"Bahamas","bh":"Bahrain","bd":"Bangladesh",
    "bb":"Barbados","by":"Belarus","be":"Belgium","bo":"Bolivia","bw":"Botswana",
    "br":"Brazil","bn":"Brunei","kh":"Cambodia","cm":"Cameroon","ca":"Canada",
    "ky":"Cayman Is.","cl":"Chile","cn":"China","co":"Colombia","cr":"Costa Rica",
    "hr":"Croatia","cu":"Cuba","cy":"Cyprus","dk":"Denmark","do":"Dominican Rep.",
    "cd":"DR Congo","ec":"Ecuador","eg":"Egypt","sv":"El Salvador","ae":"UAE",
    "ee":"Estonia","et":"Ethiopia","fj":"Fiji","fi":"Finland","fr":"France",
    "de":"Germany","gh":"Ghana","gt":"Guatemala","hn":"Honduras","hk":"Hong Kong",
    "hu":"Hungary","in":"India","id":"Indonesia","ir":"Iran","ie":"Ireland",
    "il":"Israel","it":"Italy","ci":"Ivory Coast","jm":"Jamaica","jp":"Japan",
    "jo":"Jordan","kz":"Kazakhstan","ke":"Kenya","kr":"S. Korea","kw":"Kuwait",
    "lv":"Latvia","lb":"Lebanon","ls":"Lesotho","ly":"Libya","lt":"Lithuania",
    "lu":"Luxembourg","mg":"Madagascar","mw":"Malawi","my":"Malaysia","ml":"Mali",
    "mt":"Malta","mu":"Mauritius","mx":"Mexico","md":"Moldova","ma":"Morocco",
    "mm":"Myanmar","na":"Namibia","np":"Nepal","nl":"Netherlands","nz":"New Zealand",
    "ni":"Nicaragua","ng":"Nigeria","no":"Norway","om":"Oman","pk":"Pakistan",
    "pa":"Panama","pg":"Papua NG","py":"Paraguay","pe":"Peru","ph":"Philippines",
    "pl":"Poland","pt":"Portugal","pr":"Puerto Rico","qa":"Qatar","ro":"Romania",
    "ru":"Russia","rw":"Rwanda","sa":"Saudi Arabia","sn":"Senegal","sg":"Singapore",
    "sk":"Slovakia","si":"Slovenia","za":"South Africa","es":"Spain","lk":"Sri Lanka",
    "sr":"Suriname","se":"Sweden","ch":"Switzerland","tw":"Taiwan","tz":"Tanzania",
    "th":"Thailand","cz":"Czech Rep.","is":"Iceland","tt":"Trinidad","tn":"Tunisia",
    "tr":"Turkey","ug":"Uganda","ua":"Ukraine","gb":"UK","us":"USA",
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

_FAKE_SORTED = sorted(COUNTRY_ALIASES.items(), key=lambda x: x[1])
_FAKE_PAGE_SIZE = 42
_FAKE_PAGES = [_FAKE_SORTED[i:i+_FAKE_PAGE_SIZE] for i in range(0, len(_FAKE_SORTED), _FAKE_PAGE_SIZE)]


# ── Country flag emoji map ────────────────────────────────────────────────────
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


# Names are loaded per-country from names.json
# ─────────────────────────────────────────────────────────────────────────────

# ── Health Check Server ───────────────────────────────────────────────────────
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running.")
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
    def log_message(self, format, *args):
        pass

def run_health_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    server.serve_forever()
# ─────────────────────────────────────────────────────────────────────────────

def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(CHANNEL_NAME, url=CHANNEL_URL)],
        [InlineKeyboardButton(OWNER_NAME,   url=OWNER_URL)],
    ])

# ── MarkdownV2 escape ──────────────────────────────────────────────────────────
def e(t: str) -> str:
    for c in r"\_*[]()~`>#+-=|{}.!":
        t = t.replace(c, "\\" + c)
    return t

# ── BIN formatter ─────────────────────────────────────────────────────────────
def fmt_bin(bin_number: str, data: dict) -> str:
    brand   = str(data.get("brand",   "N/A"))
    bank    = str(data.get("bank",    "N/A"))
    typ     = str(data.get("type",    "N/A"))
    level   = str(data.get("level",   "N/A"))
    country = str(data.get("country", "N/A"))
    emoji   = str(data.get("emoji",   ""))
    no_vbv  = str(data.get("no_vbv",  "TRUE"))
    novbv_icon = "✅" if no_vbv == "TRUE" else "❌"
    return (
        "💳 *BIN RESULT*\n\n"
        "📌 *BIN:* `" + bin_number + "`\n"
        "🏦 *Bank:* "    + e(bank)    + "\n"
        "📳 *Brand:* "   + e(brand)   + "\n"
        "💴 *Type:* "    + e(typ)     + "\n"
        "⭐ *Level:* "   + e(level)   + "\n"
        "🌍 *Country:* " + emoji + " " + e(country) + "\n"
        "🔐 *NO VBV:* "  + novbv_icon + " *" + e(no_vbv) + "*"
    )

# ── Fetch BIN from API ────────────────────────────────────────────────────────
ALPHA3 = {
    "US":"USA","GB":"GBR","AU":"AUS","CA":"CAN","DE":"DEU","FR":"FRA",
    "IN":"IND","BR":"BRA","MX":"MEX","JP":"JPN","CN":"CHN","RU":"RUS",
    "SG":"SGP","NL":"NLD","ES":"ESP","IT":"ITA","SE":"SWE","NO":"NOR",
    "FI":"FIN","BE":"BEL","AT":"AUT","CH":"CHE","NZ":"NZL","ZA":"ZAF",
    "PT":"PRT","PL":"POL","TW":"TWN","TT":"TTO","DO":"DOM","AR":"ARG",
    "VE":"VEN","IL":"ISR","KZ":"KAZ","BN":"BRN","JO":"JOR","AE":"ARE",
    "PE":"PER","NG":"NGA","TR":"TUR","MY":"MYS","EG":"EGY","HN":"HND",
    "CR":"CRI","CO":"COL","EC":"ECU","GT":"GTM","CL":"CHL","TN":"TUN",
    "MT":"MLT","PA":"PAN","HK":"HKG","SA":"SAU","IE":"IRL","DK":"DNK",
}

async def fetch_bin(bin_number: str) -> dict | None:
    try:
        resp = requests.get(
            "https://binlist.io/lookup/" + bin_number + "/",
            headers={"Accept": "application/json"},
            timeout=8
        )
        if resp.status_code == 200:
            d = resp.json()
            bank    = d.get("bank", {})
            country = d.get("country", {})
            alpha2  = country.get("alpha2", "N/A").upper() if isinstance(country, dict) else "N/A"
            return {
                "brand":   str(d.get("scheme", d.get("brand", "N/A"))).upper(),
                "bank":    str(bank.get("name", "N/A") if isinstance(bank, dict) else bank).upper(),
                "type":    str(d.get("type", "N/A")).upper(),
                "level":   str(d.get("brand", d.get("tier", "N/A"))).upper(),
                "country": str(country.get("name", "N/A") if isinstance(country, dict) else country).upper(),
                "alpha2":  alpha2,
                "alpha3":  ALPHA3.get(alpha2, alpha2),
                "numeric": str(country.get("numeric", "N/A") if isinstance(country, dict) else "N/A"),
                "emoji":   str(country.get("emoji", "") if isinstance(country, dict) else ""),
                "no_vbv":  "TRUE" if not d.get("prepaid", False) else "FALSE",
            }
    except Exception as ex:
        print("[BIN] error:", ex)
    return None

# ── /start ────────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user  = update.effective_user
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

# ── /help ─────────────────────────────────────────────────────────────────────
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

# ── /chkbin ───────────────────────────────────────────────────────────────────
async def bin_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usage = (
        "❌ Invalid usage\\!\n\n"
        "✅ Usage: `/chkbin 440769`\n"
        "📌 Example: `/chkbin 521234`"
    )
    if not context.args:
        await update.message.reply_text(usage, parse_mode="MarkdownV2", reply_markup=main_keyboard())
        return
    bin_number = context.args[0].strip()[:6]
    if not bin_number.isdigit() or len(bin_number) < 6:
        await update.message.reply_text(usage, parse_mode="MarkdownV2", reply_markup=main_keyboard())
        return

    # Check local DB first
    if bin_number in BIN_DB:
        await update.message.reply_text(
            fmt_bin(bin_number, BIN_DB[bin_number]),
            parse_mode="MarkdownV2", reply_markup=main_keyboard()
        )
        return

    loading = await update.message.reply_text("🔍 Looking up BIN...")

    async def do_animate(msg):
        frames = [
            "🔍 Looking up BIN ⬜⬜⬜",
            "🔍 Looking up BIN 🟦⬜⬜",
            "🔍 Looking up BIN 🟦🟦⬜",
            "🔍 Looking up BIN 🟦🟦🟦",
            "🔍 Looking up BIN ⬜⬜⬜",
        ]
        for frame in frames:
            try:
                await msg.edit_text(frame)
                await asyncio.sleep(0.7)
            except Exception:
                pass

    anim = asyncio.create_task(do_animate(loading))
    data = await fetch_bin(bin_number)
    anim.cancel()
    try:
        await anim
    except asyncio.CancelledError:
        pass
    try:
        await loading.delete()
    except Exception:
        pass

    if not data:
        await update.message.reply_text(
            "⚠️ BIN not found\\. Please check the number and try again\\.",
            parse_mode="MarkdownV2", reply_markup=main_keyboard()
        )
        return
    await update.message.reply_text(
        fmt_bin(bin_number, data), parse_mode="MarkdownV2", reply_markup=main_keyboard()
    )

# ── /genbin ───────────────────────────────────────────────────────────────────
async def genbin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    arg = context.args[0].lower() if context.args else ""

    if arg:
        # Filter BINs by country alpha2
        alpha2 = arg.upper()
        # Also allow full country name
        if len(arg) != 2:
            alpha2 = next(
                (v["alpha2"] for v in BIN_DB.values() if v.get("country","").lower() == arg),
                None
            )
        if not alpha2:
            await update.message.reply_text(
                "⚠️ Unknown country code\\. Use ISO 2\\-letter code like `us`, `gb`, `au`",
                parse_mode="MarkdownV2", reply_markup=main_keyboard()
            )
            return
        pool = {k: v for k, v in BIN_DB.items() if v.get("alpha2","").upper() == alpha2}
        if not pool:
            await update.message.reply_text(
                "⚠️ No BINs found for that country in the database\\.",
                parse_mode="MarkdownV2", reply_markup=main_keyboard()
            )
            return
    else:
        pool = BIN_DB

    bin_number = random.choice(list(pool.keys()))
    data = pool[bin_number]
    await update.message.reply_text(
        fmt_bin(bin_number, data), parse_mode="MarkdownV2", reply_markup=main_keyboard()
    )


# ── Country picker keyboard builder ──────────────────────────────────────────
def fake_country_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    items = _FAKE_PAGES[page]
    rows = []
    row = []
    for i, (code, _) in enumerate(items):
        flag = COUNTRY_EMOJI.get(code, "🌐")
        display = COUNTRY_DISPLAY.get(code, code.upper())
        row.append(InlineKeyboardButton(f"{flag} {display}", callback_data=f"fake:{code}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    # Navigation row
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀ Prev", callback_data=f"fake_page:{page-1}"))
    nav.append(InlineKeyboardButton(f"📄 {page+1}/{len(_FAKE_PAGES)}", callback_data="fake_noop"))
    if page < len(_FAKE_PAGES) - 1:
        nav.append(InlineKeyboardButton("Next ▶", callback_data=f"fake_page:{page+1}"))
    rows.append(nav)

    # Random button
    rows.append([InlineKeyboardButton("🎲 Random Country", callback_data="fake:random")])
    return InlineKeyboardMarkup(rows)

# ── /fake ─────────────────────────────────────────────────────────────────────
def build_fake_identity(country_key: str) -> str:
    """Build a fake identity message for the given country key."""
    addresses = COUNTRY_DATA.get(country_key, [])
    if not addresses:
        return None

    addr = random.choice(addresses)
    country_names = NAMES_DATA.get(country_key, {})
    first_pool = country_names.get("first") or [n for v in NAMES_DATA.values() for n in v.get("first", [])]
    last_pool  = country_names.get("last")  or [n for v in NAMES_DATA.values() for n in v.get("last", [])]
    first = random.choice(first_pool)
    last  = random.choice(last_pool)

    # Get flag emoji for this country
    code = next((k for k, v in COUNTRY_ALIASES.items() if v == country_key), "")
    flag = COUNTRY_EMOJI.get(code, "🌐")

    address1 = addr.get("address1", "N/A")
    address2 = addr.get("address2", "")
    city     = addr.get("city",     "N/A")
    state    = addr.get("state",    "N/A")
    postcode = addr.get("postcode", "N/A")
    phone    = addr.get("phone",    "N/A")

    msg = (
        f"{flag} *Fake Identity* — {country_key}\n\n"
        f"▸ *Name:* `{first} {last}`\n"
        f"▸ *Phone:* `{phone}`\n"
        f"▸ *Address 1:* `{address1}`\n"
    )
    if address2:
        msg += f"▸ *Address 2:* `{address2}`\n"
    msg += (
        f"▸ *City:* `{city}`\n"
        f"▸ *State:* `{state}`\n"
        f"▸ *Postcode:* `{postcode}`\n"
        f"▸ *Country:* `{country_key}`"
    )
    return msg


async def fake(update: Update, context: ContextTypes.DEFAULT_TYPE):
    arg = context.args[0].lower() if context.args else ""

    if arg:
        # Direct usage: /fake us
        country_key = COUNTRY_ALIASES.get(arg)
        if not country_key:
            for k in COUNTRY_DATA:
                if k.lower() == arg:
                    country_key = k
                    break
        if not country_key or country_key not in COUNTRY_DATA:
            await update.message.reply_text(
                "⚠️ Unknown country code\\. Use `/fake` to open the country picker\\.",
                parse_mode="MarkdownV2", reply_markup=main_keyboard()
            )
            return
        msg = build_fake_identity(country_key)
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=main_keyboard())
    else:
        # Show interactive country picker
        await update.message.reply_text(
            "🌍 *Select a country* to generate a fake identity:",
            parse_mode="MarkdownV2",
            reply_markup=fake_country_keyboard(0)
        )


async def fake_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    # Answer immediately to stop the loading spinner
    await query.answer()

    data = query.data

    # ── No-op (page indicator button) ────────────────────────────────────────
    if data == "fake_noop":
        return

    # ── Page navigation ───────────────────────────────────────────────────────
    if data.startswith("fake_page:"):
        page = int(data.split(":")[1])
        try:
            await query.edit_message_text(
                "🌍 *Select a country* to generate a fake identity:",
                parse_mode="MarkdownV2",
                reply_markup=fake_country_keyboard(page)
            )
        except Exception:
            pass
        return

    # ── Country selected ──────────────────────────────────────────────────────
    if data.startswith("fake:"):
        code = data.split(":")[1]
        if code == "random":
            country_key = random.choice(list(COUNTRY_DATA.keys()))
            back_code   = next((k for k, v in COUNTRY_ALIASES.items() if v == country_key), "")
        else:
            country_key = COUNTRY_ALIASES.get(code)
            back_code   = code

        if not country_key or country_key not in COUNTRY_DATA:
            await query.answer("Country not found.", show_alert=True)
            return

        msg = build_fake_identity(country_key)

        # Result keyboard: regenerate same country, back to picker, random
        result_kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔄 Regenerate", callback_data=f"fake:{back_code}"),
                InlineKeyboardButton("🌍 Pick Country", callback_data="fake_page:0"),
            ],
            [InlineKeyboardButton("🎲 Random", callback_data="fake:random")],
        ])

        # Edit the message in-place — each user edits only their own message
        # so multiple concurrent users never interfere with each other
        try:
            await query.edit_message_text(
                msg,
                parse_mode="Markdown",
                reply_markup=result_kb
            )
        except Exception:
            # Fallback if edit fails (e.g. message too old)
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=msg,
                parse_mode="Markdown",
                reply_markup=result_kb
            )

# ── Luhn Algorithm ────────────────────────────────────────────────────────────
def luhn_complete(prefix: str) -> str:
    digits = [int(d) for d in str(prefix)]
    digits.append(0)
    total = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    check = (10 - (total % 10)) % 10
    return str(prefix) + str(check)

# ── /gen ──────────────────────────────────────────────────────────────────────
async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    USAGE = (
        "❌ *No BIN provided\\!*\n\n"
        "ℹ️ *Usage:*\n"
        "`/gen BIN`\n`/gen BIN EXP`\n`/gen BIN EXP CVV`\n"
        "`/gen BIN\\|EXP\\|CVV`\n\n"
        "📌 *Examples:*\n"
        "`/gen 498416`\n`/gen 49841612345`\n"
        "`/gen 498416 05/28`\n`/gen 498416 05/28 999`\n"
        "`/gen 498416\\|05\\|2028\\|999`"
    )
    if not context.args:
        await update.message.reply_text(USAGE, parse_mode="MarkdownV2", reply_markup=main_keyboard())
        return

    raw   = " ".join(context.args).strip()
    parts = [p.strip() for p in raw.split("|")] if "|" in raw else raw.split()

    bin_number = parts[0] if parts else ""
    if not bin_number.isdigit() or len(bin_number) < 6 or len(bin_number) > 15:
        await update.message.reply_text(USAGE, parse_mode="MarkdownV2", reply_markup=main_keyboard())
        return

    fixed_exp = None
    if len(parts) >= 2:
        exp_raw = parts[1].strip().replace("/", "")
        if len(exp_raw) == 4 and exp_raw.isdigit():
            fixed_exp = (exp_raw[:2], "20" + exp_raw[2:])
        elif len(exp_raw) == 6 and exp_raw.isdigit():
            fixed_exp = (exp_raw[:2], exp_raw[2:])
        elif len(exp_raw) == 2 and exp_raw.isdigit():
            fixed_exp = (str(random.randint(1, 12)).zfill(2), "20" + exp_raw)

    fixed_cvv = None
    if len(parts) >= 3:
        cvv_raw = parts[2].strip()
        if cvv_raw.isdigit() and 2 <= len(cvv_raw) <= 4:
            fixed_cvv = cvv_raw

    bin_info = BIN_DB.get(bin_number[:6])
    cards = []
    for _ in range(10):
        pad    = 15 - len(bin_number)
        middle = "".join([str(random.randint(0, 9)) for _ in range(pad)])
        cc_num = luhn_complete(bin_number + middle)
        if fixed_exp:
            mm, yyyy = fixed_exp
        else:
            mm   = str(random.randint(1, 12)).zfill(2)
            yyyy = str(random.randint(2026, 2030))
        cvv = fixed_cvv if fixed_cvv else str(random.randint(100, 999))
        cards.append(cc_num + "|" + mm + "|" + yyyy + "|" + cvv)

    exp_label = (fixed_exp[0] + "/" + fixed_exp[1]) if fixed_exp else "RAND"
    cvv_label = fixed_cvv if fixed_cvv else "RAND"

    header = (
        "💳 *Generated CC*\n"
        "🔹 BIN: `" + bin_number + "` "
        "\\| EXP: `" + exp_label + "` "
        "\\| CVV: `" + cvv_label + "`\n"
    )
    if bin_info:
        vbv_icon = "✅" if bin_info.get("no_vbv", "TRUE") == "TRUE" else "❌"
        header += (
            "🏦 *Bank:* "    + e(str(bin_info.get("bank",    "N/A"))) + "\n"
            "📳 *Brand:* "   + e(str(bin_info.get("brand",   "N/A"))) + "\n"
            "🌍 *Country:* " + str(bin_info.get("emoji", "")) + " " + e(str(bin_info.get("country", "N/A"))) + "\n"
            "🔐 *NO VBV:* "  + vbv_icon + "\n"
        )

    body = "\n".join("`" + cc + "`" for cc in cards)
    await update.message.reply_text(
        header + "\n" + body, parse_mode="MarkdownV2", reply_markup=main_keyboard()
    )

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    t = threading.Thread(target=run_health_server, daemon=True)
    t.start()
    print(f"[✓] Health server running on port {PORT}")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",  start))
    app.add_handler(CommandHandler("help",   help_cmd))
    app.add_handler(CommandHandler("chkbin", bin_lookup))
    app.add_handler(CommandHandler("genbin", genbin))
    app.add_handler(CommandHandler("fake",   fake))
    app.add_handler(CallbackQueryHandler(fake_callback, pattern="^fake"))
    app.add_handler(CommandHandler("gen",    gen))
    print("[✓] Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()