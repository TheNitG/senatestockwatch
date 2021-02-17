# Import necessary packages
import os

import cfscrape
import discord as discord
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import re


def map_senators(dates, names, companies, tickers, prices):
    senators = {}
    for x in range(len(names)):
        name = names[x]
        if name in senators:
            senators[name].append([dates[x], companies[x], tickers[x], prices[x]])
        else:
            senators[name] = [[dates[x], companies[x], tickers[x], prices[x]]]
    return senators


def obtain_data():
    scraper = cfscrape.create_scraper()  # returns a CloudflareScraper instance
    # Declare the URL
    URL = "https://sec.report/Senate-Stock-Disclosures"
    # Declare Browser
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.27 Safari/537.36"
    headers = {'User-Agent': user_agent}
    # Get the page
    page = scraper.get(URL, headers=headers)
    # Use BeautifulSoup package to parse as html
    soup = BeautifulSoup(page.content, 'html.parser')

    contents = soup.prettify()

    dates = re.findall(r'\d{4}-\d\d-\d\d', contents)
    names_reversed = re.findall(r'\[\w+, \w+]', contents)
    names = []
    for name in names_reversed:
        name_contents = name.replace('[', '').replace(']', '').split(', ')
        names.append(name_contents[1] + ' ' + name_contents[0])
    companies = [x.replace('/CIK/Search/', '').replace('+', ' ') for x in
                 re.findall(r'/CIK/Search/(?:\w+\+)+', contents)]
    tickers = [x.replace('/Ticker/', '') for x in re.findall(r'/Ticker/\w+', contents)]
    prices = re.findall(r'\$\d+(?: - \$\d+)?', contents.replace(',', ''))
    return dates, names, companies, tickers, prices


def pretty_string(data):
    output = ''
    for date, company, ticker, price in data:
        output += f'{date}\t{ticker}\t{price}\n'
    return output[:-2]


load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

client = discord.Client()

date_list, name_list, company_list, ticker_list, price_list = obtain_data()
senator_map = map_senators(date_list, name_list, company_list, ticker_list, price_list)


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.idle, activity=discord.Game("Listening to s!help"))
    print(f'{client.user.name} has connected to Discord!')


@client.event
async def on_message(message):
    content = message.content
    if re.search(r'^s!senators$', content):
        await message.channel.send('\n'.join(set(name_list)))
    elif re.search(r'^s!s.+$', content):
        target = ' '.join([x.capitalize() for x in content[4:].lower().split(' ')])
        print(target)
        if target in senator_map:
            await message.channel.send(target + ':\n```' + pretty_string(senator_map[target]) + '```')
        else:
            await message.channel.send('No senator found, please try again.')


client.run(TOKEN)

