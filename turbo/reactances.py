"""
Модуль, содержащий описание расчёта реактивных сопротивлений турбомашины.

Классы:

* ``Reactances``

  Единственный класс модуля, хранящий и рассчитывающий реактивные сопротивления.
"""

from typing import Optional

from common.stator import ACMachineStator
from turbo.rotor import *


class Reactances:
    """
    Класс, хранящий и рассчитывающий реактивные сопротивления турбомашин (т. н. «иксы»).

    Атрибуты:

    * ``rotor_dissipation_factor``

      Коэффициент рассеяния роторной обмотки.

    * ``x_stator``

      Реактивное сопротивление рассеяния обмотки статора, о. е.

    * ``x_ad``

      Продольное реактивное сопротивление реакции якоря, о. е.

    * ``x_d``

      Продольное синхронное реактивное сопротивление обмотки статора для прямого порядка следования фаз, о. е.

    * ``x_d_prime``

      Продольное переходное реактивное сопротивление обмотки статора, о. е.

    * ``x_d_2prime``

      Продольное сверхпереходное реактивное сопротивление обмотки статора, о. е.

    * ``x_P``

      Реактивное сопротивление Потье, о. е.

    * ``x_total``

      Суммарное реактивное сопротивление, о. е.

    * ``x_rotor``

      Реактивное сопротивление рассеяния обмотки ротора, о. е.

    * ``x_0``

      Реактивное сопротивление нулевой последовательности, о. е.

    * ``x_2``

      Реактивное сопротивление обратной последовательности, о. е.

    Методы:

    * ``compute_x_ad(stator_reaction_current: float, magnetizing_current: float) -> None``

      Рассчитывает продольное реактивное сопротивление реакции якоря `x_{ad}`:math:.

    * ``compute_stator_armature_reactance(stator: ACMachineStator, air_gap: float, pole_pairs: int) -> None``

      Рассчитывает реактивное сопротивление рассеяния обмотки статора `x_l`:math:.

    * ``compute_x_d() -> None``

      Рассчитывает продольное синхронное реактивное сопротивление обмотки статора `x_d`:math:.

    * ``compute_rotor_dissipation_factor(rotor: TurboMachineRotor, pole_pairs: int, magnetizing_current: float,
      no_load_total_flow: float) -> None``

      Рассчитывает коэффициент рассеяния роторной обмотки.

    * ``compute_x_prime() -> None``

      Рассчитывает продольные переходное и сверхпереходное реактивные сопротивления обмотки статора `x_d'`:math: и
      `x_d''`:math:.

    * ``compute_x_Potier(bandaging: TurboMachineRotorBandaging) -> None``

      Рассчитывает реактивное сопротивление Потье `x_P`:math:.

    * ``compute_total_reactance() -> None``

      Рассчитывает полное реактивное сопротивление `x`:math: и реактивное сопротивление рассеяния обмотки ротора
      `x_f`:math:.

    * ``compute_zero_sequence_reactance(stator: ACMachineStator, rotor_armature_coefficient: float,
      pole_pairs: int) -> None``

      Рассчитывает реактивное сопротивление нулевой последовательности `x_0`:math:.

    * ``compute_reverse_sequence_reactance(damping: bool = False) -> None``

      Рассчитывает реактивное сопротивление обратной последовательности `x_2`:math:.

    Реализует паттерн «Одиночка».
    """
    # Как ни прискорбно, но тут придётся всё хранить в виде атрибутов класса, потому что все эти иксы дурные нужны в
    # куче мест после этого

    __slots__ = ["__k_beta",
                 "__k_x",
                 "__l_x",
                 "__end_part_reactance",
                 "rotor_dissipation_factor",
                 "x_stator",
                 "x_ad",
                 "x_d",
                 "x_d_prime",
                 "x_d_2prime",
                 "x_P",
                 "x_total",
                 "x_rotor",
                 "x_0",
                 "x_2"]

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self,
                 stator: ACMachineStator,
                 current: float,
                 voltage: float,
                 frequency: float,
                 pole_pairs: int,
                 phase_count: int
                 ) -> None:
        # Дурные коэффициенты. Обожаю коэффициенты. Нет. Ненавижу, на самом деле. Из-за них приходится всю структуру
        # класса менять, чёрт побери
        self.__k_beta: Optional[float] = None
        self.__k_x: Optional[float] = None
        self.__l_x: Optional[float] = None
        self.__compute_crazy_coefficients(stator, current, voltage, frequency, pole_pairs, phase_count)

        self.rotor_dissipation_factor: Optional[float] = None

        self.__end_part_reactance: Optional[float] = None
        self.__compute_end_part_reactance(stator, pole_pairs)

        # Тут почти та же ситуация, что и с лямбдами в магнитной цепи. Обычно у меня имена понятные, но тут они просто
        # слишком длинные будут. Да и иксы эти - редкое исключение, когда у всех настолько одинаковые обозначения и все
        # настолько к ним привыкли, что проще написать кучу иксов
        self.x_stator: Optional[float] = None
        self.x_ad: Optional[float] = None
        self.x_d: Optional[float] = None
        self.x_d_prime: Optional[float] = None
        self.x_d_2prime: Optional[float] = None
        self.x_P: Optional[float] = None
        self.x_total: Optional[float] = None
        self.x_rotor: Optional[float] = None
        self.x_0: Optional[float] = None
        self.x_2: Optional[float] = None

    def __compute_crazy_coefficients(self,
                                     stator: ACMachineStator,
                                     current: float,
                                     voltage: float,
                                     frequency: float,
                                     pole_pairs: int,
                                     phase_count: int
                                     ) -> None:
        """
        Вспомогательный метод, рассчитывающий коэффициенты `K_β`:math:, `K_x`:math: и `l_x`:math:.

        :param stator: Объект, представляющий статор турбомашины.
        :param current: Ток статора, А.
        :param voltage: Напряжение статора, В.
        :param frequency: Частота сети, Гц.
        :param pole_pairs: Число пар полюсов машины.
        :param phase_count: Число фаз машины.
        """

        beta = stator.armature.shortening
        self.__k_beta = (3 * beta + 1) / 4 if beta > 2 / 3 else (6 * beta - 1) / 4

        # 15000 - это комбинация тройки, на которую делится число фаз, 50-ти, на которые делится частота и 100, на
        # которые делится квадрат числа витков
        self.__k_x = 0.407 * stator.armature.turn_count ** 2 * current * frequency * phase_count / 15000 / pole_pairs /\
            voltage

        self.__l_x = stator.length
        if stator.vent_channel_count is not None:
            self.__l_x -= 0.2 * stator.vent_channel_count * stator.vent_channel_width
        self.__l_x *= 0.1

    def __compute_end_part_reactance(self,
                                     stator: ACMachineStator,
                                     pole_pairs: int
                                     ) -> None:
        """
        Вспомогательный метод, рассчитывающий реактивное сопротивление лобовой части обмотки.

        :param stator: Объект, представляющий статор турбомашины.
        :param pole_pairs: Число пар полюсов машины.
        """

        # 0.15 - это комбо из 0.3 в формуле и деления на 2
        self.__end_part_reactance = 0.15 * self.__k_x * (3 * stator.armature.shortening - 1) * stator.inner_diameter /\
                                    pole_pairs / 1e3

    def compute_x_ad(self,
                     stator_reaction_current: float,
                     magnetizing_current: float
                     ) -> None:
        """
        Метод, рассчитывающий продольное реактивное сопротивление реакции якоря.

        :param stator_reaction_current: Ток реакции якоря, А.
        :param magnetizing_current: Ток намагничивания, А.
        """

        self.x_ad = stator_reaction_current / magnetizing_current

    def compute_stator_armature_reactance(self,
                                          stator: ACMachineStator,
                                          air_gap: float,
                                          pole_pairs: int
                                          ) -> None:
        """
        Метод, рассчитывающий реактивное сопротивление рассеяния обмотки статора.

        :param stator: Объект, представляющий статор турбомашины.
        :param air_gap: Воздушный зазор в машине, мм.
        :param pole_pairs: Число пар полюсов машины.
        """

        h_11, h_31, h_2s = stator.armature.get_auxiliary_dimensions(stator.wedge_height, stator.slit_height)
        x_slot = 2 * pole_pairs * self.__l_x * self.__k_x * self.__k_beta / stator.slot_count *\
            ((3 * h_31 + h_11) / 3 / stator.slot_width + 0.2 + air_gap / (2 * stator.tooth_pitch + air_gap / 2)) / 100
        x_diff = 0.375 * air_gap * stator.tooth_pitch * self.x_ad / stator.pole_pitch / stator.slots_per_pole_phase /\
            stator.armature.columns / stator.armature.wire.wire_width

        self.x_stator = x_slot + x_diff + self.__end_part_reactance

    def compute_x_d(self) -> None:
        """
        Метод, рассчитывающий продольное синхронное реактивное сопротивление обмотки статора.
        """

        self.x_d = self.x_ad + self.x_stator

    def compute_rotor_dissipation_factor(self,
                                         rotor: TurboMachineRotor,
                                         pole_pairs: int,
                                         magnetizing_current: float,
                                         no_load_total_flow: float
                                         ) -> None:
        """
        Метод, рассчитывающий коэффициент рассеяния роторной обмотки.

        :param rotor: Объект, представляющий ротор турбомашины.
        :param pole_pairs: Число пар полюсов машины.
        :param magnetizing_current: Ток намагничивания, А.
        :param no_load_total_flow: Полный магнитный поток в машине на холостом ходу, Вб.
        """

        self.rotor_dissipation_factor = 1 + 0.0835 * magnetizing_current * rotor.effective_wires * rotor.length /\
                                        no_load_total_flow / rotor.get_armature_coefficient(pole_pairs) *\
                                        ((2 * (rotor.wedge_height + rotor.armature.insulation.wedge_filling) +
                                          rotor.slot_height - rotor.armature.insulation.bottom_filling -
                                          rotor.armature.insulation.body_insulation) / rotor.slot_width +
                                         rotor.air_gap / (2 * rotor.tooth_pitch + rotor.air_gap / 2)) * 1e-8

    def compute_x_prime(self) -> None:
        """
        Метод, рассчитывающий продольные переходное и сверхпереходное реактивные сопротивления обмотки статора.
        """

        self.x_d_prime = self.x_d - self.x_ad / self.rotor_dissipation_factor
        self.x_d_2prime = self.x_stator + 0.025

    def compute_x_Potier(self,
                         bandaging: TurboMachineRotorBandaging
                         ) -> None:
        """
        Метод, рассчитывающий реактивное сопротивление Потье.

        :param bandaging: Объект, представляющий бандажи ротора.
        """

        self.x_P = 0.8 * self.x_d_prime

        if bandaging.ismagnetic:
            self.x_P += self.__end_part_reactance / 2

    def compute_total_reactance(self) -> None:
        """
        Метод, рассчитывающий полное реактивное сопротивление и реактивное сопротивление рассеяния обмотки ротора.
        """

        self.x_total = self.rotor_dissipation_factor * self.x_ad
        self.x_rotor = (self.rotor_dissipation_factor - 1) * self.x_ad

    def compute_zero_sequence_reactance(self,
                                        stator: ACMachineStator,
                                        rotor_armature_coefficient: float,
                                        pole_pairs: int
                                        ) -> None:
        """
        Метод, рассчитывающий реактивное сопротивление нулевой последовательности.

        :param stator: Объект, представляющий статор турбомашины.
        :param rotor_armature_coefficient: Обмоточный коэффициент роторной обмотки.
        :param pole_pairs: Число пар полюсов машины.
        """

        beta = stator.armature.shortening
        h_11, h_31, h_2s = stator.armature.get_auxiliary_dimensions(stator.wedge_height, stator.slit_height)

        coef_1 = 2 * pole_pairs * self.__k_x * self.__l_x / stator.slot_count / stator.slot_width
        coef_2 = 2 * self.x_ad * rotor_armature_coefficient / stator.get_armature_coefficient() ** 2
        coef_3 = 4 * (pole_pairs / stator.slot_count) ** 2

        if beta > 2 / 3:
            coef_4 = beta - 2 / 3
            self.x_0 = coef_1 * ((3 * beta - 2) * h_31 + h_11 * (9 * beta - 5) / 12 - h_2s * (9 * beta - 8) / 12) /\
                100 + coef_2 * coef_4 * (coef_3 + 0.037 + 0.39 * coef_4 - coef_4 ** 2)
        else:
            coef_4 = 2 / 3 - beta
            self.x_0 = coef_1 * ((2 - 3 * beta) * h_31 + h_11 * (7 - 9 * beta) / 12 - h_2s * (4 - 9 * beta) / 12) /\
                100 + coef_2 * coef_4 * (coef_3 + 0.5 * coef_4 - coef_4 ** 2)

    def compute_reverse_sequence_reactance(self,
                                           damping: bool = False
                                           ) -> None:
        """
        Метод, рассчитывающий реактивное сопротивление обратной последовательности.

        :param damping: Флаг, указывающий на наличие/отсутствие демпферной системы в больших зубцах ротора.
        """

        if damping:
            self.x_2 = 1.05 * self.x_d_2prime
        else:
            self.x_2 = 1.22 * self.x_d_2prime


__all__ = "Reactances"
