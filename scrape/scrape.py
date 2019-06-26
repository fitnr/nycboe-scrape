#!/usr/bin/env python3
import sys
import re
import csv
import urllib.parse
from argparse import ArgumentParser
import requests
from bs4 import BeautifulSoup


def Soup(text):
    return BeautifulSoup(text, 'html.parser')


def get(session, url):
    r = session.get(url)
    if r.status_code != 200:
        raise RuntimeError('problem connecting to ' + url)
    return r.text


def findlinks(soup):
    '''Find links that aren't to Home or Back.'''
    return soup.select('a[title!=Home][title!=Back]')

def findtitle(soup):
    regex = re.compile(r'AD (\d\d)')
    a = soup(text=regex)
    try:
        return regex.search(a[0]).group(1)
    except IndexError:
        return None


def parsetable(soup):
    '''Parse a table into list of lists.'''
    output = []
    for tr in soup.find_all('tr'):
        row = [col.text.strip() for col in tr.find_all('td') if col.text.strip() != '']
        if row[0] != 'Total' and not row[0].startswith('Reported'):
            output.append(row)
    return output


def main():
    parser = ArgumentParser()
    parser.add_argument('url')
    args = parser.parse_args()

    with requests.Session() as session:
        soup = Soup(get(session, args.url))

        writer = csv.writer(sys.stdout)

        first = True

        for a in findlinks(soup):
            link = urllib.parse.urljoin(args.url, a.attrs['href'])
            print('getting', link, file=sys.stderr)
            adsoup = Soup(get(session, link))
            district = findtitle(adsoup)
            results = parsetable(adsoup.find('table', {'class': 'underline'}))
            if first is True:
                results[0].insert(0, 'reporting')
                results[0].insert(0, 'ED')
                writer.writerow(results[0])
                first = False

            for row in results[1:]:
                ed = re.search(r'ED\s+(\d+)', row[0]).group(1)
                row[0] = '{}{:03d}'.format(district, int(ed))

            writer.writerows(results[1:])


if __name__ == '__main__':
    main()
