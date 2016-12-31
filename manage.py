import os
from flask_script import Manager
from faker import Faker
from blog.database import session, Entry, User
from blog import app
from getpass import getpass
from werkzeug.security import generate_password_hash
from flask_migrate import Migrate, MigrateCommand
from blog.database import Base

manager = Manager(app)
fake = Faker()

@manager.command
def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

@manager.command
def seed():
	for i in range(25):
		entry = Entry(
			title = "Test Entry #{}".format(i),
			# get_sentences returns a tuple the size of
			# what's passed in. [0] will access the tuple
			content = fake.text()
		)
		session.add(entry)
	session.commit()

@manager.command
def adduser():
    name = input("Name: ")
    email = input("Email: ")
    if session.query(User).filter_by(email=email).first():
        print("User with that email address already exists")
        return

    password = ""
    while len(password) < 8 or password !=password2:
        password=getpass("Password: ")
        password2=getpass("Re-enter Password: ")

    user = User(name=name, email=email, password=generate_password_hash(password))
    session.add(user)
    session.commit()

class DB(object):
    def __init__(self, metadata):
        self.metadata = metadata

migrate = Migrate(app, DB(Base.metadata))
manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    manager.run()