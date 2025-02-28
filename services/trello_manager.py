import requests
import json

class TrelloManager:
    def __init__(self, api_key, token):
        self.api_key = api_key
        self.token = token
        self.base_url = "https://api.trello.com/1"
        
    def create_board(self, name, description=None, default_lists=True):
        """Create a new Trello board with optional default lists."""
        url = f"{self.base_url}/boards"
        query = {
            'name': name,
            'desc': description or "",
            'defaultLists': default_lists,
            'key': self.api_key,
            'token': self.token
        }
        response = requests.post(url, params=query)
        return response.json()
    
    def create_list(self, board_id, name, position="bottom"):
        """Create a new list on a board."""
        url = f"{self.base_url}/lists"
        query = {
            'name': name,
            'idBoard': board_id,
            'pos': position,
            'key': self.api_key,
            'token': self.token
        }
        response = requests.post(url, params=query)
        return response.json()
    
    def create_card(self, list_id, name, description=None, due_date=None, labels=None):
        """Create a new card in a list."""
        url = f"{self.base_url}/cards"
        query = {
            'name': name,
            'desc': description or "",
            'idList': list_id,
            'key': self.api_key,
            'token': self.token
        }
        
        if due_date:
            query['due'] = due_date
            
        response = requests.post(url, params=query)
        card_data = response.json()
        
        # Add labels if provided
        if labels and 'id' in card_data:
            for label in labels:
                self.add_label_to_card(card_data['id'], label)
                
        return card_data
    
    def add_member_to_board(self, board_id, email):
        """Add a member to a board using their email."""
        url = f"{self.base_url}/boards/{board_id}/members"
        query = {
            'email': email,
            'type': 'normal',
            'key': self.api_key,
            'token': self.token
        }
        response = requests.put(url, params=query)
        return response.json()
    
    def add_label_to_card(self, card_id, label_name, color=None):
        """Add a label to a card."""
        # First, get available labels on the board
        card_info = self.get_card(card_id)
        if not card_info.get('id'):
            return {"error": "Card not found"}
        
        board_id = card_info.get('idBoard')
        
        # Get labels for this board
        labels = self.get_board_labels(board_id)
        
        # Find matching label
        label_id = None
        for label in labels:
            if label.get('name') == label_name:
                label_id = label.get('id')
                break
        
        # If no matching label exists and color is provided, create one
        if not label_id and color:
            new_label = self.create_label(board_id, label_name, color)
            label_id = new_label.get('id')
        
        # If no label found or created, we can't continue
        if not label_id:
            return {"error": f"Label '{label_name}' not found and could not be created"}
        
        # Add the label to the card
        url = f"{self.base_url}/cards/{card_id}/idLabels"
        query = {
            'value': label_id,
            'key': self.api_key,
            'token': self.token
        }
        response = requests.post(url, params=query)
        return response.json()

    def get_card(self, card_id):
        """Get card details."""
        url = f"{self.base_url}/cards/{card_id}"
        query = {
            'key': self.api_key,
            'token': self.token
        }
        response = requests.get(url, params=query)
        return response.json()

    def get_board_labels(self, board_id):
        """Get all labels for a board."""
        url = f"{self.base_url}/boards/{board_id}/labels"
        query = {
            'key': self.api_key,
            'token': self.token
        }
        response = requests.get(url, params=query)
        return response.json()

    def create_label(self, board_id, name, color):
        """Create a new label on a board."""
        url = f"{self.base_url}/boards/{board_id}/labels"
        query = {
            'name': name,
            'color': color,
            'key': self.api_key,
            'token': self.token
        }
        response = requests.post(url, params=query)
        return response.json()

    def move_card(self, card_id, list_id):
        """Move a card to a different list."""
        url = f"{self.base_url}/cards/{card_id}"
        query = {
            'idList': list_id,
            'key': self.api_key,
            'token': self.token
        }
        response = requests.put(url, params=query)
        return response.json()

    def add_checklist_to_card(self, card_id, title, items):
        """Add a checklist with items to a card."""
        # Create checklist
        url = f"{self.base_url}/cards/{card_id}/checklists"
        query = {
            'name': title,
            'key': self.api_key,
            'token': self.token
        }
        response = requests.post(url, params=query)
        
        if response.status_code != 200:
            return {"error": "Failed to create checklist"}
        
        checklist_id = response.json().get('id')
        
        # Add items to checklist
        results = []
        for item in items:
            item_response = self.add_checklist_item(checklist_id, item)
            results.append(item_response)
        
        return {
            "checklist_id": checklist_id,
            "items": results
        }

    def add_checklist_item(self, checklist_id, name):
        """Add an item to a checklist."""
        url = f"{self.base_url}/checklists/{checklist_id}/checkItems"
        query = {
            'name': name,
            'key': self.api_key,
            'token': self.token
        }
        response = requests.post(url, params=query)
        return response.json()

    def get_board_lists(self, board_id):
        """Get all lists on a board."""
        url = f"{self.base_url}/boards/{board_id}/lists"
        query = {
            'key': self.api_key,
            'token': self.token
        }
        response = requests.get(url, params=query)
        return response.json()

    def get_list_cards(self, list_id):
        """Get all cards in a list."""
        url = f"{self.base_url}/lists/{list_id}/cards"
        query = {
            'key': self.api_key,
            'token': self.token
        }
        response = requests.get(url, params=query)
        return response.json()

    def create_webhook(self, callback_url, id_model, description=None):
        """Create a webhook for a board, list, or card."""
        url = f"{self.base_url}/webhooks"
        payload = {
            'callbackURL': callback_url,
            'idModel': id_model,
            'description': description or f"Webhook for {id_model}",
            'key': self.api_key,
            'token': self.token
        }
        response = requests.post(url, json=payload)
        return response.json()

# Usage example
def setup_game_project_board(project_name, features, team_members):
    trello = TrelloManager(API_KEY, TOKEN)
    
    # Create main board
    board = trello.create_board(f"{project_name} - Development", default_lists=False)
    board_id = board['id']
    
    # Create custom lists
    lists = {}
    for list_name in ["Backlog", "Planning", "In Progress", "Testing", "Complete"]:
        list_data = trello.create_list(board_id, list_name)
        lists[list_name] = list_data['id']
    
    # Create feature cards
    for feature in features:
        trello.create_card(
            lists["Backlog"],
            feature["name"],
            description=feature["description"],
            labels=feature["labels"]
        )
    
    # Add team members to board
    for member in team_members:
        trello.add_member_to_board(board_id, member["email"])
    
    return board_id 