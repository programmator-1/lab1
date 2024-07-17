import hashlib, io
import os

import uvicorn
from PIL import Image
from fastapi import Form, File, UploadFile
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from fastapi.middleware.wsgi import WSGIMiddleware
from flask import Flask, render_template
# модули работы с формами и полями в формах
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import SubmitField, BooleanField, IntegerField
# модули валидации полей формы
from wtforms.validators import NumberRange
from flask_wtf.file import FileField, FileAllowed, FileRequired
# обязательно добавить для работы со стандартными шаблонами
from flask_bootstrap import Bootstrap
# Функции из модуля обработки изображений
from image_processing import process_image, create_color_distribution_graph
from werkzeug.utils import secure_filename

# Приложение Flask
flask_app = Flask(__name__)
# Приложение FastAPI
app = FastAPI()
# Bootstrap
bootstrap = Bootstrap(flask_app)

# используем csrf токен
SECRET_KEY = 'secret'
flask_app.config['SECRET_KEY'] = SECRET_KEY
# используем капчу и полученные секретные ключи с сайта Google
flask_app.config['RECAPTCHA_USE_SSL'] = False
flask_app.config['RECAPTCHA_PUBLIC_KEY'] = '6Ldn7xEqAAAAAJQ3CdItS8AUZiUCqJ1PDGhihcdW'
flask_app.config['RECAPTCHA_PRIVATE_KEY'] = '6Ldn7xEqAAAAAHimzM0R6aQoGHqzOQd38yWr8MYQ'
flask_app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}

# Приложение Flask будет запускаться поверх FastAPI
app.mount("/v1", WSGIMiddleware(flask_app))

# Директория для статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/v2/static", StaticFiles(directory="static"), name="static")
# Директория для шаблонов
templates = Jinja2Templates(directory="templates")


# создаем форму для загрузки файла
class ImageForm(FlaskForm):
    # поле загрузки файла
    # здесь валидатор укажет ввести правильные файлы
    file = FileField('Загрузить изображение', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Только изображения!')])
    # Поле для ввода размера полосы,
    # валидатор допускает только значения из диапазона [1..1000]
    size = IntegerField('Размер сдвига:', default=8, validators=[NumberRange(min=1, max=256)])
    # поле формы с captcha
    recaptcha = RecaptchaField()
    # кнопка submit, для пользователя отображена как send
    submit = SubmitField('Загрузить')


def make_filenames(filename, images):
    filebase = Path(filename).stem
    fileext = Path(filename).suffix
    #  преобразуем имена файлов в хеш-строку
    images.append("static/" + hashlib.sha256((filebase + fileext).encode('utf-8')).hexdigest())
    images.append("static/" + hashlib.sha256((filebase + "_trans" + fileext).encode('utf-8')).hexdigest())
    images.append("static/" + hashlib.sha256((filebase + "_distr" + fileext).encode('utf-8')).hexdigest())


############### v1 - Flask ###############

@flask_app.route("/")
def index():
    return render_template('index.html')


# метод обработки запроса GET и POST от клиента
@flask_app.route("/image_form", methods=['GET', 'POST'])
def image_form():
    # создаем объект формы
    form = ImageForm()
    # обнуляем переменные, передаваемые в форму
    images = []
    ready = False

    # проверяем нажатие сабмит и валидацию введенных данных
    if form.validate_on_submit():
        ready = True
        filename = secure_filename(form.file.data.filename)
        make_filenames(filename, images)
        # сохраняем изображения в папке static
        temp_name = "static/" + hashlib.sha256(filename.encode('utf-8')).hexdigest() + Path(filename).suffix
        form.file.data.save(temp_name)
        p_image = Image.open(temp_name).convert("RGB")
        os.remove(temp_name)
        # оригинал
        p_image.save(images[0], 'JPEG')
        # трансформированное изображение
        process_image(images[0], images[1], form.size.data)
        # график распределения цветов
        create_color_distribution_graph(images[0], images[2])

    # передаем форму в шаблон, так же передаем имя файлов,
    # если был нажат сабмит, либо передадим falsy значения
    return render_template('image_form.html', form=form, images=images, ready=ready)


############### v2 - FastAPI ###############

@app.get("/v2", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index_v2.html", {"request": request})


@app.get("/v2/image_form", response_class=HTMLResponse)
async def image_form(request: Request):
    return templates.TemplateResponse("image_form_v2.html", {"request": request, "size": 8})


@app.post("/v2/image_form", response_class=HTMLResponse)
async def image_form(request: Request,
                     sz: int = Form(),
                     file: UploadFile = File()):
    ready = False
    images = []

    if file and len(file.filename):
        ready = True
        filename = file.filename
        make_filenames(filename, images)
        # берем содержимое файлов
        content = await file.read()
        p_image = Image.open(io.BytesIO(content)).convert("RGB")
        # сохраняем изображения в папке static
        # оригинал
        p_image.save(images[0], 'JPEG')
        # трансформированное изображение
        process_image(images[0], images[1], sz)
        # график распределения цветов
        create_color_distribution_graph(images[0], images[2])

    # возвращаем html с параметрами-ссылками на изображения, которые позже будут
    # извлечены браузером запросами get по указанным ссылкам в img src
    return templates.TemplateResponse("image_form_v2.html", {"request": request,
                                                             "ready": ready, "images": images,
                                                             "size": sz})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)