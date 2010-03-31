Google App Engine Pusherapp Wrapper
===================================

Getting started
---------------

Request pusher credentials from <http://pusherapp.com>

Instantiate a pusher, using your API key

    import pusherapp
    pusher = pusherapp.Pusher(key='your-pusher-key')
    
Trigger an event

    Pusher['channel'].trigger('event', data={msg => 'Hello world!'})


Using within Google App Engine
------------------------------

Typical usage (e.g. using a taskqueue, see: http://code.google.com/appengine/docs/python/taskqueue/):

    import pusherapp

    from google.appengine.api import urlfetch
    from google.appengine.api.labs import taskqueue
    from google.appengine.ext import webapp

    class MyWebAppRequestHandler(webapp.RequestHandler):
    
        def get(self):
            # ...
    
        def post(self):
            # ...
        
            # Trigger some event with pusherapp, using a taskqueue
            taskqueue.add(url='/worker/push/channel/event', params={'msg': 'Hello world!'})
        
            # ...
    
    class WorkerPushRequestHandler(webapp.RequestHandler):
    
        def post(self, channel, event):
    
            # Construct pusher...
            pusher = pusherapp.Pusher(key=self.pusher_api_key)
        
            # Construct data from request parameters...
            data = dict([(arg, self.request.get(arg)) for arg in self.request.arguments()])
        
            # Trigger the event...
            result = pusher[channel].trigger(event, data=data)
        
            # Handle success/failure...
            if result.status_code >= 200 and result.status_code <= 299:
                self.response.headers["Content-Type"] = "text/plain"
                self.response.out.write("OK")
                #self.response.out.write("\nchannel: %s, event: %s, data: %s" % (channel, event, str(data)))
            else:
                self.error(result.status_code)
