FROM python:3.8

COPY . /app

WORKDIR /app

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

