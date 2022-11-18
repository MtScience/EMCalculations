"""
Модуль, содержащий описания характеристик свойств электротехнических сталей.

Классы:

* ``Steel``

  Базовый класс, служащий основой для остальных классов.

* ``Steel2414Along``

  Сталь 2412/2414 вдоль проката.

* ``Steel2414Across``

  Сталь 2412/2414 поперёк проката.

* ``Steel2414Mean``

  Сталь 2412/2414 усреднённая.

* ``Steel3414Along``

  Сталь 3412/3414 вдоль проката.

* ``Steel3414Across``

  Сталь 3412/3414 поперёк проката.

* ``M27050AAlong``

  Сталь М270-50А вдоль проката.

* ``M27050AAcross``

  Сталь М270-50А поперёк проката.

* ``M27050AMean``

  Сталь М270-50А усреднённая.

* ``M33050AAlong``

  Сталь М330-50А вдоль проката.

* ``M33050AAcross``

  Сталь М330-50А поперёк проката.

* ``M33050AMean``

  Сталь М330-50А усреднённая.

* ``M40050AAlong``

  Сталь М4000-50А вдоль проката.

* ``M40050AAcross``

  Сталь М400-50А поперёк проката.

* ``M40050AMean``

  Сталь М400-50А усреднённая.

* ``Steel35HN3MFARotor``

  Роторная сталь 35ХН3МФА.
"""


from abc import ABC, abstractmethod
from typing import List
from scipy import interpolate
from numpy import arange


class Steel(ABC):
    __slots__ = ["B",
                 "H",
                 "BH_curve",
                 "B_loss",
                 "W_loss",
                 "losses_curve"
                 ]

    # Стали также "одиночки", для экономии памяти
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @abstractmethod
    def __init__(self) -> None:
        # self.B - список, содержащий значения индукции, self.H - список, содержащий соответствующие значения
        # напряжённости магнитного поля
        pass

    def _create_BH_curve(self) -> None:
        # Вообще, тут бы убрать экстраполяцию, заменив её на нормальные характеристики сталей, но пока что имеем что
        # имеем
        self.BH_curve = interpolate.interp1d(self.B, self.H, kind="quadratic", fill_value="extrapolate")

    def _create_losses_curve(self) -> None:
        # А вот тут без экстраполяции никак. И хотя я, вообще-то, не особо люблю линейные интерполяции (а уж
        # экстраполяции особенно), но тут это самый лучший вариант, потому что для большинства имеющихся сталей
        # наблюдается своего рода насыщение, когда с ростом индукции скорость возрастания потерь падает (а не растёт,
        # как было бы в случае классической формулы с квадратичным ростом). И тут, видимо, должна быть асимптота, но
        # посчитать её я не могу в силу отсутствия формул. В таком случае линейный экстраполянт даст ошибку, но она
        # будет меньше, чем ошибка квадратичной функции или любого из стандартных способов интер-/эктраполяции. При этом
        # же некоторые стали ведут себя наоборот - у них скорость возрастания потерь растёт. Но тогда в разумных
        # пределах линейный экстаполянт пойдёт выше, чем квадратичная функция, что тоже будет точнее.
        #
        # А вообще убил бы - все же знают, что индукция в машине может достигать 2.5 Тл - не-е-ет, чёрт побери, мы
        # померим до 1.8, а там делайте что хотите. У-у-уЪ!
        self.losses_curve = interpolate.interp1d(self.B_loss, self.W_loss, kind="linear", fill_value="extrapolate")


# А вот для 3414 пришлось сделать ручками, потому как полных данных по не у меня нет и не особо предвидится
class Steel3414Along(Steel):
    def __init__(self) -> None:
        self.B: List[float]
        self.B = [0.6, 0.605, 0.61, 0.615, 0.62, 0.625, 0.63, 0.635, 0.64, 0.645, 0.65, 0.655, 0.66, 0.665, 0.67, 0.675,
                  0.68, 0.685, 0.69, 0.695, 0.7, 0.705, 0.71, 0.715, 0.72, 0.725, 0.73, 0.735, 0.74, 0.745, 0.75, 0.755,
                  0.76, 0.765, 0.77, 0.775, 0.78, 0.785, 0.79, 0.795, 0.8, 0.805, 0.81, 0.815, 0.82, 0.825, 0.83, 0.835,
                  0.84, 0.845, 0.85, 0.855, 0.86, 0.865, 0.87, 0.875, 0.88, 0.885, 0.89, 0.895, 0.9, 0.905, 0.91, 0.915,
                  0.92, 0.925, 0.93, 0.935, 0.94, 0.945, 0.95, 0.955, 0.96, 0.965, 0.97, 0.975, 0.98, 0.985, 0.99,
                  0.995, 1, 1.005, 1.01, 1.015, 1.02, 1.025, 1.03, 1.035, 1.04, 1.045, 1.05, 1.055, 1.06, 1.065, 1.07,
                  1.075, 1.08, 1.085, 1.09, 1.095, 1.1, 1.105, 1.11, 1.115, 1.12, 1.125, 1.13, 1.135, 1.14, 1.145, 1.15,
                  1.155, 1.16, 1.165, 1.17, 1.175, 1.18, 1.185, 1.19, 1.195, 1.2, 1.205, 1.21, 1.215, 1.22, 1.225, 1.23,
                  1.235, 1.24, 1.245, 1.25, 1.255, 1.26, 1.265, 1.27, 1.275, 1.28, 1.285, 1.29, 1.295, 1.3, 1.305, 1.31,
                  1.315, 1.32, 1.325, 1.33, 1.335, 1.34, 1.345, 1.35, 1.355, 1.36, 1.365, 1.37, 1.375, 1.38, 1.385,
                  1.39, 1.395, 1.4, 1.405, 1.41, 1.415, 1.42, 1.425, 1.43, 1.435, 1.44, 1.445, 1.45, 1.455, 1.46, 1.465,
                  1.47, 1.475, 1.48, 1.485, 1.49, 1.495, 1.5, 1.505, 1.51, 1.515, 1.52, 1.525, 1.53, 1.535, 1.54, 1.545,
                  1.55, 1.555, 1.56, 1.565, 1.57, 1.575, 1.58, 1.585, 1.59, 1.595, 1.6, 1.605, 1.61, 1.615, 1.62, 1.625,
                  1.63, 1.635, 1.64, 1.645, 1.65, 1.655, 1.66, 1.665, 1.67, 1.675, 1.68, 1.685, 1.69, 1.695, 1.7, 1.705,
                  1.71, 1.715, 1.72, 1.725, 1.73, 1.735, 1.74, 1.745, 1.75, 1.755, 1.76, 1.765, 1.77, 1.775, 1.78,
                  1.785, 1.79, 1.795, 1.8, 1.805, 1.81, 1.815, 1.82, 1.825, 1.83, 1.835, 1.84, 1.845, 1.85, 1.855, 1.86,
                  1.865, 1.87, 1.875, 1.88, 1.885, 1.89, 1.895, 1.9, 1.905, 1.91, 1.915, 1.92, 1.925, 1.93, 1.935, 1.94,
                  1.945, 1.95, 1.955, 1.96, 1.965, 1.97, 1.975, 1.98, 1.985, 1.99, 1.995, 2]
        self.H: List[float]
        self.H = [0.81, 0.82, 0.83, 0.84, 0.85, 0.86, 0.87, 0.88, 0.89, 0.9, 0.91, 0.93, 0.95, 0.97, 0.99, 1.01, 1.02,
                  1.04, 1.06, 1.08, 1.1, 1.11, 1.12, 1.13, 1.14, 1.15, 1.16, 1.17, 1.18, 1.19, 1.2, 1.21, 1.22, 1.23,
                  1.24, 1.25, 1.26, 1.27, 1.28, 1.29, 1.3, 1.31, 1.32, 1.33, 1.34, 1.35, 1.36, 1.37, 1.38, 1.39, 1.4,
                  1.41, 1.42, 1.44, 1.45, 1.46, 1.47, 1.49, 1.5, 1.51, 1.52, 1.54, 1.55, 1.57, 1.58, 1.6, 1.61, 1.63,
                  1.64, 1.66, 1.67, 1.69, 1.7, 1.72, 1.73, 1.75, 1.76, 1.78, 1.79, 1.81, 1.82, 1.84, 1.85, 1.87, 1.88,
                  1.9, 1.92, 1.94, 1.95, 1.97, 1.98, 2, 2.01, 2.03, 2.04, 2.06, 2.07, 2.09, 2.1, 2.12, 2.13, 2.15, 2.16,
                  2.18, 2.19, 2.21, 2.22, 2.24, 2.25, 2.27, 2.28, 2.3, 2.31, 2.33, 2.34, 2.36, 2.37, 2.39, 2.4, 2.42,
                  2.43, 2.45, 2.46, 2.48, 2.49, 2.51, 2.52, 2.54, 2.55, 2.57, 2.58, 2.6, 2.61, 2.63, 2.65, 2.67, 2.68,
                  2.7, 2.72, 2.74, 2.75, 2.77, 2.79, 2.81, 2.83, 2.85, 2.87, 2.89, 2.91, 2.93, 2.95, 2.98, 3, 3.03,
                  3.05, 3.08, 3.1, 3.13, 3.15, 3.18, 3.2, 3.23, 3.26, 3.29, 3.32, 3.35, 3.38, 3.41, 3.44, 3.47, 3.5,
                  3.54, 3.58, 3.62, 3.66, 3.7, 3.74, 3.78, 3.82, 3.86, 3.9, 3.96, 4.02, 4.08, 4.14, 4.2, 4.26, 4.32,
                  4.38, 4.44, 4.5, 4.57, 4.64, 4.71, 4.78, 4.85, 4.92, 4.99, 5.06, 5.13, 5.2, 5.31, 5.42, 5.54, 5.65,
                  5.76, 5.87, 5.98, 6.1, 6.21, 6.32, 6.49, 6.66, 6.83, 6.99, 7.16, 7.33, 7.49, 7.66, 7.88, 8, 8.24,
                  8.48, 8.72, 8.96, 9.2, 9.44, 9.68, 9.92, 10.16, 10.4, 10.86, 11.32, 11.78, 12.24, 12.7, 13.16, 13.62,
                  14.08, 14.54, 15, 15.87, 16.73, 17.6, 18.46, 19.33, 20.2, 21.07, 21.93, 22.8, 23.66, 25.12, 26.58,
                  28.04, 29.5, 30.96, 32.41, 33.87, 35.33, 36.79, 38.25, 41.43, 44.6, 47.78, 50.95, 54.13, 57.3, 60.48,
                  63.65, 66.83, 70, 79, 88, 97, 106, 115, 124, 133, 142, 151, 160]
        self._create_BH_curve()

        self.B_loss: List[float]
        B_loss = arange(0, 1.8, 0.1)
        self.B_loss = list(B_loss)
        self.W_loss: List[float]
        self.W_loss = list(1.5 * B_loss ** 2 / 2.25)
        self._create_losses_curve()

    def __str__(self) -> str:
        return "Сталь 3414 (вдоль проката)"


class Steel3414Across(Steel):
    def __init__(self) -> None:
        self.B: List[float]
        self.B = [0.2, 0.205, 0.21, 0.215, 0.22, 0.225, 0.23, 0.235, 0.24, 0.245, 0.25, 0.255, 0.26, 0.265, 0.27, 0.275,
                  0.28, 0.285, 0.29, 0.295, 0.3, 0.305, 0.31, 0.315, 0.32, 0.325, 0.33, 0.335, 0.34, 0.345, 0.35, 0.355,
                  0.36, 0.365, 0.37, 0.375, 0.38, 0.385, 0.39, 0.395, 0.4, 0.405, 0.41, 0.415, 0.42, 0.425, 0.43, 0.435,
                  0.44, 0.445, 0.45, 0.455, 0.46, 0.465, 0.47, 0.475, 0.48, 0.485, 0.49, 0.495, 0.5, 0.505, 0.51, 0.515,
                  0.52, 0.525, 0.53, 0.535, 0.54, 0.545, 0.55, 0.555, 0.56, 0.565, 0.57, 0.575, 0.58, 0.585, 0.59,
                  0.595, 0.6, 0.605, 0.61, 0.615, 0.62, 0.625, 0.63, 0.635, 0.64, 0.645, 0.65, 0.655, 0.66, 0.665, 0.67,
                  0.675, 0.68, 0.685, 0.69, 0.695, 0.7, 0.705, 0.71, 0.715, 0.72, 0.725, 0.73, 0.735, 0.74, 0.745, 0.75,
                  0.755, 0.76, 0.765, 0.77, 0.775, 0.78, 0.785, 0.79, 0.795, 0.8, 0.805, 0.81, 0.815, 0.82, 0.825, 0.83,
                  0.835, 0.84, 0.845, 0.85, 0.855, 0.86, 0.865, 0.87, 0.875, 0.88, 0.885, 0.89, 0.895, 0.9, 0.905, 0.91,
                  0.915, 0.92, 0.925, 0.93, 0.935, 0.94, 0.945, 0.95, 0.955, 0.96, 0.965, 0.97, 0.975, 0.98, 0.985,
                  0.99, 0.995, 1, 1.005, 1.01, 1.015, 1.02, 1.025, 1.03, 1.035, 1.04, 1.045, 1.05, 1.055, 1.06, 1.065,
                  1.07, 1.075, 1.08, 1.085, 1.09, 1.095, 1.1, 1.105, 1.11, 1.115, 1.12, 1.125, 1.13, 1.135, 1.14, 1.145,
                  1.15, 1.155, 1.16, 1.165, 1.17, 1.175, 1.18, 1.185, 1.19, 1.195, 1.2, 1.205, 1.21, 1.215, 1.22, 1.225,
                  1.23, 1.235, 1.24, 1.245, 1.25, 1.255, 1.26, 1.265, 1.27, 1.275, 1.28, 1.285, 1.29, 1.295, 1.3, 1.305,
                  1.31, 1.315, 1.32, 1.325, 1.33, 1.335, 1.34, 1.345, 1.35, 1.355, 1.36, 1.365, 1.37, 1.375, 1.38,
                  1.385, 1.39, 1.395, 1.4, 1.405, 1.41, 1.415, 1.42, 1.425, 1.43, 1.435, 1.44, 1.445, 1.45, 1.455, 1.46,
                  1.465, 1.47, 1.475, 1.48, 1.485, 1.49, 1.495, 1.5, 1.505, 1.51, 1.515, 1.52, 1.525, 1.53, 1.535, 1.54,
                  1.545, 1.55, 1.555, 1.56, 1.565, 1.57, 1.575, 1.58, 1.585, 1.59, 1.595, 1.6, 1.605, 1.61, 1.615, 1.62,
                  1.625, 1.63, 1.635, 1.64, 1.645, 1.65, 1.655, 1.66, 1.665, 1.67, 1.675, 1.68, 1.685, 1.69, 1.695, 1.7,
                  1.705, 1.71, 1.715, 1.72, 1.725, 1.73, 1.735, 1.74, 1.745, 1.75, 1.755, 1.76, 1.765, 1.77, 1.775,
                  1.78, 1.785, 1.79, 1.795, 1.8, 1.805, 1.81, 1.815, 1.82, 1.825, 1.83, 1.835, 1.84, 1.845, 1.85, 1.855,
                  1.86, 1.865, 1.87, 1.875, 1.88, 1.885, 1.89, 1.895]
        self.H: List[float]
        self.H = [0.4, 0.41, 0.42, 0.43, 0.44, 0.45, 0.46, 0.47, 0.48, 0.49, 0.5, 0.51, 0.52, 0.53, 0.54, 0.55, 0.56,
                  0.57, 0.58, 0.59, 0.6, 0.61, 0.62, 0.63, 0.64, 0.65, 0.66, 0.67, 0.68, 0.69, 0.7, 0.71, 0.72, 0.73,
                  0.74, 0.75, 0.76, 0.77, 0.78, 0.79, 0.8, 0.81, 0.82, 0.83, 0.84, 0.85, 0.86, 0.87, 0.88, 0.89, 0.9,
                  0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99, 1, 1.01, 1.02, 1.03, 1.04, 1.05, 1.06, 1.07,
                  1.08, 1.09, 1.1, 1.11, 1.12, 1.13, 1.14, 1.15, 1.16, 1.17, 1.18, 1.19, 1.2, 1.21, 1.22, 1.23, 1.24,
                  1.25, 1.26, 1.27, 1.28, 1.29, 1.3, 1.31, 1.32, 1.33, 1.34, 1.35, 1.36, 1.37, 1.38, 1.39, 1.4, 1.41,
                  1.42, 1.44, 1.45, 1.46, 1.47, 1.49, 1.5, 1.51, 1.52, 1.54, 1.55, 1.57, 1.58, 1.6, 1.62, 1.64, 1.65,
                  1.67, 1.68, 1.7, 1.72, 1.74, 1.76, 1.78, 1.8, 1.82, 1.84, 1.86, 1.88, 1.9, 1.92, 1.95, 1.97, 1.99,
                  2.01, 2.04, 2.06, 2.08, 2.1, 2.13, 2.15, 2.18, 2.2, 2.23, 2.25, 2.28, 2.3, 2.33, 2.35, 2.38, 2.4,
                  2.43, 2.45, 2.48, 2.5, 2.53, 2.55, 2.58, 2.6, 2.63, 2.66, 2.69, 2.72, 2.75, 2.78, 2.81, 2.84, 2.87,
                  2.9, 2.95, 3, 3.05, 3.1, 3.15, 3.2, 3.25, 3.3, 3.35, 3.4, 3.46, 3.51, 3.57, 3.62, 3.68, 3.73, 3.79,
                  3.84, 3.9, 3.95, 4.03, 4.1, 4.18, 4.25, 4.33, 4.4, 4.48, 4.55, 4.63, 4.7, 4.82, 4.94, 5.06, 5.18, 5.3,
                  5.42, 5.54, 5.66, 5.78, 5.9, 6.08, 6.26, 6.44, 6.62, 6.8, 6.98, 7.16, 7.34, 7.52, 7.7, 8, 8.3, 8.6,
                  8.9, 9.2, 9.5, 9.8, 10.1, 10.4, 10.7, 11.33, 11.96, 12.59, 13.22, 13.85, 14.48, 15.11, 15.74, 16.37,
                  17, 18.05, 19.1, 20.15, 21.2, 22.25, 23.3, 24.35, 25.4, 26.45, 27.5, 28.75, 30, 31.25, 32.5, 33.75,
                  35, 36.25, 37.5, 38.75, 40, 41.4, 42.8, 44.2, 45.6, 47, 48.4, 49.8, 51.2, 52.6, 54, 55.5, 57, 58.5,
                  60, 61.5, 63, 64.5, 66, 67.5, 69, 70.9, 72.8, 74.7, 76.6, 78.5, 80.4, 82.3, 84.2, 86.1, 88, 90.3,
                  92.6, 94.9, 97.2, 99.5, 101.8, 104.1, 106.4, 108.7, 111, 113.7, 116.4, 119.1, 121.8, 124.5, 127.2,
                  129.9, 132.6, 135.3, 138, 142, 146, 150, 154, 158, 162, 166, 170, 174, 178, 184.7, 191.4, 198.1,
                  204.8, 211.5, 218.2, 224.9, 231.6, 238.3, 245, 254.5, 264, 273.5, 283, 292.5, 302, 311.5, 321, 331]
        self._create_BH_curve()

        self.B_loss: List[float]
        B_loss = arange(0, 1.8, 0.1)
        self.B_loss = list(B_loss)
        self.W_loss: List[float]
        self.W_loss = list(3.4 * B_loss ** 2 / 2.25)
        self._create_losses_curve()

    def __str__(self) -> str:
        return "Сталь 3414 (поперёк проката)"


class Steel2414Along(Steel):
    def __init__(self) -> None:
        self.B: List[float]
        self.B = [0, 0.007743300, 0.011623000, 0.016016999, 0.021189000, 0.026881000, 0.032825001, 0.040831000,
                  0.048331998, 0.171709999, 0.396829993, 0.673969984, 0.868489981, 0.963919997, 1.027799964,
                  1.075299978, 1.112699986, 1.144000053, 1.291800022, 1.349799991, 1.383900046, 1.406499982,
                  1.424499989, 1.440099955, 1.450899959, 1.462599993, 1.472800016, 1.540799975, 1.592399955,
                  1.631000042, 1.658699989, 1.688799977, 1.715199947, 1.739199996, 1.759699941, 1.779999971]
        self.H: List[float]
        self.H = [0, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800,
                  900, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]
        self._create_BH_curve()

        self.B_loss: List[float]
        self.B_loss = list(arange(0, 1.8, 0.1))
        self.W_loss: List[float]
        self.W_loss = [0, 0.014681, 0.057808001, 0.122869998, 0.205819994, 0.302670002, 0.414570004, 0.539990008,
                       0.681159973, 0.838329971, 1.019700050, 1.228000045, 1.473799944, 1.780200005, 2.193000078,
                       2.664900064, 3.084300041, 3.428999901]
        self._create_losses_curve()

    def __str__(self) -> str:
        return "Сталь 2414 (вдоль проката)"


class Steel2414Across(Steel):
    def __init__(self) -> None:
        self.B: List[float]
        self.B = [0, 0.002655800, 0.003987200, 0.003446700, 0.007429400, 0.009288900, 0.011421000, 0.013536000,
                  0.015920000, 0.047010001, 0.101499997, 0.183990002, 0.284069985, 0.387840003, 0.487260014,
                  0.578029990, 0.661270022, 0.733500004, 1.122799993, 1.239199996, 1.290899992, 1.321099997,
                  1.343299985, 1.361400008, 1.373900056, 1.387799978, 1.396999955, 1.469599962, 1.518800020,
                  1.559299946, 1.593400002, 1.623900056, 1.654299974, 1.677899957, 1.700500011, 1.724099994]
        self.H: List[float]
        self.H = [0, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1,
                  2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        self._create_BH_curve()

        self.B_loss: List[float]
        self.B_loss = list(arange(0, 1.8, 0.1))
        self.W_loss: List[float]
        self.W_loss = [0, 0.02746, 0.097365998, 0.192959994, 0.309780002, 0.442820013, 0.594340026, 0.761330009,
                       0.946269989, 1.149700046, 1.373299956, 1.628100038, 1.924800038, 2.299299955, 2.784800053,
                       3.246299982, 3.609499931, 3.934200048]
        self._create_losses_curve()

    def __str__(self) -> str:
        return "Сталь 2414 (поперёк проката)"


class Steel2414Mean(Steel):
    def __init__(self) -> None:
        self.B: List[float]
        self.B = [0, 0.005199550, 0.007805100, 0.009731850, 0.014309200, 0.018084950, 0.022123000, 0.027183500,
                  0.032125999, 0.109360000, 0.249164995, 0.428979993, 0.576279983, 0.675880000, 0.757529989,
                  0.826664984, 0.886985004, 0.938750029, 1.207300007, 1.294499993, 1.337400019, 1.363799989,
                  1.383899987, 1.400749981, 1.412400007, 1.425199986, 1.434899986, 1.505199969, 1.555599988,
                  1.595149994, 1.626049995, 1.656350017, 1.684749961, 1.708549976, 1.730099976, 1.752049983]
        self.H: List[float]
        self.H = [0, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1,
                  2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        self._create_BH_curve()

        self.B_loss: List[float]
        self.B_loss = list(arange(0, 1.8, 0.1))
        self.W_loss: List[float]
        self.W_loss = [0, 0.0210705, 0.077586999, 0.157914996, 0.257799998, 0.372745007, 0.504455015, 0.650660008,
                       0.813714981, 0.994015008, 1.196500003, 1.428050041, 1.699299991, 2.03974998, 2.488900065,
                       2.955600023, 3.346899986, 3.681599975]
        self._create_losses_curve()

    def __str__(self) -> str:
        return "Сталь 2414 (усреднённая)"


class M27050AAlong(Steel):
    def __init__(self) -> None:
        self.B: List[float]
        self.B = [0, 0.009745100, 0.014480000, 0.020315001, 0.026628001, 0.034265999, 0.041917000, 0.053006999,
                  0.064057000, 0.237379998, 0.517159998, 0.784659982, 0.916729987, 0.998480022, 1.060799956,
                  1.108100057, 1.146399975, 1.177700043, 1.328099966, 1.384899974, 1.416900039, 1.438400030,
                  1.457000017, 1.470499992, 1.482699990, 1.494199991, 1.503000021, 1.576200008, 1.623800039,
                  1.662099957, 1.694800019, 1.721899986, 1.745200038, 1.766199946, 1.788200021, 1.805899978]
        self.H: List[float]
        self.H = [0, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1,
                  2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        self._create_BH_curve()

        self.B_loss: List[float]
        self.B_loss = list(arange(0, 1.8, 0.1))
        self.W_loss: List[float]
        self.W_loss = [0, 0.013813, 0.053376999, 0.111670002, 0.185369998, 0.271539986, 0.370330006, 0.482380003,
                       0.608910024, 0.751179993, 0.908850014, 1.091500044, 1.302099943, 1.552600026, 1.863700032,
                       2.246000051, 2.604199886, 2.915199995]
        self._create_losses_curve()

    def __str__(self) -> str:
        return "Сталь М270-50А (вдоль проката)"


class M27050AAcross(Steel):
    def __init__(self) -> None:
        self.B: List[float]
        self.B = [0, 0.002114200, 0.003182000, 0.004504900, 0.005575200, 0.007161400, 0.008751900, 0.011147000,
                  0.012999000, 0.036116999, 0.075963996, 0.132620007, 0.203769997, 0.282460004, 0.363499999,
                  0.444139987, 0.523500025, 0.596570015, 1.072600007, 1.225399971, 1.287400007, 1.320199966,
                  1.345100045, 1.363999963, 1.378200054, 1.389500022, 1.402699947, 1.478999972, 1.528800011,
                  1.569399953, 1.605100036, 1.632500052, 1.663200021, 1.691900015, 1.711599946, 1.734099984]
        self.H: List[float]
        self.H = [0, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1,
                  2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        self._create_BH_curve()

        self.B_loss: List[float]
        self.B_loss = list(arange(0, 1.8, 0.1))
        self.W_loss: List[float]
        self.W_loss = [0, 0.029914999, 0.104039997, 0.204840004, 0.325080007, 0.461769998, 0.611800015, 0.774110019,
                       0.949280024, 1.137099981, 1.33949995, 1.565500021, 1.824699998, 2.140399933, 2.555299997,
                       2.957000017, 3.290400028, 3.559299946]
        self._create_losses_curve()

    def __str__(self) -> str:
        return "Сталь М270-50А (поперёк проката)"


class M27050AMean(Steel):
    def __init__(self) -> None:
        self.B: List[float]
        self.B = [0, 0.005929650, 0.008831000, 0.012409950, 0.016101600, 0.020713699, 0.025334450, 0.032077000,
                  0.038528000, 0.136748498, 0.296561997, 0.458639994, 0.560249992, 0.640470013, 0.712149978,
                  0.776120022, 0.834950000, 0.887135029, 1.200349987, 1.305149972, 1.352150023, 1.379299998,
                  1.401050031, 1.417249978, 1.430450022, 1.441850007, 1.452849984, 1.527599990, 1.576300025,
                  1.615749955, 1.649950027, 1.677200019, 1.704200029, 1.729049981, 1.749899983, 1.769999981]
        self.H: List[float]
        self.H = [0, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1,
                  2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        self._create_BH_curve()

        self.B_loss: List[float]
        self.B_loss = list(arange(0, 1.8, 0.1))
        self.W_loss: List[float]
        self.W_loss = [0, 0.021864, 0.078708498, 0.158255003, 0.255225003, 0.366654992, 0.49106501, 0.628245011,
                       0.779095024, 0.944139987, 1.124174982, 1.328500032, 1.563399971, 1.846499979, 2.209500015,
                       2.601500034, 2.947299957, 3.23724997]
        self._create_losses_curve()

    def __str__(self) -> str:
        return "Сталь М270-50А (усреднённая)"


class M33050AAlong(Steel):
    def __init__(self) -> None:
        self.B: List[float]
        self.B = [0, 0.003888200, 0.006209000, 0.009053700, 0.011651000, 0.015027000, 0.018921001, 0.022560000,
                  0.026702000, 0.086140998, 0.236770004, 0.528090000, 0.788360000, 0.914229989, 0.995459974,
                  1.052700043, 1.097000003, 1.131100059, 1.292299986, 1.349200010, 1.379799962, 1.402500033,
                  1.419499993, 1.433400035, 1.445899963, 1.456099987, 1.465800047, 1.533699989, 1.575199962,
                  1.618000031, 1.643499970, 1.669399977, 1.707100034, 1.730399966, 1.752500057, 1.772300005]
        self.H: List[float]
        self.H = [0, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1,
                  2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        self._create_BH_curve()

        self.B_loss: List[float]
        self.B_loss = list(arange(0, 1.9, 0.1))
        self.W_loss: List[float]
        self.W_loss = [0, 0.016469, 0.061636999, 0.131579995, 0.221149996, 0.327320009, 0.447840005, 0.582099974,
                       0.732599974, 0.901189983, 1.08949995, 1.305899978, 1.558400035, 1.870499969, 2.27760005,
                       2.719700098, 3.091300011, 3.406699896, 3.688699961]
        self._create_losses_curve()

    def __str__(self) -> str:
        return "Сталь М330-50А (вдоль проката)"


class M33050AAcross(Steel):
    def __init__(self) -> None:
        self.B: List[float]
        self.B = [0, 0.001836500, 0.002623500, 0.003663600, 0.004974900, 0.006275500, 0.007588200, 0.009407900,
                  0.011270000, 0.031707998, 0.064496003, 0.115170002, 0.187810004, 0.274190009, 0.371969998,
                  0.469839990, 0.568009973, 0.657050014, 1.119500041, 1.236899972, 1.286299944, 1.316699982,
                  1.338600039, 1.354699969, 1.366799951, 1.380800009, 1.391199946, 1.461300015, 1.508900046,
                  1.548699975, 1.582299948, 1.612699986, 1.647699952, 1.662899971, 1.687199950, 1.685999990]
        self.H: List[float]
        self.H = [0, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1,
                  2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        self._create_BH_curve()

        self.B_loss: List[float]
        self.B_loss = list(arange(0, 1.9, 0.1))
        self.W_loss: List[float]
        self.W_loss = [0, 0.031198001, 0.106810004, 0.208179995, 0.330440015, 0.469000012, 0.624450028, 0.796029985,
                       0.983229995, 1.188300014, 1.415099978, 1.668599963, 1.967900038, 2.331599951, 2.821500063,
                       3.258599997, 3.599400043, 3.900099993, 4.115499973]
        self._create_losses_curve()

    def __str__(self) -> str:
        return "Сталь М330-50А (поперёк проката)"


class M33050AMean(Steel):
    def __init__(self) -> None:
        self.B: List[float]
        self.B = [0, 0.002310000, 0.003603900, 0.005146900, 0.006956100, 0.008754400, 0.010568000, 0.012632000,
                  0.014955000, 0.042624000, 0.091509998, 0.189410001, 0.336360008, 0.498149991, 0.644029975,
                  0.761839986, 0.854240000, 0.925670028, 1.215199947, 1.294800043, 1.334300041, 1.359799981,
                  1.378499985, 1.393599987, 1.406399965, 1.417600036, 1.427199960, 1.496299982, 1.541499972,
                  1.581599951, 1.613199949, 1.641499996, 1.667000055, 1.694599986, 1.716500044, 1.736299992]
        self.H: List[float]
        self.H = [0, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1,
                  2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        self._create_BH_curve()

        self.B_loss: List[float]
        self.B_loss = list(arange(0, 1.9, 0.1))
        self.w_loss: List[float]
        self.W_loss = [0, 0.02283, 0.082099997, 0.167140007, 0.271899998, 0.393649995, 0.531729996, 0.684949994,
                       0.854399979, 1.041900039, 1.25059998, 1.486799955, 1.762799978, 2.105499983, 2.548199892,
                       2.994699955, 3.351999998, 3.634500027, 3.875299931]
        self._create_losses_curve()

    def __str__(self) -> str:
        return "Сталь М330-50А (усреднённая)"


class M40050AAlong(Steel):
    def __init__(self) -> None:
        self.B: List[float]
        self.B = [0, 0.006607100, 0.009253300, 0.011900000, 0.014796000, 0.017716000, 0.020900000, 0.024071001,
                  0.027502000, 0.068736002, 0.142820001, 0.299169987, 0.549449980, 0.765470028, 0.938820004,
                  1.044499993, 1.101899981, 1.142699957, 1.311499953, 1.371399999, 1.404500008, 1.428400040,
                  1.446900010, 1.461799979, 1.475100040, 1.486799955, 1.496500015, 1.569599986, 1.616700053,
                  1.655599952, 1.686800003, 1.712399960, 1.738000035, 1.760800004, 1.780900002, 1.800600052]
        self.H: List[float]
        self.H = [0, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1,
                  2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        self._create_BH_curve()

        self.B_loss: List[float]
        self.B_loss = list(arange(0, 1.8, 0.1))
        self.W_loss: List[float]
        self.W_loss = [0, 0.015536, 0.072013997, 0.161070004, 0.27493, 0.411220014, 0.561460018, 0.727779984,
                       0.91069001, 1.118399978, 1.354900002, 1.624799967, 1.933300018, 2.298599958, 2.744199991,
                       3.301399946, 4.088900089, 4.856699944]
        self._create_losses_curve()

    def __str__(self) -> str:
        return "Сталь М400-50А (вдоль проката)"


class M40050AAcross(Steel):
    def __init__(self) -> None:
        self.B: List[float]
        self.B = [0, 0.002860000, 0.003914000, 0.005207300, 0.006513400, 0.007554800, 0.008842200, 0.010147000,
                  0.011724000, 0.026556000, 0.045049001, 0.069793001, 0.103110000, 0.150389999, 0.211850002,
                  0.286559999, 0.369080007, 0.453770012, 1.031299949, 1.214300036, 1.292299986, 1.340299964,
                  1.372699976, 1.396600008, 1.414700031, 1.429700017, 1.440099955, 1.525699973, 1.576500058,
                  1.613100052, 1.644400001, 1.673400044, 1.699000001, 1.718299985, 1.742200017, 1.762899995]
        self.H: List[float]
        self.H = [0, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1,
                  2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        self._create_BH_curve()

        self.B_loss: List[float]
        self.B_loss = list(arange(0, 1.8, 0.1))
        self.W_loss: List[float]
        self.W_loss = [0, 0.02884, 0.11772, 0.242029995, 0.391629994, 0.561860025, 0.753380001, 0.964479983,
                       1.197700024, 1.452499986, 1.733899951, 2.047600031, 2.398799896, 2.7973001, 3.290400028,
                       3.947000027, 4.800300121, 5.4302001]
        self._create_losses_curve()

    def __str__(self) -> str:
        return "Сталь М400-50А (поперёк проката)"


class M40050AMean(Steel):
    def __init__(self) -> None:
        self.B: List[float]
        self.B = [0, 0.004733550, 0.006583650, 0.008553650, 0.010654700, 0.012635400, 0.014871100, 0.017109000,
                  0.019613000, 0.047646001, 0.093934501, 0.184481494, 0.326279990, 0.457930014, 0.575335003,
                  0.665529996, 0.735489994, 0.798234984, 1.171399951, 1.292850018, 1.348399997, 1.384350002,
                  1.409799993, 1.429199994, 1.444900036, 1.458249986, 1.468299985, 1.547649980, 1.596600056,
                  1.634350002, 1.665600002, 1.692900002, 1.718500018, 1.739549994, 1.761550009, 1.781750023]
        self.H: List[float]
        self.H = [0, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1,
                  2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        self._create_BH_curve()

        self.B_loss: List[float]
        self.B_loss = list(arange(0, 1.8, 0.1))
        self.W_loss: List[float]
        self.W_loss = [0, 0.022188, 0.094866998, 0.201549999, 0.333279997, 0.48654002, 0.657420009, 0.846129984,
                       1.054195017, 1.285449982, 1.544399977, 1.836199999, 2.166049957, 2.547950029, 3.01730001,
                       3.624199986, 4.444600105, 5.143450022]
        self._create_losses_curve()

    def __str__(self) -> str:
        return "Сталь М400-50А (усреднённая)"


class Steel35HN3MFARotor(Steel):
    def __init__(self):
        self.B: List[float]
        self.B = [0.81, 0.815, 0.82, 0.825, 0.83, 0.835, 0.84, 0.845, 0.85, 0.855, 0.86, 0.865, 0.87, 0.875, 0.88,
                  0.885, 0.89, 0.895, 0.9, 0.905, 0.91, 0.915, 0.92, 0.925, 0.93, 0.935, 0.94, 0.945, 0.95, 0.955, 0.96,
                  0.965, 0.97, 0.975, 0.98, 0.985, 0.99, 0.995, 1, 1.005, 1.01, 1.015, 1.02, 1.025, 1.03, 1.035, 1.04,
                  1.045, 1.05, 1.055, 1.06, 1.065, 1.07, 1.075, 1.08, 1.085, 1.09, 1.095, 1.1, 1.105, 1.11, 1.115, 1.12,
                  1.125, 1.13, 1.135, 1.14, 1.145, 1.15, 1.155, 1.16, 1.165, 1.17, 1.175, 1.18, 1.185, 1.19, 1.195, 1.2,
                  1.205, 1.21, 1.215, 1.22, 1.225, 1.23, 1.235, 1.24, 1.245, 1.25, 1.255, 1.26, 1.265, 1.27, 1.275,
                  1.28, 1.285, 1.29, 1.295, 1.3, 1.305, 1.31, 1.315, 1.32, 1.325, 1.33, 1.335, 1.34, 1.345, 1.35, 1.355,
                  1.36, 1.365, 1.37, 1.375, 1.38, 1.385, 1.39, 1.395, 1.4, 1.405, 1.41, 1.415, 1.42, 1.425, 1.43, 1.435,
                  1.44, 1.445, 1.45, 1.455, 1.46, 1.465, 1.47, 1.475, 1.48, 1.485, 1.49, 1.495, 1.5, 1.505, 1.51, 1.515,
                  1.52, 1.525, 1.53, 1.535, 1.54, 1.545, 1.55, 1.555, 1.56, 1.565, 1.57, 1.575, 1.58, 1.585, 1.59,
                  1.595, 1.6, 1.605, 1.61, 1.615, 1.62, 1.625, 1.63, 1.635, 1.64, 1.645, 1.65, 1.655, 1.66, 1.665, 1.67,
                  1.675, 1.68, 1.685, 1.69, 1.695, 1.7, 1.705, 1.71, 1.715, 1.72, 1.725, 1.73, 1.735, 1.74, 1.745, 1.75,
                  1.755, 1.76, 1.765, 1.77, 1.775, 1.78, 1.785, 1.79, 1.795, 1.8, 1.805, 1.81, 1.815, 1.82, 1.825, 1.83,
                  1.835, 1.84, 1.845, 1.85, 1.855, 1.86, 1.865, 1.87, 1.875, 1.88, 1.885, 1.89, 1.895, 1.9, 1.905, 1.91,
                  1.915, 1.92, 1.925, 1.93, 1.935, 1.94, 1.945, 1.95, 1.955, 1.96, 1.965, 1.97, 1.975, 1.98, 1.985,
                  1.99, 1.995, 2, 2.005, 2.01, 2.015, 2.02, 2.025, 2.03, 2.035, 2.04, 2.045, 2.05, 2.055, 2.06, 2.065,
                  2.07, 2.075, 2.08, 2.085, 2.09, 2.095, 2.1, 2.105, 2.11, 2.115, 2.12, 2.125, 2.13, 2.135, 2.14, 2.145,
                  2.15, 2.155, 2.16, 2.165, 2.17, 2.175, 2.18, 2.185, 2.19, 2.195, 2.2, 2.205, 2.21, 2.215, 2.22, 2.225,
                  2.23, 2.235, 2.24, 2.245, 2.25, 2.255, 2.26, 2.265, 2.27, 2.275, 2.28, 2.285, 2.29, 2.295, 2.3, 2.305,
                  2.31, 2.315, 2.32]
        self.H: List[float]
        self.H = [11.94, 11.98, 12.02, 12.06, 12.1, 12.14, 12.18, 12.22, 12.26, 12.3, 12.34, 12.38, 12.42, 12.46, 12.5,
                  12.54, 12.58, 12.62, 12.66, 12.7, 12.74, 12.78, 12.82, 12.86, 12.9, 12.94, 12.98, 13.02, 13.06, 13.1,
                  13.14, 13.18, 13.22, 13.26, 13.3, 13.35, 13.4, 13.45, 13.5, 13.55, 13.59, 13.64, 13.68, 13.73, 13.77,
                  13.82, 13.86, 13.91, 13.95, 14, 14.04, 14.09, 14.13, 14.18, 14.22, 14.27, 14.31, 14.36, 14.4, 14.45,
                  14.49, 14.54, 14.58, 14.63, 14.67, 14.72, 14.76, 14.81, 14.85, 14.9, 14.94, 14.99, 15.03, 15.08,
                  15.12, 15.17, 15.21, 15.26, 15.3, 15.39, 15.48, 15.57, 15.66, 15.75, 15.84, 15.93, 16.02, 16.11, 16.2,
                  16.32, 16.44, 16.56, 16.68, 16.8, 16.92, 17.04, 17.16, 17.28, 17.4, 17.61, 17.82, 18.03, 18.24, 18.45,
                  18.66, 18.87, 19.08, 19.29, 19.5, 19.75, 20, 20.25, 20.5, 20.75, 21, 21.25, 21.5, 21.75, 22, 22.25,
                  22.5, 22.75, 23, 23.25, 23.5, 23.75, 24, 24.25, 24.5, 24.95, 25.4, 25.85, 26.3, 26.75, 27.2, 27.65,
                  28.1, 28.55, 29, 29.65, 30.3, 30.95, 31.6, 32.25, 32.9, 33.55, 34.2, 34.85, 35.5, 36.4, 37.3, 38.2,
                  39.1, 40, 40.9, 41.8, 42.7, 43.6, 44.5, 46.15, 47.8, 49.45, 51.1, 52.75, 54.4, 56.05, 57.7, 59.35, 61,
                  63, 65, 67, 69, 71, 73, 75, 77, 79, 81, 83.4, 85.8, 88.2, 90.6, 93, 95.4, 97.8, 100.2, 102.6, 105,
                  107.5, 110, 112.5, 115, 117.5, 120, 122.5, 125, 127.5, 130, 134, 138, 142, 146, 150, 154, 158, 162,
                  166, 170, 177, 184, 191, 198, 205, 212, 219, 226, 233, 240, 250, 260, 270, 280, 290, 300, 310, 320,
                  330, 340, 351, 362, 373, 384, 395, 406, 417, 428, 439, 450, 472, 494, 516, 538, 560, 582, 604, 626,
                  648, 670, 697.5, 725, 752.5, 780, 807.5, 835, 862.5, 890, 920, 950, 980, 1010, 1040, 1070, 1100, 1130,
                  1160, 1190, 1220, 1250, 1280, 1310, 1340, 1370, 1400, 1430, 1460, 1490, 1520, 1550, 1580, 1610, 1640,
                  1670, 1700, 1730, 1760, 1790, 1820, 1850, 1880, 1910, 1940, 1970, 2000, 2030, 2060, 2090, 2120, 2150,
                  2180, 2210, 2240, 2270]
        self._create_BH_curve()

    def __str__(self) -> str:
        return "Роторная сталь 35ХН3МФА"


__all__ = ["Steel",
           "Steel2414Along",
           "Steel2414Across",
           "Steel2414Mean",
           "Steel3414Along",
           "Steel3414Across",
           "M27050AAlong",
           "M27050AAcross",
           "M27050AMean",
           "M33050AAlong",
           "M33050AAcross",
           "M33050AMean",
           "M40050AAlong",
           "M40050AAcross",
           "M40050AMean",
           "Steel35HN3MFARotor"]
