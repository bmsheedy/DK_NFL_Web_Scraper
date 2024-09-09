"""
---DraftKings NFL Web Scraper---
-----------------------------------------------------------------------------------------------------------------------
DraftKings Sportsbook web scraper to extract, aggregate, and format NFL game odds into a JSON file using Python’s BeautifulSoup library.
-----------------------------------------------------------------------------------------------------------------------
---Created by Brandon Sheedy---
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime


# Replacing the unicode minus for JSON readability.
def replace_minus(text):
    if text:
        return text.replace('\u2212', '-')
    return text


# DraftKings NFL games url.
url = 'https://sportsbook.draftkings.com/leagues/football/nfl?category=game-lines&subcategory=game'

# Sending request.
response = requests.get(url)

# Check request is valid.
if response.status_code == 200:
    
    nfl_games = []
    temp_game = []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Scraping for all teams' odds.
    outcome_cells = soup.find_all('div', class_='sportsbook-outcome-cell__body')

    # Iterate through each teams' odds.
    for index, cell in enumerate(outcome_cells):
        # Get aria-label: holds team names and description of what odds are for.
        aria_label = cell.get('aria-label')

        # Scraps for the odds of each wager type for a game.
        odds_span = cell.find('span', class_='sportsbook-odds american no-margin default-color') or \
                    cell.find('span', class_='sportsbook-odds american default-color')
                    
        odds = odds_span.text.strip() if odds_span else 'N/A'
        odds = replace_minus(odds)

        temp_game.append({
            'aria_label': aria_label,
            'odds': odds
        })
        
        # Every 6 items is 1 game.
        if (index + 1) % 6 == 0:
            # Separate odds for each team.
            team1_entries = temp_game[:3]
            team2_entries = temp_game[3:]
            
            # Reformatting scraped data for JSON readability.
            team1 = {
                'name':team1_entries[2]['aria_label'].strip(),
                'ml_odds':team1_entries[2]['odds'],
                'spread':team1_entries[0]['aria_label'].split()[-1],
                'spread_odds':team1_entries[0]['odds'],
                'o/u':team1_entries[1]['aria_label'],
                'ou_odds':team1_entries[1]['odds'],
            }
            team2 = {
                'name':team2_entries[2]['aria_label'].strip(),
                'ml_odds':team2_entries[2]['odds'],
                'spread':team2_entries[0]['aria_label'].split()[-1],
                'spread_odds':team2_entries[0]['odds'],
                'o/u':team2_entries[1]['aria_label'],
                'ou_odds':team2_entries[1]['odds'],
            }

            nfl_games.append({
                f'game_{(index + 1) // 6}': {
                    'team1': team1,
                    'team2': team2
                }
            })
            
            temp_game = []

    if temp_game:
        nfl_games.append({
            f'game_{(index + 1) // 6 + 1}': temp_game
        })

    # Timestamped filename.
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'dk_nfl_game_odds_{timestamp}.json'

    # Save data to JSON.
    with open(filename, 'w') as json_file:
        json.dump({'NFL_games': nfl_games}, json_file, indent=4)
