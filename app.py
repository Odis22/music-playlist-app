from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Playlist, PlaylistSong
from flask import session as login_session
import random
import string

# oauth imports
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from werkzeug import secure_filename

app = Flask(__name__)
APPLICATION_NAME = "Playlist catalog project"

engine = create_engine('sqlite:///musicplaylist.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly
    # logout, let's strip out the information before the equals sign in our
    # token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output

app.route('/fbdisconnect')


def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).all()[0]
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# playlist = {'name': 'uplifting music', 'id': '1'}

# playlists = [{'name': 'uplifting music', 'id': '1'}, {'name':'Romantic
# music', 'id':'2'},{'name':'Angry workout music',
# 'id':'3'},{'name':'Dance hits', 'id':'4'}]


# songs = [ {'name':'Rise up', 'artist':'Andra Day', 'time':'4.13','album' :'Cheers to the fall', 'id':'1'}, {'name':'thinking out loud','artist':'Ed Sheeran', 'time':'4.41', 'album':'X','id':'2'},{'name':'My time', 'artist':'fabolous','time':'4.35', 'album':'beauty','id':'3'},{'name':'Teach me how to dougie', 'artist':'cali swag district', 'time':'3.34', 'album':'Rap dance hits','id':'4'} ]
# song =  {'name':'Rise up','artist':'Andra Day','time':'4.13','album' :'Cheers to the fall'}
# songs = []

@app.route('/playlist/<int:playlist_id>/song/JSON')
def playlistJSON(playlist_id):
    playlist = session.query(Playlist).filter_by(id=playlist_id).one()
    songs = session.query(PlaylistSong).filter_by(
        playlist_id=playlist_id).all()
    return jsonify(PlaylistSongs=[s.serialize for s in songs])


@app.route('/playlist/<int:playlist_id>/song/<int:song_id>/JSON')
def playlistSongJSON(playlist_id, song_id):
    Playlist_Song = session.query(PlaylistSong).filter_by(id=song_id).one()
    return jsonify(Playlist_Song=Playlist_Song.serialize)


@app.route('/playlist/JSON')
def playlistsJSON():
    playlists = session.query(Playlist).all()
    return jsonify(playlists=[p.serialize for p in playlists])

# Show all playlist


@app.route('/')
@app.route('/playlist/')
def showPlaylists():
    playlists = session.query(Playlist).all()
    return render_template('Home.html', playlists=playlists)


# Create a new playlist
@app.route('/playlist/new/', methods=['GET', 'POST'])
def newPlaylist():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newPlaylist = Playlist(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newPlaylist)
        flash('New Store %s Successfully Created' % newPlaylist.name)
        session.commit()
        return redirect(url_for('showPlaylists'))
    else:
        return render_template('newPlaylist.html')


# Edit playlist

@app.route('/playlist/<int:playlist_id>/edit/', methods=['GET', 'POST'])
def editPlaylist(playlist_id):
    editedPlaylist = session.query(
    Playlist).filter_by(id=playlist_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedPlaylist.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this playlist. Please create your own playlist in order to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
       if request.form['name']:
            editedPlaylist.name = request.form['name']
        return redirect(url_for('showplaylists', playlist_id=playlist_id))
    else:
        return render_template('editPlaylist.html', playlist=editedPlaylist)

    # return "This page will be for editing a playlist"
    
@app.route('/playlist/<int:playlist_id>/delete/', methods=['GET', 'POST'])
def deletePlaylist(playlist_id):
    deletedPlaylist = session.query(
        Playlist).filter_by(id=playlist_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if deletedPlaylist.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this playlist. Please create your own playlist in order to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(deletedPlaylist)
        flash('%s Successfully Deleted' % deletedPlaylist)
        session.commit()
        return redirect(url_for('showplaylists', playlist_id=playlist_id))
    else:
        return render_template('deletePlaylist.html', playlist=deletedPlaylist)
            
# show a playlist song
@app.route('/playlist/<int:playlist_id>/')
@app.route('/playlist/<int:playlist_id>/song/')
def showSong(playlist_id):
    playlist = session.query(Playlist).filter_by(id=playlist_id).one()
    creator = getUserInfo(playlist.user_id)
    songs = session.query(PlaylistSong).filter_by(
        playlist_id=playlist_id).all()
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('playlistsongs.html', songs=songs, playlist=playlist, creator=creator) 
    else: 
        return render_template('song.html', songs=songs, playlist=playlist, creator=creator)
# return 'This page is a song from a playlist %s' % playlist_id
    
@app.route('/playlist/<int:playlist_id>/song/new/', methods=['GET', 'POST'])
def newPlaylistSong(playlist_id):
    if 'username' not in login_session:
        return redirect('/login')
    playlist = session.query(Playlist).filter_by(id=playlist_id).one()
    if login_session['user_id'] != playlist.user_id:
        return "<script>function myFunction() {alert('You are not authorized to add playlist songs. Please create your own account to add songs');}</script><body onload='myFunction()''>"
        if request.method == 'POST':
            newSong = PlaylistSong(name=request.form['name'], artist=request.form[
                           'artist'], genre=request.form['genre'], playlist_id=playlist_id, user_id=login_session['user_id'] )
        session.add(newSong)
        session.commit()
        flash('New song %s Successfully added' % (newSong.name))
        return redirect(url_for('showPlaylists', playlist_id=playlist_id))
    else:
        return render_template('newplaylistsong.html', playlist_id=playlist_id)
        

    # return 'This page is for adding a new song to the library %s' %playlist_id

@app.route('/playlist/<int:playlist_id>/song/<int:song_id>/edit', methods=['GET', 'POST'])
def editPlaylistSong(playlist_id, song_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedSong = session.query(PlaylistSong).filter_by(id=song_id).one()
    playlist = session.query(Playlist).filter_by(id=playlist_id).one()
    if login_session['user_id'] != playlist.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit song info on this playlist. Please create your own playlist in order to edit items.');}</script><body onload='myFunction()''>"
        return redirect('/login')
    if request.method == 'POST':
        if request.form['name']:
            editedSong.name = request.form['name']
        if request.form['artist']:
            editedSong.artist = request.form['artist']
        if request.form['genre']:
            editedSong.genre = request.form['genre']
        session.add(editedSong)
        session.commit()
        return redirect(url_for('showPlaylists', playlist_id=playlist_id))
    else:
        return render_template('editplaylistsong.html', playlist_id=playlist_id, song_id=song_id, song=editedSong)

    # return 'This page is for editing information about song 
    
@app.route('/playlist/<int:playlist_id>/song/<int:song_id>/delete',methods=['GET', 'POST'])
def deletePlaylistSong(playlist_id, song_id):
    if 'username' not in login_session:
        return redirect('/login')
    playlist = session.query(Playlist).filter_by(id=playlist_id).one()
    songtodelete = session.query(PlaylistSong).filter_by(id=song_id).one()
    if login_session['user_id'] != playlist.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete songs. Please create your own playlist in order to delete songs.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(songtodelete)
        session.commit()
        flash('Song Successfully Deleted')
        return redirect(url_for('song', playlist_id=playlist_id))
    else:
        return render_template('deleteplaylistSong.html', song=songtodelete)
 # return "This page is for deleting a song
 
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showPlaylists'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showPlaylists'))
    


if __name__ == '__main__':
    app.secret_key = '1234'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
