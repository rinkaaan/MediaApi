from apiflask import APIBlueprint, Schema, HTTPError
from apiflask.fields import String, Integer, List, Nested, Boolean
from sqlalchemy import desc, asc
from sqlalchemy.exc import IntegrityError

from api.schemas.main import AlbumSchema
from models.base import AlbumModel
from nguylinc_python_utils.misc import validate_ksuid

album_bp = APIBlueprint("Album", __name__, url_prefix="/album")


class AddAlbumIn(Schema):
    name = String()


@album_bp.post("/")
@album_bp.input(AddAlbumIn, arg_name="params")
@album_bp.output(AlbumSchema)
def add_album(params):
    from api.app import session
    try:
        album = AlbumModel()
        album.name = params["name"]
        session.add(album)
        session.commit()
        session.refresh(album)
    except IntegrityError:
        session.rollback()
        raise HTTPError(400, "Album already exists")
    return album.to_dict()


class QueryAlbumsIn(Schema):
    last_id = String(load_default=None)
    limit = Integer(load_default=30)
    descending = Boolean(load_default=True)
    search = String(load_default=None)


class QueryAlbumsOut(Schema):
    albums = List(Nested(AlbumSchema))
    no_more_albums = Boolean()


@album_bp.get("/query")
@album_bp.input(QueryAlbumsIn, arg_name="params", location="query")
@album_bp.output(QueryAlbumsOut)
def query_albums(params):
    from api.app import session
    q = session.query(AlbumModel)

    if params["last_id"]:
        if params["descending"]:
            q = q.filter(AlbumModel.id < params["last_id"])
        else:
            q = q.filter(AlbumModel.id > params["last_id"])

    if params["search"]:
        q = q.filter(AlbumModel.name.contains(params["search"]))

    if params["descending"]:
        q = q.order_by(desc(AlbumModel.id))
    else:
        q = q.order_by(asc(AlbumModel.id))

    q = q.limit(params["limit"])
    albums = [album.to_dict() for album in q]
    return {
        "albums": albums,
        "no_more_albums": len(albums) < params["limit"]
    }


class DeleteAlbumIn(Schema):
    album_ids = List(String(validate=validate_ksuid))


@album_bp.delete("/")
@album_bp.input(DeleteAlbumIn, arg_name="params")
@album_bp.output({})
def delete_album(params):
    from api.app import session
    for album_id in params["album_ids"]:
        session.query(AlbumModel).filter(AlbumModel.id == album_id).delete()
    session.commit()
    return {}
