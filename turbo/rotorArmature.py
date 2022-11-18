"""
Модуль, содержащий описание роторной обмотки турбомашины.

Классы:

* ``TurboMachineRotorArmature``

  Класс, описывающий обмотку ротора турбомашины.
"""


from typing import Optional, Dict, Union

from common.wireDatabase import BusDB
from turbo.armatureInsulation import TurboMachineRotorInsulation


class TurboMachineRotorArmature:
    """
    Класс, описывающий статорную обмотку катушечного типа машины переменного тока.

    Атрибуты:

    * ``insulation: TurboMachineRotorInsulation``

      Изоляция роторной обмотки.

    * ``parallel_branches: int``

      Число параллельных ветвей обмотки.

    * ``wire_height: float``

      Высота используемого обмоточного проводника (шины), мм.

    * ``wire_width: float``

      Ширина используемого обмоточного проводника (шины), мм.

    * ``wire_section: float``

      Сечение используемого обмоточного проводника (шины), мм².

    * ``turn_count: Union[int, float, None]``

      Число витков катушки. В момент инициализации равно ``None``. Может быть типов ``int`` (в нормальном случае) или
      ``float`` (в случае дробного числа витков в фазе).

    * ``turn_length: Optional[float]``

      Длина витка, мм. В момент инициализации равна ``None``.

    * ``resistance: Optional[Dict[int, float]]``

      Сопротивление обмотки постоянному току, Ом. Рассчитывается для температур 15, 75, 100, 115 и 120 градусов
      Цельсия. В момент инициализации равно ``None``.

    * ``current_density: Optional[float]``

      Плотность тока в обмотке, А/мм². В момент инициализации равна ``None``.

    Методы:

    * ``compute_turn_count_per_branch(pole_pairs: int, slots_per_pole_phase: int, effective_wires: int) -> None``

      Рассчитывает число витков в параллельной ветви обмотки.

    * ``compute_turn_length(stator_length: float, diameter: float, pole_pairs: int) -> None``

      Рассчитывает длину витка обмотки.

    * ``compute_resistance(conductivity: float) -> None``

      Рассчитывает сопротивление обмотки при разных температурах. Сохраняет в словарь.

    * ``compute_current_density(current: float) -> None``

      Рассчитывает плотность тока в обмотке.

    Реализует паттерн «Одиночка», поскольку ротор не может иметь более одной обмотки.
    """

    __slots__ = ["insulation",
                 "parallel_branches",
                 "wire_height",
                 "wire_width",
                 "wire_section",
                 "equivalent_wire_section",
                 "turn_count",
                 "turn_length",
                 "resistance",
                 "current_density"]

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self,
                 parallel_branches: int,
                 insulation: TurboMachineRotorInsulation,
                 wire_height: float,
                 wire_width: float
                 ) -> None:
        self.parallel_branches = parallel_branches  # Число параллельных ветвей

        self.turn_count: Union[int, float, None] = None
        self.turn_length: Optional[float] = None

        self.insulation = insulation
        self.wire_height, self.wire_width, self.wire_section = BusDB().pick_bus(wire_height, wire_width)
        self.equivalent_wire_section: Optional[float] = None

        self.resistance: Optional[Dict[int, float]] = None  # Сопротивление обмотки
        self.current_density: Optional[float] = None

    @staticmethod
    def get_turn_end_part_length(diameter: float,
                                 pole_pairs: int
                                 ) -> float:
        """
        Вспомогательный метод, рассчитывающий длину лобовой части полувитка обмотки.

        :param diameter: Диаметр ротора по расточке, мм.
        :param pole_pairs: Количество пар полюсов машины.
        :return: Длина лобовой части полувитка, мм.
        """
        return 1.35 * diameter / pole_pairs ** 0.8

    def compute_turn_count(self,
                           effective_wires: int,
                           effective_wires_small: Optional[int],
                           coils_per_pole: Union[int, float]) -> None:
        """
        Метод, рассчитывающий число витков в параллельной ветви обмотки.

        :param effective_wires: Количество эффективных проводников в пазу.
        :param effective_wires_small: Количество эффективных проводников в малом пазу.
        :param coils_per_pole: Количество катушек на полюс.
        """

        if effective_wires_small is not None:
            self.turn_count = (effective_wires * (coils_per_pole - 1) + effective_wires_small) / self.parallel_branches
        else:
            self.turn_count = (effective_wires * (coils_per_pole - 1)) / self.parallel_branches

        if self.turn_count.is_integer():
            self.turn_count = int(self.turn_count)

    def compute_turn_length(self,
                            rotor_length: float,
                            diameter: float,
                            pole_pairs: int
                            ) -> None:
        """
        Метод, рассчитывающий длину витка обмотки.

        :param rotor_length: Длина ротора статора (длина паза), мм.
        :param diameter: Диаметр ротора по расточке, мм.
        :param pole_pairs: Количество пар полюсов машины.
        """

        end_part_length = self.get_turn_end_part_length(diameter, pole_pairs)
        self.turn_length = 2 * (end_part_length + rotor_length)

    def compute_resistance(self,
                           conductivity: float,
                           rotor_length: float,
                           diameter: float,
                           pole_pairs: int,
                           vert_vent_channel_length: float,
                           vert_vent_channel_width: float,
                           vert_vent_channel_pitch: float
                           ) -> None:
        """
        Метод, рассчитывающий сопротивление обмотки.

        :param conductivity: Удельная проводимость материала обмотки, мм/Ом∙мм².
        :param rotor_length: Длина ротора статора (длина паза), мм.
        :param diameter: Диаметр ротора по расточке, мм.
        :param pole_pairs: Количество пар полюсов машины.
        :param vert_vent_channel_pitch: Шаг вертикальных вентиляционных каналов, мм.
        :param vert_vent_channel_width: Ширина вертикальных вентиляционных каналов, мм.
        :param vert_vent_channel_length: Длина вертикальных вентиляционных каналов, мм.
        """

        if vert_vent_channel_pitch is not None:
            adj_factor = 1 - vert_vent_channel_length * vert_vent_channel_width /\
                vert_vent_channel_pitch / self.wire_width
        else:
            adj_factor = 1

        self.equivalent_wire_section = self.wire_section * adj_factor
        end_part_length = self.get_turn_end_part_length(diameter, pole_pairs)

        # Номинальное значение сопротивления
        base_value = 4 * pole_pairs * self.turn_count / conductivity / self.parallel_branches * \
            (rotor_length / self.equivalent_wire_section + end_part_length / self.wire_section)

        # Словарь из значений сопротивления при 15, 75, 105 и 120 градусах
        self.resistance = dict(zip([15, 75, 100, 115, 120],
                                   map(lambda x: x * base_value, [1, 1.24, 1.34, 1.4, 1.42])))

    def compute_current_density(self,
                                current: float
                                ) -> None:
        """
        Метод, рассчитывающий плотность тока в обмотке.

        :param current: Ток в обмотке, А.
        """

        self.current_density = current / self.parallel_branches / self.equivalent_wire_section


__all__ = ["TurboMachineRotorArmature"]
