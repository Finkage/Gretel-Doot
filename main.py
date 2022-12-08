import os
import discord
from discord.ext import commands
import datetime
import asyncio

# Set up the intents with a value of 268568656
intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.message_content = True
intents.messages = True
intents.reactions = True

# Create the bot, set the command prefix, and set the intents
bot = commands.Bot(command_prefix='!', intents = intents)

# Store the alarms in a list
alarms = []

# reads alarms from list and stores them into alarms[]
async def read_alarms_from_file():
    # Open the alarms.txt file in read mode
    with open('alarms.txt', 'r') as f:
        # Iterate over the lines in the file
        for line in f:
            # Parse the alarm time and role from the line
            time_str, role_str = line.strip().split(' ')
            time = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M')
            role = discord.utils.get(bot.guild.role, name=role_str)

            # Create a new alarm dictionary and add it to the alarms list
            alarms.append({'time': time, 'role': role})

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

    # Read the alarms from the file
    await read_alarms_from_file()

# writes all alarms and roles associated from alarms[] to alarms.txt
async def write_alarms_to_file():
    # Open the alarms.txt file in write mode
    with open('alarms.txt', 'w') as f:
        # Iterate over the alarms and write them to the file
        for alarm in alarms:
            f.write(f"{alarm['time']} {alarm['role']}\n")

# primary command for setting alarms to go off
@bot.command(usage='!setalarm <time> <role>')
async def setalarm(ctx, time, *, role):
    # Convert the time string to a datetime object
    alarm_time = datetime.datetime.strptime(time, '%Y-%m-%d-%H:%M')

    # Check if the given role exists in the guild
    role_obj = discord.utils.get(ctx.guilds, name=role)
    if not role_obj:
        await ctx.send(f'Error: Role "{role}" does not exist.')
        return

    # Add the alarm to the list
    alarms.append({'time': alarm_time, 'role': role_obj})

    # Write the alarms to the file
    await write_alarms_to_file()

    # Start a new task to run the alarm
    asyncio.create_task(run_alarm(ctx, alarm_time, role_obj))


# THIS IS NOT FULLY FUNCTIONAL, JUST DELETES FROM LIST, NOT FROM TASKS
@bot.command(usage='!deletealarm <time>')
async def deletealarm(ctx, time):
    # Convert the time string to a datetime object
    alarm_time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')

    # Find the alarm in the list and delete it
    for alarm in alarms:
        if alarm['time'] == alarm_time:
            alarms.remove(alarm)
            await ctx.send(f'Alarm at {time} deleted.')
            return

    # If the alarm is not found, send an error message
    await ctx.send(f'Error: Alarm at {time} not found.')

# allows for alarms to be adjusted come DST changes !!!! NEEDS TO BE FIXED TO REFLECT THIS CHANGE IN RUNNING TASKS
@bot.command(usage='!adjustalarms <forward/backward>')
async def adjustalarms(ctx, direction):
    # Check if the direction is "forward" or "backward"
    if direction != 'forward' and direction != 'backward':
        await ctx.send('Error: Invalid direction. Must be "forward" or "backward".')
        return

    # Iterate through the alarms and adjust the time by one hour
    for alarm in alarms:
        if direction == 'forward':
            alarm['time'] += datetime.timedelta(hours=1)
        elif direction == 'backward':
            alarm['time'] -= datetime.timedelta(hours=1)

    # Send a message confirming that the alarms have been adjusted
    await ctx.send(f'All alarms adjusted {direction} one hour.')


# primary tast that runs the alarm routine
async def run_alarm(ctx, alarm_time, role):
    # Set up a while loop that runs until the alarm time is reached
    while True:
        # Calculate the time difference between now and the alarm time
        #print(str(alarm_time) + f'' + str(datetime.datetime.now()) + f'')
        time_difference = alarm_time - datetime.datetime.now()
        #print(str(time_difference) + f'')

        # If the alarm time has been reached, ping the role, add one day to the alarm time, sleep for one day, and then check again. If the alarm is in the past, adjust so that it is in the future then continue the task as normal.
        if -10 <= time_difference.total_seconds() <= 0:
            await ctx.send(f'@{role}')
            alarm_time += datetime.timedelta(days=1)
            await asyncio.sleep(24 * 60 * 60)
        elif time_difference.total_seconds() < -10:
            alarm_time += datetime.timedelta(days=1)

@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)

bot.run(os.environ['TOKEN'])