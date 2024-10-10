FROM python:3.11.9

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100


COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

WORKDIR /bot

COPY ./bot /bot/

CMD ["python", "/bot/main.py"]