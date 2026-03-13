import os
import random
import asyncio
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
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
        pass  # Suppress access logs

def run_health_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    server.serve_forever()
# ─────────────────────────────────────────────────────────────────────────────

def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(CHANNEL_NAME, url=CHANNEL_URL)],
        [InlineKeyboardButton(OWNER_NAME,   url=OWNER_URL)],
    ])

# ── BIN DATABASE ──────────────────────────────────────────────────────────────
BIN_DB = {
    # AUSTRALIA
    "456432": {"brand":"VISA","bank":"SUNCORP-METWAY, LTD.","type":"DEBIT","level":"CLASSIC","country":"AUSTRALIA","alpha2":"AU","alpha3":"AUS","numeric":"036","emoji":"🇦🇺","no_vbv":"TRUE"},
    "456430": {"brand":"VISA","bank":"SUNCORP-METWAY, LTD.","type":"DEBIT","level":"CLASSIC","country":"AUSTRALIA","alpha2":"AU","alpha3":"AUS","numeric":"036","emoji":"🇦🇺","no_vbv":"TRUE"},
    "460198": {"brand":"VISA","bank":"COMMONWEALTH BANK OF AUSTRALIA","type":"CREDIT","level":"CLASSIC","country":"AUSTRALIA","alpha2":"AU","alpha3":"AUS","numeric":"036","emoji":"🇦🇺","no_vbv":"TRUE"},
    "494052": {"brand":"VISA","bank":"COMMONWEALTH BANK OF AUSTRALIA","type":"CREDIT","level":"CLASSIC","country":"AUSTRALIA","alpha2":"AU","alpha3":"AUS","numeric":"036","emoji":"🇦🇺","no_vbv":"TRUE"},
    "456442": {"brand":"VISA","bank":"COMMONWEALTH BANK OF AUSTRALIA","type":"CREDIT","level":"CLASSIC","country":"AUSTRALIA","alpha2":"AU","alpha3":"AUS","numeric":"036","emoji":"🇦🇺","no_vbv":"TRUE"},
    "552638": {"brand":"MASTERCARD","bank":"BENDIGO AND ADELAIDE BANK LIMITED","type":"CREDIT","level":"BUSINESS","country":"AUSTRALIA","alpha2":"AU","alpha3":"AUS","numeric":"036","emoji":"🇦🇺","no_vbv":"TRUE"},
    "498416": {"brand":"VISA","bank":"MACQUARIE BANK, LTD.","type":"CREDIT","level":"SIGNATURE","country":"AUSTRALIA","alpha2":"AU","alpha3":"AUS","numeric":"036","emoji":"🇦🇺","no_vbv":"TRUE"},
    "516361": {"brand":"MASTERCARD","bank":"WESTPAC BANKING CORPORATION","type":"DEBIT","level":"STANDARD","country":"AUSTRALIA","alpha2":"AU","alpha3":"AUS","numeric":"036","emoji":"🇦🇺","no_vbv":"TRUE"},
    "531355": {"brand":"MASTERCARD","bank":"NATIONAL AUSTRALIA BANK LIMITED","type":"CREDIT","level":"PLATINUM","country":"AUSTRALIA","alpha2":"AU","alpha3":"AUS","numeric":"036","emoji":"🇦🇺","no_vbv":"TRUE"},
    "546827": {"brand":"MASTERCARD","bank":"AUSTRALIA AND NEW ZEALAND BANKING GROUP","type":"CREDIT","level":"STANDARD","country":"AUSTRALIA","alpha2":"AU","alpha3":"AUS","numeric":"036","emoji":"🇦🇺","no_vbv":"TRUE"},
    # UNITED STATES
    "401754": {"brand":"VISA","bank":"WACHOVIA BANK N.A.","type":"DEBIT","level":"CLASSIC","country":"UNITED STATES","alpha2":"US","alpha3":"USA","numeric":"840","emoji":"🇺🇸","no_vbv":"TRUE"},
    "401797": {"brand":"VISA","bank":"CAPITAL ONE BANK","type":"CREDIT","level":"CLASSIC","country":"UNITED STATES","alpha2":"US","alpha3":"USA","numeric":"840","emoji":"🇺🇸","no_vbv":"TRUE"},
    "401804": {"brand":"VISA","bank":"CITIBANK (SOUTH DAKOTA) N.A.","type":"CREDIT","level":"PLATINUM","country":"UNITED STATES","alpha2":"US","alpha3":"USA","numeric":"840","emoji":"🇺🇸","no_vbv":"TRUE"},
    "401854": {"brand":"VISA","bank":"CAPITAL ONE BANK","type":"CREDIT","level":"GOLD/PREM","country":"UNITED STATES","alpha2":"US","alpha3":"USA","numeric":"840","emoji":"🇺🇸","no_vbv":"TRUE"},
    "401868": {"brand":"VISA","bank":"BANK OF AMERICA N.A.","type":"CREDIT","level":"GOLD/PREM","country":"UNITED STATES","alpha2":"US","alpha3":"USA","numeric":"840","emoji":"🇺🇸","no_vbv":"TRUE"},
    "401901": {"brand":"VISA","bank":"BANK OF AMERICA N.A.","type":"CREDIT","level":"GOLD/PREM","country":"UNITED STATES","alpha2":"US","alpha3":"USA","numeric":"840","emoji":"🇺🇸","no_vbv":"TRUE"},
    "401975": {"brand":"VISA","bank":"FIA CARD SERVICES N.A.","type":"CREDIT","level":"PLATINUM","country":"UNITED STATES","alpha2":"US","alpha3":"USA","numeric":"840","emoji":"🇺🇸","no_vbv":"TRUE"},
    "401981": {"brand":"VISA","bank":"CITIBANK N.A.","type":"CREDIT","level":"CLASSIC","country":"UNITED STATES","alpha2":"US","alpha3":"USA","numeric":"840","emoji":"🇺🇸","no_vbv":"TRUE"},
    "402021": {"brand":"VISA","bank":"MBNA AMERICA BANK N.A.","type":"CREDIT","level":"PLATINUM","country":"UNITED STATES","alpha2":"US","alpha3":"USA","numeric":"840","emoji":"🇺🇸","no_vbv":"TRUE"},
    "402297": {"brand":"VISA","bank":"JPMORGAN CHASE BANK","type":"CREDIT","level":"CLASSIC","country":"UNITED STATES","alpha2":"US","alpha3":"USA","numeric":"840","emoji":"🇺🇸","no_vbv":"TRUE"},
    # UNITED KINGDOM
    "414260": {"brand":"VISA","bank":"AIB GROUP (UK) PLC","type":"CREDIT","level":"BUSINESS","country":"UNITED KINGDOM","alpha2":"GB","alpha3":"GBR","numeric":"826","emoji":"🇬🇧","no_vbv":"TRUE"},
    "454434": {"brand":"VISA","bank":"AIB GROUP (UK) PLC","type":"DEBIT","level":"CLASSIC","country":"UNITED KINGDOM","alpha2":"GB","alpha3":"GBR","numeric":"826","emoji":"🇬🇧","no_vbv":"TRUE"},
    "413777": {"brand":"VISA","bank":"CITIBANK INTERNATIONAL PLC","type":"CREDIT","level":"CLASSIC","country":"UNITED KINGDOM","alpha2":"GB","alpha3":"GBR","numeric":"826","emoji":"🇬🇧","no_vbv":"TRUE"},
    "445984": {"brand":"VISA","bank":"CITIBANK INTERNATIONAL PLC","type":"CREDIT","level":"GOLD","country":"UNITED KINGDOM","alpha2":"GB","alpha3":"GBR","numeric":"826","emoji":"🇬🇧","no_vbv":"TRUE"},
    "486483": {"brand":"VISA","bank":"HSBC BANK PLC","type":"CREDIT","level":"CORPORATE T&E","country":"UNITED KINGDOM","alpha2":"GB","alpha3":"GBR","numeric":"826","emoji":"🇬🇧","no_vbv":"TRUE"},
    "450906": {"brand":"VISA","bank":"CLYDESDALE BANK PLC","type":"CREDIT","level":"CLASSIC","country":"UNITED KINGDOM","alpha2":"GB","alpha3":"GBR","numeric":"826","emoji":"🇬🇧","no_vbv":"TRUE"},
    "476142": {"brand":"VISA","bank":"YORKSHIRE BANK","type":"DEBIT","level":"CLASSIC","country":"UNITED KINGDOM","alpha2":"GB","alpha3":"GBR","numeric":"826","emoji":"🇬🇧","no_vbv":"TRUE"},
    "401840": {"brand":"VISA","bank":"WOOLWICH PLC","type":"CREDIT","level":"CLASSIC","country":"UNITED KINGDOM","alpha2":"GB","alpha3":"GBR","numeric":"826","emoji":"🇬🇧","no_vbv":"TRUE"},
    "401841": {"brand":"VISA","bank":"WOOLWICH PLC","type":"CREDIT","level":"GOLD/PREM","country":"UNITED KINGDOM","alpha2":"GB","alpha3":"GBR","numeric":"826","emoji":"🇬🇧","no_vbv":"TRUE"},
    "402193": {"brand":"VISA","bank":"NATIONAL WESTMINSTER BANK PLC","type":"CREDIT","level":"GOLD/PREM","country":"UNITED KINGDOM","alpha2":"GB","alpha3":"GBR","numeric":"826","emoji":"🇬🇧","no_vbv":"TRUE"},
    # GERMANY
    "455620": {"brand":"VISA","bank":"SANTANDER CONSUMER BANK AG","type":"CREDIT","level":"GOLD","country":"GERMANY","alpha2":"DE","alpha3":"DEU","numeric":"276","emoji":"🇩🇪","no_vbv":"TRUE"},
    "456874": {"brand":"VISA","bank":"LANDESBANK BERLIN AG","type":"CREDIT","level":"GOLD","country":"GERMANY","alpha2":"DE","alpha3":"DEU","numeric":"276","emoji":"🇩🇪","no_vbv":"TRUE"},
    "413585": {"brand":"VISA","bank":"COMMERZBANK AG","type":"CREDIT","level":"GOLD","country":"GERMANY","alpha2":"DE","alpha3":"DEU","numeric":"276","emoji":"🇩🇪","no_vbv":"TRUE"},
    "428258": {"brand":"VISA","bank":"LANDESBANK BERLIN AG","type":"CREDIT","level":"CLASSIC","country":"GERMANY","alpha2":"DE","alpha3":"DEU","numeric":"276","emoji":"🇩🇪","no_vbv":"TRUE"},
    "427742": {"brand":"VISA","bank":"COMMERZBANK AG","type":"CREDIT","level":"BUSINESS","country":"GERMANY","alpha2":"DE","alpha3":"DEU","numeric":"276","emoji":"🇩🇪","no_vbv":"TRUE"},
    "424911": {"brand":"VISA","bank":"LANDESBANK SAAR","type":"CREDIT","level":"PLATINUM","country":"GERMANY","alpha2":"DE","alpha3":"DEU","numeric":"276","emoji":"🇩🇪","no_vbv":"TRUE"},
    "424201": {"brand":"VISA","bank":"LANDESBANK BADEN-WUERTTEMBERG","type":"CREDIT","level":"GOLD","country":"GERMANY","alpha2":"DE","alpha3":"DEU","numeric":"276","emoji":"🇩🇪","no_vbv":"TRUE"},
    "457038": {"brand":"VISA","bank":"DZ BANK AG","type":"CREDIT","level":"GOLD","country":"GERMANY","alpha2":"DE","alpha3":"DEU","numeric":"276","emoji":"🇩🇪","no_vbv":"TRUE"},
    "425723": {"brand":"VISA","bank":"BAYERISCHE LANDESBANK","type":"CREDIT","level":"CORPORATE","country":"GERMANY","alpha2":"DE","alpha3":"DEU","numeric":"276","emoji":"🇩🇪","no_vbv":"TRUE"},
    "401849": {"brand":"VISA","bank":"COMMERZBANK AG","type":"DEBIT","level":"CLASSIC","country":"GERMANY","alpha2":"DE","alpha3":"DEU","numeric":"276","emoji":"🇩🇪","no_vbv":"TRUE"},
    # CANADA
    "450004": {"brand":"VISA","bank":"CANADIAN IMPERIAL BANK OF COMMERCE","type":"CREDIT","level":"BUSINESS","country":"CANADA","alpha2":"CA","alpha3":"CAN","numeric":"124","emoji":"🇨🇦","no_vbv":"TRUE"},
    "451607": {"brand":"VISA","bank":"ROYAL BANK OF CANADA","type":"CREDIT","level":"BUSINESS","country":"CANADA","alpha2":"CA","alpha3":"CAN","numeric":"124","emoji":"🇨🇦","no_vbv":"TRUE"},
    "408586": {"brand":"VISA","bank":"TORONTO-DOMINION BANK","type":"CREDIT","level":"CLASSIC","country":"CANADA","alpha2":"CA","alpha3":"CAN","numeric":"124","emoji":"🇨🇦","no_vbv":"TRUE"},
    "472409": {"brand":"VISA","bank":"THE TORONTO-DOMINION BANK","type":"DEBIT","level":"CLASSIC","country":"CANADA","alpha2":"CA","alpha3":"CAN","numeric":"124","emoji":"🇨🇦","no_vbv":"TRUE"},
    "544612": {"brand":"MASTERCARD","bank":"CANADIAN TIRE BANK","type":"CREDIT","level":"STANDARD","country":"CANADA","alpha2":"CA","alpha3":"CAN","numeric":"124","emoji":"🇨🇦","no_vbv":"TRUE"},
    "518127": {"brand":"MASTERCARD","bank":"PRESIDENT'S CHOICE BANK","type":"CREDIT","level":"STANDARD","country":"CANADA","alpha2":"CA","alpha3":"CAN","numeric":"124","emoji":"🇨🇦","no_vbv":"TRUE"},
    "400128": {"brand":"VISA","bank":"LA FEDERATION DES CAISSES DESJARDINS DU QUEBEC","type":"CREDIT","level":"CLASSIC","country":"CANADA","alpha2":"CA","alpha3":"CAN","numeric":"124","emoji":"🇨🇦","no_vbv":"TRUE"},
    "400129": {"brand":"VISA","bank":"LA FEDERATION DES CAISSES DESJARDINS DU QUEBEC","type":"CREDIT","level":"CLASSIC","country":"CANADA","alpha2":"CA","alpha3":"CAN","numeric":"124","emoji":"🇨🇦","no_vbv":"TRUE"},
    "401951": {"brand":"VISA","bank":"FIRST NATIONAL BANK OF OMAHA","type":"CREDIT","level":"CLASSIC","country":"CANADA","alpha2":"CA","alpha3":"CAN","numeric":"124","emoji":"🇨🇦","no_vbv":"FALSE"},
    "401953": {"brand":"VISA","bank":"FIRST NATIONAL BANK OF OMAHA","type":"CREDIT","level":"CLASSIC","country":"CANADA","alpha2":"CA","alpha3":"CAN","numeric":"124","emoji":"🇨🇦","no_vbv":"FALSE"},
    # BRAZIL
    "498406": {"brand":"VISA","bank":"BANCO DO BRASIL, S.A.","type":"CREDIT","level":"PLATINUM","country":"BRAZIL","alpha2":"BR","alpha3":"BRA","numeric":"076","emoji":"🇧🇷","no_vbv":"TRUE"},
    "552072": {"brand":"MASTERCARD","bank":"ITAU UNIBANCO S.A.","type":"CREDIT","level":"PLATINUM","country":"BRAZIL","alpha2":"BR","alpha3":"BRA","numeric":"076","emoji":"🇧🇷","no_vbv":"TRUE"},
    "552640": {"brand":"MASTERCARD","bank":"ITAU UNIBANCO S.A.","type":"CREDIT","level":"BUSINESS","country":"BRAZIL","alpha2":"BR","alpha3":"BRA","numeric":"076","emoji":"🇧🇷","no_vbv":"TRUE"},
    "544859": {"brand":"MASTERCARD","bank":"ITAU UNIBANCO S.A.","type":"CREDIT","level":"GOLD","country":"BRAZIL","alpha2":"BR","alpha3":"BRA","numeric":"076","emoji":"🇧🇷","no_vbv":"TRUE"},
    "552289": {"brand":"MASTERCARD","bank":"BANCO DO BRASIL, S.A.","type":"CREDIT","level":"BLACK","country":"BRAZIL","alpha2":"BR","alpha3":"BRA","numeric":"076","emoji":"🇧🇷","no_vbv":"TRUE"},
    "400102": {"brand":"VISA","bank":"BANCO DO BRASIL S.A.","type":"DEBIT","level":"ELECTRON","country":"BRAZIL","alpha2":"BR","alpha3":"BRA","numeric":"076","emoji":"🇧🇷","no_vbv":"FALSE"},
    "400235": {"brand":"VISA","bank":"BANCO ITAU S.A.","type":"CREDIT","level":"CLASSIC","country":"BRAZIL","alpha2":"BR","alpha3":"BRA","numeric":"076","emoji":"🇧🇷","no_vbv":"TRUE"},
    "400236": {"brand":"VISA","bank":"CAIXA ECONOMICA FEDERAL","type":"CREDIT","level":"CLASSIC","country":"BRAZIL","alpha2":"BR","alpha3":"BRA","numeric":"076","emoji":"🇧🇷","no_vbv":"TRUE"},
    "402382": {"brand":"VISA","bank":"CAIXA ECONOMICA FEDERAL","type":"DEBIT","level":"ELECTRON","country":"BRAZIL","alpha2":"BR","alpha3":"BRA","numeric":"076","emoji":"🇧🇷","no_vbv":"FALSE"},
    "402383": {"brand":"VISA","bank":"CAIXA ECONOMICA FEDERAL","type":"CREDIT","level":"CLASSIC","country":"BRAZIL","alpha2":"BR","alpha3":"BRA","numeric":"076","emoji":"🇧🇷","no_vbv":"TRUE"},
}

# ── Helpers ───────────────────────────────────────────────────────────────────
ALPHA3 = {
    "US":"USA","GB":"GBR","AU":"AUS","CA":"CAN","DE":"DEU","FR":"FRA",
    "IN":"IND","BR":"BRA","MX":"MEX","JP":"JPN","CN":"CHN","RU":"RUS",
    "SG":"SGP","NL":"NLD","ES":"ESP","IT":"ITA","SE":"SWE","NO":"NOR",
    "FI":"FIN","BE":"BEL","AT":"AUT","CH":"CHE","NZ":"NZL","ZA":"ZAF",
    "PT":"PRT","PL":"POL","TW":"TWN","TT":"TTO","DO":"DOM","AR":"ARG",
    "VE":"VEN","IL":"ISR","KZ":"KAZ","BN":"BRN","JO":"JOR","AE":"ARE",
    "MO":"MAC","PE":"PER","NG":"NGA","BA":"BIH","TR":"TUR","MY":"MYS",
    "EG":"EGY","GR":"GRC","HN":"HND","CR":"CRI","CO":"COL","EC":"ECU",
    "GT":"GTM","CL":"CHL","PY":"PRY","TN":"TUN","MT":"MLT","PA":"PAN",
}

def e(t):
    for c in r"_[]()~>#+=|{}.!-":
        t = t.replace(c, "\\" + c)
    return t

def fmt_bin(bin_number, data):
    brand   = str(data.get("brand",   "N/A"))
    bank    = str(data.get("bank",    "N/A"))
    typ     = str(data.get("type",    "N/A"))
    level   = str(data.get("level",   "N/A"))
    country = str(data.get("country", "N/A"))
    alpha2  = str(data.get("alpha2",  "N/A"))
    emoji   = str(data.get("emoji",   ""))
    no_vbv  = str(data.get("no_vbv",  "TRUE"))
    novbv_icon = "\u2705" if no_vbv == "TRUE" else "\u274c"
    return (
        "\U0001f4b3 *BIN RESULT*\n\n"
        + "\U0001f4cc *BIN:* `" + bin_number + "`\n"
        + "\U0001f3e6 *Bank:* " + e(bank) + "\n"
        + "\U0001f4f3 *Brand:* " + e(brand) + "\n"
        + "\U0001f4b4 *Type:* " + e(typ) + "\n"
        + "\u2b50 *Level:* " + e(level) + "\n"
        + "\U0001f30d *Country:* " + emoji + " " + e(country) + "\n"
        + "\U0001f510 *NO VBV:* " + novbv_icon + " *" + e(no_vbv) + "*"
    )

async def fetch_bin(bin_number):
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
        "`/gen 498416123` \\(long BIN\\)\n"
        "`/gen 498416 05/28`\n"
        "`/gen 498416 05/28 999`\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔍 *BIN LOOKUP*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "`/chkbin 440769` — Lookup BIN info\n"
        "`/genbin` — Random BIN from database\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🪪 *FAKE IDENTITY*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "`/fake` — Random nationality\n"
        "`/fake us` — USA identity\n"
        "`/fake gb` — UK identity\n"
        "`/fake au` — Australian identity\n\n"
        "🌍 *Supported:* us gb au ca de fr es\n"
        "nl se no fi dk ie nz br mx in tr ch be"
    )
    await update.message.reply_text(msg, parse_mode="MarkdownV2", reply_markup=main_keyboard())

# ── /chkbin ───────────────────────────────────────────────────────────────────
async def bin_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usage = (
        "\u274c Invalid usage\\!\n\n"
        "\u2705 Usage: `/chkbin 440769`\n"
        "\U0001f4cc Example: `/chkbin 521234`"
    )
    if not context.args:
        await update.message.reply_text(usage, parse_mode="MarkdownV2", reply_markup=main_keyboard())
        return
    bin_number = context.args[0].strip()[:6]
    if not bin_number.isdigit() or len(bin_number) < 6:
        await update.message.reply_text(usage, parse_mode="MarkdownV2", reply_markup=main_keyboard())
        return

    loading = await update.message.reply_text("\U0001f50d Looking up BIN...")

    async def do_animate(msg):
        frames = [
            "\U0001f50d Looking up BIN \u2b1c\u2b1c\u2b1c",
            "\U0001f50d Looking up BIN \U0001f7e6\u2b1c\u2b1c",
            "\U0001f50d Looking up BIN \U0001f7e6\U0001f7e6\u2b1c",
            "\U0001f50d Looking up BIN \U0001f7e6\U0001f7e6\U0001f7e6",
            "\U0001f50d Looking up BIN \u2b1c\u2b1c\u2b1c",
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
            "\u26a0\ufe0f BIN not found\\. Please check the number and try again\\.",
            parse_mode="MarkdownV2", reply_markup=main_keyboard()
        )
        return
    await update.message.reply_text(
        fmt_bin(bin_number, data), parse_mode="MarkdownV2", reply_markup=main_keyboard()
    )

# ── /genbin ───────────────────────────────────────────────────────────────────
async def genbin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bin_number = random.choice(list(BIN_DB.keys()))
    data = BIN_DB[bin_number]
    await update.message.reply_text(
        fmt_bin(bin_number, data), parse_mode="MarkdownV2", reply_markup=main_keyboard()
    )

# ── /fake ─────────────────────────────────────────────────────────────────────
async def fake(update: Update, context: ContextTypes.DEFAULT_TYPE):
    valid_nats = [
        "us","gb","au","ca","de","fr","es","nl","se","no",
        "fi","dk","ie","nz","br","mx","in","tr","ch","be"
    ]
    nat = context.args[0].lower() if context.args else ""
    if nat and nat not in valid_nats:
        await update.message.reply_text(
            "\u26a0\ufe0f Unknown nationality: " + nat + "\n\nAvailable: " + ", ".join(valid_nats),
            reply_markup=main_keyboard()
        )
        return
    try:
        url  = "https://randomuser.me/api/?nat=" + nat if nat else "https://randomuser.me/api/"
        resp = requests.get(url, timeout=8)
        u    = resp.json()["results"][0]
        first    = u["name"]["first"]
        last     = u["name"]["last"]
        phone    = u["phone"]
        dob      = u["dob"]["date"][:10]
        street   = str(u["location"]["street"]["number"]) + " " + u["location"]["street"]["name"]
        city     = u["location"]["city"]
        state    = u["location"]["state"]
        country  = u["location"]["country"]
        postcode = str(u["location"]["postcode"])
        domains  = ["gmail.com","yahoo.com","hotmail.com","outlook.com","icloud.com","protonmail.com"]
        sep      = random.choice([".", "_", ""])
        num      = random.choice(["", str(random.randint(1, 999))])
        email    = first.lower() + sep + last.lower() + num + "@" + random.choice(domains)
        msg = (
            "\U0001f464 *Fake Identity*\n\n"
            + "\u25b8 *Name:* "     + e(first + " " + last) + "\n"
            + "\u25b8 *Email:* "    + e(email)    + "\n"
            + "\u25b8 *Phone:* "    + e(phone)    + "\n"
            + "\u25b8 *DOB:* "      + e(dob)      + "\n"
            + "\u25b8 *Address:* "  + e(street)   + "\n"
            + "\u25b8 *City:* "     + e(city)     + "\n"
            + "\u25b8 *State:* "    + e(state)    + "\n"
            + "\u25b8 *Country:* "  + e(country)  + "\n"
            + "\u25b8 *Postcode:* " + e(postcode)
        )
        await update.message.reply_text(msg, parse_mode="MarkdownV2", reply_markup=main_keyboard())
    except Exception as ex:
        await update.message.reply_text(
            "\u26a0\ufe0f Error fetching identity: " + str(ex), reply_markup=main_keyboard()
        )

# ── Luhn Algorithm ────────────────────────────────────────────────────────────
def luhn_complete(prefix):
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

# ── /gen ─────────────────────────────────────────────────────────────────────
async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    USAGE = (
        "\u274c *No BIN provided\\!*\n\n"
        "\u2139\ufe0f *Usage:*\n"
        "`/gen BIN`\n`/gen BIN EXP`\n`/gen BIN EXP CVV`\n"
        "`/gen BIN\\|EXP\\|CVV`\n\n"
        "\U0001f4cc *Examples:*\n"
        "`/gen 498416`\n`/gen 49841612345`\n"
        "`/gen 498416 05/28`\n`/gen 498416 05/28 999`\n"
        "`/gen 498416\\|05\\|2028\\|999`"
    )
    if not context.args:
        await update.message.reply_text(USAGE, parse_mode="MarkdownV2", reply_markup=main_keyboard())
        return

    raw = " ".join(context.args).strip()
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
        "\U0001f4b3 *Generated CC*\n"
        "\U0001f539 BIN: `" + bin_number + "` "
        "\\| EXP: `" + exp_label + "` "
        "\\| CVV: `" + cvv_label + "`\n"
    )
    if bin_info:
        vbv_icon = "\u2705" if bin_info.get("no_vbv", "TRUE") == "TRUE" else "\u274c"
        header += (
            "\U0001f3e6 *Bank:* "    + e(str(bin_info.get("bank",    "N/A"))) + "\n"
            "\U0001f4f3 *Brand:* "   + e(str(bin_info.get("brand",   "N/A"))) + "\n"
            "\U0001f30d *Country:* " + str(bin_info.get("emoji", "")) + " " + e(str(bin_info.get("country", "N/A"))) + "\n"
            "\U0001f510 *NO VBV:* "  + vbv_icon + "\n"
        )

    body = "\n".join("`" + cc + "`" for cc in cards)
    await update.message.reply_text(
        header + "\n" + body, parse_mode="MarkdownV2", reply_markup=main_keyboard()
    )

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    # Start health check server in background thread
    t = threading.Thread(target=run_health_server, daemon=True)
    t.start()
    print(f"Health server running on port {PORT}")

    # Start Telegram bot
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",  start))
    app.add_handler(CommandHandler("help",   help_cmd))
    app.add_handler(CommandHandler("chkbin", bin_lookup))
    app.add_handler(CommandHandler("genbin", genbin))
    app.add_handler(CommandHandler("fake",   fake))
    app.add_handler(CommandHandler("gen",    gen))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()