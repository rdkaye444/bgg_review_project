# A utility function to request data from boardgame geek

import requests
import xml.etree.ElementTree as ET
import json
import os
import time
from datetime import datetime

# Global variable to store all game data in memory
GAMES_DATA = []

def get_game_details(game_id):
    """
    Fetch board game details from BoardGameGeek XML API and return as JSON.
    
    Args:
        game_id (int): The BGG game ID to fetch
        
    Returns:
        dict: Game details as a JSON object, or None if game not found
    """
    url = 'https://boardgamegeek.com/xmlapi2/thing'
    params = {'id': game_id, 'stats': 1}
    
    try:
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 404:
            print(f'Game not found for {game_id}')
            return None
            
        tree = ET.fromstring(response.content)
        
        # Find the first item element
        item = tree.find('.//item')
        if item is None:
            print(f'No item data found for game {game_id}')
            return None
            
        # Convert item element to dictionary
        game_data = {'game_id': game_id}  # Add game_id to the output
        for child in item:
            # Handle attributes
            if child.attrib:
                game_data[child.tag] = child.attrib
            # Handle text content
            if child.text and child.text.strip():
                game_data[child.tag] = child.text.strip()
            # Handle nested elements
            if len(child) > 0:
                game_data[child.tag] = []
                for subchild in child:
                    subchild_data = {'value': subchild.text.strip() if subchild.text else ''}
                    subchild_data.update(subchild.attrib)
                    game_data[child.tag].append(subchild_data)
        
        return game_data
        
    except requests.exceptions.RequestException as e:
        print(f'Error fetching game data: {e}')
        return None

def add_game_to_memory(game_data, game_id):
    """
    Add or update game data in memory.
    
    Args:
        game_data (dict): The game data to store
        game_id (int): The game ID
    """
    global GAMES_DATA
    
    # Check if game already exists in memory
    for i, game in enumerate(GAMES_DATA):
        if game.get('game_id') == game_id:
            GAMES_DATA[i] = game_data  # Update existing entry
            break
    else:
        GAMES_DATA.append(game_data)  # Add new entry
    
    print(f'Game {game_id} added to memory')

def save_all_games_to_json():
    """
    Save all games from memory to a JSON file.
    """
    if not os.path.exists('data'):
        os.makedirs('data')
        
    filename = 'data/games.json'
    
    # Write all data to file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(GAMES_DATA, f, indent=2, ensure_ascii=False)
    
    print(f'All game data saved to {filename}')

def load_existing_data():
    """
    Load existing game data from JSON file into memory.
    """
    global GAMES_DATA
    filename = 'data/games.json'
    
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                GAMES_DATA = json.load(f)
            print(f'Loaded {len(GAMES_DATA)} existing games from {filename}')
        except json.JSONDecodeError:
            print(f'Warning: Could not read existing data from {filename}. Starting fresh.')

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) != 2:
        print('Usage: python bgg.py <game_id>')
        sys.exit(1)
    
    if not sys.argv[1].isdigit():
        print('Usage, max game ID must be an integer')
        sys.exit(1)
        
    try:
        # Load existing data at start
        load_existing_data()
        
        game_id = int(sys.argv[1])
        for current_game_id in range(int(sys.argv[1])):
            game_data = get_game_details(current_game_id)
            
            if game_data:
                add_game_to_memory(game_data, current_game_id)
                time.sleep(3)
            
        # Save all data at the end
        save_all_games_to_json()
            
    except ValueError:
        print('Error: Game ID must be a number')
        sys.exit(1)