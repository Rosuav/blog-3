import os
from flask_script import Manager
from loremipsum import get_sentences

from blog import app

manager = Manager(app)

@manager.command
def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

@manager.command
def seed():
	for i in range(25):
		entry = Entry(
			title = "Test Entry #{}".format(i),
			content = get_sentences(1)
		)
		session.add(entry)
	session.commit()

if __name__ == "__main__":
    manager.run()