from characterai import aiocai
import asyncio
from apicode import aiclient

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

# Example usage
async def main():
    char = 'gc6qOU5zms07_eFoWdGWKCUlGxmHEVIBj33ZhNfUxY0'
    api_key = aiclient
    aipart = AIPart(char, api_key)
    
    # Example messages for demonstration
    messages = ["Hello!", "How are you?", "exit"]

    await aipart.initialize_chat()

    for msg in messages:
        if msg.lower() == 'exit':
            break

        response = await aipart.process_incoming_message(msg)
        print(response)

if __name__ == "__main__":
    asyncio.run(main())

