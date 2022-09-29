FROM python:3.10.2-slim
RUN mkdir /game
COPY ./game_server /game/
RUN pip install --no-cache-dir --upgrade -r game/requirements.txt
COPY ./app /app/
# CMD ["python3", "game/server.py"]
