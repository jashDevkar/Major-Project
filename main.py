from fastapi import FastAPI, File, UploadFile, Form
import speech_recognition as sr
from pydub import AudioSegment
from googletrans import Translator
from deep_translator import GoogleTranslator
import os

app = FastAPI()

@app.get("/")
def greet():
    return "server is running"


@app.post("/speech-to-text/")
async def speech_to_text(
    file: UploadFile = File(...),
    source_lang: str = Form("en-IN"),  
    translate_to: str = Form("en")      
):
    try:
        os.makedirs("uploads", exist_ok=True)
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())

        if not file.filename.endswith(".wav"):
            sound = AudioSegment.from_file(file_path)
            wav_path = file_path.rsplit(".", 1)[0] + ".wav"
            sound.export(wav_path, format="wav")
        else:
            wav_path = file_path

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            detected_text = recognizer.recognize_google(audio_data, language=source_lang)

        os.remove(file_path)
        if wav_path != file_path:
            os.remove(wav_path)

        translator = Translator()
      
        src_lang = source_lang.split("-")[0]

        translated = translator.translate(detected_text, src=src_lang, dest=translate_to)

        romanized = GoogleTranslator(source=translate_to, target="en").translate(translated.text)

        return {
            "original_text": detected_text,
            "translated_text": translated.text,
            "romanized_text": romanized,
            "source_language": source_lang,
            "target_language": translate_to
        }

    except sr.UnknownValueError:
        return {"error": "Could not understand the audio"}
    except sr.RequestError as e:
        return {"error": f"API request failed: {e}"}
    except Exception as e:
        return {"error": str(e)}
