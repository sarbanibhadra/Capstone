import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import app
from database.models import db

MIGRATION_DIR = os.path.join('app', 'migrations')

migrate = Migrate(app, db, MIGRATION_DIR)
print("test point1")

manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':

    print("test point2")
    manager.run()