#!/usr/bin/env python3
"""Example for aiohttp.web websocket server
"""

import asyncio
import os
from aiohttp.web import Application, Response, MsgType, WebSocketResponse
import argparse

import sys
sys.path.append('../')
from pyxdotool.instruction import Instruction
import json

parser = argparse.ArgumentParser(description='Plot data from output of the black hole simulation.')
parser.add_argument('--host', type=str, default='localhost')
parser.add_argument('--port', '-p', type=int, default=8000)

WS_FILE = os.path.join(os.path.dirname(__file__), 'websocket.html')
DISPLAY = ':0'

def parseRequest(data):
    def parseExtraArgs(dic):
        if 'args' in dic:
            return dic['args']
        else:
            return {}
    i = Instruction(display=':0')
    if type(data) is dict:
        data = [data]
        
    for instr in data:
        if 'mouseMoveRelative' in instr:
            dx = instr['mouseMoveRelative']['dx']
            dy = instr['mouseMoveRelative']['dy']
            args = parseExtraArgs(instr['mouseMoveRelative'])
            i.mouseMoveRelative(dx, dy, *args)
            
        elif 'mouseMove' in instr:
            x = instr['mouseMove']['x']
            y = instr['mouseMove']['y']
            args = parseExtraArgs(instr['mouseMove'])
            i.mouseMove(x, y, *args)
            
        elif 'key' in instr:
            keys = instr['key']['keys']
            args = parseExtraArgs(instr['key'])
            i.key(keys, *args)
            
        elif 'search' in instr:
            regexp = instr['search']['regexp']
            args = parseExtraArgs(instr['search'])
            i.search(regexp, **args)
            
        elif 'windowActivate' in instr:
            args = parseExtraArgs(instr['windowActivate'])
            i.windowActivate(**args)
            
        elif 'windowFocus' in instr:
            args = parseExtraArgs(instr['windowFocus'])
            i.windowFocus(**args)
            
        elif 'sleep' in instr:
            time = instr['sleep']['time']
            i.sleep(time)

        elif 'click' in instr:
            button = instr['click']['button']
            args = parseExtraArgs(instr['click'])
            i.click(button, **args)
            
        else:
            print('Unsupported instruction', instr)
    print(i.instructions)
    return i.exec()    


@asyncio.coroutine
def wsHandler(request):
    resp = WebSocketResponse()
    ok, protocol = resp.can_start(request)
    if not ok:
        with open(WS_FILE, 'rb') as fp:
            return Response(body=fp.read(), content_type='text/html')

    yield from resp.prepare(request)
    
    print('Someone joined.')
    for ws in request.app['sockets']:
        ws.send_str('Someone joined')
    request.app['sockets'].append(resp)

    while True:
        msg = yield from resp.receive()

        if msg.tp == MsgType.text:
            obj = json.loads(msg.data)
            retVal = parseRequest(obj)

            for ws in request.app['sockets']:
                if ws is resp:
                    ws.send_str(json.dumps(retVal))
        else:
            break

    request.app['sockets'].remove(resp)
    print('Someone disconnected.')
    for ws in request.app['sockets']:
        ws.send_str('Someone disconnected.')
    return resp


@asyncio.coroutine
def init(loop, args):
    app = Application(loop=loop)
    app['sockets'] = []
    app.router.add_route('GET', '/', wsHandler)

    handler = app.make_handler()
    srv = yield from loop.create_server(handler, args.host, args.port)
    print("Server started at http://{}:{}".format(args.host, args.port))
    return app, srv, handler


@asyncio.coroutine
def finish(app, srv, handler):
    for ws in app['sockets']:
        ws.close()
    app['sockets'].clear()
    yield from asyncio.sleep(0.1)
    srv.close()
    yield from handler.finish_connections()
    yield from srv.wait_closed()


if __name__ == '__main__':
    args = parser.parse_args()
    loop = asyncio.get_event_loop()
    app, srv, handler = loop.run_until_complete(init(loop, args))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(finish(app, srv, handler))
