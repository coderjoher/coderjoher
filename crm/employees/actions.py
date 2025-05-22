from datetime import date
from .models import Employee
from crm.database import load_data, save_data
from crm.projects.actions import get_project # For validation

def add_employee(employee_data):
    """
    Adds a new employee.
    employee_data: dict containing employee information.
    Requires: full_name, email, phone_number, role.
    Optional: hire_date (date object or ISO string, defaults to today).
    """
    new_employee = Employee(
        full_name=employee_data.get('full_name'),
        email=employee_data.get('email'),
        phone_number=employee_data.get('phone_number'),
        role=employee_data.get('role'),
        hire_date=employee_data.get('hire_date') # Employee model handles default/conversion
    )
    
    all_employees_data = load_data('employees')
    all_employees_data.append(new_employee.to_dict())
    save_data('employees', all_employees_data)
    
    return new_employee.to_dict()

def get_employee(employee_id):
    """
    Retrieves an employee by their ID.
    """
    all_employees_data = load_data('employees')
    for employee_data in all_employees_data:
        if employee_data.get('employee_id') == employee_id:
            return employee_data
    return None

def list_employees():
    """
    Lists all employees.
    """
    return load_data('employees')

def assign_project_to_employee(employee_id, project_id):
    """
    Assigns a project to an employee.
    """
    # First, ensure the employee exists
    all_employees_data = load_data('employees')
    employee_idx = -1
    current_employee_data = None

    for i, emp_data in enumerate(all_employees_data):
        if emp_data.get('employee_id') == employee_id:
            employee_idx = i
            current_employee_data = emp_data
            break
    
    if not current_employee_data:
        # Employee not found, so we can't assign a project.
        # Depending on desired behavior, could raise ValueError or return None.
        # Current tests expect None if employee is not found.
        return None

    # Then, ensure the project exists
    if not get_project(project_id):
        raise ValueError(f"Project with ID {project_id} not found. Cannot assign to employee.")

    # Proceed with assignment
    if project_id not in current_employee_data.get('assigned_project_ids', []):
        current_employee_data.setdefault('assigned_project_ids', []).append(project_id)
    
    all_employees_data[employee_idx] = current_employee_data # Update the list
    save_data('employees', all_employees_data)
    
    return current_employee_data

def update_employee(employee_id, updated_data):
    """
    Updates an existing employee.
    updated_data: dict containing fields to update.
    """
    all_employees_data = load_data('employees')
    employee_found = False
    updated_employee_data_dict = None
    
    for i, emp_data in enumerate(all_employees_data):
        if emp_data.get('employee_id') == employee_id:
            # Update the employee's data
            emp_data.update(updated_data)
            
            # Handle hire_date conversion if it's in updated_data and is a date object
            if 'hire_date' in updated_data and isinstance(updated_data['hire_date'], date):
                emp_data['hire_date'] = updated_data['hire_date'].isoformat()
            
            all_employees_data[i] = emp_data
            updated_employee_data_dict = emp_data
            employee_found = True
            break
            
    if employee_found:
        save_data('employees', all_employees_data)
        return updated_employee_data_dict
    else:
        return None
