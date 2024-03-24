import os

from apiflask import APIBlueprint, Schema
from apiflask.fields import File
from apiflask.validators import FileSize, FileType

main_bp = APIBlueprint("Main", __name__, url_prefix="/main")


class Cookies(Schema):
    cookies = File(validate=[FileType([".txt"]), FileSize(max="1 MB")])


@main_bp.post("/cookies")
@main_bp.input(Cookies, location="files")
def update_cookies(files_data):
    f = files_data["cookies"]
    f.save(os.path.join(os.path.expanduser("~"), "cookies.txt"))
    return {}
