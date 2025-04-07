
import math

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt


def transform_image(ifname: str, ofname: str, T: int, by_horizontal: bool):
    """
    Функция преобразования изображения
    :param ifname: название файла с исходным изображением
    :param ofname: название файла с новым изображением
    :param T: период функции, в пикселях
    :param by_horizontal: если True, то изменение происходит по горизонтали
    :return: нет
    """

    image_in = Image.open(ifname)

    image0 = np.array(image_in)
    image1 = image0.copy()

    w, h = image_in.width, image_in.height
    f = math.pi / T
    for i in range(h):
        for j in range(w):
            x = j if by_horizontal else i
            angle = (x % T) * f
            factor = math.sin(angle)
            image1[i][j] = image1[i][j] * factor

    image_out = Image.fromarray(image1)
    image_out.save(ofname)


def color_distribution(ifname: str, ofname: str):
    """
    Функция для построения графика распределения цветов
    :param ifname: название файла с исходным изображением
    :param ofname: название файла с графиком распределения цветов
    :return: нет
    """

    image = Image.open(ifname)

    (w, h) = image.size
    wh = w * h

    r = np.array(image.getchannel(0)).reshape((wh,))
    g = np.array(image.getchannel(1)).reshape((wh,))
    b = np.array(image.getchannel(2)).reshape((wh,))

    rdist = [0 for _ in range(256)]
    gdist = [0 for _ in range(256)]
    bdist = [0 for _ in range(256)]

    for p in r:
        rdist[p] += 1

    for p in g:
        gdist[p] += 1

    for p in b:
        bdist[p] += 1

    for i in range(256):
        rdist[i] /= (wh) * 100
        gdist[i] /= (wh) * 100
        bdist[i] /= (wh) * 100

    plt.plot(rdist, color="red")
    plt.plot(gdist, color="green")
    plt.plot(bdist, color="blue")
    plt.savefig(ofname)
    plt.close()
