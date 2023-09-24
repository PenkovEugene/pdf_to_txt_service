import os
import asyncio
import requests

import psutil
import uvicorn
from fastapi import FastAPI, File, UploadFile, WebSocket
from typing import List

from functions.common import pdf_to_txt, get_now, save_file

HEALTH_EVENTS = {}


app = FastAPI(debug=True)


@app.post("/upload/{extension}")
def upload(extension: str, files: List[UploadFile] = File(...)):
    # Create temporary directory
    files_path = f"{os.getcwd()}/files"

    # Save file(s)
    list_filenames = []

    for file in files:
        try:
            content = file.file.read()
            filename = file.filename

            # Check multiple files
            if extension in filename:
                list_filenames.append(filename)

            with open(f"{files_path}/upload/{filename}", "wb") as file_save:
                file_save.write(content)

        except Exception as e:
            print(e)

            return {"message": "There was an error uploading the file(s)"}

        finally:
            file.file.close()

    # Text recognition
    try:
        for filename in list_filenames:
            # Запуск метода распознавания текста
            content = pdf_to_txt(f"{files_path}/upload/{filename}")

            filename_txt = f"{filename.split('.')[0]}.txt"
            save_file(f"{files_path}/recognized/{filename_txt}", str(content))

            # Отправка на серверы
            URL_DB_API = "http://127.0.0.1:5001/"
            res = requests.post(URL_DB_API, files={'files': open(f"{files_path}/recognized/{filename_txt}")})
            print(res.text)

            URL_CS_API = "http://127.0.0.1:5002/"
            res = requests.post(URL_CS_API, files={'files': open(f"{files_path}/recognized/{filename_txt}")})
            print(res.text)

        return {"message": "Files have been successfully uploaded and transferred to the database server and contextual search subsystem"}

    except Exception as e:
        print(e)
        return {"message": "Error with file(s)"}


@app.websocket("/health")
async def send_status(websocket: WebSocket):
    seconds_sleep = 10

    await websocket.accept()
    while True:
        # Создание события и добавление его в словарь HEALTH_EVENTS
        hdd = psutil.disk_usage('/')

        HEALTH_EVENTS[get_now()] = {
            "cpu_times": psutil.cpu_times().user,
            "cpu_percent": psutil.cpu_percent(1),
            "disk_total": hdd.total / (2**30),
            "disk_used": hdd.used / (2**30),
            "hdd_free": hdd.free / (2**30)
        }

        # Если есть подключение с сервером мониторинга, то отправляем события о состоянии
        try:
            if str(websocket.client_state) == "WebSocketState.CONNECTED":
                if HEALTH_EVENTS:
                    # Отправка на сервер мониторинга
                    await websocket.send_json(HEALTH_EVENTS)
                    # т.к. события были отправлены, то очищаем словарь HEALTH_EVENTS
                    HEALTH_EVENTS.clear()

            # Приостановка метода на seconds_sleep (10 секунд)
            await asyncio.sleep(seconds_sleep)

        except Exception as e:
            print(e)


if __name__ == '__main__':
    HOST = "127.0.0.1"
    PORT = 5000

    uvicorn.run(app, host=HOST, port=PORT)



