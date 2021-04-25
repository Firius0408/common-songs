import os
import sys
import json
import datetime
from concurrent.futures import ThreadPoolExecutor, wait
from typing import Dict, List
import spotifywebapi

users = {}
userplaylists = {}
playlisttracks = {}

def getUser(userString: str) -> Dict:
    global users
    userString = userString.replace('spotify:user:', '')
    if userString in users.keys():
        return users[userString]
    else:
        temp = sp.getUser(userString)
        users[userString] = temp
        return temp

def getUserPlaylists(user: Dict) -> List[Dict]:
    global userplaylists
    iid = user['id']
    if iid in userplaylists.keys():
        return userplaylists[iid]
    else:
        temp = sp.getUserPlaylists(user)
        userplaylists[iid] = temp
        return temp


def getTracksFromItem(playlist: Dict) -> List[Dict]:
    global playlisttracks
    iid = playlist['id']
    if iid in playlisttracks.keys():
        return playlisttracks[iid]
    else:
        temp = sp.getTracksFromItem(playlist)
        playlisttracks[iid] = temp
        return temp


def appendTracksFromItem(playlist: Dict, tracks: List[Dict]) -> None:
    global playlisttracks
    iid = playlist['id']
    if iid in playlisttracks.keys():
        tracks.append(playlisttracks[iid])
    else:
        temp = sp.getTracksFromItem(playlist)
        playlisttracks[iid] = temp
        tracks.append(temp)


def commonSongsUsersThread(userid: str, tracksss: List, executor: ThreadPoolExecutor):
    user = getUser(userid)
    playlists = getUserPlaylists(user)
    trackss = []
    futures = []
    for playlist in playlists:
        if playlist['owner']['id'] != userid or "Top Songs of " in playlist['name'] or playlist['id'] == '5eS0KgG63Opb1EqOE63Gpa':
            continue

        futures.append(executor.submit(appendTracksFromItem, playlist, trackss))

    wait(futures)
    tracksss.append(trackss)

def commonSongsUsers(userids: List[str], playlistid: str = None) -> None:
    userids = [i.replace('spotify:user:', '') for i in userids]
    if len(userids) < 2:
        print('You need at least 2 users bruh')
        return

    print('Pulling songs...')
    tracksss = []
    futures = []
    for userid in userids:
        futures.append(executor.submit(commonSongsUsersThread, userid, tracksss, executor))

    wait(futures)
    print('Finding common songs...')
    trackuri = []
    for trackss in tracksss:
        trackuri.append([track['track']['uri']
                         for tracks in trackss for track in tracks if track['track'] is not None])

    commonuri = set(trackuri[0])
    for i in trackuri[1:]:
        commonuri.intersection_update(i)

    if None in commonuri:
        commonuri.remove(None)

    if (playlistid):
        tempplaylist = sp.getPlaylistFromId(playlistid)
        playlisttracks = getTracksFromItem(tempplaylist)
        playlisttracksset = {i['track']['uri'] for i in playlisttracks}
        newtracksset = commonuri - playlisttracksset
        if newtracksset:
            print('Adding to playlist...')
            botuser.addSongsToPlaylist(playlistid, list(newtracksset))
            changes.append(userids)
            print('Finished')
        else:
            print('Playlist already up to date')
    else:
        names = [getUser(i)['display_name'] for i in userids]
        name = 'Common Songs between ' + ' and '.join(names)
        print('Creating playlist...')
        playlistid = botuser.createPlaylist(name)['id']
        commonsongs.append((userids, playlistid))
        data['commonsongs'] = commonsongs
        if __name__ == '__main__':
            with open(sys.path[0] + '/data.json') as f:
                json.dump(data, f, indent=4, separators=(',', ': '))
        else:
            with open('./data.json') as f:
                json.dump(data, f, indent=4, separators=(',', ': '))

        botuser.addSongsToPlaylist(playlistid, list(commonuri))
        print('Playlist created\nid: %s' % playlistid)


def commonSongsUsersAll() -> None:
    for commonsong in commonsongs:
        while True:
            print(', '.join(commonsong[0]))
            try:
                commonSongsUsers(commonsong[0], commonsong[1])
            except Exception as err:
                print(err)
            else:
                break


sp = spotifywebapi.Spotify(os.getenv('SPOTIFY_CLIENT_ID'), os.getenv('SPOTIFY_CLIENT_SECRET'))
refreshtoken = os.getenv('SPOTIFY_REFRESHTOKEN')
botuser = sp.getAuthUser(refreshtoken)
if __name__ == '__main__':
    with open(sys.path[0] + '/data.json') as json_file:
        data = json.load(json_file)

    commonsongs = data['commonsongs']
    changes = []
    print('Starting at %s\n' % datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
    executor = ThreadPoolExecutor()
    commonSongsUsersAll()
    if changes:
        print('\nPlaylists for the following users have changed:')
        for userids in changes:
            print(', '.join(userids))

    executor.shutdown()
    print('\nFinished at %s' % datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))

else:
    with open('./data.json') as json_file:
        data = json.load(json_file)

    commonsongs = data['commonsongs']
