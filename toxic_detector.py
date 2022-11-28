import discord
from toxic_database import *
from discord.ui import Button, View
from googleapiclient import discovery
from dotenv import load_dotenv
import json
import os

# Getting all secrets

API_KEY = ""
token = ""

#User will need to alter "login_info" to their own desired info
login_info = ["localhost", "root", "0210"] 
db_name = "Discord"


#Initializing database and establishing connection
try:
  connection = create_db_connection(login_info[0], login_info[1], login_info[2], db_name)
  current_settings = fetch_all_setttings_data(connection)
except:
  connection = create_server_connection(login_info[0], login_info[1], login_info[2])
  create_database(connection)
  connection = create_db_connection(login_info[0], login_info[1], login_info[2], db_name)
  create_setting_table(connection)
  create_table(connection)
  current_settings = fetch_all_setttings_data(connection)


# Giving the bot Intents

intents = discord.Intents()
intents.message_content = True
intents.messages = True
intents.guilds = True

client = discord.Bot(command_prefix="+", intents=intents)
mod_channel = 1041513715343818752

# Initializing Perspective API

ai_client = discovery.build(
  "commentanalyzer",
  "v1alpha1",
  developerKey=API_KEY,
  discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
  static_discovery=False,
)

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

# Succesful Run Message

if current_settings == []:
  @client.event
  async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send("""Hello! Thanks for inviting me! 🙏
                                \nTo function properly, I need admins to update my settings! 
                                \nYou can do this by using '/settings'.""")
        break

@client.event
async def on_message(message):
    if int(message.channel.id) != mod_channel and current_settings != []:
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
      channel1 = client.get_channel(current_settings[0][3])
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

      

      async def button_callback(interaction):
        await message.delete()
        view.clear_items()
        view.add_item(button2)
        await interaction.response.edit_message(view = view, embed=embed2)

      button.callback = button_callback

      #Checking if message is too toxic
      sensitivity = current_settings[0][1]
      limit = current_settings[0][2]
      if value >= sensitivity:  
          await message.add_reaction('🚩')
          await channel1.send(embed=embed2, view=view)

          # Gets offenses and checks if it exists
          values = get_offenses(connection, usr)
          if value == []: #if it doesn't exist, it will add user
            insert_new_user(usr, connection)
          else: #if it does exist, it will update the count
            ofs = int(values[0][0])
            update_offense_count(usr, connection, ofs)
          values = get_offenses(connection, usr)
          
          #if user has gone past the limit of offenses, a special message will send to the moderators
          if values[0][0] > limit: 
            embed3 = discord.Embed(
              title=f'{usr.name} has gone past the offence limit of {current_settings[0][2]}',
              description=f"User ID: `{usr.id}`")
            embed3.add_field(name=f"Last Message:", value=f"```{msg}```")
            embed3.add_field(name=f"Score:", value=f"```{value}```")
            embed3.add_field(name=f"Offenses:", value= values[0][0])
            embed3.add_field(name=f"Message Link:", value=f"https://discord.com/channels/{gld.id}/{channel2.id}/{message.id}")
            await channel1.send(embed=embed3, view=view2)
            


@client.slash_command(name="hi")
async def hey(ctx):
  await ctx.send("Hey!!")


@client.slash_command(name = "settings", description = "Use this command to change the bot settings!") 
#for this to work, be sure to add your bot to the mod channel!
async def settings(ctx):
  global current_settings
  if int(ctx.channel_id) == current_settings[0][3]:
    #The following will collect the desired system settings from a moderator
    view = View()
    embed1 = discord.Embed(title = """Please tell me your desired sensitivity of the bot! 
                                    \nThe number inputted should be between 0-1.
                                    \n0 meaning not sensitive to inappropiate messages and 1 being very sensitive.""")
    embed2 = discord.Embed(title = """Please tell me your desired offense limit!
                                    \nThe limit determines how many inappropiate messages you will allow users to send before we notify you.""")
    embed3 = discord.Embed(title = """Please tell me your desired alert channel!
                                    \nThis channel will be used to send moderators alerts about users.""")

    await ctx.send(embed = embed1, view = view)
    view.clear_items()
    msg = await client.wait_for("message")
    new_sense = float(msg.content)

    await ctx.send(embed = embed2, view = view)
    view.clear_items()
    msg = await client.wait_for("message")
    new_limit = int(msg.content)

    await ctx.send(embed = embed3, view = view)
    view.clear_items()
    msg = await client.wait_for("message")
    new_modchannel = int(msg.content)

    serverid = int(ctx.guild.id)

    #The database will update, given that the types are correct
    try:
      current_settings = fetch_all_setttings_data(connection)
      if new_sense <= 0 or new_sense >1: #checking if the sensitivity makes sense
        await ctx.send("There was some kind of error 😢")
      else:
        if current_settings == []:
          insert_server_setting(connection, new_sense, new_limit, new_modchannel, serverid)
        else:
          update_settings(connection, new_sense, new_limit, new_modchannel, serverid)
        await ctx.send("Settings Updated!")
        await ctx.send('😃')
    except:
      await ctx.send("There was some kind of error 😢")
  else: #This will occur if the use of this command didn't occur in the alert channel
    await ctx.send("Permission Denied.")
    await ctx.send('👿')

client.run(token)