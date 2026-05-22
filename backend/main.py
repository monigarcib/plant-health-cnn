from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import tensorflow as tf
from tensorflow.keras import layers, models
from PIL import Image
import numpy as np
import io


app = FastAPI(title="Clasificador de Plantas")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def crear_modelo():
    data_augmentation = tf.keras.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.1),
        layers.RandomZoom(0.1),
        layers.RandomContrast(0.1),
    ])

    model = models.Sequential([
        layers.Input(shape=(128, 128, 3)),
        data_augmentation,

        layers.Conv2D(32, (3, 3), activation="relu"),
        layers.MaxPooling2D(2, 2),

        layers.Conv2D(64, (3, 3), activation="relu"),
        layers.MaxPooling2D(2, 2),

        layers.Conv2D(128, (3, 3), activation="relu"),
        layers.MaxPooling2D(2, 2),

        layers.Flatten(),
        layers.Dense(128, activation="relu"),
        layers.Dropout(0.5),
        layers.Dense(1, activation="sigmoid")
    ])

    return model


model = crear_modelo()
model.load_weights("modelo_plantas.weights.h5")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


def preprocesar_imagen(file_bytes: bytes):
    image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    image = image.resize((128, 128))

    img_array = np.array(image) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    return img_array


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        img_array = preprocesar_imagen(file_bytes)

        prediction = model.predict(img_array)[0][0]

        if prediction >= 0.5:
            clase = "sana"
            confianza = float(prediction * 100)
            mensaje = "La planta parece estar en buen estado."
        else:
            clase = "marchita"
            confianza = float((1 - prediction) * 100)
            mensaje = "La planta podría presentar señales de deterioro."

        return {
            "clase": clase,
            "confianza": round(confianza, 2),
            "probabilidad_sana": round(float(prediction), 4),
            "mensaje": mensaje
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))