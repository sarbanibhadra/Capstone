import os
from flask import Flask, render_template, request, jsonify, abort, session, redirect, url_for
from sqlalchemy import exc
import json 
import flask_cors
from flask_cors import CORS
from flask_cors import cross_origin
from authlib.integrations.flask_client import OAuth
from urllib.parse import quote_plus, urlencode
from database.models import db_drop_and_create_all, setup_db, Movie, Actor
from auth.auth import AuthError, requires_auth, auth_register
import requests
from requests.structures import CaseInsensitiveDict
from os import environ as env
from flask_wtf import Form
from forms import *

def create_app(test_config=None):
    """
    Create and configure the Flask application.
    
    Args:
        test_config (dict, optional): Test configuration. Defaults to None.
    
    Returns:
        Flask: The configured Flask application.
    """
    app = Flask(__name__, template_folder='template')
    print("APP_SECRET_KEY : " + os.environ['APP_SECRET_KEY'])
    app.secret_key = os.environ['APP_SECRET_KEY'].encode('utf8')
    app.app_context().push()
    setup_db(app)
    CORS(app)
    oauth = OAuth(app)
    
    # NOTE: Uncomment the following line on the first run to drop all records and start the DB from scratch
    # db_drop_and_create_all()
    
    auth_register(oauth)

    @app.route("/login")
    def login():
        """
        Login route to redirect to the Auth0 authorization URL.
        
        Returns:
            Response: Redirect response to the Auth0 authorization URL.
        """
        return oauth.auth0.authorize_redirect(
            redirect_uri=url_for('callback', _external=True)
        )

    @app.route("/callback", methods=["GET", "POST"])
    def callback():
        """
        Callback route to handle the response from Auth0.
        
        Returns:
            Response: Redirect response to the home page.
        """
        token = oauth.auth0.authorize_access_token()
        print("token")
        print(token)
        session["user"] = token
        return redirect("/")

    @app.route("/")
    def home():
        """
        Home route to render the home page.
        
        Returns:
            Response: Rendered home page template.
        """
        return render_template('home.html', session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

    @app.route("/logout")
    def logout():
        """
        Logout route to clear the session and redirect to the Auth0 logout URL.
        
        Returns:
            Response: Redirect response to the Auth0 logout URL.
        """
        session.clear()
        return redirect(
            "https://" + env.get("AUTH0_DOMAIN") 
            + "/v2/logout?"
            + urlencode(
                {
                    "returnTo": url_for("home", _external=True),
                    "client_id": env.get("AUTH0_CLIENT_ID"),
                },
                quote_via=quote_plus,
            )
        )

    @app.route('/actors', methods=['GET'])
    @requires_auth(session, 'get:actor')
    def get_actors(jwt):
        """
        Route to get all actors.
        
        Args:
            jwt (str): JSON Web Token.
        
        Returns:
            Response: Rendered actors page template.
        """
        if request.method == 'GET':
            print("Inside get actors") 
            all_actors = Actor.query.all()
            actors = []
            if len(all_actors) == 0:
                abort(404)
        
            print(len(all_actors))
            print(type(all_actors[0]))
            for d in all_actors:
                actors.append(d.retrive())
        
            return render_template('actors.html', actors=actors)

    @app.route('/actors/create', methods=['GET', 'POST'])
    @requires_auth(session, 'post:actor')
    def create_actor(jwt):
        """
        Route to create a new actor.
        
        Args:
            jwt (str): JSON Web Token.
        
        Returns:
            Response: Redirect to actors page or rendered new actor form template.
        """
        if request.method == 'GET':
            print("Inside actor create get method")
            form = ActorForm()
            return render_template('forms/new_actor.html', form=form)
        elif request.method == 'POST':
            print("Inside actor create POST method")
            try:
                data = request.form
                print(data.getlist('name')[0])
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print(message)
            name = data.getlist('name')[0]
            print(name)
            age = data.getlist('age')[0]
            print(age)
            gender = data.getlist('gender')[0]
            print(gender)
            if data == 'null':
                abort(400)
            try:
                new_actor = Actor(name=name, age=age, gender=gender)
                new_actor.insert()
                new_actor = [new_actor.retrive()]
                return redirect('/actors')
            except:
                return json.dumps({'success': False, 'error': "An error occurred"}), 500

    @app.route('/actors/update', methods=['GET', 'POST'])
    @requires_auth(session, 'patch:actor')
    def update_actor(jwt):
        """
        Route to update an existing actor.
        
        Args:
            jwt (str): JSON Web Token.
        
        Returns:
            Response: Redirect to actors page or rendered update actor form template.
        """
        print("Inside actor update method")
        if request.method == 'GET':
            print("Inside actor update get method")
            all_actors = Actor.query.all()
            actors = []

            if len(all_actors) == 0:
                abort(404)
        
            for d in all_actors:
                actors.append(d.retrive())
            form = ActorForm()
            return render_template('forms/update_actor.html', form=form, actors=actors)
        if request.method == 'POST':
            data = request.form
            id = data.getlist('actors')[0]
            actor = Actor.query.filter(Actor.id == id).one_or_none()

            if actor is None:
                abort(404)

            try:
                if data.getlist('name')[0] != "":
                    actor.name = data.getlist('name')[0]
                
                if data.getlist('age')[0] != "":
                    actor.age = data.getlist('age')[0]

                if data.getlist('gender')[0] != "":
                    actor.gender = data.getlist('gender')[0]
                
                actor.update()
                actor = [actor.retrive()]
                return redirect('/actors')
            except:
                return json.dumps({'success': False, 'error': "An error occurred"}), 500

    @app.route('/actors/delete', methods=['GET', 'POST', 'DELETE'])
    @requires_auth(session, 'delete:actor')
    def delete_actor(jwt):
        """
        Route to delete an existing actor.
        
        Args:
            jwt (str): JSON Web Token.
        
        Returns:
            Response: Redirect to actors page or rendered delete actor form template.
        """
        print("inside delete")
        if request.method == 'GET':
            print("Inside actor delete get method")
            all_actors = Actor.query.all()
            actors = []

            if len(all_actors) == 0:
                abort(404)
        
            for d in all_actors:
                actors.append(d.retrive())
            return render_template('forms/delete_actor.html', actors=actors)
        elif request.method == 'POST':
            option = request.form['actors']
            actor = Actor.query.filter(Actor.id == option).one_or_none()
            
            if actor is None:
                abort(404)

            try:
                actor.delete()
                return redirect('/actors')
            except:
                return json.dumps({'success': False, 'error': "An error occurred"}), 500

    @app.route('/movies', methods=['GET'])
    @requires_auth(session, 'get:movie')
    def get_movies(jwt):
        """
        Route to get all movies.
        
        Args:
            jwt (str): JSON Web Token.
        
        Returns:
            Response: Rendered movies page template.
        """
        if request.method == 'GET':
            print("Inside get movies") 
            all_movies = Movie.query.all() 
            movies = []

            if len(all_movies) == 0:
                abort(404)
        
            for d in all_movies:
                dr = d.retrive()
                if dr.get('actors') is not None:
                    actor = Actor.query.filter(Actor.id == dr.get('actors')).one_or_none()
                    dr.update({"actors": actor.retrive().get('name')})
                movies.append(dr)
                
            return render_template('movies.html', movies=movies)

    @app.route('/movies/create', methods=['GET', 'POST'])
    @requires_auth(session, 'post:movie')
    def create_movie(jwt):
        """
        Route to create a new movie.
        
        Args:
            jwt (str): JSON Web Token.
        
        Returns:
            Response: Redirect to movies page or rendered new movie form template.
        """
        if request.method == 'GET':
            form = MovieForm()
            all_actors = Actor.query.all()
            actors = []

            if len(all_actors) == 0:
                abort(404)
        
            for d in all_actors:
                actors.append(d.retrive())
            return render_template('forms/new_movie.html', form=form, actors=actors)
        elif request.method == 'POST':
            try:
                data = request.form
                title = data.getlist('title')[0]
                release_date = data.getlist('release_date')[0]
                actors = data.getlist('actors')[0]
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print(message)
                abort(400)

            if data == 'null':
                abort(400)
            try:
                new_movie = Movie(title=title, release_date=release_date, actors=actors)
                new_movie.insert()
                new_movie = [new_movie.retrive()]
                return redirect('/movies')
            except:
                return json.dumps({'success': False, 'error': "An error occurred"}), 500

    @app.route('/movies/update', methods=['GET', 'POST'])
    @requires_auth(session, 'patch:movie')
    def update_movie(jwt):
        """
        Route to update an existing movie.
        
        Args:
            jwt (str): JSON Web Token.
        
        Returns:
            Response: Redirect to movies page or rendered update movie form template.
        """
        if request.method == 'GET':
            all_movies = Movie.query.all()
            movies = []

            if len(all_movies) == 0:
                abort(404)
        
            for d in all_movies:
                movies.append(d.retrive())
            form = MovieForm()
            return render_template('forms/update_movie.html', form=form, movies=movies)
        if request.method == 'POST':
            data = request.form
            id = data.getlist('movies')[0]
            movie = Movie.query.filter(Movie.id == id).one_or_none()

            if movie is None:
                abort(404)

            try:
                if data.getlist('title')[0] is not None:
                    movie.title = data.getlist('title')[0]
                
                if data.getlist('release_date')[0] is not None:
                    movie.release_date = json.dumps([data.getlist('release_date')[0]])
                    
                movie.update()
                movie = [movie.retrive()]
                return redirect('/movies')
            except:
                return json.dumps({'success': False, 'error': "An error occurred"}), 500

    @app.route('/movies/delete', methods=['GET', 'POST', 'DELETE'])
    @requires_auth(session, 'delete:movie')
    def delete_movie(jwt):
        """
        Route to delete an existing movie.
        
        Args:
            jwt (str): JSON Web Token.
        
        Returns:
            Response: Redirect to movies page or rendered delete movie form template.
        """
        if request.method == 'GET':
            all_movies = Movie.query.all()
            movies = []

            if len(all_movies) == 0:
                abort(404)
        
            for d in all_movies:
                movies.append(d.retrive())
            return render_template('forms/delete_movie.html', movies=movies)
        elif request.method == 'POST':
            option = request.form['movies']
            movie = Movie.query.filter(Movie.id == option).one_or_none()

            if movie is None:
                abort(404)

            try:
                movie.delete()
                return redirect('/movies')
            except:
                return json.dumps({'success': False, 'error': "An error occurred"}), 500

    # Error handling
    @app.errorhandler(401)
    def unprocessable(error):
        """
        Error handler for 401 Unauthorized error.
        
        Args:
            error (Exception): The caught exception.
        
        Returns:
            Response: Rendered error page template.
        """
        return render_template('error.html', error=error, message="401-You are not authorized!!!")

    @app.errorhandler(422)
    def unprocessable(error):
        """
        Error handler for 422 Unprocessable Entity error.
        
        Args:
            error (Exception): The caught exception.
        
        Returns:
            Response: Rendered error page template.
        """
        return render_template('error.html', error=error, message="422-Unprocessable!!")

    @app.errorhandler(404)
    def resource_not_found(error):
        """
        Error handler for 404 Not Found error.
        
        Args:
            error (Exception): The caught exception.
        
        Returns:
            Response: Rendered error page template.
        """
        return render_template('error.html', error=error, message="404-Resource not found!!")

    @app.errorhandler(400)
    def bad_request(error):
        """
        Error handler for 400 Bad Request error.
        
        Args:
            error (Exception): The caught exception.
        
        Returns:
            Response: Rendered error page template.
        """
        return render_template('error.html', error=error, message="400-Bad Request!!")

    @app.errorhandler(405)
    def method_not_allowed(error):
        """
        Error handler for 405 Method Not Allowed error.
        
        Args:
            error (Exception): The caught exception.
        
        Returns:
            Response: Rendered error page template.
        """
        return render_template('error.html', error=error, message="405-Method Not Allowed!!")

    @app.errorhandler(403)
    def permission_not_present(error):
        """
        Error handler for 403 Forbidden error.
        
        Args:
            error (Exception): The caught exception.
        
        Returns:
            Response: Rendered error page template.
        """
        return render_template('error.html', error=error, message="403-Permission Not Found!!")

    @app.errorhandler(500)
    def error_present(error):
        """
        Error handler for 500 Internal Server Error.
        
        Args:
            error (Exception): The caught exception.
        
        Returns:
            Response: Rendered error page template.
        """
        return render_template('error.html', error=error, message="500-An error occurred!!")

    return app

app = create_app()

if __name__ == '__main__':
    app.run()
