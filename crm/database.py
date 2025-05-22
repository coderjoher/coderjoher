import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def get_file_path(entity_type):
    return os.path.join(DATA_DIR, f"{entity_type}.json")

def save_data(entity_type, data_list):
    """Saves a list of entity objects to a JSON file.
    Each object in data_list should be a dictionary.
    """
    file_path = get_file_path(entity_type)
    with open(file_path, 'w') as f:
        json.dump(data_list, f, indent=4, default=str) # default=str to handle dates/uuids

def load_data(entity_type):
    """Loads a list of entity objects from a JSON file."""
    file_path = get_file_path(entity_type)
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return [] # Return empty list if file is empty or corrupted

# Example usage (for testing, can be removed later):
# if __name__ == '__main__':
#     # Test save
#     clients_data = [
#         {'client_id': '1', 'name': 'Test Client 1', 'email': 'test1@example.com'},
#         {'client_id': '2', 'name': 'Test Client 2', 'email': 'test2@example.com'}
#     ]
#     save_data('clients', clients_data)
#     print(f"Saved sample clients data to {get_file_path('clients')}")

#     # Test load
#     loaded_clients = load_data('clients')
#     print(f"Loaded clients: {loaded_clients}")
