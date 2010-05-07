Google App Engine Pusherapp Wrapper
===================================

Getting started
---------------

Request pusher credentials from <http://pusherapp.com>

First, instantiate a pusher, using your API key

    import pusherapp
    pusher = pusherapp.Pusher(app_id='your-pusher-app-id',
        key='your-pusher-api-key', secret='your-pusher-secret')
    
Next, trigger an event

    pusher['channel'].trigger('event', data={'msg': 'Hello world!'})

You probably want to run this in a taskqueue... read on for details...

Using within Google App Engine
------------------------------

Typical usage (e.g. using a taskqueue, see: <http://code.google.com/appengine/docs/python/taskqueue/>):

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
            # The task will be picked up by WorkerPushRequestHandler, below
            taskqueue.add(url='/worker/push/channel/event', params={'msg': 'Hello world!'})
        
            # ...
    
    class WorkerPushRequestHandler(webapp.RequestHandler):
    
        pusher_api_key = "{your-pusher-api-key}"
        pusher_app_id  = "{your-pusher-app-id}"
        pusher_secret  = "{your-pusher-secret}"
    
        def post(self, channel, event):
    
            # Construct pusher...
            pusher = pusherapp.Pusher(app_id=self.pusher_app_id,
                key=self.pusher_api_key, secret=self.pusher_secret)
        
            # Construct data from request parameters...
            data = dict([(arg, self.request.get(arg)) for arg in self.request.arguments()])
        
            # Trigger the event...
            result = pusher[channel].trigger(event, data=data)
        
            # Handle success/failure...
            if result.status_code >= 200 and result.status_code <= 299:
                self.response.headers["Content-Type"] = "text/plain"
                self.response.out.write("OK")
            else:
                self.error(result.status_code)
