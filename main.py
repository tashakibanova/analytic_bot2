from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv
import fitz  # PyMuPDF
import pandas as pd
import os
from io import BytesIO

# Загружаем переменные окружения
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# Разрешаем запросы с любых источников
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API is running"}

# Хранилище лимитов по email
email_counters = {}
LIMIT = 5

@app.post("/upload")
async def upload_file(file: UploadFile, email: str = Form(...)):
    count = email_counters.get(email, 0)
    if count >= LIMIT:
        raise HTTPException(status_code=403, detail="Вы достигли лимита бесплатных анализов.")

    content = await file.read()
    extension = file.filename.split(".")[-1].lower()

    try:
        if extension == "pdf":
            text = extract_text_from_pdf(content)
        elif extension in ["csv", "xlsx"]:
            text = extract_text_from_spreadsheet(content, extension)
        else:
            raise ValueError("Недопустимый формат файла. Поддерживаются PDF, CSV, XLSX.")

        analysis = ask_gpt(text)

        email_counters[email] = count + 1
        return {"result": analysis}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def extract_text_from_pdf(file_bytes):
    text = ""
    pdf = fitz.open(stream=file_bytes, filetype="pdf")
    for page in pdf:
        text += page.get_text()
    return text[:3000]

def extract_text_from_spreadsheet(file_bytes, extension):
    if extension == "csv":
        df = pd.read_csv(BytesIO(file_bytes))
    else:
        df = pd.read_excel(BytesIO(file_bytes))
    return df.to_string(index=False)[:3000]

def ask_gpt(text):
    prompt = (
        "Вы — эксперт по финансовому анализу. Проанализируйте следующий текст отчета и кратко ответьте:\n"
        "- Доходность\n- Долги\n- Риски\n- Общая стабильность\n\n"
        f"Текст:\n{text}"
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.4,
    )

    return response.choices[0].message.content
