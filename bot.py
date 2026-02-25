import os
import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz
import asyncio

# โหลดค่าจาก Environment ของ Railway
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))                # ช่องสำหรับข้อความอัตโนมัติ (vehicle / Airdrop)
JOIN_CHANNEL_ID = int(os.getenv("JOIN_CHANNEL_ID", 0))   # ✅ ช่องสำหรับแจ้ง "เข้าเซิร์ฟเวอร์"
LEAVE_CHANNEL_ID = int(os.getenv("LEAVE_CHANNEL_ID", 0)) # ✅ ช่องสำหรับแจ้ง "ออกเซิร์ฟเวอร์"

# เปิด intents สำหรับตรวจจับสมาชิก
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

tz = pytz.timezone("Asia/Bangkok")
scheduler = AsyncIOScheduler(timezone=tz)

MESSAGES = {
"Airdrop": {
        "text": "# แจ้งเตือน อีก 10 นาที เข้า Airdrop ครับเพื่อนๆ\n**ชาวเมืองทุกท่านระวังโดนปรับนะครับ**\n<@&1419750622517006393> <@&1419750622517006394>",
        "image": "https://media2.giphy.com/media/ne3qb8GHvteK4QGtbs/giphy.gif",
        "times": ["19:50","21:50"],
        "color": 0xff5858,
        "activity": "กำลังรอสมาชิกเข้าแอร์ดรอปนะครับ 😎"
    },
    "Airdrop5": {
        "text": "# แจ้งเตือน อีก 5 นาที เข้า Airdrop ครับเพื่อนๆ\n**ชาวเมืองทุกท่านระวังโดนปรับนะครับ**\n<@&1419750622517006393> <@&1419750622517006394>",
        "image": "https://media2.giphy.com/media/ne3qb8GHvteK4QGtbs/giphy.gif",
        "times": ["19:56","21:56"],
        "color": 0xff5858,
        "activity": "กำลังรอสมาชิกเข้าแอร์ดรอปนะครับ 😎"
    },
    "Airdrop1": {
        "text": "# แจ้งเตือน ระบบเปิด Airdrop ให้เข้าเรียบร้อยแล้ว\n**โดนปรับก็ช่างหัวโคตรพ่อมึงโคตรแม่มึงนะครับ ตามหลายเทื่อละ**\n<@&1419750622517006393> <@&1419750622517006394>",
        "image": "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExd3Y4eTFvN3d1NXpkbmsxMWFyM2lzeDNrNzkxOXdpejRjcm8xOW02MyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/1KhjvfXgXcYxS0cuG0/giphy.gif",
        "times": ["20:01","22:01"],
        "color": 0x4682B4,
        "activity": "พร้อมปรับคนที่ขาด Airdrop แล้ว ✅"
    },
}

WAITING_ACTIVITY = "Bot By BoonHome"

async def set_activity(text=WAITING_ACTIVITY):
    activity = discord.Activity(type=discord.ActivityType.competing, name=text)
    await bot.change_presence(status=discord.Status.online, activity=activity)

async def send_message(category: str):
    data = MESSAGES.get(category)
    if not data:
        return
    await set_activity(data["activity"])
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        embed = discord.Embed(description=data["text"], color=data["color"])
        embed.set_image(url=data["image"])
        await channel.send(embed=embed)
        print(f"[{datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')}] ✅ Message sent ({category})")
    await set_activity(WAITING_ACTIVITY)

# 🔔 แจ้งเตือนสมาชิกเข้า
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(JOIN_CHANNEL_ID or CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="🎉 มีสมาชิกใหม่เข้าร่วมเซิร์ฟเวอร์!",
            description=f"ยินดีต้อนรับ {member.mention} เข้าสู่ **{member.guild.name}** 💫",
            color=0x66FF66,
            timestamp=datetime.now(tz)
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)
        print(f"[{datetime.now(tz)}] ✅ {member} เข้าร่วมเซิร์ฟเวอร์")

# 🔕 แจ้งเตือนสมาชิกออก
@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(LEAVE_CHANNEL_ID or CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="👋 มีสมาชิกออกจากเซิร์ฟเวอร์",
            description=f"{member.name} ได้ออกจาก **{member.guild.name}**",
            color=0xED4245,
            timestamp=datetime.now(tz)
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)
        print(f"[{datetime.now(tz)}] ❌ {member} ออกจากเซิร์ฟเวอร์")

# --- คำสั่ง Discord เดิม ---
@bot.command()
async def sendnow(ctx, category: str = "vehicle"):
    if category not in MESSAGES:
        await ctx.send(f"❌ หมวด '{category}' ไม่มีอยู่")
        return
    await send_message(category)
    await ctx.send(f"✅ ส่งข้อความหมวด '{category}' เรียบร้อยแล้ว!")

@bot.command()
async def Carnow(ctx, category: str = "vehicle1"):
    if category not in MESSAGES:
        await ctx.send(f"❌ หมวด '{category}' ไม่มีอยู่")
        return
    await send_message(category)
    await ctx.send(f"✅ ส่งข้อความหมวด '{category}' เรียบร้อยแล้ว!")

@bot.command()
async def status(ctx):
    await ctx.send(f"✅ บอททำงานอยู่ ({datetime.now(tz).strftime('%H:%M:%S %d/%m/%Y')})")

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    await set_activity(WAITING_ACTIVITY)
    for cat, info in MESSAGES.items():
        for t in info["times"]:
            hour, minute = map(int, t.split(":"))
            scheduler.add_job(
                send_message,
                trigger=CronTrigger(hour=hour, minute=minute, timezone=tz),
                args=[cat],
                coalesce=True,
                misfire_grace_time=60
            )
    scheduler.start()
    print("🕒 Scheduler started. Waiting for next job...")

bot.run(TOKEN)
