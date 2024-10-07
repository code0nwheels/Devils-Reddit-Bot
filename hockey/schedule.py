import requests
from datetime import datetime
import pytz
from typing import List, Dict, Any, Optional
from .game import Game

API_FULL_SCHEDULE_URL = 'https://api-web.nhle.com/v1/schedule/{}'
API_TEAM_SCHEDULE_URL = 'https://api-web.nhle.com/v1/club-schedule-season/{}/{}'

class Schedule:
    def __init__(self, date: str = "now"):
        self.schedule: List[Dict[str, Any]] = []
        self.date = date

        if date == "now":
            current_date = datetime.now().astimezone(pytz.UTC)
        else:
            current_date = datetime.strptime(date, "%Y-%m-%d").astimezone(pytz.UTC)

        self.date = current_date.strftime("%Y-%m-%d")
        self.season = self._calculate_season(current_date)

    @staticmethod
    def _calculate_season(date: datetime) -> str:
        if date.month > 7:
            return f"{date.year}{date.year + 1}"
        else:
            return f"{date.year - 1}{date.year}"

    def fetch_full_schedule(self) -> None:
        try:
            response = requests.get(API_FULL_SCHEDULE_URL.format(self.date))
            response.raise_for_status()
            data = response.json()
            self.schedule = data['gameWeek'][0]['games']
        except requests.RequestException as e:
            print(f"Failed to fetch full schedule: {e}")

    def fetch_team_schedule(self, team_tri_code: str) -> None:
        try:
            response = requests.get(API_TEAM_SCHEDULE_URL.format(team_tri_code, self.season))
            response.raise_for_status()
            data = response.json()
            self.schedule = data['games']
        except requests.RequestException as e:
            print(f"Failed to fetch team schedule: {e}")

    def get_schedule(self, number_of_games: int = None) -> List[Game]:
        games = []
        if number_of_games:
            for game in self.schedule[:number_of_games]:
                games.append(Game(game['id']))
        else:
            for game in self.schedule:
                games.append(Game(game['id']))
        
        return games

    def get_game(self, *, team_id: int = None) -> Optional[Game]:
        for game in self.schedule:
            if team_id:
                if game['awayTeam']['id'] == team_id or game['homeTeam']['id'] == team_id:
                    return Game(game['id'])
            else:
                if game['gameDate'] == self.date:
                    return Game(game['id'])
        return None

    def get_game_by_id(self, game_id: int) -> Optional[Game]:
        for game in self.schedule:
            if game['id'] == game_id:
                return Game(game['id'])
        return None
    
    def get_next_game(self) -> Optional[Game]:
        for game in self.schedule:
            if game['gameState'] in ['FUT', 'PRE'] and game['gameScheduleState'] == 'OK':
                return Game(game['id'])
        return None
    
    def get_next_time_playing_opponent(self, team_id: int) -> Optional[Game]:
        for game in self.schedule:
            if game['awayTeam']['id'] == team_id or game['homeTeam']['id'] == team_id:
                if game['gameState'] in ['FUT', 'PRE'] and game['gameScheduleState'] == 'OK':
                    return Game(game['id'])
        return None
    
    def set_date(self, date: str) -> None:
        self.date = date
        self.season = self._calculate_season(datetime.strptime(date, "%Y-%m-%d"))
