import requests
import json
from collections import defaultdict

# whenever a user enters a new song on the add_song route, one of these
# functions will get called. I have not decided if I want to store all the songs
# that show up in the search in the database, 10 of them, or even only the first one
# (the one they intended). So i have included both of these functions. Once the song
# is returned, the result will be used to properly store it in the website's database
# sample input (shown below) could be any valid song title
def getTopSong(song_title):
    params = { 'term': song_title, 'media': 'music', 'entity' : "song"}
    search_object = requests.get('https://itunes.apple.com/search?', params = params).json()
    topResult = search_object['results'][0]
    returnDict = {'artist' : topResult['artistName'], 'name' : topResult['trackName']}
    return (returnDict)
def getAllSongs(song_title):
    params = { 'term': song_title, 'media': 'music', 'entity' : "song"}
    search_object = requests.get('https://itunes.apple.com/search?', params = params).json()
    songs = search_object['results']
    l_dictSongs = []
    for song in songs:
        returnDict = {'artist' : song['artistName'], 'name' : song['trackName']}
        l_dictSongs.append(returnDict)
    return l_dictSongs

print (getTopSong("Eye 2 Eye"))
print (getTopSong("Early mornin trappin"))
print (getTopSong("Nice for what"))
