from datetime import date, datetime
import json # For pretty printing

# Import action modules
from crm.clients import actions as client_actions
from crm.projects import actions as project_actions
from crm.employees import actions as employee_actions
from crm.finance import actions as finance_actions
from crm.notes import actions as note_actions
from crm.notes.actions import ALLOWED_LINKED_TYPES as NOTE_ALLOWED_LINKED_TYPES


# --- Input Helper Functions ---
def get_string_input(prompt, optional=False):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        elif optional:
            return None # Allow empty input if optional
        print("Input cannot be empty.")

def get_date_input(prompt, optional=False):
    while True:
        date_str = input(prompt).strip()
        if not date_str and optional:
            return None
        if not date_str and not optional:
            print("Date cannot be empty.")
            continue
        try:
            return date.fromisoformat(date_str)
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

def get_float_input(prompt, optional=False):
    while True:
        value_str = input(prompt).strip()
        if not value_str and optional:
            return None
        if not value_str and not optional:
            print("Input cannot be empty.")
            continue
        try:
            value = float(value_str)
            if value > 0:
                return value
            print("Value must be positive.")
        except ValueError:
            print("Invalid number. Please enter a valid float.")

def get_choice_input(prompt, choices_dict):
    print(prompt)
    for key, description in choices_dict.items():
        print(f"  {key}. {description}")
    
    while True:
        choice = input("Enter choice: ").strip()
        if choice in choices_dict:
            return choice
        print(f"Invalid choice. Please select from {', '.join(choices_dict.keys())}.")

def get_yes_no_input(prompt):
    while True:
        value = input(prompt + " (y/n): ").strip().lower()
        if value in ['y', 'yes']:
            return True
        elif value in ['n', 'no']:
            return False
        print("Invalid input. Please enter 'y' or 'n'.")

# --- Utility for printing results ---
def print_results(data):
    if data is None:
        print("No data found or operation failed.")
    elif isinstance(data, list) and not data:
        print("No items found.")
    elif isinstance(data, (dict, list)):
        print(json.dumps(data, indent=2, default=str)) # default=str for dates/uuids
    else:
        print(data)

# --- Handler Functions (Clients) ---
def handle_add_client():
    print("\n-- Add New Client --")
    try:
        name = get_string_input("Full Name: ")
        contact_person = get_string_input("Contact Person: ")
        email = get_string_input("Email: ")
        phone_number = get_string_input("Phone Number: ")
        address = get_string_input("Address: ")
        company_name = get_string_input("Company Name (optional): ", optional=True)
        
        client_data = {
            'name': name,
            'contact_person': contact_person,
            'email': email,
            'phone_number': phone_number,
            'address': address,
            'company_name': company_name
        }
        new_client = client_actions.add_client(client_data)
        print("\nClient added successfully:")
        print_results(new_client)
    except ValueError as e:
        print(f"Error adding client: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def handle_list_clients():
    print("\n-- List All Clients --")
    try:
        clients = client_actions.list_clients()
        if clients:
            print_results(clients)
        else:
            print("No clients found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def handle_get_client():
    print("\n-- Get Client by ID --")
    try:
        client_id = get_string_input("Enter Client ID: ")
        client = client_actions.get_client(client_id)
        if client:
            print_results(client)
        else:
            print(f"Client with ID '{client_id}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def handle_update_client():
    print("\n-- Update Client --")
    try:
        client_id = get_string_input("Enter Client ID to update: ")
        client = client_actions.get_client(client_id)
        if not client:
            print(f"Client with ID '{client_id}' not found.")
            return

        print("Enter new values (leave blank to keep current):")
        name = get_string_input(f"Name ({client.get('name')}): ", optional=True)
        contact_person = get_string_input(f"Contact Person ({client.get('contact_person')}): ", optional=True)
        email = get_string_input(f"Email ({client.get('email')}): ", optional=True)
        phone_number = get_string_input(f"Phone Number ({client.get('phone_number')}): ", optional=True)
        address = get_string_input(f"Address ({client.get('address')}): ", optional=True)
        company_name = get_string_input(f"Company Name ({client.get('company_name', '')}): ", optional=True)

        update_data = {}
        if name: update_data['name'] = name
        if contact_person: update_data['contact_person'] = contact_person
        if email: update_data['email'] = email
        if phone_number: update_data['phone_number'] = phone_number
        if address: update_data['address'] = address
        if company_name is not None: update_data['company_name'] = company_name # Allow clearing company name

        if not update_data:
            print("No changes provided.")
            return

        updated_client = client_actions.update_client(client_id, update_data)
        print("\nClient updated successfully:")
        print_results(updated_client)
    except ValueError as e:
        print(f"Error updating client: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# --- Handler Functions (Projects) ---
def handle_add_project():
    print("\n-- Add New Project --")
    try:
        project_name = get_string_input("Project Name: ")
        client_id = get_string_input("Client ID for this project: ")
        # Basic check if client exists (optional, can be more robust)
        if not client_actions.get_client(client_id):
            print(f"Warning: Client with ID '{client_id}' not found. Proceeding anyway.")
        description = get_string_input("Description: ")
        start_date = get_date_input("Start Date (YYYY-MM-DD): ")
        end_date_str = get_string_input("End Date (YYYY-MM-DD, optional, leave blank if none): ", optional=True)
        end_date = date.fromisoformat(end_date_str) if end_date_str else None
        status = get_string_input("Status (e.g., Planning, In Progress - optional, defaults to 'Planning'): ", optional=True) or "Planning"

        project_data = {
            'project_name': project_name,
            'client_id': client_id,
            'description': description,
            'start_date': start_date,
            'end_date': end_date,
            'status': status
        }
        new_project = project_actions.add_project(project_data)
        print("\nProject added successfully:")
        print_results(new_project)
    except ValueError as e:
        print(f"Error adding project: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def handle_list_projects():
    print("\n-- List Projects --")
    try:
        filter_by_client = get_yes_no_input("Filter by Client ID?")
        client_id_filter = None
        if filter_by_client:
            client_id_filter = get_string_input("Enter Client ID to filter by: ")
        
        projects = project_actions.list_projects(client_id=client_id_filter)
        if projects:
            print_results(projects)
        else:
            print("No projects found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def handle_get_project():
    print("\n-- Get Project by ID --")
    try:
        project_id = get_string_input("Enter Project ID: ")
        project = project_actions.get_project(project_id)
        if project:
            print_results(project)
        else:
            print(f"Project with ID '{project_id}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def handle_update_project():
    print("\n-- Update Project --")
    try:
        project_id = get_string_input("Enter Project ID to update: ")
        project = project_actions.get_project(project_id)
        if not project:
            print(f"Project with ID '{project_id}' not found.")
            return

        print("Enter new values (leave blank to keep current):")
        project_name = get_string_input(f"Project Name ({project.get('project_name')}): ", optional=True)
        # client_id typically not changed, or handled differently (e.g. re-assign project)
        description = get_string_input(f"Description ({project.get('description')}): ", optional=True)
        
        current_start_date = project.get('start_date')
        start_date_str = get_string_input(f"Start Date ({current_start_date}) (YYYY-MM-DD): ", optional=True)
        start_date = date.fromisoformat(start_date_str) if start_date_str else None

        current_end_date = project.get('end_date', '') or '' # Handle None for display
        end_date_str = get_string_input(f"End Date ({current_end_date}) (YYYY-MM-DD, or 'clear' to remove): ", optional=True)
        end_date = None
        clear_end_date = False
        if end_date_str:
            if end_date_str.lower() == 'clear':
                clear_end_date = True
            else:
                try:
                    end_date = date.fromisoformat(end_date_str)
                except ValueError:
                    print("Invalid end date format. Not changed.")
        
        status = get_string_input(f"Status ({project.get('status')}): ", optional=True)

        update_data = {}
        if project_name: update_data['project_name'] = project_name
        if description: update_data['description'] = description
        if start_date: update_data['start_date'] = start_date # Project actions will convert to string if needed
        if end_date: update_data['end_date'] = end_date
        if clear_end_date: update_data['end_date'] = None
        if status: update_data['status'] = status
        
        if not update_data:
            print("No changes provided.")
            return

        updated_project = project_actions.update_project(project_id, update_data)
        print("\nProject updated successfully:")
        print_results(updated_project)
    except ValueError as e:
        print(f"Error updating project: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# --- Handler Functions (Employees) ---
def handle_add_employee():
    print("\n-- Add New Employee --")
    try:
        full_name = get_string_input("Full Name: ")
        email = get_string_input("Email: ")
        phone_number = get_string_input("Phone Number: ")
        role = get_string_input("Role (e.g., Developer, Manager): ")
        hire_date_str = get_string_input("Hire Date (YYYY-MM-DD, optional, defaults to today): ", optional=True)
        hire_date = date.fromisoformat(hire_date_str) if hire_date_str else None

        employee_data = {
            'full_name': full_name,
            'email': email,
            'phone_number': phone_number,
            'role': role,
            'hire_date': hire_date
        }
        new_employee = employee_actions.add_employee(employee_data)
        print("\nEmployee added successfully:")
        print_results(new_employee)
    except ValueError as e:
        print(f"Error adding employee: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def handle_list_employees():
    print("\n-- List All Employees --")
    try:
        employees = employee_actions.list_employees()
        if employees:
            print_results(employees)
        else:
            print("No employees found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def handle_get_employee():
    print("\n-- Get Employee by ID --")
    try:
        employee_id = get_string_input("Enter Employee ID: ")
        employee = employee_actions.get_employee(employee_id)
        if employee:
            print_results(employee)
        else:
            print(f"Employee with ID '{employee_id}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def handle_update_employee():
    print("\n-- Update Employee --")
    try:
        employee_id = get_string_input("Enter Employee ID to update: ")
        employee = employee_actions.get_employee(employee_id)
        if not employee:
            print(f"Employee with ID '{employee_id}' not found.")
            return

        print("Enter new values (leave blank to keep current):")
        full_name = get_string_input(f"Full Name ({employee.get('full_name')}): ", optional=True)
        email = get_string_input(f"Email ({employee.get('email')}): ", optional=True)
        phone_number = get_string_input(f"Phone Number ({employee.get('phone_number')}): ", optional=True)
        role = get_string_input(f"Role ({employee.get('role')}): ", optional=True)
        
        current_hire_date = employee.get('hire_date')
        hire_date_str = get_string_input(f"Hire Date ({current_hire_date}) (YYYY-MM-DD): ", optional=True)
        hire_date = date.fromisoformat(hire_date_str) if hire_date_str else None

        update_data = {}
        if full_name: update_data['full_name'] = full_name
        if email: update_data['email'] = email
        if phone_number: update_data['phone_number'] = phone_number
        if role: update_data['role'] = role
        if hire_date: update_data['hire_date'] = hire_date # Employee actions will convert

        if not update_data:
            print("No changes provided.")
            return

        updated_employee = employee_actions.update_employee(employee_id, update_data)
        print("\nEmployee updated successfully:")
        print_results(updated_employee)
    except ValueError as e:
        print(f"Error updating employee: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def handle_assign_project_to_employee():
    print("\n-- Assign Project to Employee --")
    try:
        employee_id = get_string_input("Enter Employee ID: ")
        if not employee_actions.get_employee(employee_id):
             print(f"Employee with ID '{employee_id}' not found.")
             return
        project_id = get_string_input("Enter Project ID to assign: ")
        if not project_actions.get_project(project_id): # Basic check
             print(f"Warning: Project with ID '{project_id}' not found. Proceeding with assignment.")

        updated_employee = employee_actions.assign_project_to_employee(employee_id, project_id)
        if updated_employee:
            print(f"\nProject '{project_id}' assigned to employee '{employee_id}':")
            print_results(updated_employee)
        else:
            # This case might not be hit if get_employee above catches it, but good for safety
            print(f"Failed to assign project. Employee with ID '{employee_id}' might not exist.")
            
    except ValueError as e: # Should not happen with current assign_project logic, but good practice
        print(f"Error assigning project: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# --- Handler Functions (Finance) ---
def handle_add_transaction():
    print("\n-- Add Financial Transaction --")
    try:
        type_choices = {'1': 'Income', '2': 'Expense'}
        type_choice = get_choice_input("Transaction Type:", type_choices)
        transaction_type = type_choices[type_choice]
        
        description = get_string_input("Description: ")
        amount = get_float_input("Amount: ") # Ensures positive float
        
        project_id = get_string_input("Project ID (optional, leave blank if none): ", optional=True)
        if project_id and not project_actions.get_project(project_id): # Basic check
            print(f"Warning: Project with ID '{project_id}' not found. Proceeding.")

        transaction_date_str = get_string_input("Transaction Date (YYYY-MM-DD, optional, defaults to today): ", optional=True)
        transaction_date = date.fromisoformat(transaction_date_str) if transaction_date_str else None

        transaction_data = {
            'type': transaction_type,
            'description': description,
            'amount': amount,
            'project_id': project_id,
            'transaction_date': transaction_date
        }
        new_transaction = finance_actions.add_transaction(transaction_data)
        print("\nTransaction added successfully:")
        print_results(new_transaction)
    except ValueError as e:
        print(f"Error adding transaction: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def handle_get_project_finances():
    print("\n-- Get Project Finances --")
    try:
        project_id = get_string_input("Enter Project ID: ")
        transactions = finance_actions.get_project_finances(project_id)
        if transactions:
            print(f"\nFinances for Project ID '{project_id}':")
            print_results(transactions)
        else:
            print(f"No financial transactions found for project ID '{project_id}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def handle_get_overall_financial_summary():
    print("\n-- Overall Financial Summary --")
    try:
        summary = finance_actions.get_overall_financial_summary()
        print_results(summary)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# --- Handler Functions (Notes) ---
def handle_add_note():
    print("\n-- Add New Note --")
    try:
        content = get_string_input("Note Content: ")
        
        # Build choices for linked_to_type
        type_choices = {str(i+1): type_name for i, type_name in enumerate(NOTE_ALLOWED_LINKED_TYPES)}
        type_choice_key = get_choice_input("Link this note to:", type_choices)
        linked_to_type = type_choices[type_choice_key]
        
        linked_to_id = None
        if linked_to_type != "General":
            linked_to_id = get_string_input(f"Enter ID for {linked_to_type}: ")
            # Basic existence check (optional)
            if linked_to_type == "Client" and not client_actions.get_client(linked_to_id):
                print(f"Warning: Client with ID '{linked_to_id}' not found.")
            elif linked_to_type == "Project" and not project_actions.get_project(linked_to_id):
                 print(f"Warning: Project with ID '{linked_to_id}' not found.")
            elif linked_to_type == "Employee" and not employee_actions.get_employee(linked_to_id):
                 print(f"Warning: Employee with ID '{linked_to_id}' not found.")


        created_by_employee_id = get_string_input("Created by Employee ID (optional): ", optional=True)
        if created_by_employee_id and not employee_actions.get_employee(created_by_employee_id):
            print(f"Warning: Employee (creator) with ID '{created_by_employee_id}' not found.")

        note_data = {
            'content': content,
            'linked_to_type': linked_to_type,
            'linked_to_id': linked_to_id,
            'created_by_employee_id': created_by_employee_id
        }
        new_note = note_actions.add_note(note_data)
        print("\nNote added successfully:")
        print_results(new_note)
    except ValueError as e:
        print(f"Error adding note: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def handle_get_notes_for_item():
    print("\n-- Get Notes for Item --")
    try:
        # Build choices for item_type (excluding "General" as it needs different handling)
        item_type_choices_list = [t for t in NOTE_ALLOWED_LINKED_TYPES if t != "General"]
        item_type_choices = {str(i+1): type_name for i, type_name in enumerate(item_type_choices_list)}
        
        if not item_type_choices: # Should not happen with current NOTE_ALLOWED_LINKED_TYPES
            print("No item types available to link notes to (excluding 'General').")
            return

        type_choice_key = get_choice_input("Select Item Type:", item_type_choices)
        item_type = item_type_choices[type_choice_key]
        
        item_id = get_string_input(f"Enter {item_type} ID: ")
        
        notes = note_actions.get_notes_for_item(item_type, item_id)
        if notes:
            print(f"\nNotes for {item_type} ID '{item_id}':")
            print_results(notes)
        else:
            print(f"No notes found for {item_type} ID '{item_id}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def handle_list_all_notes():
    print("\n-- List All Notes --")
    try:
        notes = note_actions.list_all_notes()
        if notes:
            print_results(notes)
        else:
            print("No notes found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# --- Sub-Menus ---
def show_client_menu():
    menu_options = {
        '1': "Add New Client",
        '2': "List All Clients",
        '3': "Get Client by ID",
        '4': "Update Client",
        '0': "Back to Main Menu"
    }
    while True:
        print("\n-- Manage Clients --")
        choice = get_choice_input("Client Menu:", menu_options)
        if choice == '1': handle_add_client()
        elif choice == '2': handle_list_clients()
        elif choice == '3': handle_get_client()
        elif choice == '4': handle_update_client()
        elif choice == '0': break
        input("\nPress Enter to continue...")


def show_project_menu():
    menu_options = {
        '1': "Add New Project",
        '2': "List Projects",
        '3': "Get Project by ID",
        '4': "Update Project",
        '0': "Back to Main Menu"
    }
    while True:
        print("\n-- Manage Projects --")
        choice = get_choice_input("Project Menu:", menu_options)
        if choice == '1': handle_add_project()
        elif choice == '2': handle_list_projects()
        elif choice == '3': handle_get_project()
        elif choice == '4': handle_update_project()
        elif choice == '0': break
        input("\nPress Enter to continue...")

def show_employee_menu():
    menu_options = {
        '1': "Add New Employee",
        '2': "List All Employees",
        '3': "Get Employee by ID",
        '4': "Update Employee",
        '5': "Assign Project to Employee",
        '0': "Back to Main Menu"
    }
    while True:
        print("\n-- Manage Employees --")
        choice = get_choice_input("Employee Menu:", menu_options)
        if choice == '1': handle_add_employee()
        elif choice == '2': handle_list_employees()
        elif choice == '3': handle_get_employee()
        elif choice == '4': handle_update_employee()
        elif choice == '5': handle_assign_project_to_employee()
        elif choice == '0': break
        input("\nPress Enter to continue...")


def show_finance_menu():
    menu_options = {
        '1': "Add Financial Transaction",
        '2': "Get Project Finances",
        '3': "Get Overall Financial Summary",
        '0': "Back to Main Menu"
    }
    while True:
        print("\n-- Manage Finance --")
        choice = get_choice_input("Finance Menu:", menu_options)
        if choice == '1': handle_add_transaction()
        elif choice == '2': handle_get_project_finances()
        elif choice == '3': handle_get_overall_financial_summary()
        elif choice == '0': break
        input("\nPress Enter to continue...")


def show_notes_menu():
    menu_options = {
        '1': "Add New Note",
        '2': "Get Notes for Specific Item",
        '3': "List All Notes",
        '0': "Back to Main Menu"
    }
    while True:
        print("\n-- Manage Notes --")
        choice = get_choice_input("Notes Menu:", menu_options)
        if choice == '1': handle_add_note()
        elif choice == '2': handle_get_notes_for_item()
        elif choice == '3': handle_list_all_notes()
        elif choice == '0': break
        input("\nPress Enter to continue...")


# --- Main Menu & Loop ---
def show_main_menu():
    main_menu_options = {
        '1': "Manage Clients",
        '2': "Manage Projects",
        '3': "Manage Employees",
        '4': "Manage Finance",
        '5': "Manage Notes",
        '0': "Exit CRM"
    }
    print("\n===== CRM Main Menu =====")
    return get_choice_input("Main Menu:", main_menu_options)

def main():
    print("Welcome to the Basic CRM CLI!")
    while True:
        choice = show_main_menu()
        
        if choice == '1':
            show_client_menu()
        elif choice == '2':
            show_project_menu()
        elif choice == '3':
            show_employee_menu()
        elif choice == '4':
            show_finance_menu()
        elif choice == '5':
            show_notes_menu()
        elif choice == '0':
            print("Exiting CRM. Goodbye!")
            break
        # No else needed as get_choice_input handles invalid choices

if __name__ == "__main__":
    main()
