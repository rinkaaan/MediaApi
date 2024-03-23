from apiflask import APIBlueprint, Schema, HTTPError
from apiflask.fields import String, Integer, List, Nested, Boolean
from sqlalchemy import desc, asc
from sqlalchemy.exc import IntegrityError

from api.schemas.main import AlbumSchema
from models.base import AlbumModel
from utils.misc import validate_ksuid, get_ksuid

album_bp = APIBlueprint("Album", __name__, url_prefix="/album")


class AddAlbumIn(Schema):
    name = String()


class AddAlbumOut(Schema):
    name = String()


@album_bp.post("/")
@album_bp.input(AddAlbumIn, arg_name="params")
@album_bp.output(AddAlbumOut)
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
    return {
        "name": album.name
    }


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


class RenameAlbumIn(Schema):
    album_id = String(validate=validate_ksuid)
    new_name = String()


@album_bp.put("/rename")
@album_bp.input(RenameAlbumIn, arg_name="params")
@album_bp.output({})
def rename_album(params):
    from api.app import session
    album = session.query(AlbumModel).filter(AlbumModel.id == params["album_id"]).one()
    album.name = params["new_name"]
    album.id = get_ksuid()
    session.commit()

    # rename all media_albums with the new album id
    session.execute(
        f"UPDATE media_albums SET album_id = '{album.id}' WHERE album_id = '{params['album_id']}'"
    )

    return {}
