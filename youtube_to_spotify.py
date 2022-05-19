#!/usr/bin/env python3

import datetime
import sys
import argparse
import spotipy as sp
import util.general_utility as helpers
import util.spotify_helpers as sp_helpers
import util.youtube_helpers as yt_helpers
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.oauth2 as oauth2
from ytmusicapi import YTMusic

# Default Playlist
thursday_playlist_url = 'https://open.spotify.com/playlist/5PK2WZI139tzi9CaJwsSvr?si=a6eac2bd5ff04567'
youtube_playlist_id = 'PLO-BQZhJ6t2rR0PqtsuFlgWEje5AmTSGN'

# Usage and argument parsing
parser = argparse.ArgumentParser(description='Used to transfer songs from a YouTube playlist to a Spotify playlist.')
# parser.add_argument('--date', type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'), dest='start_date', default='2022-01-01',
#                     help='earliest date from which we query songs, format: YYYY-MM-DD')
parser.add_argument('--action', choices=['append', 'create', 'print'], dest='result_action', default='print',
                    help='action which to take with results, either print results, append to a Spotify playlist (as given by spotifyPlaylistID arg), ' +
                    'or create a new Spotify playlist')
parser.add_argument('--spotifyPlaylistID', dest='playlist_url', default=None,
                    help='spotify playlist ID to append to when using --action append')
parser.add_argument('--spotifyPlaylistNewName', dest='spotify_playlist_new_name',
                    default=None, help='When using --action create, what to title the new Spotify playlist')
parser.add_argument('--spotifyPlaylistNewDesc', dest='spotify_playlist_new_desc', default=None,
                    help='When using --action create, the resulting description for the new Spotify playlist')
parser.add_argument('--youtubePlaylistID', dest='youtube_playlist_id', default=youtube_playlist_id,
                    help='YouTube playlist ID from which we gather track information//YouTube playlist ID to append to when using --action append')
parser.add_argument('--spotifyUsername', dest='spotify_username', default='daineish',
                    help='your spotify username')
parser.add_argument('--youtubeUsername', dest='youtube_username', default='daineish')

args = parser.parse_args()

# Special argument handling
if args.result_action == 'append':
    # ensure user gave playlist ID which we can append to
    if args.playlist_url is None:
        print('If using --action append, an existing Spotify playlist ID must be privded via --spotifyPlaylistID')
        print('Example Usage: ./main.py --action append --spotifyPlaylistID https://open.spotify.com/playlist/5PK...')
        sys.exit('Bad user input')

print('Initializing Spotify and YouTube clients...')
# CLIENT_ID=/set in environment variable, export SPOTIPY_CLIENT_ID=.../
# CLIENT_SECRET=/set in environment variable, export SPOTIPY_CLIENT_SECRET=.../
# REDIRECT_URI=/set in environment variable, export SPOTIPY_REDIRECT_URI='http://...'
SCOPE='playlist-modify-private' # To create playlist, we need this scope
token = sp.util.prompt_for_user_token(args.spotify_username, SCOPE)
spotify = sp.Spotify(auth=token)
ytmusic = YTMusic('headers_auth.json')
print('Done!')

# Get all tracks from the given YouTube playlist and store as a list
print('Retrieving YouTube playlist...')
playlist_yt = yt_helpers.get_yt_playlist(args.youtube_playlist_id, ytmusic)
playlist_tracks_yt = playlist_yt['tracks']

# If we are creating a playlist, and user did not specify a name a description,
# use the one from the Spotify playlist
if args.result_action == 'create' and (args.spotify_playlist_new_name is None or args.spotify_playlist_new_desc is None):
    if args.spotify_playlist_new_name is None:
        args.spotify_playlist_new_name = playlist_yt['title']
    if args.spotify_playlist_new_desc is None:
        args.spotify_playlist_new_desc = playlist_yt['description']
print('Done!')

# Using gathered tracks from YouTube playlist, use spotipy to search Spotify for equivalent tracks
print('Querying Spotify for YouTube tracks, may take a few minutes depending on playlist size...')
playlist_tracks_spotify = []
for yt_track in playlist_tracks_yt:
    yt_track_name = yt_track['title']
    yt_track_artists = ", ".join([artist['name'] for artist in yt_track['artists']])
    playlist_tracks_spotify.append(
        sp_helpers.get_best_sp_track_from_yt(yt_track_artists, yt_track_name, spotify))
print('Done!')

# Depending on user input, handle resulting Spotify tracks accordingly
sp_ids = [track['id'] for track in playlist_tracks_spotify]
if(args.result_action == 'print'):
    print('--------------\nspotify tracks\n--------------')
    for track in playlist_tracks_spotify:
        # print(track)
        print(helpers.get_track_string_sp(track))
    print('\n\n\n--------------\nyoutube tracks\n--------------')
    for track in playlist_tracks_yt:
        print(helpers.get_track_string_yt(track))
elif(args.result_action == 'append'):
    sp_helpers.add_tracks_to_spotify_playlist(spotify, args.spotify_username, args.playlist_url, sp_ids)
    print('Appended to Spotify playlist: ', args.playlist_url)
elif(args.result_action == 'create'):
    spotify_playlist_added = spotify.user_playlist_create(args.spotify_username, args.spotify_playlist_new_name, public=False, collaborative=False, description=args.spotify_playlist_new_desc)
    sp_helpers.add_tracks_to_spotify_playlist(spotify, args.spotify_username, spotify_playlist_added['id'], sp_ids)
    print('Spotify playlist created: ', spotify_playlist_added['external_urls']['spotify'])
else:
    sys.exit('Internal error: Unknown action')
