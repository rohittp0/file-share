import random
import shutil
from glob import glob
from pathlib import Path

from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import RedirectResponse
from preview_generator.exception import UnsupportedMimeType
from preview_generator.manager import PreviewManager
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

upload_path = "static/uploads"
icons_path = "static/icons"

Path(upload_path).mkdir(parents=True, exist_ok=True)
manager = PreviewManager(f"{icons_path}/generated", create_folder=True)
templates = Jinja2Templates(directory="templates")


def get_safe_path(path) -> str:
    if not path:
        return ""

    path = path.replace(".", "").strip()

    if path.startswith("/"):
        path = path.replace("/", "", 1)
    if path.endswith("/"):
        path = path[:-1]

    return path


@app.post("/create-folder/")
async def create_folder(folder: str = Form(str), parent: str | None = Form(None)):
    folder = get_safe_path(folder)
    parent = get_safe_path(parent)
    path = f"{upload_path}/{parent}/{folder}"

    try:
        Path(path).mkdir(parents=True)
    except FileExistsError:
        return RedirectResponse(url=f"/?folder={parent}&error={folder} already exists", status_code=302)

    return RedirectResponse(url=f"/?folder={path}", status_code=302)


@app.post("/upload-files/")
async def create_upload_files(uploaded_files: list[UploadFile], parent: str | None = Form(None)):
    parent = get_safe_path(parent)
    path = f"{upload_path}/{parent}"

    for file in uploaded_files:
        with open(f"{path}/{random.randint(0, 1000)}{file.filename}", "wb+") as out:
            shutil.copyfileobj(file.file, out)

    return RedirectResponse(url=f"/?folder={parent}", status_code=302)


@app.get("/")
async def files(request: Request, folder="", error=""):
    object_list = []

    folder = get_safe_path(folder)

    if folder:
        previous = get_safe_path(f"/?folder={Path(folder).parent}")
    else:
        previous = None

    context = {"parent": folder, "request": request, "error": error, "previous": previous}

    if not Path(f"{upload_path}/{folder}").exists():
        context["error"] = "Folder Not Found"
        return templates.TemplateResponse("files.html", context=context)

    for file in glob(f"{upload_path}/{folder}/*"):
        name = Path(file).name

        if Path(file).is_dir():
            icon = f"{icons_path}/folder.webp"
            file = f"/?folder={name}"
        else:
            try:
                icon = manager.get_jpeg_preview(file, width=100, height=100)
            except UnsupportedMimeType:
                icon = f"{icons_path}/unknown.webp"

        object_list.append({"url": file, "icon": icon, "name": name})

    context["files"] = object_list
    return templates.TemplateResponse("files.html", context=context)
