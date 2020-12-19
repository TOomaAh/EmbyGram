FROM python:3.7

ENV API_KEY=emby_api
ENV SERVER=http://localhost
ENV USER_ID=list,of,user,id
ENV BOT_ID=bot_id
ENV ADMIN=user_id_who_recieve_error

WORKDIR /app
COPY app .
RUN pip install -r /app/requirements.txt

CMD [ "python", "/app/main.py" ]