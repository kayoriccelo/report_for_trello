
from datetime import datetime, timedelta
import requests

from _settings import API_KEY, API_TOKEN
from _useful import calculate_working_hours, format_timedelta_display


def load_custom_fields_detail(card_id):
    def get_value(custom_field_id, custom_field_value_id):
        url_value = f'https://api.trello.com/1/customFields/{custom_field_id}?key={API_KEY}&token={API_TOKEN}'
        response_value = requests.get(url_value)
        
        if response_value.status_code == 200:
            response_json = response_value.json()
            value = None
            
            for option in response_json['options']:
                if option['id'] == custom_field_value_id:
                    value = option['value']['text']
            
            response_value.close()
                    
            return {response_json['name']: value}
        
        response_value.close()
        
        return {}
    
    url = f"https://api.trello.com/1/cards/{card_id}/customFieldItems?key={API_KEY}&token={API_TOKEN}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        response_json = response.json()
        
        result = []
        
        for item in response_json:
            result.append(get_value(item['idCustomField'], item['idValue']))
            
        response.close()
            
        return result
    
    return []


def load_custom_fields(board_id):
    url = f"https://api.trello.com/1/boards/{board_id}/customFields?key={API_KEY}&token={API_TOKEN}"

    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    
    else:
        print(f"Error while loading custom fields. Status code: {response.status_code}")
        
        return []


def load_card_movements_in_listings(card_id):
    url = f"https://api.trello.com/1/cards/{card_id}/actions?key={API_KEY}&token={API_TOKEN}"
    
    movements = []
    
    response = requests.get(url)
        
    if response.status_code == 200:
        response_json = response.json()
        
        for item in response_json:
            if 'listBefore' in item['data'] and 'listAfter' in item['data']:
                movements.append({
                    'date': item['date'],
                    'origin': item['data']['listBefore']['name'],
                    'destiny': item['data']['listAfter']['name']
                })
            
        response.close()
            
    return movements


def load_cards_from_list(list_id):
    url = f"https://api.trello.com/1/lists/{list_id}/cards?key={API_KEY}&token={API_TOKEN}&fields=all"
    
    response = requests.get(url)
        
    if response.status_code == 200:
        cards_response = response.json()
        
        response.close()
        
        return cards_response
    
    return []


def get_time_in_program(movements, list_program):
    total_time_in_program = timedelta()
    start_time_in_program = None

    for movement in sorted(movements, key=lambda x: x["date"]):
        movement_date = datetime.strptime(movement["date"], '%Y-%m-%dT%H:%M:%S.%f%z')

        # TODO - Kayo: renomear para ingles
        if movement["destiny"] == list_program:
            if start_time_in_program is None:
                start_time_in_program = movement_date
        
        else:
            if start_time_in_program is not None:
                total_time_in_program += calculate_working_hours(start_time_in_program, movement_date)
                start_time_in_program = None

    return format_timedelta_display(total_time_in_program)


def get_time_in_progress(movements):
    if len(movements) <= 1:
        return format_timedelta_display(timedelta())
    
    first_movement = movements[0]
    last_movement = movements[-1]
    date_first_movement = datetime.strptime(first_movement["date"], '%Y-%m-%dT%H:%M:%S.%f%z')
    date_last_movement = datetime.strptime(last_movement["date"], '%Y-%m-%dT%H:%M:%S.%f%z')
        
    return format_timedelta_display(date_last_movement  - date_first_movement)


def load_lists(lists, list_in_program):
    result = []
    
    for list_item in lists:
        cards_response = load_cards_from_list(list_item['id'])
        
        if cards_response:                    
            formatted_cards = []

            for card_response in cards_response:
                movements = load_card_movements_in_listings(card_response['id'])
                
                if movements:
                    custom_fields_detail = load_custom_fields_detail(card_response['id'])
                    time_in_progress = get_time_in_progress(movements)
                    time_in_program = get_time_in_program(movements, list_in_program)
                
                    formatted_card = {
                        "title": card_response.get("name"),
                        "labels": [{"name": label["name"], "color": label["color"]} for label in card_response.get("labels", [])],
                        "time_in_program": time_in_program,
                        "total_time": time_in_progress,
                        'movements': movements,
                    }
                    
                    for custom_field_detail in custom_fields_detail:
                        for key, value in custom_field_detail.items():
                            formatted_card[key] = value
                    
                    formatted_cards.append(formatted_card)
                
            if formatted_cards:                
                result.append({
                    'name': list_item['name'],
                    'cards': formatted_cards
                })
                
    return result
