FROM python:3.12

WORKDIR /code

COPY requirement.txt .

RUN pip install -r requirement.txt

COPY . .

CMD [ "python", "gcexporter.py" ]
