FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

ENV PYTHONUNBUFFERED=1 \
	PYTHONIOENCODING=UTF-8 \
	PYTHONDONTWRITEBYTECODE=1

CMD ["sh", "-c", "python generate_config.py && python -u main.py"]
