
---

# 🎉 Welcome to the Ultimate Discord Bot Experience! 🎉

![RinaBot](https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExNDB5Yjlqa3F2dWFnNmlpemozMGJpbHNodWgxbWVpaHF4NGRicDdyayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/h5osyQ0PLpfELctNIi/giphy.gif)

## 🚀 Overview

Meet **RinaBot**—your new best friend on Discord! RinaBot isn’t just any bot; it’s packed with features to make your Discord server lively and fun. Whether you want anime updates, manga insights, character information, or even some quirky AI chat, RinaBot’s got you covered!

## 🛠 Features

- **🎬 Anime & Manga Insights**
  - **`-anime [title]`**: Get the latest scoop on your favorite anime.
  - **`-manga [title]`**: Dive into the world of manga with detailed info.

- **👾 Character Information**
  - **`-ch [character name]`**: Discover cool facts and details about your favorite characters.

- **🤖 Rina’s AI Chat**
  - **`-rina [message]`**: Have a chat with Rina, our character AI. It's like chatting with a virtual buddy!

- **📸 Image Magic**
  - Send an image, and RinaBot will download it and generate a snazzy caption for it. Perfect for spicing up your server with some visual flair!

## 🛠 Work in Progress

- **Sender Component**: the sender component is now functional! but the ai restart every conv for some reason lol
![qucklook](https://files.catbox.moe/3oit0e.png)


it need some more work to run but main thing work without any problem

![In Progress](https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExNjFrbXlmb24xMzI0eGlpeWptYm93M2w2NmwyOGkwbWxqeTVlNHZlZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Apou9x4qiaDdGs6R9W/giphy.gif)

## 🏗️ How It Works

1. **Connect to Discord**: RinaBot hooks up with Discord using WebSocket to stay in sync with your server.

2. **Handle Commands**: Send commands like `-anime` or `-rina` and watch RinaBot spring into action. It’s like having a personal assistant right in your chat!

3. **Process Images**: Share images and let RinaBot work its magic by generating captions and keeping your community engaged with fun content.

4. **AI Interaction**: Chat with Rina and enjoy some light-hearted banter with our Character AI. Who knows what Rina might say next?

![How It Works](https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExb2JjN3U0NHZuenVjcXQ3c2hvd2J4cGp2NHNobTlzb2xocDVhMHJwNCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/bMzhPASPFNJORLgUuE/giphy.gif)

## 🚀 Getting Started

1. **Clone the Repo**:
   ```bash
   git clone https://github.com/notkiyo/Rina-s-Realm.git
   cd Rina-s-Realm
   cd aiwaifu
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Your Token**:
   - Set up your Discord bot token in `apicode.py`. Replace the placeholder values with your actual API keys and tokens.

4. **Run the Bot**:
   ```bash
   python main.py
   ```

5. **Enjoy**: Join your Discord server and start using RinaBot’s commands. Watch your server come to life!

## 📝 Notes

- **In Progress**: This project is still a work in progress. The sender component is under construction, and we’re actively learning and refining it. Keep an eye out for updates!
- **Modular Design**: Some functionality is separated into standalone Python files for better organization and modularity. Check out `apicode.py`, `imagetotext.py`, and `animeani.py` for more details.

6. ## 🛠 Adding New Handlers and Features

  To make RinaBot even more versatile, you can easily add new handlers or functionalities. Here's a quick guide on how to do that:

  ### 1. Create a New Handler

  Start by creating a new Python file in the `handlers` directory, or modify an existing one.

  For example, if you're adding a new handler to fetch weather updates, you could create a `weather_handler.py` file with the following code:
  
  ```python
  class WeatherHandler:
      def __init__(self):
          pass
  
      async def handle_weather(self, location):
          # Code to fetch weather data goes here
          weather_info = fetch_weather_data(location)
          return weather_info
  ```
  
  ### 2. Integrate the Handler with `send_tagged_message`
  
  To make use of `send_tagged_message` and send results to Discord, you can modify your handler's response flow. For instance, in the same `weather_handler.py`:
  
  ```python
  class WeatherHandler:
      def __init__(self, discord_sender):
          self.discord_sender = discord_sender
  
      async def handle_weather(self, location, channel_id):
          weather_info = fetch_weather_data(location)
          tagged_message = f"🌤 Weather Update for {location}: {weather_info}"
          
          # Use send_tagged_message to send this message to a Discord channel
          await self.discord_sender.send_tagged_message(tagged_message, channel_id)
  ```
  
  ### 3. Modify `DiscordSender` to Handle New Tags
  
  In your `discord_sender.py`, ensure that the `send_tagged_message` function can handle your new type of message tags:
  
  ```python
  class DiscordSender:
      async def send_tagged_message(self, message, channel_id):
          # Sending the message to the Discord channel using WebSocket or Discord API
          await self.send_message(message, channel_id)
  ```
  
  ### 4. Update the Command Handler
  
  Finally, update the `CommandHandler` class in `command_handler.py` to include the new handler command. For example, if your weather command is `-weather`, you would add it like so:
  
  ```python
  class CommandHandler:
      def __init__(self, weather_handler):
          self.weather_handler = weather_handler
  
      async def handle_command(self, command, args, channel_id):
          if command == '-weather':
              location = ' '.join(args)
              await self.weather_handler.handle_weather(location, channel_id)
  ```
  
  Now, your bot will handle `-weather` commands and send weather updates to your Discord channel using the `send_tagged_message` method!

## 📚 Contributing

Got ideas for new features or improvements? We’re all ears! Fork the repo, make your changes, and submit a pull request. If you have a wild idea or a genius suggestion, let us know!

## 🥳 Acknowledgments

- **Character AI**: For making RinaBot’s chat possible.
- **Anilist API**: For providing awesome anime and manga data.
- **ImageCaptioning**: For adding that extra touch of fun to image sharing!
- **ChatGPT**: Special thanks to ChatGPT for the invaluable assistance in structuring the code  and README. Your guidance made this project better and more user-friendly!

## 💬 Feature Suggestions

Got an idea that could make RinaBot even cooler? Don’t keep it to yourself! Share your thoughts, and let’s make RinaBot the ultimate Discord sidekick. Maybe a mini-game or a custom meme generator? The sky’s the limit!

## 📧 Contact

If you have any questions, want to chat, or just want to share your thoughts, feel free to reach out at [notgogaly.exe@proton.me](mailto:notgogaly.exe@proton.me).

## 📜 License

This project is licensed under the Creative Commons Attribution 4.0 International License. You are free to share, remix, and build upon this work, even for commercial purposes, as long as you provide appropriate credit. For more details, check out the full license text [here](https://creativecommons.org/licenses/by/4.0/).

Happy Discord-ing! 🚀

![Contributing](https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExbzZldWg3NTBxOW1ld3kydDMwZmx0MHJkY3BjaXMybzEzNjE3Y3llNSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/UR4cvwP8NEZ5aR2YPU/giphy.gif)

---
