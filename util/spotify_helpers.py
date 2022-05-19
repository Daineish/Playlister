"""
File containing various helper function for accessing spotipy API
"""
import re

def get_spotify_playlist_tracks(spotify, username, playlist_id):
    """
    get all tracks from a specified playlist using spotify username
    """

    results = spotify.user_playlist_tracks(username, playlist_id)
    tracks = results['items']
    while results['next']:
        results = spotify.next(results)
        tracks.extend(results['items'])
    return tracks

def add_tracks_to_spotify_playlist(spotify, spotify_username, playlist_url, track_ids):
    """
    add tracks to a spotify playlist
    """
    # apparently spotipy only lets you add 100 tracks per call, so just doing multiple calls here
    if(len(track_ids) > 100):
        for offset in range(0, len(track_ids), 100):
            max_track_idx = min(offset+100, len(track_ids))
            spotify.user_playlist_add_tracks(spotify_username, playlist_url, tracks=track_ids[offset:max_track_idx], position=offset)
    else:
        spotify.user_playlist_add_tracks(spotify_username, playlist_url, tracks=track_ids)

def get_best_sp_track_from_yt(artists, track_name, spotify):
    """
    search Spotify for YouTube track as given in yt_track. return 'best' result.

    Parameters:
    artists: comma separated list of artists
    track_name: title of the track
    spotify: spotify client
    """

    # TODO: "there's gotta be a better way!"
    # moving everything to lowercase, probably doesn't make a difference
    artists = artists.lower()
    track_name = track_name.lower()

    # removing ' x ' string, arising from the failure to find:
    # Hallelujah by Paul Russel X Kato On The Track (on YouTube)
    # there's no way that this is a good solution, but the 'X' instead
    # of 'and' or ',' or '&' is really giving the spotify API some grief
    artists = artists.replace(' x ', ' ')
    

    # removing feature from track name. Arising from the failure to find:
    # NOT FAIR (feat. Corbin) by The Kid LAROI
    # this seems to work ok, but definitely isn't foolproof. Features are
    # usually included in the artist list, but this isn't a hard rule
    track_name = re.sub(r'\(feat\..*\)', '', track_name)

    # artist first seems to be more successful
    search_string = artists + ' ' + track_name

    # passing in artist and track name into the query instead of separating these
    # using track: `trackname` artist: `artistname`
    # this seems to be more successful
    results = spotify.search(q=search_string, type='track')

    if(len(results['tracks']['items']) == 0):
        # TODO: error handling
        return ''
    return results['tracks']['items'][0]
