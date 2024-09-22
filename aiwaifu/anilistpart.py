import requests
import re


class AnilistHandler:
    def __init__(self):
        self.url = 'https://graphql.anilist.co'

    def strip_html_tags(self, text):
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)

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
            return self.strip_html_tags(description)
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
            return self.strip_html_tags(description)
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
            return self.strip_html_tags(description)
        else:
            return f"Error fetching character description: {response.status_code}"

    def get_anime_details(self, name):
        query = '''
        query ($name: String!) {
            Media(search: $name, type: ANIME) {
                description
                averageScore
                status
            }
        }
        '''
        variables = {'name': name}
        response = requests.post(self.url, json={'query': query, 'variables': variables})
        if response.status_code == 200:
            data = response.json()
            details = data.get('data', {}).get('Media', {})
            description = details.get('description', 'No description available')
            average_score = details.get('averageScore', 'No average score available')
            status = details.get('status', 'No status available')
            return {
                'description': self.strip_html_tags(description),
                'averageScore': average_score,
                'status': status
            }
        else:
            return f"Error fetching anime details: {response.status_code}"

    def get_manga_details(self, name):
        query = '''
        query ($name: String!) {
            Media(search: $name, type: MANGA) {
                description
                averageScore
                status
            }
        }
        '''
        variables = {'name': name}
        response = requests.post(self.url, json={'query': query, 'variables': variables})
        if response.status_code == 200:
            data = response.json()
            details = data.get('data', {}).get('Media', {})
            description = details.get('description', 'No description available')
            average_score = details.get('averageScore', 'No average score available')
            status = details.get('status', 'No status available')
            return {
                'description': self.strip_html_tags(description),
                'averageScore': average_score,
                'status': status
            }
        else:
            return f"Error fetching manga details: {response.status_code}"
