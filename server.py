import asyncio
import json
import websockets
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import ssl, os

app = FastAPI()

# Task dictionary for managing WebSocket connections
tasks = {}

import updateData


@app.get("/data.json")
async def getData():
    with open("static/data.json") as f:
        data = json.loads(f.read())
    return JSONResponse(data)


@app.get("/{page_name}")
async def get_page(page_name: str):
    file_path = f"static/{page_name}.html"
    if os.path.exists(file_path):
        return HTMLResponse(open(file_path).read())
    return HTMLResponse("Page not found", status_code=404)


@app.get("/")
async def get_home():
    return HTMLResponse(open("static/home.html").read())


# Static file serving
app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=6789)
