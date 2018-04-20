import os
import requests
import json
from collections import defaultdict
from flask import Flask, render_template, session, redirect, request, url_for, flash
from flask_script import Manager, Shell
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, PasswordField, BooleanField, SelectMultipleField, ValidationError, IntegerField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from flask_sqlalchemy import SQLAlchemy
import random
from flask_migrate import Migrate, MigrateCommand
from threading import Thread
from werkzeug import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# Imports for login management
from flask_login import LoginManager, login_required, logout_user, login_user, UserMixin, current_user

# Configure base directory of app
basedir = os.path.abspath(os.path.dirname(__file__))

# Application configurations
app = Flask(__name__)
app.static_folder = 'static'
app.config['SECRET_KEY'] = 'hardtoguessstring'
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL') or "postgresql://jack:jack@localhost/SI364projectplanjrclegg"
# Lines for db setup so it will work as expected
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set up Flask debug and necessary additions to app
manager = Manager(app)
db = SQLAlchemy(app) # For database use
migrate = Migrate(app, db) # For database use/updating
manager.add_command('db', MigrateCommand) # Add migrate command to manager

## Set up Shell context so it's easy to use the shell to debug
# Define function
def make_shell_context():
    return dict( app=app, db=db)
# Add function use to manager
manager.add_command("shell", Shell(make_context=make_shell_context))

# Login configurations setup
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app) # set up login manager

# spotify api SETUP
client_id = "5f84fa73d2fa4b7fb3ce8abd6d882af6"
client_secret = "a50d80f6fb754aaf9b0f24f9fcf952cc"
redirect_uri = "http://localhost:5000"
oauth_token = ""
## DB load function
## Necessary for behind the scenes login manager that comes with flask_login capabilities! Won't run without this.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) # returns User object or None
# Special model for users to log in
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    playlists = db.relationship('Playlist', backref= 'User')
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True
song_rankings = db.Table('song_rankings',
    db.Column('song_id', db.Integer, db.ForeignKey('songs.id')),
    db.Column('ranking_id', db.Integer, db.ForeignKey('rankings.id'))
    )

user_playlists = db.Table('user_playlists',
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlists.id')),
    db.Column('song_id', db.Integer, db.ForeignKey('songs.id'))
    )

# playlist model, one user to many playlists
class Playlist(db.Model):
    __tablename__  = "playlists"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))
    userID = db.Column(db.Integer, db.ForeignKey('users.id'))
    songs = db.relationship('Song', secondary = user_playlists, backref = db.backref('playlists', lazy = 'dynamic'), lazy = 'dynamic')
    def __repr__(self):
        return "Playlist ID: {}, User ID: {}".format(self.id, self.userID)
# song model, many songs to many playlists
class Song(db.Model):
    __tablename__ = "songs"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))
    artist = db.Column(db.String(64))
    ranks = db.relationship('Rankings', secondary = song_rankings, backref = db.backref('songs', lazy = 'dynamic'), lazy = 'dynamic')
    def __repr__(self):
        return "{} by {}".format(self.name, self.artist)
# rankings model, many ratings to many songs
class Rankings(db.Model):
    __tablename__ = "rankings"
    id = db.Column(db.Integer, primary_key = True)
    songID = db.Column(db.Integer, db.ForeignKey('songs.id'))
    userID = db.Column(db.Integer, db.ForeignKey('users.id'))
    rank = db.Column(db.Integer)
    def __repr__(self):
        return "User: {}, Song: {}, Ranked: {}".format(self.userID, self.songID, self.rank)

# helper functions:
def searchSong(song):
    headers ={"Content-Type": "application/json", "Authorization": "Bearer " + oauth_token}
    params = { 'q': song, 'type': 'track'} #q can be any artist name, Muse is the default in the Spotify API
    search_object = requests.get('https://api.spotify.com/v1/search?', headers=headers, params = params).json()
    try:
        dictReturn = {"artist" : search_object['tracks']['items'][0]['artists'][0]['name'], "title" : search_object['tracks']['items'][0]['name']}
    except:
        dictReturn = False
    return dictReturn
def get_or_create_song(title_in, artist_in, rank_in = None):
    song = db.session.query(Song).filter_by(name = title_in, artist = artist_in).first()
    if song:
        return song
    else:
        song = Song(name = title_in, artist = artist_in)
        if rank_in is not None:
            rank = Rankings(songID = song.id, userID = current_user.id, rank = rank_in)
            song.ranks.append(rank)
        db.session.add(song)
        db.session.commit()
        return song

def addSongToPlaylist(formSongs, playlist_in, user_in):
    song = formSongs.split(',')[0].strip().rstrip()
    rank = formSongs.split(',')[1].strip().rstrip()
    data = searchSong(song)
    if data != False:
        song = get_or_create_song(title_in = data['title'], artist_in = data['artist'], rank_in = rank)
        playlist_in.songs.append(song)
        get_or_create_ranking(playlist_in.name, song.name, user_in, rank)
    else:
        flash("Error adding song: {}".format(song))
    return
def get_or_create_playlist(name_in, user_in, songs):
    playlist = Playlist.query.filter_by(name = name_in, userID = user_in.id).first()
    if playlist:
        return playlist
    else:
        playlist = Playlist(name = name_in, userID = user_in.id)
        song = songs.split(',')[0].strip().rstrip()
        rank = songs.split(',')[1].strip().rstrip()
        data = searchSong(song)
        if data != False:
            song = get_or_create_song(data['title'], data['artist'])
            playlist.songs.append(song)
            get_or_create_ranking(playlist.name, song.name, user_in, rank)
        else:
            flash("Error adding song: {}".format(song))
        db.session.add(playlist)
        db.session.commit()
        return playlist
def getPlaylistByTitle(title_in, user_in):
    playlist = Playlist.query.filter_by(name = title_in, userID = int(user_in.id)).first()
    return playlist
def getSongByTitle(title_in):
    song = Song.query.filter_by(name = title_in).first()
    return song
def get_or_create_ranking(playlist_title, song_title, user_in, rank_in):
    playlist = getPlaylistByTitle(playlist_title, user_in)
    song = getSongByTitle(song_title)
    ranking = Rankings.query.filter_by(songID = song.id, userID = user_in.id, rank = rank_in).first()
    if ranking:
        flash ("Already has a rank! Not changed!")
        return ranking
    else:
        playlist_in = getPlaylistByTitle(playlist_title, user_in)
        song_in = getSongByTitle(song_title)
        ranking = Rankings(songID = song_in.id, userID = user_in.id, rank = rank_in)
        song_in.ranks.append(ranking)
        db.session.add(ranking)
        db.session.commit()
        return ranking
def getRankBySong(song_in):
    rank = Rankings.query.filter_by(songID = song_in.id, userID = current_user.id).first()
    return rank
# forms to submit
class createPlaylistForm(FlaskForm):
    name = StringField("What would you like to call it?", validators = [Required()])
    song_picks = StringField("Give us a song & rank to start the playlist with! (Format: song, rank)")
    submit = SubmitField("Create playlist!")
    def validate_song_picks(self, field):
        song = field.data.split(',')[0].strip().rstrip()
        rank = field.data.split(',')[1].strip().rstrip()
        if not song or not rank:
            raise ValidationError("Song not added correctly, Enter the form as specified")

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')
class SearchForm(FlaskForm):
    query = StringField("Search for a song!", validators = [ Required() ])
    submit = SubmitField("Submit")

class RegistrationForm(FlaskForm):
    email = StringField('Email:', validators=[Required(),Length(1,64),Email()])
    username = StringField('Username:',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Usernames must have only letters, numbers, dots or underscores')])
    password = PasswordField('Password:',validators=[Required(),EqualTo('password2',message="Passwords must match")])
    password2 = PasswordField("Confirm Password:",validators=[Required()])
    submit = SubmitField('Register User')

    #Additional checking methods for the form
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken')

class editSongForm(FlaskForm):
    newRank = IntegerField("Rerank this song: ")
    submit = SubmitField("Submit change")

    def validate_newRank(self, field):
        if (type(field.data)) != type(5):
            raise ValidationError("New rank must be an integer!")
class deleteButton(FlaskForm):
    playlists = SelectMultipleField("Which playlist should we delete it from?")
    delete = SubmitField("Are you sure to delete this?")
class deletePlaylistForm(FlaskForm):
    delete = SubmitField("Delete this playlist?")
class addSongsForm(FlaskForm):
    song_picks = StringField("Want to add a song? (Please add like this: song, rank)")
    submit = SubmitField("Add song")

def validateDeleteForm(form):
    try:
        return form.playlists.data
    except:
        return False
def validateUpdateRankForm(form):
    try:
        return form.newRank.data
    except:
        return False
########################
#### View functions ####
########################

# will present a welcome message, a link to the user login page, as well as all
# the playlists for the currently logged in user and the ability to click these playlists
@app.route('/', methods = ['GET', 'POST'])
def home():
    try:
        playlists = Playlist.query.filter_by(userID = current_user.id)
    except:
        playlists = False
    form = createPlaylistForm(request.form)
    if request.method == "POST" and form.validate_on_submit():
        playlist = get_or_create_playlist(form.name.data, current_user, form.song_picks.data)
        addSongToPlaylist(form.song_picks.data, playlist, current_user)
        return redirect(url_for('createPlaylist', name = playlist.name))
    else:
        form = createPlaylistForm()
        searchForm = SearchForm()
        return render_template("index.html", playlists = playlists, form = form, searchForm = searchForm)

# when a user clicks on a playlist from the home page, they will be directed here
# where they can see all the songs on the playlist, and have the ability to click
# a link to add a song to the playlist, delete the song from the playlist,
# or edit a current song's ranking in the playlist
@app.route('/playlist_<name>', methods = ['GET', 'POST'])
@login_required
def createPlaylist(name):
    playlist = getPlaylistByTitle(name, current_user)
    songs = playlist.songs
    delete_form = deletePlaylistForm()
    return render_template("playlist_view.html", songs = songs, playlistName = name, form = delete_form)

# when a user attempts to edit a song from the above view function, they will
# be directed here, where they can see the song's information and current ranking
# and a form to update the song's ranking within the playlist
@app.route('/edit_song_<name>', methods = ['GET', 'POST'])
@login_required
def editSong(name):
    form = deleteButton(request.form)
    playlists = Playlist.query.filter_by(userID = current_user.id)
    song = getSongByTitle(name)
    song_instances = []
    for playlist in playlists:
        if song in playlist.songs:
            song_instances.append((song, playlist))
    playlist_names = [(playlist[1].id, playlist[1].name) for playlist in song_instances]
    form.playlists.choices = playlist_names
    if validateDeleteForm(form):
        ids = form.playlists.data
        for id in ids:
            playlist = Playlist.query.filter_by(userID = current_user.id, id = int(id)).first()
            song = getSongByTitle(name)
            playlist_songs = [song_in for song_in in playlist.songs if song_in is not song]
            playlist.songs = playlist_songs
            db.session.commit()
        return redirect(url_for('createPlaylist', name = playlist.name))
    form = editSongForm(request.form)
    if request.method=="POST" and form.validate_on_submit():
        rank = getRankBySong(song)
        rank.rank = form.newRank.data
        db.session.commit()
    form = editSongForm()
    delete_form = deleteButton()
    delete_form.playlists.choices = playlist_names
    rank = getRankBySong(song)
    return render_template("edit_song.html", form = form, songs = song_instances, song_name = name, delete_form = delete_form, rank = rank.rank)


# if on the createPlaylist view the user wishes to add a song, they will be brought
# to this page where there will be a form that they can add a song to any of their playlists
@app.route('/add_songs_<pname>', methods = ['GET', 'POST'])
@login_required
def addSongs(pname):
    form = addSongsForm(request.form)
    playlist = getPlaylistByTitle(pname, current_user)
    if request.method == "POST" and form.validate_on_submit():
        addSongToPlaylist(form.song_picks.data, playlist, current_user)
        return redirect(url_for('createPlaylist', name = pname))
    form = addSongsForm()
    return render_template('add_songs.html', form = form, playlist = playlist, pname = pname)
#def addSongToPlaylist(formSongs, playlist_in, user_in)


# this is a public page that will allow anybody to see the songs that are currently
# rated in the top 5 on the website
@app.route('/all_songs', methods=['GET', 'POST'])
def allSongs():
    if (type(request.args.get('query'))) != type(None):
        search = request.args.get('query')
        song_in = getSongByTitle(search)
    else:
        song_in = None
    songRanks = []
    songs = Song.query.all()
    for song in songs:
        ranks = Rankings.query.filter_by(songID = song.id)
        for rank in ranks:
            songRanks.append((song.name, rank.rank))
    averageCounts = {}
    for song in songRanks:
        if song[0] in averageCounts:
            averageCounts[song[0]]['counts'] += 1
            averageCounts[song[0]]['total'] += song[1]
        else:
            averageCounts[song[0]] = {}
            averageCounts[song[0]]['counts'] = 1
            averageCounts[song[0]]['total'] = song[1]
    return render_template('global_rankings.html', counts = averageCounts, song = song_in)

@app.route('/delete_playlist_<pname>', methods = ['GET', 'POST'])
@login_required
def deletePlaylist(pname):
    form = deletePlaylistForm(request.form)
    if form.validate_on_submit():
        try:
            playlist = Playlist.query.filter_by(name = pname, userID = current_user.id).first()
            db.session.delete(playlist)
            db.session.commit()
            flash("Playist deleted!")
            return redirect(url_for('home'))
        except:
            flash("Error deleting playlist!")
            return redirect(url_for('home'))
    else:
        return redirect(url_for('createPlaylist', name = pname))
# route to allow users to login after coming from the home page, will redirect
# back to the homepage
@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(url_for('home'))
        flash('Invalid username or password.')
    return render_template('login.html',form=form)

# route to allow users to logout, which will then redirect back to the home page
@app.route('/logout', methods = ['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('home'))

# route to allow users to register to join the website, which will then redirect
# back to the homepage
@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,username=form.username.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You can now log in!')
        return redirect(url_for('login'))
    return render_template('register.html',form=form)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    db.create_all()
    app.run(use_reloader = True, debug = True)
    #manager.run()
