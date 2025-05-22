import uuid
from datetime import date

class Client:
    def __init__(self, name, contact_person, email, phone_number, address, company_name=None, client_id=None, project_ids=None):
        self.client_id = client_id if client_id else str(uuid.uuid4())
        self.name = name
        self.company_name = company_name
        self.contact_person = contact_person
        self.email = email
        self.phone_number = phone_number
        self.address = address
        self.date_added = date.today()
        self.project_ids = project_ids if project_ids else []

    def to_dict(self):
        return {
            'client_id': self.client_id,
            'name': self.name,
            'company_name': self.company_name,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone_number': self.phone_number,
            'address': self.address,
            'date_added': self.date_added.isoformat(), # For JSON serialization
            'project_ids': self.project_ids
        }
