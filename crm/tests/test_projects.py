import unittest
import os
import json
from datetime import date, timedelta
from unittest.mock import patch, mock_open

from crm.projects.models import Project
from crm.projects.actions import add_project, get_project, list_projects, update_project
from crm.database import DATA_DIR, get_file_path, save_data, load_data

# Dummy client ID for testing project linkage
DUMMY_CLIENT_ID_1 = "client_uuid_1"
DUMMY_CLIENT_ID_2 = "client_uuid_2"

class TestProjectActions(unittest.TestCase):

    def setUp(self):
        # Ensure a clean state for each test
        self.projects_file_path = get_file_path('projects')
        if os.path.exists(self.projects_file_path):
            os.remove(self.projects_file_path)
        save_data('projects', []) # Create an empty projects file

        # You might also want to clear/mock clients.json if your project tests depend on client existence
        # For this subtask, we are only passing client_id as a string.
        self.clients_file_path = get_file_path('clients')
        if os.path.exists(self.clients_file_path):
             os.remove(self.clients_file_path)
        save_data('clients', [])


    def tearDown(self):
        # Clean up project files
        if os.path.exists(self.projects_file_path):
            os.remove(self.projects_file_path)
        # Clean up client files (if any were created for more complex tests)
        if os.path.exists(self.clients_file_path):
            os.remove(self.clients_file_path)

    def test_project_model_date_handling(self):
        # Test that Project model handles string and date objects for start_date and end_date
        today = date.today()
        project1 = Project("Test 1", DUMMY_CLIENT_ID_1, "Desc 1", today, today + timedelta(days=10))
        self.assertEqual(project1.start_date, today)
        
        project2 = Project("Test 2", DUMMY_CLIENT_ID_1, "Desc 2", today.isoformat(), (today + timedelta(days=10)).isoformat())
        self.assertEqual(project2.start_date, today)
        self.assertEqual(project2.end_date, today + timedelta(days=10))

        project3 = Project("Test 3", DUMMY_CLIENT_ID_1, "Desc 3", today, None)
        self.assertIsNone(project3.end_date)

        project4_dict = project2.to_dict()
        self.assertEqual(project4_dict['start_date'], today.isoformat())

    # Dummy client data for setting up client for project tests
    sample_client_data_for_project_tests = { # Renamed to be more specific
        'name': 'Test Client for Project Module', 
        'contact_person': 'Project Linker',
        'email': 'project.linker@example.com', 
        'phone_number': '1234509876', 
        'address': '789 Link St',
        'company_name': 'Link Inc.'
    }

    def _add_dummy_client(self, email_suffix=""):
        from crm.clients.actions import add_client as add_client_action
        client_data = self.sample_client_data_for_project_tests.copy()
        client_data['email'] = f"project.linker{email_suffix}@example.com" # Ensure unique email if called multiple times
        client = add_client_action(client_data)
        self.assertIsNotNone(client, "Failed to create dummy client for project tests")
        return client['client_id']


    def test_add_project(self):
        valid_client_id = self._add_dummy_client(email_suffix="_add_project")
        start_date_obj = date(2023, 1, 1)
        end_date_obj = date(2023, 12, 31)
        project_data = {
            'project_name': 'New Website', 
            'client_id': valid_client_id, # Use the valid client_id
            'description': 'A brand new website for a client.',
            'start_date': start_date_obj, # Pass as date object
            'end_date': end_date_obj.isoformat(), # Pass as ISO string
            'status': 'Planning'
        }
        added_project = add_project(project_data)
        
        self.assertIsNotNone(added_project)
        self.assertEqual(added_project['project_name'], project_data['project_name'])
        self.assertEqual(added_project['client_id'], valid_client_id)
        self.assertEqual(added_project['start_date'], start_date_obj.isoformat())
        self.assertEqual(added_project['end_date'], end_date_obj.isoformat())
        self.assertIn('project_id', added_project)
        
        loaded_projects = load_data('projects')
        self.assertEqual(len(loaded_projects), 1)
        self.assertEqual(loaded_projects[0]['project_name'], project_data['project_name'])

    def test_add_project_invalid_client_id(self):
        start_date_obj = date(2023, 1, 1)
        project_data_invalid_client = {
            'project_name': 'Website for Ghost', 
            'client_id': 'non_existent_client_id_12345', # Invalid client_id
            'description': 'A website for a non-existent client.',
            'start_date': start_date_obj,
            'status': 'Planning'
        }
        with self.assertRaisesRegex(ValueError, "Client with ID non_existent_client_id_12345 not found."):
            add_project(project_data_invalid_client)
        
        # Ensure no project was added
        loaded_projects = load_data('projects')
        self.assertEqual(len(loaded_projects), 0)


    def test_get_project(self):
        valid_client_id = self._add_dummy_client(email_suffix="_get_project")
        project_data = {
            'project_name': 'API Development', 
            'client_id': valid_client_id,
            'description': 'Develop a new REST API.',
            'start_date': date.today(),
            'status': 'In Progress'
        }
        added_project = add_project(project_data)
        
        retrieved_project = get_project(added_project['project_id'])
        self.assertIsNotNone(retrieved_project)
        self.assertEqual(retrieved_project['project_name'], project_data['project_name'])
        
        non_existent_project = get_project('non_existent_id')
        self.assertIsNone(non_existent_project)

    def test_list_projects(self):
        valid_client_id_1 = self._add_dummy_client(email_suffix="_list_projects1")
        valid_client_id_2 = self._add_dummy_client(email_suffix="_list_projects2")

        # Test on an empty project list
        self.assertEqual(list_projects(), [])
        
        proj1_data = {
            'project_name': 'Project Alpha', 'client_id': valid_client_id_1, 
            'description': 'Alpha desc', 'start_date': date(2023, 5, 1)
        }
        proj2_data = {
            'project_name': 'Project Beta', 'client_id': valid_client_id_2, 
            'description': 'Beta desc', 'start_date': date(2023, 6, 1)
        }
        proj3_data = {
            'project_name': 'Project Gamma', 'client_id': valid_client_id_1, 
            'description': 'Gamma desc', 'start_date': date(2023, 7, 1)
        }
        add_project(proj1_data)
        add_project(proj2_data)
        add_project(proj3_data)
        
        all_projs = list_projects()
        self.assertEqual(len(all_projs), 3)
        
        client1_projs = list_projects(client_id=valid_client_id_1) 
        self.assertEqual(len(client1_projs), 2)
        self.assertTrue(any(p['project_name'] == 'Project Alpha' for p in client1_projs))
        self.assertTrue(any(p['project_name'] == 'Project Gamma' for p in client1_projs))
        
        client2_projs = list_projects(client_id=valid_client_id_2) 
        self.assertEqual(len(client2_projs), 1)
        self.assertEqual(client2_projs[0]['project_name'], 'Project Beta')

    def test_update_project(self):
        valid_client_id_1 = self._add_dummy_client(email_suffix="_update_project1")
        valid_client_id_2 = self._add_dummy_client(email_suffix="_update_project2")

        project_data = {
            'project_name': 'Initial Project Name', 
            'client_id': valid_client_id_1,
            'description': 'Initial description.',
            'start_date': date(2024,1,1),
            'status': 'Planning'
        }
        added_project = add_project(project_data)
        project_id = added_project['project_id']
        
        update_data = {'project_name': 'Updated Project Name', 'status': 'Completed', 'end_date': date(2024,6,30)}
        updated_project = update_project(project_id, update_data)
        
        self.assertIsNotNone(updated_project)
        self.assertEqual(updated_project['project_name'], update_data['project_name'])
        self.assertEqual(updated_project['status'], update_data['status'])
        self.assertEqual(updated_project['end_date'], update_data['end_date'].isoformat())
        
        retrieved_project = get_project(project_id)
        self.assertEqual(retrieved_project['project_name'], update_data['project_name'])
        self.assertEqual(retrieved_project['status'], update_data['status'])
        
        non_existent_update = update_project('non_existent_id_proj', {'project_name': 'Ghost Project'})
        self.assertIsNone(non_existent_update)

        # Test updating client_id to a valid one
        update_client_id_data = {'client_id': valid_client_id_2}
        updated_project_client = update_project(project_id, update_client_id_data)
        self.assertIsNotNone(updated_project_client)
        self.assertEqual(updated_project_client['client_id'], valid_client_id_2)

        # Test updating client_id to a non-existent one
        invalid_client_id_for_update = 'fake_client_id_789_update'
        update_invalid_client_id_data = {'client_id': invalid_client_id_for_update}
        with self.assertRaisesRegex(ValueError, f"Client with ID {invalid_client_id_for_update} not found. Cannot update project's client ID."):
            update_project(project_id, update_invalid_client_id_data)
        
        # Ensure the client_id was not actually changed after the error
        current_project_state = get_project(project_id)
        self.assertEqual(current_project_state['client_id'], valid_client_id_2) # Should still be the last valid one


if __name__ == '__main__':
    unittest.main()
