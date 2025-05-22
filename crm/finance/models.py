import uuid
from datetime import date

class FinancialTransaction:
    def __init__(self, type, description, amount, transaction_date=None, project_id=None, transaction_id=None):
        self.transaction_id = transaction_id if transaction_id else str(uuid.uuid4())
        self.project_id = project_id # Optional, foreign key to Project
        self.type = type # "Income" or "Expense"
        self.description = description
        self.amount = amount
        
        if isinstance(transaction_date, str):
            self.transaction_date = date.fromisoformat(transaction_date)
        else:
            self.transaction_date = transaction_date if transaction_date else date.today()

    def to_dict(self):
        return {
            'transaction_id': self.transaction_id,
            'project_id': self.project_id,
            'type': self.type, # "Income" or "Expense"
            'description': self.description,
            'amount': self.amount,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None
        }
