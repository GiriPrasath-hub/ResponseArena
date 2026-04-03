FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 7860

# FORCE RUN THIS (NO AUTO-DETECTION)
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]