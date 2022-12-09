import os
import discord
from discord.ext import tasks, commands
import pytz
from datetime import datetime

# Set up the intents with a value of 268568656
intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.message_content = True
intents.messages = True
intents.reactions = True

gretelDoot = commands.Bot(command_prefix='!', intents = intents)

@tasks.loop(minutes=1)
async def ping_roles():
    # get the current time in PST
    tz = pytz.timezone('America/Los_Angeles')
    now = datetime.now(tz)

    # get the guild by its name
    guild = gretelDoot.get_guild(1049599729970987018)#discord.utils.get(gretelDoot.guilds, name="1049599729970987018")

    # get the channel by its name
    channel = gretelDoot.get_channel(1049599729970987021)
    
    # ping "colo" role at 12:55 and 12:57 in PST
    if now.hour in [12, 17] and now.minute in [28, 55, 57]:
        role = discord.utils.get(guild.roles, name="colo")
        await role.edit(mentionable=True)
        await channel.send(f"Ping! {role.mention}")
        await role.edit(mentionable=False)

    # ping "conquest" role at 00:30, 3:30, 7:30, 9:30, 11:30, 13:30, 15:30, 17:30, 19:30 in PST
    if now.hour in [0, 3, 7, 9, 11, 13, 15, 17, 19] and now.minute == 30:
        role = discord.utils.get(guild.roles, name="conquest")
        await role.edit(mentionable=True)
        await channel.send(f"Ping! {role.mention}")
        await role.edit(mentionable=False)

@gretelDoot.event
async def on_ready():
    print('Logged in as')
    print(gretelDoot.user.name)
    print(gretelDoot.user.id)
    print('------')

    # start the ping_roles loop
    ping_roles.start()

gretelDoot.run(os.environ['TOKEN'])