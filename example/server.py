#!/usr/bin/env python

import logging

from BaseHTTPServer import HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler
from ConfigParser import ConfigParser
from urlparse import urlparse
from urllib import urlencode
from urlparse import parse_qsl
from StringIO import StringIO
from gzip import GzipFile

from sanction import Client

def get_config():
	config = ConfigParser({}, dict)
	config.read("example.ini") 

	c = config._sections["sanction"]
	del c["__name__"]

	if "http_debug" in c:
		c["http_debug"] = c["http_debug"] == "true"

	return config._sections["sanction"]


logging.basicConfig(format="%(message)s")
l = logging.getLogger(__name__)
config = get_config()


class Handler(BaseHTTPRequestHandler):
	route_handlers = {
		"/": "handle_root",
		"/login/google": "handle_google_login",
		"/oauth2/google": "handle_google",
		"/login/facebook": "handle_facebook_login",
		"/oauth2/facebook": "handle_facebook",
		"/login/foursquare": "handle_foursquare_login",
		"/oauth2/foursquare": "handle_foursquare",
		"/login/deviantart": "handle_deviantart_login",
		"/oauth2/deviantart": "handle_deviantart",
		"/login/stackexchange": "handle_stackexchange_login",
		"/oauth2/stackexchange": "handle_stackexchange"
	}

	def do_GET(self):
		url = urlparse(self.path)
		if url.path in self.route_handlers:
			getattr(self, self.route_handlers[url.path])(
			dict(parse_qsl(url.query)))
		else:
			self.send_response(404)


	def handle_root(self, data):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write('''
			login with: <a href="/oauth2/google">Google</a>,
			<a href="/oauth2/facebook">Facebook</a>,
			<a href="/oauth2/foursquare">Foursquare</a>,
			<a href="/oauth2/deviantart">Deviant Art</a>,
			<a href="/oauth2/stackexchange">Stack Exchange</a>
		''')


	def handle_google(self, data):
		self.send_response(302)
		c = Client(auth_endpoint="https://accounts.google.com/o/oauth2/auth")
		self.send_header("Location", c.get_auth_uri(config["google.client_id"],
			scope=("email",),
			redirect_uri="http://localhost:8080/login/google"))
		self.end_headers()


	def handle_google_login(self, data):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.log_message(self.path)
		self.end_headers()

		c = Client(token_endpoint="https://accounts.google.com/o/oauth2/token",
			resource_endpoint="https://www.googleapis.com/oauth2/v1",
			redirect_uri="http://localhost:8080/login/google")
		c.auth_received(data, config["google.client_id"],
			config["google.client_secret"])

		self.wfile.write("Access token: %s<br>" % c.access_token)

		data = c.fetch("/userinfo")
		self.wfile.write("First name: %s<br>" % data["name"])
		self.wfile.write("Last name: %s<br>" % data["family_name"])
		self.wfile.write("Email: %s<br>" % data["email"])

		
	def handle_facebook(self, data):
		self.send_response(302)
		c = Client(auth_endpoint="https://www.facebook.com/dialog/oauth",
				redirect_uri="http://localhost:8080/login/facebook")
		self.send_header("Location", c.get_auth_uri(
			config["facebook.client_id"],
			scope=config["facebook.scope"].split(","),
			scope_delim=",",))
		self.end_headers()


	def handle_facebook_login(self, data):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.log_message(self.path)
		self.end_headers()

		c = Client(
			token_endpoint="https://graph.facebook.com/oauth/access_token",
			resource_endpoint="https://graph.facebook.com",
			redirect_uri="http://localhost:8080/login/facebook")
		c.auth_received(data, config["facebook.client_id"],
			config["facebook.client_secret"])

		d = c.fetch("/me")

		self.wfile.write("Access token: %s<br>" % c.access_token)
		self.wfile.write("First name: %s<br>" % d["first_name"])
		self.wfile.write("Last name: %s<br>" % d["last_name"])
		self.wfile.write("Email: %s<br>" % d["email"])

		# to see a wall post in action, uncomment this
		"""
		c.request("/feed", method="POST", body=urlencode({
		"message": "test post from py-sanction"
		}))
		"""
		d = c.fetch("/me/feed", data=urlencode({
			"message": "test post from py-sanction"
		}))


	def handle_foursquare(self, data):
		c = Client(Foursquare, get_config())
		self.send_response(302)
		self.send_header("Location", c.flow.authorization_uri())
		self.end_headers()

	def handle_deviantart(self, data):
		c = Client(DeviantArt, get_config())
		self.send_response(302)
		self.send_header("Location", c.flow.authorization_uri())
		self.end_headers()

	def handle_stackexchange(self, data):
		c = Client(StackExchange, get_config())
		self.send_response(302)
		self.send_header("Location", c.flow.authorization_uri())
		self.end_headers()


	def handle_foursquare_login(self, data):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.log_message(self.path)
		self.end_headers()

		c = Client(Foursquare, get_config())
		cred = c.flow.authorization_received(data)

		d = c.request("/users/24700343")

		self.wfile.write("Access token: %s<br>" % cred.access_token)
		self.wfile.write("Type: %s<br>" % cred.token_type)
		self.wfile.write("Expires in: %d<br>" % cred.expires_in)

		self.wfile.write(d)

	def handle_deviantart_login(self, data):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.log_message(self.path)
		self.end_headers()

		c = Client(DeviantArt, get_config())
		cred = c.flow.authorization_received(data)

		d = c.request("/placebo")

		self.wfile.write("Access token: %s<br>" % cred.access_token)
		self.wfile.write("Type: %s<br>" % cred.token_type)
		self.wfile.write("Expires in: %d<br>" % cred.expires_in)

		self.wfile.write(d)


	def handle_stackexchange_login(self, data):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.log_message(self.path)
		self.end_headers()

		c = Client(StackExchange, get_config())
		cred = c.flow.authorization_received(data)

		d = c.request("/me", body=urlencode({
			"site": "stackoverflow"
		}))

		self.wfile.write("<!DOCTYPE html>")
		self.wfile.write("<head><meta charset=\"utf-8\"/></head><body>")
		self.wfile.write("Access token: %s<br>" % cred.access_token)
		self.wfile.write("Type: %s<br>" % cred.token_type)
		self.wfile.write("Expires in: %d<br>" % cred.expires_in)

		# stackexchange gzips all data
		h = StringIO(d)
		gzip_data = GzipFile(fileobj=h)
		d = gzip_data.read()
		gzip_data.close()
		self.wfile.write(d)
		self.wfile.write("</body></html>")


def main(): 
	l.setLevel(1)
	server = HTTPServer(("", 8080), Handler)
	l.info("starting server. press <ctrl>+c to exit")
	server.serve_forever()

if __name__=="__main__":
	main()

