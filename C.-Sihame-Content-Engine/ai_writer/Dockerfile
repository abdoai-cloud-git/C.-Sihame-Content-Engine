FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/backend
ENV PORT=8080

COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY backend /app/backend
COPY knowledge_pack /app/knowledge_pack
COPY feedback_log.md /app/feedback_log.md

# Graphics Designer pack (brand rules, materiality, typography)
# NOTE: CI workflow copies this into the build context before building
COPY coach-siham-graphics-designer /app/coach-siham-graphics-designer
ENV DESIGNER_PACK_DIR=/app/coach-siham-graphics-designer

EXPOSE 8080

WORKDIR /app/backend

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
