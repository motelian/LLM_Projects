from faker import Faker
import pandas as pd
import numpy as np
from datamodel import Client, Node, Relationship

# Initialize Faker
fake = Faker()

# Define number of couples and children
num_couples = 4
children_distribution = [3, 2, 3, 2]  # Total 10 children, Gaussian-like distribution

# Define dataframes
client_df = pd.DataFrame()
node_df = pd.DataFrame()
rel_df = pd.DataFrame()

# Client ID, Mapping ID, and Relationship ID counters
client_id = 1
mapping_id = 1
rel_id = 1

# Generate data
for couple in range(num_couples):
    # Generate couple data
    last_name = fake.last_name()
    address = fake.address().replace("\n", ", ")
    
    for spouse in range(2):

        adult_info = {
            'id': client_id,
            'first_name': fake.first_name(),
            'last_name': last_name,
            'address': address,
            'age': np.random.randint(25, 50)
        }
        adult_client = Client(**adult_info)
        client_df = client_df.append(adult_client.to_dict(), ignore_index=True)
        
        node_info = {
            'id': mapping_id,
            'client_id': client_id,
            'node_id': couple + 1,  # Assign same NodeID to spouses
            'node_type': "Family"
        }
        print(node_info)
        node = Node(**node_info)
        node_df = node_df.append(node.to_dict(), ignore_index=True)

        client_id += 1
        mapping_id += 1

    # Add spouse relationship
    rel_info = {
        'id': rel_id,
        'party1': client_id - 2,
        'party2': client_id - 1,
        'reltype': 'Spouse'
    }
    rel = Relationship(**rel_info)
    rel_df = rel_df.append(rel.to_dict(), ignore_index=True)

    rel_id += 1

    # Generate children data
    for child in range(children_distribution[couple]):
        child_info = {
            'id': client_id,
            'first_name': fake.first_name(),
            'last_name': last_name,
            'address': address,
            'age': np.random.randint(1, 18) 
        }
        child_client = Client(**child_info)
        client_df = client_df.append(child_client.to_dict(), ignore_index=True)

        node_info = {
            'id': mapping_id,
            'client_id': client_id,
            'node_id': couple + 1,  # Assign same NodeID to spouses
            'node_type': 'Family'
        }
        child_node = Node(**node_info)
        node_df = node_df.append(child_node.to_dict(), ignore_index=True)

        # Add child-parent relationship for both parents
        for parent_id in range(client_id - 2, client_id - 1):
            rel_info = {
                'id': rel_id,
                'party1': client_id - 1,
                'party2': client_id,
                'reltype': 'Minor Child'
            }
            rel = Relationship(**rel_info)
            rel_df = rel_df.append(rel.to_dict(), ignore_index=True)
            
            rel_id += 1

        client_id += 1
        mapping_id += 1

# Show the generated data
client_df.to_csv('clients.csv', index=False)
node_df.to_csv('client_node_mapping.csv', index=False)
rel_df.to_csv('relationship.csv', index=False)
print("Success!")






# Function to generate spouse data using Faker
# def spouses(num_couples):
#     spouses_data = []
#     for i in range(num_couples):
#         last_name = fake.last_name()
#         address = fake.address().split("\n")[0]  # Simplify the address to one line
#         spouses_data.append({'ClientID': f'Client{2*i+1}', 'FirstName': fake.first_name(), 
#                              'LastName': last_name, 'Address': address, 'RelationshipType': 'Spouse'})
#         spouses_data.append({'ClientID': f'Client{2*i+2}', 'FirstName': fake.first_name(), 
#                              'LastName': last_name, 'Address': address, 'RelationshipType': 'Spouse'})
#     return spouses_data

# # Function to generate children data using Faker
# def generate_children_with_faker(total_children, num_couples, mean, std, spouses_data):
#     np.random.seed(0)  # For reproducibility
#     children_counts = np.random.normal(mean, std, num_couples).astype(int)
#     children_counts = np.clip(children_counts, 1, None)  # Ensure at least one child per couple
#     children_counts = np.round((children_counts / children_counts.sum()) * total_children).astype(int)

#     children_data = []
#     child_id = 2 * num_couples + 1
#     for i in range(num_couples):
#         last_name = spouses_data[2*i]['LastName']
#         address = spouses_data[2*i]['Address']
#         for _ in range(children_counts[i]):
#             children_data.append({'ClientID': f'Client{child_id}', 'FirstName': fake.first_name(),
#                                   'LastName': last_name, 'Address': address, 
#                                   'RelationshipType': 'Minor Child'})
#             child_id += 1

#     return children_data

# # Parameters for data generation
# num_couples = 4
# children_distribution_mean = 2.5
# children_distribution_std = 0.7
# total_children = 10

# # Generate spouse and children data
# spouses_data = generate_spouses_with_faker(num_couples)
# children_data = generate_children_with_faker(total_children, num_couples, children_distribution_mean, children_distribution_std, spouses_data)

# # Combine Data and Convert to DataFrame
# client_data = spouses_data + children_data
# clients_df = pd.DataFrame(client_data)

# # Function to generate client-node mapping
# def generate_client_node_mapping(clients_df):
#     node_mapping = []
#     for i, row in clients_df.iterrows():
#         node_mapping.append({'ClientID': row['ClientID'], 'NodeID': f"Node{row['LastName']}"})
#     return pd.DataFrame(node_mapping)

# # Function to generate relationship node table
# def generate_relationship_node_table(clients_df):
#     relationship_node_data = []
#     for i in range(1, num_couples + 1):
#         relationship_node_data.append({'NodeID': f'NodeFamily{i}', 'RelationshipType': 'Family'})
#     return pd.DataFrame(relationship_node_data)

# # Generate client-node mapping and relationship node tables
# client_node_mapping_df = generate_client_node_mapping(clients_df)
# relationship_node_df = generate_relationship_node_table(clients_df)

# # Displaying the dataframes
# (clients_df, client_node_mapping_df, relationship_node_df)
