FROM node:20-alpine as frontend
RUN apk add git
RUN git clone --depth 1 https://github.com/koldun256/knowledge-fishing /frontend
WORKDIR /frontend
RUN npm install && npm run build

FROM python:3.12

RUN apt update && apt install -y git
RUN pip install -r requirements.txt

RUN git clone --depth 1 https://github.com/shevnind/Knowledge-fishing /backend

WORKDIR /backend

RUN mkdir ssl
COPY ssl ./ssl/

RUN mkdir build
COPY --from=frontend /frontend/build ./build

ENV DATABASE_PATH = "sqlite:////data/database.db"

EXPOSE 8000
EXPOSE 443
CMD ["python3", "main.py"]