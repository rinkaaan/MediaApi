from apiflask import APIBlueprint, Schema, HTTPError
from apiflask.fields import String, Integer, List, Nested, Boolean
from typing import List as ListType
from sqlalchemy import desc, asc
from sqlalchemy.exc import IntegrityError

from api.schemas.main import AlbumSchema
from models.base import AlbumModel, MediaModel
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


class GetAlbumIn(Schema):
    album_id = String(validate=validate_ksuid)


@album_bp.get("/")
@album_bp.input(GetAlbumIn, arg_name="params", location="query")
@album_bp.output(AlbumSchema)
def get_album(params):
    from api.app import session
    album = session.query(AlbumModel).filter(AlbumModel.id == params["album_id"]).one()
    return album


class QueryAlbumsIn(Schema):
    last_id = String(load_default=None)
    limit = Integer(load_default=60)
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
    albums: ListType[AlbumModel] = q.all()
    album_schemas = []

    for album in albums:
        sorted_medias = sorted(album.media, key=lambda media: media.created_at, reverse=True)
        if sorted_medias:
            newest_media: MediaModel = sorted_medias[0]
            album_schema: AlbumSchema = AlbumSchema.from_dict(album.to_dict())
            album_schema.thumbnail_path = newest_media.thumbnail_path
            album_schemas.append(album_schema)
        else:
            print(f"No media in {album.name}")
            session.delete(album)

    return {
        "albums": album_schemas,
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
