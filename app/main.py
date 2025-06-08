import os
import uuid

from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import shutil
import librosa
from threading import Lock
import yt_dlp

from genre_model.processing.feature_extraction import extract_features
from genre_model.predict import make_prediction, resolve_prediction

app = FastAPI()
app.state.counter = 0
app.state.lock = Lock()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload/", response_class=HTMLResponse)
async def upload_audio(request: Request, file: UploadFile = File(...)):
    counter_value = None
    with request.app.state.lock:
        request.app.state.counter += 1
        counter_value = request.app.state.counter

    assert counter_value is not None

    file_location = f"uploaded_files/uploaded_{counter_value}.mp3"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        audio, sr = librosa.load(file_location)
    except Exception as e:
        print(f"Error happened {e}")
        return JSONResponse(status_code=400, content="")

    features_data = extract_features(audio, sr)
    result = make_prediction(input_data=features_data)
    print(result)
    str_result = resolve_prediction(input_data=result[0]["preds"][0])

    return templates.TemplateResponse("result.html", {"request": request, "result": str_result})


@app.post("/upload_yt_url/", response_class=HTMLResponse)
async def upload_audio_youtube(request: Request, youtube_url: str = Form(...)):

    print(youtube_url)

    fileName = f"youtube_{uuid.uuid4().hex[:8]}"
    output_path = os.path.join("uploaded_files/", f"{fileName}.mp3")

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "outtmpl": output_path.replace(".mp3", ".%(ext)s"),
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(youtube_url, download=True)

    audio, sr = librosa.load(f"uploaded_files/{fileName}.mp3")

    features_data = extract_features(audio, sr)
    result = make_prediction(input_data=features_data)
    print(result)
    str_result = resolve_prediction(input_data=result[0]["preds"][0])

    return templates.TemplateResponse("result.html", {"request": request, "result": str_result})
