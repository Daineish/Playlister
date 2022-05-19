"""
File containing general utility functions for our YouTube/Spotify/Apple Music conversions
"""


def get_track_string(song_name, artists):
    """
    get a string containing track name and artists
    """

    artists_string = ""
    for artist in artists:
        if(artists_string is not ""):
            artists_string += ', '
        artists_string += artist['name']
    ret_str = song_name + "\" by " + artists_string + "\n"
    return ret_str

def get_track_string_sp(track):
    """
    get a string containing track name and artist from a spotify track dict
    """

    track_name = track['name']
    track_artists = track['artists']
    return get_track_string(track_name, track_artists)

def get_track_string_yt(track):
    """
    get a string containing track name and artist from a youtube track dict

    Example:
    The Count (feat. Wiz Khalifa) by Curren$y, Harry Fraud
    """

    track_name = track['title']
    track_artists = track['artists']
    return get_track_string(track_name, track_artists)
