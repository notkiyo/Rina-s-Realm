import websocket
import json
import threading
import time
import requests
import asyncio
from characterai import aiocai
from apicode import aiclient, token
from imagetotext import ImageCaptioning
from animeani import AnilistHandler

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
BLACK = '\033[30m'


class CommandHandler:
    def __init__(self):
        # Initialize command handlers
        self.handlers = {
            "-anime": self.handle_anime,
            "-manga": self.handle_manga,
            "-ch": self.handle_character,
            # Add more commands and their handlers here
        }

        # Initialize instances of handler classes if needed
        self.anilist_handler = AnilistHandler()

    def handle_command(self, command, args):
        """
        Handle a command by calling the appropriate method.
        """
        if command in self.handlers:
            self.handlers[command](args)
        else:
            # Pass unknown commands to Character AI
            response = asyncio.run(self.pass_to_ai(f"Unknown command: {command} {args}"))
            print(response)

    def handle_anime(self, args):
        """
        Handle the -anime command.
        """
        self.anilist_handler.print_anime_info(args)

    def handle_manga(self, args):
        """
        Handle the -manga command.
        """
        self.anilist_handler.print_manga_info(args)

    def handle_character(self, args):
        """
        Handle the -character command.
        """
        self.anilist_handler.print_character_info(args)

    async def pass_to_ai(self, text):
        """
        Pass unknown commands to Character AI for processing.
        """
        aipart = AIPart('gc6qOU5zms07_eFoWdGWKCUlGxmHEVIBj33ZhNfUxY0', aiclient)
        response = await aipart.process_incoming_message(text)
        return response


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
        print(f'{BLACK}{answer.name}: {answer.text}{RESET}')

    async def handle_message(self, text):
        """
        Send a message to the Character AI and receive a response.
        """
        if not self.chat or not self.chat_id:
            await self.initialize_chat()

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


def get_json_request(ws, request):
    """
    Send a JSON request to the WebSocket server.
    """
    ws.send(json.dumps(request))


def got_json_response(ws):
    """
    Receive and parse a JSON response from the WebSocket server.
    """
    response = ws.recv()
    if response:
        return json.loads(response)
    return None


def heartbeat(ws, interval):
    """
    Send a heartbeat to the WebSocket server to keep the connection alive.
    """
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
    """
    Connect to the WebSocket server and start the event loop.
    """
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
    """
    Download an image from a URL and save it to a file.
    """
    img_data = requests.get(image_url).content
    with open(filename, 'wb') as handler:
        handler.write(img_data)
    return filename


async def handle_image_attachment(image_url):
    """
    Handle an image attachment by downloading it and generating a caption.
    """
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
    """
    Main event loop for handling incoming WebSocket events.
    """
    command_handler = CommandHandler()

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
                # Check if the content starts with a command
                command_parts = content.split(' ', 1)
                if len(command_parts) > 1:
                    command = command_parts[0].strip().lower()
                    args = command_parts[1].strip()
                    command_handler.handle_command(command, args)
                else:
                    # Handle general text content with Character AI
                    response = asyncio.run(command_handler.pass_to_ai(content))
                    print(response)


if __name__ == "__main__":
    connect()
