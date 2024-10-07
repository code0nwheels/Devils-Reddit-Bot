import requests

API_URL = 'https://records.nhl.com/site/api/franchise?include=teams.id&include=teams.active&include=teams.triCode&include=teams.placeName&include=teams.commonName&include=teams.fullName&include=teams.logos&include=teams.conference.name&include=teams.division.name'

class Team:
    def __init__(self, team_id: int):
        self.team_id = team_id
        self.team = {}
        self._fetch_team()

    def _fetch_team(self) -> None:
        try:
            response = requests.get(API_URL.format(self.team_id))
            response.raise_for_status()
            data = response.json()

            for franchise in data['data']:
                for team in franchise['teams']:
                    if team['id'] == self.team_id:
                        self.team = team
        except requests.RequestException as e:
            print(f"Failed to fetch team data: {e}")

    @property
    def id(self) -> int:
        return self.team.get('id')

    @property
    def abbreviation(self) -> str:
        return self.team.get('triCode')

    @property
    def city(self) -> str:
        return self.team.get('placeName')

    @property
    def division(self) -> str:
        return self.team.get('division', {}).get('name')

    @property
    def conference(self) -> str:
        return self.team.get('conference', {}).get('name')

    @property
    def full_name(self) -> str:
        return self.team.get('fullName')
