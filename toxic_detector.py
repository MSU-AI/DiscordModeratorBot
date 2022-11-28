import discord
from discord.ui import Button, View
from googleapiclient import discovery
from toxic_database import *

def analyze_msg(ai_client, msg):
    analyze_request = {
    'comment': { 'text': msg },
    'requestedAttributes': {'SEVERE_TOXICITY': {}}
    }
    response = ai_client.comments().analyze(body=analyze_request).execute()
    print(response)
    value = response['attributeScores']['SEVERE_TOXICITY']['summaryScore']['value']
    return value

def construct_buttons():
    button = Button(label="Delete Message", style=discord.ButtonStyle.green, emoji="🗑️")
    button_v2 = Button(label="Message Deleted", style=discord.ButtonStyle.green, emoji="✅", disabled=True)
    button2 = Button(label="Forgive", style=discord.ButtonStyle.green, emoji="🥺")
    button2_v2 = Button(label="Forgiven", style=discord.ButtonStyle.green, emoji="✅", disabled=True)
    view = View()
    view.add_item(button)
    view.add_item(button2)

    button4 = Button(label="Ban", style=discord.ButtonStyle.red, emoji="🔨")
    button5 = Button(label="Kick", style=discord.ButtonStyle.red, emoji="🦶")
    button6 = Button(label="Mute", style=discord.ButtonStyle.red, emoji="🔇")
    view2 = View()
    view2.add_item(button6)
    view2.add_item(button5)
    view2.add_item(button4)
    return button, button_v2, button2, button2_v2, button4, view, view2

def construct_embeds(usr, channel2, message, msg, value, gld, ofs, limit):
    embed2 = discord.Embed(
            title=f'{usr.name} just sent a potentially harmful message',
            description=f"User ID: `{usr.id}`")
    embed2.add_field(name=f"Contents:", value=f"```{msg}```")
    embed2.add_field(name=f"Score:", value=f"```{value}```")
    embed2.add_field(name=f"Number of Offenses:", value=f"```{ofs+1}```")
    embed2.add_field(name=f"Channel:", value=f"{channel2.mention}")
    embed2.add_field(name=f"Message Link:", value=f"https://discord.com/channels/{gld.id}/{channel2.id}/{message.id}")

    embed3 = discord.Embed(
            title=f'{usr.name} has hit the offence limit of {limit}',
            description=f"User ID: `{usr.id}`")
    embed3.add_field(name=f"Last Message:", value=f"```{msg}```")
    embed3.add_field(name=f"Score:", value=f"```{value}```")
    embed3.add_field(name=f"Offenses:", value=f"{ofs+1}")
    embed3.add_field(name=f"Message Link:", value=f"https://discord.com/channels/{gld.id}/{channel2.id}/{message.id}")

    return embed2, embed3

async def execute_operation(client, ai_client, message, connection, current_settings, cid):
    usr = message.author
    msg = message.content
    channel1 = client.get_channel(cid)
    gld = message.guild
    channel2 = message.channel

    print(msg)

    value = analyze_msg(ai_client, msg)

    offense = get_offenses(connection, usr)
    if len(offense) > 0:
        ofs = int(offense[0][0])
    else:
        ofs = 0

    sensitivity = current_settings[0][2]
    limit = current_settings[0][1]
    print(f"The LIMIT IS {limit}")
    print(f"The number of OFS is {ofs}")

    embed2, embed3 = construct_embeds(usr, channel2, message, msg, value, gld, ofs, limit)
    button, button_v2, button2, button2_v2, button4, view, view2 = construct_buttons()

    
    async def button_callback(interaction):
        await message.delete()
        view.remove_item(button)
        view.add_item(button_v2)
        await interaction.response.edit_message(view = view, embed=embed2)

    async def button_callback2(interaction):
        sub_offense_count(usr, connection, ofs)
        view.remove_item(button2)
        view.add_item(button2_v2)
        await interaction.response.edit_message(view = view, embed=embed2)

    async def button_callback3(interaction):
        usr.ban()
        await interaction.response.edit_message(view = view2, embed=embed3)

    button2.callback = button_callback2
    button.callback = button_callback
    button4.callback = button_callback3

    if value >= sensitivity:
        if len(offense) > 0:
            add_offense_count(usr, connection, ofs)
        else: 
            insert_new_user(usr, connection)

        await message.add_reaction('🚩')
        await channel1.send(embed=embed2, view=view)

        if ofs+1 >= limit:
            await channel1.send(embed=embed3, view=view2)
        
        