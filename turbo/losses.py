import math
from typing import Dict, Optional, Union
from scipy import interpolate

from common.stator import ACMachineStator
from common.steelDatabase import Steel
from turbo.magneticCircuit import LoadedMagneticCircuit, NoLoadMagneticCircuit
from turbo.mass import Mass
from turbo.rotor import *


class Losses:
    __slots__ = ["__stator_steel",
                 "__freq_reduced",
                 "__phi_gamma",
                 "__phi_beta",
                 "stator_ohmic",
                 "stator_copper",
                 "stator_SC_surface_harmonics",
                 "stator_SC_surface_teeth",
                 "stator_SC_pulse",
                 "rotor_SC_surface_harmonics",
                 "rotor_SC_surface_teeth",
                 "screen_and_plate",
                 "end_part_yoke",
                 "end_part_teeth",
                 "structural_parts",
                 "end_part_SC_losses",
                 "steel_SC_losses",
                 "stator_yoke",
                 "stator_teeth",
                 "stator_steel",
                 "stator_OC_surface_harmonics",
                 "stator_OC_surface_teeth",
                 "stator_OC_pulse",
                 "stator_OC_add_pulse",
                 "rotor_add_surface",
                 "end_part_OC_losses",
                 "steel_OC_losses",
                 "excitation",
                 "bearings",
                 "rotor_friction",
                 "bandaging_friction",
                 "brush_ring",
                 "brush_crossarm",
                 "ventilation",
                 "mechanical",
                 "Field_coefficient"
                 ]

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self,
                 stator_steel: Union[Dict[str, Steel], Steel],
                 frequency: float) -> None:
        self.__stator_steel = stator_steel
        self.__freq_reduced: float = frequency / 50

        # А вот так. Я сразу создам эту дурную функцию (или что оно там такое? Интерполятор?), дабы оно создавалось лишь
        # раз и потом можно было сколько угодно вызывать метод, её (его) использующий. А то вот что-то мне подсказывает,
        # что нужны будут графики потом...
        gamma = [i / 100 for i in range(60, 86)]
        phi_gamma = [12.8, 11.6, 10.4, 9.2, 8.2, 7.2, 6.4, 5.8, 5.4, 5.2, 5.2, 5.4, 5.6, 6.2, 6.6, 7.4, 8, 8.8, 9.6,
                     10.6, 11.4, 12.4, 13.2, 14, 15.2, 16.2]
        self.__phi_gamma = interpolate.interp1d(gamma, phi_gamma, kind="linear")

        # И ещё разок!
        beta = [i / 100 for i in range(40, 101)]
        phi_beta = [2.8, 3.2, 3.8, 4.4, 5.2, 6.2, 7.2, 8.6, 9.8, 11.1, 12.2, 13.2, 15.1, 16.3, 17.2, 18.6, 19.6, 20.1,
                    20.3, 20.4, 21.5, 21.6, 21.3, 21.2, 20.9, 20.5, 19.8, 17.7, 16.8, 14.9, 13.4, 11.8, 10.2, 8.6, 7.2,
                    5.7, 4.4, 3.1, 2.1, 1.6, 1.4, 1.4, 1.6, 2.1, 2.8, 4.0, 5.2, 6.4, 7.8, 9.4, 11.8, 14.1, 16.5, 18.2,
                    20.4, 22.2, 23.3, 24.0, 24.5, 24.8, 25.0]
        self.__phi_beta = interpolate.interp1d(beta, phi_beta, kind="linear")

        # Все потери в киловаттах
        self.stator_ohmic: Optional[float] = None  # Омические потери в статоре
        self.stator_copper: Optional[float] = None  # Полные потери в обмотке статора
        self.stator_SC_surface_harmonics: Optional[float] = None  # Потери на пов-ти статора из-за гармоник поля ротора
        self.stator_SC_surface_teeth: Optional[float] = None  # Потери на пов-ти статора из-за зубцов ротора
        self.stator_SC_pulse: Optional[float] = None  # Пульсационные потери в зубцах статора

        self.rotor_SC_surface_harmonics: Optional[float] = None  # Потери на пов-ти ротора из-за гармоник поля
        self.rotor_SC_surface_teeth: Optional[float] = None  # Потери на пов-ти ротора из-за зубцов статора

        self.screen_and_plate: Optional[float] = None  # Потери в нажимной пластине и медном экране
        self.end_part_yoke: Optional[float] = None
        self.end_part_teeth: Optional[float] = None  # Потери в зубцах крайнего пакета
        self.structural_parts: Optional[float] = None  # Потери в конструктивных деталях

        self.end_part_SC_losses: Optional[float] = None  # Сумма потерь в торцевой зоне при КЗ
        self.steel_SC_losses: Optional[float] = None  # Сумма потерь в стали при КЗ

        self.stator_yoke: Optional[float] = None
        self.stator_teeth: Optional[float] = None
        self.stator_steel: Optional[float] = None
        self.stator_OC_surface_harmonics: Optional[float] = None  # Потери на пов-ти статора из-за гармоник поля ротора
        self.stator_OC_surface_teeth: Optional[float] = None  # Потери на пов-ти статора из-за зубцов ротора
        self.stator_OC_pulse: Optional[float] = None  # Пульсационные потери в зубцах статора
        self.stator_OC_add_pulse: Optional[float] = None  # Добавочные пульсационные потери в зубцах статора

        self.rotor_add_surface: Optional[float] = None  # Добавочные потери на пов-ти ротора

        self.end_part_OC_losses: Optional[float] = None  # Сумма потерь в торцевой зоне при ХХ
        self.steel_OC_losses: Optional[float] = None  # Сумма потерь ХХ

        self.excitation: Optional[float] = None  # Потери на возбуждение

        self.bearings: Optional[float] = None  # Потери в подшипниках
        self.rotor_friction: Optional[float] = None  # Потери на трение бочкой о воздух
        self.bandaging_friction: Optional[float] = None  # Потери на трение бандажом о воздух
        self.brush_ring: Optional[float] = None  # Потери на трение щёток о контактное кольцо
        self.brush_crossarm: Optional[float] = None  # Потери на трение щёток непонятно обо что, но вроде об траверсу
        # self.channel: Optional[float] = None  # Потери в вентиляционных каналах
        self.ventilation: Optional[float] = None  # Потери на вентиляцию
        self.mechanical: Optional[float] = None  # Полные механические потери

        self.Field_coefficient: Optional[float] = None  # Коэф-т Фильда / коэф-т добавочных потерь

    def compute_stator_copper_losses(self,
                                     stator: ACMachineStator,
                                     current: float,
                                     phase_count: int
                                     ) -> None:
        self.stator_ohmic = phase_count * stator.armature.resistance[75] * current ** 2 / 1e3
        self.Field_coefficient = 1 + 0.107 * (stator.armature.rows * stator.armature.columns *
                                              stator.armature.wire.wire_width * stator.effective_wires
                                              / stator.slot_width * self.__freq_reduced) ** 2 *\
                                 (stator.armature.wire.wire_height / 10) ** 4
        self.stator_copper = self.stator_ohmic * self.Field_coefficient

    def __compute_stator_SC_steel_losses(self,
                                         stator: ACMachineStator,
                                         rotor: TurboMachineRotor,
                                         mag_circuit: LoadedMagneticCircuit,
                                         mass: Mass,
                                         pole_pairs: int) -> None:
        # Это у меня есть произведение полуторной степени приведённой частоты на квадрат отношение МДС к зазору. Просто
        # это значение тут во всех трёх формулах есть
        MMF_freq_15 = (mag_circuit.rotor_SC_MMF / mag_circuit.air_gap_coef / rotor.air_gap) ** 2 *\
            self.__freq_reduced ** 1.5

        # Очередной дурной коэффициент. А вообще, если сделать график вот этого, то можно понять, что оно очень похоже
        # на некоторую элементарную функцию. Что мешало просто дать формулу для неё - тайна сия велика есть.  А степень
        # 7.5 - это, конечно, красота, да-а-а... На кол посадить мало за такое
        self.stator_SC_surface_harmonics = self.__phi_gamma(rotor.surface_relation) * MMF_freq_15 *\
            stator.effective_length * stator.inner_diameter ** 3 / rotor.outer_diameter ** 3.5 / 10 ** 7.5

        aux = 2 * math.pi * rotor.air_gap / rotor.tooth_pitch
        k_t2 = (aux / math.sinh(aux)) ** 2  # Это такой коэффициент потерь с учётом затухания потока в зазоре.
        phi_Z2 = 5e4 / rotor.surface_relation * (pole_pairs / rotor.slot_pitch_count) ** 2.5
        self.stator_SC_surface_teeth = phi_Z2 * k_t2 * MMF_freq_15 * stator.effective_length *\
            stator.inner_diameter ** 3 / pole_pairs ** 2 / 1e18

        self.stator_SC_pulse = 12.5 / rotor.surface_relation * k_t2 * MMF_freq_15 * mass.stator_teeth /\
            math.sqrt(rotor.slot_pitch_count) / 1e9

    def __compute_rotor_SC_steel_losses(self,
                                        stator: ACMachineStator,
                                        rotor: TurboMachineRotor,
                                        mag_circuit: LoadedMagneticCircuit,
                                        pole_pairs: int) -> None:
        freq_15 = self.__freq_reduced ** 1.5

        self.rotor_SC_surface_harmonics = self.__phi_beta(stator.armature.shortening) * freq_15 * \
                                          stator.inner_diameter ** 5 / pole_pairs ** 4 * rotor.length * \
                                          (stator.current_load / mag_circuit.air_gap_coef / rotor.air_gap) ** 2 / 1e20

        phi_delta = 62.7 * (stator.get_armature_coefficient() /
                            math.sinh(2 * math.pi * rotor.air_gap / stator.tooth_pitch)) ** 2
        self.rotor_SC_surface_teeth = phi_delta * freq_15 * stator.current_load ** 2 *\
            stator.inner_diameter ** 3 / pole_pairs ** 1.5 * rotor.length / math.sqrt(stator.slot_count) / 1e16

    def compute_SC_steel_losses(self,
                                stator: ACMachineStator,
                                rotor: TurboMachineRotor,
                                mag_circuit: LoadedMagneticCircuit,
                                mass: Mass,
                                pole_pairs: int
                                ) -> None:
        self.__compute_stator_SC_steel_losses(stator, rotor, mag_circuit, mass, pole_pairs)
        self.__compute_rotor_SC_steel_losses(stator, rotor, mag_circuit, pole_pairs)

        self.steel_SC_losses = self.stator_SC_surface_harmonics + self.stator_SC_surface_teeth +\
            self.stator_SC_pulse + self.rotor_SC_surface_harmonics + self.rotor_SC_surface_teeth

    def __compute_stator_OC_steel_losses(self,
                                         stator: ACMachineStator,
                                         rotor: TurboMachineRotor,
                                         mag_circuit: NoLoadMagneticCircuit,
                                         mass: Mass,
                                         pole_pairs: int,
                                         k_x: float,  # Коэф-т увеличения потерь в стали. И зачем он только нужен...
                                         scr: float   # Отношение короткого замыкания
                                         ) -> None:
        # Тут у нас начинаются удельные потери в стали. А поскольку сталь у нас может быть словарём или просто сталью,
        # то надо проверять, что происходит
        if type(self.__stator_steel) is dict:
            W_a = self.__stator_steel["yoke"].losses_curve(mag_circuit.B_field["stator yoke"])
            W_z = self.__stator_steel["teeth"].losses_curve(mag_circuit.B_field["stator teeth"])
        else:
            W_a = self.__stator_steel.losses_curve(mag_circuit.B_field["stator yoke"])
            W_z = self.__stator_steel.losses_curve(mag_circuit.B_field["stator yoke"])

        freq_15 = self.__freq_reduced ** 1.5

        self.stator_yoke = 1.3 * k_x * W_a * mass.stator_yoke * freq_15 / 1e3
        self.stator_teeth = 1.5 * W_z * mass.stator_teeth * freq_15 / 1e3

        # Дальше один нюанс. В простом расчёте ПОЧЕМУ-ТО потерями в стали считается только сумма этих двух. С какого
        # перепуга-то?! У вас что, чай состоит только из воды, а заварка и сахар - это "добавочные ингредиенты"?
        # Извращенцы. Поэтому я напишу отдельный метод, выдающий только сумму этих двух, а в потери в стали запишу всё,
        # вместе с пульсациями и прочим таким
        scr **= 2
        aux = rotor.slot_width / rotor.air_gap
        gamma_c = aux ** 2 / (aux + 5)

        self.stator_OC_surface_harmonics = self.stator_SC_surface_harmonics * scr
        self.stator_OC_surface_teeth = self.stator_SC_surface_teeth * scr
        self.stator_OC_pulse = self.stator_SC_pulse * scr
        self.stator_OC_add_pulse = W_z * mass.stator_teeth * rotor.surface_relation *\
            (gamma_c * rotor.air_gap * rotor.slot_pitch_count * self.__freq_reduced /
             2 / stator.tooth_pitch / pole_pairs) ** 2 / 1e3

        self.stator_steel = self.stator_yoke + self.stator_teeth + self.stator_OC_surface_harmonics +\
            self.stator_OC_surface_teeth + self.stator_OC_pulse + self.stator_OC_add_pulse

    def __compute_rotor_OC_steel_losses(self,
                                        stator: ACMachineStator,
                                        mag_circuit: NoLoadMagneticCircuit,
                                        pole_pairs: int
                                        ) -> None:
        self.rotor_add_surface = 5.1 / math.sqrt(stator.slot_count) * stator.effective_length *\
            self.__freq_reduced ** 1.5 * stator.inner_diameter ** 3 / pole_pairs ** 1.5 *\
            (mag_circuit.B_field["air gap"] * (mag_circuit.stator_teeth_air_gap_coef - 1)) ** 2 / 1e8

    def compute_OC_steel_losses(self,
                                stator: ACMachineStator,
                                rotor: TurboMachineRotor,
                                mag_circuit: NoLoadMagneticCircuit,
                                mass: Mass,
                                pole_pairs: int,
                                k_x: float,
                                scr: float) -> None:
        self.__compute_stator_OC_steel_losses(stator, rotor, mag_circuit, mass, pole_pairs, k_x, scr)
        self.__compute_rotor_OC_steel_losses(stator, mag_circuit, pole_pairs)

        self.steel_OC_losses = self.stator_steel + self.rotor_add_surface

    def compute_end_part_SC_losses(self,
                                   stator: ACMachineStator,
                                   rotor: TurboMachineRotor,
                                   mag_circuit: LoadedMagneticCircuit,
                                   pole_pairs: int,
                                   k_z: int  # Число разбиений крайнего пакета
                                   ) -> None:
        stator_yoke_height = stator.get_yoke_height()

        self.structural_parts = (stator.current_load * stator.inner_diameter) ** 2 / 1e11
        b_z = (stator.tooth_pitch + stator.get_tooth_pitch_bottom()) / 2 - stator.slot_width
        self.end_part_teeth = 0.21 * stator.slot_count / k_z * \
            (b_z * mag_circuit.stator_reaction_MMF * stator.slot_height /
             (stator.slot_height + rotor.slot_height)) ** 2 * self.__freq_reduced ** 1.5 / 1e13
        self.end_part_SC_losses = self.end_part_teeth + self.structural_parts

        if stator.pressure_plate_thickness is not None:
            # А в противном случае ничего делать не надо, всё равно этих потерь там нет, а значит и потери в торцевой
            # зоне машины состоят только из вышеописанного

            # Толщина медного экрана. Если есть, то есть, хорошо, а если нет, то локально примем её равно нулю, ибо так
            # проще написать будет
            copper_screen = stator.copper_screen_thickness if stator.copper_screen_thickness is not None else 0

            # Странный, непонятный коэффициент, названия коему я не видел
            beta = math.pi / 10 * math.sqrt(stator.pressure_plate_thickness / stator_yoke_height * self.__freq_reduced *
                                            (1 + copper_screen / stator.pressure_plate_thickness))
            phi_beta = 155 * (10 / beta) ** 2 / stator_yoke_height

            self.screen_and_plate = phi_beta * (0.16 * stator.pressure_plate_thickness + 3.2 * copper_screen) /\
                (stator.outer_diameter - 2 * stator_yoke_height) *\
                (mag_circuit.stator_reaction_MMF * self.__freq_reduced / beta / pole_pairs) ** 2 / 1e11
            self.end_part_yoke = 0.015 * stator_yoke_height * mag_circuit.stator_reaction_MMF ** 2 / beta /\
                pole_pairs ** 3 * self.__freq_reduced ** 1.5 / 1e10
            self.end_part_SC_losses += self.screen_and_plate + self.end_part_yoke

    def compute_end_part_OC_losses(self,
                                   scr: float
                                   ) -> None:
        self.end_part_OC_losses = self.end_part_SC_losses * scr ** 2

    def compute_excitation_losses(self,
                                  rotor: TurboMachineRotor,
                                  mag_circuit: LoadedMagneticCircuit,
                                  exc_efficiency: float  # КПД возбудителя
                                  ) -> None:
        self.excitation = (mag_circuit.nominal_field_current ** 2 * rotor.armature.resistance[75] +
                           2 * mag_circuit.nominal_field_current) / exc_efficiency / 1e3

    def __compute_bearing_losses(self,
                                 mass: Mass,
                                 shaft: Shaft,
                                 pole_pairs: int
                                 ) -> None:
        self.bearings = 255 * math.sqrt(mass.rotor * shaft.journal_length / 2) *\
            (self.__freq_reduced * shaft.journal_diameter / pole_pairs) ** 1.5 / 10 ** 7.5

    def __compute_air_friction_losses(self,
                                      rotor: TurboMachineRotor,
                                      bandaging: TurboMachineRotorBandaging,
                                      pole_pairs: int
                                      ) -> None:
        freq_p_3 = (self.__freq_reduced / pole_pairs) ** 3
        self.rotor_friction = 57.3 * freq_p_3 * rotor.length * rotor.outer_diameter ** 4 / 1e15
        self.bandaging_friction = 25 * freq_p_3 * bandaging.ring_width * bandaging.outer_diameter ** 4 / 1e15

    def __compute_brush_losses(self,
                               shaft: Shaft,
                               pole_pairs: int
                               ) -> None:
        aux = self.__freq_reduced * shaft.brush_width * shaft.brush_length / 2 / pole_pairs

        self.brush_ring = shaft.ring_outer_diameter * shaft.ring_brush_count * aux / 1e6
        self.brush_crossarm = shaft.ring_inner_diameter * shaft.crossarm_brush_count * aux / 1e6

    def __compute_ventilation_losses(self,
                                     slot_rate: float,
                                     end_part_rate: float,
                                     slot_velocity: float,
                                     end_part_velocity: float,
                                     overheat_gen: float,  # Превышение температуры воздуха в генераторе
                                     overheat_vent: float  # Превышение температуры воздуха в вентиляторе
                                     ) -> None:
        channel = (slot_velocity * slot_rate + end_part_velocity * end_part_rate) / 10

        # Расход воздуха. Замечательно. А что это за такие интересные значения, обозначение в богомерзкой Excel'ке как
        # "из расчёта Насти" тогда? Что это за расчёт такой, зачем он нужен и вообще, кто такая Настя? Кроме того,
        # расчёт прям магический - для любой машины получает расход воздуха 10 не то литров, не то кубометров в секунду
        # и скорость воздуха 2 м/с. Чтоб я так работал, как эта Настя
        sc_losses = self.stator_copper + self.steel_SC_losses + self.end_part_SC_losses
        oc_losses = self.stator_steel + self.rotor_add_surface + self.end_part_OC_losses
        air_flow_rate = (sc_losses + oc_losses + self.excitation +
                         self.rotor_friction + self.bandaging_friction + channel) /\
                        1.1 / (overheat_gen - overheat_vent)
        if air_flow_rate < 0:
            raise ValueError("Отрицательное значение расхода воздуха на вентиляцию")

        self.ventilation = 1.1 * air_flow_rate * overheat_vent

    def compute_mechanical_losses(self,
                                  rotor: TurboMachineRotor,
                                  bandaging: TurboMachineRotorBandaging,
                                  mass: Mass,
                                  shaft: Shaft,
                                  pole_pairs: int,
                                  slot_rate: float,
                                  end_part_rate: float,
                                  slot_velocity: float,
                                  end_part_velocity: float,
                                  overheat_gen: float,  # Превышение температуры воздуха в генераторе
                                  overheat_vent: float  # Превышение температуры воздуха в вентиляторе
                                  ) -> None:
        self.__compute_bearing_losses(mass, shaft, pole_pairs)
        self.__compute_air_friction_losses(rotor, bandaging, pole_pairs)
        self.__compute_brush_losses(shaft, pole_pairs)
        self.__compute_ventilation_losses(slot_rate, end_part_rate, slot_velocity, end_part_velocity, overheat_gen,
                                          overheat_vent)

        self.mechanical = self.rotor_friction + self.bandaging_friction + self.brush_ring + self.brush_ring +\
            self.bearings + self.ventilation

    def get_normal_stator_steel_losses(self) -> float:
        return self.stator_yoke + self.stator_teeth

    def get_total_SC_losses(self) -> float:
        return self.stator_copper + self.steel_SC_losses + self.end_part_SC_losses

    def get_total_OC_losses(self) -> float:
        return self.stator_steel + self.rotor_add_surface + self.end_part_OC_losses

    def get_efficiency(self,
                       power: float
                       ) -> float:
        losses = self.stator_copper + self.steel_SC_losses + self.end_part_SC_losses + self.stator_steel +\
            self.rotor_add_surface + self.end_part_OC_losses + self.excitation + self.mechanical

        return power / (power + losses)


__all__ = "Losses"
