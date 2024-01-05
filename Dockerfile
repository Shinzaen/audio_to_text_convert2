# 베이스 이미지를 선택합니다.
FROM python:3.8

# 애플리케이션 코드를 이미지에 추가합니다.
WORKDIR /app
COPY . /app

# 필요한 종속성을 설치합니다.
RUN pip install -r requirements.txt

# 애플리케이션을 실행합니다.
CMD ["python", "app.py"]
