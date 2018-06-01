import grey_harvest


def gen(num=1):
	''' spawn a harvester '''
	harvester = grey_harvest.GreyHarvester()

	''' harvest some proxies from teh interwebz '''
	count = 0
	for proxy in harvester.run():
			print proxy
			count += 1
			if count >= num:
					break
