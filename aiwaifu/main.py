import json
import asyncio
import aiohttp
import websockets
from characterai import aiocai
from apicode import aiclient, token
from imagetotext import ImageCaptioning
from animeani import AnilistHandler

# WebSocket URL and token
ws_url = 'wss://gateway.discord.gg/?v=6&encoding=json'
token = token  # apicode.py

# Initialize ImageCaptioning class and Discord sender
image_captioning = ImageCaptioning()

# ANSI escape codes for color
RESET = '\033[0m'
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
BLACK = '\033[30m'


class CommandHandler:
    def __init__(self):
        # Initialize command handlers
        self.handlers = {
            "-anime": self.handle_anime, # anime info
            "-manga": self.handle_manga, # manga info
            "-ch": self.handle_character, # character info
            "-rina": self.handle_rina,  # (AI) command
        }

        # Initialize instances of handler classes
        self.anilist_handler = AnilistHandler()

    async def handle_command(self, command, args):
        """
        Handle a command by calling the appropriate method.
        """
        if command in self.handlers:
            await self.handlers[command](args)
        else:
            await print_response("unknown_command", f"Unknown command: {command}")

    async def handle_anime(self, args):
        """
        Handle the -anime command.
        """
        self.anilist_handler.print_anime_info(args)
        await print_response("anime_info", f"Fetched anime info for: {args}")

    async def handle_manga(self, args):
        """
        Handle the -manga command.
        """
        self.anilist_handler.print_manga_info(args)
        await print_response("manga_info", f"Fetched manga info for: {args}")

    async def handle_character(self, args):
        """
        Handle the -character command.
        """
        self.anilist_handler.print_character_info(args)
        await print_response("character_info", f"Fetched character info for: {args}")

    async def handle_rina(self, args):
        """
        Handle the -rina command by initializing Rina's AI and responding.
        """
        rina_ai = AIPart('gc6qOU5zms07_eFoWdGWKCUlGxmHEVIBj33ZhNfUxY0', aiclient)  # Assuming correct character ID and API key
        await rina_ai.initialize_chat()  # Initialize the AI chat session
        response = await rina_ai.process_incoming_message(args)
        await print_response("rina_response", f"Rina: {response}")  # Output Rina's response in the console


class AIPart:
    def __init__(self, char, api_key):
        """
        Initialize the AIPart class with the character ID and API key.
        """
        self.char = char
        self.client = aiocai.Client(api_key)
        self.chat = None
        self.chat_id = None

    async def initialize_chat(self):
        """
        Set up a new chat session with the Character AI and store the chat ID.
        """
        me = await self.client.get_me()
        chat = await self.client.connect()
        new, answer = await chat.new_chat(self.char, me.id)
        self.chat = chat
        self.chat_id = new.chat_id
        await print_response("chat_init", f'{answer.name}: {answer.text}')

    async def handle_message(self, text):
        """
        Send a message to the Character AI and receive a response.
        """
        try:
            message = await self.chat.send_message(self.char, self.chat_id, text)
            return f'{message.name}: {message.text}'
        except Exception as e:
            return f"An error occurred: {e}"

    async def process_incoming_message(self, text):
        """
        Process an incoming message by sending it to the Character AI and returning the response.
        """
        response = await self.handle_message(text)
        return response


async def get_json_request(ws, request):
    """
    Send a JSON request to the WebSocket server.
    """
    await ws.send(json.dumps(request))


async def got_json_response(ws):
    """
    Receive and parse a JSON response from the WebSocket server.
    """
    response = await ws.recv()
    if response:
        return json.loads(response)
    return None


async def heartbeat(ws, interval):
    """
    Send a heartbeat to the WebSocket server to keep the connection alive.
    """
    await print_response("heartbeat", "Heartbeat begin")
    while True:
        await asyncio.sleep(interval)
        heartbeatJSON = {
            "op": 1,
            "d": None
        }
        await get_json_request(ws, heartbeatJSON)
        await print_response("heartbeat", "Heartbeat sent")


async def connect():
    """
    Connect to the WebSocket server and start the event loop.
    """
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
    """
    Handle an image attachment by downloading it and generating a caption.
    """
    await print_response("image_url", f"Image URL: {image_url}")

    # Download the image
    image_path = await download_image(image_url)
    await print_response("image_download", f"Image downloaded to {image_path}")

    # Generate the caption
    caption = image_captioning.generate_caption(image_path)
    if caption:
        await print_response("image_caption", f"Generated Caption: {caption}")
    else:
        await print_response("image_caption", "Failed to generate caption.")


async def download_image(image_url, filename="image.png"):
    """
    Download an image from a URL and save it to a file.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            img_data = await response.read()
            with open(filename, 'wb') as handler:
                handler.write(img_data)
    return filename


async def event_loop(ws):
    """
    Main event loop for handling incoming WebSocket events.
    """
    command_handler = CommandHandler()

    while True:
        event = await got_json_response(ws)
        if event and event.get('t') == 'MESSAGE_CREATE':
            author = event['d']['author']['username']
            content = event['d']['content']
            attachments = event['d']['attachments']

            await print_response("message_create", f"{author}: {content}")

            # Check if there are attachments (images)
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
                    await command_handler.handle_command(command, args)


# Centralized function to print responses
async def print_response(tag, message):
    """
    Centralized function for printing responses based on a tag.
    """
    print(f"{tag.upper()}: {message}")


if __name__ == "__main__":
    asyncio.run(connect())

    asyncio.run(connect())
