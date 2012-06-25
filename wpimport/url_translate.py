import csv
import logging
import os.path as path
import urlparse
from BeautifulSoup import BeautifulSoup

class URLTranslator:

    def __init__(self):
        self.dictionary = {}
        self.location = None

    def load_dictionary_from_csv(self, csvfile):
        if path.exists(csvfile):
            csvreader = csv.reader(open(csvfile))
            for row in csvreader:
                if len (row) >= 2:
                    self.dictionary[row[0]] = row[1]

    def translate(self, html):
        if not html:
            return None
            
        soup = BeautifulSoup(html)

        links = soup.findAll('a')

        for l in links:
            if l.has_key('href'):
                href = l['href']
                if self.location:
                    href = urlparse.urljoin(self.location, href) 
                if self.dictionary.has_key(href):
                    logging.info('%s translated in %s' % (href, self.dictionary[href]))
                    l['href'] = self.dictionary[href]
                else : 
                    logging.info('missing translation for %s' % (href))
       

        return unicode(soup)
