# * ``steel: Union[Dict[str, Steel], Steel] ``
#
#       Тип стали сердечника. Словарь, содержащий ключи ``along`` и ``across``, соответствующие объектам типа ``Steel``,
#       описывающим характеристики намагничивания стали соответственно вдоль и поперёк проката, либо объект типа
#       ``Steel``, описывающий усреднённую характеристику намагничивания стали.

from common.stator import ACMachineStator
from common.steelDatabase import Steel
from turbo.rotor import TurboMachineRotor, TurboMachineRotorBandaging

from abc import ABC
from typing import Optional, Union, Dict, Tuple
import numpy as np
import math


class MagneticCircuit(ABC):
    __slots__ = ["stator_steel",
                 "rotor_steel",
                 "_lines",
                 "_sections",
                 "_rotor_branching_factors",
                 "_stator_keys",
                 "_rotor_keys",
                 "stator_teeth_air_gap_coef",
                 "stator_vent_air_gap_coef",
                 "stator_step_air_gap_coef",
                 "rotor_teeth_air_gap_coef",
                 "air_gap_coef",
                 "stator_flow",
                 "rotor_flow",
                 "lambda_2",
                 "phi_s",
                 "phi_b",
                 "B_field",
                 "H_field",
                 "MMF",
                 "stator_MMF",
                 "total_MMF"
                 ]

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self,
                 stator: ACMachineStator,
                 rotor: TurboMachineRotor,
                 stator_steel: Union[Dict[str, Steel], Steel],
                 rotor_steel: Steel,
                 pole_pairs: int,
                 fill_factor: float
                 ) -> None:
        # Значит так. Тут я решил пользоваться словарями для хранения данных вместо отдельных атрибутов, как в статоре и
        # роторе, потому что тут всё одинаково. Более или менее. А вот там полнейший разброд и шатание, так что там
        # такие аккуратные структурки не сделаешь. Чёрт возьми

        # Сталька статора. Или две. Смотря чего расчётчик захочет
        self.stator_steel = stator_steel
        self.rotor_steel = rotor_steel  # Сталька ротора. Всегда одна

        # Длина магнитных линий в разных кусках машины. Вот за этим и подаём на вход целые ротор со статором
        rotor_tooth_magnetic_line = rotor.get_tooth_half_magnetic_line()
        rotor_tooth_slot_magnetic_line = rotor.get_tooth_slot_half_magnetic_line()
        self._lines: Dict[str, Optional[float]] =\
            {"air gap": rotor.air_gap * 0.1,
             "stator yoke": stator.get_yoke_magnetic_line(pole_pairs, rotor.surface_relation),
             "stator teeth": stator.get_tooth_magnetic_line(),
             "rotor yoke": rotor.get_yoke_magnetic_line(pole_pairs),
             "rotor teeth 0.2": rotor_tooth_magnetic_line,
             "rotor teeth 0.7": rotor_tooth_magnetic_line,
             "rotor teeth slots 0.2": rotor_tooth_slot_magnetic_line,
             "rotor teeth slots 0.7": rotor_tooth_slot_magnetic_line}

        # Сечения в разных кусках машины. Нужны для индукций
        self._sections: Dict[str, Optional[float]] =\
            {"air gap": rotor.get_air_gap_section(pole_pairs, stator.length),
             "stator yoke": 2 * stator.get_yoke_section(stator.effective_length),
             "stator teeth": stator.get_teeth_section_third(stator.effective_length),
             "rotor yoke": 2 * rotor.get_yoke_section(),
             "rotor teeth 0.2": rotor.get_teeth_section_02(pole_pairs),
             "rotor teeth 0.7": rotor.get_teeth_section_07(pole_pairs),
             "rotor teeth slots 0.2": rotor.get_teeth_section_slot_02(pole_pairs),
             "rotor teeth slots 0.7": rotor.get_teeth_section_slot_07(pole_pairs)}

        self._rotor_branching_factors: Dict[str, Optional[float]] =\
            {"rotor teeth 0.2": rotor.get_flow_branching_factor_02(),
             "rotor teeth 0.7": rotor.get_flow_branching_factor_07(),
             "rotor teeth slots 0.2": rotor.get_flow_branching_factor_slot_02(),
             "rotor teeth slots 0.7": rotor.get_flow_branching_factor_slot_07()}

        # Чисто для простоты рефакторинга: списки ключей
        self._stator_keys = ["air gap", "stator yoke", "stator teeth"]
        self._rotor_keys = ["rotor yoke", "rotor teeth 0.2", "rotor teeth 0.7", "rotor teeth slots 0.2",
                            "rotor teeth slots 0.7"]

        self.stator_teeth_air_gap_coef: Optional[float] = None  # Коэф-т зазора, обусловленный зубчатостью статора
        self.stator_vent_air_gap_coef: Optional[float] = None  # Коэф-т зазора, обусловленный вент. каналами статора
        self.stator_step_air_gap_coef: Optional[float] = None  # Коэф-т зазора, обусловленный ступ-тью крайних пакетов
        self.rotor_teeth_air_gap_coef: Optional[float] = None  # Коэф-т зазора, обусловленный зубчатостью ротора
        self.air_gap_coef: Optional[float] = None  # Общий коэффициент зазора
        # Да-а-а, детка, ещё... Больше коэффициентов... Обожаю их... Ты так шикарно считаешь коэффициенты...

        self.__compute_air_gap_coefficients(stator, rotor)  # Сразу и посчитаем, почему бы и нет

        self.stator_flow: Optional[float] = None  # Поток статора, Вб
        self.rotor_flow: Optional[float] = None  # Поток ротора, D,

        # Я очень не хотел выносить это сюда, но увы, иначе пришлось бы пересчитывать при построении характеристики
        # холостого хода, а это нам не надо, ибо так мы теряем скорость

        # Да, я знаю, обычно я стараюсь давать понятные имена переменных, но писать что-то в духе
        # magnetic_conductivity_for_rotor_dispersion_flow или ещё что почище - это слишком. Нет. Я отказываюсь
        self.lambda_2: Optional[float] = None  # Магнитная проводимость для поперечно-пазового рассеяния
        self.phi_s: Optional[float] = None  # Поперечно-пазовый поток рассеяния
        self.phi_b: Optional[float] = None  # Поток рассеяния через бандажи

        self.__compute_lambda_2(rotor, pole_pairs)

        self.B_field: Optional[Dict[str, Optional[float]]] = None  # Словарь значений индукции, Тл
        self.H_field: Optional[Dict[str, Optional[float]]] = None  # Словарь значений напряжённости, А/см
        self.MMF: Optional[Dict[str, Optional[float]]] = None  # Словарь значений МДС, А

        self.stator_MMF: Optional[float] = None  # МДС на статор, А
        self.total_MMF: Optional[float] = None  # Полная МДС, А

    def __compute_air_gap_coefficients(self,
                                       stator: ACMachineStator,
                                       rotor: TurboMachineRotor
                                       ) -> None:
        self.stator_teeth_air_gap_coef = 1 + stator.slot_width ** 2 /\
            (stator.tooth_pitch * (stator.slot_width + 5 * rotor.air_gap) - stator.slot_width ** 2)

        if stator.vent_channel_count is not None:
            length = stator.length - stator.vent_channel_width * stator.vent_channel_count
            if stator.bypass_thickness is not None:
                length -= 2 * stator.bypass_thickness
            package_width = length / (stator.vent_channel_count + 1)
            self.stator_vent_air_gap_coef = 1 + stator.vent_channel_width ** 2 /\
                ((stator.vent_channel_width + package_width) * (5 * rotor.air_gap + stator.vent_channel_width) -
                 stator.vent_channel_width ** 2)
        else:
            self.stator_vent_air_gap_coef = 1

        self.stator_step_air_gap_coef = 1 + 5 / math.sqrt(rotor.air_gap * (stator.length + rotor.length) / 2)
        self.rotor_teeth_air_gap_coef = 1 + rotor.surface_relation / 2 * rotor.slot_width ** 2 /\
            (rotor.tooth_pitch * (rotor.slot_width + 5 * rotor.air_gap) - rotor.slot_width ** 2)
        self.air_gap_coef = self.stator_teeth_air_gap_coef + self.stator_vent_air_gap_coef +\
            self.stator_step_air_gap_coef + self.rotor_teeth_air_gap_coef - 3

    def __compute_lambda_2(self,
                           rotor: TurboMachineRotor,
                           pole_pairs: int
                           ) -> None:
        self.lambda_2 = rotor.length * pole_pairs / rotor.slot_count * \
                        ((rotor.slot_height - rotor.wedge_height - rotor.armature.insulation.all_fillings() -
                          rotor.armature.insulation.body_insulation) / 2 / rotor.slot_width +
                         (rotor.armature.insulation.wedge_filling + rotor.wedge_height) / rotor.wedge_width +
                         rotor.air_gap / (2 * rotor.tooth_pitch + rotor.air_gap / 2))

    def compute_stator_B_fields(self) -> None:
        self.B_field = {key: self.stator_flow / self._sections[key] for key in self._stator_keys}

    def compute_stator_H_fields(self,
                                rotor_surface_relation: float
                                ) -> None:
        # А вот это уже чистый хак - такой величины как напряжённость поля в зазоре в расчёте нет и там сразу считается
        # МДС. Однако мне тогда придётся оставлять пустое поле, что малость нарушает единство структуры, и писать
        # отдельно вычисление для МДС зазора. А так я смогу просто написать dictionary comprehension. Но увы,
        # унифицировать всё не получится, так что тут всё же пришлось использовать явные ключи словарей
        # Да, кстати, 8000 - это комбинация приводного множителя и коэффициента в формуле
        self.H_field = {"air gap": 8e3 * self.air_gap_coef * self.B_field["air gap"]}

        stator_yoke_eff_B = self.B_field["stator yoke"] * \
                            (18 - 10 * rotor_surface_relation) / (18 - 9 * rotor_surface_relation)

        # TODO: А собственно, где этот весь коэффициент ответвления в пазы статора и прочие пафосные названия? Надо
        #  выпытать
        # UPD: Домогнулся. Ничего не дало. Ждём-с
        if type(self.stator_steel) is dict:
            # Колдуны. Колдуны и ведьмы. Режут ярмо вдоль проката. Говорят, что так в сумме потери меньше. Я помню, что
            # должно быть наоборот, но тут уже не моя забота расследовать, кто прав, а кто нет. Если написанное в двух
            # строках ниже не есть правильно - это на совести тех, кто придумал расчётную методику. Аминь
            self.H_field["stator yoke"] = float(self.stator_steel["yoke"].BH_curve(stator_yoke_eff_B))
            self.H_field["stator teeth"] = \
                float(self.stator_steel["teeth"].BH_curve(self.B_field["stator teeth"]))
        else:
            self.H_field["stator yoke"] = float(self.stator_steel.BH_curve(stator_yoke_eff_B))
            self.H_field["stator teeth"] = \
                float(self.stator_steel.BH_curve(self.B_field["stator teeth"]))

    def compute_stator_MMF(self) -> None:
        mmf = {key: self.H_field[key] * self._lines[key] for key in self._stator_keys}
        self.MMF = mmf
        self.stator_MMF = sum(mmf.values())

    def compute_rotor_B_fields(self) -> None:
        self.B_field.update({key: self.rotor_flow / self._sections[key] if self._sections[key] is
                                                                           not None else None for key in self._rotor_keys})

    def compute_rotor_H_fields(self,
                               rotor_yoke_saturation_factor: float
                               ) -> None:
        # TODO: Найти нормальный способ считать напряжённости (а заодно и характеристику холостого хода): скачок на
        #  характеристике - это не серьёзно
        self.H_field["rotor yoke"] = float(self.rotor_steel.BH_curve(self.B_field["rotor yoke"]) *
                                           rotor_yoke_saturation_factor)

        # А теперь мы вспомним функциональное программирование и заставим змейку прикинуться Haskell'ем и эмулировать
        # нам zipWith3. Let There Be Rock!
        # А вообще: мне одному кажется нелогичным, что функция с названием "отобразить" используется не только для
        # отображений, но и для слияний с помощью функций, тогда как функция с подходящим названием "слить" умеет только
        # делать списки кортежей из наборов списков? Равно как и наличие функции sum при отсутствии функции product (без
        # подключений модулей)? Наркоманы, короче
        def helper(key: str, b_field: float, branching_factor: float) -> Tuple[str, Optional[float]]:
            if b_field is None:
                h_field = None
            elif b_field > 2.05:
                h_field = (b_field - 1.956) * 5.2 / (8 + 6.5 * branching_factor) * 1e4
            else:
                h_field = float(self.rotor_steel.BH_curve(b_field))
            return key, h_field

        keys = self._rotor_branching_factors.keys()
        factors = self._rotor_branching_factors.values()
        b_fields = [self.B_field[key] for key in keys]

        self.H_field.update(map(helper, keys, b_fields, factors))

    def compute_rotor_MMF(self) -> None:
        mmf = {key: self.H_field[key] * self._lines[key] if self.H_field[key] is not None else None
               for key in self._rotor_keys}
        self.MMF.update(mmf)
        self.total_MMF = sum(filter(None, self.MMF.values()))


class NoLoadMagneticCircuit(MagneticCircuit):
    __slots__ = ["rotor_current", "magnetizing_current"]

    def __init__(self,
                 stator: ACMachineStator,
                 rotor: TurboMachineRotor,
                 stator_steel: Union[Dict[str, Steel], Steel],
                 rotor_steel: Steel,
                 pole_pairs: int,
                 fill_factor: float
                 ) -> None:
        super().__init__(stator, rotor, stator_steel, rotor_steel, pole_pairs, fill_factor)

        self.rotor_current: Optional[float] = None  # Ток ротора на холостом ходу, А
        self.magnetizing_current: Optional[float] = None  # Ток намагничивания, А

    def compute_stator_flow(self,
                            stator: ACMachineStator,
                            voltage: int,
                            frequency: int
                            ) -> None:
        # 0.13 в качестве множителя в качестве мини-оптимизации: в формуле написано 0.26 * 50 / 100 и ещё куча
        # переменных множителей
        self.stator_flow = 0.13 * voltage / frequency / stator.armature.turn_count / stator.get_armature_coefficient()

    def compute_rotor_flow(self,
                           rotor: TurboMachineRotor,
                           bandaging: TurboMachineRotorBandaging,
                           stator_length: float
                           ) -> None:
        self.phi_s = self.lambda_2 * self.stator_MMF * 1e-8  # Поперечно-пазовый поток рассеяния

        # Поток рассеяния через бандажи. Если бандаж магнитный, то считаем, если нет - то нет его
        if bandaging.ismagnetic:
            self.phi_b = 1.2 * (bandaging.outer_diameter - bandaging.inner_diameter) / \
                         stator_length * rotor.air_gap * self.stator_flow / bandaging.offset
        else:
            self.phi_b = 0

        self.rotor_flow = self.stator_flow + self.phi_s + self.phi_b

    def compute_rotor_currents(self,
                               rotor_turn_count: Union[int, float]
                               ) -> None:
        self.rotor_current = self.total_MMF / rotor_turn_count
        self.magnetizing_current = self.MMF["air gap"] / rotor_turn_count

    def get_no_load_characteristic(self,
                                   rotor: TurboMachineRotor
                                   ):
        voltage_levels = np.linspace(0, 1.2, num=30)  # Думаю, 30-ти точек хватит за глаза - характеристика-то простая

        b_fields = {key: self.B_field[key] * voltage_levels for key in self._stator_keys}
        b_fields["stator yoke"] *= (18 - 10 * rotor.surface_relation) / (18 - 9 * rotor.surface_relation)
        h_fields = {"air gap": 8e3 * self.air_gap_coef * b_fields["air gap"]}

        if type(self.stator_steel) is dict:
            h_fields["stator yoke"] = self.stator_steel["yoke"].BH_curve(b_fields["stator yoke"])
            h_fields["stator teeth"] = self.stator_steel["teeth"].BH_curve(b_fields["stator teeth"])
        else:
            h_fields.update({k: self.stator_steel.BH_curve(b_fields[k]) for k in ["stator yoke", "stator teeth"]})

        mmf = {key: h_fields[key] * self._lines[key] for key in self._stator_keys}
        stator_mmf = sum(mmf.values())
        rotor_flow = (self.stator_flow + self.phi_b) * voltage_levels + \
                     self.lambda_2 * stator_mmf * 1e-8

        b_fields.update({k: rotor_flow / self._sections[k] if self._sections[k] is not None
                         else None for k in self._rotor_keys})
        h_fields["rotor yoke"] = self.rotor_steel.BH_curve(b_fields["rotor yoke"]) * rotor.get_yoke_saturation_factor()

        def helper(key: str, b_field: np.array, branching_factor: float) -> Tuple[str, Optional[np.array]]:
            if b_field is None:
                return key, None

            h_field = []
            for b in b_field:
                if b > 2.05:
                    h_field.append((b - 1.956) * 5.2 / (8 + 6.5 * branching_factor) * 1e4)
                else:
                    h_field.append(self.rotor_steel.BH_curve(b))
            h_field = np.array(h_field)

            return key, h_field

        keys = self._rotor_branching_factors.keys()
        factors = self._rotor_branching_factors.values()
        b_fields_tmp = [b_fields[key] for key in keys]

        h_fields.update(map(helper, keys, b_fields_tmp, factors))
        mmf.update({key: h_fields[key] * self._lines[key] if h_fields[key] is not None else None
                    for key in self._rotor_keys})
        mmf_total = sum(filter(lambda x: x is not None, mmf.values()))

        rotor_current = list(mmf_total / rotor.armature.turn_count)
        voltage_levels = list(voltage_levels)

        return rotor_current, voltage_levels


class LoadedMagneticCircuit(MagneticCircuit):
    __slots__ = ["stator_reaction_MMF",
                 "stator_reaction_MMF_reduced",
                 "stator_reaction_current_reduced",
                 "rotor_SC_current",
                 "rotor_SC_MMF",
                 "field_current",
                 "nominal_field_current",
                 "nominal_field_MMF",
                 "relative_EMF"
                 ]

    def __init__(self,
                 stator: ACMachineStator,
                 rotor: TurboMachineRotor,
                 stator_steel: Union[Dict[str, Steel], Steel],
                 rotor_steel: Steel,
                 pole_pairs: int,
                 fill_factor: float
                 ) -> None:
        super().__init__(stator, rotor, stator_steel, rotor_steel, pole_pairs, fill_factor)

        self.stator_reaction_MMF: Optional[float] = None  # МДС реакции якоря, А
        self.stator_reaction_MMF_reduced: Optional[float] = None  # Она же, приведённая к обмотке ротора
        self.stator_reaction_current_reduced: Optional[float] = None  # Ток реакции якоря, приведённый к обмотке ротора

        self.rotor_SC_current: Optional[float] = None
        self.rotor_SC_MMF: Optional[float] = None
        self.field_current: Optional[float] = None
        self.nominal_field_current: Optional[float] = None
        self.nominal_field_MMF: Optional[float] = None

        self.relative_EMF: Optional[float] = None

    def compute_stator_reaction(self,
                                current: float,
                                pole_pairs: int,
                                phase_count: int,
                                stator_turn_count: Union[int, float],
                                stator_armature_coefficient: float,
                                rotor_turn_count: Union[int, float],
                                rotor_armature_coefficient: float
                                ) -> None:
        self.stator_reaction_MMF = 1.06 * current * stator_turn_count * stator_armature_coefficient * phase_count /\
            3 / pole_pairs
        self.stator_reaction_MMF_reduced = self.stator_reaction_MMF / rotor_armature_coefficient
        self.stator_reaction_current_reduced = self.stator_reaction_MMF_reduced / rotor_turn_count

    def compute_SC_current(self,
                           x_stator: float,
                           magnetizing_current: float
                           ) -> None:
        self.rotor_SC_current = self.stator_reaction_current_reduced + x_stator * magnetizing_current

    def compute_EMF(self,
                    cos_phi: float,
                    sin_phi: float,
                    x_stator: float
                    ) -> None:
        # Тут, вообще, не очень-то и понятно, с этими пере- и недовозбуждениями, так что пока считаем только для
        # перевозбуждения, потому что что-то такое я слышал от главного конструктора.

        # А вообще обожаю эти относительные единицы, ага. Давайте складывать сопротивление с синусом угла, а потом ещё и
        # брать корни из этого, и заявлять, что это напряжение. М-м-м... Кайф.
        self.relative_EMF = math.hypot(cos_phi, sin_phi + x_stator)

    def compute_rotor_SC_MMF(self,
                             rotor_turn_count: Union[int, float]
                             ) -> None:
        self.rotor_SC_MMF = rotor_turn_count * self.rotor_SC_current

    def compute_stator_flow(self,
                            no_load_flow: float
                            ) -> None:
        self.stator_flow = no_load_flow * self.relative_EMF

    def compute_rotor_flow(self,
                           rotor: TurboMachineRotor,
                           bandaging: TurboMachineRotorBandaging,
                           stator_length: float,
                           sin_phi: float,
                           x_stator: float
                           ) -> None:
        # Магия! Почему считаем именно так - тайна сродни тому, под какой травой японцы придумывают сюжеты для аниме или
        # как выжить в России
        magic_MMF = math.sqrt(self.stator_reaction_MMF_reduced ** 2 + self.stator_MMF ** 2 +
                              2 * self.stator_reaction_MMF_reduced * self.stator_MMF *
                              (x_stator + sin_phi / self.relative_EMF))
        self.phi_s = self.lambda_2 * magic_MMF * 1e-8  # Поперечно-пазовый поток рассеяния

        # Поток рассеяния через бандажи. Если бандаж магнитный, то считаем, если нет - то нет его
        if bandaging.ismagnetic:
            self.phi_b = 1.2 * (bandaging.outer_diameter - bandaging.inner_diameter) / \
                         stator_length * rotor.air_gap * self.stator_flow / bandaging.offset
        else:
            self.phi_b = 0

        self.rotor_flow = self.stator_flow + self.phi_s + self.phi_b

    def compute_field_current(self,
                              rotor_turn_count: Union[int, float],
                              sin_phi: float,
                              x_stator: float
                              ) -> None:
        self.field_current = self.total_MMF / rotor_turn_count
        self.nominal_field_MMF = math.sqrt(self.total_MMF ** 2 + self.stator_reaction_MMF_reduced ** 2 +
                                           2 * self.total_MMF * self.stator_reaction_MMF_reduced *
                                           (x_stator + sin_phi / self.relative_EMF))
        self.nominal_field_current = self.nominal_field_MMF / rotor_turn_count

    def get_static_overload(self,
                            cos_phi: float
                            ) -> float:
        return self.nominal_field_current / self.rotor_SC_current / cos_phi

    def get_SCR(self,
                no_load_current: float
                ) -> float:
        return no_load_current / self.rotor_SC_current


__all__ = ["MagneticCircuit", "NoLoadMagneticCircuit", "LoadedMagneticCircuit"]
