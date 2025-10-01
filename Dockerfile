FROM node:20-alpine as frontend
RUN apk add git
RUN git clone https://github.com/koldun256/knowledge-fishing /frontend
WORKDIR /frontend
RUN npm install && npm run build



FROM python:3.12

RUN apt update && apt install -y git

RUN git clone https://github.com/shevnind/Knowledge-fishing /backend

WORKDIR /backend
# RUN chmod 777 requirements.txt
RUN pip install -r requirements.txt
# RUN ls -a

RUN mkdir build
COPY --from=frontend /frontend/build ./build

RUN mkdir -p ../data

EXPOSE 8000
CMD ["python3", "main.py"]
