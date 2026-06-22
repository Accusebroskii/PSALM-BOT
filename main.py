import os
import discord
import schedule
import time
import random
import threading
from flask import Flask
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "0"))

PSALMS = [
    {
        "reference": "Psalm 23:1-3",
        "text": (
            "The Lord is my shepherd; I shall not want. "
            "He makes me lie down in green pastures. "
            "He leads me beside still waters. "
            "He restores my soul."
        ),
    },
    {
        "reference": "Psalm 1:1-2",
        "text": (
            "Blessed is the man who walks not in the counsel of the wicked, "
            "nor stands in the way of sinners, nor sits in the seat of scoffers; "
            "but his delight is in the law of the Lord, "
            "and on his law he meditates day and night."
        ),
    },
    {
        "reference": "Psalm 46:1-3",
        "text": (
            "God is our refuge and strength, a very present help in trouble. "
            "Therefore we will not fear though the earth gives way, "
            "though the mountains be moved into the heart of the sea, "
            "though its waters roar and foam."
        ),
    },
    {
        "reference": "Psalm 91:1-2",
        "text": (
            "He who dwells in the shelter of the Most High "
            "will abide in the shadow of the Almighty. "
            "I will say to the Lord, 'My refuge and my fortress, "
            "my God, in whom I trust.'"
        ),
    },
    {
        "reference": "Psalm 27:1",
        "text": (
            "The Lord is my light and my salvation; whom shall I fear? "
            "The Lord is the stronghold of my life; of whom shall I be afraid?"
        ),
    },
    {
        "reference": "Psalm 34:8",
        "text": (
            "Oh, taste and see that the Lord is good! "
            "Blessed is the man who takes refuge in him!"
        ),
    },
    {
        "reference": "Psalm 37:4",
        "text": (
            "Delight yourself in the Lord, "
            "and he will give you the desires of your heart."
        ),
    },
    {
        "reference": "Psalm 42:1-2",
        "text": (
            "As a deer pants for flowing streams, so pants my soul for you, O God. "
            "My soul thirsts for God, for the living God."
        ),
    },
    {
        "reference": "Psalm 51:10",
        "text": (
            "Create in me a clean heart, O God, "
            "and renew a right spirit within me."
        ),
    },
    {
        "reference": "Psalm 55:22",
        "text": (
            "Cast your burden on the Lord, and he will sustain you; "
            "he will never permit the righteous to be moved."
        ),
    },
    {
        "reference": "Psalm 62:1-2",
        "text": (
            "For God alone my soul waits in silence; "
            "from him comes my salvation. "
            "He alone is my rock and my salvation, my fortress; "
            "I shall not be greatly shaken."
        ),
    },
    {
        "reference": "Psalm 63:1",
        "text": (
            "O God, you are my God; earnestly I seek you; "
            "my soul thirsts for you; my flesh faints for you, "
            "as in a dry and weary land where there is no water."
        ),
    },
    {
        "reference": "Psalm 100:1-3",
        "text": (
            "Make a joyful noise to the Lord, all the earth! "
            "Serve the Lord with gladness! Come into his presence with singing! "
            "Know that the Lord, he is God! It is he who made us, and we are his."
        ),
    },
    {
        "reference": "Psalm 103:1-3",
        "text": (
            "Bless the Lord, O my soul, and all that is within me, bless his holy name! "
            "Bless the Lord, O my soul, and forget not all his benefits, "
            "who forgives all your iniquity, who heals all your diseases."
        ),
    },
    {
        "reference": "Psalm 118:24",
        "text": (
            "This is the day that the Lord has made; "
            "let us rejoice and be glad in it."
        ),
    },
    {
        "reference": "Psalm 119:105",
        "text": (
            "Your word is a lamp to my feet "
            "and a light to my path."
        ),
    },
    {
        "reference": "Psalm 121:1-2",
        "text": (
            "I lift up my eyes to the hills. From where does my help come? "
            "My help comes from the Lord, who made heaven and earth."
        ),
    },
    {
        "reference": "Psalm 139:1-3",
        "text": (
            "O Lord, you have searched me and known me! "
            "You know when I sit down and when I rise up; "
            "you discern my thoughts from afar. "
            "You search out my path and my lying down "
            "and are acquainted with all my ways."
        ),
    },
    {
        "reference": "Psalm 145:3",
        "text": (
            "Great is the Lord, and greatly to be praised, "
            "and his greatness is unsearchable."
        ),
    },
    {
        "reference": "Psalm 150:6",
        "text": (
            "Let everything that has breath praise the Lord! "
            "Praise the Lord!"
        ),
    },
    {
        "reference": "Psalm 19:1",
        "text": (
            "The heavens declare the glory of God, "
            "and the sky above proclaims his handiwork."
        ),
    },
    {
        "reference": "Psalm 16:8",
        "text": (
            "I have set the Lord always before me; "
            "because he is at my right hand, I shall not be shaken."
        ),
    },
    {
        "reference": "Psalm 31:3",
        "text": (
            "For you are my rock and my fortress; "
            "and for your name's sake you lead me and guide me."
        ),
    },
    {
        "reference": "Psalm 40:1-2",
        "text": (
            "I waited patiently for the Lord; he inclined to me and heard my cry. "
            "He drew me up from the pit of destruction, out of the miry bog, "
            "and set my feet upon a rock, making my steps secure."
        ),
    },
    {
        "reference": "Psalm 46:10",
        "text": (
            "Be still, and know that I am God. "
            "I will be exalted among the nations, "
            "I will be exalted in the earth!"
        ),
    },
    {
        "reference": "Psalm 56:3",
        "text": (
            "When I am afraid, I put my trust in you."
        ),
    },
    {
        "reference": "Psalm 73:26",
        "text": (
            "My flesh and my heart may fail, "
            "but God is the strength of my heart and my portion forever."
        ),
    },
    {
        "reference": "Psalm 86:5",
        "text": (
            "For you, O Lord, are good and forgiving, "
            "abounding in steadfast love to all who call upon you."
        ),
    },
    {
        "reference": "Psalm 90:2",
        "text": (
            "Before the mountains were brought forth, "
            "or ever you had formed the earth and the world, "
            "from everlasting to everlasting you are God."
        ),
    },
    {
        "reference": "Psalm 107:1",
        "text": (
            "Oh give thanks to the Lord, for he is good, "
            "for his steadfast love endures forever!"
        ),
    },
    {
        "reference": "Psalm 130:1-2",
        "text": (
            "Out of the depths I cry to you, O Lord! "
            "O Lord, hear my voice! "
            "Let your ears be attentive to the voice of my pleas for mercy!"
        ),
    },
    {
        "reference": "Psalm 143:8",
        "text": (
            "Let me hear in the morning of your steadfast love, "
            "for in you I trust. Make me know the way I should go, "
            "for to you I lift up my soul."
        ),
    },
    {
        "reference": "Psalm 147:3",
        "text": (
            "He heals the brokenhearted "
            "and binds up their wounds."
        ),
    },
]

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

app = Flask(__name__)

@app.route("/")
def home():
    return "Psalm Bot is alive!", 200

def run_flask():
    app.run(host="0.0.0.0", port=8000)

async def send_psalm():
    await client.wait_until_ready()
    try:
        channel = await client.fetch_channel(CHANNEL_ID)
    except discord.NotFound:
        print(f"[ERROR] Channel ID {CHANNEL_ID} not found. Check your CHANNEL_ID secret.")
        return
    except discord.Forbidden as e:
        print(f"[ERROR] Forbidden accessing channel {CHANNEL_ID}: {e.status} {e.text}")
        guilds = [f"{g.name} (ID: {g.id})" for g in client.guilds]
        print(f"[DEBUG] Bot is in these servers: {guilds if guilds else 'NONE — bot has not been added to any server!'}")
        return
    except Exception as e:
        print(f"[ERROR] Unexpected error fetching channel: {type(e).__name__}: {e}")
        return

    psalm = random.choice(PSALMS)
    now = datetime.now().strftime("%A, %B %d, %Y")

    embed = discord.Embed(
        title=f"Daily Psalm — {now}",
        description=psalm["text"],
        color=discord.Color.gold(),
    )
    embed.set_footer(text=psalm["reference"])

    await channel.send(
        content="@everyone",
        embed=embed,
        allowed_mentions=discord.AllowedMentions(everyone=True),
    )
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Sent psalm: {psalm['reference']}")

@tree.command(name="test", description="Send a random psalm to the configured channel right now.")
@discord.app_commands.default_permissions(administrator=True)
async def test_command(interaction: discord.Interaction):
    await interaction.response.send_message("Sending a psalm now...", ephemeral=True)
    await send_psalm()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] /test used by {interaction.user}")

def schedule_psalm():
    import asyncio
    schedule.every().day.at("08:00").do(lambda: asyncio.run_coroutine_threadsafe(send_psalm(), client.loop))

    while True:
        schedule.run_pending()
        time.sleep(30)

@client.event
async def on_ready():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Logged in as {client.user} (ID: {client.user.id})")
    print(f"[INFO] Psalms will be sent daily at 08:00 to channel ID {CHANNEL_ID}")

    domains = os.environ.get("REPLIT_DOMAINS", "")
    if domains:
        primary = domains.split(",")[0].strip()
        print(f"[INFO] UptimeRobot URL: https://{primary}/api/ping")

    for guild in client.guilds:
        print(f"[DEBUG] Channels visible in '{guild.name}':")
        for ch in guild.text_channels:
            print(f"  #{ch.name} — ID: {ch.id}")

    await tree.sync()
    print("[INFO] Slash commands synced")

    scheduler_thread = threading.Thread(target=schedule_psalm, daemon=True)
    scheduler_thread.start()

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("[ERROR] BOT_TOKEN secret is not set. Please add it in Replit Secrets.")
        exit(1)
    if CHANNEL_ID == 0:
        print("[ERROR] CHANNEL_ID secret is not set. Please add it in Replit Secrets.")
        exit(1)

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("[INFO] Keep-alive web server started on port 8000")

    client.run(BOT_TOKEN)
