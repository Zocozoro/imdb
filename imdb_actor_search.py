import imdb
import json


def _get_actor_name_from_user():
    name = input('Please enter the name of the actor/actress you want you know about: ').split(' ')
    # name = 'Jeff Goldblum'.split(' ')
    return "{}, {}".format(name[1], name[0])


def _get_movie_title_and_year(film):
    title = film.data.get('title')
    title = title if '()' not in title else title[:-3]
    year = film.data.get('year')
    year = year if year is not None else 3000  # the sorted() method will crash if passed None so return 3000
    return {'title': title, 'year': year}


def _get_json_object_from_actor(actor):
    pass


def _interact_with_actor(actor):
    filmography = actor['filmography'][0].get('actor')  # [0] index needed?

    if filmography is None:
        print("{} has not been in any movies.".format(actor['name']))
        return

    print("\n{} has been in {} movies.".format(actor['name'], len(filmography)))

    while True:
        print("Please select an option: ")
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

            if len(answer) > 1:
                reverse = True if answer[1] == '-r' else False

            json_object = _get_json_object_from_actor(actor)
        elif answer[0] == 'quit':
            break
        else:
            print('')
        input('BLERG')


def _get_int_from_user_input():
    while True:
        answer = input('Please select the number of the actor you would like to see: ')
        try:
            integer = int(answer)
            return integer
        except ValueError:
            print('{} is not an integer.'.format(answer))
        except Exception as ex:
            print('Error: {}'.format(str(ex)))


def main():
    global ia
    ia = imdb.IMDb()
    print('Welcome to the IMDb python program!!')
    while True:
        actor_name_query = _get_actor_name_from_user()
        print("Please wait a moment while we retrieve information about {} from IMDb".format(actor_name_query))
        actor_results = ia.search_person(actor_name_query)
        # List comes back with many actors with similar names so perform a direct name search on results
        # to see if we get a single exact match.
        actor = [x for x in actor_results]# if x.data['name'] == actor_name_query]

        if len(actor) == 1:  # We have found exact match.
            actor_info = ia.get_person(actor[0].personID)
            # _interact_with_actor(actor_info)
        else:
            print("There were {0} actors found with the name '{1}'".format(len(actor_results), actor_name_query))
            for index, actor in enumerate(actor_results):
                print("{0} - {1}".format(index, actor['name']))
            actor_index = _get_int_from_user_input()
            actor_info = ia.get_person(actor_results[actor_index].personID)

        _interact_with_actor(actor_info)
        # break


if __name__ == '__main__':
    main()
