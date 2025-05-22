import uuid
from datetime import date

class Employee:
    def __init__(self, full_name, email, phone_number, role, hire_date=None, employee_id=None, assigned_project_ids=None):
        self.employee_id = employee_id if employee_id else str(uuid.uuid4())
        self.full_name = full_name
        self.email = email
        self.phone_number = phone_number
        self.role = role # e.g., "Developer", "Project Manager", "Designer"
        
        if isinstance(hire_date, str):
            self.hire_date = date.fromisoformat(hire_date)
        else:
            self.hire_date = hire_date if hire_date else date.today()
            
        self.assigned_project_ids = assigned_project_ids if assigned_project_ids else []

    def to_dict(self):
        return {
            'employee_id': self.employee_id,
            'full_name': self.full_name,
            'email': self.email,
            'phone_number': self.phone_number,
            'role': self.role,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'assigned_project_ids': self.assigned_project_ids
        }
