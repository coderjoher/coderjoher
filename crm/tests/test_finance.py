import unittest
import os
import json
from datetime import date, timedelta
from unittest.mock import patch, mock_open

from crm.finance.models import FinancialTransaction
from crm.finance.actions import (
    add_transaction,
    get_project_finances,
    get_overall_financial_summary
)
from crm.database import DATA_DIR, get_file_path, save_data, load_data

# Import project and client actions for creating dummy projects/clients
from crm.projects.actions import add_project as add_project_action
from crm.clients.actions import add_client as add_client_action

# DUMMY_PROJECT_ID_FIN_1 = "project_fin_aaa" # No longer used directly
# DUMMY_PROJECT_ID_FIN_2 = "project_fin_bbb" # No longer used directly

class TestFinanceActions(unittest.TestCase):

    sample_client_data_for_finance_tests = {
        'name': 'Test Client for FinanceTests', 'email': 'client.fin@example.com',
        'contact_person': 'Fin Linker', 'phone_number': '456', 'address': 'AddrFin'
    }
    sample_project_data_for_finance_tests = {
        'project_name': 'Test Project for Finance Transactions', 
        'description': 'A test project for finance.',
        'start_date': date(2024, 1, 1)
        # client_id will be set dynamically
    }

    def _add_dummy_client_for_project(self, email_suffix=""):
        client_data = self.sample_client_data_for_finance_tests.copy()
        client_data['email'] = f"client.fin{email_suffix}@example.com"
        client = add_client_action(client_data)
        self.assertIsNotNone(client, "Failed to create dummy client for finance tests")
        return client['client_id']

    def _add_dummy_project(self, client_id, project_name_suffix=""):
        project_data = self.sample_project_data_for_finance_tests.copy()
        project_data['client_id'] = client_id
        project_data['project_name'] = f"Test Project Fin {project_name_suffix}"
        project = add_project_action(project_data)
        self.assertIsNotNone(project, "Failed to create dummy project for finance tests")
        return project['project_id']

    def setUp(self):
        self.transactions_file_path = get_file_path('transactions')
        if os.path.exists(self.transactions_file_path):
            os.remove(self.transactions_file_path)
        save_data('transactions', [])

    def tearDown(self):
        if os.path.exists(self.transactions_file_path):
            os.remove(self.transactions_file_path)

    def test_transaction_model_date_handling(self):
        today = date.today()
        trans1 = FinancialTransaction("Income", "Test", 100, transaction_date=today)
        self.assertEqual(trans1.transaction_date, today)
        
        trans2 = FinancialTransaction("Expense", "Test", 50, transaction_date=today.isoformat())
        self.assertEqual(trans2.transaction_date, today)

        trans3 = FinancialTransaction("Income", "Default Date", 200) # Relies on default
        self.assertEqual(trans3.transaction_date, today)
        
        trans4_dict = trans1.to_dict()
        self.assertEqual(trans4_dict['transaction_date'], today.isoformat())

    def test_add_transaction(self):
        dummy_client_id = self._add_dummy_client_for_project(email_suffix="_add_trans")
        valid_project_id = self._add_dummy_project(dummy_client_id, project_name_suffix="_add_trans")

        # Valid Income
        income_data = {
            'type': 'Income', 'description': 'Client Payment', 
            'amount': 5000.00, 'project_id': valid_project_id,
            'transaction_date': date(2023, 1, 15)
        }
        added_income = add_transaction(income_data)
        self.assertIsNotNone(added_income)
        self.assertEqual(added_income['type'], 'Income')
        self.assertEqual(added_income['amount'], 5000.00)
        self.assertEqual(added_income['transaction_date'], date(2023,1,15).isoformat())
        self.assertEqual(added_income['project_id'], valid_project_id)

        # Valid Expense (default date, no project)
        expense_data = {
            'type': 'Expense', 'description': 'Software License', 
            'amount': 150.00
        }
        added_expense = add_transaction(expense_data)
        self.assertIsNotNone(added_expense)
        self.assertEqual(added_expense['type'], 'Expense')
        self.assertEqual(added_expense['transaction_date'], date.today().isoformat())
        self.assertIsNone(added_expense['project_id'])
        
        loaded_transactions = load_data('transactions')
        self.assertEqual(len(loaded_transactions), 2)

        # Test invalid type
        with self.assertRaises(ValueError, msg="Should raise ValueError for invalid type"):
            add_transaction({'type': 'InvalidType', 'description': 'Test', 'amount': 100})

        # Test invalid amount (negative)
        with self.assertRaises(ValueError, msg="Should raise ValueError for negative amount"):
            add_transaction({'type': 'Income', 'description': 'Test', 'amount': -100})
        
        # Test invalid amount (zero)
        with self.assertRaises(ValueError, msg="Should raise ValueError for zero amount"):
            add_transaction({'type': 'Income', 'description': 'Test', 'amount': 0})

        # Test with non-existent project_id
        invalid_project_id_trans_data = {
            'type': 'Income', 'description': 'Payment for ghost project', 
            'amount': 100.00, 'project_id': 'non_existent_project_fin_id'
        }
        with self.assertRaisesRegex(ValueError, "Project with ID non_existent_project_fin_id not found. Cannot add transaction."):
            add_transaction(invalid_project_id_trans_data)


    def test_get_project_finances(self):
        dummy_client_id = self._add_dummy_client_for_project(email_suffix="_get_fin")
        project_id_1 = self._add_dummy_project(dummy_client_id, project_name_suffix="_P1_get_fin")
        project_id_2 = self._add_dummy_project(dummy_client_id, project_name_suffix="_P2_get_fin")

        add_transaction({'type': 'Income', 'description': 'P1 Income 1', 'amount': 1000, 'project_id': project_id_1})
        add_transaction({'type': 'Expense', 'description': 'P1 Expense 1', 'amount': 200, 'project_id': project_id_1})
        add_transaction({'type': 'Income', 'description': 'P2 Income 1', 'amount': 500, 'project_id': project_id_2})
        add_transaction({'type': 'Expense', 'description': 'General Expense', 'amount': 50}) # No project_id

        project1_finances = get_project_finances(project_id_1)
        self.assertEqual(len(project1_finances), 2)
        self.assertTrue(all(t['project_id'] == project_id_1 for t in project1_finances))
        self.assertTrue(any(t['description'] == 'P1 Income 1' for t in project1_finances))

        project2_finances = get_project_finances(project_id_2)
        self.assertEqual(len(project2_finances), 1)
        self.assertEqual(project2_finances[0]['description'], 'P2 Income 1')
        
        non_existent_project_finances = get_project_finances("non_existent_project")
        self.assertEqual(len(non_existent_project_finances), 0)

    def test_get_overall_financial_summary(self):
        # Test with no transactions
        summary_empty = get_overall_financial_summary()
        self.assertEqual(summary_empty['total_income'], 0)
        self.assertEqual(summary_empty['total_expenses'], 0)
        self.assertEqual(summary_empty['net_profit_loss'], 0)

        dummy_client_id_summary = self._add_dummy_client_for_project(email_suffix="_summary_fin")
        project_id_for_summary = self._add_dummy_project(dummy_client_id_summary, project_name_suffix="_summary")

        add_transaction({'type': 'Income', 'description': 'Income 1', 'amount': 1000})
        add_transaction({'type': 'Income', 'description': 'Income 2', 'amount': 500, 'project_id': project_id_for_summary})
        add_transaction({'type': 'Expense', 'description': 'Expense 1', 'amount': 200})
        add_transaction({'type': 'Expense', 'description': 'Expense 2', 'amount': 150, 'project_id': project_id_for_summary})
        add_transaction({'type': 'Expense', 'description': 'Expense 3', 'amount': 50})

        summary_filled = get_overall_financial_summary()
        self.assertEqual(summary_filled['total_income'], 1500) # 1000 + 500
        self.assertEqual(summary_filled['total_expenses'], 400) # 200 + 150 + 50
        self.assertEqual(summary_filled['net_profit_loss'], 1100) # 1500 - 400

if __name__ == '__main__':
    unittest.main()
