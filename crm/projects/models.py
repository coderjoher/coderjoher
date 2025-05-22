import uuid
from datetime import date

class Project:
    def __init__(self, project_name, client_id, description, start_date, end_date=None, status="Planning", project_id=None, employee_ids=None, financial_transaction_ids=None):
        self.project_id = project_id if project_id else str(uuid.uuid4())
        self.project_name = project_name
        self.client_id = client_id # Foreign key to Client
        self.description = description
        
        if isinstance(start_date, str):
            self.start_date = date.fromisoformat(start_date)
        else:
            self.start_date = start_date
            
        if isinstance(end_date, str):
            self.end_date = date.fromisoformat(end_date)
        elif end_date is not None:
            self.end_date = end_date
        else:
            self.end_date = None
            
        self.status = status # e.g., "Planning", "In Progress", "Completed", "On Hold"
        self.employee_ids = employee_ids if employee_ids else []
        self.financial_transaction_ids = financial_transaction_ids if financial_transaction_ids else []

    def to_dict(self):
        return {
            'project_id': self.project_id,
            'project_name': self.project_name,
            'client_id': self.client_id,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'employee_ids': self.employee_ids,
            'financial_transaction_ids': self.financial_transaction_ids
        }
