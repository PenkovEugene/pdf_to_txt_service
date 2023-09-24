import os
import uvicorn
from fastapi import FastAPI, File, UploadFile, WebSocket, Request
from typing import List

app = FastAPI(debug=True)

@app.post("/")
def upload(files: List[UploadFile] = File(...)):
    # Create temporary directory
    temp_path = f"{os.getcwd()}\\search_mdl\\upload\\"

    # Save file(s)
    list_filenames = []

    for file in files:
        try:
            content = file.file.read()
            filename = file.filename

            # Check multiple files
            
            list_filenames.append(filename)
            with open(f"{temp_path}{filename}", "wb") as file_save:
                file_save.write(content)
                return {"search_mdl's message": "OK"}

        except Exception as e:
            print(e)

            return {"message": "There was an error uploading the file(s)"}
        
        finally:
            file.file.close()

        
if __name__ == '__main__':
    HOST = "127.0.0.1"
    PORT = 5002

    uvicorn.run(app, host=HOST, port=PORT)