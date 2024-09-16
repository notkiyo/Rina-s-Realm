from AnilistPython import Anilist

class AnilistHandler:
    def __init__(self):
        self.anilist = Anilist()
    
    def print_anime_info(self, name):
        self.anilist.print_anime_info(name)
    
    def print_manga_info(self, name):
        self.anilist.print_manga_info(name)
    
    def print_character_info(self, name):
        # Add the method for characters if it exists in the Anilist API
        self.anilist.print_character_info(name)

def main():
    handler = AnilistHandler()
    
    while True:
        option = input("Choose an option (anime, manga, character, close): ").strip().lower()
        
        if option == "close":
            print("Exiting program.")
            break
        
        name = input("Enter the name: ").strip()
        
        if option == "anime":
            handler.print_anime_info(name)
        elif option == "manga":
            handler.print_manga_info(name)
        elif option == "character":
            handler.print_character_info(name)
        else:
            print("Invalid option. Please choose 'anime', 'manga', 'character', or 'close'.")

if __name__ == "__main__":
    main()
