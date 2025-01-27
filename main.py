import requests
from bs4 import BeautifulSoup


profile_name = 'zedvanzed'
base_url = 'https://letterboxd.com'
name_length = len(profile_name)

def get_profile(profile_name):

    profile_r = requests.get(f'{base_url}/{profile_name}/films/diary/')
    soup = BeautifulSoup(profile_r.content, "html.parser")
    return soup


def get_diary_urls(profile_soup):
    diary_urls = [base_url + a.get('href')[name_length+1:] for a in profile_soup.select('h3>a[href]')]
    return diary_urls
    

def get_movie_data(url):
 #print(f'Getting data from {url} ({count}/{num_movies})')
    r = requests.get(url)

    if r.status_code != 200:
        print(f'Error: {r.status_code}')
        return

    soup = BeautifulSoup(r.content, "html.parser")

    #print(soup)

    return({
        'title': soup.select_one('#film-page-wrapper h1').get_text(),
        'cast':soup.select_one('#tab-cast p').get_text(',',strip=True),
        #'director':soup.select_one('#tab-director p').get_text(',',strip=True),
        'details':soup.select_one('#tab-details p').get_text(',',strip=True),
        #'date':soup.select_one('#tab-date p').get_text(',',strip=True),
        #'year':soup.select_one('#tab-year p').get_text(',',strip=True),
        #'rating':soup.select_one('.film-poster-meta-score').get_text(),
        #'review':soup.select_one('.diary-review-content').get_text(),
        'genres':soup.select_one('#tab-genres p').get_text(',',strip=True),
        'url':url
    })



def main():

    profile_soup = get_profile(profile_name)

    diary_urls = get_diary_urls(profile_soup)

    num_movies = len(diary_urls)
    
    print(f'Found {num_movies} diary entries')

    #print(diary_urls)

    data = []
    count = 0
    for url in diary_urls:
        count += 1

        data.append(get_movie_data(url))

    for movie in data:
        print(movie)
        print('\n\n')