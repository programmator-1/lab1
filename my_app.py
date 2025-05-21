"""
Вариант 8
Веб-приложение должно поменять местами правую и левую часть кар-
тинки либо верхнюю и нижнюю, в зависимости от желания пользователя, нари-
совать график распределения цветов исходной картинки.
"""

# Flask
from flask import Flask, render_template

# модули работы с формами и полями в формах
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import SubmitField, RadioField

# модули валидации полей формы
from wtforms.validators import InputRequired
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

    # Радио-кнопки для выбора направления
    choice = RadioField('Direction',
                        choices=[('Horizontal', 'Поменять местами левую и правую половины'),
                                 ('Vertical', 'Поменять местами верхнюю и нижнюю половины')],
                        validators=[InputRequired()])
    # поле формы с captcha
    recaptcha = RecaptchaField()
    # кнопка submit
    submit = SubmitField('Загрузить')


# модуль проверки и преобразование имени файла
# для устранения в имени символов типа / и т.д.
from werkzeug.utils import secure_filename

# подключаем наш модуль
import my_utils as utils


# метод обработки запроса GET и POST от клиента
@app.route("/", methods=['GET', 'POST'])
def swap():
    # создаем объект формы
    form = ImageForm()
    # обнуляем переменные, передаваемые в форму
    params = {'original': None, 'swapped': None, 'colors': None}

    # проверяем нажатие сабмит и валидацию введенных данных
    if form.validate_on_submit():
        filename = secure_filename(form.upload.data.filename)
        choice = form.choice.data
        # файлы с изображениями сохраняются в каталог static
        # переменные, передаваемые в форму, содержат
        # имена файлов в каталоге ./static
        ext = filename[filename.rindex("."):]
        params['original'] = './static/original' + ext
        params['swapped'] = './static/swapped' + ext
        params['colors'] = './static/colors.jpeg'
        # сохраняем загруженный файл
        form.upload.data.save(params['original'])

        # Swap image
        utils.image_swap(params['original'], params['swapped'], choice)
        # Make color distribution
        utils.make_colors(params['original'], params['colors'])

    # передаем форму в шаблон, так же передаем имя файлов,
    # если был нажат сабмит, либо передадим falsy значения
    return render_template('index.html', form=form, params=params)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080)
