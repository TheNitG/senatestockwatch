# Import necessary packages
import os

import discord as discord
from dotenv import load_dotenv
import re
import urllib.request
from datetime import date
import json


today = date.today()


async def build_embed(message, senator):
    # Note: date_recieved is spelled as it is in the .json file
    embed = discord.Embed(title=f'Senator information for {senator["date_recieved"]}',
                          color=discord.Color.blue())

    embed.set_author(name='SenateStockWatch Bot')

    embed.add_field(name='Senator Name', value=f'{senator["first_name"]} {senator["last_name"]}', inline=False)
    embed.add_field(name='Transactions Reported Today', value='#'*20, inline=False)

    transactions = senator['transactions']
    for num, transaction in enumerate(transactions):
        print(transaction)
        ticker = transaction['ticker']
        ticker = 'N/A' if ticker == '--' else ticker[ticker.index('>') + 1:ticker.index('</')]
        embed.add_field(name=f'Transaction {num + 1}: ({transaction["type"]})', value=f'Transaction Date: '
        f'{transaction["transaction_date"]}\nTicker: {ticker} | {re.sub(r" <.*", "", transaction["asset_description"])}'
        f'\nAmount: {transaction["amount"]}', inline=False)
    embed.set_footer(text='Thanks for using SenateStockWatch Bot!')

    await message.channel.send(embed=embed)


async def obtain_data(message, date_use=f'{today.month:02d}_{today.day:02d}_{today.year}'):
    # Declare the URL
    url = f'https://senatestockwatcher.com/data/transaction_report_for_{date_use}' \
          f'.json'
    # Get the page
    data = urllib.request.urlopen(url).read().decode()
    senators_json = json.loads(data)

    for senator in senators_json:
        await build_embed(message, senator)


def pretty_string(data):
    output = ''
    for date, company, ticker, price in data:
        output += f'{date}\t{ticker}\t{price}\n'
    return output[:-2]


load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

client = discord.Client()


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.idle, activity=discord.Game("Listening to !help"))
    print(f'{client.user.name} has connected to Discord!')


@client.event
async def on_message(message):
    content = message.content
    if re.search(r'^!today$', content):
        try:
            await obtain_data(message)
        except:
            await message.channel.send('No data for today as of right now')
    elif re.search(r'^!day \d{1,2}/\d{1,2}/\d{4}$', content):
        try:
            day_parts = content[5:].split('/')
            day = f'{int(day_parts[0]):02d}_{int(day_parts[1]):02d}_{int(day_parts[2])}'
            await obtain_data(message, day)
        except:
            await message.channel.send(f'No data for {content[5:]} as of right now')


client.run(TOKEN)
