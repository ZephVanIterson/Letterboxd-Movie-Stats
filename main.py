import requests
from bs4 import BeautifulSoup


profile_name = 'zedvanzed'

base_url = 'https://letterboxd.com'
profile_r = requests.get(f'{base_url}/{profile_name}/films/diary/')
soup = BeautifulSoup(profile_r.content, "html.parser")


name_length = len(profile_name)


#Get list of urls of each diary entry
diary_urls = [base_url + a.get('href')[name_length+1:] for a in soup.select('h3>a[href]')]

num_movies = len(diary_urls)


print(f'Found {num_movies} diary entries')

#print(diary_urls)

data = []
count = 0
for url in diary_urls:
    count += 1

    #print(f'Getting data from {url} ({count}/{num_movies})')
    r = requests.get(url)

    if r.status_code != 200:
        print(f'Error: {r.status_code}')
        continue

    soup = BeautifulSoup(r.content, "html.parser")

    data.append({
        'title': soup.select_one('#film-page-wrapper h1').get_text(),
        'cast':soup.select_one('#tab-cast p').get_text(',',strip=True),
        #'director':soup.select_one('#tab-director p').get_text(',',strip=True),
        'details':soup.select_one('#tab-details p').get_text(',',strip=True),
        'year':soup.select_one('#tab-year p').get_text(',',strip=True),
        #'rating':soup.select_one('.film-poster-meta-score').get_text(),
        #'review':soup.select_one('.diary-review-content').get_text(),
        'genres':soup.select_one('#tab-genres p').get_text(',',strip=True),
        'url':url
    })

    


for movie in data:
    print(movie)
    print('\n\n')