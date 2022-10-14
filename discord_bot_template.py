import discord
from discord.ui import Button, View

PREFIX = ""
TOKEN = ""

# Sets the prefix of the bot

client = discord.Bot(command_prefix=PREFIX, intents=discord.Intents.all())

# Giving bot appropriate intents
# Currently giving all intents for demo purposes

Activity_Message = ""

# Sets activity message in bot profile/

@client.event
async def on_ready():
    activity = discord.Game(name=Activity_Message, type=3)

    # (Type) sets the type activity the bot is doing (Playing Game, Streaming, Activity or Custom Activity)

    await client.change_presence(status=discord.Status.idle, activity=activity)

    # Status sets the bots status (Online, Idle, Do not Disturb and Invisible)

    print("Online")
    await client.wait_until_ready()

    # Ready confirmation and status with prefix tips

@client.event
async def on_command_error(ctx, error):

    # Catches a missing argument error
    if isinstance(error, discord.ext.commands.MissingRequiredArgument):
        pass

    # Catches any errors based on instance

@client.slash_command(name = "ping", description = "Gets the bot's latency")
async def ping(ctx):
    await ctx.respond(f"Pong! 🏓\n *{client.latency}* ms")

    # Returns the latency of the bot

@client.slash_command(name = "hi", description = "Says hi back to the user")
async def ping(ctx):
    await ctx.respond(f"Hey {ctx.author.mention}!")

    # Says Hey back to the user (using a mention)

client.run(TOKEN)

