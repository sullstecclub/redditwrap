import praw
import socket, ssl
from threading import Thread
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from urlparse import parse_qs,urlparse
from cgi import parse_header, parse_multipart
import sys
from pprint import pprint
import json


class Handler(BaseHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		self.send_header('Access-Control-Allow-Origin', '*')
		self.end_headers()
		params = parse_qs(self.path[self.path.find('?')+1:])
		r = praw.Reddit(user_agent='redditwrap')
		req = params['req'][0]
		
		if req == "comments":
			submission = r.get_submission(params['url'][0])
			self.wfile.write("yeah man we're good")

		if req == "submit":
			submissions = r.get_subreddit('test').get_hot(limit=5)
			comment = params['c'][0]
			submissionsList = list(submissions)
			submissionsList[0].add_comment(comment)

		elif req == "posts":
			print "Getting Reddit Posts\n\n"
			submissions = r.get_subreddit('funny').get_hot(limit=15)
			res = []
			for post in submissions:
				res.append({
					'num_comments': post.num_comments,
					'url': post.url,
					'title': post.title,
					'user': str(post.author),
					'subreddit': str(post.subreddit),
					'time': post.created_utc,
					'nsfw': post.over_18
				})
				pprint(vars(post))
			self.wfile.write(json.dumps(res))

		elif req == "login":
			username = params['username'][0]
			password = params['password'][0]
			r.login(username, password)
			

	def do_POST(self):
		postvars = self.parse_POST()
		print postvars

	def parse_POST(self):
		ctype, pdict = parse_header(self.headers['content-type'])
		if ctype == 'multipart/form-data':
			postvars = parse_multipart(self.rfile, pdict)
		elif ctype == 'application/x-www-form-urlencoded':
			length = int(self.headers['content-length'])
			postvars = parse_qs(
			self.rfile.read(length),
			keep_blank_values=1)
		else:
			postvars = {}
		self.wfile.write(self.path)
		return postvars

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
	pass

def serve_on_port(port):
	server = ThreadingHTTPServer(("172.16.241.188",port), Handler)
	server.serve_forever()

Thread(target=serve_on_port, args=[1111]).start()
serve_on_port(2222)