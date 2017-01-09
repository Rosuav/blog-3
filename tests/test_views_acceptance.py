import os
import unittest
import multiprocessing
import time
from urllib.parse import urlparse

from werkzeug.security import generate_password_hash
from splinter import Browser
from faker import Faker

#Config app to use testing db
os.environ["CONFIG_PATH"] = "blog.config.TestingConfig"
fake = Faker()

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

    def test_login_correct(self):
        self.browser.visit("http://127.0.0.1:8080/login")
        self.browser.fill("email", "alice@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080")

    def test_login_incorrect(self):
        self.browser.visit("http://127.0.0.1:8080/login")
        self.browser.fill("email", "non_registered@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/login")

    def test_new_entry(self):
        test_login_correct()
        self.browser.visit("http://127.0.0.1:8080/entry/add")
        self.browser.fill("title", fake.text())
        self.browser.fill("entry", fake.text())
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080")

    if __name__ == "__main__":
        unittest.main()

# TODO: Investigate why 0 tests are running when run with
# PYTHONPATH="." python tests/test_views_acceptance.py