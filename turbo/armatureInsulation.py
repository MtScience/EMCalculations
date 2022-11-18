"""
Модуль, содержащий возможные типы изоляции статорных обмоток.

Классы:

* ``TurboMachineRotorInsulation``

  Класс, описывающий изоляцию обмотки ротора турбомашины.
"""


class TurboMachineRotorInsulation:
    """
    Класс, описывающий изоляцию обмотки ротора турбомашины.

    Атрибуты:

    * ``turn_insulation: float``

      Толщина витковой изоляции, мм.

    * ``body_insulation: float``

      Толщина корпусной изоляции (пазовой коробочки), мм.

    * ``wedge_filling: float``

      Толщина прокладки под клин, мм.

    * ``bottom_filling: float``

      Толщина прокладки на дно паза, мм.

    Методы:

    * ``all_fillings(self) -> float``

      Возвращает суммарную толщину прокладок в пазу, мм.

    Реализует паттерн «Одиночка».
    """
    __slots__ = ["turn_insulation",
                 "body_insulation",
                 "wedge_filling",
                 "bottom_filling"]

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self,
                 turn_insulation: float,
                 body_insulation: float,
                 wedge_filling: float,
                 bottom_filling: float
                 ) -> None:
        super().__init__()

        self.turn_insulation = turn_insulation  # Витковая изоляция
        self.body_insulation = body_insulation  # Корпусная изоляция (пазовая коробочка)

        self.wedge_filling = wedge_filling  # Прокладка под клин
        self.bottom_filling = bottom_filling  # Прокладка на дно паза

    def all_fillings(self) -> float:
        """
        Метод, возвращающий суммарную толщину прокладок по высоте паза.

        :return: Суммарная толщина прокладок, мм.
        """

        return self.wedge_filling + self.bottom_filling


__all__ = ["TurboMachineRotorInsulation"]
