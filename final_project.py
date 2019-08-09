#!/usr/bin/env python2

from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   jsonify,
                   url_for,
                   session,
                   make_response,
                   flash)
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Artist, Name, User
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import random
import string
import datetime
import json
import httplib2
import requests

app = Flask(__name__)
app.secret_key = 'super secret key'
CLIENT_ID = json.loads(open(
    'client_secret_Google.json', 'r').read())['web']['client_id']


# Connect to the database
engine = create_engine('sqlite:///artists.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session_db = DBSession()


# Create the login page
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(50))
    session['state'] = state
    return render_template('signin.html', STATE=state)


# Create the Google connect login
@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
    This function connects the user to the app using google oauth sign in.
    It handles all communications with the
    server in order to validate the user through safe protocols.
    :return:
    """
    # Validate state token
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret_Google.json',
                                             scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)  # gives error
    except FlowExchangeError:
        response = make_response(json.dumps(
                                 'Failed to upgrade the authorization code.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = session.get('access_token')
    stored_gplus_id = session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
                                 'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use
    session['access_token'] = credentials.access_token
    session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    session['username'] = data['name']
    session['picture'] = data['picture']
    session['email'] = data['email']

    user_id = getUserID(session['email'])
    if not user_id:
        user_id = createUser(session)
    session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += session['username']
    output += '!</h1>'
    output += '<img src="'
    output += session['picture']
    output += ' "style = "width: 300px;height: 300px;border-radius: 150px; \
              -webkit-border-radius: ''150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % session['username'])
    print("Done!")
    return output


# Create Google login disconnect
@app.route('/gdisconnect')
def gdisconnect():
    """
    This method disconnects the user if they have signed in through google.
    It deletes all current information
    that the app needs about the user so that user privacy is maintained.
    :return:
    """
    access_token = session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del session['access_token']
        del session['gplus_id']
        del session['username']
        del session['email']
        del session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
                                 'Failed to revoke token for given user.',
                                 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Create the logout page
@app.route('/logout')
def logout():
    if 'username' in session:
        gdisconnect()
        flash("You have successfully been logged out.")
        return redirect(url_for('showArtists'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showArtists'))


# Create user in database
def createUser(session):
    """
    This helper method is used to create a user within the database.
    It takes in the session dictionary so that
    the user can be added to the database.
    :param session:
    :return:
    """
    newUser = User(name=session['username'], email=session['email'],
                   picture=session['picture'])
    session_db.add(newUser)
    session_db.commit()
    user = session_db.query(User).filter_by(email=session['email']).one()
    return user.id


# Get user info from database
def getUserInfo(user_id):
    """
    This is the helper method that returns the user information.
    It takes in the user id so that the user can be returned.
    :param user_id:
    :return:
    """
    user = session_db.query(User).filter_by(id=user_id).one()
    return user


# Get user ID (email) for reference
def getUserID(email):
    """
    This is the helper method that is able to get the user id given the email
    information. It is used when the email is given within the session
    dictionary.
    :param email:
    :return:
    """
    try:
        user = session_db.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Create the default page to display all types artists
@app.route('/')
@app.route('/artist/')
def showArtists():
    artists = session_db.query(Artist).all()
    return render_template('artists.html', artists=artists, session=session)


# Create the page to display all artists of a specific type
@app.route('/artist/<int:artist_id>/')
def showStyle(artist_id):
    artist = session_db.query(Artist).filter_by(id=artist_id).one()
    items = session_db.query(Name).filter_by(type_id=artist_id).all()
    return render_template('names.html', items=items, artist=artist)


# Create the page to display the description of a specific artist of a
# specific type
@app.route('/artist/<int:artist_id>/<int:name_id>')
def showDescription(artist_id, name_id):
    """
    This function displays description of something.
    :param artist_id:
    :param name_id:
    :return:
    """
    artist = session_db.query(Artist).filter_by(id=artist_id).one()
    description = session_db.query(Name).filter_by(id=name_id).one()
    return render_template('descriptions.html', artist=artist,
                           description=description)


# JSON APIs to view Artist Information
@app.route('/artist/<int:artist_id>/JSON')
def artistTypeJSON(artist_id):
    artistType = session_db.query(Artist).filter_by(id=artist_id).one()
    items = session_db.query(Name).filter_by(
        type_id=artist_id).all()
    return jsonify(name=[i.serialize for i in items])


@app.route('/artist/JSON')
def artistJSON():
    artists = session_db.query(Artist).all()
    return jsonify(artist=[i.serialize for i in artists])


# Create a new artist
@app.route('/artist/new/', methods=['GET', 'POST'])
def newArtist():
    types = session_db.query(Artist).all()
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        print('POST')
        if request.form['type'] == 'other':
            newArtist = Artist(style=request.form['other'])
            session_db.add(newArtist)
            session_db.commit()
            newName = Name(name=request.form['name'],
                           description=request.form['description'],
                           artist=newArtist, user_id=session['user_id'])
            session_db.add(newName)
            session_db.commit()
            flash('New Type %s Successfully Created' % newArtist.name)
        else:
            artist = session_db.query(Artist).filter_by(
                                              id=request.form['type']).one()
            newName = Name(name=request.form['name'], description=request.form[
                           'description'], artist=artist,
                           user_id=session['user_id'])
            session_db.add(newName)
            session_db.commit()
        flash('New artist %s Successfully Created' % newName.name)
        return redirect(url_for('showArtists'))
    else:
        print('GET')
        return render_template('newArtist.html', types=types)


# Edit an artist
@app.route('/artist/<int:name_id>/edit/', methods=['GET', 'POST'])
def editArtist(name_id):
    artist = session_db.query(Artist).all()
    name = session_db.query(Name).filter_by(id=name_id).one()
    if 'username' not in session:
        flash('Please login to edit this item.')
        return redirect('/login')
    if getUserInfo(name.user_id).name != session['username']:
        flash('You are not authorized to edit this item.')
        return render_template('artists.html')
    if request.method == 'POST':
        if request.form['name']:
            name.name = request.form['name']
        if request.form['description']:
            name.description = request.form['description']
        if request.form['type']:
            name.artist_id = request.form['type']
        session_db.add(name)
        session_db.commit()
        return redirect(url_for('showArtists'))
    else:
        return render_template('editArtists.html', name=name, types=artist)


# Delete an artist
@app.route('/artist/<int:name_id>/delete/', methods=['GET', 'POST'])
def deleteArtist(name_id):
    artist = session_db.query(Artist).all()
    name = session_db.query(Name).filter_by(id=name_id).one()
    if 'username' not in session:
        flash('Please login to delete this item.')
        return redirect('/login')
    if getUserInfo(name.user_id).name != session['username']:
        flash('You are not authorized to delete this item.')
        return render_template('artists.html')
    if request.method == 'POST':
        session_db.delete(name)
        flash('%s Successfully Deleted' % name.name)
        session_db.commit()
        return redirect(url_for('showArtists'))
    else:
        return render_template('deleteArtist.html', name=name, types=artist)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
