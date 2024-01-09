from pydantic.dataclasses import dataclass
from dataclasses import asdict
from typing import List

@dataclass
class Client:
    id: int
    first_name: str
    last_name: str
    age: int
    address: str

    def to_dict(self):
        return asdict(self)
    
@dataclass
class Node:
    id: int
    client_id:int
    node_id: int
    node_type: str
    
    def to_dict(self):
        return asdict(self)
    
@dataclass
class Relationship:
    id: int
    party1:int
    party2: int
    reltype: str
    
    def to_dict(self):
        return asdict(self)



# if __name__ == "__main__":
#     test_client= {
#         'id': 1,
#         'first_name': "John",
#         'last_name': "Doe",
#         'age': "29",
#         'address': "123 Market St."
#     }
#     a = Client(**test_client)
#     b = a.to_dict()
#     print(b)
    
