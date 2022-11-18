"""
Модуль, содержащий описание статора машин переменного тока.

Классы:

* ``ACMachineStator``

  Класс, описывающий статор машины переменного тока.
"""

import math
from typing import Optional, Tuple, Union

from common.statorArmature import *


class ACMachineStator:
    """
    Класс, описывающий статор машины переменного тока. Универсальный класс, подходящий для всех типов машин.

    Атрибуты:

    * ``outer_diameter: float``

      Внешний диаметр сердечника, мм.

    * ``inner_diameter: float``

      Внутренний диаметр сердечника (диаметр по расточке), мм.

    * ``length: float``

      Полная длина сердечника, мм.

    * ``slot_count: int``

      Число пазов.

    * ``slot_height: float``

      Глубина/высота паза в свету, мм.

    * ``slot_width: float``

      Ширина паза в свету, мм.

    * ``slit_height: float``

      Высота шлица (расстояние от расточки до клина), мм.

    * ``wedge_height: float``

      Высота пазового клина, мм.

    * ``effective_wires: int``

      Количество эффективных проводников в пазу.

    * ``armature: CoilArmature``

      Статорная обмотка. Является объектом соответствующего типа.

    * ``vent_channel_count: Optional[int]``

      Число вентиляционных каналов статора. В случае их отсутствия равно ``None``.

    * ``vent_channel_width: Optional[float]``

      Ширина вентиляционных каналов статора, мм. В случае их отсутствия равна ``None``.

    * ``stud_count: Optional[int]``

      Число стягивающих шпилек в статоре. В случае их отсутствия равно ``None``.

    * ``stud_diameter: Optional[float]``

      Диаметр стягивающих шпилек, мм. В случае их отсутствия равен ``None``.

    * ``bypass_thickness: Optional[float]``

      Толщина шунтов статора, мм. В случае их отсутствия равна ``None``.

    * ``pressure_plate_thickness: Optional[float]``

      Толщина нажимной пластины статора, мм. В случае её отсутствия равна ``None``.

    * ``copper_screen_thickness: Optional[float]``

      Толщина медного экрана статора, мм. В случае его отсутствия равна ``None``.

    * ``slots_per_pole_phase: Union[int, float, None]``

      Число пазов на полюс и фазу. В момент инициализации равно ``None``.

    * ``pole_pitch: Optional[float]``

      Полюсное деление, мм. В момент инициализации равно ``None``.

    * ``tooth_pitch: Optional[float]``

      Зубцовое деление, мм. В момент инициализации равно ``None``.

    * ``current_load: Optional[float]``

      Линейная токовая нагрузка статора, А/см. В момент инициализации равна ``None``.

    Методы:

    * ``compute_slots_per_pole_phase(pole_pairs: int, phase_count: int) -> None``

      Вычисляет число пазов на полюс и фазу.

    * ``compute_pole_pitch(pole_pairs: int) -> None``

      Вычисляет полюсное деление.

    * ``compute_tooth_pitch() -> None``

      Вычисляет зубцовое деление.

    * ``compute_effective_length(fill_factor: float) -> None``

      Вычисляет эффективную длину сердечника статора, мм.

    * ``compute_current_load(current: float) -> None``

      Вычисляет линейную токовую нагрузку якоря.

    * ``get_heat_load(self) -> float``

      Возвращает произведение линейной токовой нагрузки на плотность тока в обмотке (тепловую нагрузку), А²/см∙мм².

    * ``get_stamp_slot_dimensions(assembly_allowance: float, stamp_allowance: float) -> Tuple[float, float]``

      Возвращает глубину и ширину паза в штампе, мм.

    * ``get_armature_coefficient() -> float``

      Возвращает обмоточный коэффициент статора.

    * ``get_diameter_third() -> float``

      Возвращает диаметр статора на уровне `1/3`:math: высоты зубца, мм.

    * ``get_diameter_bottom() -> float``

      Возвращает диаметр статора на уровне дна паза, мм.

    * ``get_tooth_pitch_third() -> float``

      Возвращает зубцовое деление статора на уровне `1/3`:math: высоты зубца, мм.

    * ``get_tooth_pitch_bottom() -> float``

      Возвращает зубцовое деление статора на уровне дна паза, мм.

    * ``get_yoke_height() -> float``

      Возвращает эффективную высоту ярма статора (с учётом шпилек), мм.

    * ``get_yoke_section(effective_length: float) -> float``

      Возвращает эффективное сечение ярма статора, м².

    * ``get_teeth_section_third(effective_length: float) -> float``

      Возвращает суммарное сечение зубцов на уровне `1/3`:math: их высоты, м².

    * ``get_yoke_magnetic_line(rotor_surface_relation: float) -> float``

      Возвращает длину магнитной линии в ярме, см.

    * ``get_tooth_magnetic_line() -> float``

      Возвращает длину магнитной линии в зубце, см.

    * ``get_flow_branching_factor(effective_length: float) -> float``

      Возвращает коэффициент ответвления магнитного потока в пазы статора.

    Реализует паттерн «Одиночка».
    """

    __slots__ = ["outer_diameter",
                 "inner_diameter",
                 "length",
                 "effective_length",
                 "slot_count",
                 "slot_height",
                 "slot_width",
                 "slit_height",
                 "wedge_height",
                 "effective_wires",
                 "armature",
                 "vent_channel_count",
                 "vent_channel_width",
                 "stud_count",
                 "stud_diameter",
                 "bypass_thickness",
                 "pressure_plate_thickness",
                 "copper_screen_thickness",
                 "slots_per_pole_phase",
                 "pole_pitch",
                 "tooth_pitch",
                 "current_load"
                 ]

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self,
                 outer_diameter: float,
                 inner_diameter: float,
                 length: float,
                 slot_count: int,
                 slot_height: float,
                 slot_width: float,
                 slit_height: float,
                 wedge_height: float,
                 effective_wires: int,
                 armature: CoilArmature,  # Вообще-то тут должен стоять более общий тип, но его тут не появится, пока я
                 # не научусь считать стержневую обмотку
                 vent_channel_count: Optional[int] = None,
                 vent_channel_width: Optional[float] = None,
                 stud_count: Optional[int] = None,
                 stud_diameter: Optional[float] = None,
                 bypass_thickness: Optional[float] = None,
                 pressure_plate_thickness: Optional[float] = None,
                 copper_screen_thickness: Optional[float] = None
                 ) -> None:
        self.outer_diameter = outer_diameter  # Внешний диаметр
        self.inner_diameter = inner_diameter  # Внутренний диаметр
        self.length = length  # Длина сердечника
        self.effective_length: Optional[float] = None  # Эффективная длина сердечника

        self.slot_count = slot_count  # Число пазов
        self.slot_height = slot_height  # Высота паза
        self.slot_width = slot_width  # Ширина паза
        self.slit_height = slit_height  # Высота шлица
        self.wedge_height = wedge_height  # Высота клина
        self.effective_wires = effective_wires  # Число эффективных проводников в пазу
        self.armature = armature  # Обмотка

        self.vent_channel_count = vent_channel_count  # Число вентиляционных каналов статора
        self.vent_channel_width = vent_channel_width  # Их ширина

        self.stud_count = stud_count  # Число стягивающих шпилек
        self.stud_diameter = stud_diameter  # ...и их диаметр

        self.bypass_thickness = bypass_thickness  # Толщина шунта статора
        self.pressure_plate_thickness = pressure_plate_thickness  # Толщина нажимной пластины
        self.copper_screen_thickness = copper_screen_thickness  # Толщина медного экрана

        self.slots_per_pole_phase: Union[int, float, None] = None  # Число пазов на полюс и фазу
        self.pole_pitch: Optional[float] = None  # Полюсное деление
        self.tooth_pitch: Optional[float] = None  # Зубцовое деление
        self.current_load: Optional[float] = None  # Линейная токовая нагрузка

    def compute_slots_per_pole_phase(self,
                                     pole_pairs: int,
                                     phase_count: int
                                     ) -> None:
        """
        Метод, рассчитывающий число пазов статора на полюс и фазу.

        :param pole_pairs: Количество пар полюсов машины.
        :param phase_count: Число фаз.
        """

        self.slots_per_pole_phase = self.slot_count / 2 / pole_pairs / phase_count
        if self.slots_per_pole_phase == (int_count := int(self.slots_per_pole_phase)):
            self.slots_per_pole_phase = int_count

    def compute_pole_pitch(self,
                           pole_pairs: int
                           ) -> None:
        """
        Метод, рассчитывающий полюсное деление.

        :param pole_pairs: Количество пар полюсов машины.
        """

        self.pole_pitch = math.pi * self.inner_diameter / 2 / pole_pairs

    def compute_tooth_pitch(self) -> None:
        """
        Метод, рассчитывающий зубцовое деление статора.
        """

        self.tooth_pitch = math.pi * self.inner_diameter / self.slot_count

    def compute_effective_length(self,
                                 fill_factor: float  # А может прикрутить значение по умолчанию?
                                 ) -> None:
        """
        Метод, рассчитывающий эффективную длину статора с учётом вентиляционных каналов и шунтов (суммарную длину чистой
        стали).

        :param fill_factor: Коэффициент заполнения статора сталью.
        """

        length = self.length
        if self.bypass_thickness is not None:
            length -= 2 * self.bypass_thickness
        if self.vent_channel_count is not None:
            length -= self.vent_channel_width * self.vent_channel_count

        self.effective_length = length * fill_factor

    def compute_current_load(self,
                             current: float
                             ) -> None:
        """
        Метод, рассчитывающий линейную токовую нагрузку статора.

        :param current: Ток в обмотке, А.
        """

        # 10 - это приводной коэффициент, потому что принято выражать в А/см, а без него получаются А/мм
        self.current_load = 10 * current * self.effective_wires / self.armature.parallel_branches / self.tooth_pitch

    def get_stamp_slot_dimensions(self,
                                  assembly_allowance: float,
                                  stamp_allowance: float
                                  ) -> Tuple[float, float]:
        """
        Метод, возвращающий размеры паза в штампе.

        :param assembly_allowance: Припуск на распушку (по ширине паза), мм.
        :param stamp_allowance: Припуск на штамп (по высоте паза), мм.
        :return: Глубина и ширина паза в штампе, мм.
        """

        height = self.slot_height + stamp_allowance
        width = self.slot_width + assembly_allowance

        return height, width

    def get_heat_load(self) -> float:
        """
        Метод, возвращающий произведение линейной токовой нагрузки статора на плотность тока в обмотке (тепловую
        нагрузку).

        :return: Тепловая нагрузка статора, А²/см∙мм²
        """

        return self.current_load * self.armature.current_density

    # А вот то, что идёт дальше, предвещает расчёт магнитной цепи... Больше методов богу методов! Больше классов к трону
    # классов!

    def get_armature_coefficient(self) -> float:
        """
        Метод, возвращающий обмоточный коэффициент статора.

        :return: Обмоточный коэффициент.
        """

        coeff = math.sin(math.pi / 6) * math.sin(self.armature.shortening * math.pi / 2) /\
            math.sin(math.pi / 6 / self.slots_per_pole_phase) / self.slots_per_pole_phase

        return coeff

    def get_diameter_third(self) -> float:
        """
        Метод, возвращающий диаметр статора на уровне `1/3`:math: высоты зубца.

        :return: Диаметр статора на указанном уровне, мм.
        """

        return self.inner_diameter + 2 * self.slot_height / 3

    def get_diameter_bottom(self) -> float:
        """
        Метод, возвращающий диаметр статора на уровне дна паза.

        :return: Диаметр статора на указанном уровне, мм.
        """

        return self.inner_diameter + 2 * self.slot_height

    def get_tooth_pitch_third(self) -> float:
        """
        Метод, возвращающий зубцовое деление статора на уровне `1/3`:math: высоты зубца.

        :return: Зубцовое деление статора на указанном уровне, мм.
        """

        return math.pi * self.get_diameter_third() / self.slot_count

    def get_tooth_pitch_bottom(self) -> float:
        """
        Метод, возвращающий зубцовое деление статора на уровне дна паза.

        :return: Зубцовое деление статора на указанном уровне, мм.
        """

        return math.pi * self.get_diameter_bottom() / self.slot_count

    def get_yoke_height(self) -> float:
        """
        Метод, возвращающий эффективную высоту ярма статора с учётом шпилек.

        :return: Эффективная высота ярма, мм.
        """

        height = (self.outer_diameter - self.get_diameter_bottom()) / 2

        if self.stud_diameter is not None:
            height -= self.stud_diameter / 3

        if height <= 0:
            raise ValueError("Отрицательная высота спинки статора")

        return height

    def get_yoke_section(self,
                         effective_length: float
                         ) -> float:
        """
        Метод, возвращающий эффективное сечение ярма статора.

        :param effective_length: Эффективная длина статора, мм.
        :return: Эффективное сечение ярма, м².
        """

        # 1e-6 нужно для перевода в м²
        return self.get_yoke_height() * effective_length * 1e-6

    def get_teeth_section_third(self,
                                effective_length: float
                                ) -> float:
        """
        Метод, возвращающий суммарное сечение зубцов статора на уровне `1/3`:math: их высоты.

        :param effective_length: Эффективная длина статора, мм.
        :return: Суммарное сечение зубцов, м².
        """

        if self.tooth_pitch - self.slot_width <= 0:
            raise ValueError("Отрицательная ширина зубца")

        # 1e-6 нужно для перевода в м²
        return 1.91 * effective_length * (self.get_tooth_pitch_third() - self.slot_width) * \
            self.slots_per_pole_phase * 1e-6

    def get_yoke_magnetic_line(self,
                               pole_pairs: int,
                               rotor_surface_relation: float
                               ) -> float:
        """
        Метод, возвращающий расчётную длину магнитной линии в ярме статора.

        :param pole_pairs: Количество пар полюсов машины.
        :param rotor_surface_relation: Отношение обмотанной поверхности ротора к полной.
        :return: Длина магнитной линии, см.
        """

        # 0.1 нужно для перевода в сантиметры
        length = math.pi * rotor_surface_relation * (self.outer_diameter - self.get_yoke_height()) / \
            4 / pole_pairs * 0.1
        return length

    def get_tooth_magnetic_line(self) -> float:
        """
        Метод, возвращающий расчётную длину магнитной линии в зубце статора.

        :return: Длина магнитной линии, см.
        """

        # 0.1 нужно для перевода в сантиметры
        return self.slot_height * 0.1

    def get_flow_branching_factor(self,
                                  effective_length: float
                                  ) -> float:
        """
        Метод, возвращающий коэффициент ответвления потока в пазы статора.

        :return: Коэффициент ответвления.
        """

        t13 = self.get_tooth_pitch_third()

        return t13 * self.length / (t13 - self.slot_width) / effective_length - 1


__all__ = "ACMachineStator"
