import requests
from hockey.team import Team
from datetime import datetime, timedelta
import pytz
from typing import Dict, Any

GAME_STATES = {
    "LIVE": "Live",
    "CRIT": "Live",
    "FINAL": "Final",
    "OFF": "Final",
    "OVER": "Final",
    "FUT": "Scheduled",
    "PRE": "Scheduled"
}

GAME_SCHEDULE_STATES = {
    "OK": "Scheduled",
    "TBD": "To Be Determined",
    "PPD": "Postponed",
    "SUSP": "Suspended",
    "CNCL": "Cancelled"
}

GAME_TYPES = {
    1: "Preseason",
    2: "Regular Season",
    3: "Playoffs"
}

API_URL = 'https://api-web.nhle.com/v1/gamecenter/{}/landing'

class Game:
    def __init__(self, game_id: int):
        self.game = None
        self.game_id = game_id
        self.game_object: Dict[str, Any] = {}
        self.round = 0
        self._fetch_game()

    def _fetch_game(self) -> None:
        try:
            response = requests.get(API_URL.format(self.game_id))
            response.raise_for_status()
            self.game_object = response.json()
        except requests.RequestException as e:
            print(f"Failed to fetch game data: {e}")
    
    def refresh(self) -> None:
        self._fetch_game()
    
    @property
    def season(self) -> str:
        return self.game_object.get('season', "Unknown")

    def get_away_team(self) -> Team:
        return Team(self.game_object.get('awayTeam', {}).get('id'))

    def get_home_team(self) -> Team:
        return Team(self.game_object.get('homeTeam', {}).get('id'))

    @property
    def away_team_abbr(self) -> str:
        return self.game_object.get('awayTeam', {}).get('abbrev', 'UNK')
    
    @property
    def home_team_abbr(self) -> str:
        return self.game_object.get('homeTeam', {}).get('abbrev', 'UNK')

    @property
    def away_team_full_name(self) -> str:
        if self.away_team_id == 59:
            return "Utah Hockey Club"
        return self.game_object.get('awayTeam', {}).get('placeName', {}).get("default", "Unknown") + " " + self.game_object.get('awayTeam', {}).get('name', {}).get("default", "Unknown")
    
    @property
    def home_team_full_name(self) -> str:
        if self.home_team_id == 59:
            return "Utah Hockey Club"
        return self.game_object.get('homeTeam', {}).get('placeName', {}).get("default", "Unknown") + " " + self.game_object.get('homeTeam', {}).get('name', {}).get("default", "Unknown")
    
    @property
    def away_team_id(self) -> int:
        return self.game_object.get('awayTeam', {}).get('id', 0)
    
    @property
    def home_team_id(self) -> int:
        return self.game_object.get('homeTeam', {}).get('id', 0)

    @property
    def game_state(self) -> str:
        return GAME_STATES.get(self.game_object.get('gameState'), 'Unknown')

    @property
    def schedule_state(self) -> str:
        return GAME_SCHEDULE_STATES.get(self.game_object.get('gameScheduleState'), 'Unknown')

    def game_time(self, format: str, timezone: str = "US/Eastern") -> str:
        utc = datetime.strptime(self.game_object['startTimeUTC'], "%Y-%m-%dT%H:%M:%SZ")
        utc = pytz.utc.localize(utc)
        return utc.astimezone(pytz.timezone(timezone)).strftime(format)
    
    @property
    def raw_game_time(self) -> datetime:
        utctz = pytz.timezone('UTC')
        return utctz.localize(datetime.strptime(self.game_object['startTimeUTC'], "%Y-%m-%dT%H:%M:%SZ"))
    
    def raw_pregame_time(self, minutes_before_start: int = 30) -> datetime:
        return self.raw_game_time - timedelta(minutes=minutes_before_start)
    
    def pregame_time(self, format: str, timezone: str = "US/Eastern", minutes_before_start: int = 30) -> str:
        return self.raw_pregame_time(minutes_before_start).astimezone(pytz.timezone(timezone)).strftime(format)

    @property
    def away_team_record(self) -> str:
        if self.is_regular_season:
            return self.game_object.get('awayTeam', {}).get('record', {})
        elif self.is_playoffs:
            return f"{self.game_object.get('summary', {}).get('seasonSeriesWins', {}).get('awayTeamWins', 0)}-" \
                   f"{self.game_object.get('summary', {}).get('seasonSeriesWins', {}).get('homeTeamWins', 0)}"
        else:
            return "0-0-0"
    
    @property
    def home_team_record(self) -> str:
        if self.is_regular_season:
            return self.game_object.get('homeTeam', {}).get('record', {})
        elif self.is_playoffs:
            return f"{self.game_object.get('summary', {}).get('seasonSeriesWins', {}).get('homeTeamWins', 0)}-" \
                   f"{self.game_object.get('summary', {}).get('seasonSeriesWins', {}).get('awayTeamWins', 0)}"
        else:
            return "0-0-0"
    
    @property
    def game_type(self) -> str:
        return GAME_TYPES.get(self.game_object.get('gameType'), 'Unknown')

    @property
    def venue(self) -> str:
        return self.game_object.get('venue', {}).get('default', 'Unknown')

    @property
    def away_score(self) -> int:
        return self.game_object.get('awayTeam', {}).get('score', 0)
    
    @property
    def home_score(self) -> int:
        return self.game_object.get('homeTeam', {}).get('score', 0)
    
    @property
    def is_today(self) -> bool:
        return self.raw_game_time.date() == datetime.now().date()
    
    @property
    def is_ppd(self) -> bool:
        return self.schedule_state == "Postponed"
    
    @property
    def is_scheduled(self) -> bool:
        return self.schedule_state == "Scheduled"
    
    @property
    def is_live(self) -> bool:
        return self.game_state == "Live"

    @property
    def is_final(self) -> bool:
        return self.game_state == "Final"
    
    @property
    def is_playoffs(self) -> bool:
        return self.game_type == "Playoffs"
    
    @property
    def is_regular_season(self) -> bool:
        return self.game_type == "Regular Season"
    
    @property
    def is_preseason(self) -> bool:
        return self.game_type == "Preseason"
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Game):
            return False
        return self.game_id == value.game_id
    
    def __str__(self) -> str:
        return f"{self.away_team_full_name} @ {self.home_team_full_name} - {self.game_time('%Y-%m-%d %I:%M %p')}"
