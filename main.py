import requests
import bs4
import threading
import re
import RandomHeaders
import random

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
#AMAZON_URL = "https://www.amazon.com/s/search-alias%3Dtradein-aps&field-keywords={0}&page={1}"
AMAZON_URL = "https://www.amazon.com/s/ref=sr_nr_i_0?srs=9187220011&fst=as%3Aoff&rh=i%3Atradein-aps%2Ck%3A{0}%2Ci%3Astripbooks&page={1}"
USED_PRICE_URL = "https://www.amazon.com/gp/offer-listing/{0}/ref=dp_olp_used?ie=UTF8&condition=used"
ALL_PAGE = "https://www.amazon.com/gp/offer-listing/{0}/ref=olp_f_new?ie=UTF8&f_all=true&f_new=true&f_used=true"
ITEM_SELECTOR = ".s-item-container"
TRADE_IN_SELECTOR = ".a-color-price"
ITEM_SPECIFICS = ".a-text-left.a-col-right"
# Page count = [0], Publisher = [1], ISBN-100 = [2], ISBN-13 = [3]
BOOK_TITLE = ".s-access-title"
BOOK_COVER = ".cfMarker"
TRADE_IN_REVIEW_BOX = ".a-span-last"
THREADS = 10
try:
	proxy = open("proxyAddress.txt").read().strip()
except:
	raise Exception("Proxy not defined")
proxy = {}
proxyStatus = {}

def chunks(l, n):
	for i in xrange(0, len(l), n):
		yield l[i:i + n]

def isTradeInEligible(item):
	# Determines if the item is trade in eligible or not
	return ('tradein' in item.select(TRADE_IN_REVIEW_BOX)[0])

def extractAllPageInfo(asin):
	info = {}
	url = ALL_PAGE.format(asin)
	page = grabPage(url)
	offer = page.select(".olpOffer")[0]
	try:
		info['comment'] = offer.select('.expandedNote')[0].getText().strip().partition("\n")[0]
	except:
		info['comment'] = offer.select(".comments")[0].getText().strip().partition("\n")[0]
	info['sellerName'] = offer.select(".olpSellerName")[0].getText().strip()
	sellerColumn = offer.select(".olpSellerColumn")
	info['percentRating'] = sellerColumn[0].select("b")[0].getText().strip()
	info['totalRatings'] = int(''.join(re.findall("\d+", str(sellerColumn[0].select(".a-spacing-small")[0].getText()).partition("(")[2].partition(")")[0])))
	info['arrivalDate'] = offer.select(".a-expander-partial-collapse-content")[0].getText().strip()
	return info

def getPageCount(page):
	try:
		pageCount = int(page.select(".pagnDisabled")[0].getText())
	except:
		try:
			pageCount = int(re.findall("(\d+)", str(page.select("#pagn")[0].getText().replace("\n", " ")))[-1])
		except:
			pageCount = 1
	return pageCount

def extractPrice(itemID):
	try:
		page = grabPage(USED_PRICE_URL.format(itemID))
		offer = page.select(".olpOffer")[0]
		price = float(offer.select(".olpOfferPrice")[0].getText().replace("$", ""))
		try:
			shipping = float(offer.select(".olpShippingPrice")[0].getText().replace("$", ""))
		except:
			shipping = 0
		return price + shipping
	except:
		print("Error returning 1000...")
		return 1000

def grabPage(url):
	for i in range(10):

		proxies = {"http": proxy, "https": proxy}
		try:
			res = requests.get(url, headers=RandomHeaders.LoadHeader(), proxies=proxies, timeout=10)
		except Exception as exp:
			res = None
		if res != None:
			break
	page = bs4.BeautifulSoup(res.text, 'lxml')
	try:
		pageNum = re.findall('page\S(\d+)', url)[0]
	except:
		pageNum = 1
	print("Grabbed: {} | Page: {}".format(page.title.string, pageNum))
	return page

def extractInfoFromItem(item):
	try:
		tempInfo = {}
		tempInfo['title'] = item.select(BOOK_TITLE)[0].getText()
		tempInfo['item_id'] = str(item.select(".s-access-detail-page")[0]).partition('/dp/')[2].partition("/")[0]
		tempInfo['item_url'] = "https://www.amazon.com/dp/" + tempInfo['item_id']
		tempInfo['cover'] = str(item.select(BOOK_COVER)[0]).partition('src="')[2].partition('"')[0]
		tempInfo['page_count'] = item.select(ITEM_SPECIFICS)[0].getText()
		tempInfo['publisher'] = item.select(ITEM_SPECIFICS)[1].getText()
		tempInfo['isbn_100'] = item.select(ITEM_SPECIFICS)[2].getText()
		tempInfo['isbn_13'] = item.select(ITEM_SPECIFICS)[3].getText()
		tempInfo['trade_in_price'] = float(item.select(TRADE_IN_SELECTOR)[0].getText().replace('$', ''))
	except:
		tempInfo = None
	return tempInfo

def extractInfoFromPage(page):
	pageItems = []
	for item in page.select(ITEM_SELECTOR):
		info = extractInfoFromItem(item)
		if info != None:
			pageItems.append(info)
	return pageItems

def extractInfoFromURL(url):
	page = grabPage(url)
	return extractInfoFromPage(page)

def genURLs(keyword, pageCount):
	urlList = []
	for i in range(1, pageCount+1):
		url = AMAZON_URL.format(keyword, i)
		urlList.append(url)
	return urlList

class search(object):
	def __init__(self):
		self.toSearch = []
		self.results = []
		self.profitable = []

	def add(self, keyword):
		url = AMAZON_URL.format(keyword, 1)
		page = grabPage(url)
		pageCount = getPageCount(page)
		print("Keyword: {} Pages: {}".format(keyword, pageCount))
		for url in genURLs(keyword, pageCount):
			self.toSearch.append(url)

	def extractFromURL(self, urlList):
		for url in urlList:
			info = extractInfoFromURL(url)
			for val in info:
				val['purchase_price'] = extractPrice(val['item_id'])
				self.results.append(val)
				if val['purchase_price'] < val['trade_in_price']:
					self.profitable.append(val)
					print("Profitable item found")

	def start(self):
		parts = int(len(self.toSearch)/THREADS)
		if parts != 0:
			listOfURLs = chunks(self.toSearch, parts)
		else:
			listOfURLs = chunks(self.toSearch, 1)
		threads = [threading.Thread(target=self.extractFromURL, args=(urlList,)) for urlList in listOfURLs]
		for thread in threads:
			thread.start()
		for thread in threads:
			thread.join()
		return self.results

class amazonTextbookDB(object):
	def __init__(self, arg):
		self.arg = arg
		self.database = []

	def search(self, keyword):
		url = AMAZON_URL.format(keyword, 1)
		page = grabPage(url)
		pageCount = getPageCount(page)
		print("Keyword: {} Pages: {}".format(keyword, pageCount))
		for i in range(1, pageCount):
			if i != 1:
				url = AMAZON_URL.format(keyword, i)
				page = grabPage(url)



	#def search(self, keyword):


if __name__ == '__main__':
	print extractAllPageInfo('0134093410')
	'''url = "https://www.amazon.com/s/ref=sr_nr_i_0?srs=9187220011&fst=as%3Aoff&rh=i%3Atradein-aps%2Ck%3Abiology%2Ci%3Astripbooks&keywords=biology&ie=UTF8&qid=1527811678"
	#url = "https://www.amazon.com/s/ref=nb_sb_noss_2?url=srs%3D9187220011%26search-alias%3Dtradein-aps&field-keywords=python+2&rh=i%3Atradein-aps%2Ck%3Apython+2"
	#url = "https://www.amazon.com/s/ref=nb_sb_noss_2?url=srs%3D9187220011%26search-alias%3Dtradein-aps&field-keywords=python+program&rh=i%3Atradein-aps%2Ck%3Apython+program"
	#url = "https://www.amazon.com/s/ref=nb_sb_noss_2?url=srs%3D9187220011%26search-alias%3Dtradein-aps&field-keywords=python+3&rh=i%3Atradein-aps%2Ck%3Apython+3"
	url = "https://www.amazon.com/s/ref=sr_pg_2?&fst=p90x%3A1&rh=i%3Atradein-aps%2Ck%3Atextbooks&page=2"
	#page = grabPage(url)
	#print extractInfoFromPage(page)
	#print getResultCount(page).getText()
	e = search()
	e.add(raw_input("Search Term: "))
	f = e.start()
	print("{} Profitable items found".format(len(e.profitable)))
	for val in e.profitable:
		print("{} - ${}".format(val['item_url'],  val['trade_in_price'] - val['purchase_price']))'''
