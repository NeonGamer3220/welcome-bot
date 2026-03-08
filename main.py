import discord
from discord.ext import commands
import json
import os
import os

# Load configuration
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

config = load_config()

# File to store member count
COUNT_FILE = config.get("COUNT_FILE", "member_count.json")

# Load or initialize member count
def load_count():
    if os.path.exists(COUNT_FILE):
        with open(COUNT_FILE, "r") as f:
            return json.load(f)
    return {"count": 0}

def save_count(data):
    with open(COUNT_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Bot setup
intents = discord.Intents.default()
intents.members = True  # Required to track member joins
intents.message_content = True  # Required for commands to work

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_member_join(member):
    """Send welcome message when a member joins"""
    # Load current count
    data = load_count()
    data["count"] += 1
    save_count(data)
    
    count = data["count"]
    
    # Get the welcome channel
    welcome_channel_id = config.get("WELCOME_CHANNEL_ID")
    if not welcome_channel_id:
        print("ERROR: WELCOME_CHANNEL_ID not set in config.json")
        return
    
    welcome_channel = bot.get_channel(welcome_channel_id)
    
    if not welcome_channel:
        print(f"ERROR: Could not find channel with ID {welcome_channel_id}")
        return
    
    # Format the welcome message
    welcome_message = config.get("WELCOME_MESSAGE", "Welcome {member}! You are the {count} player!")
    welcome_message = welcome_message.replace("{member}", member.mention)
    welcome_message = welcome_message.replace("{count}", str(count))
    welcome_message = welcome_message.replace("{member.name}", member.name)
    
    # Send the welcome message
    await welcome_channel.send(welcome_message)
    print(f"Welcome message sent for {member.name} - they are player #{count}")

@bot.command()
async def invite(ctx):
    """Generate an invite link with the required permissions for the bot"""
    # Define required permissions
    permissions = discord.Permissions(
        send_messages=True,
        embed_links=True,
        read_message_history=True,
        use_external_emojis=True
    )
    
    # Create invite URL
    invite_url = discord.utils.oauth_url(
        client_id=bot.user.id,
        permissions=permissions
    )
    
    embed = discord.Embed(
        title="🤖 Bot Invite Link",
        description="Use this link to invite the bot to your server:",
        color=discord.Color.green()
    )
    embed.add_field(
        name="Invite URL",
        value=f"[Click here to invite]({invite_url})"
    )
    embed.add_field(
        name="Required Permissions",
        value="- Send Messages\n- Embed Links\n- Read Message History\n- Use External Emojis\n- Server Members Intent (enabled in Discord Developer Portal)"
    )
    embed.set_footer(text="Note: Make sure to enable 'Server Members Intent' in the Bot section of Discord Developer Portal!")
    
    await ctx.send(embed=embed)

@bot.command()
async def count(ctx):
    """Check the current member count"""
    data = load_count()
    await ctx.send(f"Total members welcomed so far: {data['count']}")

@bot.command()
async def setcount(ctx, new_count: int):
    """Set the member count manually"""
    data = {"count": new_count}
    save_count(data)
    await ctx.send(f"Member count set to {new_count}")

# Run the bot
if __name__ == "__main__":
    # Get token from environment variable or config
    token = os.getenv("DISCORD_TOKEN") or os.getenv("BOT_TOKEN")
    
    if not token:
        print("ERROR: Please set DISCORD_TOKEN environment variable")
        print("You can create a .env file with: DISCORD_TOKEN=your_token_here")
        exit(1)
    
    print(f"Starting welcome bot...")
    print(f"Welcome channel: {config.get('WELCOME_CHANNEL_ID')}")
    print(f"Welcome message: {config.get('WELCOME_MESSAGE')}")
    
    bot.run(token)
