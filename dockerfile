FROM python:3.9

RUN adduser --disabled-password --gecos '' ml-api-user

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /opt/mlops_webapp
COPY . .

WORKDIR /opt/
RUN git clone https://github.com/PetrDoroshev/MlOpsProject.git

WORKDIR /opt/mlops_webapp

RUN pip install --upgrade pip
RUN pip install -r requirements/requirements.txt

ENV PYTHONPATH="/opt/MlOpsProject:"

RUN chown -R ml-api-user /opt/mlops_webapp/uploaded_files

USER ml-api-user

EXPOSE 8000

CMD ["bash", "./run.sh"]
