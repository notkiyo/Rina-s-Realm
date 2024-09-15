import websocket
import json
import threading
import time
import requests
import asyncio
from characterai import aiocai
from apicode import aiclient, token
from imagetotext import ImageCaptioning

# WebSocket URL and token
ws_url = 'wss://gateway.discord.gg/?v=6&encording=json'
token = token  # Use the correct token from apicode

# Initialize ImageCaptioning class
image_captioning = ImageCaptioning()

# ANSI escape codes for color
RESET = '\033[0m'
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'

class AIPart:
    def __init__(self, char, api_key):
        self.char = char
        self.client = aiocai.Client(api_key)
        self.chat = None
        self.chat_id = None

    async def initialize_chat(self):
        me = await self.client.get_me()
        chat = await self.client.connect()
        new, answer = await chat.new_chat(self.char, me.id)
        self.chat = chat
        self.chat_id = new.chat_id
        print(f'{answer.name}: {answer.text}')

    async def handle_message(self, text):
        if not self.chat or not self.chat_id:
            await self.initialize_chat()

        try:
            message = await self.chat.send_message(self.char, self.chat_id, text)
            return f'{message.name}: {message.text}'
        except Exception as e:
            return f"An error occurred: {e}"

    async def process_incoming_message(self, text):
        response = await self.handle_message(text)
        return response

# WebSocket handling functions
def get_json_request(ws, request):
    ws.send(json.dumps(request))

def got_json_response(ws):
    response = ws.recv()
    if response:
        return json.loads(response)
    return None

def heartbeat(ws, interval):
    print(f'{CYAN}Heartbeat begin{RESET}')
    while True:
        time.sleep(interval)
        heartbeatJSON = {
            "op": 1,
            "d": None
        }
        get_json_request(ws, heartbeatJSON)
        print(f"{GREEN}Heartbeat sent{RESET}")

def connect():
    ws = websocket.WebSocket()
    ws.connect(ws_url)
    print(f'{CYAN}WebSocket connected{RESET}')

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

def download_image(image_url, filename="image.png"):
    img_data = requests.get(image_url).content
    with open(filename, 'wb') as handler:
        handler.write(img_data)
    return filename

async def handle_image_attachment(image_url):
    print(f"{CYAN}Image URL: {image_url}{RESET}")

    # Download the image
    image_path = download_image(image_url)
    print(f"{GREEN}Image downloaded to {image_path}{RESET}")

    # Generate the caption
    caption = image_captioning.generate_caption(image_path)
    if caption:
        return f"{YELLOW}Generated Caption: {caption}{RESET}"
    else:
        return f"{RED}Failed to generate caption.{RESET}"

def event_loop(ws):
    aipart = AIPart('gc6qOU5zms07_eFoWdGWKCUlGxmHEVIBj33ZhNfUxY0', aiclient)

    while True:
        event = got_json_response(ws)
        if event and event.get('t') == 'MESSAGE_CREATE':
            author = event['d']['author']['username']
            content = event['d']['content']
            attachments = event['d']['attachments']

            print(f"{CYAN}{author}: {content}{RESET}")

            # Check if there are attachments (images)
            if attachments:
                for attachment in attachments:
                    if attachment['content_type'].startswith('image'):
                        caption = asyncio.run(handle_image_attachment(attachment['url']))
                        print(caption)
            
            # Handle Character AI if there's text content
            if content:
                response = asyncio.run(aipart.process_incoming_message(content))
                print(response)

if __name__ == "__main__":
    connect()
