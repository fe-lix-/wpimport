#!/usr/bin/env python

import getpass
from optparse import OptionParser
import socket

from url_translate import URLTranslator
from wordpress_xmlrpc.base import *
from wordpress_xmlrpc import Client
from wordpress_xmlrpc import WordPressPage
from wordpress_xmlrpc.methods.pages import EditPage, NewPage, GetPage



class Page:
    def __init__(self):
        self.pid = 0
        self.url = None
        self.title = ''
        self.content = ''
        self.custom_fields = []
        self.translator = URLTranslator()
        self.translator.load_dictionary_from_csv('eugin-url.csv')

    def filter_page(self, content):
        content = self.translator.translate(clean_html(content))

    def from_csv(self, csv):
        self.pid = csv[0]
        if csv[1]:
            self.translator.location = csv[1]
            self.url = csv[1]
        self.title = csv[2]
        content = clean_html(csv[3])
        content = self.translator.translate(content)
        if content :
            self.content = content
        else:
            self.content = ''
        if len(csv) >= 5:
            self.custom_fields.append({"key":"_su_title","value":csv[4]})
        else:
            self.custom_fields.append({"key":"_su_title","value":""})
        if len(csv) >= 6:
            self.custom_fields.append({"key":"_su_keywords","value":csv[5]})
        else:
            self.custom_fields.append({"key":"_su_keywords","value":""})
        if len(csv) >= 7:
            self.custom_fields.append({"key":"_su_description","value":csv[6]})
        else:
            self.custom_fields.append({"key":"_su_description","value":""})

    def get(self, name):
        if name == 'keywords':
            for fields in self.custom_fields:
                if fields['key'] == '_su_keywords':
                    return fields['value']
        if name == 'description':
            for fields in self.custom_fields:
                if fields['key'] == '_su_description':
                    return fields['value']
        if name == 'title':
            for fields in self.custom_fields:
                if fields['key'] == '_su_title':
                    return fields['value']

    def to_csv(self):
        return [self.pid, self.title, self.content, self.get('title'), self.get('keywords'), self.get('description')]


class WordpressImporter:

    def __init__(self, options,args):
        self.options = options
        self.url = args[0]
        self.user = args[1]

    def password(self):
        self.passwd = getpass.getpass()

    def update_metas(self,page, metas):
        if not hasattr(page, 'custom_fields'):
            page.custom_fields = []
        for m in metas:
            updated = False
            for n in page.custom_fields:
                if n['key'] == m['key']:
                    n['value'] = m['value']
                    updated = True
            if not updated:
                page.custom_fields.append(m)


    def load_element(self,csvline):
        tmp = Page()
        tmp.from_csv(csvline)

        if not tmp.pid:
            print 'Creating new page %s' % (tmp.title)
            page = WordPressPage()
            page.title = tmp.title
            page.description = tmp.content
            self.update_metas(page,tmp.custom_fields)
            try:
                tmp.pid = self.xmlrpc.call(NewPage(page,True))
            except socket.gaierror:
                print 'Failed'
            self.csvwriter.writerow(tmp.to_csv())
        else:
            print 'Updating page %s - %s' % (tmp.pid, tmp.title)
            page = self.xmlrpc.call(GetPage(tmp.pid))
            page.title = tmp.title
            page.description = tmp.content
            try:
                self.update_metas(page, tmp.custom_fields)
            except socket.gaierror:
                print 'Failed'
            self.xmlrpc.call(EditPage(tmp.pid,page,True))

    def run(self):
        self.password()
        self.xmlrpc = Client(self.url, self.user, self.passwd)
        if self.options.csv:
            f = open(self.options.csv, 'r')
            if self.options.csv == 'output.csv':
                tmp_csv = open('./output-1.csv','w+')
            else:
                tmp_csv = open('./output.csv','w+')
            self.csvwriter = UnicodeWriter(tmp_csv)
            csvreader = UnicodeReader(f)
            for row in csvreader:
                self.load_element(row)





def main():
    parser = OptionParser()

    parser.add_option(
        '--from-csv',
        help='Specify the CSV file from which to get the top',
        dest='csv',
        metavar='CSV',
        default=False
    )

    (options, args) = parser.parse_args()

    wp_importer = WordpressImporter(options,args)
    wp_importer.run()

if __name__ == "__main__":
    main()
