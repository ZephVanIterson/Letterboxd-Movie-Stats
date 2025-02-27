import requests
from bs4 import BeautifulSoup
import re


profile_name = 'zedvanzed'
base_url = 'https://letterboxd.com'
name_length = len(profile_name)


def clean_url(url):
    """Removes trailing '/digits/' from a URL."""
    return re.sub(r'/\d+/$', '/', url)

def get_profile(profile_name):

    profile_r = requests.get(f'{base_url}/{profile_name}/films/diary/')
    soup = BeautifulSoup(profile_r.content, "html.parser")
    return soup


def get_diary_urls(profile_soup):
    diary_urls = [base_url + a.get('href')[name_length+1:] for a in profile_soup.select('h3>a[href]')]
    return diary_urls

def get_next_page_url(profile_soup):
    """
    Find the URL for the next page in the pagination, if it exists.
    """
    next_link = profile_soup.select_one('a.next')
    if next_link:
        return base_url + next_link.get('href')
    return None

def scrape_all_pages(profile_name):
    """Scrapes all diary entry URLs from all pages."""
    profile_soup = get_profile(profile_name)
    all_diary_urls = []

    page_count = 0

    while profile_soup:
        page_count += 1
        print(f'Scraping page {page_count}...')
        # Extract diary URLs from the current page
        all_diary_urls.extend(get_diary_urls(profile_soup))
        
        # Get the next page URL
        next_page_url = get_next_page_url(profile_soup)
        if not next_page_url:
            break  # Stop if there's no next page
        
        # Fetch the next page
        response = requests.get(next_page_url)
        profile_soup = BeautifulSoup(response.text, 'html.parser')

    return all_diary_urls

def get_movie_data(url):
    print(f'Getting data from {url}')
    
    r = requests.get(url)
    
    if r.status_code != 200:
        print("Error:", r.status_code, "while fetching", url)
        return None  # Return None to indicate failure
    
    soup = BeautifulSoup(r.content, "html.parser")
    
    # Helper function to safely get text from a selector
    def safe_get_text(selector, default="N/A", separator=","):
        element = soup.select_one(selector)
        return element.get_text(separator, strip=True) if element else default

    return {
        'title': safe_get_text('#film-page-wrapper h1', 'Unknown Title'),
        'cast': safe_get_text('#tab-cast p', 'No Cast Listed'),
        'details': safe_get_text('#tab-details p', 'No Details Available'),
        'genres': safe_get_text('#tab-genres p', 'No Genres Available'),
        'url': url
    }



def main():

    profile_soup = get_profile(profile_name) #

    # diary_urls = get_diary_urls(profile_soup) #Page 1

    # next_page_url = get_next_page_url(profile_soup)

    diary_urls = scrape_all_pages(profile_name)
    num_movies = len(diary_urls)
    
    print(f'Found {num_movies} diary entries')

    #print(diary_urls)

    print("getting movie data...")
    data = []
    movie_count = 0
    for url in diary_urls:
        movie_count += 1

        #if url ends in /any digits/ remove it
        #what causes this?
        url = clean_url(url)
        
        #Check if Nonetype
        if url is None:
            print(f'Error: {url}')
            print("URL is None")
            continue
        else:
            movie_data = get_movie_data(url)
            if movie_data:
                data.append(movie_data)
            else:
                print(f'Error: {url}')


    # for movie in data:
    #     print(movie)
    #     print('\n\n')




    #Get Number of movies in each genre
    total_genres = 0

    genre_count = {}
    for movie in data:
        genres = movie['genres'].split(',')
        for genre in genres:
            if genre in genre_count: #if genre is already in the dictionary
                genre_count[genre] += 1
            else: #new genre
                genre_count[genre] = 1
                total_genres += 1


    #get percentage of each genre
    genre_percents = {}
    for genre, count in genre_count.items():
        genre_percents[genre] = count / movie_count * 100
        

    #print highest genre to lowest
    sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)
    sorted_genre_percents = sorted(genre_percents.items(), key=lambda x: x[1], reverse=True)

    #print top 5 in a niceformat with percent
    for genre, count in sorted_genres[:5]:
        print(genre,": ", count, "movies", "(", genre_percents[genre], "%)")
    #Get a list of attributes for each movie
    attributes = set()
    for movie in data:
        for key in movie:
            attributes.add(key)


    #most viewed actors
    actor_count = {}
    for movie in data:
        actors = movie['cast'].split(',')
        for actor in actors:
            if actor in actor_count:
                actor_count[actor] += 1
            else:
                actor_count[actor] = 1


    #percent of movies each actor is in
    actor_percents = {}
    for actor, count in actor_count.items():
        actor_percents[actor] = count / movie_count * 100

    sorted_actors = sorted(actor_count.items(), key=lambda x: x[1], reverse=True)

    for actor, count in sorted_actors[:5]:
        print(actor,": ", count, "movies", "(", actor_percents[actor], "%)")
        



    #print attributes oine per row
    for attribute in attributes:
        print(attribute)

    # #print highest rated movie
    # print(max(data, key=lambda x: x['rating']))

    # #printy lowest rated movie
    # print(min(data, key=lambda x: x['rating']))



if __name__ == '__main__':
    main()