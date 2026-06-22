import os
import discord
from discord import app_commands
from datetime import datetime
from flask import Flask
import threading

MODMAIL_BOT_TOKEN = os.environ.get("MODMAIL_BOT_TOKEN")
MODMAIL_CHANNEL_ID = int(os.environ.get("MODMAIL_CHANNEL_ID", "0"))

active_threads = {}

intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
intents.members = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Mod Mail Bot is alive!", 200

def run_flask():
    flask_app.run(host="0.0.0.0", port=8001)

async def get_modmail_channel():
    try:
        return await client.fetch_channel(MODMAIL_CHANNEL_ID)
    except discord.NotFound:
        print(f"[ERROR] Modmail channel {MODMAIL_CHANNEL_ID} not found.")
        return None
    except discord.Forbidden:
        print(f"[ERROR] No permission to access modmail channel {MODMAIL_CHANNEL_ID}.")
        return None

async def find_thread_for_user(user_id):
    thread_id = active_threads.get(user_id)
    if not thread_id:
        return None
    try:
        thread = await client.fetch_channel(thread_id)
        if thread.archived:
            del active_threads[user_id]
            return None
        return thread
    except Exception:
        active_threads.pop(user_id, None)
        return None

async def handle_user_dm(message):
    user = message.author
    channel = await get_modmail_channel()
    if channel is None:
        await user.send("⚠️ The modmail system is currently unavailable. Please try again later.")
        return

    thread = await find_thread_for_user(user.id)

    if thread is None:
        thread = await channel.create_thread(
            name=f"{user.name} — {user.id}",
            type=discord.ChannelType.public_thread,
        )
        active_threads[user.id] = thread.id
        print(f"[{datetime.now().strftime('%H:%M:%S')}] New thread for {user.name} (ID: {user.id})")

        intro = discord.Embed(
            title="📬 New Mod Mail",
            color=discord.Color.blue(),
            timestamp=datetime.now(),
        )
        intro.add_field(name="User", value=f"{user.mention} (`{user.name}`)", inline=True)
        intro.add_field(name="User ID", value=str(user.id), inline=True)
        intro.set_thumbnail(url=user.display_avatar.url)
        intro.set_footer(text="Reply here to respond • Type !close to close the ticket")
        await thread.send(embed=intro)

        await user.send(
            "✅ Your message has been received! Our staff will get back to you as soon as possible.\n"
            "You can keep sending messages here and they'll all be forwarded."
        )

    fwd = discord.Embed(
        description=message.content or "*[no text]*",
        color=discord.Color.green(),
        timestamp=datetime.now(),
    )
    fwd.set_author(name=f"{user.name}", icon_url=user.display_avatar.url)

    if message.attachments:
        fwd.set_image(url=message.attachments[0].url)
        if len(message.attachments) > 1:
            fwd.add_field(
                name="Additional Attachments",
                value="\n".join(a.url for a in message.attachments[1:]),
            )

    await thread.send(embed=fwd)

async def handle_staff_reply(message):
    user_id = next((uid for uid, tid in active_threads.items() if tid == message.channel.id), None)
    if user_id is None:
        return

    if message.content.lower().strip() == "!close":
        try:
            user = await client.fetch_user(user_id)
            await user.send("📪 Your mod mail ticket has been closed. Thanks for reaching out!")
        except Exception:
            pass

        closed = discord.Embed(
            description="✅ Ticket closed.",
            color=discord.Color.red(),
            timestamp=datetime.now(),
        )
        closed.set_footer(text=f"Closed by {message.author.name}")
        await message.channel.send(embed=closed)
        await message.channel.edit(archived=True, locked=True)
        active_threads.pop(user_id, None)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Thread closed by {message.author.name}")
        return

    if message.author.bot:
        return

    try:
        user = await client.fetch_user(user_id)
        reply = discord.Embed(
            description=message.content or "*[no text]*",
            color=discord.Color.orange(),
            timestamp=datetime.now(),
        )
        reply.set_author(name=f"Staff — {message.author.name}", icon_url=message.author.display_avatar.url)

        if message.attachments:
            reply.set_image(url=message.attachments[0].url)

        await user.send(embed=reply)
        await message.add_reaction("✅")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message.author.name} replied to {user.name}")
    except discord.Forbidden:
        await message.channel.send("⚠️ Could not DM the user — they may have DMs disabled.")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if isinstance(message.channel, discord.DMChannel):
        await handle_user_dm(message)
    elif isinstance(message.channel, discord.Thread):
        await handle_staff_reply(message)

@client.event
async def on_ready():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Mod Mail Bot logged in as {client.user} (ID: {client.user.id})")

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

if __name__ == "__main__":
    if not MODMAIL_BOT_TOKEN:
        print("[ERROR] MODMAIL_BOT_TOKEN secret is not set.")
        exit(1)
    if MODMAIL_CHANNEL_ID == 0:
        print("[ERROR] MODMAIL_CHANNEL_ID secret is not set.")
        exit(1)

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("[INFO] Keep-alive server started on port 8001")

    client.run(MODMAIL_BOT_TOKEN)
