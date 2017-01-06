import os
import unittest
import multiprocessing
import time
from urllib.parse import urlparse

from werkzeug.security import generate_password_hash
from splinter import Browser

#Config app to use testing db
os.environ["CONFIG_PATH"] = "blog.config.TestingConfig"

from blog import app
from blog.database import Base, engine, session, User

class TestViews(unittest.TestCase):
    def setUp(self):
        """Test Setup"""
        self.browser = Browser("phantomjs")

        #Set up the tables
        Base.metadata.create_all(engine)

        #Create an example user
        self.user = User(name="Alice", email="alice@example.com",
                         password=generate_password_hash("test"))
        session.add(self.user)
        session.commit()

        self.process = multiprocessing.Process(target=app.run,
                                               kwargs={"port:8080"})
        self.process.start()
        time.sleep(1)

    def tearDown(self):
        """Test Teardown"""
        #Remove the tables and their data 
        self.process.terminate()
        session.close()
        engine.dispose()
        Base.metadata.drop_all(engine)
        self.browser.quit()

    if __name__ == "__main__":
        unittest.main()