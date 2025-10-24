FROM node:20-alpine as frontend
RUN apk add git
RUN git clone --depth 1 https://github.com/koldun256/knowledge-fishing /frontend
WORKDIR /frontend
RUN npm install && npm run build

FROM python:3.12

RUN apt update && apt install -y git

RUN git clone --depth 1 https://github.com/shevnind/Knowledge-fishing /backend

WORKDIR /backend

RUN pip install -r requirements.txt

RUN mkdir build
COPY --from=frontend /frontend/build ./build

COPY certificate.crt /backend/ssl/
COPY certificate_ca.crt /backend/ssl/
COPY certificate.key /backend/ssl/

EXPOSE 8000
EXPOSE 443
CMD ["python3", "main.py"]