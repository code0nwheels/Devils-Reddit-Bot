import praw
import schedule
import time
from datetime import datetime, timedelta
from hockey.schedule import Schedule
from hockey.game import Game
from dotenv import load_dotenv
import os
import pytz

# Load environment variables from .env file
load_dotenv()

# Reddit bot configuration using environment variables
reddit = praw.Reddit(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    user_agent="rdevilsgdt",
    username=os.getenv("USERNAME"),
    password=os.getenv("PASSWORD")
)

SUBREDDIT = "testbots"

def post_gdt(game: Game):
    """
    Posts a Game Day Thread (GDT) to r/devils.
    """
    title = f"GDT: {game.away_team_full_name} at {game.home_team_full_name} - {game.game_time('%I:%M %p')} ET"
    
    # Check if the game thread exists already
    subreddit = reddit.subreddit(SUBREDDIT)
    existing_threads = list(subreddit.new(limit=10))
    
    for thread in existing_threads:
        if game.away_team_full_name in thread.title and game.home_team_full_name in thread.title:
            print("Game thread already exists.")
            return
    
    # Submit the post
    submission = subreddit.submit(title, selftext="Discuss the game here!")
    print(f"Posted thread: {submission.title}")


def check_for_next_game():
    """
    Checks if there is a game starting in 30 minutes and posts the GDT if not already posted.
    """
    schedule = Schedule()  # Default to today's date
    schedule.fetch_team_schedule("njd")  # Fetch Devils schedule
    
    next_game = schedule.get_next_game()
    
    if next_game:
        # Calculate the time difference between now and game time
        now = datetime.now(pytz.utc).astimezone()
        game_time = next_game.raw_game_time.astimezone()
        print(now, game_time)
        # Check if the game is 30 minutes from now
        if True:#now + timedelta(minutes=3009) >= game_time:# > now:
            post_gdt(next_game)
        else:
            print("No game in the next 30 minutes.")
    else:
        print("No upcoming game found.")


# Schedule the job to run on every 30th minute of the hour
schedule.every().hour.at(":42").do(check_for_next_game)

# Main loop to keep the script running
if __name__ == "__main__":
    while True:
        check_for_next_game()#schedule.run_pending()
        time.sleep(60)
