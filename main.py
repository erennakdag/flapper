from fastapi import FastAPI, status
from models import Like, User, Flap
from utils import users, generate_random_id
import datetime

app = FastAPI()

@app.get("/")
def index(user_name: str):
    
    followings = users.find_one({"_id": user_name})["following"]
    flaps = []
    
    for following in followings:
        user = users.find_one({"_id": following})
        user_flaps = user["flaps"]
        flaps.extend([user_flaps[k] for k in user_flaps])
    
    flaps = sorted(flaps, key=lambda x: x["date"], reverse=True)
    
    return {"flaps": flaps}


@app.get("/{user_name}")
def get_user(user_name: str):
    user = users.find_one({"_id": user_name})
    return user or status.HTTP_404_NOT_FOUND


@app.post("/create-profile/")
def create_profile(user: User):
    user = user.dict()
    users.insert_one(user)
    return user


@app.get("/{user_name}/flaps/")
def get_flaps(user_name: str):
    user = users.find_one({"_id": user_name})
    return user["flaps"]


@app.get("/{user_name}/flaps/{flap_id}")
def get_flap_by_id(user_name: str, flap_id: str):
    return get_flaps(user_name)[flap_id]


@app.post("/{user_name}/create-flap/")
def create_flap(user_name: str, flap: Flap):
    flap = flap.dict()
    flap["user_name"] = user_name
    flap_id = generate_random_id()
    flap["flap_id"] = flap_id
    flap["date"] = round(datetime.datetime.now().timestamp() * 1000)
    result = users.update_one({"_id": user_name}, {"$set": {f"flaps.{flap_id}": flap}}).modified_count
    return {"status": "OK" if result else "ERROR", **flap}


@app.post("/like")
def like_flap(like: Like):
    like = like.dict()
    flap_id = like["flap_id"]
    user_name_liking = like["user_name_liking"]
    user_name_liked = like["user_name_liked"]
    
    user_liked = users.find_one({"_id": user_name_liked})
    user_flaps = user_liked["flaps"]
    
    likes = user_flaps[flap_id]["likes"]
    dislikes = user_flaps[flap_id]["dislikes"]
    
    if user_name_liking in likes:
        del user_flaps[flap_id]["likes"][likes.index(user_name_liking)]
    else:
        if user_name_liking in dislikes:
            del user_flaps[flap_id]["dislikes"][dislikes.index(user_name_liking)]
        user_flaps[flap_id]["likes"].append(user_name_liking)
    
    result = users.update_one({"_id": user_name_liked}, {"$set": {"flaps": user_flaps}}).modified_count
    return {"status": "OK" if result else "ERROR"}


@app.post("/dislike")
def dislike_flap(dislike: Like):
    dislike = dislike.dict()
    flap_id = dislike["flap_id"]
    user_name_disliking = dislike["user_name_liking"]
    user_name_disliked = dislike["user_name_liked"]
    
    user_disliked = users.find_one({"_id": user_name_disliked})
    user_flaps = user_disliked["flaps"]
    
    likes = user_flaps[flap_id]["likes"]
    dislikes = user_flaps[flap_id]["dislikes"]
    
    if user_name_disliking in dislikes:
        del user_flaps[flap_id]["dislikes"][dislikes.index(user_name_disliking)]
    else: 
        if user_name_disliking in likes:
            del user_flaps[flap_id]["likes"][likes.index(user_name_disliking)]
        user_flaps[flap_id]["dislikes"].append(user_name_disliking)
        
    result = users.update_one({"_id": dislike["user_name_liked"]}, {"$set": {"flaps": user_flaps}}).modified_count
    return {"status": "OK" if result else "ERROR"}


@app.delete("/delete/{user_name}/{flap_id}/")
def delete_flap(user_name: str, flap_id: str):
    result = users.update_one({"_id": user_name}, {"$unset": {f"flaps.{flap_id}": ""}}).modified_count
    return {"status": "OK" if result else "ERROR"}


@app.delete("/delete/{user_name}/")
def delete_user(user_name: str):
    result = users.delete_one({"_id": user_name}).deleted_count
    return {"status": "OK" if result else "ERROR"}


@app.post("/follow/")
def follow(following_user: str, followed_user: str):
    following = users.update_one({"_id": following_user}, {"$addToSet": {"following": followed_user}})
    followed = users.update_one({"_id": followed_user}, {"$addToSet": {"followers": following_user}})
    
    return {"status": "OK" if following and followed else "ERROR"}


@app.post("/unfollow/")
def unfollow(unfollowing_user: str, unfollowed_user: str):
    unfollowing = users.update_one({"_id": unfollowing_user}, {"$pull": {"following": unfollowed_user}})
    unfollowed = users.update_one({"_id": unfollowed_user}, {"$pull": {"followers": unfollowing_user}})
    
    return {"status": "OK" if unfollowing and unfollowed else "ERROR"}


@app.post("/{user_name}/{flap_owner}/{flap_id}/create-subflap/")
def create_subflap(user_name: str, flap_owner: str, flap_id: int, subflap: Flap):
    subflap = subflap.dict()
    subflap["user_name"] = user_name
    subflap_id = generate_random_id()
    subflap["flap_id"] = subflap_id
    subflap["date"] = round(datetime.datetime.now().timestamp() * 1000)
    result = users.update_one({"_id": flap_owner}, {"$set": {f"flaps.{flap_id}.subflaps.{subflap_id}": subflap}}).modified_count
    return {"status": "OK" if result else "ERROR", **subflap}
