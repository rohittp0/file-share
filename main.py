import random
import shutil
from glob import glob
from pathlib import Path

from fastapi import FastAPI, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.staticfiles import StaticFiles

app = FastAPI()

upload_path = "static/uploads"

Path(upload_path).mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post("/upload-files/")
async def create_upload_files(uploaded_files: list[UploadFile]):
    for file in uploaded_files:
        with open(f"{upload_path}/{random.randint(0, 1000)}{file.filename}", "wb+") as out:
            shutil.copyfileobj(file.file, out)

    return RedirectResponse("/", status_code=200)


@app.get("/files")
async def files():
    object_list = []

    for file in glob(f"{upload_path}/*"):
        object_list.append(f"<a href='{file}'><object data='{file}'></object></a>")

    object_list = "\n".join(object_list)

    return HTMLResponse(content=f"""
        <head>
            <style>
                object{{
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                }}
                
                a {{
                    text-decoration: none;
                    cursor: pointer;
                    width: 20vw;
                    height: 20vw;
                }}
            </style>
        </head>
        <body style='display: flex; flex-wrap: wrap;'>{object_list}</body>
    """)


@app.get("/")
async def main():
    content = """
<body>
<form action="/upload-files/" enctype="multipart/form-data" method="post">
<input name="uploaded_files" type="file" multiple>
<input type="submit">
<a href="/files">Files</a>
</form>
</body>
    """
    return HTMLResponse(content=content)
