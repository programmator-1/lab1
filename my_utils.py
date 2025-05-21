import numpy as np
from PIL import Image
import matplotlib.pyplot as plt


# Функция для обмена местами частей изображения
# в зависимости от выбора пользователя
def image_swap(name_in: str, name_out: str, choice: str):
    image_in = Image.open(name_in)
    image0 = np.array(image_in)

    image1 = image0.copy()

    if choice == 'Horizontal':
        width = image0.shape[1]
        half = width // 2
        image1[:, 0:half, :] = image0[:, half:width, :]
        image1[:, half:width, :] = image0[:, 0:half, :]
    elif choice == 'Vertical':
        height = image0.shape[0]
        half = height // 2
        image1[0:half, :, :] = image0[half:height, :, :]
        image1[half:height, :, :] = image0[0:half, :, :]

    image_out = Image.fromarray(image1)
    image_out.save(name_out)


# Функция для построения графика распределения цветов
def make_colors(name_in: str, name_out: str):
    image = Image.open(name_in)

    (width, height) = image.size
    size = width * height

    r = np.array(image.getchannel(0)).reshape((size,))
    g = np.array(image.getchannel(1)).reshape((size,))
    b = np.array(image.getchannel(2)).reshape((size,))

    r_hist = [0 for _ in range(256)]
    g_hist = [0 for _ in range(256)]
    b_hist = [0 for _ in range(256)]

    for pix in r:
        r_hist[pix] += 1

    for pix in g:
        g_hist[pix] += 1

    for pix in b:
        b_hist[pix] += 1

    plt.plot(r_hist, color="red")
    plt.plot(g_hist, color="green")
    plt.plot(b_hist, color="lue")
    plt.savefig(name_out)
    plt.close()
