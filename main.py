import asyncio
import json
import os
import tempfile
import zipfile
from typing import Union

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpcore
from dotenv import dotenv_values

envs = dotenv_values('.env')
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

headers = {
    "Authorization": f"Basic {envs['AUTHORIZATION']}"
}


@app.get("/backups/{user_id}")
async def backups(request: Request, user_id):
    user_res = send_request("GET", f"https://open.timepill.net/api/users/{user_id}")
    if 'id' not in user_res:
        return HTMLResponse(content="<h1>未找到用户！请检测ID是否正确。</h1>")

    notebooks_res = send_request("GET", f"https://open.timepill.net/api/users/{user_id}/notebooks")
    notebook_details = {}
    tasks = []
    for notebook in notebooks_res:
        if not notebook['isExpired']:
            continue
        tasks.append(async_send_request("GET",
                                        f"https://open.timepill.net/api/notebooks/{notebook['id']}/diaries?page=1&page_size=9999"))

    results = await asyncio.gather(*tasks)
    for result in results:
        if 'count' in result and result['count'] > 0:
            notebook_details[result['items'][0]['notebook_id']] = result['items']

    create_data_js(to_json_str(user_res), to_json_str(notebooks_res), to_json_str(notebook_details))

    folder_path = f"./show"
    zip_file_name = 'timepill.zip'
    with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                zipf.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file),
                                           start=folder_path))

    return FileResponse(zip_file_name, media_type='application/zip', filename="timepill.zip")


def create_data_js(user: str, notebooks: str, notebook_details: str):
    content = """
        let notebookDetailsJson = '%s'
        let userJson = '%s'
        let notebooksJson = '%s'
    """ % (notebook_details, user, notebooks)
    with open('show/js/data.js', 'w', encoding='utf-8') as file:
        file.write(content)


def to_json_str(data: dict):
    json_str = json.dumps(data, ensure_ascii=False)
    return json_str.replace("\\", "\\\\").replace("'", "\\'")


async def async_send_request(method: str, url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.request(method, url, headers=headers)
        return response.json()


def send_request(method: str, url: str):
    res = httpcore.request(method, url, headers=headers)
    return json.loads(res.content.decode("utf-8"))


@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="home.html")
