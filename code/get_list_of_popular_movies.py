from bs4 import BeautifulSoup
import urllib2
import urlparse
import sys

from logtemplate import get_log
log = get_log('retrieve_popular_movies', level="debug")

IMDB_BASE_URL = "http://www.imdb.com/"
POPULAR_URL="http://www.imdb.com/search/title?at=0&count=100&sort=num_votes&title_type=feature"


def connect(url):
    try:
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page)
        log.debug('connected to %s' % url)
    except Exception:
        log.error("\n\n Failed to connect or parse %s\n" % url)
        raise Exception
        
    return soup

def parse_single_page(soup):
    
    films_on_page = []
    for movie_card in soup.find_all('td', {'class':'title'}):
        link = movie_card.find('a')
        imdb_id = link['href'].strip('/').replace('title/','')
        name = link.get_text()
        films_on_page.append( (imdb_id, name) )

    return films_on_page


def click_next(soup):
    link = soup.find('span', {'class':'pagination'}).find('a')
    target = urlparse.urljoin(IMDB_BASE_URL, link['href'])
    print target
    soup = connect( target )
    return soup


def parse_all(start_url, total=300):
    films = []
    soup = connect(start_url)
    count = 0
    while len(films) < total:
        films.extend( parse_single_page(soup) )
        soup = click_next(soup)
        count += 1
        print >> sys.stderr, '%i pages scraped.' % count

    return films


if __name__ == '__main__':

    films = parse_all( POPULAR_URL, total=300)
    




