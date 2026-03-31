FROM python:3.11-slim

WORKDIR /app

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 7860

CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app"]

# CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "1", "--timeout", "120", "app.app:app"]