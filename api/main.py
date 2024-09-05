from typing import Union, Optional, Annotated
from fastapi import FastAPI, HTTPException, Depends, UploadFile
from strawberry.fastapi import GraphQLRouter
from pydantic import EmailStr
from mongoengine import connect, disconnect
import cloudinary
import os
from dotenv import load_dotenv

from .database.types import UserType, LoginType, UserSignUpType
from .schema import schema , Context
from .database.models import User as UserModel
from .utils import get_savan_data, password_hasher, password_checker
from .auth.handler import JWTBearer, encode_jwt, decode_jwt
from .uploader import upload_image

load_dotenv()

async def get_context() -> Context:
    return Context()

graphql_app = GraphQLRouter(schema, context_getter=get_context)
graphql_dev_app = GraphQLRouter(schema, debug=True, context_getter=get_context, graphql_ide="apollo-sandbox")

app = FastAPI(title="Beatify API", version="0.1.0")
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", default="duqwlbo9s"),
    api_key=os.getenv("CLOUDINARY_API_KEY", default="852443822948814"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET", default="Y8BLlObJoLCU_wcTnVm0AmoeJ9U")
)
connect(host="mongodb+srv://raviblog:Ravisaini12beatify@beatify.8c3uw.mongodb.net/beatify?retryWrites=true&w=majority&appName=Beatify")
app.include_router(graphql_app, prefix="/graphql", include_in_schema=False)
app.include_router(graphql_dev_app, prefix="/dev/graphql", include_in_schema=False)

@app.get("/")
def root():
    return {"message": "Welcome to the Beatify API!", "version": "0.1.0", "status": "running"}

@app.post("/login")
def user_login(data: LoginType):
    user = UserModel.objects(email=data.email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not password_checker(data.password, user.password):
        raise HTTPException(status_code=403, detail="Invalid password")
    return {**encode_jwt(user.id), "user": UserType(**user.to_mongo().to_dict(), id=str(user.id))}

@app.post("/create-account")
def user_create_account(user: UserSignUpType):
    _user = UserModel.objects(email=user.email).first()
    if _user is not None:
        raise HTTPException(status_code=409, detail="User already exists")
    user_data = user.dict()
    user_data["password"] = password_hasher(user_data["password"])
    user = UserModel(**user_data).save()
    return {**encode_jwt(user.id), "user": UserType(**user.to_mongo().to_dict(), id=str(user.id))}

async def get_current_user(token: Annotated[str, Depends(JWTBearer())]):
    user_id = decode_jwt(token).get("user_id", None)
    if user_id is None:
        raise HTTPException(status_code=403, detail="Invalid token")
    user = UserModel.objects(id=user_id).first()
    return user

@app.get("/user/me", dependencies=[Depends(JWTBearer())], response_model=UserType)
async def read_user_me(current_user: UserModel | None = Depends(get_current_user)):
    return UserType(**current_user.to_mongo().to_dict(), id=str(current_user.id))

@app.get("/user/exists")
async def check_user_exists(email: EmailStr):
    user = UserModel.objects(email=email).first()
    return {"exists": user is not None} 

@app.post("/user", response_model=UserType)
async def create_user(user: UserType):
    inserted_user = UserModel(**user.dict()).save()
    return UserType(**inserted_user.to_mongo().to_dict())

@app.post("/forgot-password")
async def forgot_password(email: EmailStr):
    user = UserModel.objects(email=email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Password reset link sent to your email"}


@app.post("/user/{id}/upload", dependencies=[Depends(JWTBearer())])
async def upload_profile_picture(id: str, file: UploadFile):
    user = UserModel.objects(id=id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    url = await upload_image(file)
    user.profile_picture = url
    user.save()
    return UserType(**user.to_mongo().to_dict(), id=str(user.id))

@app.get("/savan_data")
async def read_savan_data():
    return get_savan_data()

@app.get("/music-languages")
async def read_music_languages():
    music_languages = [
        {"id": "hin", "name": "Hindi", "color": "FFD700"},
        {"id": "itr", "name": "International", "color": "000000"},
        {"id": "pun", "name": "Punjabi", "color": "FF1493"},
        {"id": "mal", "name": "Malayalam", "color": "FF69B4"},
        {"id": "tam", "name": "Tamil", "color": "FF4500"},
        {"id": "tel", "name": "Telugu", "color": "FF6347"},
        {"id": "ben", "name": "Bengali", "color": "4169E1"},
        {"id": "guj", "name": "Gujarati", "color": "FF0000"},
        {"id": "kan", "name": "Kannada", "color": "FF8C00"},
        {"id": "mar", "name": "Marathi", "color": "800080"},
        {"id": "ori", "name": "Oriya", "color": "008000"},
    ]
    return {"results": music_languages}

@app.get("/personalized/top-artists")
async def read_top_artist():
    data = get_savan_data('__call=social.getTopArtists&api_version=4&_format=json&_marker=0&ctx=android')
    new = []
    data = data["top_artists"]
    for item in data:
        new.append(
            {"id": item["artistid"],
            "name": item["name"],
            "image": item["image"],
            "is_followed": item["is_followed"],
            "type": "artist"})
    return {"results": new}

@app.get("/artist/search")
async def search_artist(q: str, p: Optional[int] = 1, n: Optional[int] = 10, marker: Optional[int] = 0, doFormat: bool = False):
    data = get_savan_data(f'__call=search.getArtistResults&_format=json&_marker={marker}&api_version=4&ctx=android&n={n}&p={p}&q={q}')
    if doFormat:
        new = []
        results = data["results"]
        for item in results:
            if item["entity"] == 0: continue
            new.append(
                {"id": item["id"],
                "name": item["name"],
                "image": item["image"],
                "is_followed": item["is_followed"],
                "type": "artist"})
        return {"results": new, "total": data["total"], "start": data["start"]}
        
    return {"results": data["results"], "total": data["total"], "start": data["start"]}

from .helpers.formatter import JioSaavn

@app.get("/browse/new-releases")
def read_new_releases(image_size: Optional[str] = 'medium', p: Optional[int] = 1, n: Optional[int] = 10):
    data = get_savan_data(f'__call=content.getAlbums&api_version=4&_format=json&_marker=0&n={n}&p={p}&ctx=web6dot0')
    data = JioSaavn.jiosaavan_albums_formatted(data["data"], image_size)
    return {"results": data, "total": len(data), "title": "New Releases"}


@app.get("/browse/this-year-hits")
def read_this_year_hits(image_size: Optional[str] = 'medium', include_songs: Optional[bool] = False):
    data = get_savan_data(f'__call=search.topAlbumsoftheYear&api_version=4&_format=json&_marker=0&album_year=1980&album_lang=hindi')
    data = JioSaavn.jiosaavan_albums_formatted(data, image_size, include_songs)
    return {"results": data, "total": len(data), "title": "This Year Hits"}