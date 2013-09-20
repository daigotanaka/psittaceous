# The MIT License (MIT)
# 
# Copyright (c) 2013 Daigo Tanaka (@daigotanaka)
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# coding: utf-8

from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from flask import Flask, render_template, request
import os
import json

class WebServer(Flask):

    def __init__(self, name=__name__, host="0.0.0.0", port=8000, template="./template/"):
        self.name = name
        self.host = host
        self.port = port
        self.template_folder = template
        self.sockets = set()

    def create_instance(self):
        self.flask = Flask(self.name, template_folder=self.template_folder)
        self.flask.secret_key = os.urandom(24)
        self.flask.debug = True
     
        self.http_server = WSGIServer((self.host,self.port), self.wsgi_app, handler_class=WebSocketHandler)

        return self.flask

    def start(self, args=None):
        print("Server started at %s:%s" % (self.host,self.port))
        self.http_server.serve_forever()

    def wsgi_app(self, environ, start_response):  
        path = environ["PATH_INFO"]
        if path == "/websocket":
            return self.handle_websocket(environ["wsgi.websocket"])
 
        return self.flask(environ, start_response)
 
    def handle_websocket(self, ws):
        if not ws in self.sockets:
            if len(self.sockets) > 10:
                self.exceeded_max_connection(ws)
            else:
                self.sockets.add(ws)

        while True:
            message = ws.receive()
            if message is None:
                break
            message = json.loads(message)
            erase_list = []
            for socket in self.sockets:
                if not socket.socket:
                    erase_list.append(socket)
                    continue
                socket.send(json.dumps({"output": message["output"]}))
            for socket in erase_list:
                self.sockets.remove(socket)

    def exceeded_max_connection(self, ws):
        ws.send(json.dumps({"output": "Sorry, max connection reached."}))

    def update_screen(self, html=None):
        html = html or "<img src=\"http://placekitten.com/300/200\">"
        erase_list = []
        for socket in self.sockets:
            if not socket.socket:
                erase_list.append(socket)
            socket.send(json.dumps({"output": html}))
        for socket in erase_list:
            self.sockets.remove(socket)


server = WebServer()
flask = server.create_instance()


@flask.route("/")
def index():
    return render_template("index.html", port=server.port)


@flask.route("/update/", methods=["POST"])
def update():
    html = request.form["html"] or None
    server.update_screen(html=html)
    return render_template("index.html", port=server.port)


def start_server(args=None):
    server.start()

if __name__ == "__main__":
    start_server()
