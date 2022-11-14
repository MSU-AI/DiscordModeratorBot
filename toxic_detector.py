from toxic_database import *
import discord
from discord.ui import Button, View
from googleapiclient import discovery
import json
import os

API_KEY = ""
token = ""
cid = 1030517807336673320
mid = 1041513715343818752
login_info = ["localhost", "root", "password"] #in the future, I think we can implement some kind of login
db_name = "data"                               # via the database with the settings
creation = False


intents = discord.Intents()
intents.message_content = True
intents.messages = True
intents.guilds = True

if creation == False:
  try:
    connection = create_server_connection(login_info[0], login_info[1], login_info[2])
    create_db(db_name, connection)
    connection = create_db_connection(login_info[0], login_info[1], login_info[2], db_name)
    create_table(connection)
    creation = True
  except:
    creation = False


client = discord.Bot(command_prefix="+", intents=intents)

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

@client.event
async def on_message(message):

    button = Button(label="Delete Message", style=discord.ButtonStyle.green, emoji="🗑️")
    button2 = Button(label="Message Deleted", style=discord.ButtonStyle.green, emoji="✅", disabled=True)
    view = View()
    view.add_item(button)


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


    async def button_callback(interaction):
      await message.delete()
      view.clear_items()
      view.add_item(button2)
      await interaction.response.edit_message(view = view, embed=embed2)
    button.callback = button_callback
    if value > 0.65:  #this is where I made a lot of my changes
        user_data = fetch_user_data(usr, connection)
        mod_channel = client.get(mid)
        if user_data == []:
          insert_new_user(usr, connection)
        else:
          update_offense_count(usr, connection)
        
        user_data = fetch_all_data(usr, connection)
        message_to_mod = """Warning! User {} has commited an offense in a text channel! 
                        \nThey have said: {}. 
                        \nThey have also commited {} offenses. 
                        \nI recommend review over this offense.""".format(usr, msg, user_data[1])
        await message.add_reaction('🚩')
        await channel1.send(embed=embed2, view=view)
        await mod_channel.send(message_to_mod)

    

@client.slash_command(name="hi")
async def hey(ctx):
  await ctx.send("Hey!!")


client.run(token)