from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil
import librosa
from threading import Lock

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

    audio, sr = librosa.load(file_location)

    features_data = extract_features(audio, sr)
    result = make_prediction(input_data=features_data)
    print(result)
    str_result = resolve_prediction(input_data=result[0]["preds"][0])

    return templates.TemplateResponse("result.html", {"request": request, "result": str_result})

