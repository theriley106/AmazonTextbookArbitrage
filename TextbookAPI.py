import threading
import random
import requests
import RandomHeaders
import bs4
import time
import csv
proxies = {
	
}
def get_dec(x):
	a = (float(''.join(ele for ele in x if ele.isdigit() or ele == '.')))
	a = float("{0:.2f}".format(a))
	return a
def AmazonTrade(Keywords, CSV=False, Debug=0):
	Information = []
	URLs = []
	for keyword in Keywords:
		for i in range(1,75):
			URLs.append('https://www.amazon.com/s/ref=sr_pg_{}?srs=9187220011&fst=as%3Aoff&rh=n%3A283155%2Ck%3Atextbooks&page={}&keywords={}'.format(i, i, str(keyword)))
	def NewURL(URLs):
		try:
			url = random.choice(URLs)
			URLs.remove(url)
			return str(url)
		except BaseException as exp:
			if Debug > 1:
				print(exp)
			pass
	def TradeFromHTML(colorprice):
		a = (float(''.join(ele for ele in colorprice if ele.isdigit() or ele == '.')))
		a = float("{0:.2f}".format(a))
		return a
	def DownloadPage(URLs):
		URL = NewURL(URLs)
		for tries in range(3):
			try:
				res = requests.get(URL, headers=RandomHeaders.LoadHeader(), proxies=proxies)
				print(URL)
				page = bs4.BeautifulSoup(res.text, "lxml")
				break
			except BaseException as exp:
				if Debug > 1:
					print(exp)
				pass
		return page
	def ConvertPageToNumbers(page):
		items = page.select('.s-item-container')
		for item in items:
			TIV = TradeFromHTML(str(item.select('.a-color-price')))
			item = str(item).partition('ISBN-10:')[2]
			item = str(item).partition('left;"><span class="a-size-small a-color-secondary">')[2]
			ASIN = str(item).partition('</span></div>')[0]
			Information.append([ASIN, TIV])
	def RemoveDuplicate(rawlist):
		#2 Part List Only
		NewList = []
		for Contents in rawlist:
			if Contents not in NewList:
				NewList.append(Contents)
		return NewList
	def RemoveCheapBooks(rawlist, price):
		NewerList = []
		for Contents in rawlist:
			if Contents[1] > price:
				NewerList.append(Contents)
		return NewerList
	def Scrape(URLs):
		while len(URLs) > 0:
			try:
				Page = DownloadPage(URLs)
				ConvertPageToNumbers(Page)
			except BaseException as exp:
				if Debug > 1:
					print(exp)
				pass
	threads = [threading.Thread(name='worker{}'.format(n), target=Scrape, args=([URLs])) for n in range(10)]
	for t in threads: t.start()
	for t in threads: t.join()
	Information = RemoveDuplicate(Information)
	Information = RemoveCheapBooks(Information, 50)
	if CSV != False:
		with open(CSV, "wb") as f:
			writer = csv.writer(f)
			writer.writerows(Information)
	return Information





def Biblio(ListOfASIN, CSV=False, Debug=0):
	Information = []
	def TradeFromHTML(colorprice):
		a = (float(''.join(ele for ele in colorprice if ele.isdigit() or ele == '.')))
		a = float("{0:.2f}".format(a))
		return a
	def GenerateURL(ListOfASIN):
		try:
			Asin = random.choice(ListOfASIN)
			Url = 'http://www.biblio.com/search.php?stage=1&pageper=50&country=1&omit_product_types=bp,bd,ns&keyisbn={}&strip_common=1&program=1005&order=price_ship_usasc'.format(Asin)
			ListOfASIN.remove(Asin)
			return [str(Url), str(Asin)]
		except BaseException as exp:
			if Debug > 1:
				print(exp)
			pass
	def DownloadPage(ListOfASIN):
		URL = GenerateURL(ListOfASIN)
		Asin = URL[1]
		URL = URL[0]
		for tries in range(3):
			try:
				res = requests.get(URL, headers=RandomHeaders.LoadHeader(), proxies=proxies)
				print(URL)
				page = bs4.BeautifulSoup(res.text, "lxml")
				break
			except BaseException as exp:
				if Debug > 1:
					print(exp)
				pass
		
		return [page, Asin]
	def ConvertPageToNumbers(page, Asin):
		Price = TradeFromHTML(str(str(page.select('.ob-price')[0]).partition('Price: <span class="price">')[2]).partition(' </span>\n</h3>\n<span class="shipping"')[0])
		Shipping = TradeFromHTML(str(str(page.select('.ob-price')[0]).partition('"shipping">Shipping (US): </span>')[2]))
		Price = round(Price + Shipping, 2)
		Information.append([Asin, Price])
	def Scrape(ListOfASIN):
		while len(ListOfASIN) > 0:
			try:
				Data = DownloadPage(ListOfASIN)
				page = Data[0]
				Asin = Data[1]
				ConvertPageToNumbers(page, Asin)
			except BaseException as exp:
				if Debug > 0:
					print(exp)
					time.sleep(1)
				pass

	if hasattr(ListOfASIN, 'lower'): 
		#Determines if the user inputted a string or list
		ListOfASIN = [ListOfASIN]

	threads = [threading.Thread(name='worker{}'.format(n), target=Scrape, args=([ListOfASIN])) for n in range(10)]
	for t in threads: t.start()
	for t in threads: t.join()
	if CSV != False:
		with open(CSV, "wb") as f:
			writer = csv.writer(f)
			writer.writerows(Information)
	return Information


def Half(ListOfASIN, CSV=False, Debug=0):
	Information = []
	def TradeFromHTML(colorprice):
		a = (float(''.join(ele for ele in colorprice if ele.isdigit() or ele == '.')))
		a = float("{0:.2f}".format(a))
		return a
	def GenerateURL(ListOfASIN):
		try:
			Asin = random.choice(ListOfASIN)
			Url = 'http://search.half.ebay.com/{}'.format(Asin)
			ListOfASIN.remove(Asin)
			return [str(Url), str(Asin)]
		except BaseException as exp:
			if Debug > 1:
				print(exp)
			pass
	def DownloadPage(ListOfASIN):
		URL = GenerateURL(ListOfASIN)
		Asin = URL[1]
		URL = URL[0]
		for tries in range(3):
			try:
				res = requests.get(URL, headers=RandomHeaders.LoadHeader(), proxies=proxies)
				print(URL)
				page = bs4.BeautifulSoup(res.text, "lxml")
				break
			except BaseException as exp:
				if Debug > 1:
					print(exp)
				pass
		
		return [page, Asin]
	def ConvertPageToNumbers(page, Asin):
		halfprices = []
		re = page.select('.PDP_itemList')
		for tables in re:
			price = TradeFromHTML(tables.select('.tr-border td')[0].getText())
			halfprices.append([price])
		halfprices.sort()
		Price = halfprices[0]
		Price = round((Price[0] + 3.49),2)
		Information.append([Asin, Price])
	def Scrape(ListOfASIN):
		while len(ListOfASIN) > 0:
			try:
				Data = DownloadPage(ListOfASIN)
				page = Data[0]
				Asin = Data[1]
				ConvertPageToNumbers(page, Asin)
			except BaseException as exp:
				if Debug > 0:
					print(exp)
					time.sleep(1)
				pass

	if hasattr(ListOfASIN, 'lower'): 
		#Determines if the user inputted a string or list
		ListOfASIN = [ListOfASIN]

	threads = [threading.Thread(name='worker{}'.format(n), target=Scrape, args=([ListOfASIN])) for n in range(10)]
	for t in threads: t.start()
	for t in threads: t.join()
	if CSV != False:
		with open(CSV, "wb") as f:
			writer = csv.writer(f)
			writer.writerows(Information)
	return Information
