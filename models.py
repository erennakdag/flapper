from pydantic import BaseModel
from typing import Dict, List, Optional

class Like(BaseModel):
    user_name_liking: str
    user_name_liked: str
    flap_id: str

class Flap(BaseModel):
    likes: Optional[List[str]] = [] # user_names are stored
    dislikes: Optional[List[str]] = [] # user_names are stored
    body: str
    date: Optional[int] = None
    subflaps = {}

class User(BaseModel):
    user_name: str
    name: str
    profile_img: Optional[str] = None
    bio: Optional[str] = ""
    following: Optional[List[str]] = [] # user_names are stored
    followers: Optional[List[str]] = [] # user_names are stored
    flaps: Optional[Dict[str, dict]] = {}
    
    def dict(self):
        """ overrides the dict method in BaseModel 
        so that the field 'user_name' is changed as '_id' for MongoDB
        Returns:
            dict: the dict representation of the model
        """
        d = super().dict()
        d['_id'] = d['user_name']
        del d['user_name']
        return d
    