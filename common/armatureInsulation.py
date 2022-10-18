from typing import Union, Tuple
from common.wireTypes import *
from abc import ABC, abstractmethod


class CoilInsulation(ABC):
    """
    Абстрактный класс, перечисляющий атрибуты изоляции катушечной обмотки. Служит базовым классом для всех типов
    изоляции катушечных обмоток.

    Атрибуты:

    * ``turn_insulation: float``

      Толщина витковой изоляции, мм.

    * ``column_insulation: float``

      Толщина замотки столбика, мм.

    * ``body_insulation: Tuple[float, float]``

      Толщина корпусной изоляции по высоте и по ширине, мм.

    * ``semicond_coating: float``

      Толщина полупроводящего покрытия для предотвращения частичных разрядов, мм.

    * ``wedge_filling: float``

      Толщина прокладки под клин, мм.

    * ``coil_filling: float``

     Толщина прокладки между катушками в пазу, мм.

    * ``bottom_filling: float``

      Толщина прокладки на дно паза, мм.

    Методы:

    * ``all_fillings(self) -> float``

      Возвращает суммарную толщину прокладок в пазу, мм.

    * ``all_insulation(self) -> Tuple[float, float]``

      Возвращает суммарную толщину изоляции по высоте и по ширине, мм.

    Реализует паттерн «Одиночка», поскольку у статора не может быть две системы изоляции одновременно.
    """

    __slots__ = ["turn_insulation",
                 "column_insulation",
                 "body_insulation",
                 "semicond_coating",
                 "wedge_filling",
                 "coil_filling",
                 "bottom_filling"]

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self) -> None:
        self.turn_insulation: float
        self.column_insulation: float
        self.body_insulation: Tuple[float, float]
        self.semicond_coating: float
        self.wedge_filling: float
        self.coil_filling: float
        self.bottom_filling: float

    @abstractmethod
    def __str__(self) -> str:
        pass

    def all_fillings(self) -> float:
        """
        Метод, возвращающий суммарную толщину прокладок по высоте паза.

        :return: Суммарная толщина прокладок, мм.
        """

        return self.wedge_filling + self.coil_filling + self.bottom_filling

    def all_insulation(self) -> Tuple[float, float]:
        """
        Метод, возвращающий суммарные толщины изоляции в пазу.

        :return: Суммарная толщина изоляции по высоте и по ширине паза, мм.
        """

        height = self.turn_insulation + self.semicond_coating + self.body_insulation[0] + self.column_insulation
        width = self.turn_insulation + self.semicond_coating + self.body_insulation[1] + self.column_insulation
        return height, width


class Monolith2New(CoilInsulation):
    """
    Класс, описывающий катушечную изоляцию типа Монолит-2 по новому СТО. Используется только с проводниками типов
    ППТА-2 и ПЭТВСД.

    Атрибуты:

    * ``turn_insulation: float``

      Толщина витковой изоляции, мм.

    * ``column_insulation: float``

      Толщина замотки столбика, мм.

    * ``body_insulation: Tuple[float, float]``

      Толщина корпусной изоляции по высоте и по ширине, мм.

    * ``semicond_coating: float``

      Толщина полупроводящего покрытия для предотвращения частичных разрядов, мм.

    * ``wedge_filling: float``

      Толщина прокладки под клин, мм.

    * ``coil_filling: float``

     Толщина прокладки между катушками в пазу, мм.

    * ``bottom_filling: float``

      Толщина прокладки на дно паза, мм.

    Методы:

    * ``all_fillings(self) -> float``

      Возвращает суммарную толщину прокладок в пазу, мм.

    * ``all_insulation(self) -> Tuple[float, float]``

      Возвращает суммарную толщину изоляции по высоте и по ширине, мм.

    Возбуждает исключения:

    * ``ValueError``

      В случае попытки использования с обмоточным проводником, не указанном с СТО, возбуждает ``ValueError``.

    Наследует класс ``CoilInsulation``.
    """

    def __init__(self,
                 wire: WireType,
                 voltage: int,
                 *args,
                 **kwargs
                 ) -> None:
        """
        Конструктор класса ``Monolith2New``.

        :param wire: Объект, описывающий используемый для выполнений обмотки проводник.
        :param voltage: Напряжение статора машины, В.
        :param *args: Игнорируется, добавлено для совместимости интерфейса классов.
        :param **kwargs: Игнорируется, добавлено для совместимости интерфейса классов.
        """

        super().__init__()

        if voltage >= 10000:
            if (t := type(wire)) is PPTA2:
                self.turn_insulation = 0  # Витковая изоляция
                self.body_insulation = (4.84, 4.84)  # Корпусная изоляция (по высоте, по ширине)
            elif t is PETVSD:
                self.turn_insulation = 0.8
                self.body_insulation = (5.28, 5.28)
            else:
                raise ValueError("Неверный тип проводника")

            self.column_insulation = 0.2  # Замотка столбика
            self.semicond_coating = 0.4  # Полупроводниковое покрытие
            self.wedge_filling = 0.5  # Прокладка под клин
            self.coil_filling = 4  # Прокладка между катушками
            self.bottom_filling = 0.5  # Прокладка на дно паза

        elif voltage >= 3000:
            if type(wire) is PPTA2 or PETVSD:
                self.body_insulation = (3.08, 3.08)
            else:
                raise ValueError("Неверный тип проводника")

            self.turn_insulation = 0
            self.column_insulation = 0.2
            self.semicond_coating = 0.4
            self.wedge_filling = 0.5
            self.coil_filling = 3
            self.bottom_filling = 0.5

        elif voltage >= 380:
            if (t := type(wire)) is PPTA2 or PETVSD:
                self.body_insulation = (1.76, 1.76)
            elif t is PPS:
                self.body_insulation = (0.69, 0.46)
            else:
                raise ValueError("Неверный тип проводника")

            self.turn_insulation = 0
            self.column_insulation = 0.2
            self.semicond_coating = 0
            self.wedge_filling = 0.5
            self.coil_filling = 3
            self.bottom_filling = 0.5

        else:
            raise ValueError("Слишком маленькое напряжение")

    def __str__(self) -> str:
        return "Монолит-2 (новый)"


class Monolith2Old(CoilInsulation):
    """
    Класс, описывающий катушечную изоляцию типа Монолит-2 по старому СТО. Используется только с проводниками типов
    ППТА-2, ПЭТВСД, ПСДТ, ППС и ППЛС.

    Атрибуты:

    * ``turn_insulation: float``

      Толщина витковой изоляции, мм.

    * ``column_insulation: float``

      Толщина замотки столбика, мм.

    * ``body_insulation: Tuple[float, float]``

      Толщина корпусной изоляции по высоте и по ширине, мм.

    * ``semicond_coating: float``

      Толщина полупроводящего покрытия для предотвращения частичных разрядов, мм.

    * ``wedge_filling: float``

      Толщина прокладки под клин, мм.

    * ``coil_filling: float``

     Толщина прокладки между катушками в пазу, мм.

    * ``bottom_filling: float``

      Толщина прокладки на дно паза, мм.

    Методы:

    * ``all_fillings(self) -> float``

      Возвращает суммарную толщину прокладок в пазу, мм.

    * ``all_insulation(self) -> Tuple[float, float]``

      Возвращает суммарную толщину изоляции по высоте и по ширине, мм.

    Возбуждает исключения:

    * ``ValueError``

      В случае попытки использования с обмоточным проводником, не указанном с СТО, возбуждает ``ValueError``.

    Наследует класс ``CoilInsulation``.
    """

    def __init__(self,
                 wire: WireType,
                 voltage: int,
                 *args,
                 **kwargs) -> None:
        """
        Конструктор класса ``Monolith2Old``.

        :param wire: Объект, описывающий используемый для выполнений обмотки проводник.
        :param voltage: Напряжение статора машины, В.
        :param *args: Игнорируется, добавлено для совместимости интерфейса классов.
        :param **kwargs: Игнорируется, добавлено для совместимости интерфейса классов.
        """

        super().__init__()

        if voltage >= 10000:
            if (t := type(wire)) in [PPTA2, PPS, PPLS]:
                self.turn_insulation = 0  # Витковая изоляция
                self.body_insulation = (4.84, 4.84)  # Корпусная изоляция (по высоте, по ширине)
            elif t is PSDT:
                self.turn_insulation = 0.8
                self.body_insulation = (5.28, 5.28)
            else:
                raise ValueError("Неверный тип проводника")

            self.column_insulation = 0.2  # Замотка столбика
            self.semicond_coating = 0.48  # Полупроводниковое покрытие
            self.wedge_filling = 0.5  # Прокладка под клин
            self.coil_filling = 4  # Прокладка между катушками
            self.bottom_filling = 0.5  # Прокладка на дно паза

        elif voltage >= 3000:
            if type(wire) is PSDT:
                self.turn_insulation = 0.52
                self.body_insulation = (3.52, 3.52)
            else:
                self.turn_insulation = 0
                self.body_insulation = (3.08, 3.08)

            self.column_insulation = 0.2
            self.semicond_coating = 0.48
            self.wedge_filling = 0.5
            self.coil_filling = 3
            self.bottom_filling = 0.5

        elif voltage >= 380:
            if type(wire) not in [PPTA2, PETVSD, PPS, PPLS]:
                raise ValueError("Неверный тип проводника")

            self.turn_insulation = 0
            self.column_insulation = 0.2
            self.body_insulation = (1.76, 1.76)
            self.semicond_coating = 0
            self.wedge_filling = 0.5
            self.coil_filling = 3
            self.bottom_filling = 0.5

        else:
            raise ValueError("Слишком маленькое напряжение")

    def __str__(self) -> str:
        return "Монолит-2 (старый)"


class Micafil(CoilInsulation):
    """
    Класс, описывающий катушечную изоляцию типа Микафил. Используется только с проводниками типов ПЭТВСД и ПСДТ.

    Атрибуты:

    * ``turn_insulation: float``

      Толщина витковой изоляции, мм.

    * ``column_insulation: float``

      Толщина замотки столбика, мм.

    * ``body_insulation: Tuple[float, float]``

      Толщина корпусной изоляции по высоте и по ширине, мм.

    * ``semicond_coating: float``

      Толщина полупроводящего покрытия для предотвращения частичных разрядов, мм.

    * ``wedge_filling: float``

      Толщина прокладки под клин, мм.

    * ``coil_filling: float``

     Толщина прокладки между катушками в пазу, мм.

    * ``bottom_filling: float``

      Толщина прокладки на дно паза, мм.

    Методы:

    * ``all_fillings(self) -> float``

      Возвращает суммарную толщину прокладок в пазу, мм.

    * ``all_insulation(self) -> Tuple[float, float]``

      Возвращает суммарную толщину изоляции по высоте и по ширине, мм.

    Возбуждает исключения:

    * ``ValueError``

      В случае попытки использования с обмоточным проводником, не указанном с СТО, возбуждает ``ValueError``.

    Наследует класс ``CoilInsulation``.
    """

    def __init__(self,
                 wire: WireType,
                 voltage: int,
                 turn_count: int,
                 *args,
                 **kwargs) -> None:
        """
        Конструктор класса ``Micafil``.

        :param wire: Объект, описывающий используемый для выполнений обмотки проводник.
        :param voltage: Напряжение статора машины, В.
        :param turn_count: Число витков катушки.
        :param *args: Игнорируется, добавлено для совместимости интерфейса классов.
        :param **kwargs: Игнорируется, добавлено для совместимости интерфейса классов.
        """

        super().__init__()

        wire_type = type(wire)
        if voltage >= 10000:
            if wire_type is not PETVSD:
                raise ValueError("Неверный тип проводника")

            self.turn_insulation = 0.4  # Витковая изоляция
            self.column_insulation = 0.2  # Замотка столбика
            self.body_insulation = (6, 6)  # Корпусная изоляция (по высоте, по ширине)
            self.semicond_coating = 0.4  # Полупроводниковое покрытие
            self.wedge_filling = 1  # Прокладка под клин
            self.coil_filling = 4  # Прокладка между катушками
            self.bottom_filling = 1  # Прокладка на дно паза

        elif voltage >= 6600:
            # Извращенцы, ещё и к количеству витков катушки привязались зачем-то... А людям теперь это учитывать...
            # В число витков следует подавать половину числа эффективных проводников в пазу
            if turn_count < 10 and wire_type is PSDT:
                self.turn_insulation = 0.4
            elif turn_count >= 10 and wire_type is PETVSD:
                self.turn_insulation = 0
            else:
                raise ValueError("Неверный тип проводника")

            self.column_insulation = 0.2
            self.body_insulation = (4, 4)
            self.semicond_coating = 0.4
            self.wedge_filling = 0.5
            self.coil_filling = 3
            self.bottom_filling = 0.5

        elif voltage >= 3300:
            if wire_type is not PETVSD:
                raise ValueError("Неверный тип проводника")

            self.turn_insulation = 0
            self.column_insulation = 0.2
            self.body_insulation = (3, 3)
            self.semicond_coating = 0
            self.wedge_filling = 0.5
            self.coil_filling = 3
            self.bottom_filling = 0.5

        elif voltage >= 380:
            if wire_type is not PETVSD:
                raise ValueError("Неверный тип проводника")

            self.turn_insulation = 0
            self.column_insulation = 0.2
            self.body_insulation = (2, 2)
            self.semicond_coating = 0
            self.wedge_filling = 0.5
            self.coil_filling = 3
            self.bottom_filling = 0.5

        else:
            raise ValueError("Слишком маленькое напряжение")

    def __str__(self) -> str:
        return "Микафил"


class CustomCoilInsulation(CoilInsulation):
    """
    Абстрактный класс, перечисляющий атрибуты изоляции катушечной обмотки. Служит базовым классом для всех типов
    изоляции катушечных обмоток.

    Атрибуты:

    * ``turn_insulation: float``

      Толщина витковой изоляции, мм.

    * ``column_insulation: float``

      Толщина замотки столбика, мм.

    * ``body_insulation: Tuple[float, float]``

      Толщина корпусной изоляции по высоте и по ширине, мм.

    * ``semicond_coating: float``

      Толщина полупроводящего покрытия для предотвращения частичных разрядов, мм.

    * ``wedge_filling: float``

      Толщина прокладки под клин, мм.

    * ``coil_filling: float``

     Толщина прокладки между катушками в пазу, мм.

    * ``bottom_filling: float``

      Толщина прокладки на дно паза, мм.

    Методы:

    * ``all_fillings(self) -> float``

      Возвращает суммарную толщину прокладок в пазу, мм.

    * ``all_insulation(self) -> Tuple[float, float]``

      Возвращает суммарную толщину изоляции по высоте и по ширине, мм.

    Наследует класс ``CoilInsulation``.
    """

    def __init__(self,
                 turn_insulation: float,
                 column_insulation: float,
                 body_insulation: Union[float, Tuple[float, float]],
                 semicond_coating: float,
                 wedge_filling: float,
                 coil_filling: float,
                 bottom_filling: float
                 ) -> None:
        super().__init__()

        self.turn_insulation = turn_insulation  # Витковая изоляция
        self.column_insulation = column_insulation  # Замотка столбика

        if (t := type(body_insulation)) is tuple:
            self.body_insulation = body_insulation  # Корпусная изоляция (по высоте, по ширине)
        elif t is float:
            self.body_insulation = (body_insulation, body_insulation)
        else:
            raise ValueError

        self.semicond_coating = semicond_coating  # Полупроводниковое покрытие
        self.wedge_filling = wedge_filling  # Прокладка под клин
        self.coil_filling = coil_filling  # Прокладка между катушками
        self.bottom_filling = bottom_filling  # Прокладка на дно паза

    def __str__(self) -> str:
        return "Пользовательский"
