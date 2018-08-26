"""A python module to let the user interact with the IMDb database and pull movie lists for actors and actresses."""
import imdb
import json
from pathlib import Path


def _get_movie_title_and_year(film):
    """A function to pull movie title and release year for further consumption.

    args:
        film: the IMDb 'Movie' object to pull info from.

    returns:
        a dictionary containing the films name and release year.
    """
    title = film.data.get('title')
    # for some reason, movies that to not have a release date and empty parenthesis on the end of the film name.
    title = title if '()' not in title else title[:-3]

    year = film.data.get('year')
    # we want to sort on the year so if year is not present we need to give an arbitrary int value so the
    # sorted function does not crash. 3000 was used as this happened on movies that are not out yet, so we want
    # them to be sorted at the 'recent' end.
    year = year if year is not None else 3000

    return {'title': title, 'year': year}


def _get_json_object_from_actor(actor, reverse):
    """Builds a JSON string

    Args:
        actor: the Person class to pull movie list from.
        reverse: whether movie list should be in most recent first or not.

    Returns:
        A properly formed JSON string.
    """
    actor_or_actress = [s for s in actor['filmography'][0] if s.startswith('act')][0]

    films = [_get_movie_title_and_year(film) for film
             in actor['filmography'][0].get(actor_or_actress)
             if film.data.get('kind') == 'movie']
    actual_films = []
    for film in sorted(films, key=lambda film: film['year'], reverse=reverse):
        year_value = film.get('year')
        actual_films.append({'name': film.get('title'),
                             'year': year_value if year_value != 3000 else 'unreleased'})
    dict_object = {
        'actor_name': actor.data['name'],
        'films': actual_films
    }
    json_object = json.dumps(dict_object, indent=4)
    return json_object


def _interact_with_actor(actor):
    """Once a particular Person has been decided, we want to grab their list of movies and let the user decide
    whether to print the results out to screen or to a JSON file.

    Args:
        actor: The IMDbPy Person class of the actor/actress of interest.
    """
    print('Retrieving movie information for {}'.format(actor['name']))
    # the key for the dictionary containing the films the actor starred in is listed as either 'actor'
    # if male or 'actress' if female, so we just grab the one that starts with 'act'.
    actor_or_actress = [s for s in actor['filmography'][0] if s.startswith('act')][0]

    filmography = actor['filmography'][0].get(actor_or_actress)

    if filmography is None:
        print("{} has not been in any movies.".format(actor['name']))
        return

    print("\n{} has been in {} movies.".format(actor['name'], len(filmography)))

    while True:
        print("\nPlease select an option: ")
        print("\tlist [-r]\t\twill print movies chronologically (providing the optional -r flag will reverse order)")
        print("\tjson [-r] <save_directory>\t\twill save to a json file (providing the optional -r flag will reverse "
              "order; defaults to current directory if <save_directory> is not provided)")
        print("\tquit\t\twill stop interacting with {} and search for another actor".format(actor['name']))

        answer = input("Your choice: ").split(' ')  # too primitive??

        if answer[0] == 'list':
            reverse = False

            if len(answer) > 1:
                reverse = True if answer[1] == '-r' else False

            film_list = [_get_movie_title_and_year(film) for film in filmography if film.data.get('kind') == 'movie']

            # We sort on the second item in the tuple which is the year.
            for film in sorted(film_list, key=lambda film: film['year'], reverse=reverse):
                year_value = film.get('year')
                print("{} ({})".format(film.get('title'), year_value if year_value != 3000 else 'unreleased'))

        elif answer[0] == 'json':
            reverse = False
            file_location = Path().absolute()

            if len(answer) > 1:
                if answer[1] == '-r':

                    reverse = True if answer[1] == '-r' else False

                    if len(answer) > 2:
                        try:
                            file_location = Path(answer[2])
                        except Exception as e:
                            print(e)
                            continue
                else:
                    # if optional -r was not present, but user entered a directory for saving.
                    try:
                        file_location = Path(answer[1])
                    except Exception as e:
                        print(e)
                        continue

            path = Path(Path(file_location) / "{}.json".format(actor['name']))
            try:
                with open(path, mode='wt') as f:
                    f.write(_get_json_object_from_actor(actor, reverse))
            except Exception as e:
                print(e)
                continue

            print('\n{}.json file successfully saved!\n'.format(actor['name']))

        elif answer[0] == 'quit':
            break

        else:
            print('Not valid input. Please try again.')


def _get_index_from_user_input(min_index, max_index):
    """Needed a loop to ensure we got a valid integer from user.

    Args:
        min_index: the minimum value allowed
        max_index: the maximum value allowed

    Returns:
        An integer
    """
    while True:
        answer = input('Please select the number of the actor you would like to see: ')
        try:
            integer = int(answer)
            if integer < min_index or integer > max_index:
                print('Please select a value between {} and {}'.format(min_index, max_index))
                continue
            return integer
        except ValueError:
            print('{} is not an integer.'.format(answer))
        except Exception as ex:
            print('Error: {}'.format(str(ex)))


def imdb_actor_search():
    """ The primary function of this module. Starts a series CLI prompts to retrieve movie lists for actors."""
    global ia
    ia = imdb.IMDb()
    print('Welcome to the IMDb python program!!')
    while True:
        actor_name_query = input('Please enter the name of the actor/actress you want you know about '
                                 '(to quit, enter nothing and press return): ')
        if actor_name_query == '':
            break

        print("Please wait a moment while we retrieve information about {} from IMDb".format(actor_name_query))
        actor_results = ia.search_person(actor_name_query)

        # List comes back with many actors with similar names so perform a direct name search on results
        # using list comprehension.
        actor = [x for x in actor_results if x['name'].lower() == actor_name_query.lower()]

        if len(actor) == 1:  # We have found exact match.
            actor_info = ia.get_person(actor[0].personID)
        else:
            print("There were {0} actors found with the name '{1}'".format(len(actor_results), actor_name_query))
            for index, actor in enumerate(actor_results):
                print("{0} - {1}".format(index, actor['name']))
            actor_index = _get_index_from_user_input(0, len(actor_results)-1)
            actor_info = ia.get_person(actor_results[actor_index].personID)

        _interact_with_actor(actor_info)


if __name__ == '__main__':
    imdb_actor_search()
