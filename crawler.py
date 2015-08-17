#-*- coding: utf-8 -*-
#
# Crawler.py
#

import httplib
import re
from posixpath import join, dirname, normpath
from urllib import quote

class Crawler:
    '''
    Class responsible for performing basic operations related to crawling like
    Fetching links from a given URL
    Validating the links
    and again fetching the links until max depth reached
    '''

    def __init__(self, max_depth = 0):
        self.visited = {}
        self.max_depth = max_depth
        self.current_depth = 1

    def start(self, url):
        self.crawl(url)

    def crawl(self, url):
        print url
        links = self.getLinks(url)
        self.visited.update({url:True})

        for link in links:
            if self.visited.has_key(link) and self.visited[link]:
                continue
            else:
                if self.current_depth <= self.max_depth:
                    self.visited.update({link:False})
                    self.current_depth += 1
                    self.crawl(link)
                else:
                    self.visited.update({link:False})
        #decrease current depth as we are coming out from recursion
        self.current_depth -= 1

    def getLinks(self, url):
        links = []
        valid_links = []

        rx_url = re.match('(https?)://([^/]+)(.*)', url)
        if not rx_url:
            print "Please enter valid URL: http(s)://www.example.com"

        protocol = rx_url.group(1)
        host = rx_url.group(2)
        path = rx_url.group(3)

        if protocol == 'http':
            conn = httplib.HTTPConnection(host, timeout=10)
        else:
            conn = httplib.HTTPSConnection(host, timeout=10)

        try:
            conn.request('GET', path)
        except:
            print "ERROR: Unable to connect:", path
            return valid_links

        res = conn.getresponse()

        #not handling 301 and 302
        if res.status == 200:
            if re.search('text/html', res.getheader('Content-Type')):
                htmlString = res.read().decode("utf-8")
                links = re.findall('''href\s*=\s*['"]\s*([^'"]+)['"]''',
                    htmlString, re.S)
                links = list(set(links))
                for link in links:
                    valid_link = self.validate_link(url, link)
                    if valid_link:
                        valid_links.append(valid_link)
        return valid_links

    def validate_link(self, url, link):
        # Remove anchor
        link = re.sub(r'#[^#]*$', '', link)

        # Skip prefix
        if re.search('^(#|javascript:|mailto:|tel:)', link):
            return None

        #validate URL
        rx_url = re.match('(https?://)([^/:]+)(:[0-9]+)?([^\?]*)(\?.*)?', url)
        url_protocol = rx_url.group(1)
        url_host = rx_url.group(2)
        url_port = rx_url.group(3) if rx_url.group(3) else ''
        url_path = rx_url.group(4) if len(rx_url.group(4)) > 0 else '/'
        url_dir_path = dirname(url_path)

        #validate link and create a full url using above 'url'
        rx_link = re.match('((https?://)([^/:]+)(:[0-9]+)?)?([^\?]*)(\?.*)?', link)
        link_full_url = rx_link.group(1) != None
        link_protocol = rx_link.group(2) if rx_link.group(2) else url_protocol
        link_host = rx_link.group(3) if rx_link.group(3) else url_host
        link_port = rx_link.group(4) if rx_link.group(4) else url_port
        link_path = quote(rx_link.group(5), '/%') if rx_link.group(5) else url_path
        link_query = quote(rx_link.group(6), '?=&%') if rx_link.group(6) else ''
        link_dir_path = dirname(link_path)

        if not link_full_url and not link.startswith('/'):
            link_path = normpath(join(url_dir_path, link_path))

        link_url = link_protocol + link_host + link_port + link_path + link_query
        return link_url

if __name__ == '__main__':
    max_depth = 1
    print "Crawler Started with Max Depth:", max_depth
    crawler = Crawler(max_depth)
    crawler.crawl("http://recruiterbox.com/")
    total_url_crawled = 0
    for link in crawler.visited:
        if crawler.visited[link]:
            total_url_crawled += 1
    print "Total URL found =", len(crawler.visited)
    print "Total URL crawled =", total_url_crawled
    print "Crawler Stopped"