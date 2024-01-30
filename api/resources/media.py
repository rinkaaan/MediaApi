import json
import os.path
import subprocess

from apiflask import APIBlueprint, Schema, HTTPError
from apiflask.fields import String, List, Integer, Boolean, Nested
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError

from api.schemas.main import MediaSchema
from models.base import MediaModel, AlbumModel
from nguylinc_python_utils.misc import validate_ksuid

media_bp = APIBlueprint("Media", __name__, url_prefix="/media")


class AddMediaIn(Schema):
    # title = String()
    # thumbnail_path = String()
    media_url = String()
    # media_type = String()
    album_ids = List(String(validate=validate_ksuid))


@media_bp.post("/")
@media_bp.input(AddMediaIn, arg_name="params")
@media_bp.output(MediaSchema)
def add_media(params):
    from api.app import session, bucket, CACHE_DOMAIN

    command = f"yt-dlp --write-info-json --skip-download -o metadata --cookies ~/Desktop/cookies.txt \"{params['media_url']}\""
    process = subprocess.run(command, shell=True)
    if process.returncode == 0:
        # read files/metadata.json
        with open("metadata.info.json", "r") as f:
            metadata = json.load(f)

            id = metadata["id"]
            # title = metadata["title"]
            thumbnail = metadata["thumbnail"]
            # description = metadata["description"]
            website = metadata["extractor_key"]
            uploader = metadata["uploader"]

            upload_date = metadata["upload_date"]
            duration = metadata["duration"]
            webpage_url = metadata["webpage_url"]

            print(id)
            # print(title)
            print(thumbnail)
            # print(description)
            print(website)
            print(uploader)
            print(upload_date)
            print(duration)
            print(webpage_url)

            # download image at thumbnail
            # extract image extension from thumbnail url
            thumbnail_extension = os.path.basename(thumbnail).split(".")[1].split("?")[0]
            thumbnail_filename = f"thumbnail.{thumbnail_extension}"
            thumbnail_path = f"videos/{website}/{id}/thumbnail.{thumbnail_extension}"
            command = f"curl \"{thumbnail}\" -o \"{thumbnail_filename}\""
            process = subprocess.run(command, shell=True)

            if process.returncode != 0:
                raise HTTPError(400, "Error downloading thumbnail")

            bucket.upload_local_file(
                local_file=thumbnail_filename,
                file_name=thumbnail_path,
            )
            subprocess.run(f"rm thumbnail.{thumbnail_extension}", shell=True)

            thumbnail = f"{CACHE_DOMAIN}/file/{bucket.name}/{thumbnail_path}"

            media = MediaModel()
            media.id = f"{website}#{id}"
            media.thumbnail_path = thumbnail
            media.uploader = uploader
            media.duration = duration
            media.webpage_url = webpage_url

            # set thumbnail of all albums to thumbnail of media
            q = session.query(AlbumModel).filter(AlbumModel.id.in_(params["album_ids"]))
            for album in q.all():
                album.thumbnail_path = thumbnail
                media.albums.append(album)

            # if uploader not an album, add as new album
            q = session.query(AlbumModel).filter(AlbumModel.name == f"uploader={uploader}")
            if not q.first():
                print(f"uploader={uploader} not found, creating new album")
                album = AlbumModel()
                album.name = f"uploader={uploader}"
                album.thumbnail_path = thumbnail
                session.add(album)
                media.albums.append(album)

            # if website not an album, add as new album
            q = session.query(AlbumModel).filter(AlbumModel.name == f"website={website}")
            if not q.first():
                print(f"website={website} not found, creating new album")
                album = AlbumModel()
                album.name = f"website={website}"
                album.thumbnail_path = thumbnail
                session.add(album)
                media.albums.append(album)

            videos_album = session.query(AlbumModel).filter(AlbumModel.name == f"media_type=Videos").first()
            media.albums.append(videos_album)

            session.add(media)

            subprocess.run("rm metadata.info.json", shell=True)

    # else:
    #     raise HTTPError(400, "Invalid media URL")
    else:
        command = f"gallery-dl --no-download --dump-json --cookies ~/Desktop/cookies.txt \"{params['media_url']}\" > metadata.json"
        process = subprocess.run(command, shell=True)

        if process.returncode == 0:
            # read files/metadata.json
            with open("metadata.json", "r") as f:
                metadata = json.load(f)

                photos_album = session.query(AlbumModel).filter(AlbumModel.name == f"media_type=Photos").first()

                for image_obj in metadata:
                    # skip objects with length != 3
                    if len(image_obj) != 3:
                        continue
                    image_url = image_obj[1]
                    image_data = image_obj[2]
                    category = image_data["category"]
                    num = image_data["num"]
                    image_extension = image_data["extension"]
                    media = MediaModel()

                    if category == "twitter":
                        image_data = image_obj[2]
                        uploader = image_data["author"]["nick"]
                        username = image_data["author"]["name"]
                        image_id = image_data["tweet_id"]
                        webpage_url = f"https://twitter.com/{username}/status/{image_id}"
                        # content = image_data["content"]

                        print(image_url)
                        print(uploader)
                        print(webpage_url)
                        # print(content)

                        media.id = f"twitter#{image_id}#{num}"
                        media.uploader = uploader
                        media.webpage_url = webpage_url

                    elif category == "instagram":
                        image_data = image_obj[2]
                        uploader = image_data["fullname"]
                        image_id = image_data["post_shortcode"]
                        webpage_url = f"https://www.instagram.com/p/{image_id}"
                        # description = image_data["description"]

                        print(image_url)
                        print(uploader)
                        print(webpage_url)
                        # print(description)

                        media.id = f"instagram#{image_id}#{num}"
                        media.uploader = uploader
                        media.webpage_url = webpage_url

                    else:
                        raise HTTPError(422, "Unsupported photo website")

                    # Download image at image_url
                    # extract image extension from image url
                    image_filename = f"image.{image_extension}"
                    image_path = f"images/{category}/{image_id}/{num}.{image_extension}"
                    command = f"curl \"{image_url}\" -o \"{image_filename}\""
                    process = subprocess.run(command, shell=True)

                    if process.returncode != 0:
                        raise HTTPError(400, "Error downloading image")

                    bucket.upload_local_file(
                        local_file=image_filename,
                        file_name=image_path,
                    )
                    subprocess.run(f"rm image.{image_extension}", shell=True)

                    image_url = f"{CACHE_DOMAIN}/file/{bucket.name}/{image_path}"
                    media.thumbnail_path = image_url

                    # set thumbnail of all albums to thumbnail of media
                    q = session.query(AlbumModel).filter(AlbumModel.id.in_(params["album_ids"]))
                    for album in q.all():
                        album.thumbnail_path = image_url
                        media.albums.append(album)

                    # append photos album to media
                    media.albums.append(photos_album)

                    if num == 1:
                        # if uploader not an album, add as new album
                        q = session.query(AlbumModel).filter(AlbumModel.name == f"uploader={uploader}")
                        if not q.first():
                            print(f"uploader={uploader} not found, creating new album")
                            uploader_album = AlbumModel()
                            uploader_album.name = f"uploader={uploader}"
                            uploader_album.thumbnail_path = image_url
                            session.add(uploader_album)

                        # if website not an album, add as new album
                        q = session.query(AlbumModel).filter(AlbumModel.name == f"website={category}")
                        if not q.first():
                            print(f"website={category} not found, creating new album")
                            website_album = AlbumModel()
                            website_album.name = f"website={category}"
                            website_album.thumbnail_path = image_url
                            session.add(website_album)

                    uploader_album = session.query(AlbumModel).filter(AlbumModel.name == f"uploader={uploader}").first()
                    website_album = session.query(AlbumModel).filter(AlbumModel.name == f"website={category}").first()

                    media.albums.append(uploader_album)
                    media.albums.append(website_album)

                    session.add(media)

                subprocess.run("rm metadata.json", shell=True)

                # update thumbnail of photos album
                photos_album.thumbnail_path = image_url
        else:
            raise HTTPError(400, "Invalid media URL")

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPError(400, "Media already exists")

    return {}


class AddMediaToAlbumIn(Schema):
    media_id = String(validate=validate_ksuid)
    album_id = String(validate=validate_ksuid)


@media_bp.post("/add-to-album")
@media_bp.input(AddMediaToAlbumIn, arg_name="params")
@media_bp.output({})
def add_media_to_album(params):
    from api.app import session
    media = session.query(MediaModel).filter(MediaModel.id == str(params["media_id"])).first()
    album = session.query(AlbumModel).filter(AlbumModel.id == str(params["album_id"])).first()
    media.albums.append(album)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPError(400, "Media already in album")
    return {}


class RemoveMediaFromAlbumIn(Schema):
    media_id = String(validate=validate_ksuid)
    album_id = String(validate=validate_ksuid)


@media_bp.post("/remove-from-album")
@media_bp.input(RemoveMediaFromAlbumIn, arg_name="params")
@media_bp.output({})
def remove_media_from_album(params):
    from api.app import session
    media = session.query(MediaModel).filter(MediaModel.id == str(params["media_id"])).first()
    if not media:
        raise HTTPError(404, "Media not found")

    album = session.query(AlbumModel).filter(AlbumModel.id == str(params["album_id"])).first()
    if not album:
        raise HTTPError(404, "Album not found")

    media.albums.remove(album)
    session.commit()
    return {}


class GetMediaIn(Schema):
    media_id = String()


@media_bp.get("/")
@media_bp.input(GetMediaIn, arg_name="params", location="query")
@media_bp.output(MediaSchema)
def get_media(params):
    from api.app import session
    media = session.query(MediaModel).filter(MediaModel.id == str(params["media_id"])).first()
    if not media:
        raise HTTPError(404, "Media not found")
    media_dict = media.to_dict()
    media_dict["albums"] = [album.to_dict() for album in media.albums]
    return media_dict


class QueryMediaIn(Schema):
    last_id = String(load_default=None)
    limit = Integer(load_default=30)
    descending = Boolean(load_default=True)
    # search = String(load_default=None)
    album_id = String(load_default=None, validate=validate_ksuid)


class QueryMediaOut(Schema):
    media = List(Nested(MediaSchema))
    no_more_media = Boolean()


@media_bp.get("/query")
@media_bp.input(QueryMediaIn, arg_name="params", location="query")
@media_bp.output(QueryMediaOut)
def query_media(params):
    from api.app import session
    q = session.query(MediaModel)

    if params["album_id"]:
        q = q.filter(MediaModel.albums.any(id=str(params["album_id"])))

    if params["last_id"]:
        if params["descending"]:
            q = q.filter(MediaModel.id < params["last_id"])
        else:
            q = q.filter(MediaModel.id > params["last_id"])

    # if params["search"]:
    #     q = q.filter(MediaModel.title.contains(params["search"]))

    if params["descending"]:
        q = q.order_by(desc(MediaModel.created_at))
    q = q.limit(params["limit"])

    if params["album_id"]:
        media_list = [media.to_dict() for media in q.all()]
    # if album was not specified, populate albums field of each media
    else:
        media_list = []
        for media in q.all():
            media_dict = media.to_dict()
            media_dict["albums"] = [album.to_dict() for album in media.albums]
            media_list.append(media_dict)

    return {
        "media": media_list,
        "no_more_media": len(media_list) < params["limit"]
    }


class DeleteMediaIn(Schema):
    media_ids = List(String(validate=validate_ksuid))


@media_bp.delete("/")
@media_bp.input(DeleteMediaIn, arg_name="params")
@media_bp.output({})
def delete_media(params):
    from api.app import session
    for media_id in params["media_ids"]:
        media = session.query(MediaModel).filter(MediaModel.id == str(media_id)).first()
        if not media:
            continue
        session.delete(media)
    session.commit()
    return {}
