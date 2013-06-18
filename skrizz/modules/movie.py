# -*- coding: utf8 -*-
"""
imdb.py - Skrizz Movie Information Module
Copyright 2012-2013, Elad Alfassa, <elad@fedoraproject.org>
Copyright 2013, Bryan Chain, http://www.bryanchain.com

Licensed under the Eiffel Forum License 2.

This module relies on imdbapi.com
"""
import json
import skrizz.web as web
import skrizz.module

@skrizz.module.commands('movie', 'imdb')
@skrizz.module.example('.movie Movie Title')
def movie(skrizz, trigger):
    """
    Returns some information about a movie, like Title, Year, Rating, Genre and IMDB Link.
    """
    if not trigger.group(2):
        return
    word=trigger.group(2).rstrip()
    word=word.replace(" ", "+")
    uri="http://www.imdbapi.com/?t="+word
    u = web.get_urllib_object(uri, 30)
    data = json.load(u) #data is a Dict containing all the information we need
    u.close()
    if data['Response'] == 'False':
        if 'Error' in data:
            message = '[MOVIE] %s' % data['Error']
        else:
            skrizz.debug('movie', 'Got an error from the imdb api, search phrase was %s' % word, 'warning')
            skrizz.debug('movie', str(data), 'warning')
            message = '[MOVIE] Got an error from imdbapi'
    else:
        message = '[MOVIE] Title: ' +data['Title']+ \
                  ' | Year: ' +data['Year']+ \
                  ' | Rating: ' +data['imdbRating']+ \
                  ' | Genre: ' +data['Genre']+ \
                  ' | IMDB Link: http://imdb.com/title/' + data['imdbID']
    skrizz.say(message)

if __name__ == '__main__':
    print __doc__.strip()
