from typing import Tuple

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# Преобразование одной полосы
def transform_one(img0: np.ndarray, img1: np.ndarray, sz: int, rect: Tuple[int, int, int, int]):
    x0, y0 = rect[0], rect[1]
    w, h = rect[2], rect[3]

    xs, ys = w // sz, h // sz

    # horizontal shift
    for i in range(0, xs - 1):
        x1 = x0 + i * sz
        x2 = x1 + sz
        x3 = x2 + sz

        # top
        img1[y0:y0 + sz, x2:x3] = img0[y0:y0 + sz, x1:x2]
        # bottom
        img1[h - sz:h, x1:x2] = img0[h - sz:h, x2:x3]

    # vertical shift
    for i in range(0, ys - 1):
        y1 = y0 + i * sz
        y2 = y1 + sz
        y3 = y2 + sz

        # left
        img1[y1:y2, x0:x0 + sz] = img0[y2:y3, x0:x0 + sz]
        # right
        img1[y2:y3, w - sz:w] = img0[y1:y2, w - sz:w]


# Преобразование всего изображения
def transform(img0: np.ndarray, sz: int):
    img1 = img0.copy()

    x, y = 0, 0
    h, w, _ = img0.shape
    w, h = w // sz * sz, h // sz * sz

    while w > sz and h > sz:
        transform_one(img0, img1, sz, (x, y, w, h))
        w, h = w - 2 * sz, h - 2 * sz
        x, y = x + sz, y + sz

    return img1


# Преобразование изображения из файла и запись результата в файл
def process_image(ifname: str, ofname: str, size: int):
    img0 = np.array(Image.open(ifname, formats=["JPEG"]))
    img1 = transform(img0, size)
    Image.fromarray(img1).save(ofname, format="JPEG")


# Создание графика распределения цветов
def create_color_distribution_graph(ifname: str, ofname: str):
    img0 = np.array(Image.open(ifname, formats=["JPEG"]))
    h, w, _ = img0.shape

    # Calculate color distributions

    # Следующие массивы будут использоваться для
    # подсчета пикселей определенного цвета во
    # всем изображении
    r = [0 for _ in range(0, 256)]  # красный
    g = [0 for _ in range(0, 256)]  # зеленый
    b = [0 for _ in range(0, 256)]  # синий

    # подсчет пикселей
    for i in range(0, h):
        for j in range(0, w):
            p = img0[i][j]
            r[p[0]] += 1
            g[p[1]] += 1
            b[p[2]] += 1

    # построение графика и сохранение в файл
    plt.plot(r, color="red")
    plt.plot(g, color="green")
    plt.plot(b, color="blue")
    plt.savefig(ofname, format="JPEG")
    plt.close()

