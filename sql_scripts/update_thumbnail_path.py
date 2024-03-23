from models.base import MediaModel
from sql_scripts.clients import session


def get_file_path(url):
    return url.split("nguylinc-photos-test/")[1]

class Test:
    def test_add_ksuid(self):
        medias = session.query(MediaModel).all()

        for media in medias:
            media: MediaModel = session.query(MediaModel).filter(MediaModel.id == media.id).first()
            media.thumbnail_path = get_file_path(media.thumbnail_path)

        session.commit()
