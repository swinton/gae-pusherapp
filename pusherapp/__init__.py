#!/usr/bin/env python

"""
A Google App Engine wrapper for the pusherapp service (http://www.pusherapp.com).

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
            
            # Trigger some event, using a taskqueue
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

"""

import logging, sys

from django.utils import simplejson as json
from google.appengine.api import urlfetch

host   = 'api.pusherapp.com'
port   = 80
key    = False
secret = False

class Pusher():
    __key = False
    __channels = {}
    __globals = {}

    def __init__(self, **kwargs):
        # Read in globals...
        self.__globals = globals()
        
        # Get (required) key...
        if kwargs.has_key('key'):
            self.__key = kwargs['key']
        elif self.__globals['key']:
            self.__key = self.__globals['key']
        else:
            # Key is required but not specified, raise exception
            raise NameError('KeyRequired', 'Key is required, but not specified')
        
        # Get (optional) channel
        if kwargs.has_key('channel'):
            self.__make_channel(kwargs['channel'])
    
    def __getitem__(self, key):
        if not self.__channels.has_key(key):
            # if channel doesn't exist, make one...
            return self.__make_channel(key)
        return self.get_channel(key)
        
    def __make_channel(self, channel):
        self.__channels[channel] = self.Channel(channel, self)
        return self.__channels[channel]
        
    def add_channel(self, channel):
        return self.__make_channel(channel)
    
    def get_channel(self, channel):
        return self.__channels[channel]
    
    def get_key(self):
        return self.__key
    
    class Channel():
        __pusher = False
        __name = False
        
        def __init__(self, channel, pusher):
            self.__pusher = pusher
            self.__name = channel
            
        def trigger(self, event, data={}):
            host = globals()['host']
            key = self.__pusher.get_key()
            
            # Construt the pusher end point...
            pusher_end_point = 'http://%s/app/%s/channel/%s' % (host, key, self.__name)
            
            # JSON-encode the data...
            data = json.dumps({'event': event, 'data': data})
            
            # Log this event...
            logging.debug("Triggering %s on the %s channel (%s, %s)\n" % (event, self.__name, pusher_end_point, data))
            
            # Fire the event, RESTfully...
            return urlfetch.fetch(
                url=pusher_end_point,
                payload=data,
                method=urlfetch.POST,
                headers={'Content-Type': 'application/json'}
            )