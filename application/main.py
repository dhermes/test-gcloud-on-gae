import datetime
import logging
import time

from google.appengine.api.app_identity import get_application_id
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.webapp.util import login_required
import webapp2

from gcloud.datastore import SCOPE
from gcloud.datastore import connection
from oauth2client import client


APP_NAME = get_application_id()
IMPLICIT_CREDENTIALS = client.GoogleCredentials.get_application_default()
SCOPED_CREDENTIALS = IMPLICIT_CREDENTIALS.create_scoped(SCOPE)
CONNECTION = connection.Connection(credentials=SCOPED_CREDENTIALS)
if APP_NAME is None:
    DATASET = None
else:
    DATASET = CONNECTION.dataset(APP_NAME)


class Foo(ndb.Model):
    now = ndb.DateTimeProperty(auto_now_add=True)
    nickname = ndb.BlobProperty(indexed=True)
    email = ndb.BlobProperty(indexed=True)
    user_id = ndb.BlobProperty(indexed=True)


def make_entity(user):
    entity = DATASET.entity('Foo')
    entity['now'] = datetime.datetime.utcnow()
    entity['nickname'] = user.nickname()
    entity['email'] = user.email()
    entity['user_id'] = user.user_id()
    start = time.time()
    entity.save()
    duration = time.time() - start
    logging.debug('Saving %r took %f seconds.', entity.key(), duration)
    return entity


def make_ndb_entity(user):
    foo_entity = Foo(nickname=user.nickname(),
                     email=user.email(),
                     user_id=user.user_id())
    start = time.time()
    foo_entity.put()
    duration = time.time() - start
    logging.debug('Saving %r took %f seconds.', foo_entity.key,
                  duration)
    return foo_entity


class MainHandler(webapp2.RequestHandler):

    @login_required
    def get(self):
        user = users.get_current_user()
        entity = make_entity(user)
        key_id = entity.key().id()
        message = 'Key saved: %d' % (key_id,)
        self.response.write(message)


class NDBHandler(webapp2.RequestHandler):

    @login_required
    def get(self):
        user = users.get_current_user()
        foo_entity = make_ndb_entity(user)
        key_id = foo_entity.key.id()
        message = 'Key saved: %d' % (key_id,)
        self.response.write(message)



app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/ndb', NDBHandler),
], debug=True)
