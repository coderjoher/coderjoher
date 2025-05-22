from .models import Client
from crm.database import load_data, save_data

def add_client(client_data):
    """
    Adds a new client.
    client_data: dict containing client information.
    """
    new_client = Client(
        name=client_data.get('name'),
        contact_person=client_data.get('contact_person'),
        email=client_data.get('email'),
        phone_number=client_data.get('phone_number'),
        address=client_data.get('address'),
        company_name=client_data.get('company_name')
    )
    
    all_clients_data = load_data('clients')
    all_clients_data.append(new_client.to_dict())
    save_data('clients', all_clients_data)
    
    return new_client.to_dict()

def get_client(client_id):
    """
    Retrieves a client by their ID.
    """
    all_clients_data = load_data('clients')
    for client_data in all_clients_data:
        if client_data.get('client_id') == client_id:
            return client_data
    return None

def list_clients():
    """
    Lists all clients.
    """
    return load_data('clients')

def update_client(client_id, updated_data):
    """
    Updates an existing client.
    """
    all_clients_data = load_data('clients')
    client_found = False
    updated_client_data = None
    
    for i, client_data in enumerate(all_clients_data):
        if client_data.get('client_id') == client_id:
            # Update the client's data
            client_data.update(updated_data)
            # Ensure date_added is not overwritten if not in updated_data
            # and convert date objects if they are strings (e.g. from Client.to_dict())
            if 'date_added' in updated_data and isinstance(updated_data['date_added'], str):
                 # Assuming Client model's date_added is a date object,
                 # and to_dict converted it to isoformat string.
                 # Here, we are working with dicts from json, so it should be fine.
                 # If we were creating Client objects, we'd parse it.
                 pass # Keep as string for JSON
            
            all_clients_data[i] = client_data
            updated_client_data = client_data
            client_found = True
            break
            
    if client_found:
        save_data('clients', all_clients_data)
        return updated_client_data
    else:
        return None
