from config import *

from bs4 import BeautifulSoup
import csv
from nltk import clean_html
import re
import urllib2

def scrape_bfi_voters():

    # initialize lists of voters with header labels
    voters_list = [['voterid', 'name', 'category', 'country', 'gender', 'film1', 'film2', 'film3', 'film4', 'film5', 'film6', 'film7', 'film8', 'film9', 'film10', 'comment']]

    # deal with manual filmid creation
    filmid_manual = 1000
    filmid_manual_dict = {}

    # open main BFI voters page and extract the tables with lists of voters
    bfi_soup = BeautifulSoup(urllib2.urlopen(bfi_url).read(), 'html5lib')
    tables = bfi_soup.findAll('table', attrs= {'class':'sas-poll'})
    bfi_soup.decompose()

    # parse through each voter (under a distinct <tr> tag)
    for table in tables:
        trs = table.findAll('tr')
        for tr in trs:

            # extract voterid and save link
            voter_link = tr.find('a').get('href').encode('utf8')
            voter_info = [voter_link.split('/')[-1].encode('utf8')]

            # extract voter name, type, country, and gender
            voter_info.extend([val.text.encode('utf8') for val in tr.findAll('td')])

            # open voter page
            voter_soup = BeautifulSoup(urllib2.urlopen(voter_link).read(), 'html5lib')
            film_table = voter_soup.find('table', attrs= {'class':'sas-poll'})

            # extract ten filmids
            for tr in film_table.findAll('tr'):
                try:
                    link = tr.findNext('td').findNext('p').find('a')
                    voter_info.append(link.get('href').split('/')[-1].encode('utf8'))
                except:
                    filmid_manual_info = [val.text.encode('utf8') for val in tr.findAll('td')]
                    if filmid_manual_info[0] in filmid_manual_dict:
                        voter_info.append(filmid_manual_dict.get(filmid_manual_info[0])[0])
                    else:
                        filmid_manual_dict[filmid_manual_info[0]] = [filmid_manual, filmid_manual_info[1], filmid_manual_info[2]]
                        voter_info.append(filmid_manual)
                        filmid_manual += 1

            # extract voter comment
            voter_info.append(clean_html(str(voter_soup.find('div', attrs= {'class':'wysiwyg'}))))

            # append info on this single voter to the list of all voters
            voter_soup.decompose()
            voters_list.append(voter_info)
            print voter_info

            # write voter info to csv
            with open(csv_output_dir+'voters.csv', 'wb') as f:
                writer = csv.writer(f)
                writer.writerows(voters_list)
                f.close()

    return voters_list, filmid_manual_dict

def scrape_bfi_films(voters_list, filmid_manual_dict):

    # get list of unique film ids
    filmid_list = []
    for i in voters_list:
        for j in i[5:-1]: filmid_list.append(j)
    filmid_list = set(filmid_list)

    # initialize lists of films with header labels
    film_list = [['filmid', 'title', 'director', 'country', 'year', 'genre', 'type', 'category']]

    # add manual filmids to list
    for k,v in filmid_manual_dict.iteritems():
        film_list.append([v[0], k, v[2], '', v[1], '', '', ''])

    # visit each of the film webpages
    for filmid in filmid_list:
        if filmid[0] == 'f': continue
        film_soup = BeautifulSoup(urllib2.urlopen('http://www.bfi.org.uk/films-tv-people/'+str(filmid)).read(), 'html5lib')

        # extract film title and append with film id
        film_info = [filmid, film_soup.find('title').contents[0].split('(')[0].strip().encode('utf8')]

        # extract director(s)
        try:
            film_info.append(" & ".join([director.text.encode('utf8') for director in film_soup.find('p', text=re.compile('Director.*'), attrs={'class':'row-label'}).findNext('p').findAll('a')]))
        except:
            film_info.append('')

        # extract country(ies)
        try:
            film_info.append(" & ".join([country.text.encode('utf8') for country in film_soup.find('p', text=re.compile('Countr.*'), attrs={'class':'row-label'}).findNext('p').findAll('span')]))
        except:
            film_info.append('')

        # extract year, genre, type, and category
        for k in ['Year', 'Genre', 'Type', 'Category']:
            try:
                film_info.append(film_soup.find('p', text=k, attrs={'class':'row-label'}).findNext('p').find('span').contents[0].encode('utf8'))
            except:
                film_info.append('')

        # append info on this single film to the list of all films
        film_soup.decompose()
        film_list.append(film_info)
        print film_info

        # write film info to csv
        with open(csv_output_dir+'films.csv', 'wb') as f:
            writer = csv.writer(f)
            writer.writerows(film_list)
            f.close()

    return film_list