import discord
from googleapiclient import discovery
import json
import os

API_KEY = ''

intents = discord.Intents()
intents.message_content = True
intents.messages = True

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
    if message.author == client.user:
        return

    msg = message.content
    print(msg)
    
    analyze_request = {
    'comment': { 'text': msg },
    'requestedAttributes': {'SEVERE_TOXICITY': {}}
    }
    response = ai_client.comments().analyze(body=analyze_request).execute()
    print(response)
    value = response['attributeScores']['SEVERE_TOXICITY']['summaryScore']['value']
    print(value)
    if value > 0.6:
        await message.channel.send("That was kinda rude, please calm down.")
    

@client.slash_command(name="hi")
async def hey(ctx):
  await ctx.send("Hey!!")


client.run('')
