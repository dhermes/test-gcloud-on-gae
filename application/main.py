import webapp2

from gcloud import datastore


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
