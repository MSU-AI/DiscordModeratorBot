import discord
from discord.ui import Button, View
from googleapiclient import discovery
import json
import os

API_KEY = ""
token = ""

intents = discord.Intents()
intents.message_content = True
intents.messages = True
intents.guilds = True

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
    if value > 0.65:
        await message.add_reaction('🚩')
        await channel1.send(embed=embed2, view=view)    
    

@client.slash_command(name="hi")
async def hey(ctx):
  await ctx.send("Hey!!")


client.run(token)

