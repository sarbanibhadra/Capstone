import os
from sqlalchemy import Column, String, Integer, DateTime, create_engine
from flask_sqlalchemy import SQLAlchemy
import json

key1 = 'DATABASE'
key2 = 'USER'
key3 = 'PASSWORD'

database_name = os.getenv(key1)
dbuser = os.getenv(key2)
dbpass = os.getenv(key3)

database_name = "postgres"
database_path = "postgresql+psycopg2://{}@localhost:5432/{}".format('sarbanidas', database_name)
DATABASE_URL = os.getenv('DATABASE_URL')

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=DATABASE_URL):
    """
    Bind a Flask application and a SQLAlchemy service.

    :param app: The Flask application instance.
    :param database_path: The database URI. Defaults to DATABASE_URL.
    """
    if database_path.startswith("postgres://"):
        database_path = database_path.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)

'''
db_drop_and_create_all()
    drops the database tables and starts fresh
    can be used to initialize a clean database
    !!NOTE you can change the database_filename variable to have multiple verisons of a database
'''
def db_drop_and_create_all():
    """
    Drop all tables and create them fresh.
    Useful for initializing a clean database.
    Note: This function can be modified to have multiple versions of a database.
    """
    print("drop all testing")
    # db.drop_all()
    print("create all")
    # db.create_all()
    print("done all")
    # add one demo row which is helping in POSTMAN test
    # movie = Movie(
    #     title='Tenat1',
    #     release_date='1.10.2021'        
    # )
    # movie.insert()

    # actor = Actor(
    #     name='Kollyn',
    #     age=23,
    #     gender='F'       
    # )
    # actor.insert()

'''
Movie
a model entity, extends the base SQLAlchemy Model
'''
class Movie(db.Model):
    # Autoincrementing, unque primary key
    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    # String Title
    title = Column(String(80), unique=True)
    release_date = Column(DateTime(), nullable=False)
    actors = Column(String(200), nullable=True)

    '''
    insert()
        inserts a new model into a database
        the model must have a unique name
        the model must have a unique id or null id
    '''
    def insert(self):
        """
        Insert a new model into the database.
        The model must have a unique name and a unique or null id.
        """
        db.session.add(self)
        print("commit all")
        db.session.commit()

    '''
    long()
        long form representation of the Drink model
    '''
    def retrive(self):
        """
        Retrieve a long-form representation of the Movie model.
        
        :return: A dictionary representing the Movie model.
        """
        return {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date,
            'actors': self.actors
        }

    '''
    delete()
        deletes a new model into a database
        the model must exist in the database
    '''
    def delete(self):
        """
        Delete the model from the database.
        The model must exist in the database.
        """
        db.session.delete(self)
        db.session.commit()

    '''
    update()
        updates a new model into a database
        the model must exist in the database
    '''
    def update(self):
        """
        Update the model in the database.
        The model must exist in the database.
        """
        db.session.commit()

'''
Actor
a model entity, extends the base SQLAlchemy Model
'''
class Actor(db.Model):
    # Autoincrementing, unque primary key
    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    name = Column(String(80), unique=True)
    age = Column(Integer().with_variant(Integer, "sqlite"), nullable=False)
    gender = Column(String(10), nullable=False)

    def retrive(self):
        """
        Retrieve a representation of the Actor model.
        
        :return: A dictionary representing the Actor model.
        """
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender
        }   

    '''
    insert()
        inserts a new model into a database
        the model must have a unique name
        the model must have a unique id or null id
    '''
    def insert(self):
        """
        Insert a new model into the database.
        The model must have a unique name and a unique or null id.
        """
        db.session.add(self)
        db.session.commit()

    '''
    delete()
        deletes a new model into a database
        the model must exist in the database
    '''
    def delete(self): 
        """
        Delete the model from the database.
        The model must exist in the database.
        """
        db.session.delete(self)
        db.session.commit()

    '''
    update()
        updates a new model into a database
        the model must exist in the database
    '''
    def update(self):
        """
        Update the model in the database.
        The model must exist in the database.
        """
        db.session.commit()
