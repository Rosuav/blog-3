import os
from flask_script import Manager
from faker import Faker
from blog.database import session, Entry
from blog import app

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

if __name__ == "__main__":
    manager.run()