import grey_harvest


def gen(num=1):
	proxyList = []
	''' spawn a harvester '''
	harvester = grey_harvest.GreyHarvester()

	''' harvest some proxies from teh interwebz '''
	count = 0
	for proxy in harvester.run():
			proxies = {
			  "http": str(proxy),
			  "https": str(proxy),
			}
			proxyList.append(proxies)
			print proxy
	return proxyList

if __name__ == '__main__':
	gen()
