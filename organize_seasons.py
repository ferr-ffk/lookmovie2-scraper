from importlib.metadata import files
import os
from pathlib import Path

folder = "D:\\Downloads"

def get_episode_files():
    """Returns a list of episode files in the specified folder."""
    return [file for file in os.listdir(folder) if file.endswith(".mp4")]


def get_season_by_episode(episode_file: str):
    """Extracts the season number from the episode name."""
    episode_file = episode_file.lstrip("adventure-time-S")
    
    return episode_file[0] if episode_file[0].isdigit() else "0"
    

if __name__ == "__main__":
    episode_files = get_episode_files()
    
    if not episode_files:
        print("No episode files found.")
    else:
        print(f"Found {len(episode_files)} episode files.")
        
        for episode_file in episode_files:
            season_number = get_season_by_episode(episode_file)
            print(f"Episode: {episode_file}, Season: {season_number}")
            
            # Here you can add logic to move or organize the files by season
            # For example, create a folder for each season and move the files there
            season_folder = Path(folder) / f"season-{season_number}"
            
            os.makedirs(season_folder, exist_ok=True)
            
            new_episode_file = episode_file.replace("sson", "season").replace("sason", "season")
            
            source_path = Path(folder) / episode_file
            destination_path = season_folder / new_episode_file
            
            source_path.rename(destination_path)
            print(f"Moved {episode_file} to {season_folder}")
            
        print("All episodes organized by season.")
            