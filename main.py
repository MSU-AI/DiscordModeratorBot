import discord
from toxic_database import *
from toxic_detector import *
from question_detection import *
from discord.ui import Button, View
from googleapiclient import discovery
from dotenv import load_dotenv
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
    connection = create_server_connection(login_info[0], login_info[1], login_info[2])
    create_database(connection)
    connection = create_db_connection(login_info[0], login_info[1], login_info[2], db_name)
    create_setting_table(connection)
    create_table(connection)
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
  current_settings = fetch_all_setttings_data(connection)

  if message.author == client.user:
      return

  msg = message.content
  channel = message.channel
  value = analyze_msg(ai_client, msg)
  
  print(f"Is it a question: {is_question(msg)}")
  
  if is_question(msg) and value < 0.5:
    await execute_operations2(client, message)
  else:
    await execute_operation(client, ai_client, message, connection, current_settings, current_settings[0][3])

  


@client.slash_command(name = "settings", description = "Use this command to change the bot settings!") 
#for this to work, be sure to add your bot to the mod channel!
async def settings(ctx):
  current_settings = fetch_all_setttings_data(connection)
  if ctx.author.guild_permissions.administrator:
    #The following will collect the desired system settings from a moderator
    view = View()
    embed1 = discord.Embed(title = "Please set the desired bot sensitivity!")
    embed1.add_field(name=f"Sensitivity:", value=f"`Not set`")
    embed1.add_field(name=f"Offense Limit:", value=f"`Not set`")
    embed1.add_field(name=f"Alert Channel:", value=f"#Not set")
    embed1.add_field(name="""The number inputted should be between 0-1.\n0 being not sensitive to inappropiate messages and 1 being very sensitive.""", value="** **")

    await ctx.respond(embed = embed1, view = view)
    view.clear_items()
    msg = await client.wait_for("message")
    new_sense = float(msg.content)

    embed2 = discord.Embed(title = "Please set the desired offense limit!")
    embed2.add_field(name=f"Sensitivity:", value=f"`{new_sense}`")
    embed2.add_field(name=f"Offense Limit:", value=f"`Not set`")
    embed2.add_field(name=f"Alert Channel:", value=f"#Not set")
    embed2.add_field(name="The limit determines how many inappropiate messages you will allow users to send before we notify you.", value="** **")

    await ctx.respond(embed = embed2, view = view)
    view.clear_items()
    msg = await client.wait_for("message")
    new_limit = int(msg.content)

    embed3 = discord.Embed(title = "Please set the desired alert channel!")
    embed3.add_field(name=f"Sensitivity:", value=f"`{new_sense}`")
    embed3.add_field(name=f"Offense Limit:", value=f"`{new_limit}`")
    embed3.add_field(name=f"Alert Channel:", value=f"#Not set")
    embed3.add_field(name="This channel will be used to send moderators alerts about users.\nEnter the Channel ID.", value="** **")

    await ctx.respond(embed = embed3, view = view)
    view.clear_items()
    msg = await client.wait_for("message")
    new_modchannel = int(msg.content)

    embed4 = discord.Embed(title = "Settings Updated!! 😃")
    embed4.add_field(name=f"Sensitivity:", value=f"`{new_sense}`")
    embed4.add_field(name=f"Offense Limit:", value=f"`{new_limit}`")
    embed4.add_field(name=f"Alert Channel:", value=f"<#{new_modchannel}>")

    serverid = int(ctx.guild.id)

    #The database will update, given that the types are correct
    try:
      current_settings = fetch_all_setttings_data(connection)
      if new_sense <= 0 or new_sense >1: #checking if the sensitivity makes sense
        await ctx.respond("There was some kind of error 😢")
      else:
        if current_settings == []:
          insert_server_setting(connection, new_sense, new_limit, new_modchannel, serverid)
        else:
          update_settings(connection, new_sense, new_limit, new_modchannel, serverid)
        await ctx.respond(embed=embed4)
    except:
      await ctx.respond("There was some kind of error 😢")
  else: #This will occur if the use of this command didn't occur in the alert channel
    await ctx.respond("Permission Denied. 👿")
  

@client.slash_command(name="hi")
async def hey(ctx):
  await ctx.send("Hey!!")


client.run(token)

