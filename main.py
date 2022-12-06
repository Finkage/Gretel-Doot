import os
import discord
from discord.ext import commands
import datetime
import asyncio


bot = commands.Bot(command_prefix='!', intents = discord.Intents(value = 268568656))

# Store the alarms in a list
alarms = []

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command()
async def setalarm(ctx, time, *, role):
    # Convert the time string to a datetime object
    alarm_time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')

    # Check if the given role exists in the guild
    role_obj = discord.utils.get(ctx.guild.roles, name=role)
    if not role_obj:
        await ctx.send(f'Error: Role "{role}" does not exist.')
        return

    # Add the alarm to the list
    alarms.append({'time': alarm_time, 'role': role_obj})

    # Start a new task to run the alarm
    asyncio.create_task(run_alarm(alarm_time, role_obj))

@bot.command()
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

@bot.command()
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

async def run_alarm(alarm_time, role):
    # Set up a while loop that runs until the alarm time is reached
    while True:
        # Calculate the time difference between now and the alarm time
        time_difference = alarm_time - datetime.datetime.now()

        # If the alarm time has been reached, ping the role and break the loop
        if time_difference.total_seconds() <= 0:
            await ctx.send(f'@{role}')
            break

        # Sleep for one day, then check again
        await asyncio.sleep(24 * 60 * 60)

bot.run(os.environ['TOKEN'])