import json
import logging
import msgpack
import os
import re
import tempfile
import time

from io import BytesIO
from flask import Flask
from fluent import handler

class StructuredMessage(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __str__(self):
        return '%s' % (json.dumps(self.kwargs))

app = Flask(__name__)
@app.route("/")
def hello():

    response = ""
    # response += "<i>If everyone is moving forward together, then success takes care of itself.<i>" – Henry Ford"
    response += "<html>"
    response += "<head>"
    response += "<style> .center { display: block; margin-left: auto; margin-right: auto; width: 50%; } </style>"
    response += "</head>"

    response += "<body>"
    response += "<img src='https://www.bynder.com/static/3.0/img/fb-logo-large.jpg' class='center' />"
    response += "</body>"
    response += "</html>"

    return response

@app.route("/globvars")
def globvars():
    response = "APP_ENV is " + re.sub(r'\W+', '', os.environ.get('APP_ENV'))
    response += "AWS_REGION is " + re.sub(r'\W+', '', os.environ.get('AWS_REGION'))

    return response

@app.route("/health")
def healthy():
    response = ""
    response = "I am ok"

    return response

@app.route("/log-console")
def log_console():
    start = time.time()

    jsondata = '{"name":"John", "age":30, "city":"New York"}'
    for x in range(100000):
        print(jsondata)
    end = time.time()

    duration = (end - start)
    return "Console output (100000 json lines): " + str(duration)

@app.route("/log-disk")
def log_disk():
    start = time.time()

    jsondata =  '{"name":"John", "age":30, "city":"New York"}'
    fp = tempfile.TemporaryFile()
    for x in range(100000):
        fp.write(jsondata.encode())
    fp.close()
    end = time.time()

    duration = (end - start)
    return "Disk output (100000 json lines): " + str(duration)

@app.route("/logging-example")
def logme():
    _ = StructuredMessage   # optional, to improve readability

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    ts = int(time.time())

    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logging.info(_(correlation_id='f5980a81-026c-4bfd-b451-2ddee1254f19', log_level='INFO', message='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed sit amet arcu eu orci tempus eleifend.\nThis sentence will appear on a newline.'))

    return "Wrote some JSON to STDOUT"

@app.route("/fluent-tcp-log")
def logtcp():
    custom_format = {
      'host': '%(hostname)s',
      'where': '%(module)s.%(funcName)s',
      'type': '%(levelname)s',
      'stack_trace': '%(exc_text)s'
    }

    logging.basicConfig(level=logging.INFO)
    l = logging.getLogger('fluent.test')
    h = handler.FluentHandler(
        'app.follow',
        host=os.environ.get('HOST_IP'),
        port=24224,
        buffer_overflow_handler=overflow_handler)
    formatter = handler.FluentRecordFormatter(custom_format)
    h.setFormatter(formatter)
    l.addHandler(h)
    l.info({
      'from': 'userA',
      'to': 'userB'
    })
    l.info('{"from": "userC", "to": "userD"}')
    l.info("This log entry will be logged with the additional key: 'message'.")
    l.info("This log entry will be logged over\r\nmultiple\r\nlines.")

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

def overflow_handler(pendings):
    unpacker = msgpack.Unpacker(BytesIO(pendings))
    for unpacked in unpacker:
        print(unpacked)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int("8080"))
