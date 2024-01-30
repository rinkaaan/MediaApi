import os
import time

from apiflask import APIFlask
from b2sdk.v2 import InMemoryAccountInfo, B2Api
from dotenv import load_dotenv
from flask_cors import CORS
from flask_socketio import SocketIO

from api.resources.album import album_bp
from api.resources.media import media_bp
from models.base import Base, AlbumModel
from nguylinc_python_utils.sqlalchemy import init_sqlite_db

load_dotenv()

b2_account_id = os.getenv("B2_ACCOUNT_ID")
b2_application_key = os.getenv("B2_APPLICATION_KEY")
b2_bucket_name = os.getenv("B2_BUCKET_NAME")

info = InMemoryAccountInfo()
b2_api = B2Api(info)
b2_api.authorize_account("production", b2_account_id, b2_application_key)
bucket = b2_api.get_bucket_by_name(b2_bucket_name)

app = APIFlask(__name__, title="Media API", version="0.1.0", spec_path="/openapi.yaml", docs_ui="rapidoc")
socketio = SocketIO(app, cors_allowed_origins="*")
session = init_sqlite_db(Base)

app.config["SPEC_FORMAT"] = "yaml"
app.config["LOCAL_SPEC_PATH"] = "openapi.yaml"
app.config["SYNC_LOCAL_SPEC"] = True
CORS(app, supports_credentials=False, origins="*", allow_headers="*")

app.register_blueprint(album_bp)
app.register_blueprint(media_bp)


@socketio.on("connect")
def on_connect():
    print("Client connected!")


@app.teardown_appcontext
def shutdown_session(exception=None):
    if session:
        session.remove()


@app.before_request
def add_fake_delay():
    # fake_delay = 100
    fake_delay = 0.5
    # fake_delay = 1
    # fake_delay = 0
    time.sleep(fake_delay)


port = 34200
BASE_URL = "http://127.0.0.1:" + str(port)
CACHE_DOMAIN = os.getenv("CACHE_DOMAIN")


def init_models():
    from api.app import session

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
    app.run(port=port, debug=True)
