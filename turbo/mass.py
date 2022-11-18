"""
Модуль, хранящий описание расчёта массы турбомашины.

Классы:

* ``Mass``

  Единственный класс модуля, хранящий и рассчитывающий массы частей машины.
"""

from typing import Optional
import math

from common.constants import COPPER_DENSITY, STEEL_DENSITY
from common.stator import ACMachineStator
from turbo.rotor import TurboMachineRotor


class Mass:
    """
    Класс, хранящий и рассчитывающий массы частей турбомашины.

    Атрибуты:

    * ``stator_teeth``

      Суммарная масса зубцов статора, кг.

    * ``stator_yoke``

      Масса ярма статора, кг.

    * ``stator_armature``

      Масса обмотки статора, кг.

    * ``rotor_armature``

      Масса обмотки ротора, кг.

    * ``rotor``

      Общая масса ротора, кг.

    Методы:

    * ``compute_stator_masses(stator: ACMachineStator, phase_count: int) -> None``

      Рассчитывает массы частей статора.

    * ``compute_rotor_masses(rotor: TurboMachineRotor, pole_pairs: int) -> None``

      Рассчитывает массы частей ротора.

    * ``get_total_copper_mass() -> float``

      Возвращает суммарную массу меди в машине.

    * ``get_stator_steel_mass(self) -> float``

      Возвращает общую массу стали статора.

    Реализует паттерн «Одиночка».
    """

    __slots__ = ["stator_teeth",
                 "stator_yoke",
                 "stator_armature",
                 "rotor_armature",
                 "rotor"
                 ]

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self) -> None:
        self.stator_teeth: Optional[float] = None
        self.stator_yoke: Optional[float] = None
        self.stator_armature: Optional[float] = None

        self.rotor_armature: Optional[float] = None
        self.rotor: Optional[float] = None

    def compute_stator_masses(self,
                              stator: ACMachineStator,
                              phase_count: int
                              ) -> None:
        """
        Метод, рассчитывающий массы частей статора.

        :param stator: Объект, представляющий статор турбомашины.
        :param phase_count: Число фаз машины.
        """

        self.stator_yoke = STEEL_DENSITY * math.pi / 4 *\
            (stator.outer_diameter ** 2 - stator.get_diameter_bottom() ** 2) * stator.effective_length * 1e-9

        # А вот массу зубчиков я посчитаю не совсем так, как написано в методике, но мой вариант даёт эквивалентный
        # результат, избавляя меня при этом от необходимости дописывать ещё несколько методов
        self.stator_teeth = STEEL_DENSITY * stator.effective_length *\
            (math.pi / 4 * (stator.get_diameter_bottom() ** 2 - stator.inner_diameter ** 2) -
             stator.slot_count * stator.slot_height * stator.slot_width) * 1e-9

        copper_section = stator.armature.rows * stator.armature.columns * stator.armature.wire.wire_section
        self.stator_armature = COPPER_DENSITY * phase_count * stator.armature.parallel_branches * copper_section *\
            stator.armature.turn_length * stator.armature.turn_count * 1e-9

    def compute_rotor_masses(self,
                             rotor: TurboMachineRotor,
                             pole_pairs: int
                             ) -> None:
        """
        Метод, рассчитывающий массы частей ротора.

        :param rotor: Объект, представляющий ротор турбомашины.
        :param pole_pairs: Число пар полюсов машины.
        """

        end_part_length = rotor.armature.get_turn_end_part_length(rotor.outer_diameter, pole_pairs)
        self.rotor_armature = COPPER_DENSITY * 4 * pole_pairs * rotor.armature.parallel_branches *\
            rotor.armature.turn_count * (rotor.armature.equivalent_wire_section * rotor.length +
                                         rotor.armature.wire_section * end_part_length) * 1e-9

        # Это, короче, такой колдунский способ прикинуть массу ротора вместе с валом и прочими свистелками, на него
        # навешанными. Просто взять невразумительную плотность, да ещё потом на полтора умножить. И некоторые ещё после
        # этого удивляются, почему я бросил инженерное дело. Потому что там все творят вот такое безумие
        self.rotor = 7850 * 1.5 * math.pi / 4 * rotor.outer_diameter ** 2 * rotor.length * 1e-9

    def get_total_copper_mass(self) -> float:
        """
        Метод, возвращающий суммарную массу меди в машине.

        :return: Масса меди, кг.
        """

        return self.stator_armature + self.rotor_armature

    def get_stator_steel_mass(self) -> float:
        """
        Метод, возвращающий суммарную массу стали статора.

        :return: Масса стали, кг.
        """

        return self.stator_yoke + self.stator_teeth


__all__ = "Mass"
