from AnilistPython import Anilist
import re

class AnilistHandler:
    def __init__(self):
        self.anilist = Anilist()

    def remove_html_tags(self, text):
        """
        Remove HTML tags from the text.
        """
        clean = re.compile(r'<.*?>')
        return re.sub(clean, '', text)
    
    def print_anime_info(self, name):
        anime_info = self.anilist.get_anime_info(name)  # Assuming returns HTML or raw text
        return self.remove_html_tags(anime_info)

    def print_manga_info(self, name):
        manga_info = self.anilist.get_manga_info(name)  # Assuming  returns HTML or raw text
        return self.remove_html_tags(manga_info)

    def print_character_info(self, name):
        character_info = self.anilist.get_character_info(name)  # Assuming  returns HTML or raw text
        return self.remove_html_tags(character_info)


