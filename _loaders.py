
from datetime import datetime, timedelta, timezone
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


def load_card_movements_in_listings(card_id, start_date, end_date, list_in_program):
    url = f"https://api.trello.com/1/cards/{card_id}/actions?key={API_KEY}&token={API_TOKEN}"
    movements = []
    
    response = requests.get(url)
    if response.status_code == 200:
        response_json = response.json()
        response_json = [item for item in response_json if 'listBefore' in item['data'] and 'listAfter' in item['data']]
        
        exist_movement_in_date_range = False
        
        if len(response_json) > 0:
            if response_json[0]['data']['listAfter']['name'] == list_in_program:
                exist_movement_in_date_range = True
                
            if not exist_movement_in_date_range:
                for i in range(len(response_json)):
                    item = response_json[i]
                    
                    date = datetime.strptime(item['date'], '%Y-%m-%dT%H:%M:%S.%f%z')
                        
                    if end_date.date() > date.date() > start_date.date():
                        exist_movement_in_date_range = True
                        break            
            
            if exist_movement_in_date_range:
                for i in range(len(response_json)):
                    item = response_json[i]
                    
                    date = datetime.strptime(item['date'], '%Y-%m-%dT%H:%M:%S.%f%z')
                                            
                    if i == 0:
                        time_in_list = datetime.now(timezone.utc) - date
                    
                    elif i < len(response_json) - 1:
                        previous_item = response_json[i - 1]
                        previous_date = datetime.strptime(previous_item['date'], '%Y-%m-%dT%H:%M:%S.%f%z')
                        time_in_list = previous_date - date
                        
                    else:
                        time_in_list = timedelta()
                    
                    movements.append({
                        'date': date.strftime('%d/%m/%Y %H:%M:%S'),
                        'origin': item['data']['listBefore']['name'],
                        'destiny': item['data']['listAfter']['name'],
                        'time_in_list': format_timedelta_display(time_in_list)
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

    if len(movements) > 0:
        movements = sorted(movements, key=lambda x: x["date"])
        
        for i in range(len(movements)):
            movement = movements[i]

            if movement["destiny"] == list_program:
                days, time_str = movement["time_in_list"].split("d ")
                hours, minutes, seconds = map(int, time_str.split(":"))

                total_time_in_program += timedelta(days=int(days), hours=hours, minutes=minutes, seconds=seconds)

    return format_timedelta_display(total_time_in_program)


def get_time_in_progress(movements, list_program):
    if len(movements) <= 1:
        return format_timedelta_display(timedelta())
    
    total_time_in_progress = timedelta()    
    first_movement = movements[-1]
    last_movement = movements[0]
    date_first_movement = None
    
    if first_movement["date"] != '--' and last_movement["date"] != '--':
        date_first_movement = datetime.strptime(first_movement["date"], '%d/%m/%Y %H:%M:%S')
        date_last_movement = datetime.strptime(last_movement["date"], '%d/%m/%Y %H:%M:%S')
        total_time_in_progress += (
            date_last_movement.replace(tzinfo=timezone.utc) - date_first_movement.replace(tzinfo=timezone.utc)
        )
        
    if len(movements) > 0:        
        if last_movement["destiny"] == list_program:
            date_last_movement = datetime.strptime(last_movement["date"], '%d/%m/%Y %H:%M:%S')
            total_time_in_progress += (
                datetime.now().replace(tzinfo=timezone.utc) - date_last_movement.replace(tzinfo=timezone.utc)
            )
        
    return format_timedelta_display(total_time_in_progress)


def load_lists(boards, list_in_program, start_date, end_date):
    result = []
    
    for board in boards:
        for list_item in board['lists']:
            cards_response = load_cards_from_list(list_item['id'])
            
            if cards_response:                    
                formatted_cards = []

                for card_response in cards_response:
                    movements = load_card_movements_in_listings(card_response['id'], start_date, end_date, list_in_program)
                    
                    if movements:
                        custom_fields_detail = load_custom_fields_detail(card_response['id'])
                        time_in_progress = get_time_in_progress(movements, list_in_program)
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
