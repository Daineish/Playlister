#!/usr/bin/env python3

import datetime
import sys
import argparse
import spotipy as sp
import util.general_utility as helpers
import util.spotify_helpers as sp_helpers
import util.youtube_helpers as yt_helpers
from spotipy.oauth2 import SpotifyClientCredentials
from ytmusicapi import YTMusic

# Default Playlist
thursday_playlist_url = 'https://open.spotify.com/playlist/5PK2WZI139tzi9CaJwsSvr?si=a6eac2bd5ff04567'

# Usage and argument parsing
parser = argparse.ArgumentParser(description='Used to transfer songs from a Spotify playlist to a Youtube playlist.')
parser.add_argument('--date', type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'), dest='start_date', default='2022-01-01',
                    help='earliest date from which we query songs, format: YYYY-MM-DD')
parser.add_argument('--action', choices=['append', 'create', 'print'], dest='result_action', default='print',
                    help='action which to take with results, either print results, append to a YouTube playlist (as given by youtubePlaylistID arg), ' +
                    'or create a new YouTube playlist')
parser.add_argument('--youtubePlaylistID', dest='youtube_playlist_id', default=None,
                    help='YouTube playlist ID to append to when using --action append')
parser.add_argument('--youtubePlaylistNewName', dest='youtube_playlist_new_name',
                    default=None, help='When using --action create, what to title the new YouTube playlist')
parser.add_argument('--youtubePlaylistNewDesc', dest='youtube_playlist_new_desc', default=None,
                    help='When using --action create, the resulting description for the new YouTube playlist')
parser.add_argument('--spotifyPlaylistID', dest='playlist_url', default=thursday_playlist_url,
                    help='spotify URL or URI from which we gather track information')
parser.add_argument('--spotifyUsername', dest='spotify_username', default='daineish',
                    help='your spotify username')

args = parser.parse_args()

# Special argument handling
if args.result_action == 'append':
    # ensure user gave playlist ID which we can append to
    if args.youtube_playlist_id is None:
        print('If using --action append, an existing YouTube playlist ID must be privded via --youtubePlaylistID')
        print('Example Usage: ./main.py --action append --youtubePlaylistID PLO-BQZh...')
        sys.exit('Bad user input')

print('Initializing Spotify and YouTube clients...')
spotify = sp.Spotify(client_credentials_manager=SpotifyClientCredentials())
ytmusic = YTMusic('headers_auth.json')
print('Done!')

# Get all tracks from the given spotify playlist and store as a list
print('Retrieving Spotify playlist...')
playlist_tracks_spotify = sp_helpers.get_spotify_playlist_tracks(spotify,
    args.spotify_username, args.playlist_url)

# If we are creating a playlist, and user did not specify a name a description,
# use the one from the Spotify playlist
if args.result_action == 'create' and (args.youtube_playlist_new_name is None or args.youtube_playlist_new_desc is None):
    sp_playlist = spotify.user_playlist(
        user=args.spotify_username, playlist_id=args.playlist_url)
    if args.youtube_playlist_new_name is None:
        args.youtube_playlist_new_name = sp_playlist['name']
    if args.youtube_playlist_new_desc is None:
        args.youtube_playlist_new_desc = sp_playlist['description']
print('Done!')

# Using gathered tracks from Spotify playlist, use ytmusicapi to search YouTube for equivalent tracks
print('Querying YouTube for Spotify tracks, may take a few minutes depending on playlist size...')
playlist_tracks_youtube = []
for sp_track in playlist_tracks_spotify:
    time_added = datetime.datetime.strptime(
        sp_track['added_at'], '%Y-%m-%dT%H:%M:%SZ')
    if(time_added > args.start_date):
        playlist_tracks_youtube.append(
            yt_helpers.get_best_yt_track_from_sp(sp_track, ytmusic))
print('Done!')

# Depending on user input, handle resulting YouTube tracks accordingly
yt_ids = [track['videoId'] for track in playlist_tracks_youtube]
if(args.result_action == 'print'):
    print('--------------\nspotify tracks\n--------------')
    for track in playlist_tracks_spotify:
        print(helpers.get_track_string_sp(track['track']))
    print('\n\n\n--------------\nyoutube tracks\n--------------')
    for track in playlist_tracks_youtube:
        print(helpers.get_track_stringget_track_string_yt(track))
elif(args.result_action == 'append'):
    yt_status, yt_dict = ytmusic.add_playlist_items(playlistId=args.youtube_playlist_id, videoIds=yt_ids, duplicates=False)
    print(yt_status)
    print('Appended to YouTube playlist')
elif(args.result_action == 'create'):
    yt_playlist_id = ytmusic.create_playlist(
        title=args.youtube_playlist_new_name, description=args.youtube_playlist_new_desc, privacy_status='PRIVATE', video_ids=yt_ids)
    print('YouTube playlist created: ', yt_playlist_id)
else:
    sys.exit('Internal error: Unknown action')
