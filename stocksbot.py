# Reddit bot made for /r/stocks.  Summon with '$' followed by the ticker symbol.  
# Created by /u/chuiy

#import Python Reddit API Wrapper
import humanize
import socket
from threading import Lock
import praw
from praw import *
#Allows us to print from a dictionary
from pprint import pprint
import time
import os.path
import ystockquote
from requests import *
from bs4 import BeautifulSoup

alreadyDone = open('done.txt', 'a+')

user_agent = "/u/StocksBot created by /u/chuiy"

r = praw.Reddit(user_agent=user_agent)
r.login('stocksBot', 'bosox1')
ownName = "stocksBot"

while True:
	try:
		sub = r.get_subreddit('stocksBot')
		#set subReddit
		comments = praw.helpers.comment_stream(r, sub, limit=200) 
		#Retrieves 200 comments from the subReddit
		for comment in comments:
			if "$$" in comment.body and comment.id not in alreadyDone.read() and comment.author.name != ownName:
			#if /u/stocksBot finds $$ in the post, the comment is new, and the name does not match ours
				position = comment.body.index('$')
				#find position of first $.  Temporary hack.
				start = position + 2 #find first character of ticker symbol
				end = start + 4 #find last character
				symbolList = []
				for letter in comment.body[start:end]:
					symbolList.append(letter)
				
				symbol = ''.join(str(e) for e in symbolList if e.isalpha()) #turn list of letters in symbol into string
				symbol.strip()
				
				summaryPage = requests.get('http://finance.yahoo.com/q/pr?s=' + symbol, stream=False)				
				
				d = summaryPage.content
				soup1 = BeautifulSoup(d)

				getSummary = soup1.find_all('p')

				price = str(ystockquote.get_price(symbol))
				change = str(ystockquote.get_change(symbol))
				volume = str(ystockquote.get_volume(symbol))
				stockExchange = str(ystockquote.get_stock_exchange(symbol))
				marketCap = str(ystockquote.get_market_cap(symbol))
				bValue = str(ystockquote.get_book_value(symbol))
				ebitda = str(ystockquote.get_ebitda(symbol))
				mvavg = str(ystockquote.get_200day_moving_avg(symbol))
				High = str(ystockquote.get_52_week_high(symbol))
				Low = str(ystockquote.get_52_week_low(symbol))
				
				commaData = []

				data=[price, change, volume, stockExchange, mvavg, bValue, ebitda, marketCap, High, Low]		


				for individData in data:
					commaInt = humanize.intcomma(individData)
					commaData.append(commaInt)
				
				if float(price) > 0.00:
			
					try:
						stockInfo = ('\n'
						'**'+symbol+'**\n'
						''+stockExchange+'\n'
						'\n'
						'Price | Volume  |  Book Data | 200 day moving avg\n'
						':--:|:--:|:--:|:--:|\n'
						'  $'+commaData[0]+' |  '+commaData[2]+'  |  $'+commaData[5]+'|  $'+commaData[4]+' \n'
'\n'
						'EBITDA | Market Cap  |  52 Week High | 52 Week Low\n'
                                        	':--:|:--:|:--:|:--:|\n'
                                        	'  $'+commaData[6]+' |  $'+commaData[7]+'  |  $'+commaData[8]+'|  $'+commaData[9]+' \n'
                                        	'\n'

						'**Brief Summary**\n\n'
						''+ getSummary[1].text[:450] + '..\n\n'
						'Hi, I\'m /u/stocksBot. Summon me with "$$" immeditely followed by the ticker symbol and I will reply with information about the stock.  \n\n'
						'Created by /u/chuiy.  |  Contribute on GitHub')
	
						alreadyDone.write(comment.id)
						#add comment.id to the set alreadyDone
						comment.reply(stockInfo) #reply to the comment
						time.sleep(15) #wait five minutes, prevents raising praw.errors.RateLimitExceeded
					except BaseException:
						#couldNotFind = (
						#'Sorry, I could not find information for the symbol you provided.  If you believe this is an error, contact /u/chuiy.'
						#)
						alreadyDone.write(comment.id)
						#comment.reply(couldNotFind)
				
				else:
					alreadyDone.write(comment.id)
	except praw.errors.RateLimitExceeded as error:
		print("Sleeping %d seconds" % error.sleep_time)
		time.sleep(error.sleep_time)




