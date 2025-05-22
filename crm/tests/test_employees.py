import unittest
import os
import json
from datetime import date, timedelta
from unittest.mock import patch, mock_open

from crm.employees.models import Employee
from crm.employees.actions import (
    add_employee, 
    get_employee, 
    list_employees, 
    update_employee, # Added import for update_employee
    assign_project_to_employee
)
from crm.database import DATA_DIR, get_file_path, save_data, load_data

# Dummy project ID for testing assignments - will be replaced by actual project creation
# DUMMY_PROJECT_ID_1 = "project_uuid_abc" # No longer used directly
# DUMMY_PROJECT_ID_2 = "project_uuid_xyz" # No longer used directly

# Import project actions for creating dummy projects
from crm.projects.actions import add_project as add_project_action
from crm.clients.actions import add_client as add_client_action # For project's client

class TestEmployeeActions(unittest.TestCase):

    sample_client_data_for_employee_tests = {
        'name': 'Test Client for EmployeeTests', 'email': 'client.emp@example.com',
        'contact_person': 'Emp Linker', 'phone_number': '123', 'address': 'Addr'
    }
    sample_project_data_for_employee_tests = {
        'project_name': 'Test Project for Employee Assignment', 
        'description': 'A test project.',
        'start_date': date(2024, 1, 1)
        # client_id will be set dynamically
    }

    def _add_dummy_client_for_project(self, email_suffix=""):
        client_data = self.sample_client_data_for_employee_tests.copy()
        client_data['email'] = f"client.emp{email_suffix}@example.com"
        client = add_client_action(client_data)
        self.assertIsNotNone(client, "Failed to create dummy client for project in employee tests")
        return client['client_id']

    def _add_dummy_project(self, client_id, project_name_suffix=""):
        project_data = self.sample_project_data_for_employee_tests.copy()
        project_data['client_id'] = client_id
        project_data['project_name'] = f"Test Project {project_name_suffix}"
        project = add_project_action(project_data)
        self.assertIsNotNone(project, "Failed to create dummy project for employee tests")
        return project['project_id']

    def _add_dummy_employee(self, email_suffix=""):
        emp_data = {
            'full_name': f'Dummy Employee {email_suffix}',
            'email': f'dummy.emp{email_suffix}@example.com',
            'phone_number': '123456789',
            'role': 'Tester'
        }
        employee = add_employee(emp_data)
        self.assertIsNotNone(employee, "Failed to create dummy employee")
        return employee['employee_id']

    def setUp(self):
        # Ensure a clean state for each test
        self.employees_file_path = get_file_path('employees')
        if os.path.exists(self.employees_file_path):
            os.remove(self.employees_file_path)
        save_data('employees', []) # Create an empty employees file

    def tearDown(self):
        # Clean up
        if os.path.exists(self.employees_file_path):
            os.remove(self.employees_file_path)

    def test_employee_model_date_handling(self):
        today = date.today()
        emp1 = Employee("John Test", "john@test.com", "123", "Tester", hire_date=today)
        self.assertEqual(emp1.hire_date, today)
        
        emp2 = Employee("Jane Test", "jane@test.com", "456", "Tester", hire_date=today.isoformat())
        self.assertEqual(emp2.hire_date, today)

        emp3 = Employee("Default Date", "default@test.com", "789", "Tester") # Relies on default
        self.assertEqual(emp3.hire_date, today)
        
        emp4_dict = emp1.to_dict()
        self.assertEqual(emp4_dict['hire_date'], today.isoformat())

    def test_add_employee(self):
        hire_date_obj = date(2022, 1, 1)
        employee_data_1 = {
            'full_name': 'Alice Wonderland', 
            'email': 'alice@example.com',
            'phone_number': '1112223333', 
            'role': 'Developer',
            'hire_date': hire_date_obj # Pass as date object
        }
        added_emp_1 = add_employee(employee_data_1)
        
        self.assertIsNotNone(added_emp_1)
        self.assertEqual(added_emp_1['full_name'], employee_data_1['full_name'])
        self.assertEqual(added_emp_1['hire_date'], hire_date_obj.isoformat())
        self.assertIn('employee_id', added_emp_1)
        
        employee_data_2 = {
            'full_name': 'Bob The Builder', 
            'email': 'bob@example.com',
            'phone_number': '4445556666', 
            'role': 'Manager',
            # No hire_date, should default to today
        }
        added_emp_2 = add_employee(employee_data_2)
        self.assertEqual(added_emp_2['hire_date'], date.today().isoformat())
        
        loaded_employees = load_data('employees')
        self.assertEqual(len(loaded_employees), 2)
        self.assertEqual(loaded_employees[0]['full_name'], employee_data_1['full_name'])

    def test_get_employee(self):
        employee_data = {
            'full_name': 'Charlie Brown', 
            'email': 'charlie@example.com',
            'phone_number': '7778889999', 
            'role': 'Designer'
        }
        added_employee = add_employee(employee_data)
        
        retrieved_employee = get_employee(added_employee['employee_id'])
        self.assertIsNotNone(retrieved_employee)
        self.assertEqual(retrieved_employee['full_name'], employee_data['full_name'])
        
        non_existent_employee = get_employee('non_existent_id')
        self.assertIsNone(non_existent_employee)

    def test_list_employees(self):
        self.assertEqual(list_employees(), []) # Test on an empty list
        
        emp_data1 = {'full_name': 'Employee One', 'email': 'one@co.com', 'phone_number': '1', 'role': 'R1'}
        emp_data2 = {'full_name': 'Employee Two', 'email': 'two@co.com', 'phone_number': '2', 'role': 'R2'}
        add_employee(emp_data1)
        add_employee(emp_data2)
        
        employees = list_employees()
        self.assertEqual(len(employees), 2)
        self.assertTrue(any(e['full_name'] == emp_data1['full_name'] for e in employees))
        self.assertTrue(any(e['full_name'] == emp_data2['full_name'] for e in employees))

    def test_assign_project_to_employee(self):
        employee_data = {
            'full_name': 'Diana Prince', 
            'email': 'diana@example.com',
            'phone_number': '1231231234', 
            'role': 'Hero'
        }
        added_employee = add_employee(employee_data) # This uses the module's add_employee
        emp_id = added_employee['employee_id']

        # Setup a dummy client and project for valid assignment
        dummy_client_id = self._add_dummy_client_for_project(email_suffix="_assign_proj")
        valid_project_id_1 = self._add_dummy_project(dummy_client_id, project_name_suffix="P1_Assign")
        valid_project_id_2 = self._add_dummy_project(dummy_client_id, project_name_suffix="P2_Assign")


        # Assign first project
        updated_emp = assign_project_to_employee(emp_id, valid_project_id_1)
        self.assertIsNotNone(updated_emp)
        self.assertIn(valid_project_id_1, updated_emp['assigned_project_ids'])
        self.assertEqual(len(updated_emp['assigned_project_ids']), 1)

        # Assign second project
        updated_emp = assign_project_to_employee(emp_id, valid_project_id_2)
        self.assertIn(valid_project_id_1, updated_emp['assigned_project_ids'])
        self.assertIn(valid_project_id_2, updated_emp['assigned_project_ids'])
        self.assertEqual(len(updated_emp['assigned_project_ids']), 2)

        # Try assigning the first project again (should not duplicate)
        updated_emp = assign_project_to_employee(emp_id, valid_project_id_1)
        self.assertEqual(len(updated_emp['assigned_project_ids']), 2)
        
        # Test with non-existent employee
        non_existent_assign = assign_project_to_employee('non_existent_emp_id', valid_project_id_1)
        self.assertIsNone(non_existent_assign)
        
        # Test with non-existent project
        fake_project_id = "project_does_not_exist_404"
        with self.assertRaisesRegex(ValueError, f"Project with ID {fake_project_id} not found. Cannot assign to employee."):
            assign_project_to_employee(emp_id, fake_project_id)
        
        # Verify data is saved correctly after valid assignments
        retrieved_employee = get_employee(emp_id)
        self.assertEqual(len(retrieved_employee['assigned_project_ids']), 2)
        self.assertIn(valid_project_id_1, retrieved_employee['assigned_project_ids'])
        self.assertIn(valid_project_id_2, retrieved_employee['assigned_project_ids'])


    def test_update_employee(self):
        employee_data = {
            'full_name': 'Clark Kent', 
            'email': 'clark@example.com',
            'phone_number': '5555555555', 
            'role': 'Reporter',
            'hire_date': date(2000,1,1)
        }
        added_employee = add_employee(employee_data)
        emp_id = added_employee['employee_id']
        
        update_data = {'role': 'Superman', 'phone_number': '0000000000'}
        updated_emp = update_employee(emp_id, update_data)
        
        self.assertIsNotNone(updated_emp)
        self.assertEqual(updated_emp['role'], update_data['role'])
        self.assertEqual(updated_emp['phone_number'], update_data['phone_number'])
        # Ensure hire_date is not changed if not in update_data
        self.assertEqual(updated_emp['hire_date'], date(2000,1,1).isoformat()) 
        
        retrieved_employee = get_employee(emp_id)
        self.assertEqual(retrieved_employee['role'], update_data['role'])
        
        # Test updating hire_date
        new_hire_date = date(2001,2,2)
        update_data_with_date = {'hire_date': new_hire_date}
        updated_emp_with_date = update_employee(emp_id, update_data_with_date)
        self.assertEqual(updated_emp_with_date['hire_date'], new_hire_date.isoformat())

        non_existent_update = update_employee('non_existent_id', {'role': 'Ghost'})
        self.assertIsNone(non_existent_update)

if __name__ == '__main__':
    unittest.main()
