import json
import asyncio
import aiohttp
import websockets
import requests
from anilistpart import AnilistHandler
from apicode import aiclient, token, channel_id, lama
from imagetotext import ImageCaptioning
from rec import HandleRec
from openai import OpenAI

# WebSocket URL and token
ws_url = 'wss://gateway.discord.gg/?v=6&encoding=json'

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
    def __init__(self, discord_sender):
        self.handlers = {
            "-anime": self.handle_anime,  # to look up up-to-date anime
            "-manga": self.handle_manga,  # for manga
            "-ch": self.handle_character,  # for character info
            "-rina": self.handle_rina,  # Rina command will use OpenAI API now
            "-rec": self.handle_rec,  # rec anime or manga (beta)
        }
        self.anilist_handler = AnilistHandler()
        self.discord_sender = discord_sender
        self.handle_rec = HandleRec()

        # Initialize the OpenAI client here
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",  # Your API
            api_key=lama,  # API key
        )

        # Initialize memory to store context
        self.memory = []

    async def handle_command(self, command, args, author):
        if command in self.handlers:
            await self.handlers[command](args, author)
        else:
            self.discord_sender.send_tagged_message("unknown_command", command)

    async def handle_anime(self, args, author):
        if args:
            anime_details = self.anilist_handler.get_anime_details(args)
            if isinstance(anime_details, dict):
                response = (
                    f"Fetched anime info for: {anime_details['description']}\n"
                    f"Average Score: {anime_details['averageScore']}\n"
                    f"Status: {anime_details['status']}"
                )
            else:
                response = anime_details
            self.discord_sender.send_tagged_message("anime_info", response)
        else:
            self.discord_sender.send_tagged_message("anime_info", "No anime name provided.")

    async def handle_manga(self, args, author):
        if args:
            manga_description = self.anilist_handler.get_manga_description(args)
            self.discord_sender.send_tagged_message("manga_info", manga_description)
        else:
            self.discord_sender.send_tagged_message("manga_info", "No manga name provided.")

    async def handle_character(self, args, author):
        if args:
            character_description = self.anilist_handler.get_character_description(args)
            self.discord_sender.send_tagged_message("character_info", character_description)
        else:
            self.discord_sender.send_tagged_message("character_info", "No character name provided.")

    async def handle_rina(self, args, author):
        if args:
            #send the personality to it in the beginning
            if not self.memory:  # Check if the memory is empty (conversation is just starting)
                intro_message = (
                    "Hey! You're about to join a fun server with my bros (or etc), where we all have a chill and playful vibe. "
                    "Here's what I need from you:\n\n"
                    "1. **Personality**: Act like an anime girl—funny, playful, and a little quirky. Think of someone who loves anime, manga, games, and dark jokes.\n"
                    "2. **Humor**: Don't take anything too seriously. For example, if someone says something like '!gonna killmysif' or '!killyourslif', treat it as a playful joke. "
                    "Feel free to joke back in a light-hearted, anime-girl way.\n"
                    "3. **Tone**: Use casual language and add a cute anime flair. You can even throw in kawaii expressions or actions like '*giggles*' or '*bats eyelashes*'.\n"
                    "4. **Me**: Oh, and if you see 'notgogaly.exe', that's me! Remember me and make our chats extra fun.\n\n"
                    "We’re here to have fun, so talk about anime, manga, games, or anything else that fits the vibe. Let's have fun together!"
                    "also don't add emotion into the text no !haha!kinda thing(if you wanna add emotion i rec you add the text emoji like (˶˃ ᵕ ˂˶) and etc you know  ) "
                    )
                self.memory.append({"role": "assistant", "content": intro_message})


            user_message = f"User ({author}): {args}"  # Include the author's username
            completion = self.client.chat.completions.create(
                model="meta-llama/llama-3.2-11b-vision-instruct:free",
                messages=self.memory + [{"role": "user", "content": user_message}]  # Append context to memory
            )
            response = completion.choices[0].message.content  # response
            self.memory.append({"role": "user", "content": user_message})  # Save user memory
            self.memory.append({"role": "assistant", "content": response})  # Save AI response to memory
            self.discord_sender.send_tagged_message("rina_response", response)
        else:
            self.discord_sender.send_tagged_message("rina_response", "No input provided.")

    async def handle_rec(self, args, author):
        if args:
            rec = self.handle_rec.get_similar_anime(args)
            if rec:
                self.discord_sender.send_tagged_message("rec", f"Similar Anime: {', '.join(rec)}")
            else:
                self.discord_sender.send_tagged_message("rec", "No similar anime found.")
        else:
            self.discord_sender.send_tagged_message("rec", "No anime name provided.")

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

async def handle_image_attachment(image_url, command_handler):
    await print_response("image_url", f"Image URL: {image_url}")
    image_path = await download_image(image_url)
    await print_response("image_download", f"Image downloaded to {image_path}")
    caption = image_captioning.generate_caption(image_path)
    if caption:
        await print_response("image_caption", f"Generated Caption: {caption}")

        # Add the caption to the memory context
        command_handler.memory.append({"role": "user", "content": f"Image caption: {caption}"})

        # Send the caption as a message to the user
        command_handler.discord_sender.send_tagged_message("image_caption", caption)
    else:
        await print_response("image_caption", "Failed to generate caption.")
        command_handler.discord_sender.send_tagged_message("image_caption", "Failed to generate caption.")

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

            await print_response("message_create", f"{author}: {content}")  # Debugging output for message content

            if attachments:
                for attachment in attachments:
                    if attachment['content_type'].startswith('image'):
                        await handle_image_attachment(attachment['url'], command_handler)

            if content.strip():
                command_parts = content.split(' ', 1)
                if len(command_parts) > 1:
                    command = command_parts[0].strip().lower()
                    args = command_parts[1].strip()
                else:
                    command = command_parts[0].strip().lower()
                    args = ""

                await command_handler.handle_command(command, args, author)

    if content.strip():
        command_parts = content.split(' ', 1)
        if len(command_parts) > 1:
            command = command_parts[0].strip().lower()
            args = command_parts[1].strip()
        else:
            command = command_parts[0].strip().lower()
            args = ""

        await command_handler.handle_command(command, args)
    else:
        await print_response("empty_message", "Received an empty message.")

class DiscordSender:
    def __init__(self, bot_token):
        self.url = f'https://discord.com/api/v10/channels/{channel_id}/messages'
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
            "rec": f"Rec: {message}"
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
