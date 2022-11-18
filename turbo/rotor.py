"""
Модуль, содержащий описание ротора турбомашины и его бандажа.

Классы:

* ``TurboMachineRotor``

  Класс, описывающий ротор турбомашины.

* ``TurboMachineRotorBandaging``

  Класс данных, хранящий параметры бандажа ротора.
"""

import math
from dataclasses import dataclass
from typing import ClassVar, Optional, Union

from turbo.rotorArmature import TurboMachineRotorArmature


class TurboMachineRotor:
    """
    Класс, описывающий ротор турбомашины.

    Атрибуты:

    * ``air_gap: float``

      Толщина воздушного зазора в машине на одну сторону, мм.

    * ``outer_diameter: float``

      Внешний диаметр ротора, мм.

    * ``inner_diameter: float``

      Внутренний диаметр ротора, мм. Часто указывается как 0 мм.

    * ``length: float``

      Длина сердечника ротора, мм.

    * ``slot_count: int``

      Число пазов ротора.

    * ``slot_pitch_count: int``

      Число пазовых делений ротора. Разница между число пазов и числом пазовых делений вызвана наличием больших зубцов,
      занимающих более одного пазового деления.

    * ``slot_width: float``

      Ширина паза ротора, мм.

    * ``slot_height: Optional[float]``

      Глубина паза, мм. В момент инициализации равна ``None``.

    * ``slot_height_small: Optional[float]``

      Глубина малого паза (при их наличии), мм. В момент инициализации, а также при отсутствии малых пазов равна
      ``None``.

    * ``armature: TurboMachineRotorArmature``

      Обмотка ротора.

    * ``wedge_height: float``

      Высота клина в пазу ротора, мм.

    * ``wedge_width: float``

      Ширина клина в пазу ротора, мм.

    * ``effective_wires: int``

      Число эффективных проводников в пазу.

    * ``effective_wires_small: Optional[int]``

      Число эффективных проводников в малом пазу. В случае их отсутствия равно ``None``.

    * ``coils_per_pole: Optional[Union[int, float]]``

      Число катушек обмотки на полюс. В момент инициализации равно ``None``.

    * ``pole_pitch: Optional[float]``

      Полюсное деление ротора, мм. В момент инициализации равно ``None``.

    * ``surface_relation: Optional[float]``

      Отношение обмотанной поверхности ротора к полной.

    * ``surface_relation_small: Optional[float]``

      Отношение обмотанной поверхности ротора к полной с учётом малых пазов.

    * ``vert_vent_channel_pitch: Optional[float]``

      Шаг вертикальных вентиляционных каналов в обмотке, мм. При их отсутствии равен ``None``.

    * ``vert_vent_channel_length: Optional[float]``

      Длина вертикальных вентиляционных каналов в обмотке, мм. При их отсутствии равна ``None``.

    * ``vert_vent_channel_width: Optional[float]``

      Ширина вертикальных вентиляционных каналов в обмотке, мм. При их отсутствии равна ``None``.

    * ``subslot_channel_height: Optional[float]``

      Глубина подпазового канала, мм. В случае их отсутствия равна ``None``.

    * ``subslot_channel_width: Optional[float]``

      Ширина подпазового канала, мм. В случае их отсутствия равна ``None``.

    * ``big_tooth_slot_count: Optional[int]``

      Число вентиляционных пазов в большом зубе. В случае их отсутствия равно ``None``.

    * ``big_tooth_slot_width: Optional[float]``

      Ширина вентиляционных пазов в большом зубе. В случае их отсутствия равна ``None``.

    * ``tooth_slot_width: Optional[float]``

      Ширина вентиляционных пазов в зубцах. В случае их отсутствия равна ``None``.

    * ``tooth_slot_height: Optional[float]``

      Глубина вентиляционных пазов в зубцах. В случае их отсутствия равна ``None``.

    * ``tooth_pitch: Optional[float]``

      Зубцовое деление, мм. В момент инициализации равно ``None``.

    * ``current_load: Optional[float]``

      Линейная токовая нагрузка ротора, А/см. В момент инициализации равна ``None``.

    Методы:

    * ``compute_slot_height() -> None``

      Вычисляет высоту нормального и малого (при их наличии) паза.

    * ``compute_surface_relation(pole_pairs: int) -> None``

      Вычисляет отношение обмотанной поверхности ротора к полной.

    * ``compute_coils_per_pole(pole_pairs: int) -> None``

      Вычисляет число катушек обмотки на полюс.

    * ``compute_pole_pitch(pole_pairs: int) -> None``

      Вычисляет полюсное деление ротора.

    * ``compute_tooth_pitch() -> None``

      Вычисляет пазовое/зубцовое деление ротора.

    * ``compute_current_load(current: float) -> None``

      Вычисляет линейную токовую нагрузку ротора.

    * ``get_heat_load() -> float``

      Возвращает произведение линейной токовой нагрузки на плотность тока в обмотке (тепловую нагрузку), А²/см∙мм².

    * ``get_tooth_width() -> float``

      Возвращает ширину зубца по расточке, мм.

    * ``get_teeth_section_02(pole_pairs: int) -> float``

      Возвращает суммарное сечение зубцов на уровне 20% высоты зубца, м².

    * ``get_teeth_section_07(pole_pairs: int) -> float``

      Возвращает суммарное сечение зубцов на уровне 70% высоты зубца, м².

    * ``get_teeth_section_slot_02(pole_pairs: int) -> Optional[float]``

      Возвращает суммарное сечение зубцов на уровне 20% высоты подпазового канала (при их наличии), м², либо ``None``.

    * ``get_teeth_section_slot_07(pole_pairs: int) -> Optional[float]``

      Возвращает суммарное сечение зубцов на уровне 70% высоты подпазового канала (при их наличии), м², либо ``None``.

    * ``get_yoke_section() -> float``

      Возвращает сечение ярма ротора, м².

    * ``get_air_gap_section(pole_pairs: int, stator_length: float) -> float``

      Возвращает площадь сечения воздушного зазора на полюс, м².

    * ``get_tooth_half_magnetic_line() -> float``

      Возвращает половину длины магнитной линии в зубце ротора, см. Половину по той причине, что в расчёте магнитной
      цепи МДС зубцов вычисляется по двум участкам.

    * ``get_tooth_slot_half_magnetic_line() -> Optional[float]``

      Возвращает половину длины магнитной линии в зубце ротора в области подпазового канала, см, либо ``None`` при их
      отсутствии.

    * ``get_yoke_magnetic_line(pole_pairs: int) -> float``

      Возвращает длину магнитной линии в ярме ротора, см.

    * ``get_flow_branching_factor_02() -> float``

      Возвращает коэффициент ответвления потока в паз ротора на уровне 20% высоты зубца.

    * ``get_flow_branching_factor_07() -> float``

      Возвращает коэффициент ответвления потока в паз ротора на уровне 70% высоты зубца.

    * ``get_flow_branching_factor_slot_02() -> Optional[float]``

      Возвращает коэффициент ответвления потока в паз ротора на уровне 20% высоты подпазового канала (при их наличии),
      либо ``None``.

    * ``get_flow_branching_factor_slot_07() -> Optional[float]``

      Возвращает коэффициент ответвления потока в паз ротора на уровне 70% высоты подпазового канала (при их наличии),
      либо ``None``.

    * ``get_yoke_saturation_factor() -> float``

      Возвращает коэффициент насыщения ярма ротора.

    Возбуждает исключения:

    * ``ValueError``

      В случае, если ширина зубца в основании оказывается нулевой или отрицательной, возбуждается ``ValueError``. Также,
      если глубина вентиляционного канала в зубце (при их наличии) оказывается больше глубины паза, возбуждается
      ``ValueError``.
    """

    __slots__ = ["air_gap",
                 "outer_diameter",
                 "inner_diameter",
                 "length",
                 "slot_count",
                 "slot_pitch_count",
                 "slot_width",
                 "slot_height",
                 "slot_height_small",
                 "armature",
                 "wedge_height",
                 "wedge_width",
                 "effective_wires",
                 "effective_wires_small",
                 "coils_per_pole",
                 "pole_pitch",
                 "surface_relation",
                 "surface_relation_small",
                 "vert_vent_channel_pitch",
                 "vert_vent_channel_length",
                 "vert_vent_channel_width",
                 "subslot_channel_height",
                 "subslot_channel_width",
                 "big_tooth_slot_count",
                 "big_tooth_slot_width",
                 "tooth_slot_width",
                 "tooth_slot_height",
                 "tooth_pitch",
                 "current_load"]

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self,
                 air_gap: float,
                 stator_diameter: float,
                 inner_diameter: float,
                 length: float,
                 slot_count: int,
                 slot_pitch_count: int,
                 slot_width: float,
                 armature: TurboMachineRotorArmature,
                 wedge_height: float,
                 wedge_width: float,
                 effective_wires: int,
                 effective_wires_small: Optional[int] = None,
                 vert_vent_channel_pitch: Optional[float] = None,
                 vert_vent_channel_length: Optional[float] = None,
                 vert_vent_channel_width: Optional[float] = None,
                 subslot_channel_height: Optional[float] = None,
                 subslot_channel_width: Optional[float] = None,
                 big_tooth_slot_count: Optional[int] = None,
                 big_tooth_slot_width: Optional[float] = None,
                 tooth_slot_width: Optional[float] = None,
                 tooth_slot_height: Optional[float] = None
                 ) -> None:
        self.air_gap = air_gap  # Односторонний воздушный зазор
        self.outer_diameter: float = stator_diameter - 2 * air_gap  # Внешний диаметр ротора
        self.inner_diameter = inner_diameter  # Внутренний диаметр ротора
        self.length = length  # Длина ротора

        self.slot_count = slot_count  # Число пазов
        self.slot_pitch_count = slot_pitch_count  # Число пазовых делений. Да, это турбомашинки, тут важно
        self.slot_width = slot_width  # Ширина паза
        self.slot_height: Optional[float] = None  # Глубина паза
        self.slot_height_small: Optional[float] = None  # Глубина малого паза

        self.wedge_height = wedge_height  # Высота клина
        self.wedge_width = wedge_width  # Ширина клина

        self.armature = armature  # Роторная обмотка
        self.effective_wires = effective_wires  # Число эффективных проводов в пазу
        self.effective_wires_small = effective_wires_small  # Оно же, в малом пазу

        self.subslot_channel_height = subslot_channel_height  # Глубина подпазового канала
        self.subslot_channel_width = subslot_channel_width  # Ширина его

        self.vert_vent_channel_pitch = vert_vent_channel_pitch  # Шаг вертикальных вентиляционных каналов в обмотке
        self.vert_vent_channel_length = vert_vent_channel_length  # Длина их
        self.vert_vent_channel_width = vert_vent_channel_width  # Ширина их

        self.big_tooth_slot_count = big_tooth_slot_count  # Число вентиляционных каналов в большом пазу
        self.big_tooth_slot_width = big_tooth_slot_width  # Ширина их

        self.tooth_slot_width = tooth_slot_width  # Ширина вентиляционных каналов в пазах
        self.tooth_slot_height = tooth_slot_height  # Глубина их

        self.coils_per_pole: Optional[Union[int, float]] = None  # Число катушек на полюс
        self.pole_pitch: Optional[float] = None  # Полюсное деление
        # Отношение обмотанной поверхности к полной (или, вернее, цилиндрической, но... Oh my god, who the hell cares?!)
        self.surface_relation: Optional[float] = None
        self.surface_relation_small: Optional[float] = None  # То же самое, только с учётом малых пазов

        self.tooth_pitch: Optional[float] = None  # Зубцовое деление
        self.current_load: Optional[float] = None  # Токовая нагрузка

    def compute_slot_height(self) -> None:
        """
        Метод, рассчитывающий высоту нормального и малого (при их наличии) паза ротора.
        """

        slot_height = self.effective_wires * self.armature.wire_height +\
            (self.effective_wires - 1) * self.armature.insulation.turn_insulation +\
            self.armature.insulation.body_insulation + self.armature.insulation.all_fillings() + self.wedge_height
        self.slot_height = round(slot_height, 1)

        if self.effective_wires_small is not None:
            slot_height_small = self.effective_wires_small * self.armature.wire_height + \
                (self.effective_wires_small - 1) * self.armature.insulation.turn_insulation + \
                self.armature.insulation.body_insulation + self.armature.insulation.all_fillings() + self.wedge_height
            self.slot_height_small = round(slot_height_small, 1)

        if self.tooth_slot_height is not None and self.tooth_slot_height >= self.slot_height:
            raise ValueError("Глубина вентиляционного канала в зубце больше глубины паза")

    def compute_surface_relation(self,
                                 pole_pairs: int
                                 ) -> None:
        r"""
        Метод, рассчитывающий отношение обмотанной поверхности ротора к необмотанной при наличии (`\gamma'`:math:) и
        отсутствии (`\gamma`:math:) малых пазов.

        :param pole_pairs: Количество пар полюсов машины.
        """

        self.surface_relation = self.slot_count / self.slot_pitch_count
        self.surface_relation_small = (self.slot_count - 4 * pole_pairs) / self.slot_pitch_count

    def compute_coils_per_pole(self,
                               pole_pairs: int
                               ) -> None:
        """
        Метод, рассчитывающий число катушек роторной обмотки на полюс.

        :param pole_pairs: Количество пар полюсов машины.
        :return: Число катушек на полюс.
        """

        self.coils_per_pole = self.slot_count / 4 / pole_pairs
        if self.coils_per_pole == (int_coils := int(self.coils_per_pole)):
            self.coils_per_pole = int_coils

    def compute_pole_pitch(self,
                           pole_pairs: int
                           ) -> None:
        """
        Метод, рассчитывающий полюсное деление.

        :param pole_pairs: Количество пар полюсов машины.
        """

        self.pole_pitch = math.pi * self.outer_diameter / 2 / pole_pairs

    def compute_tooth_pitch(self) -> None:
        """
        Метод, рассчитывающий зубцовое деление ротора.
        """

        self.tooth_pitch = math.pi * self.outer_diameter / self.slot_pitch_count

    def compute_current_load(self,
                             current: float
                             ) -> None:
        """
        Метод, рассчитывающий линейную токовую нагрузку ротора.

        :param current: Ток в обмотке, А.
        """

        self.current_load = 10 * current * self.effective_wires / self.armature.parallel_branches / self.tooth_pitch

    def get_heat_load(self) -> float:
        """
        Метод, возвращающий произведение линейной токовой нагрузки ротора на плотность тока в обмотке (тепловую
        нагрузку).

        :return: Тепловая нагрузка ротора, А²/см∙мм²
        """

        return self.current_load * self.armature.current_density

    def get_armature_coefficient(self,
                                 pole_pairs: int
                                 ) -> float:
        """
        Метод, возвращающий обмоточный коэффициент ротора.

        :param pole_pairs: Количество пар полюсов машины.
        :return: Обмоточный коэффициент.
        """

        coef_prime = 2 * pole_pairs * math.sin(math.pi * self.surface_relation_small / 2) /\
            (self.slot_count - 4 * pole_pairs) / math.sin(math.pi * pole_pairs / self.slot_pitch_count)

        if self.effective_wires_small is not None:
            coef = (self.effective_wires_small / self.effective_wires * math.sin(math.pi / 2 *
                    (1 - self.surface_relation + 0.5 / self.coils_per_pole)) +
                    coef_prime * (self.coils_per_pole - 1)) /\
                   (self.coils_per_pole - 1 + self.effective_wires_small / self.effective_wires)
            return coef

        return coef_prime

    def get_tooth_width(self) -> float:
        """
        Метод, возвращающий ширину зубца ротора по расточке.

        :return: Ширина зубца, мм.
        """

        width = self.tooth_pitch - self.slot_width

        if self.tooth_slot_width is not None:
            width -= self.tooth_slot_width

        return width

    def __get_diameter_bottom(self) -> float:
        """
        Вспомогательный метод, возвращающий диаметр ротора на уровне дна паза.

        :return: Диаметр ротора на указанном уровне, мм.
        """

        return self.outer_diameter - 2 * self.slot_height

    def __get_diameter_02(self) -> float:
        """
        Вспомогательный метод, возвращающий диаметр ротора на уровне 20% высоты паза.

        :return: Диаметр ротора на указанном уровне, мм.
        """

        return self.outer_diameter - 1.6 * self.slot_height

    def __get_diameter_07(self) -> float:
        """
        Вспомогательный метод, возвращающий диаметр ротора на уровне 70% высоты паза.

        :return: Диаметр ротора на указанном уровне, мм.
        """

        return self.outer_diameter - 0.6 * self.slot_height

    def __get_diameter_slot_bottom(self) -> float:
        """
        Вспомогательный метод, возвращающий диаметр ротора на уровне дна подпазового канала (при их наличии), либо
        на уровне дна паза.

        :return: Диаметр ротора на указанном уровне, мм.
        """

        if self.subslot_channel_height is not None:
            return self.__get_diameter_bottom() - 2 * self.subslot_channel_height
        return self.__get_diameter_bottom()

    def __get_diameter_slot_02(self) -> float:
        """
        Вспомогательный метод, возвращающий диаметр ротора на уровне 20% высоты подпазового канала (при их наличии),
        либо на уровне дна паза.

        :return: Диаметр ротора на указанном уровне, мм.
        """

        if self.subslot_channel_height is not None:
            return self.__get_diameter_bottom() - 1.6 * self.subslot_channel_height
        return self.__get_diameter_bottom()

    def __get_diameter_slot_07(self) -> float:
        """
        Вспомогательный метод, возвращающий диаметр ротора на уровне 70% высоты подпазового канала (при их наличии),
        либо на уровне дна паза.

        :return: Диаметр ротора на указанном уровне, мм.
        """

        if self.subslot_channel_height is not None:
            return self.__get_diameter_bottom() - 0.6 * self.subslot_channel_height
        return self.__get_diameter_bottom()

    def __get_tooth_pitch_bottom(self) -> float:
        """
        Вспомогательный метод, возвращающий зубцовое деление ротора на уровне дна паза.

        :return: Зубцовое деление на указанном уровне, мм.
        """

        return math.pi * self.__get_diameter_bottom() / self.slot_pitch_count

    def __get_tooth_pitch_02(self) -> float:
        """
        Вспомогательный метод, возвращающий зубцовое деление ротора на уровне 20% высоты паза.

        :return: Зубцовое деление на указанном уровне, мм.
        """

        return math.pi * self.__get_diameter_02() / self.slot_pitch_count

    def __get_tooth_pitch_07(self) -> float:
        """
        Вспомогательный метод, возвращающий зубцовое деление ротора на уровне 70% высоты паза.

        :return: Зубцовое деление на указанном уровне, мм.
        """

        return math.pi * self.__get_diameter_07() / self.slot_pitch_count

    def __get_tooth_pitch_slot_bottom(self) -> float:
        """
        Вспомогательный метод, возвращающий зубцовое деление ротора на уровне дна подпазового канала (при их наличии),
        либо на уровне дна паза.

        :return: Зубцовое деление на указанном уровне, мм.
        """

        return math.pi * self.__get_diameter_slot_bottom() / self.slot_pitch_count

    def __get_tooth_pitch_slot_02(self) -> float:
        """
        Вспомогательный метод, возвращающий зубцовое деление ротора на уровне 20% высоты подпазового канала (при их
        наличии), либо на уровне дна паза.

        :return: Зубцовое деление на указанном уровне, мм.
        """

        return math.pi * self.__get_diameter_slot_02() / self.slot_pitch_count

    def __get_tooth_pitch_slot_07(self) -> float:
        """
        Вспомогательный метод, возвращающий зубцовое деление ротора на уровне 70% высоты подпазового канала (при их
        наличии), либо на уровне дна паза.
        """

        return math.pi * self.__get_diameter_slot_07() / self.slot_pitch_count

    def __get_tooth_width_bottom(self) -> float:
        """
        Вспомогательный метод, возвращающий ширину зубца ротора на уровне 20% высоты паза.

        :return: Ширина зубца на указанном уровне, мм.
        """

        # Здесь не нужно проверять наличие вентиляционного канала в зубце, поскольку это исключается ещё на этапе
        # расчёта глубины паза
        return self.__get_tooth_pitch_bottom() - self.slot_width

    def __get_tooth_width_02(self) -> float:
        """
        Вспомогательный метод, возвращающий ширину зубца ротора на уровне 20% высоты паза.

        :return: Ширина зубца на указанном уровне, мм.
        """

        width = self.__get_tooth_pitch_02() - self.slot_width

        if self.tooth_slot_width is not None and self.tooth_slot_height >= 0.8 * self.slot_height:
            width -= self.tooth_slot_width

        return width

    def __get_tooth_width_07(self) -> float:
        """
        Вспомогательный метод, возвращающий ширину зубца ротора на уровне 70% высоты паза.

        :return: Ширина зубца на указанном уровне, мм.
        """

        width = self.__get_tooth_pitch_07() - self.slot_width

        if self.tooth_slot_width is not None and self.tooth_slot_height >= 0.3 * self.slot_height:
            width -= self.tooth_slot_width

        return width

    def __get_tooth_width_slot_bottom(self) -> Optional[float]:
        """
        Вспомогательный метод, возвращающий ширину зубца ротора на уровне дна подпазового канала (при их наличии), либо
        ``None``.

        :return: Ширина зубца на указанном уровне, мм, либо None.
        """

        if self.subslot_channel_height is not None:
            return self.__get_tooth_pitch_slot_bottom() - self.subslot_channel_width

        return None

    def __get_tooth_width_slot_02(self) -> Optional[float]:
        """
        Вспомогательный метод, возвращающий ширину зубца ротора на уровне 20% высоты подпазового канала (при их
        наличии), либо ``None``.

        :return: Ширина зубца на указанном уровне, мм, либо None.
        """

        if self.subslot_channel_height is not None:
            return self.__get_tooth_pitch_slot_02() - self.subslot_channel_width

        return None

    def __get_tooth_width_slot_07(self) -> Optional[float]:
        """
        Вспомогательный метод, возвращающий ширину зубца ротора на уровне 70% высоты подпазового канала (при их
        наличии), либо ``None``.

        :return: Ширина зубца на указанном уровне, мм, либо None.
        """

        if self.subslot_channel_height is not None:
            return self.__get_tooth_pitch_slot_07() - self.subslot_channel_width

        return None

    def __get_sin_alpha(self,
                        pole_pairs: int
                        ) -> float:
        r"""
        Вспомогательный метод, рассчитывающий сумму проекций ширины пазов на поперечную осб ротора при ширине паза,
        равной 1 см, соответствующую `\gamma`:math:.

        :param pole_pairs: Количество пар полюсов машины.
        :return: Сумма проекций ширины пазов.
        """

        sin_alpha = (1 - math.cos(math.pi * self.surface_relation / 2)) /\
            math.sin(math.pi * pole_pairs / self.slot_pitch_count)

        return sin_alpha

    def __get_sin_alpha_small(self,
                              pole_pairs: int
                              ) -> float:
        r"""
        Вспомогательный метод, рассчитывающий сумму проекций ширины пазов на поперечную осб ротора при ширине паза,
        равной 1 см, соответствующую `\gamma'`:math:.

        :param pole_pairs: Количество пар полюсов машины.
        :return: Сумма проекций ширины пазов
        """

        sin_alpha_small = (1 - math.cos(math.pi * self.surface_relation_small / 2)) /\
            math.sin(math.pi * pole_pairs / self.slot_pitch_count)

        return sin_alpha_small

    def get_teeth_section_02(self,
                             pole_pairs: int
                             ) -> float:
        """
        Метод, возвращающий суммарное сечение зубцов ротора на уровне 20% высоты паза.

        :param pole_pairs: Количество пар полюсов машины.
        :return: Сечение зубцов на указанном уровне, м².
        """

        # Нужно проверять обе ширину, поскольку из-за вентиляционного канала ширина в сечении 0.2h может оказаться
        # меньше, чем на дне паза
        if self.__get_tooth_width_bottom() <= 0 or self.__get_tooth_width_02() <= 0:
            raise ValueError("Отрицательная ширина зубца")

        if self.tooth_slot_height is None or self.tooth_slot_height < 0.8 * self.slot_height:
            total_slot_width = self.slot_width
        else:
            total_slot_width = self.slot_width + self.tooth_slot_width

        if self.big_tooth_slot_count is None:
            section = self.length * (self.__get_diameter_02() / pole_pairs - total_slot_width *
                                     self.__get_sin_alpha(pole_pairs)) * 1e-6
        else:
            section = self.length * (self.__get_diameter_02() / pole_pairs - total_slot_width *
                                     self.__get_sin_alpha(pole_pairs) - self.big_tooth_slot_width *
                                     self.big_tooth_slot_count) * 1e-6

        return section

    def get_teeth_section_07(self,
                             pole_pairs: int
                             ) -> float:
        """
        Метод, возвращающий суммарное сечение зубцов ротора на уровне 70% высоты паза.

        :param pole_pairs: Количество пар полюсов машины.
        :return: Сечение зубцов на указанном уровне, м².
        """

        # А вот здесь дополнительные проверки ширины не нужны, поскольку если проверка успешно пройдена для сечения
        # 0.2h и дна паза, то для сечения 0.7h она проходится автоматически
        if self.tooth_slot_height is None or self.tooth_slot_height < 0.3 * self.slot_height:
            total_slot_width = self.slot_width
        else:
            total_slot_width = self.slot_width + self.tooth_slot_width

        if self.big_tooth_slot_count is None:
            section = self.length * (self.__get_diameter_07() / pole_pairs - total_slot_width *
                                     self.__get_sin_alpha(pole_pairs)) * 1e-6
        else:
            section = self.length * (self.__get_diameter_07() / pole_pairs - total_slot_width *
                                     self.__get_sin_alpha(pole_pairs) - self.big_tooth_slot_width *
                                     self.big_tooth_slot_count) * 1e-6

        return section

    def get_teeth_section_slot_02(self,
                                  pole_pairs: int
                                  ) -> Optional[float]:
        """
        Метод, возвращающий суммарное сечение зубцов ротора на уровне 20% высоты подпазового канала (при их наличии),
        либо ``None``.

        :param pole_pairs: Количество пар полюсов машины.
        :return: Сечение зубцов на указанном уровне, м², либо None.
        """

        # Здесь достаточно проверить только ширину по дну паза, потому что никаких дополнительных дырок тут нет
        if (t := self.__get_tooth_width_slot_bottom()) is not None and t <= 0:
            raise ValueError("Отрицательная ширина зубца")

        if self.subslot_channel_width is not None:
            section = self.length * (self.__get_diameter_slot_02() / pole_pairs - self.subslot_channel_width *
                                     self.__get_sin_alpha_small(pole_pairs)) * 1e-6
            return section

        return None

    def get_teeth_section_slot_07(self,
                                  pole_pairs: int
                                  ) -> Optional[float]:
        """
        Метод, возвращающий суммарное сечение зубцов ротора на уровне 70% высоты подпазового канала (при их наличии),
        либо ``None``.

        :param pole_pairs: Количество пар полюсов машины.
        :return: Сечение зубцов на указанном уровне, м², либо None.
        """

        if self.subslot_channel_width is not None:
            section = self.length * (self.__get_diameter_slot_07() / pole_pairs - self.subslot_channel_width *
                                     self.__get_sin_alpha(pole_pairs)) * 1e-6
            return section

        return None

    def get_yoke_section(self) -> float:
        """
        Метод, возвращающий эффективное сечение ярма ротора.

        :return: Эффективное сечение ярма, м².
        """

        diameter_slot_bottom = self.__get_diameter_slot_bottom()
        section = (diameter_slot_bottom - self.inner_diameter) / 2 * (self.length + diameter_slot_bottom / 3) * 1e-6

        return section

    def get_air_gap_section(self,
                            pole_pairs: int,
                            stator_length: float
                            ) -> float:
        """
        Метод, возвращающий площадь сечения воздушного зазора на полюс.

        :param pole_pairs: Количество пар полюсов машины.
        :param stator_length: Длина статора, мм.
        :return: Площадь сечения воздушного зазора, м².
        """

        coef = math.pi / 2 * (1 - self.surface_relation / 2)
        section = (self.outer_diameter + self.air_gap) * (stator_length + 2 * self.air_gap) * coef / pole_pairs * 1e-6

        return section

    def get_tooth_half_magnetic_line(self) -> float:
        """
        Метод, возвращающий половину расчётной длины магнитной линии в зубце ротора.

        :return: Длина магнитной линии, см.
        """

        return self.slot_height / 2 * 0.1

    def get_tooth_slot_half_magnetic_line(self) -> Optional[float]:
        """
        Метод, возвращающий половину расчётной длины магнитной линии в зубце ротора в области подпазового канала (при
        их наличии), либо ``None``.

        :return: Длина магнитной линии, см, либо None.
        """

        if self.subslot_channel_height is not None:
            return self.subslot_channel_height / 2 * 0.1
        return None

    def get_yoke_magnetic_line(self,
                               pole_pairs: int
                               ) -> float:
        """
        Метод, возвращающий расчётную длину магнитной линии в ярме ротора.

        :param pole_pairs: Количество пар полюсов машины.
        :return: Длина магнитной линии, см.
        """

        return self.__get_diameter_slot_bottom() / 2 / math.sin(math.pi / 2 / pole_pairs) * 0.1

    def get_flow_branching_factor_02(self) -> float:
        """
        Метод, возвращающий коэффициент ответвления потока в пазы ротора на уровне 20% высоты паза.

        :return: Коэффициент ответвления.
        """

        return self.slot_width / self.__get_tooth_width_02()

    def get_flow_branching_factor_07(self) -> float:
        """
        Метод, возвращающий коэффициент ответвления потока в пазы ротора на уровне 70% высоты паза.

        :return: Коэффициент ответвления.
        """

        return self.slot_width / self.__get_tooth_width_07()

    def get_flow_branching_factor_slot_02(self) -> Optional[float]:
        """
        Метод, возвращающий коэффициент ответвления потока в пазы ротора на уровне 20% высоты подпазового канала (при их
        наличии), либо ``None``.

        :return: Коэффициент ответвления либо None.
        """

        if self.subslot_channel_width is not None and (tooth_width := self.__get_tooth_width_slot_02()) is not None:
            return self.subslot_channel_width / tooth_width
        return None

    def get_flow_branching_factor_slot_07(self) -> Optional[float]:
        """
        Метод, возвращающий коэффициент ответвления потока в пазы ротора на уровне 70% высоты подпазового канала (при их
        наличии), либо ``None``.

        :return: Коэффициент ответвления либо None.
        """

        if self.subslot_channel_width is not None and (tooth_width := self.__get_tooth_width_slot_07()) is not None:
            return self.subslot_channel_width / tooth_width
        return None

    def get_yoke_saturation_factor(self) -> float:
        """
        Метод, возвращающий коэффициент насыщения ярма ротора.

        :return: Коэффициент насыщения.
        """

        # Временная мера. Возможно, в дальнейшем придётся выполнить полноценный расчёт как написано в книгах, но пока
        # единица всех устраивает. И нет, я не буду делать метод статическим, потому что потом он может начать
        # обращаться к атрибутам класса
        return 1


@dataclass
class TurboMachineRotorBandaging:
    """
    Класс данных, хранящий параметры бандажа ротора.

    Атрибуты:

    * ``outer_diameter: float``

      Внешний диаметр бандажного кольца, мм.

    * ``inner_diameter: float``

      Внутренний диаметр бандажного кольца, мм.

    * ``ring_width: float``

      Ширина (длина, если длиной считать размер в направлении оси ротора) бандажного кольца, мм.

    * ``offset: float``

      Отставка бандажа, мм.

    * ``ismagnetic: bool``

      Логическое поле, указывающее, из магнитных материалов ли выполнен бандаж. По умолчанию равно ``False``.

    Реализует паттерн «Одиночка».
    """

    # Увы, тут пришлось отказаться от __slots__, потому что оно конфликтует с ismagnetic, а возводить строительные леса
    # декораторов и/или постобработок во имя оптимизации я пока не хочу, ибо так и запутаться недолго
    outer_diameter: float
    inner_diameter: float
    ring_width: float
    offset: float
    ismagnetic: bool = False

    __instance: ClassVar = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance


__all__ = ["TurboMachineRotor", "TurboMachineRotorBandaging"]
