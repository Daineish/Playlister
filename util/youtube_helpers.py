"""
File containing various helper function for accessing YouTube python API (as provided by unofficial ytmusicapi)
"""

from util.general_utility import *

def get_best_yt_track_from_sp(sp_track, ytmusic):
    """
    search youtube for spotify track as given in sp_track. return 'best' result.
    """

    results_youtube = ytmusic.search(
        query=get_track_string_sp(sp_track), filter='songs')

    # simply gathering first result for now, can add a better approach in the future
    return results_youtube[0]

def get_yt_playlist(playlist_id, ytmusic):
    """
    get a playlist from YouTube and return it
    """

    # TODO: What limit is appropriate?
    return ytmusic.get_playlist(playlistId=playlist_id, limit=1000)
