import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import app, db

database_url = os.getenv('DATABASE_URL')

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()