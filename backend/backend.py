import os.path
import shutil

from fastapi import FastAPI, Depends, status , Response , HTTPException, File, UploadFile,Form

from typing import List
from fastapi.middleware.cors import CORSMiddleware
from v4 import transcribe_audio, transcribe_and_correct
from fastapi.responses import FileResponse ,JSONResponse


app= FastAPI()

# Allow only the Vite app (running on port 5173) to access your FastAPI API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)




@app.post("/convert")
async def uploadfiles( files: List[UploadFile],maxnbwords : str =Form("0")):
    print("d5alna")
    maxnbwords=int(maxnbwords)
    print(maxnbwords )
    directory = 'upload'
    # Check if directory exists
    if os.path.exists(directory):
        # Delete the directory and its contents
        shutil.rmtree(directory)

    # Recreate the directory
    os.makedirs(directory)
    for file in files:

        data=await file.read()
        save_path=os.path.join("upload",file.filename)

        with open(save_path,"wb") as f:
            f.write(data)
    audio_path=""
    script_path=""
    for file in os.listdir("upload"):
        if file[-4:]==".mp3":
            audio_path=os.path.join("upload",file)
        elif file[-4:]==".txt":
            script_path=os.path.join("upload",file)
    if maxnbwords<=0:
        maxnbwords=None
    download_path=transcribe_and_correct(audio_path,script_path,max_words_per_line=maxnbwords)

    content ={"message": "SRT file created and ready", "download_url": download_path}
    print(content)
    return JSONResponse(content=content)

@app.post("/download",response_class=FileResponse)
def download(path : str = Form(...)):
    return path


if __name__ == "__main__":
    print("hello world")