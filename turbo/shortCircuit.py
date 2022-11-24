import math
from typing import Dict, Optional

from common.stator import ACMachineStator
from turbo.magneticCircuit import NoLoadMagneticCircuit
from turbo.reactances import Reactances
from turbo.rotor import TurboMachineRotor


class TimeConstants:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self) -> None:
        self.T_d0: Optional[float] = None
        self.T_d0_prime: Optional[float] = None
        self.T_d0_2prime: Optional[float] = None

        self.T_d_prime: Dict[str, Optional[float]] = {"1 phase": None,
                                                      "2 phase": None,
                                                      "3 phase": None}
        self.T_d_2prime: Dict[str, Optional[float]] = {"1 phase": None,
                                                       "2 phase": None,
                                                       "3 phase": None}
        self.T_a: Dict[str, Optional[float]] = {"1 phase": None,
                                                "2 phase": None}

    def compute_rotor_time_constants(self,
                                     rotor: TurboMachineRotor,
                                     mag_circuit: NoLoadMagneticCircuit,
                                     xs: Reactances,
                                     pole_pairs: int
                                     ) -> None:
        # Считаем какую-то странную постоянную времени роторной обмотки без статора. И да, тут опять специфические
        # названия, как с иксами
        self.T_d0 = 2 * pole_pairs * rotor.armature.turn_count * rotor.get_armature_coefficient(pole_pairs) * \
                    xs.rotor_dissipation_factor * mag_circuit.rotor_flow / \
                    mag_circuit.magnetizing_current / rotor.armature.resistance[75]

        self.T_d0_prime = 4 * self.T_d0 / 3
        self.T_d0_2prime = self.T_d0 * xs.rotor_dissipation_factor / 4

    def compute_transients(self,
                           xs: Reactances
                           ) -> None:
        coef_1 = (xs.x_d_prime + xs.x_2 + xs.x_0) / (xs.x_d + xs.x_2 + xs.x_0)
        coef_2 = (xs.x_d_prime + xs.x_2) / (xs.x_d + xs.x_2)
        coef_3 = xs.x_d_prime / xs.x_d

        self.T_d_prime = {"1 phase": self.T_d0_prime * coef_1,
                          "2 phase": self.T_d0_prime * coef_2,
                          "3 phase": self.T_d0_prime * coef_3}

    def compute_super_transients(self,
                                 xs: Reactances
                                 ) -> None:
        coef_1 = (xs.x_d_2prime + xs.x_2 + xs.x_0) / (xs.x_d_prime + xs.x_2 + xs.x_0)
        coef_2 = (xs.x_d_2prime + xs.x_2) / (xs.x_d_prime + xs.x_2)
        coef_3 = xs.x_d_2prime / xs.x_d_prime

        self.T_d_2prime = {"1 phase": self.T_d0_2prime * coef_1,
                           "2 phase": self.T_d0_2prime * coef_2,
                           "3 phase": self.T_d0_2prime * coef_3}

    def compute_aperiodic(self,
                          stator: ACMachineStator,
                          xs: Reactances,
                          frequency: float,
                          current: float,
                          voltage: float
                          ) -> None:
        # Сопротивление в о. е.
        rel_res = current * stator.armature.resistance[75] / voltage
        aux = 2 * math.pi * rel_res * frequency

        self.T_a = {"1 phase": (2 * xs.x_2 + xs.x_0) / 3 / aux,
                    "2 phase": xs.x_2 / aux}


class Currents:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self,
                 xs: Reactances,
                 rel_voltage: float,  # Кратность напряжения КЗ. Разницы, по сути, нет, ставить напряжение или кратность
                 rel_current: float  # Отношение номинального тока к намагничивающему
                 ) -> None:
        # Тут всё слишком просто, чтобы выносить расчёты в публичные методы, так что просто сделаю три приватных и их
        # вызову. Ибо воистину

        # Установившиеся токи
        self.static: Dict[str, Optional[float]] = {"1 phase": None,
                                                   "2 phase": None,
                                                   "3 phase": None}

        # Переходные токи
        self.transient: Dict[str, Optional[float]] = {"1 phase": None,
                                                      "2 phase": None,
                                                      "3 phase": None}

        # Сверхпереходные токи
        self.super_transient: Dict[str, Optional[float]] = {"1 phase": None,
                                                            "2 phase": None,
                                                            "3 phase": None}

        self.__compute_transients(xs, rel_voltage)
        self.__compute_super_transients(xs, rel_voltage)
        self.__compute_static(xs, rel_current)

    def __compute_transients(self,
                             xs: Reactances,
                             rel_voltage: float
                             ) -> None:
        coef_1 = 3 / (xs.x_d_prime + xs.x_2 + xs.x_0)
        coef_2 = math.sqrt(3) / (xs.x_d_prime + xs.x_2)

        self.transient = {"1 phase": rel_voltage * coef_1,
                          "2 phase": rel_voltage * coef_2,
                          "3 phase": rel_voltage / xs.x_d_prime}

    def __compute_super_transients(self,
                                   xs: Reactances,
                                   rel_voltage: float
                                   ) -> None:
        coef_1 = 3 / (xs.x_d_2prime + xs.x_2 + xs.x_0)
        coef_2 = math.sqrt(3) / (xs.x_d_2prime + xs.x_2)

        self.super_transient = {"1 phase": rel_voltage * coef_1,
                                "2 phase": rel_voltage * coef_2,
                                "3 phase": rel_voltage / xs.x_d_2prime}

    def __compute_static(self,
                         xs: Reactances,
                         rel_current: float
                         ) -> None:
        coef_1 = 3 / (xs.x_d + xs.x_2 + xs.x_0)
        coef_2 = math.sqrt(3) / (xs.x_d + xs.x_2)

        self.static = {"1 phase": rel_current * coef_1,
                       "2 phase": rel_current * coef_2,
                       "3 phase": rel_current / xs.x_d}


__all__ = "TimeConstants"
