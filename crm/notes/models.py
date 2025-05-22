import uuid
from datetime import datetime

class Note:
    def __init__(self, content, linked_to_type, linked_to_id=None, note_id=None, created_by_employee_id=None):
        self.note_id = note_id if note_id else str(uuid.uuid4())
        self.linked_to_type = linked_to_type # e.g., "Client", "Project", "Employee", "General"
        self.linked_to_id = linked_to_id # ID of the client, project, or employee
        self.content = content
        self.created_at = datetime.now()
        self.created_by_employee_id = created_by_employee_id # Optional, Employee ID

    def to_dict(self):
        return {
            'note_id': self.note_id,
            'linked_to_type': self.linked_to_type, # e.g., "Client", "Project", "Employee", "General"
            'linked_to_id': self.linked_to_id, # ID of the client, project, or employee
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None, # Ensure datetime is converted to string
            'created_by_employee_id': self.created_by_employee_id
        }
