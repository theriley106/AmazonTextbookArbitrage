import TextbookAPI
import csv
def get_dec(x):
	a = (float(''.join(ele for ele in x if ele.isdigit() or ele == '.')))
	a = float("{0:.2f}".format(a))
	return a

def Start():
	ASINlisting = []
	TextbookAPI.SecondASINlisting = []
	At = TextbookAPI.AmazonTrade(['Textbooks'], 'Amazon.csv', 2)
	for asin in At:
		ASINlisting.append(asin[0])
		SecondASINlisting.append(asin[0])
	TextbookAPI.Biblio(ASINlisting, CSV='Biblio.csv', Debug=2)
	TextbookAPI.Half(SecondASINlisting, CSV='Half.csv', Debug=2)

def CombineCSV(csvd, csvone, csvtwo):
	profit = []
	with open(csvd, 'rb') as f:
		reader = csv.reader(f)
		csvd = list(reader)
	with open(csvone, 'rb') as f:
		reader = csv.reader(f)
		csvone = list(reader)
	with open(csvtwo, 'rb') as f:
		reader = csv.reader(f)
		csvtwo = list(reader)
	for items in csvone:
		for itm in csvd:
			if items[0] in itm:
				itm.append(items[1])
	for items in csvtwo:
		for itm in csvd:
			if items[0] in itm:
				itm.append(items[1])
	for e in csvd:
		if len(e) == 4:
			if get_dec(e[1]) > get_dec(e[2]):
				profit.append(e)
				break
			if get_dec(e[1]) > get_dec(e[3]):
				profit.append(e)
	return profit
Start()
a = CombineCSV('Amazon.csv', 'Half.csv', 'Biblio.csv')
for e in a:
	print(e)