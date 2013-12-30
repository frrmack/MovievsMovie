# virtual display (to use webdriver without using
# a visual window -- faster, and works without X-forwarding)
from pyvirtualdisplay import Display

# selenium webdriver to drive Chrome
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# connection & parsing the web
from bs4 import BeautifulSoup
import urllib2
import re
import time

# html translation, encoding, encryption
import base64
import htmlentitydefs


# filesystem, I/O
import sys
import glob
import cPickle



def translateHTML(text):
    """ 
    Translate HTML entities within a string.
    For example, "&lt;" becomes "<"
    and "&nbsp;" becomes space (non-breaking).
    """
    # Clean up non-ascii characters
    text = unicode(text).encode('ascii', 'ignore')
    # Callback function for getting the corresponding
    # ISO Latin character for a single entity
    def descape_entity(regexpMatch, defs=htmlentitydefs.entitydefs):
        try:
            return defs[regexpMatch.group(1)]
        except KeyError:
            return regexpMatch.group(0) # use as is
    # The regexp pattern for a single entity
    entityPattern = re.compile("&(\w+?);")
    # Substitute all entities with their ISO Latin counterparts 
    return unicode(entityPattern.sub(descape_entity, text),
                   'latin-1')



# Encrypted Netflix login credentials File
LOGINFILE = '/home/staff/irmak/Personal/netflix_credentials.pwd'


def retrieve_login_credentials(loginfile=LOGINFILE):
    """ 
    Retrieve netflix login email and password
    from an encrypted file with strict permissions
    """
    with open(loginfile,'r') as credentialsFile:
        loginCredentials = credentialsFile.read().split()
        email, password = map(base64.b64decode, loginCredentials)
    return email, password


def scrape_ratings(soup, verbose=True):
    """ 
    BeautifulSoup scraper of a ratings table page
    """
    ratings = []
    ratingsTable = soup.find("table", {'class': "agMovieSet agMovieTable"}).tbody
    movies = ratingsTable.findAll("tr", {'class':"agMovie "}) + \
             ratingsTable.findAll("tr", {'class':"agMovie odd"})    # even rows + odd rows
    for movie in movies:
        title = movie.find("span", {'class': "title "}).a.string
        ratingReport = movie.find(text=re.compile("You rated this movie:"))
        rating = int(ratingReport.split('You rated this movie:')[-1].strip())
        ratings.append( (title, rating) )
        if verbose: print >> sys.stderr, '    %s [%i]' % (title, rating)

    return ratings




def scrape_all_ratings_from_netflix(verbose=True, totNumPages=101):
    """ 
    Selenium webdriver
    connects to Netflix,
    logs in,
    scrapes ratings
    """
    loginURL = 'https://signup.netflix.com/Login'
    ratingsURL = 'http://movies.netflix.com/MoviesYouveSeen?pn=%i&st=tt&so=0'
    browser = webdriver.Chrome()

    # login
    if verbose: print >> sys.stderr, 'Logging in to Netflix'
    browser.get(loginURL)
    emailForm = browser.find_element_by_xpath('//input[@id="email"]')
    passwordForm = browser.find_element_by_xpath('//input[@id="password"]')
    email, password = retrieve_login_credentials()
    emailForm.send_keys(email)
    passwordForm.send_keys(password + Keys.RETURN)
    time.sleep(1)

    # ratings
    all_ratings = []
    for pagenum in range(1,totNumPages+1):
        url = ratingsURL % pagenum
        if verbose: print >> sys.stderr, 'Scraping ratings page %i' % pagenum
        browser.get(url)
        pageSoup = BeautifulSoup(browser.page_source)
        ratings_on_page = scrape_ratings(pageSoup)
        all_ratings.extend(ratings_on_page)
        if verbose: print >> sys.stderr, 'End of page.\n'
        time.sleep(2) # scrape slowly to avoid attention

    # end
    browser.quit()

    return all_ratings




if __name__ == "__main__":

    #--- get ratings
    all_ratings = scrape_all_ratings_from_netflix()

    #--- sort
    #--- primary key:   descending on rating
    #--- secondary key: ascending in alphabet
    def ratingThenAlphabet( ratingInfo ):
        title, rating = ratingInfo
        return (-rating, title)
    all_ratings.sort(key = ratingThenAlphabet)

    # #--- pickle the list of tuples
    # with open('allNetflixRatings.pck', 'w') as pickleFile:
    #     cPickle.dump(all_ratings, pickleFile)

    #---[[
    #--- shortcut: if you have the pickle file,
    #--- bypass all scraping above and load the pickle
    # with open('allNetflixRatings.pck','r') as pickleFile:
    #     all_ratings = cPickle.load(pickleFile)
    #---]]

    #--- save a csv file, separator: \t
    with open('allNetflixRatings.tab', 'w') as csvFile:
        for title, rating in all_ratings:
            title = translateHTML(title)
            print >> csvFile, '%s\t%i' % (title, rating)



