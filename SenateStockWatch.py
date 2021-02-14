# Import necessary packages
import requests
from bs4 import BeautifulSoup
import re


# Declare the URL
URL = "https://sec.report/Senate-Stock-Disclosures"
# Declare Browser
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.27 Safari/537.36"
headers = {'User-Agent': user_agent}
# Get the page
page = requests.get(URL, headers=headers)
# Use BeautifulSoup package to parse as html
soup = BeautifulSoup(page.content, 'html.parser')

result = str(soup.find_all(lambda tag: tag.name == 'a' and tag.get('href') and tag.text))
contents = soup.prettify()

dates = re.findall(r'\d{4}-\d\d-\d\d', contents)
names_reversed = re.findall(r'\[\w+, \w+]', contents)
names = []
for name in names_reversed:
    name_contents = name.replace('[', '').replace(']', '').split(', ')
    names.append(name_contents[1] + ' ' + name_contents[0])
companies = [x.replace('/CIK/Search/', '').replace('+', ' ') for x in re.findall(r'/CIK/Search/(?:\w+\+)+', contents)]
tickers = [x.replace('/Ticker/', '') for x in re.findall(r'/Ticker/\w+', contents)]
prices = re.findall(r'\$\d+(?: - \$\d+)?', contents.replace(',', ''))

print(dates)
print(names)
print(companies)
print(tickers)
print(prices)
