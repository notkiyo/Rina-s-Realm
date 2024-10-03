import requests

class HandleRec:
    def __init__(self):
        self.api_url = 'https://graphql.anilist.co'

    def search_anime(self, name):
        query = '''
        query ($name: String) {
            Media(search: $name, type: ANIME) {
                id
                title {
                    romaji
                    english
                }
                relations {
                    edges {
                        node {
                            title {
                                romaji
                            }
                        }
                    }
                }
            }
        }
        '''
        variables = {
            'name': name
        }
        response = requests.post(self.api_url, json={'query': query, 'variables': variables})
        data = response.json()

        if 'errors' in data:
            print(f"Error: {data['errors']}")
            return None

        anime = data['data']['Media']
        return anime

    def get_similar_anime(self, name):
        anime = self.search_anime(name)
        if anime is None:
            return []

        # Get only the first 4 similar anime
        similar_anime = []
        if anime['relations']['edges']:
            for relation in anime['relations']['edges'][:4]:  # Limit to 4
                similar_anime.append(relation['node']['title']['romaji'])

        return similar_anime


if __name__ == "__main__":
    anilist = HandleRec()
    similar = anilist.get_similar_anime("Naruto") 
    print(f"Similar Anime: {', '.join(similar)}")
