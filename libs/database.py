import arrow
import psycopg2
import sys
import time
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from libs import database_helpers as dbhelpers
import urllib, json
from settings import settings

class database:

    def __init__(self):
        self.con = self.connect_db()


    def connect_db(self):
        try:
            con = psycopg2.connect(dbname=settings.DBNAME, user=settings.DBUSER, host=settings.DBHOST,password=settings.DBPASSWD)
            return con
        except:
            time.sleep(0.5)
            return self.connect_db()