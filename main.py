import os
import tornado.ioloop
import tornado.web
import tornado.options
import functools
import logging
import signal
import time
import boto.sqs
import boto.ses
import boto.dynamodb2

from tornado.httpserver import HTTPServer

from Handlers import *

#Tornado app configuration

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("user-login.html")

class UserRegHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("user_register.html")

class UserProfileHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("user-profile.html")

class UserMapHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("map.html")

class ShelterInHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("user_login.html")

class ShelterRegHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("user_login.html")

class ShelterMainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("user_check_in.html")

class ShelterListHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("shelter-list.html")

class ShelterProfileHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("shelter-profile.html")

class ShelterMapHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("shelter-map.html")


def get_url_list():

    main_handler_url_set = [
        #show the main page
        tornado.web.URLSpec(r"/", MainHandler),
    ]

    user_handler_url_set = [
        # create a new user #post
        tornado.web.URLSpec(r"/create",UserHandler),
    ]


    auth_handler_url_set = [
        # log in #post
        tornado.web.URLSpec(r"/auth/login",AuthHandler),
        # log out #delete
        tornado.web.URLSpec(r"/auth/logout",AuthHandler),
    ]


    center_handler_url_set = [
        # check a person in #post
        tornado.web.URLSpec(r"/center/checkin", CenterHandler),
        # register a person into waitlist
        tornado.web.URLSpec(r"/center/waitlist", CenterHandler),
        # check a person out #delete
        tornado.web.URLSpec(r"/center/checkout", CenterHandler),
    ]

    data_handler_url_set = [
        # get data of users #put
        tornado.web.URLSpec(r"/data/get", DataHandler),
        # get the list of entire data
        tornado.web.URLSpec(r"/list/get", ListHandler),
    ]

    web_handler_url_set = [
        #shelter login
        tornado.web.URLSpec(r"/shelter/login", ShelterInHandler),
        #shelter check people in page
        tornado.web.URLSpec(r"/shelter/main", ShelterMainHandler),
        #shelter register page
        tornado.web.URLSpec(r"/shelter/register", ShelterRegHandler),
        #shelter people list
        tornado.web.URLSpec(r"/shelter/list", ShelterListHandler),
        #shelter profile 
        tornado.web.URLSpec(r"/shelter/profile",ShelterProfileHandler),
        #user sign up
        tornado.web.URLSpec(r"/user/register", UserRegHandler),
        #user profile
        tornado.web.URLSpec(r"/user/profile", UserProfileHandler),
        #map
        tornado.web.URLSpec(r"/user/map", UserMapHandler),
        #map
        tornado.web.URLSpec(r"/shelter/map", ShelterMapHandler),
    ]

    message_handler_url_set = [
        #send message via cellphone, post
        tornado.web.URLSpec(r"/send", MessageHandler)
    ]

    update_handler_url_set=[
        #update the info
        tornado.web.URLSpec(r"/update", UpdateHandler)
    ]


    url_list = [
        main_handler_url_set,
        user_handler_url_set,
        auth_handler_url_set,
        center_handler_url_set,
        data_handler_url_set,
        web_handler_url_set,
        message_handler_url_set,
        update_handler_url_set,
    ]

    full_url_list = []

    for url_set in url_list:
        for url in url_set:
            full_url_list.append(url)

    return full_url_list


def get_settings():

    
    return {
        'login_url': '/auth/login',
        'debug': True
    }



def get_dynamo():

    conn = boto.dynamodb2.connect_to_region(
        config.AWS_REGION,
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_ACCESS_KEY)

    return conn


def get_app():

    url_list = get_url_list()
    settings = get_settings()
    dynamo = get_dynamo()

    application = tornado.web.Application (
        url_list,
        dynamo = dynamo,
        **settings
    )
    
    return application

def get_ioloop():

    ioloop = tornado.ioloop.IOLoop.instance()
    return ioloop


def stop_server(server):

    logging.info('stop server')
    server.stop()



#Tornado server run loop

def main():

    application = get_app()
    tornado.options.parse_command_line()
    server = HTTPServer(application)
    server.listen(8000)
    logging.info('starting server')
    ioloop = get_ioloop()
    try:
        ioloop.start()
    except KeyboardInterrupt:
        stop_server(server)

    logging.info('stop server')


if __name__=='__main__':
    main()
