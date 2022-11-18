"""
Модуль, содержащий описания типов статорных обмоток.

Классы:

* ``CoilArmature``

  Класс, описывающий обмотку катушечного типа.
"""

from typing import Optional, Tuple, Union, Dict

from common.armatureInsulation import *
from common.wireTypes import *


class CoilArmature:
    """
    Класс, описывающий статорную обмотку катушечного типа машины переменного тока.

    Атрибуты:

    * ``insulation_system: CoilInsulation``

      Система изоляции статорной обмотки.

    * ``rows: int``

      Количество горизонтальных рядов элементарных проводников в одном эффективном.

    * ``columns: int``

      Количество вертикальных рядов элементарных проводников в одном эффективном.

    * ``slot_step: int``

      Шаг обмотки по пазам.

    * ``parallel_branches: int``

      Число параллельных ветвей обмотки.

    * ``wire: WireType``

      Тип используемого обмоточного проводника.

    * ``coil_height: Optional[float]``

      Высота катушки, мм. В момент инициализации равна ``None``.

    * ``coil_width: Optional[float]``

      Ширина катушки, мм. В момент инициализации равна ``None``.

    * ``turn_count: Union[int, float, None]``

      Число витков катушки. В момент инициализации равно ``None``. Может быть типов ``int`` (в нормальном случае) или
      ``float`` (в случае дробного числа витков в фазе).

    * ``shortening: Optional[float]``

      Укорочение обмотки. В идеальном случае равно `5/6`:math: для удаления 5-й и 7-й гармоник. В момент инициализации
      равно ``None``.

    * ``turn_length: Optional[float]``

      Длина витка, мм. В момент инициализации равна ``None``.

    * ``resistance: Optional[Dict[int, float]]``

      Сопротивление обмотки постоянному току, Ом. Рассчитывается для температур 15, 75, 105 и 120 градусов Цельсия. В
      момент инициализации равно ``None``.

    * ``current_density: Optional[float]``

      Плотность тока в обмотке, А/мм². В момент инициализации равна ``None``.

    Методы:

    * ``compute_coil_dimensions(slot_height: float, slot_width: float, slit_height: float,
      wedge_height: float, arrangement_allowance: float) -> None``

      Рассчитывает размеры катушки.

    * ``set_wire(pressing: float, effective_wires: float ) -> None``

      Автоматически подбирает размеры обмоточного проводника (а также толщину его изоляции, для определённых типов
      проводников).

    * ``compute_shortening(slots_per_pole_phase: int, phase_count: int) -> None``

      Рассчитывает укорочение обмотки.

    * ``compute_turn_count_per_phase(pole_pairs: int, slots_per_pole_phase: int, effective_wires: int) -> None``

      Рассчитывает число витков в фазе обмотки.

    * ``compute_turn_length(stator_length: float, diameter: float, pole_pairs: int) -> None``

      Рассчитывает длину витка обмотки.

    * ``compute_resistance(conductivity: float) -> None``

      Рассчитывает сопротивление обмотки при разных температурах. Сохраняет в словарь.

    * ``compute_current_density(current: float) -> None``

      Рассчитывает плотность тока в обмотке.

    * ``get_auxiliary_dimensions(wedge_height: float, slit_height: float) -> Tuple[float, float, float]``

      Возвращает вспомогательные размеры обмотки для расчёта индуктивных сопротивлений.

    Реализует паттерн «Одиночка», поскольку статор не может иметь более одной обмотки.
    """

    __slots__ = ["insulation_system",
                 "rows",
                 "columns",
                 "slot_step",
                 "parallel_branches",
                 "wire",
                 "coil_height",
                 "coil_width",
                 "turn_count",
                 "shortening",
                 "turn_length",
                 "resistance",
                 "current_density"
                 ]

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self,
                 rows: int,
                 columns: int,
                 slot_step: int,
                 parallel_branches: int,
                 insulation_system: CoilInsulation,
                 wire_type: WireType
                 ) -> None:
        self.insulation_system = insulation_system  # Система изоляции
        self.rows = rows  # Число горизонтальных рядов элементарных проводников
        self.columns = columns  # Число вертикальных рядов элементарных проводников
        self.slot_step = slot_step  # Шаг обмотки по пазам
        self.parallel_branches = parallel_branches  # Число параллельных ветвей
        self.wire = wire_type  # Тип проводника

        self.coil_height: Optional[float] = None  # Высота катушки
        self.coil_width: Optional[float] = None  # Ширина катушки
        self.shortening: Optional[float] = None  # Укорочение обмотки
        self.turn_count: Union[int, float, None] = None  # Число витков
        self.turn_length: Optional[float] = None  # Длина витка
        self.resistance: Optional[Dict[int, float]] = None  # Сопротивление обмотки
        self.current_density: Optional[float] = None  # Плотность тока в обмотке

    def __str__(self) -> str:
        return "Катушечная"

    def compute_coil_dimensions(self,
                                slot_height: float,
                                slot_width: float,
                                slit_height: float,
                                wedge_height: float,
                                arrangement_allowance: float
                                ) -> None:
        """
        Метод, рассчитывающий размеры катушки.

        :param slot_height: Высота паза в свету, мм.
        :param slot_width: Ширина паза в свету, мм.
        :param slit_height: Высота шлица, мм.
        :param wedge_height: Высота клина, мм.
        :param arrangement_allowance: Припуск на укладку, мм.
        """

        self.coil_height = (slot_height - slit_height - wedge_height - self.insulation_system.all_fillings()) / 2
        self.coil_width = slot_width - arrangement_allowance

    def set_wire(self,
                 pressing: float,
                 effective_wires: int
                 ) -> None:
        """
        Метод, задающий размеры проводника обмотки.

        :param pressing: Величина опрессовки на элементарный проводник, мм.
        :param effective_wires: Количество эффективных проводников в пазу.
        """

        max_wire_height = 2 * (self.coil_height - self.insulation_system.body_insulation[0] -
                               self.insulation_system.semicond_coating) / self.rows / effective_wires - \
            self.insulation_system.turn_insulation / self.rows + pressing
        max_wire_width = (self.coil_width - self.insulation_system.all_insulation()[1]) / self.columns + pressing
        self.wire.pick_wire(max_wire_height, max_wire_width)

    def compute_shortening(self,
                           slots_per_pole_phase: int,
                           phase_count: int
                           ) -> None:
        """
        Метод, рассчитывающий укорочение обмотки.

        :param slots_per_pole_phase: Число пазов на полюс и фазу.
        :param phase_count: Число фаз.
        """

        self.shortening = self.slot_step / phase_count / slots_per_pole_phase

    def compute_turn_count(self,
                           pole_pairs: int,
                           slots_per_pole_phase: int,
                           effective_wires: int
                           ) -> None:
        """
        Метод, рассчитывающий число последовательных витков в фазе обмотки.

        :param pole_pairs: Количество пар полюсов машины.
        :param slots_per_pole_phase: Число пазов на полюс и фазу.
        :param effective_wires: Количество эффективных проводников в пазу.
        """

        self.turn_count = (pole_pairs * effective_wires * slots_per_pole_phase) / self.parallel_branches

        # Ну и тип заодно приведём. Как минимум для вывода результатов потом удобно будет
        if self.turn_count.is_integer():
            self.turn_count = int(self.turn_count)

    def compute_turn_length(self,
                            stator_length: float,
                            diameter: float,
                            pole_pairs: int
                            ) -> None:
        """
        Метод, рассчитывающий длину витка обмотки.

        :param stator_length: Длина сердечника статора (длина паза), мм.
        :param diameter: Диаметр статора по расточке, мм.
        :param pole_pairs: Количество пар полюсов машины.
        """

        end_part_length = 2.5 * diameter / pole_pairs ** 1.5
        self.turn_length = 2 * (end_part_length + stator_length)

    def compute_resistance(self,
                           conductivity: float
                           ) -> None:
        """
        Метод, рассчитывающий сопротивление обмотки.

        :param conductivity: Удельная проводимость материала обмотки, мм/Ом∙мм².
        """

        # Номинальное значение сопротивления
        base_value = self.turn_count * self.turn_length / conductivity / self.parallel_branches / \
            (self.rows * self.columns * self.wire.wire_section)

        # Словарь из значений сопротивления при 15, 75, 105 и 120 градусах
        self.resistance = dict(zip([15, 75, 105, 120], map(lambda x: x * base_value, [1, 1.24, 1.36, 1.42])))

    def compute_current_density(self,
                                current: float
                                ) -> None:
        """
        Метод, рассчитывающий плотность тока в обмотке.

        :param current: Ток в обмотке, А.
        """

        self.current_density = current / self.parallel_branches / (self.rows * self.columns * self.wire.wire_section)

    def get_auxiliary_dimensions(self,
                                 wedge_height: float,
                                 slit_height: float
                                 ) -> Tuple[float, float, float]:
        """
        Метод, возвращающий вспомогательные размеры обмотки

        :param wedge_height: Высота клина, мм.
        :param slit_height: Высота шлица, мм.
        :return: Высота меди с изоляцией между катушками, мм; расстояние от расточки до меди, мм; толщина изоляции между
        медью, мм.
        """

        coil_insulation = self.insulation_system.all_insulation()[0]

        copper_height = 2 * self.coil_height - self.wire.insulation_height - coil_insulation +\
            self.insulation_system.coil_filling

        distance_to_air = slit_height + wedge_height + self.insulation_system.wedge_filling +\
            (self.wire.insulation_height + coil_insulation) / 2

        insulation_thickness = self.wire.insulation_height + coil_insulation + self.insulation_system.coil_filling

        return copper_height, distance_to_air, insulation_thickness


__all__ = "CoilArmature"
