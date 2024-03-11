# Flask
from flask import Flask, render_template

# модули работы с формами и полями в формах
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import SubmitField, BooleanField, IntegerField

# модули валидации полей формы
from wtforms.validators import NumberRange
from flask_wtf.file import FileField, FileAllowed, FileRequired
# обязательно добавить для работы со стандартными шаблонами
from flask_bootstrap import Bootstrap

# Flask app
app = Flask(__name__)

# используем csrf токен, можете генерировать его сами
SECRET_KEY = 'secret'
app.config['SECRET_KEY'] = SECRET_KEY
# используем капчу и полученные секретные ключи с сайта Google
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LcE15MpAAAAALdaTdqDf2w3EcZGCUqpNgA6EjX5'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LcE15MpAAAAAIXMEr6N_q-Qs3Lzr_zbQDP3vPGT'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}

bootstrap = Bootstrap(app)


# создаем форму для загрузки файла
class ImageForm(FlaskForm):
    # поле загрузки файла
    # здесь валидатор укажет ввести правильные файлы
    upload = FileField('Load image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    # Чекбоксы для выбора направления
    horizontal = BooleanField('Horizontal')
    vertical = BooleanField('Vertical')
    # Поле для ввода размера полосы,
    # валидатор допускает только значения из диапазона [1..1000]
    size = IntegerField('Size', default=10, validators=[NumberRange(min=1, max=1000)])
    # поле формы с captcha
    recaptcha = RecaptchaField()
    # кнопка submit, для пользователя отображена как send
    submit = SubmitField('Upload')


# функция обработки запросов на адрес /alt
# модуль проверки и преобразование имени файла
# для устранения в имени символов типа / и т.д.
from werkzeug.utils import secure_filename

# подключаем наш модуль
import img_utils as utils


# метод обработки запроса GET и POST от клиента
@app.route("/alt", methods=['GET', 'POST'])
def alt():
    # создаем объект формы
    form = ImageForm()
    # обнуляем переменные, передаваемые в форму
    params = {'orig': None, 'alt': None, 'distr': None}

    # проверяем нажатие сабмит и валидацию введенных данных
    if form.validate_on_submit():
        # файлы с изображениями сохраняются в каталог static
        fname = secure_filename(form.upload.data.filename)
        ext = fname[fname.rindex("."):]
        # переменные, передаваемые в форму, содержат
        # имена файлов в каталоге ./static
        params['orig'] = './static/orig' + ext
        params['alt'] = './static/alt' + ext
        params['distr'] = './static/distr.jpeg'
        # сохраняем загруженный файл
        form.upload.data.save(params['orig'])

        # Alternate
        utils.img_alt(params['orig'], params['alt'], form.size.data, form.horizontal.data, form.vertical.data)
        # Distribution
        utils.make_distr(params['orig'], params['distr'])

    # передаем форму в шаблон, так же передаем имя файлов,
    # если был нажат сабмит, либо передадим falsy значения
    return render_template('alt.html', form=form, params=params)


# декоратор для вывода страницы по умолчанию
@app.route("/")
def hello():
    # создаем переменные с данными для передачи в шаблон
    some_pars = {'color': 'red'}
    body = 'Hello my dear friends!'
    # передаем данные в шаблон и вызываем его
    return render_template('index.html', body=body, some_pars=some_pars)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080)
