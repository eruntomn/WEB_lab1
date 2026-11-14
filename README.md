# Лабораторная работа 1. Настройка окружения и первый HTTP-сервер
Выполнила: 03_МОАИС_рбд2 Сергеева Виталия Викторовна 

## Ход работы

Я создала репозиторий в GitHub Desktop, открыла его в VS Code и создала виртуальное окружение с установкой Flask:

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install flask
pip freeze > requirements.txt
```

При установке Flask возникла ошибка `SSL: CERTIFICATE_VERIFY_FAILED`. Я решила её установкой с параметрами `--trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org`.


Сервер написан на Flask (`app.py`) и имеет три маршрута: `/` (приветствие), `/info` (метод, путь и заголовки запроса в JSON) и `/echo` (POST, возвращает присланный JSON с кодом 201).

```python
import os
from flask import Flask, request, jsonify

app = Flask(__name__)
APP_NAME = os.getenv("APP_NAME", "local")

@app.route("/")
def index():
    return f"Hello from {APP_NAME}!"

@app.route("/info")
def info():
    return jsonify({
        "method": request.method,
        "path": request.path,
        "headers": dict(request.headers),
    })

@app.route("/echo", methods=["POST"])
def echo():
    return jsonify({"you_sent": request.get_json(silent=True)}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

Адрес `0.0.0.0` нужен, чтобы сервер был доступен снаружи контейнера. Если указать `127.0.0.1`, он будет слушать только внутри самого контейнера.

Запрос `GET /info` в браузере (DevTools, вкладка Network):

![img1](img1.png)

![img2](img2.png)

Статус `200 OK`, тип ответа `application/json`, сервер `Werkzeug/3.1.9 Python/3.11.9`. Во вкладке Response видно тело ответа в JSON.

![img3](img3.png)

В запросе стартовая строка `GET /info HTTP/1.1`, заголовки (`Host`, `User-Agent`, `Accept`) и пустая строка. В ответе строка статуса `HTTP/1.1 200 OK`, заголовки (`Content-Type`, `Content-Length`, `Server`, `Date`) и тело в JSON.

Запрос к несуществующему адресу `/nothing`:

![img4](img4.png)

Сервер вернул `404 NOT FOUND` и HTML-страницу с ошибкой.

POST-запрос на `/echo` с JSON в теле:

![img5](img5.png)

Dockerfile:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

Сначала копируется только `requirements.txt` и устанавливаются зависимости, а потом копируется код. Образ собран командой `docker build -t web-lab1 .`:

![img12](img12.png)

```yaml
services:
  web:
    build: .
    container_name: web-lab1
    ports:
      - "5000:5000"
    environment:
      - APP_NAME=web-lab1
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

`ports: "5000:5000"` пробрасывает порт хоста в порт контейнера, `environment` задаёт переменную окружения, `volumes` подключает папку хоста к контейнеру. Запуск командой `docker compose up -d --build`:

![img6](img6.png)

![img7](img7.png)

Образ собран (слои взяты из кэша), создана сеть и запущен контейнер `web-lab1`. Приложение открывается на `http://localhost:5000`.

Состояние контейнера (`docker compose ps`): статус `Up`, порты `0.0.0.0:5000->5000/tcp`.

![img8](img8.png)

Логи (`docker compose logs`): сервер запущен на `0.0.0.0:5000`.

![img9](img9.png)

Логи в реальном времени (`docker compose logs -f web`): после обращения к странице в логе появилась строка `"GET / HTTP/1.1" 200`.

![img10](img10.png)

Использование ресурсов (`docker stats`):

![img11](img11.png)


