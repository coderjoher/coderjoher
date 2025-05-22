import unittest
import os
import json
from datetime import datetime, date # Added date for project creation
from unittest.mock import patch, mock_open

from crm.notes.models import Note
from crm.notes.actions import (
    add_note,
    get_notes_for_item,
    list_all_notes,
    ALLOWED_LINKED_TYPES
)
from crm.database import DATA_DIR, get_file_path, save_data, load_data

# Import actions for creating dummy entities for linking
from crm.clients.actions import add_client as add_client_action
from crm.projects.actions import add_project as add_project_action
from crm.employees.actions import add_employee as add_employee_action


class TestNoteActions(unittest.TestCase):

    # Helper methods to create dummy entities
    def _add_dummy_client(self, suffix=""):
        data = {'name': f'Note Client {suffix}', 'email': f'note.client{suffix}@example.com', 'contact_person':'CP', 'phone_number':'1', 'address':'Addr'}
        client = add_client_action(data)
        self.assertIsNotNone(client, f"Failed to create dummy client with suffix {suffix}")
        return client['client_id']

    def _add_dummy_project(self, client_id, suffix=""):
        # Projects need a valid client_id first
        data = {'project_name': f'Note Project {suffix}', 'client_id': client_id, 'description': 'Desc', 'start_date': date(2024,1,1)}
        project = add_project_action(data)
        self.assertIsNotNone(project, f"Failed to create dummy project with suffix {suffix}")
        return project['project_id']

    def _add_dummy_employee(self, suffix=""):
        data = {'full_name': f'Note Employee {suffix}', 'email': f'note.emp{suffix}@example.com', 'phone_number': '2', 'role': 'Tester'}
        employee = add_employee_action(data)
        self.assertIsNotNone(employee, f"Failed to create dummy employee with suffix {suffix}")
        return employee['employee_id']

    def setUp(self):
        self.notes_file_path = get_file_path('notes')
        if os.path.exists(self.notes_file_path):
            os.remove(self.notes_file_path)
        save_data('notes', [])
        
        # Clean up other entity files that might have been created by helpers
        for entity_type in ['clients', 'projects', 'employees']:
            path = get_file_path(entity_type)
            if os.path.exists(path):
                os.remove(path)
            save_data(entity_type, []) # Ensure they are empty for a clean test run


    def tearDown(self):
        if os.path.exists(self.notes_file_path):
            os.remove(self.notes_file_path)
        
        for entity_type in ['clients', 'projects', 'employees']:
            path = get_file_path(entity_type)
            if os.path.exists(path):
                os.remove(path)

    def test_note_model_creation_and_to_dict(self):
        valid_client_id = self._add_dummy_client(suffix="_model_client")
        valid_employee_id = self._add_dummy_employee(suffix="_model_emp")
        
        before_creation = datetime.now()
        note = Note(
            content="Test content",
            linked_to_type="Client",
            linked_to_id=valid_client_id,
            created_by_employee_id=valid_employee_id
        )
        after_creation = datetime.now()
        
        self.assertIsNotNone(note.note_id)
        self.assertEqual(note.content, "Test content")
        self.assertEqual(note.linked_to_type, "Client")
        self.assertEqual(note.linked_to_id, valid_client_id)
        self.assertEqual(note.created_by_employee_id, valid_employee_id)
        self.assertTrue(before_creation <= note.created_at <= after_creation)
        
        note_dict = note.to_dict()
        self.assertEqual(note_dict['note_id'], note.note_id)
        self.assertEqual(note_dict['content'], "Test content")
        self.assertEqual(note_dict['created_at'], note.created_at.isoformat())


    def test_add_note_valid_links(self):
        client1 = self._add_dummy_client(suffix="_cl1")
        emp1 = self._add_dummy_employee(suffix="_emp1_creator")
        emp2_linked = self._add_dummy_employee(suffix="_emp2_linked")
        proj_client = self._add_dummy_client(suffix="_proj_cl")
        proj1 = self._add_dummy_project(proj_client, suffix="_proj1")

        # Note linked to Client
        client_note_data = {
            'content': 'Client discussion.', 'linked_to_type': 'Client',
            'linked_to_id': client1, 'created_by_employee_id': emp1
        }
        added_client_note = add_note(client_note_data)
        self.assertEqual(added_client_note['linked_to_id'], client1)
        self.assertEqual(added_client_note['created_by_employee_id'], emp1)

        # Note linked to Project
        project_note_data = {
            'content': 'Project update.', 'linked_to_type': 'Project',
            'linked_to_id': proj1, 'created_by_employee_id': emp1
        }
        added_project_note = add_note(project_note_data)
        self.assertEqual(added_project_note['linked_to_id'], proj1)

        # Note linked to Employee
        employee_note_data = {
            'content': 'Employee feedback.', 'linked_to_type': 'Employee',
            'linked_to_id': emp2_linked, 'created_by_employee_id': emp1
        }
        added_employee_note = add_note(employee_note_data)
        self.assertEqual(added_employee_note['linked_to_id'], emp2_linked)

        # General note (no specific link ID, no creator)
        general_note_data = {'content': 'General info.', 'linked_to_type': 'General'}
        added_general_note = add_note(general_note_data)
        self.assertEqual(added_general_note['linked_to_type'], 'General')
        self.assertIsNone(added_general_note['linked_to_id'])
        
        loaded_notes = load_data('notes')
        self.assertEqual(len(loaded_notes), 4)

    def test_add_note_invalid_inputs_and_links(self):
        # Test invalid linked_to_type
        with self.assertRaisesRegex(ValueError, "Invalid linked_to_type: InvalidType. Allowed types are:"):
            add_note({'content': 'Test', 'linked_to_type': 'InvalidType'})

        # Test missing linked_to_id when not "General"
        with self.assertRaisesRegex(ValueError, "linked_to_id is required when linked_to_type is 'Client'."):
            add_note({'content': 'Test', 'linked_to_type': 'Client'}) # No ID
            
        # Test empty content
        with self.assertRaisesRegex(ValueError, "Note content cannot be empty."):
            add_note({'content': '', 'linked_to_type': 'General'})

        # Test adding note with non-existent linked_to_id
        fake_client_id = "client_id_fake_404"
        with self.assertRaisesRegex(ValueError, f"Client with ID {fake_client_id} not found. Cannot add note."):
            add_note({'content': 'Test', 'linked_to_type': 'Client', 'linked_to_id': fake_client_id})

        fake_project_id = "project_id_fake_404"
        with self.assertRaisesRegex(ValueError, f"Project with ID {fake_project_id} not found. Cannot add note."):
            add_note({'content': 'Test', 'linked_to_type': 'Project', 'linked_to_id': fake_project_id})
        
        fake_employee_id_link = "employee_id_link_fake_404"
        with self.assertRaisesRegex(ValueError, f"Employee with ID {fake_employee_id_link} not found. Cannot add note."):
            add_note({'content': 'Test', 'linked_to_type': 'Employee', 'linked_to_id': fake_employee_id_link})

        # Test adding note with non-existent created_by_employee_id
        valid_client_for_creator_test = self._add_dummy_client(suffix="_creator_test")
        fake_creator_id = "creator_id_fake_404"
        note_data_fake_creator = {
            'content': 'Note with fake creator', 'linked_to_type': 'Client',
            'linked_to_id': valid_client_for_creator_test, 'created_by_employee_id': fake_creator_id
        }
        with self.assertRaises(ValueError) as context:
            add_note(note_data_fake_creator)
        self.assertEqual(str(context.exception), f"Employee (creator) with ID {fake_creator_id} not found. Cannot add note.")


    def test_get_notes_for_item(self):
        client_x_id = self._add_dummy_client(suffix="_X_get_notes")
        project_y_client_id = self._add_dummy_client(suffix="_Y_client_get_notes") # Client for project Y
        project_y_id = self._add_dummy_project(project_y_client_id, suffix="_Y_get_notes")
        employee_z_id = self._add_dummy_employee(suffix="_Z_get_notes")

        add_note({'content': 'Note A for Client X', 'linked_to_type': 'Client', 'linked_to_id': client_x_id})
        add_note({'content': 'Note B for Project Y', 'linked_to_type': 'Project', 'linked_to_id': project_y_id})
        add_note({'content': 'Note C for Client X', 'linked_to_type': 'Client', 'linked_to_id': client_x_id})
        add_note({'content': 'Note D (General)', 'linked_to_type': 'General'})
        add_note({'content': 'Note E for Employee Z', 'linked_to_type': 'Employee', 'linked_to_id': employee_z_id})

        client_x_notes = get_notes_for_item('Client', client_x_id)
        self.assertEqual(len(client_x_notes), 2)
        self.assertTrue(any(n['content'] == 'Note A for Client X' for n in client_x_notes))
        self.assertTrue(any(n['content'] == 'Note C for Client X' for n in client_x_notes))

        project_y_notes = get_notes_for_item('Project', project_y_id)
        self.assertEqual(len(project_y_notes), 1)
        self.assertEqual(project_y_notes[0]['content'], 'Note B for Project Y')
        
        employee_z_notes = get_notes_for_item('Employee', employee_z_id)
        self.assertEqual(len(employee_z_notes), 1)
        self.assertEqual(employee_z_notes[0]['content'], 'Note E for Employee Z')

        non_existent_client_notes = get_notes_for_item('Client', 'NonExistent404')
        self.assertEqual(len(non_existent_client_notes), 0)
        
        general_notes_by_item = get_notes_for_item('General', None) 
        self.assertEqual(len(general_notes_by_item), 0, "get_notes_for_item should not fetch General notes by ID this way")


    def test_list_all_notes(self):
        self.assertEqual(list_all_notes(), []) # Test with no notes

        client1_id_list = self._add_dummy_client(suffix="_list_all_c1")
        project_client_id_list = self._add_dummy_client(suffix="_list_all_pc1") # Client for project
        project1_id_list = self._add_dummy_project(project_client_id_list, suffix="_list_all_p1")

        add_note({'content': 'Note 1', 'linked_to_type': 'Client', 'linked_to_id': client1_id_list})
        add_note({'content': 'Note 2', 'linked_to_type': 'Project', 'linked_to_id': project1_id_list})
        add_note({'content': 'Note 3', 'linked_to_type': 'General'})

        all_notes = list_all_notes()
        self.assertEqual(len(all_notes), 3)
        contents = [n['content'] for n in all_notes]
        self.assertIn('Note 1', contents)
        self.assertIn('Note 2', contents)
        self.assertIn('Note 3', contents)

if __name__ == '__main__':
    unittest.main()
