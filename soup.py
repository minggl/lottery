import urllib2
from bs4 import BeautifulSoup

def soup(url):
	data = urllib2.urlopen(url)
	content = BeautifulSoup(data)
	return content