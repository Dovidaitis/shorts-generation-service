from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from openai import OpenAI
from tempfile import NamedTemporaryFile
import os

client = OpenAI()

app = FastAPI()

# Add CORS middleware
# Allows to make requests from any origin 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

def get_time() -> str:
    time = datetime.now()
    time_dic = {
        "year": time.year,
        "month": time.month,
        "day": time.day,
        "hour": time.hour,
        "minute": time.minute,
        "second": time.second
    }
    return time_dic

@app.get("/")
async def root():
    return {"message": "sanity_check"}

@app.post("/transcribe_audio")
async def upload_audio(file: UploadFile = File(...)):
    time_received = get_time()
    # Validate the file is an .mp3 based on the MIME type
    if file.content_type != "audio/mpeg":
        raise HTTPException(status_code=400, detail="Invalid file type. Only .mp3 audio files are accepted.")

    
    with NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        temp_file_path = temp_file.name
        contents = await file.read()
        temp_file.write(contents)
        temp_file.flush()

    try:
        transcript = client.audio.transcriptions.create(
            file=open(temp_file_path, "rb"),
            model="whisper-1",
            response_format="json",
            timestamp_granularities=["segment"]
        )
    finally:
        os.remove(temp_file_path)

    return {"filename": file.filename, "transcript": transcript.text, "time_received": time_received}