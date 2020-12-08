import os

from app import app
from app import db
from flask_migrate import Migrate
from flask_migrate import MigrateCommand
from flask_script import Manager


database_url = os.getenv('DATABASE_URL')

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()