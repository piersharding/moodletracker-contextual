from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch
import feedparser
from django.utils import simplejson

# an issue URL looks like  http://tracker.moodle.org/si/jira.issueviews:issue-xml/MDL-22951/MDL-22951.xml
MOODLE_TRACKER = 'http://tracker.moodle.org/si/jira.issueviews:issue-xml/'

class TrackerFailHandler(webapp.RequestHandler):
  def get(self):
    self.response.out.write("""
    <html><body>
    <h1>moodletracker - invalid format</h1>
    </body></html>
    """)
    self.response.set_status(404, 'moodletracker - invalid format')
    return

class TrackerHandler(webapp.RequestHandler):
  def get(self, tracker_id):
    
    url = MOODLE_TRACKER + tracker_id + '/' + tracker_id + '.xml'
    result = urlfetch.fetch(url)
    if result.status_code != 200:
        self.response.set_status(404, 'moodletracker - tracker not found')
        return
    
    dom = feedparser.parse(result.content)
    data = {}
    if dom != None:
       if dom.has_key('items'):
            d = dom['items'][0]
            for i in ('title', 'summary', 'link', 'status', 'version', 'component', 'key',
                       'created', 'type', 'votes', 'assignee', 'comment', 'updated', 'resolution', 'priority', 'reporter'):
                data[i] = d[i].replace('"', '&quot;').replace("\n", '')
    
    els = []
    for i in data:
        els.append( '"' + i + '":["' + data[i] + '"]')
    txt = ','.join(els);
    self.response.out.write('{'+txt+'}')
    self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
    self.response.headers["Access-Control-Allow-Origin"] = '*'
    self.response.set_status(200)
    return

def main():
  application = webapp.WSGIApplication([
    ('/tracker/(MDL\-\d+?)', TrackerHandler),
    ('/tracker.*?', TrackerFailHandler),
  ], debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
