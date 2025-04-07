# Flask
from flask import Flask, render_template

# модули работы с формами и полями в формах
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import SubmitField, IntegerField, BooleanField

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
    # Поле загрузки файла
    upload = FileField('Выбор изображения', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    # Поле для ввода периода функции
    period = IntegerField('Период', default=100, validators=[NumberRange(min=1, max=10000)])
    # Чек-боксы для выбора направления изменения
    horizontal = BooleanField('По горизонтали')
    vertical = BooleanField('По вертикали')
    # поле формы с captcha
    recaptcha = RecaptchaField()
    # кнопка submit, для пользователя отображена как 'Загрузить'
    submit = SubmitField('Загрузить')


# модуль проверки и преобразование имени файла
# для устранения в имени символов типа / и т.д.
from werkzeug.utils import secure_filename

# подключаем наш модуль
import mymod


# метод обработки запроса GET и POST от клиента
@app.route("/trans", methods=['GET', 'POST'])
def alt():
    # создаем объект формы
    form = ImageForm()
    # обнуляем переменные, передаваемые в форму
    params = {'orig': None, 'trans': None, 'distr': None}

    # проверяем нажатие сабмит и валидацию введенных данных
    if form.validate_on_submit():
        # файлы с изображениями сохраняются в каталог static
        filename = secure_filename(form.upload.data.filename)
        ext = filename[filename.rindex("."):]
        # переменные, передаваемые в форму, содержат
        # имена трех файлов - оригинального изображения,
        # преобразованного изображения и изображения с
        # распределением цветов
        params['orig'] = './static/orig' + ext
        params['trans'] = './static/trans' + ext
        params['orig_distr'] = './static/orig_distr.jpeg'
        params['trans_distr'] = './static/trans_distr.jpeg'
        # сохраняем загруженный файл
        form.upload.data.save(params['orig'])

        # Преобразовываем изображение в соответствии с заданием
        T = form.period.data # период функции
        by_horizontal = form.horizontal.data # изменения по горизонтали или вертикали
        mymod.transform_image(params['orig'], params['trans'], T, by_horizontal)
        # Получаем распределение цветов
        mymod.color_distribution(params['orig'], params['orig_distr'])
        mymod.color_distribution(params['trans'], params['trans_distr'])

    # передаем форму в шаблон, так же передаем имя файлов,
    # если был нажат сабмит, либо передадим falsy значения
    return render_template('trans.html', form=form, params=params)


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
