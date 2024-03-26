import logging

from models.base import MediaModel, AlbumModel
from sql_scripts.clients import session


def get_file_path(url):
    if "nguylinc-photos-test" in url:
        return url.split("nguylinc-photos-test/")[1]
    return url


class Test:
    def test_add_ksuid(self):
        albums = session.query(AlbumModel).all()
        logging.disable(logging.WARNING)

        for album in albums:
            album: AlbumModel = session.query(AlbumModel).filter(AlbumModel.id == album.id).first()
            # print(album.media)

            # for media in album.media:
            #     media: MediaModel = session.query(MediaModel).filter(MediaModel.id == media.id).first()
            #     print(media.thumbnail_path)

            sorted_medias = sorted(album.media, key=lambda media: media.created_at, reverse=True)
            if sorted_medias:
                newest_media: MediaModel = sorted_medias[0]
                # print(newest_media.thumbnail_path)
            else:
                print(f"No media in {album.name}")
                # Delete the album if there are no media
                session.delete(album)

            # get newest media added to album
            # album.medias: MediaModel = session.query(MediaModel).filter(MediaModel.album_id == album.id).order_by(MediaModel.created_at.desc()).first()
            # media: MediaModel = session.query(MediaModel).filter(MediaModel. == album.id).order_by(MediaModel.created_at.desc()).first()
            # print(album.name)
            # print(media.thumbnail_path)
            # print()

        session.commit()
