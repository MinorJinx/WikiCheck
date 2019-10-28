''' Created by Jeremy Reynolds for UALR COSMOS Team
	Searches wikipedia to check if url has a wikipage.
	Uses BeautifulSoup to parse wikipage infobox to find
	website hrefs.
	If input url matches url on the wikipage, the wikipage
	is searched for the terms 'mainstream' and 'popular'.

	Expects .csv with hostnames in first column.
	Outputs .csv with list of mainstream/popular hostnames.
'''

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import urllib.parse, wikipedia, csv, re

inputFile = 'sitelist.csv'		# CSV input file that contains hostname list
outputFile = 'output.csv'		# CSV output file
urlNotFound = []				# Contains urls that don't have wikipages
urlFound = []					# Contains urls that have wikipages
hostnames = []					# Array to store hostnames from 'inputFile'
counter = 0

def urlStrip(url):				# Strips urls to make them uniform
	if url[0:8] == 'https://':
		url = url[8:]
	if url[0:7] == 'http://':
		url = url[7:]
	if url[0:4] == 'www.':
		url = url[4:]
	if url[-1:] == '/':
		url = url[:-1]
	return url.lower()

file = open(inputFile)			# Opens 'inputFile' and appends entries to hostnames[] array
reader = csv.reader(file)
for item in reader:
	hostnames.append(urlStrip(item[0]))
file.close()

for item in hostnames:							# Loop will check if hostnames have wikipages
	if item not in urlFound + urlNotFound:		# Prevents checking duplicate hostnames
		s = wikipedia.search(item, results=1)	# Searches Wikipedia for hostname
		urlBool = False							# T/F boolean for checking if hostname has wikipage
		infoboxUrl = []							# Contains hrefs from wikipage infobox
		counter += 1

		if s:									# If Wikipedia page was found, open with BeautifulSoup
			site = urllib.parse.quote('http://en.wikipedia.org/wiki/' + s[0], safe='/,:')
			page = urlopen(Request(site, headers={'User-Agent': 'Mozilla/5.0'}))
			soup = BeautifulSoup(page.read(), 'lxml')
			table = soup.find('table', class_='infobox vcard')

			if not table:						# Finds infobox table on wikipage
				table = soup.find('table', class_='infobox')
			if table:							# Search each row for 'Website' cell and append hrefs
				for tr in table.find_all('tr'):
					if tr.find('th'):
						if tr.find('th').text == 'Website':
							infoboxUrl = tr.find('td').text.split()
							for a in tr.find_all('a'):
								infoboxUrl.append(a.get('href'))
			for url in infoboxUrl:				# Checks if each infoboxUrl matches input hostname
				if urlStrip(url) == item:
					urlBool = True
			if urlBool:							# If match found append to urlFound, else urlNotFound
				urlFound.append(item)
				print(counter, item.ljust(30), 'Wikipage href found')
			else:
				urlNotFound.append(item)
				print(counter, item.ljust(30), 'Wikipage href not found')
		else:
			urlNotFound.append(item)			# Append hostname to urlNotFound if Wikipedia page was not found
			print(counter, item.ljust(30), 'Wikipage not found')

print('\nURLs checked:', len(hostnames))		# Print results and reset counter
print('URLs with Wikipage:', len(urlFound))
print('URLs with no Wikipage:', len(urlNotFound), '\n')
counter = 0

for url in urlFound:							# Loop will check if found urls are mainstream/popular
	s = wikipedia.search(url, results=1)		# Seaches Wikipedia for url and opens with BeautifulSoup
	site = urllib.parse.quote('http://en.wikipedia.org/wiki/' + s[0], safe='/,:')
	page = urlopen(Request(site, headers={'User-Agent': 'Mozilla/5.0'}))
	soup = BeautifulSoup(page.read(), 'lxml')
	text = soup.findAll(text=re.compile('mainstream|popular'))
	if text:									# Searches for terms: 'mainstream' or 'popular'
		counter += 1							# If term is found save url to .csv
		print(counter, url.ljust(30), 'Mainstream/Popular')
		with open(outputFile, 'a', newline='') as file:
			writer = csv.writer(file)			# Appends data to new row in 'outputFile.csv'
			writer.writerow([url])
