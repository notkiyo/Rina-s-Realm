import json
import asyncio
import aiohttp
import requests
import websockets
from characterai import aiocai
from apicode import aiclient, token
from imagetotext import ImageCaptioning

# WebSocket URL and token
ws_url = 'wss://gateway.discord.gg/?v=6&encoding=json'
token = token  # apicode.py

# Initialize ImageCaptioning class
image_captioning = ImageCaptioning()

# ANSI escape codes for color
RESET = '\033[0m'
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
BLACK = '\033[30m'

class AnilistHandler:
    def __init__(self):
        self.url = 'https://graphql.anilist.co'

    def get_anime_description(self, name):
        query = '''
        query ($name: String!) {
            Media(search: $name, type: ANIME) {
                description
            }
        }
        '''
        variables = {'name': name}
        response = requests.post(self.url, json={'query': query, 'variables': variables})
        if response.status_code == 200:
            data = response.json()
            description = data.get('data', {}).get('Media', {}).get('description', 'No description available')
            return description
        else:
            return f"Error fetching anime description: {response.status_code}"

    def get_manga_description(self, name):
        query = '''
        query ($name: String!) {
            Media(search: $name, type: MANGA) {
                description
            }
        }
        '''
        variables = {'name': name}
        response = requests.post(self.url, json={'query': query, 'variables': variables})
        if response.status_code == 200:
            data = response.json()
            description = data.get('data', {}).get('Media', {}).get('description', 'No description available')
            return description
        else:
            return f"Error fetching manga description: {response.status_code}"

    def get_character_description(self, name):
        query = '''
        query ($name: String!) {
            Character(search: $name) {
                description
            }
        }
        '''
        variables = {'name': name}
        response = requests.post(self.url, json={'query': query, 'variables': variables})
        if response.status_code == 200:
            data = response.json()
            description = data.get('data', {}).get('Character', {}).get('description', 'No description available')
            return description
        else:
            return f"Error fetching character description: {response.status_code}"

class CommandHandler:
    def __init__(self, discord_sender):
        self.handlers = {
            "-anime": self.handle_anime,
            "-manga": self.handle_manga,
            "-ch": self.handle_character,
            "-rina": self.handle_rina,
        }
        self.anilist_handler = AnilistHandler()
        self.discord_sender = discord_sender

    async def handle_command(self, command, args):
        if command in self.handlers:
            await self.handlers[command](args)
        else:
            self.discord_sender.send_tagged_message("unknown_command", command)

    async def handle_anime(self, args):
        if args:
            anime_description = self.anilist_handler.get_anime_description(args)
            self.discord_sender.send_tagged_message("anime_info", anime_description)
        else:
            self.discord_sender.send_tagged_message("anime_info", "No anime name provided.")

    async def handle_manga(self, args):
        if args:
            manga_description = self.anilist_handler.get_manga_description(args)
            self.discord_sender.send_tagged_message("manga_info", manga_description)
        else:
            self.discord_sender.send_tagged_message("manga_info", "No manga name provided.")

    async def handle_character(self, args):
        if args:
            character_description = self.anilist_handler.get_character_description(args)
            self.discord_sender.send_tagged_message("character_info", character_description)
        else:
            self.discord_sender.send_tagged_message("character_info", "No character name provided.")

    async def handle_rina(self, args):
        rina_ai = AIPart('gc6qOU5zms07_eFoWdGWKCUlGxmHEVIBj33ZhNfUxY0', aiclient)
        await rina_ai.initialize_chat()
        response = await rina_ai.process_incoming_message(args)
        self.discord_sender.send_tagged_message("rina_response", response)

class AIPart:
    def __init__(self, char, api_key):
        self.char = char
        self.client = aiocai.Client(api_key)
        self.chat = None
        self.chat_id = None
        self.initialized = False  # Add an initialization flag

    async def initialize_chat(self):
        if self.initialized:  # Check if already initialized
            return
        me = await self.client.get_me()
        chat = await self.client.connect()
        new, answer = await chat.new_chat(self.char, me.id)
        self.chat = chat
        self.chat_id = new.chat_id
        self.initialized = True  # Set flag to True
        await print_response("chat_init", f'{answer.name}: {answer.text}')


    async def handle_message(self, text):
        try:
            message = await self.chat.send_message(self.char, self.chat_id, text)
            return f'{message.name}: {message.text}'
        except Exception as e:
            return f"An error occurred: {e}"

    async def process_incoming_message(self, text):
        response = await self.handle_message(text)
        return response

async def get_json_request(ws, request):
    await ws.send(json.dumps(request))

async def got_json_response(ws):
    response = await ws.recv()
    if response:
        return json.loads(response)
    return None

async def heartbeat(ws, interval):
    await print_response("heartbeat", "Heartbeat begin")
    while True:
        await asyncio.sleep(interval)
        heartbeatJSON = {"op": 1, "d": None}
        await get_json_request(ws, heartbeatJSON)
        await print_response("heartbeat", "Heartbeat sent")

async def connect():
    async with websockets.connect(ws_url) as ws:
        await print_response("websocket", "WebSocket connected")

        event = await got_json_response(ws)
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
            await get_json_request(ws, payload)

            asyncio.create_task(heartbeat(ws, heartbeat_interval))
            await event_loop(ws)

async def handle_image_attachment(image_url):
    await print_response("image_url", f"Image URL: {image_url}")
    image_path = await download_image(image_url)
    await print_response("image_download", f"Image downloaded to {image_path}")
    caption = image_captioning.generate_caption(image_path)
    if caption:
        await print_response("image_caption", f"Generated Caption: {caption}")
    else:
        await print_response("image_caption", "Failed to generate caption.")

async def download_image(image_url, filename="image.png"):
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            img_data = await response.read()
            with open(filename, 'wb') as handler:
                handler.write(img_data)
    return filename

async def event_loop(ws):
    discord_sender = DiscordSender(token)
    command_handler = CommandHandler(discord_sender)

    while True:
        event = await got_json_response(ws)
        if event and event.get('t') == 'MESSAGE_CREATE':
            author = event['d']['author']['username']
            content = event['d']['content']
            attachments = event['d']['attachments']

            await print_response("message_create", f"{author}: {content}")

            if attachments:
                for attachment in attachments:
                    if attachment['content_type'].startswith('image'):
                        await handle_image_attachment(attachment['url'])

            # Handle commands only if content starts with a recognized command
            if content:
                command_parts = content.split(' ', 1)
                if len(command_parts) > 1:
                    command = command_parts[0].strip().lower()
                    args = command_parts[1].strip()
                else:
                    command = command_parts[0].strip().lower()
                    args = ""

                await command_handler.handle_command(command, args)


class DiscordSender:
    def __init__(self, bot_token):
        self.url = f'https://discord.com/api/v10/channels/741223003261763646/messages'  
        self.headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }

    def send_message(self, text_content):
        payload = {
            'content': text_content
        }
        response = requests.post(self.url, json=payload, headers=self.headers)
        if response.status_code == 200:
            print(f'{GREEN}Message sent successfully.{RESET}')
        else:
            print(f'{RED}Failed to send message. Status code: {response.status_code}{RESET}')
            print(f'{RED}Response: {response.text}{RESET}')

    def send_tagged_message(self, tag, message):
        """
        Send a message to Discord based on a tag.
        """
        tags = {
            "anime_info": f"Fetched anime info for: {message}",
            "manga_info": f"Fetched manga info for: {message}",
            "character_info": f"Fetched character info for: {message}",
            "rina_response": f"Rina: {message}",
            "image_caption": f"Generated Caption: {message}",
        }
        if tag in tags:
            self.send_message(tags[tag])

# Centralized function to print responses with color for debugging
async def print_response(tag, message):
    color_map = {
        "chat_init": CYAN,
        "heartbeat": YELLOW,
        "message_create": GREEN,
        "image_url": CYAN,
        "image_download": GREEN,
        "image_caption": YELLOW,
        "anime_info": CYAN,
        "manga_info": CYAN,
        "character_info": CYAN,
        "rina_response": GREEN,
        "error": RED
    }
    
    color = color_map.get(tag, RESET)
    print(f"{color}{tag.upper()}: {message}{RESET}")


if __name__ == "__main__":
    asyncio.run(connect())
