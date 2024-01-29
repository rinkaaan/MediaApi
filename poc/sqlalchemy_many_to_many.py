from sqlalchemy import Column, Integer, String, create_engine, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

if __name__ == "__main__":
    # Create a base class for declarative mapping
    Base = declarative_base()


    # Define the Album and Photo models with a many-to-many relationship
    class Album(Base):
        __tablename__ = "albums"

        id = Column(Integer, primary_key=True)
        name = Column(String)

        photos = relationship("Photo", secondary="album_photo", back_populates="albums")


    class Photo(Base):
        __tablename__ = "photos"

        id = Column(Integer, primary_key=True)
        filename = Column(String)

        albums = relationship("Album", secondary="album_photo", back_populates="photos")


    # Define the association table (album_photo)
    album_photo = Table(
        "album_photo",
        Base.metadata,
        Column("album_id", Integer, ForeignKey("albums.id")),
        Column("photo_id", Integer, ForeignKey("photos.id")),
    )

    # Create the database engine
    engine = create_engine("sqlite:///photos.db")  # Replace with your database URL

    # Create all tables in the database
    Base.metadata.create_all(engine)

    # Create a session to interact with the database
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create some sample data
    album1 = Album(name="Vacation")
    photo1 = Photo(filename="beach.jpg")
    photo2 = Photo(filename="sunset.jpg")

    # Add photos to the album
    album1.photos.append(photo1)
    album1.photos.append(photo2)

    album2 = Album(name="Family")
    photo3 = Photo(filename="baby.jpg")
    photo4 = Photo(filename="wedding.jpg")

    album2.photos.append(photo3)
    album2.photos.append(photo4)

    # Add some photos that belong to both albums
    album1.photos.append(photo3)
    album1.photos.append(photo4)

    # Add the album to the session and commit the changes
    session.add(album1)
    session.commit()

    # # Create an album with no photos
    # album3 = Album(name="Empty album")
    # session.add(album3)
    #
    # # Query for albums with their photos
    # albums = session.query(Album).all()
    # for album in albums:
    #     print(f"Album: {album.name}")
    #     for photo in album.photos:
    #         print(f"  Photo: {photo.filename}")

    # Query for photos with their albums
    photos = session.query(Photo).all()
    for photo in photos:
        print(f"Photo: {photo.filename}")
        for album in photo.albums:
            print(f"  Album: {album.name}")

    # Rename a photo and check if all albums containing it are updated
    photo3.filename = "baby2.jpg"
    session.commit()

    print("After renaming photo3:")

    albums = session.query(Album).all()
    for album in albums:
        print(f"Album: {album.name}")
        for photo in album.photos:
            print(f"  Photo: {photo.filename}")

    # Close the session
    session.close()
