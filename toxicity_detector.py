import discord
from toxicity_database import *
from discord.ui import Button, View
from googleapiclient import discovery
from dotenv import load_dotenv
import json
import os

# Getting all secrets

load_dotenv()

API_KEY = os.getenv("API_KEY")
token = os.getenv("token")
cid = os.getenv("cid")

host = os.getenv("host")
user = os.getenv("username")
pwd = os.getenv("password")

# Initializing Database

login_info = [host, user, pwd] #in the future, I think we can implement some kind of login
db_name = user
creation = False

if creation == False:
  try:
    connection = create_db_connection(login_info[0], login_info[1], login_info[2], db_name)
    create_setting_table(connection)
    create_table(connection)
    creation = True
  except:
    creation = False

# Giving the bot Intents

intents = discord.Intents()
intents.message_content = True
intents.messages = True
intents.guilds = True

client = discord.Bot(command_prefix="+", intents=intents)

# Initializing Perspective API

ai_client = discovery.build(
  "commentanalyzer",
  "v1alpha1",
  developerKey=API_KEY,
  discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
  static_discovery=False,
)

# Succesful Run Message

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
    
    button = Button(label="Delete Message", style=discord.ButtonStyle.green, emoji="🗑️")
    button2 = Button(label="Message Deleted", style=discord.ButtonStyle.green, emoji="✅", disabled=True)
    view = View()
    view.add_item(button)


    button3 = Button(label="Ban", style=discord.ButtonStyle.red, emoji="🔨")
    view2 = View()
    view2.add_item(button3)

    if message.author == client.user:
        return

    usr = message.author
    msg = message.content
    gld = message.guild

    print(msg)
    channel1 = client.get_channel(cid)
    channel2 = message.channel

    analyze_request = {
    'comment': { 'text': msg },
    'requestedAttributes': {'SEVERE_TOXICITY': {}}
    }

    response = ai_client.comments().analyze(body=analyze_request).execute()
    print(response)
    value = response['attributeScores']['SEVERE_TOXICITY']['summaryScore']['value']

    embed2 = discord.Embed(
            title=f'{usr.name} just sent a potentially harmful message',
            description=f"User ID: `{usr.id}`")
    embed2.add_field(name=f"Contents:", value=f"```{msg}```")
    embed2.add_field(name=f"Score:", value=f"```{value}```")
    embed2.add_field(name=f"Channel:", value=f"{channel2.mention}")
    embed2.add_field(name=f"Message Link:", value=f"https://discord.com/channels/{gld.id}/{channel2.id}/{message.id}")

    embed3 = discord.Embed(
            title=f'{usr.name} has gone past the offence limit of 2',
            description=f"User ID: `{usr.id}`")
    embed3.add_field(name=f"Last Message:", value=f"```{msg}```")
    embed3.add_field(name=f"Score:", value=f"```{value}```")
    embed3.add_field(name=f"Offenses:", value="2")
    embed3.add_field(name=f"Message Link:", value=f"https://discord.com/channels/{gld.id}/{channel2.id}/{message.id}")

    async def button_callback(interaction):
      await message.delete()
      view.clear_items()
      view.add_item(button2)
      await interaction.response.edit_message(view = view, embed=embed2)

    button.callback = button_callback

    if value > 0.5:  
        await message.add_reaction('🚩')
        await channel1.send(embed=embed2, view=view)

        # Code for over offenses 
        # await channel1.send(embed=embed3, view=view2)

        value = get_offenses(connection, usr)

        # Gets offenses and checks if ir exists (length is over 0)

        if len(value) > 0:

          # Assigns the number of offenses to a variable 

          ofs = int(value[0][0])

          # Updates offense count based off that variable

          update_offense_count(usr, connection, ofs)
        else:

          # If no offense, adds user to db and assigns a value of 1 offense
          
          insert_new_user(usr, connection)


@client.slash_command(name="settings")
async def settings(ctx):
  await ctx.send("Hi")

  # Enter Code for Settings...
  

@client.slash_command(name="hi")
async def hey(ctx):
  await ctx.send("Hey!!")


client.run(token)

