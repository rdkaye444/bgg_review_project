# A utility function to request data from boardgame geek

import requests
import xml.etree.ElementTree as ET
import json
import os
import time
import sys
import csv
from typing import Dict, Optional, Set
from xml.etree.ElementTree import ParseError
from datetime import datetime

# Global variable to store all game data in memory
GAMES_DATA = []

def log(message: str):
    """Print a message with a timestamp."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{timestamp}] {message}')

def get_game_details(game_id: str) -> Optional[Dict]:
    """
    Fetch board game details from BoardGameGeek XML API using game ID.
    
    Args:
        game_id (str): The BGG ID of the game to fetch
        
    Returns:
        dict: Game details as a JSON object, or None if game not found
    """
    url = 'https://boardgamegeek.com/xmlapi2/thing'
    params = {'id': game_id, 'stats': 1}
    
    try:
        response = requests.get(url, params=params, timeout=5)
        
        # Check if we got a successful response
        if response.status_code == 404:
            log(f'Game not found for ID: {game_id}')
            return None
        elif response.status_code == 429:
            log(f'Rate limit hit for ID {game_id}. Waiting 30 seconds...')
            time.sleep(30)  # Wait longer on rate limit
            return None
        elif response.status_code != 200:
            log(f'Unexpected HTTP status {response.status_code} for ID {game_id}')
            return None
            
        # Verify we got valid XML content
        content_type = response.headers.get('content-type', '')
        if 'xml' not in content_type.lower():
            log(f'Unexpected content type {content_type} for ID {game_id}')
            return None
            
        try:
            tree = ET.fromstring(response.content)
        except ParseError as e:
            log(f'Failed to parse XML for ID {game_id}: {str(e)}')
            return None
        except Exception as e:
            log(f'Unexpected XML processing error for ID {game_id}: {str(e)}')
            return None
        
        # Find the first item element
        item = tree.find('.//item')
        if item is None:
            log(f'No item data found for game ID: {game_id}')
            return None
            
        # Find the description
        description = item.find('.//description')
        if description is None:
            log(f'No description element found for game ID: {game_id}')
            return None
            
        description_text = description.text
        if not description_text or not description_text.strip():
            log(f'Empty description found for game ID: {game_id}')
            return None
            
        return {
            'bgg_id': game_id,
            'description': description_text.strip()
        }
        
    except requests.exceptions.Timeout:
        log(f'Timeout while fetching data for ID {game_id}')
        return None
    except requests.exceptions.ConnectionError:
        log(f'Connection error while fetching data for ID {game_id}')
        return None
    except requests.exceptions.RequestException as e:
        log(f'Error fetching game data for ID {game_id}: {str(e)}')
        return None
    except Exception as e:
        log(f'Unexpected error processing game ID {game_id}: {str(e)}')
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
    
    log(f'Game {game_id} added to memory')

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
    
    log(f'All game data saved to {filename}')

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
            log(f'Loaded {len(GAMES_DATA)} existing games from {filename}')
        except json.JSONDecodeError:
            log(f'Warning: Could not read existing data from {filename}. Starting fresh.')

def get_checkpoint_file(input_file: str) -> str:
    """Get the path to the checkpoint file for a given input file."""
    base_dir = os.path.dirname(input_file)
    base_name = os.path.basename(input_file)
    return os.path.join(base_dir, f'.{base_name}.checkpoint')

def load_processed_ids(checkpoint_file: str) -> Set[str]:
    """Load the set of already processed game IDs from checkpoint file."""
    if os.path.exists(checkpoint_file):
        try:
            with open(checkpoint_file, 'r') as f:
                return set(line.strip() for line in f)
        except Exception as e:
            log(f'Warning: Could not read checkpoint file: {e}')
    return set()

def save_processed_id(checkpoint_file: str, game_id: str):
    """Save a processed game ID to the checkpoint file."""
    try:
        with open(checkpoint_file, 'a') as f:
            f.write(f'{game_id}\n')
    except Exception as e:
        log(f'Warning: Could not update checkpoint file: {e}')

def enrich_games_file(input_file: str, output_file: str):
    """
    Read games from input CSV file, enrich with BGG descriptions, and write to output file.
    Supports resuming from previous interruptions.
    
    Args:
        input_file (str): Path to input CSV file (must have 'id' column)
        output_file (str): Path to output CSV file
    """
    if not os.path.exists(input_file):
        log(f'Input file not found: {input_file}')
        return
        
    # Setup checkpoint tracking
    checkpoint_file = get_checkpoint_file(input_file)
    processed_ids = load_processed_ids(checkpoint_file)
    if processed_ids:
        log(f'Resuming from checkpoint with {len(processed_ids)} previously processed games')
    
    enriched_games = []
    error_count = 0
    max_errors = 1000  # Maximum number of consecutive errors before aborting
    
    # Load existing enriched data if available
    existing_enriched_data = {}
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'id' in row and 'description' in row:
                        existing_enriched_data[row['id']] = row['description']
        except Exception as e:
            log(f'Warning: Could not read existing enriched data: {e}')
    
    try:
        # First pass: read all data and collect existing results
        with open(input_file, 'r', encoding='utf-8') as f:
            try:
                reader = csv.DictReader(f)
                if 'id' not in reader.fieldnames:
                    log('Input file must have an "id" column')
                    return
                
                # Read all rows first
                all_rows = list(reader)
                total_games = len(all_rows)
                log(f'Found {total_games} games in input file')
                
                # Process each row
                for i, row in enumerate(all_rows, 1):
                    game_id = row['id'].strip()
                    if not game_id:  # Skip empty IDs
                        log('Skipping row with empty ID')
                        continue
                    
                    # Check if we already have enriched data for this game
                    if game_id in existing_enriched_data:
                        enriched_row = {**row, 'description': existing_enriched_data[game_id]}
                        enriched_games.append(enriched_row)
                        continue
                    
                    # Skip already processed games unless they're missing from enriched_games
                    if game_id in processed_ids:
                        log(f'Skipping already processed game ID: {game_id} ({i}/{total_games})')
                        # Try to get BGG details again if we don't have the description
                        bgg_data = get_game_details(game_id)
                        if bgg_data:
                            enriched_row = {**row, 'description': bgg_data['description']}
                        else:
                            enriched_row = row
                        enriched_games.append(enriched_row)
                        continue
                        
                    log(f'Processing game ID: {game_id} ({i}/{total_games})')
                    
                    # Get BGG details
                    bgg_data = get_game_details(game_id)
                    if bgg_data:
                        # Merge original row with BGG data
                        enriched_row = {**row, 'description': bgg_data['description']}
                        enriched_games.append(enriched_row)
                        error_count = 0  # Reset error count on success
                        
                        # Update checkpoint
                        save_processed_id(checkpoint_file, game_id)
                    else:
                        # Keep original row if no BGG data found
                        enriched_games.append(row)
                        error_count += 1
                        
                        if error_count >= max_errors:
                            log(f'Aborting after {max_errors} consecutive errors')
                            break
                    
                    # Be nice to the BGG API
                    time.sleep(2)
                    
                    # Periodically save progress to output file
                    if i % 10 == 0:  # Save every 10 games
                        save_output_file(output_file, enriched_games)
                    
            except csv.Error as e:
                log(f'Error reading CSV file: {str(e)}')
                return
    except Exception as e:
        log(f'Error processing input file: {str(e)}')
        return
    finally:
        # Always try to save progress before exiting
        if enriched_games:
            save_output_file(output_file, enriched_games)

def save_output_file(output_file: str, enriched_games: list):
    """Save the current progress to the output file."""
    try:
        fieldnames = list(enriched_games[0].keys())
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(enriched_games)
        log(f'Progress saved to: {output_file}')
    except Exception as e:
        log(f'Error writing output file: {str(e)}')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        log('Usage: python bgg.py <input_file.csv> <output_file.csv>')
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        enrich_games_file(input_file, output_file)
    except KeyboardInterrupt:
        log('\nProcess interrupted by user')
        log('Progress has been saved - run the same command to resume')
        sys.exit(1)
    except Exception as e:
        log(f'Unexpected error: {str(e)}')
        log('Progress has been saved - run the same command to resume')
        sys.exit(1)