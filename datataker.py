import websocket
import json
import threading
import time

ws_url = 'wss://gateway.discord.gg/?v=6&encording=json'
token = 'MTI1NTIwMDk4ODcyMjEwMjMwNA.GHGMlD.5eXRX-OdH3fs5zAAjdDQr4wKx8loyZZBUI-I0M'

def get_json_request(ws, request):
    ws.send(json.dumps(request))

def got_json_response(ws):
    response = ws.recv()
    if response:
        return json.loads(response)
    return None

def heartbeat(ws, interval):
    print('Heartbeat begin')
    while True:
        time.sleep(interval)
        heartbeatJSON = {
            "op": 1,
            "d": None
        }
        get_json_request(ws, heartbeatJSON)
        print("Heartbeat sent")

def connect():
    ws = websocket.WebSocket()
    ws.connect(ws_url)
    print('WebSocket connected')

    event = got_json_response(ws)
    if event and event.get('op') == 10:
        heartbeat_interval = event['d']['heartbeat_interval'] / 1000

        payload = {
            'op': 2,
            'd': {
                'token': token,
                'properties': {
                    '$os': 'windows',
                    '$browser': 'chrome',
                    '$device': 'pc'
                }
            }
        }
        get_json_request(ws, payload)

        heartbeat_thread = threading.Thread(target=heartbeat, args=(ws, heartbeat_interval))
        heartbeat_thread.start()

        event_loop(ws)

def event_loop(ws):
    while True:
        event = got_json_response(ws)
        if event and event.get('t') == 'MESSAGE_CREATE':
            author = event['d']['author']['username']
            content = event['d']['content']
            print(f"{author}: {content}")


if __name__ == "__main__":
    connect()
