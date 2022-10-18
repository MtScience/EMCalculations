"""
Модуль, содержащий описания типов обмоточных проводников, используемых для выполнения статорных обмоток машин
переменного тока.

Классы:

* ``WireType``

  Абстрактный класс, перечисляющий атрибуты, общие для всех классов модуля и служащий родительским классом для них.

* ``PPTA2``

  Класс, описывающий изоляцию проводников типа ППТА-2.

* ``PSDT``

  Класс, описывающий изоляцию проводников типа ПСДТ.

* ``CustomWire``

  Класс, описывающий пользовательский тип проводника.

"""

from common.wireDatabase import WireDB
from typing import Optional
from abc import ABC, abstractmethod


class WireType(ABC):
    r"""
    Абстрактный класс, от которого наследуют все типы собственной изоляции проводников.

    Атрибуты:

    * ``insulation_height: Optional[float]``

      Толщина изоляции проводника по высоте в мм (в расчётных методиках --- параметр `\Delta a`:math:). Имеет значение
      ``None`` в момент инициализации. То же верно для остальных полей.

    * ``insulation_width: Optional[float]``

      Толщина изоляции проводника по ширине в мм (в методиках --- `\Delta b`:math:).

    * ``wire_height: Optional[float]``

      Высота неизолированной части проводника в мм (параметр `a`:math:).

    * ``wire_width: Optional[float]``

      Ширина неизолированной части проводника в мм (параметр `b`:math:).

    * ``wire_section: Optional[float]``

      Площадь сечения проводника в мм².

    Методы:

    * ``pick_wire(max_wire_height: float, max_wire_width: float) -> None``

      Подбирает проводник *с учётом изоляции.* В сущности, служит шлюзом к методу ``pick_wire`` класса ``WireDB``.
    """

    __slots__ = ["insulation_height",
                 "insulation_width",
                 "wire_height",
                 "wire_width",
                 "wire_section"]

    def __init__(self) -> None:
        self.insulation_height: Optional[float] = None
        self.insulation_width: Optional[float] = None

        self.wire_height: Optional[float] = None
        self.wire_width: Optional[float] = None
        self.wire_section: Optional[float] = None

    @abstractmethod
    def __str__(self) -> str:
        pass

    def pick_wire(self,
                  max_wire_height: float,
                  max_wire_width: float
                  ) -> None:
        """
        Метод, осуществляющий автоматический выбор стандартного проводника по максимально допустимым размерам.

        :param max_wire_height: Максимальная высота изолированного проводника в мм.
        :param max_wire_width: Максимальная высота изолированного проводника в мм.
        """

        max_copper_height = max_wire_height - self.insulation_height
        max_copper_width = max_wire_width - self.insulation_width

        self.wire_height, self.wire_width, self.wire_section = WireDB().pick_wire(max_copper_height, max_copper_width)


class PPTA2(WireType):
    r"""
    Класс, описывающий обмоточные проводники типа ППТА-2.

    Атрибуты:

    * ``insulation_height: float``

      Толщина изоляции проводника по высоте в мм (в расчётных методиках --- параметр `\Delta a`:math:). Всегда равна
      0.40 мм.

    * ``insulation_width: float``

      Толщина изоляции проводника по ширине в мм (в методиках --- `\Delta b`:math:). Всегда равна 0.42 мм.

    * ``wire_height: Optional[float]``

      Высота неизолированной части проводника в мм (параметр `a`:math:).

    * ``wire_width: Optional[float]``

      Ширина неизолированной части проводника в мм (параметр `b`:math:).

    * ``wire_section: Optional[float]``

      Площадь сечения проводника в мм².

    Методы:

    * ``pick_wire(max_wire_height: float, max_wire_width: float) -> None``

      Подбирает проводник *с учётом изоляции.* В сущности, служит шлюзом к методу ``pick_wire`` класса ``WireDB``.

    Наследует класс ``WireType``.
    """

    def __init__(self) -> None:
        super().__init__()

        # Хорошая штука ППТА-2. Изоляция постоянная, никакой возни не надо... Не то что некоторые! Фашисты!
        self.insulation_height: float = 0.40  # Толщина изоляции по высоте
        self.insulation_width: float = 0.42  # Толщина изоляции по ширине

    def __str__(self) -> str:
        return "ППТА-2"


class PPS(WireType):
    r"""
        Класс, описывающий обмоточные проводники типа ППС.

        Атрибуты:

        * ``insulation_height: float``

          Толщина изоляции проводника по высоте в мм (в расчётных методиках --- параметр `\Delta a`:math:). Всегда равна
          0.45 мм.

        * ``insulation_width: float``

          Толщина изоляции проводника по ширине в мм (в методиках --- `\Delta b`:math:). Всегда равна 0.45 мм.

        * ``wire_height: Optional[float]``

          Высота неизолированной части проводника в мм (параметр `a`:math:).

        * ``wire_width: Optional[float]``

          Ширина неизолированной части проводника в мм (параметр `b`:math:).

        * ``wire_section: Optional[float]``

          Площадь сечения проводника в мм².

        Методы:

        * ``pick_wire(max_wire_height: float, max_wire_width: float) -> None``

          Подбирает проводник *с учётом изоляции.* В сущности, служит шлюзом к методу ``pick_wire`` класса ``WireDB``.

        Наследует класс ``WireType``.
        """

    def __init__(self):
        super().__init__()

        # ППС тоже ничего так...
        self.insulation_height: float = 0.45  # Толщина изоляции по высоте
        self.insulation_width: float = 0.45  # Толщина изоляции по ширине

    def __str__(self) -> str:
        return "ППС"


class PPLS(WireType):
    r"""
        Класс, описывающий обмоточные проводники типа ППЛС.

        Атрибуты:

        * ``insulation_height: float``

          Толщина изоляции проводника по высоте в мм (в расчётных методиках --- параметр `\Delta a`:math:). Всегда равна
          0.45 мм.

        * ``insulation_width: float``

          Толщина изоляции проводника по ширине в мм (в методиках --- `\Delta b`:math:). Всегда равна 0.45 мм.

        * ``wire_height: Optional[float]``

          Высота неизолированной части проводника в мм (параметр `a`:math:).

        * ``wire_width: Optional[float]``

          Ширина неизолированной части проводника в мм (параметр `b`:math:).

        * ``wire_section: Optional[float]``

          Площадь сечения проводника в мм².

        Методы:

        * ``pick_wire(max_wire_height: float, max_wire_width: float) -> None``

          Подбирает проводник *с учётом изоляции.* В сущности, служит шлюзом к методу ``pick_wire`` класса ``WireDB``.

        Наследует класс ``WireType``.
        """

    def __init__(self):
        super().__init__()

        # И ППЛС тоже...
        self.insulation_height: float = 0.45  # Толщина изоляции по высоте
        self.insulation_width: float = 0.45  # Толщина изоляции по ширине

    def __str__(self) -> str:
        return "ППЛС"


class PSDT(WireType):
    r"""
    Класс, описывающий обмоточные проводники типа ПСДТ.

    Атрибуты:

    * ``insulation_height: Optional[float]``

      Толщина изоляции проводника по высоте в мм (в расчётных методиках --- параметр `\Delta a`:math:). Имеет значение
      ``None`` в момент инициализации. То же верно для остальных полей.

    * ``insulation_width: Optional[float]``

      Толщина изоляции проводника по ширине в мм (в методиках --- `\Delta b`:math:).

    * ``wire_height: Optional[float]``

      Высота неизолированной части проводника в мм (параметр `a`:math:).

    * ``wire_width: Optional[float]``

      Ширина неизолированной части проводника в мм (параметр `b`:math:). ``insulation_width`` и ``insulation_height``
      связаны с размерами проводника согласно СТО.

    * ``wire_section: Optional[float]``

      Площадь сечения проводника в мм².

    Методы:

    * ``pick_wire(max_wire_height: float, max_wire_width: float) -> None``

      Подбирает проводник *с учётом изоляции,* а также саму толщину изоляции.

    Наследует класс ``WireType``.
    """

    def __str__(self) -> str:
        return "ПСДТ"

    # А вот ПСДТ - штука плохая, нехорошая. Мучиться с ней надо
    def __pick_insulation(self,
                          max_wire_height: float,
                          max_wire_width: float
                          ) -> None:
        """
        Вспомогательный метод, осуществляющий подбор толщины изоляции в соответствии с СТО.

        :param max_wire_height: Максимальная высота изолированного проводника в мм.
        :param max_wire_width: Максимальная высота изолированного проводника в мм.
        """

        # Локальные переменные, хранящие размеры изоляции
        ins_heights = {1.46: 0.28, 2.72: 0.3, 4.76: 0.38}
        ins_widths = {2.68: 0.28, 3.25: 0.3, 4.19: 0.32, 5.43: 0.34, 6.76: 0.38, 9.30: 0.4, 12.10: 0.45}

        try:
            # Подобно методу "pick_wire" класса WireDB, вычисляем нужные индексы в словарях
            heights = filter(lambda h: h <= max_wire_height, ins_heights.keys())
            widths = filter(lambda h: h <= max_wire_width, ins_widths.keys())

            # И точно также находим нужные толщины изоляции либо говорим что нет такой
            height = max(heights)
            width = max(widths)
            self.insulation_height = ins_heights[height]
            self.insulation_width = ins_widths[width]
        except ValueError:
            raise ValueError("Для требуемых размеров проводника заданного типа параметры изоляции не определены")

    def pick_wire(self,
                  max_wire_height: float,
                  max_wire_width: float
                  ) -> None:
        """
        Метод, осуществляющий автоматический выбор стандартного проводника и толщины изоляции по максимально допустимым
        размерам изолированного проводника.

        :param max_wire_height: Максимальная высота изолированного проводника в мм.
        :param max_wire_width: Максимальная высота изолированного проводника в мм.
        """
        self.__pick_insulation(max_wire_height, max_wire_width)
        super().pick_wire(max_wire_height, max_wire_width)


class PETVSD(WireType):
    r"""
    Класс, описывающий обмоточные проводники типа ПЭТВСД.

    Атрибуты:

    * ``insulation_height: Optional[float]``

      Толщина изоляции проводника по высоте в мм (в расчётных методиках --- параметр `\Delta a`:math:). Имеет значение
      ``None`` в момент инициализации. То же верно для остальных полей.

    * ``insulation_width: Optional[float]``

      Толщина изоляции проводника по ширине в мм (в методиках --- `\Delta b`:math:).

    * ``wire_height: Optional[float]``

      Высота неизолированной части проводника в мм (параметр `a`:math:).

    * ``wire_width: Optional[float]``

      Ширина неизолированной части проводника в мм (параметр `b`:math:). ``insulation_width`` и ``insulation_height``
      связаны с размерами проводника согласно СТО.

    * ``wire_section: Optional[float]``

      Площадь сечения проводника в мм².

    Методы:

    * ``pick_wire(max_wire_height: float, max_wire_width: float) -> None``

      Подбирает проводник *с учётом изоляции,* а также саму толщину изоляции.

    Наследует класс ``WireType``.
    """

    # А-а-а-а! Ещё более страшный монстр пришёл! Не-е-е-ет! Не надо! Кто-нибудь, помогите, меня ПЭТВСД обижает!
    def __pick_insulation(self,
                          max_wire_height: float,
                          max_wire_width: float
                          ) -> None:
        """
        Вспомогательный метод, осуществляющий подбор толины изоляции в соответствии с СТО.

        :param max_wire_height: Максимальная высота изолированного проводника в мм.
        :param max_wire_width: Максимальная высота изолированного проводника в мм.
        """

        ins_heights = {1.31: 0.41, 1.53: 0.41, 2.47: 0.47, 4.03: 0.48}
        ins_widths = {1.31: {2.45: 0.45, 2.95: 0.45, 4.22: 0.47, 4.98: 0.48, 6.09: 0.49, 7.63: 0.53},
                      1.53: {2.45: 0.45, 2.95: 0.45, 4.23: 0.48, 4.98: 0.48, 6.09: 0.49, 7.65: 0.55, 10.56: 0.56},
                      2.47: {2.96: 0.46, 4.23: 0.48, 5.00: 0.50, 6.13: 0.53, 7.66: 0.56, 10.57: 0.57},
                      4.03: {5.02: 0.52, 6.13: 0.53, 7.67: 0.57, 10.57: 0.57}}

        try:
            heights = filter(lambda h: h <= max_wire_height, ins_heights.keys())
            height = max(heights)

            widths = filter(lambda w: w <= max_wire_width, ins_widths[height].keys())
            width = max(widths)

            self.insulation_height = ins_heights[height]
            self.insulation_width = ins_widths[height][width]
        except ValueError:
            raise ValueError("Для требуемых размеров проводника заданного типа параметры изоляции не определены")

    def pick_wire(self,
                  max_wire_height: float,
                  max_wire_width: float
                  ) -> None:
        """
        Метод, осуществляющий автоматический выбор стандартного проводника и толщины изоляции по максимально допустимым
        размерам изолированного проводника.

        :param max_wire_height: Максимальная высота изолированного проводника в мм.
        :param max_wire_width: Максимальная высота изолированного проводника в мм.
        """

        self.__pick_insulation(max_wire_height, max_wire_width)
        super().pick_wire(max_wire_height, max_wire_width)

    def __str__(self) -> str:
        return "ПЭТВСД"


class CustomWire(WireType):
    r"""
    Класс, описывающий пользовательский вариант изоляции элементарного проводника обмотки.

    Атрибуты:

    * ``insulation_height: Optional[float]``

      Толщина изоляции проводника по высоте в мм (в расчётных методиках --- параметр `\Delta a`:math:). Имеет значение
      ``None`` в момент инициализации. То же верно для остальных полей.

    * ``insulation_width: Optional[float]``

      Толщина изоляции проводника по ширине в мм (в методиках --- `\Delta b`:math:).

    * ``wire_height: Optional[float]``

      Высота неизолированной части проводника в мм (параметр `a`:math:).

    * ``wire_width: Optional[float]``

      Ширина неизолированной части проводника в мм (параметр `b`:math:). ``insulation_width`` и ``insulation_height``
      связаны с размерами проводника согласно СТО.

    * ``wire_section: Optional[float]``

      Площадь сечения проводника в мм².

    Методы:

    * ``set_insulation(self, insulation_height: float, insulation_width: float) -> None``

      Устанавливает толщину изоляции. Служит вспомогательным методом, присутствующим только в этом классе. Упрощает
      унификацию интерфейса.

    * ``pick_wire(max_wire_height: float, max_wire_width: float) -> None``

      Подбирает проводник *с учётом изоляции.* В сущности, служит шлюзом к методу ``pick_wire`` класса ``WireDB``.

    Наследует класс ``WireType``.
    """

    def __str__(self) -> str:
        return "Пользовательский"

    def set_insulation(self,
                       insulation_height: float,
                       insulation_width: float
                       ) -> None:
        """
        Метод, устанавливающий толщину изоляции для пользовательского типа проводника.

        :param insulation_height: Заданная пользователем толщина изоляции по высоте проводника, в мм.
        :param insulation_width: Заданная пользователем толщина изоляции по ширине проводника, в мм.
        """

        self.insulation_height = insulation_height
        self.insulation_width = insulation_width
