from datetime import datetime
from .models import Note
from crm.database import load_data, save_data
from crm.clients.actions import get_client
from crm.projects.actions import get_project
from crm.employees.actions import get_employee

ALLOWED_LINKED_TYPES = ["Client", "Project", "Employee", "General"]

def add_note(note_data):
    """
    Adds a new note.
    note_data: dict containing note information.
    Requires: content, linked_to_type.
    linked_to_id is required if linked_to_type is not "General".
    created_by_employee_id is optional.
    """
    content = note_data.get('content')
    linked_to_type = note_data.get('linked_to_type')
    linked_to_id = note_data.get('linked_to_id')
    created_by_employee_id = note_data.get('created_by_employee_id')

    if not content:
        raise ValueError("Note content cannot be empty.")
    
    if linked_to_type not in ALLOWED_LINKED_TYPES:
        raise ValueError(f"Invalid linked_to_type: {linked_to_type}. Allowed types are: {ALLOWED_LINKED_TYPES}")

    if linked_to_type != "General" and not linked_to_id:
        raise ValueError(f"linked_to_id is required when linked_to_type is '{linked_to_type}'.")

    # Validate linked_to_id existence if provided and not "General"
    if linked_to_id and linked_to_type != "General":
        entity_exists = False
        if linked_to_type == "Client":
            entity_exists = get_client(linked_to_id) is not None
        elif linked_to_type == "Project":
            entity_exists = get_project(linked_to_id) is not None
        elif linked_to_type == "Employee":
            entity_exists = get_employee(linked_to_id) is not None
        
        if not entity_exists:
            raise ValueError(f"{linked_to_type} with ID {linked_to_id} not found. Cannot add note.")

    # Validate created_by_employee_id existence if provided
    if created_by_employee_id and not get_employee(created_by_employee_id):
        raise ValueError(f"Employee (creator) with ID {created_by_employee_id} not found. Cannot add note.")


    new_note = Note(
        content=content,
        linked_to_type=linked_to_type,
        linked_to_id=linked_to_id,
        created_by_employee_id=created_by_employee_id
    )
    
    all_notes_data = load_data('notes')
    all_notes_data.append(new_note.to_dict())
    save_data('notes', all_notes_data)
    
    return new_note.to_dict()

def get_notes_for_item(item_type, item_id):
    """
    Retrieves notes for a specific item (Client, Project, Employee).
    "General" notes are not retrieved by this function as they are not linked to a specific item_id.
    """
    if item_type == "General":
        return [] # General notes are not linked to a specific item_id in the same way.

    all_notes_data = load_data('notes')
    item_notes = [
        note for note in all_notes_data 
        if note.get('linked_to_type') == item_type and note.get('linked_to_id') == item_id
    ]
    return item_notes

def list_all_notes():
    """
    Lists all notes.
    """
    return load_data('notes')
