from datetime import date
from .models import FinancialTransaction
from crm.database import load_data, save_data
from crm.projects.actions import get_project # For validation

def add_transaction(transaction_data):
    """
    Adds a new financial transaction.
    transaction_data: dict containing transaction information.
    Requires: type ("Income" or "Expense"), description, amount.
    Optional: project_id, transaction_date (date object or ISO string).
    """
    transaction_type = transaction_data.get('type')
    amount = transaction_data.get('amount')

    if transaction_type not in ["Income", "Expense"]:
        raise ValueError("Transaction type must be 'Income' or 'Expense'")
    
    if not isinstance(amount, (int, float)) or amount <= 0:
        raise ValueError("Transaction amount must be a positive number")

    project_id = transaction_data.get('project_id')
    if project_id and not get_project(project_id):
        raise ValueError(f"Project with ID {project_id} not found. Cannot add transaction.")

    new_transaction = FinancialTransaction(
        type=transaction_type,
        description=transaction_data.get('description'),
        amount=amount,
        project_id=project_id,
        transaction_date=transaction_data.get('transaction_date') # Model handles default/conversion
    )
    
    all_transactions_data = load_data('transactions')
    all_transactions_data.append(new_transaction.to_dict())
    save_data('transactions', all_transactions_data)
    
    return new_transaction.to_dict()

def get_project_finances(project_id):
    """
    Retrieves all financial transactions for a specific project.
    """
    all_transactions_data = load_data('transactions')
    project_transactions = [
        t for t in all_transactions_data if t.get('project_id') == project_id
    ]
    return project_transactions

def get_overall_financial_summary():
    """
    Calculates and returns a summary of all financial transactions.
    """
    all_transactions_data = load_data('transactions')
    total_income = 0.0
    total_expenses = 0.0
    
    for t_data in all_transactions_data:
        if t_data.get('type') == "Income":
            total_income += t_data.get('amount', 0)
        elif t_data.get('type') == "Expense":
            total_expenses += t_data.get('amount', 0)
            
    net_profit_loss = total_income - total_expenses
    
    return {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_profit_loss': net_profit_loss
    }
