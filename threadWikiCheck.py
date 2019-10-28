''' Created by Jeremy Reynolds for UALR COSMOS Team
	Searches wikipedia to check if url has a wikipage.
	Uses BeautifulSoup to parse wikipage infobox to find
	website hrefs.
	If input url matches url on the wikipage, the wikipage
	is searched for the terms 'mainstream' and 'popular'.

	Expects .csv with hostnames in first column.
	Outputs .csv with list of mainstream/popular hostnames.
	(Threaded version, line 26 contains worker count)
'''

from queue import Queue
from threading import Thread
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import urllib.parse, wikipedia, time, csv, re

def readFile(inputFile):
	file = open(inputFile)		# Opens 'inputFile' and appends entries to jobs[] array
	reader = csv.reader(file)
	for item in reader:
		jobs.append(urlStrip(item[0]))
	file.close()

	for i in range(4):			# Start threads, each one will process one job from the jobs[] queue
		t = Thread(target=wikiCheck, args=(queue,))
		t.setDaemon(True)
		t.start()
	for job in jobs:			# For each item in jobs[], put each into the queue in FIFO sequence
		queue.put(job)
	queue.join()				# Wait until all jobs are processed before quitting

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

def wikiCheck(queue):								# Function will check if hostnames have wikipages
	while True:
		global counter
		item = queue.get()							# 'item' contains hostname from 'inputFile'
		if item not in urlFound + urlNotFound:		# Prevents checking duplicate hostnames
			s = wikipedia.search(item, results=1)	# Searches Wikipedia for hostname
			urlBool = False							# T/F boolean for checking if hostname has wikipage
			infoboxUrl = []							# Contains hrefs from wikipage infobox

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
			counter += 1
		queue.task_done()							# Stops current queue worker

def mainstreamCheck(queue):							# Function will check if found urls are mainstream/popular
	while True:
		global counter
		url = queue.get()							# Retrieves item from queue
		s = wikipedia.search(url, results=1)		# Seaches Wikipedia for url and opens with BeautifulSoup
		site = urllib.parse.quote('http://en.wikipedia.org/wiki/' + s[0], safe='/,:')
		page = urlopen(Request(site, headers={'User-Agent': 'Mozilla/5.0'}))
		soup = BeautifulSoup(page.read(), 'lxml')
		text = soup.findAll(text=re.compile('mainstream|popular'))
		if text:									# Searches for terms: 'mainstream' or 'popular'
			counter += 1							# If term is found advance counter and save url to .csv
			print(counter, url.ljust(30), 'Mainstream/Popular')
			with open(outputFile, 'a', newline='') as file:
				writer = csv.writer(file)			# Appends data to new row in 'outputFile.csv'
				writer.writerow([url])
		queue.task_done()							# Stops current queue worker

inputFile = 'sitelist.csv'		# CSV input file that contains hostname list
outputFile = 'output.csv'		# CSV output file
urlNotFound = []				# Contains urls that don't have wikipages
urlFound = []					# Contains urls that have wikipages
jobs = []						# List of hostnames from 'inputFile' to use for threading
queue = Queue()					# Initializes Queue
counter = 1

start_time = time.time()		# Starts a timer for wikiCheck()
readFile(inputFile)				# Starts searching Wikipedia by calling checkWiki()
								# Print results and reset counter
print('\nTime taken:'.ljust(33), round(time.time()-start_time), 'seconds')
print('URLs checked:'.ljust(32), len(jobs))
print('URLs with Wikipage:'.ljust(32), len(urlFound))
print('URLs with no Wikipage:'.ljust(32), len(urlNotFound), '\n')

start_time2 = time.time()		# Starts a timer for mainstreamCheck()
queue = Queue()					# Re-Initializes Queue
jobs2 = []						# New list of urls from urlFound[] to use for threading
counter = 0

for url in urlFound:			# Appends urls from urlFound[] to jobs2[] array
	jobs2.append(urlStrip(url))
for i in range(4):				# Start threads, each one will process one job from the jobs2[] queue
	t = Thread(target=mainstreamCheck, args=(queue,))
	t.setDaemon(True)
	t.start()
for job in jobs2:				# For each item in jobs2[], put each into the queue in FIFO sequence
	queue.put(job)
queue.join()					# Wait until all jobs are processed before quitting

print('\nTime taken:'.ljust(33), round(time.time()-start_time2), 'seconds')
print('Mainstream URLs:'.ljust(32), counter)
