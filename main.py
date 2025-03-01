#Scraping HTML since letterboxd's API is not available for personal projects
#So it will be a bit slow


import requests
from bs4 import BeautifulSoup
import re

#Testing vars
Verbose = False
Testing = False

max_movies = 10

#Constants
half_star = "½"
one_star = "★"
one_half_star = "★½"
two_star = "★★"
two_half_star = "★★½"
three_star = "★★★"
three_half_star = "★★★½"
four_star = "★★★★"
four_half_star = "★★★★½"
five_star = "★★★★★"


profile_name = 'zedvanzed'
base_url = 'https://letterboxd.com'
name_length = len(profile_name)

def rating_to_number(rating):

    if rating == "No Rating":
        return None
    elif rating == half_star:
        return 0.5
    elif rating == one_star:
        return 1
    elif rating == one_half_star:
        return 1.5
    elif rating == two_star:
        return 2
    elif rating == two_half_star:
        return 2.5
    elif rating == three_star:
        return 3
    elif rating == three_half_star:
        return 3.5
    elif rating == four_star:
        return 4
    elif rating == four_half_star:
        return 4.5
    elif rating == five_star:
        return 5
    else:
        return None

def movie_to_histogram_url(movie_url):
    """Converts a movie URL to a histogram URL."""
    #ex. https://letterboxd.com/film/parasite/ -> https://letterboxd.com/csi/film/parasite/rating_histogram

    return re.sub(r'/film/', '/csi/film/', movie_url) + 'rating-histogram/'

def diary_to_movie_url(diary_url):
    """Converts a diary URL to a movie URL."""
    #rempoves the username from url
    #ex. https://letterboxd.com/zedvanzed/film/parasite/ -> https://letterboxd.com/film/parasite/
    return clean_url(re.sub(rf'/{profile_name}/', '/', diary_url))

#don't use for now
# def movie_to_diary_url(movie_url):
#     """Converts a movie URL to a diary URL."""
#     #might not quite work, may have a number in the url, not sure how to find
#     return re.sub(r'/film/', f'/{profile_name}/film/', movie_url)

def clean_url(url):
    """Removes trailing '/digits/' from a URL."""
    return re.sub(r'/\d+/$', '/', url)

def get_diary(profile_name):

    profile_r = requests.get(f'{base_url}/{profile_name}/films/diary/')

    if profile_r.status_code != 200:
        print("Error:", profile_r.status_code, "while fetching", f'{base_url}/{profile_name}/films/diary/')
        return None
    else:
        soup = BeautifulSoup(profile_r.content, "html.parser")
        return soup

def get_movie_urls(profile_soup):
    movie_urls = [base_url + a.get('href')[name_length+1:] for a in profile_soup.select('h3>a[href]')]
    return movie_urls

def get_diary_urls(profile_soup):
    diary_urls = [base_url + a.get('href') for a in profile_soup.select('h3>a[href]')]
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
    profile_soup = get_diary(profile_name)
    all_diary_urls = []
    all_movie_urls = []

    page_count = 0

    while profile_soup:
        page_count += 1
        # if Verbose:
        #     print(f'Scraping page {page_count}...')

        # Extract diary URLs from the current page
        all_diary_urls.extend(get_diary_urls(profile_soup))
        #all_movie_urls.extend(get_movie_urls(profile_soup))

        
        # Get the next page URL
        next_page_url = get_next_page_url(profile_soup)
        if not next_page_url:
            break  # Stop if there's no next page
        
        # Fetch the next page
        response = requests.get(next_page_url)
        profile_soup = BeautifulSoup(response.text, 'html.parser')

    #print("Your diary is ", page_count, "pages")

    return all_diary_urls


def get_diary_entry_data(url):
    r = requests.get(url)
    r.raise_for_status()  # Raise an exception for 4xx/5xx errors
    soup = BeautifulSoup(r.content, "html.parser")

    user_rating_element = soup.select_one('.rating') #This is the most important line to change. Inspect the html of letterboxd diary pages, and change this selector.
    user_rating = user_rating_element.get_text(strip=True) if user_rating_element else "No Rating"

    return {
        'title': soup.select_one('.film-poster img').get('alt'),
        'diary_url': url,
        'user_rating': user_rating,
    }

def get_movie_data(url):
    #print(f'Getting data from {url}')
    
    r = requests.get(url)
    r.raise_for_status()  # Raise an exception for 4xx/5xx errors
    
    if r.status_code != 200:
        print("Error:", r.status_code, "while fetching", url)
        return None  # Return None to indicate failure
    
    soup = BeautifulSoup(r.content, "html.parser")
    
    # Helper function to safely get text from a selector
    def safe_get_text(selector, default="N/A", separator=","):
        element = soup.select_one(selector)
        return element.get_text(separator, strip=True) if element else default

    # #average rating
    # average_rating = soup.select_one('.average-rating').get_text(strip=True)


    
    #This just grabs the most recent rating?
    #want to get user's rating and average rating
    # Extract rating (Letterboxd uses a span with 'rating' class)

    return {
        'title': safe_get_text('#film-page-wrapper h1', 'Unknown Title'),
        'cast': safe_get_text('#tab-cast p', 'No Cast Listed'),
        'details': safe_get_text('#tab-details p', 'No Details Available'),
        'genres': safe_get_text('#tab-genres p', 'No Genres Available'),
        'movie_url': url,
    }

def get_histogram_data(url):
    r = requests.get(url)
    r.raise_for_status()  # Raise an exception for 4xx/5xx errors
    soup = BeautifulSoup(r.content, "html.parser")

    #=IMPORTXML("https://letterboxd.com/csi/film/inception/rating-histogram/", "//span[@class='average-rating']")

    def safe_get_text(selector, default="N/A", separator=","):
        element = soup.select_one(selector)
        return element.get_text(separator, strip=True) if element else default

    #average rating
    average_rating_element = soup.select_one('.average-rating')
    if average_rating_element is None:
        average_rating = None
        if Verbose:
            print("No average rating found for", url)
    else:
        average_rating = average_rating_element.get_text(strip=True)

    return {
        'average_rating': average_rating
    }

def combine_data(movie_data, diary_data, diary_urls = None):

    #find matching pairs

    combined_dict = {}

    for movie in movie_data:
        for diary in diary_data:
            if movie['title'] == diary['title']:
                combined_dict[movie['title']] = {**movie, **diary}
                #print(f'Found match for {movie["title"]}')
                break
        
    return combined_dict
            
                
                



def main():
    global profile_name

    profile_soup = None

    while profile_soup is None:

        if Testing:
            print("Testing mode is on")
            profile_name = 'zedvanzed'
            break

        print("what is your Letterboxd username?")

        
        profile_name = input()

        profile_soup = get_diary(profile_name) 

        #if profile is not found
        if profile_soup is None:
            print("Profile not found")
        else:
            break

            



    # diary_urls = get_diary_urls(profile_soup) #Page 1

    # next_page_url = get_next_page_url(profile_soup)

    print("Scraping diary entries...")

    diary_urls = scrape_all_pages(profile_name)
    movie_urls = []
    for url in diary_urls:
        movie_urls.append(diary_to_movie_url(url))

    #print("Movie urlks:" , movie_urls)

    num_movies = len(movie_urls)
    
    print(f'Found {num_movies} diary entries')

    #print(diary_urls)

    print("getting movie data...")



    #Get movie data
    movie_count = 0
    movie_data = []
    for url in movie_urls:
        movie_count += 1
        if Verbose:
            print("Getting movie data for", url, "(" + str(movie_count) + "/" + str(num_movies) + ")")
        url = clean_url(url)
        histogram_url = movie_to_histogram_url(url)
        
        #Check if Nonetype
        if url is None:
            print(f'Error: {url}')
            print("URL is None")
            continue
        else:

            movie_entry = None

            movie_info = get_movie_data(url)
            if movie_info:
                #movie_data.append(temp)
                movie_entry = movie_info
            else:
                print(f'Error: {url}')


            histogram_info = get_histogram_data(histogram_url)
            if histogram_info:
                movie_entry = {**movie_entry, **histogram_info}
            else:
                print(f'Error: {url}')

            if movie_entry:
                movie_data.append(movie_entry)
            

        if Testing and movie_count >= max_movies:
            break
            
    #Get diary data
    diary_data = []
    diary_count = 0
    for url in diary_urls:
        diary_count += 1
        if Verbose:
            print("Getting diary data for", url, "(" + str(diary_count) + "/" + str(num_movies) + ")")
        #url = clean_url(url)
        
        #Check if Nonetype
        if url is None:
            print(f'Error: {url}')
            print("URL is None")
            continue
        else:
            temp = get_diary_entry_data(url)
            if temp:
                diary_data.append(temp)
            else:
                print(f'Error: {url}')

        if Testing and diary_count >= max_movies:
            break


    data = combine_data(movie_data, diary_data)

    #Get Number of movies in each genre
    total_genres = 0
    total_actors = 0

    genre_count = {}
    actor_count = {}
    

    top_rated_actors = []
    top_rated_genres = []

    max_above_average = {'title': 'None', 'diff': 0}
    max_below_average = {'title': 'None', 'diff': 0}

    top_rated_movies = []
    top_average_rated_movies = []
    #initialize top rated movies
    for i in range(5):
        top_rated_movies.append({'title': 'None', 'rating': 0})
        top_average_rated_movies.append({'title': 'None', 'rating': 0})


    #set data to a smaller list for testing
    # if Testing:
    #     data = data[:max_movies]
    #     num_movies = len(data)

    count = 0

    for movie_title in data:
        count += 1
        movie = data[movie_title]
        if Verbose:
            print(movie)
            print("Getting data for", movie['title'], "(" + str(count) + "/" + str(num_movies) + ")")
           

        #Genres
        genres = movie['genres'].split(',')
        for genre in genres:
            if genre in genre_count: #if genre is already in the dictionary
                genre_count[genre] += 1
            else: #new genre
                genre_count[genre] = 1
                total_genres += 1


        #Actors
        actors = movie['cast'].split(',')
        for actor in actors:

            actor = actor.strip() #remove leading and trailing whitespace

            if actor == "Show All…":
                continue
            if actor == "Jr.":
                continue

            if actor in actor_count:
                actor_count[actor] += 1
            else:
                actor_count[actor] = 1
                total_actors += 1

        #user's Rating
        user_rating = movie['user_rating']
        if user_rating is not None:
            user_rating = rating_to_number(user_rating)
            if user_rating > top_rated_movies[4]['rating']:
                top_rated_movies[4] = {'title': movie['title'], 'rating': user_rating}
                top_rated_movies.sort(key=lambda x: x['rating'], reverse=True)
        else:
            if Verbose:
                print("User has not rated", movie['title'])

        #Average Rating
        #average_rating = rating_to_number(movie['average_rating'])
        average_rating = movie['average_rating']
        if average_rating is not None:
            average_rating = float(average_rating)
            if average_rating > top_average_rated_movies[4]['rating']:
                top_average_rated_movies[4] = {'title': movie['title'], 'rating': average_rating}
                top_average_rated_movies.sort(key=lambda x: x['rating'], reverse=True)
        else:
            if Verbose:
                print("No average rating for", movie['title'])

        if user_rating is not None and average_rating is not None:
            # diff_from_average = {'title': movie['title'], 'diff': abs(user_rating - average_rating)}
            # if diff_from_average['diff'] > max_diff_from_average['diff']:
            #     max_diff_from_average = diff_from_average

            above_average = {'title': movie['title'], 'diff': user_rating - average_rating}
            below_average = {'title': movie['title'], 'diff': average_rating - user_rating}

            if above_average['diff'] > max_above_average['diff']:
                max_above_average = above_average
            if below_average['diff'] > max_below_average['diff']:
                max_below_average = below_average
            







    #get percentage of each genre
    genre_percents = {}
    for genre, count in genre_count.items():
        #round to two decimal places
        genre_percents[genre] = round(count / movie_count * 100, 2)


    #percent of movies each actor is in
    actor_percents = {}
    for actor, count in actor_count.items():
        actor_percents[actor] = round(count / movie_count * 100,2)

    #sort lists
    sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)
    sorted_actors = sorted(actor_count.items(), key=lambda x: x[1], reverse=True)

    print("Your 5 most watched genres are:")
    for genre, count in sorted_genres[:5]:
        print(genre,": ", count, "movies", "(", genre_percents[genre], "%)")

    print("\nYour 5 most watched actors are:")
    for actor, count in sorted_actors[:5]:
        print(actor,": ", count, "movies", "(", actor_percents[actor], "%)")

    print("\nYour top 5 rated movies are:")
    for movie in top_rated_movies:
        print(movie['title'], ": ", movie['rating'], "stars")

    print("\nYour top 5 average rated movies are:")
    for movie in top_average_rated_movies:
        print(movie['title'], ": ", movie['rating'], "stars")


    print("\nThe Movie you liked more than the average viewer is:")
    print(max_above_average['title'], "by", round(max_above_average['diff'],1), "stars")
    print("You rated it", rating_to_number(data[max_above_average['title']]['user_rating']), "stars and the average rating is", data[max_above_average['title']]['average_rating'], "stars")

    print("\nThe Movie you liked less than the average viewer is:")
    print(max_below_average['title'], "by", round(max_below_average['diff'],1), "stars")
    print("You rated it", rating_to_number(data[max_below_average['title']]['user_rating']), "stars and the average rating is", data[max_below_average['title']]['average_rating'], "stars")

    # #print all attributes of the movies
    # if Verbose:
    #     for movie in data:
    #         print("\n")
    #         for key, value in movie.items():
    #             print(key, ":", value)

if __name__ == '__main__':
    main()