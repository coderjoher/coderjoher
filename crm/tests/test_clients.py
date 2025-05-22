import unittest
import os
import json
from datetime import date
from unittest.mock import patch, mock_open

from crm.clients.models import Client
from crm.clients.actions import add_client, get_client, list_clients, update_client
from crm.database import DATA_DIR, get_file_path, save_data, load_data

class TestClientActions(unittest.TestCase):

    def setUp(self):
        # Ensure a clean state for each test
        self.clients_file_path = get_file_path('clients')
        if os.path.exists(self.clients_file_path):
            os.remove(self.clients_file_path)
        # Create an empty clients file
        save_data('clients', [])

    def tearDown(self):
        # Clean up
        if os.path.exists(self.clients_file_path):
            os.remove(self.clients_file_path)

    def test_add_client(self):
        client_data = {
            'name': 'Test Client 1', 
            'contact_person': 'John Doe',
            'email': 'john.doe@example.com', 
            'phone_number': '1234567890', 
            'address': '123 Test St',
            'company_name': 'Test Inc.'
        }
        added_client = add_client(client_data)
        
        self.assertIsNotNone(added_client)
        self.assertEqual(added_client['name'], client_data['name'])
        self.assertIn('client_id', added_client)
        
        loaded_clients = load_data('clients')
        self.assertEqual(len(loaded_clients), 1)
        self.assertEqual(loaded_clients[0]['name'], client_data['name'])

    def test_get_client(self):
        client_data = {
            'name': 'Test Client 2', 
            'contact_person': 'Jane Doe',
            'email': 'jane.doe@example.com', 
            'phone_number': '0987654321', 
            'address': '456 Test Ave',
            'company_name': 'Test Corp.'
        }
        added_client = add_client(client_data)
        
        retrieved_client = get_client(added_client['client_id'])
        self.assertIsNotNone(retrieved_client)
        self.assertEqual(retrieved_client['name'], client_data['name'])
        
        non_existent_client = get_client('non_existent_id')
        self.assertIsNone(non_existent_client)

    def test_list_clients(self):
        # Test on an empty client list
        self.assertEqual(list_clients(), [])
        
        client_data1 = {
            'name': 'Test Client 3', 
            'contact_person': 'Jim Beam',
            'email': 'jim.beam@example.com', 
            'phone_number': '1112223333', 
            'address': '789 Test Rd',
            'company_name': 'Test Ltd.'
        }
        client_data2 = {
            'name': 'Test Client 4', 
            'contact_person': 'Jack Daniels',
            'email': 'jack.daniels@example.com', 
            'phone_number': '4445556666', 
            'address': '101 Test Blvd',
            'company_name': 'Test LLC'
        }
        add_client(client_data1)
        add_client(client_data2)
        
        clients = list_clients()
        self.assertEqual(len(clients), 2)
        self.assertEqual(clients[0]['name'], client_data1['name'])
        self.assertEqual(clients[1]['name'], client_data2['name'])

    def test_update_client(self):
        client_data = {
            'name': 'Test Client 5', 
            'contact_person': 'Johnny Walker',
            'email': 'johnny.walker@example.com', 
            'phone_number': '7778889999', 
            'address': '202 Test Ln',
            'company_name': 'Test Group'
        }
        added_client = add_client(client_data)
        
        update_data = {'name': 'Updated Test Client 5', 'email': 'updated.jw@example.com'}
        updated_client = update_client(added_client['client_id'], update_data)
        
        self.assertIsNotNone(updated_client)
        self.assertEqual(updated_client['name'], update_data['name'])
        self.assertEqual(updated_client['email'], update_data['email'])
        
        retrieved_client = get_client(added_client['client_id'])
        self.assertEqual(retrieved_client['name'], update_data['name'])
        
        non_existent_update = update_client('non_existent_id', {'name': 'Ghost'})
        self.assertIsNone(non_existent_update)

if __name__ == '__main__':
    unittest.main()
