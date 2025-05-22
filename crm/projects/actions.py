from datetime import date
from .models import Project
from crm.database import load_data, save_data
from crm.clients.actions import get_client

def add_project(project_data):
    """
    Adds a new project.
    project_data: dict containing project information.
    Requires: project_name, client_id, description, start_date (date object or ISO string).
    Optional: end_date (date object or ISO string), status.
    """
    client_id = project_data.get('client_id')
    if not get_client(client_id):
        raise ValueError(f"Client with ID {client_id} not found.")

    new_project = Project(
        project_name=project_data.get('project_name'),
        client_id=client_id,
        description=project_data.get('description'),
        start_date=project_data.get('start_date'), # Project model handles conversion
        end_date=project_data.get('end_date'),   # Project model handles conversion
        status=project_data.get('status', "Planning") # Default status
    )
    
    all_projects_data = load_data('projects')
    all_projects_data.append(new_project.to_dict())
    save_data('projects', all_projects_data)
    
    return new_project.to_dict()

def get_project(project_id):
    """
    Retrieves a project by its ID.
    """
    all_projects_data = load_data('projects')
    for project_data in all_projects_data:
        if project_data.get('project_id') == project_id:
            return project_data
    return None

def list_projects(client_id=None):
    """
    Lists all projects, optionally filtered by client_id.
    """
    all_projects_data = load_data('projects')
    if client_id:
        return [p for p in all_projects_data if p.get('client_id') == client_id]
    return all_projects_data

def update_project(project_id, updated_data):
    """
    Updates an existing project.
    updated_data: dict containing fields to update.
    """
    if 'client_id' in updated_data:
        new_client_id = updated_data['client_id']
        if not get_client(new_client_id):
            raise ValueError(f"Client with ID {new_client_id} not found. Cannot update project's client ID.")

    all_projects_data = load_data('projects')
    project_found = False
    updated_project_data = None
    
    for i, project_data in enumerate(all_projects_data):
        if project_data.get('project_id') == project_id:
            # Update the project's data
            project_data.update(updated_data)
            
            # Handle date conversions if dates are in updated_data and are strings
            # The Project model's to_dict already ensures dates are ISO strings.
            # Here, we are working with dicts directly from JSON or to_dict.
            # If updated_data contains date objects, they should be converted to ISO strings.
            if 'start_date' in updated_data and isinstance(updated_data['start_date'], date):
                project_data['start_date'] = updated_data['start_date'].isoformat()
            if 'end_date' in updated_data and isinstance(updated_data['end_date'], date):
                project_data['end_date'] = updated_data['end_date'].isoformat()
            elif 'end_date' in updated_data and updated_data['end_date'] is None:
                 project_data['end_date'] = None


            all_projects_data[i] = project_data
            updated_project_data = project_data
            project_found = True
            break
            
    if project_found:
        save_data('projects', all_projects_data)
        return updated_project_data
    else:
        return None
