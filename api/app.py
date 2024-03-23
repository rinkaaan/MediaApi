import os
import time
import typing

from apiflask import APIFlask, HTTPBasicAuth
from b2sdk.v2 import InMemoryAccountInfo, B2Api
from dotenv import load_dotenv
from flask_cors import CORS
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash

from api.resources.album import album_bp
from api.resources.media import media_bp
from models.base import Base, AlbumModel
from utils.sqlalchemy import init_sqlite_db

load_dotenv()

B2_ACCOUNT_ID = os.getenv("B2_ACCOUNT_ID")
B2_APPLICATION_KEY = os.getenv("B2_APPLICATION_KEY")
B2_BUCKET_NAME = os.getenv("B2_BUCKET_NAME")
COOKIES_PATH = os.getenv("COOKIES_PATH")
CACHE_DOMAIN = os.getenv("CACHE_DOMAIN")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

info = InMemoryAccountInfo()
b2_api = B2Api(info)
b2_api.authorize_account("production", B2_ACCOUNT_ID, B2_APPLICATION_KEY)
bucket = b2_api.get_bucket_by_name(B2_BUCKET_NAME)

app = APIFlask(__name__, title="Media API", version="0.1.0", spec_path="/openapi.yaml", docs_ui="rapidoc")
auth = HTTPBasicAuth()
socketio = SocketIO(app, cors_allowed_origins="*")
session = init_sqlite_db(Base)

app.config["SPEC_FORMAT"] = "yaml"
app.config["LOCAL_SPEC_PATH"] = "openapi.yaml"
app.config["SYNC_LOCAL_SPEC"] = True
CORS(app, supports_credentials=False, origins="*", allow_headers="*", expose_headers="*")

app.register_blueprint(album_bp)
app.register_blueprint(media_bp)

users = {
    USERNAME: generate_password_hash(PASSWORD),
}


@auth.verify_password
def verify_password(username: str, password: str) -> typing.Union[str, None]:
    if (
        username in users
        and check_password_hash(users[username], password)
    ):
        return username
    return None


@socketio.on("connect")
def on_connect():
    print("Client connected!")


@app.teardown_appcontext
def shutdown_session(exception=None):
    if session:
        session.remove()


@app.get("/ping")
def ping():
    return "pong"


@app.before_request
@app.auth_required(auth)
def add_fake_delay():
    # fake_delay = 100
    # fake_delay = 0.5
    # fake_delay = 1
    fake_delay = 0
    time.sleep(fake_delay)


def init_models():
    # if media_type=Videos not found, create it
    q = session.query(AlbumModel).filter(AlbumModel.name == f"media_type=Videos")
    if not q.first():
        print(f"media_type=video not found, creating new album")
        album = AlbumModel()
        album.name = f"media_type=Videos"
        session.add(album)

    # if media_type=Photos not found, create it
    q = session.query(AlbumModel).filter(AlbumModel.name == f"media_type=Photos")
    if not q.first():
        print(f"media_type=photo not found, creating new album")
        album = AlbumModel()
        album.name = f"media_type=Photos"
        session.add(album)

    session.commit()


if __name__ == "__main__":
    init_models()
    app.run(port=34201, debug=True)
