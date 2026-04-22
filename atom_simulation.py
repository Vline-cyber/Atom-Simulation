import sys
import subprocess
import importlib

# ========== АВТОУСТАНОВКА ЗАВИСИМОСТЕЙ ==========
def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def ensure_dependencies():
    dependencies = {'pygame': 'pygame', 'numpy': 'numpy'}
    missing = []
    for module_name, pip_name in dependencies.items():
        try:
            importlib.import_module(module_name)
        except ImportError:
            missing.append(pip_name)
    if missing:
        print(f"Установка необходимых библиотек: {', '.join(missing)}")
        for package in missing:
            try:
                print(f"Устанавливаю {package}...")
                install_package(package)
                print(f"✓ {package} успешно установлен")
            except Exception as e:
                print(f"✗ Ошибка при установке {package}: {e}")
                print(f"pip install {' '.join(missing)}")
                sys.exit(1)
        print("Все зависимости установлены! Запуск симуляции...\n")

ensure_dependencies()

import pygame
import numpy as np
import random
from typing import List, Tuple, Optional, Callable, Set

# ========== НАСТРОЙКИ ==========
TOP_PANEL_HEIGHT = 120
BORDER = 10
BACKGROUND_COLOR = (20, 20, 30)
PANEL_COLOR = (40, 40, 50)
BORDER_COLOR = (60, 60, 70)
ELEMENT_PANEL_HEIGHT = 50

DT = 0.05
WALL_THRESHOLD = 30.0
WALL_STIFFNESS = 50.0

BOND_STIFFNESS = 500.0
BOND_DAMPING = 0.1
MAX_BOND_FORCE_FACTOR = 5.0

REPEAT_RATE = 20
REPEAT_DELAY = 0.3

CRYSTAL_LATTICE_SPACING = 30.0  # расстояние между узлами решётки (пиксели)

# ========== ПОЛНЫЕ ДАННЫЕ ЭЛЕМЕНТОВ (1-118) ==========
ELEMENT_DATA = {
    'H':  {'name': 'Водород', 'period': 1, 'group': 1,  'mass': 1.008,    'vdw_radius': 120, 'color': (255, 255, 255), 'epsilon': 1.0},
    'He': {'name': 'Гелий',   'period': 1, 'group': 18, 'mass': 4.0026,   'vdw_radius': 140, 'color': (217, 255, 255), 'epsilon': 0.2},
    'Li': {'name': 'Литий',  'period': 2, 'group': 1,  'mass': 6.94,     'vdw_radius': 182, 'color': (178, 255, 102), 'epsilon': 1.2},
    'Be': {'name': 'Бериллий','period': 2, 'group': 2,  'mass': 9.0122,   'vdw_radius': 153, 'color': (194, 255, 0),   'epsilon': 1.4},
    'B':  {'name': 'Бор',    'period': 2, 'group': 13, 'mass': 10.81,    'vdw_radius': 192, 'color': (255, 181, 181), 'epsilon': 1.6},
    'C':  {'name': 'Углерод',   'period': 2, 'group': 14, 'mass': 12.011,   'vdw_radius': 170, 'color': (80, 80, 80),    'epsilon': 1.5},
    'N':  {'name': 'Азот', 'period': 2, 'group': 15, 'mass': 14.007,   'vdw_radius': 155, 'color': (48, 80, 248),   'epsilon': 1.3},
    'O':  {'name': 'Кислород',   'period': 2, 'group': 16, 'mass': 15.999,   'vdw_radius': 152, 'color': (240, 0, 0),     'epsilon': 1.4},
    'F':  {'name': 'Фтор', 'period': 2, 'group': 17, 'mass': 18.998,   'vdw_radius': 147, 'color': (144, 224, 80),  'epsilon': 1.3},
    'Ne': {'name': 'Неон',     'period': 2, 'group': 18, 'mass': 20.180,   'vdw_radius': 154, 'color': (179, 227, 245), 'epsilon': 0.3},
    'Na': {'name': 'Натрий',   'period': 3, 'group': 1,  'mass': 22.990,   'vdw_radius': 227, 'color': (171, 92, 242),  'epsilon': 1.1},
    'Mg': {'name': 'Магний','period': 3, 'group': 2,  'mass': 24.305,   'vdw_radius': 173, 'color': (138, 255, 0),   'epsilon': 1.2},
    'Al': {'name': 'Алюминий','period': 3, 'group': 13, 'mass': 26.982,   'vdw_radius': 184, 'color': (191, 166, 166), 'epsilon': 1.8},
    'Si': {'name': 'Кремний',  'period': 3, 'group': 14, 'mass': 28.085,   'vdw_radius': 210, 'color': (240, 200, 160), 'epsilon': 2.0},
    'P':  {'name': 'Фосфор','period': 3, 'group': 15, 'mass': 30.974,   'vdw_radius': 180, 'color': (255, 128, 0),   'epsilon': 1.7},
    'S':  {'name': 'Сера',   'period': 3, 'group': 16, 'mass': 32.06,    'vdw_radius': 180, 'color': (255, 255, 48),  'epsilon': 1.9},
    'Cl': {'name': 'Хлор', 'period': 3, 'group': 17, 'mass': 35.45,    'vdw_radius': 175, 'color': (31, 240, 31),   'epsilon': 1.8},
    'Ar': {'name': 'Аргон',    'period': 3, 'group': 18, 'mass': 39.948,   'vdw_radius': 188, 'color': (128, 255, 128), 'epsilon': 1.0},
    'K':  {'name': 'Калий','period': 4, 'group': 1,  'mass': 39.098,   'vdw_radius': 275, 'color': (143, 64, 212),  'epsilon': 0.9},
    'Ca': {'name': 'Кальций',  'period': 4, 'group': 2,  'mass': 40.078,   'vdw_radius': 231, 'color': (61, 255, 0),    'epsilon': 1.1},
    'Sc': {'name': 'Скандий', 'period': 4, 'group': 3,  'mass': 44.956,   'vdw_radius': 211, 'color': (230, 230, 230), 'epsilon': 1.5},
    'Ti': {'name': 'Титан', 'period': 4, 'group': 4,  'mass': 47.867,   'vdw_radius': 200, 'color': (191, 194, 199), 'epsilon': 1.6},
    'V':  {'name': 'Ванадий', 'period': 4, 'group': 5,  'mass': 50.942,   'vdw_radius': 200, 'color': (166, 166, 171), 'epsilon': 1.7},
    'Cr': {'name': 'Хром', 'period': 4, 'group': 6,  'mass': 51.996,   'vdw_radius': 200, 'color': (138, 153, 199), 'epsilon': 1.8},
    'Mn': {'name': 'Марганец','period': 4, 'group': 7,  'mass': 54.938,   'vdw_radius': 200, 'color': (156, 122, 199), 'epsilon': 1.9},
    'Fe': {'name': 'Железо',     'period': 4, 'group': 8,  'mass': 55.845,   'vdw_radius': 200, 'color': (224, 102, 51),  'epsilon': 2.0},
    'Co': {'name': 'Кобальт',   'period': 4, 'group': 9,  'mass': 58.933,   'vdw_radius': 200, 'color': (240, 144, 160), 'epsilon': 2.1},
    'Ni': {'name': 'Никель',   'period': 4, 'group': 10, 'mass': 58.693,   'vdw_radius': 163, 'color': (80, 208, 80),   'epsilon': 2.2},
    'Cu': {'name': 'Медь',   'period': 4, 'group': 11, 'mass': 63.546,   'vdw_radius': 140, 'color': (200, 128, 51),  'epsilon': 2.3},
    'Zn': {'name': 'Цинк',     'period': 4, 'group': 12, 'mass': 65.38,    'vdw_radius': 139, 'color': (125, 128, 176), 'epsilon': 2.4},
    'Ga': {'name': 'Галлий',  'period': 4, 'group': 13, 'mass': 69.723,   'vdw_radius': 187, 'color': (194, 143, 143), 'epsilon': 1.5},
    'Ge': {'name': 'Германий','period': 4, 'group': 14, 'mass': 72.63,    'vdw_radius': 211, 'color': (102, 143, 143), 'epsilon': 1.6},
    'As': {'name': 'Мышьяк',  'period': 4, 'group': 15, 'mass': 74.922,   'vdw_radius': 185, 'color': (189, 128, 227), 'epsilon': 1.7},
    'Se': {'name': 'Селен', 'period': 4, 'group': 16, 'mass': 78.96,    'vdw_radius': 190, 'color': (255, 161, 0),   'epsilon': 1.8},
    'Br': {'name': 'Бром',  'period': 4, 'group': 17, 'mass': 79.904,   'vdw_radius': 185, 'color': (166, 41, 41),   'epsilon': 1.9},
    'Kr': {'name': 'Криптон',  'period': 4, 'group': 18, 'mass': 83.798,   'vdw_radius': 202, 'color': (92, 184, 209),  'epsilon': 0.5},
    'Rb': {'name': 'Рубидий', 'period': 5, 'group': 1,  'mass': 85.468,   'vdw_radius': 303, 'color': (112, 46, 176),  'epsilon': 0.8},
    'Sr': {'name': 'Стронций','period': 5, 'group': 2,  'mass': 87.62,    'vdw_radius': 249, 'color': (0, 255, 0),     'epsilon': 0.9},
    'Y':  {'name': 'Иттрий',  'period': 5, 'group': 3,  'mass': 88.906,   'vdw_radius': 219, 'color': (148, 255, 255), 'epsilon': 1.2},
    'Zr': {'name': 'Цирконий','period': 5, 'group': 4,  'mass': 91.224,   'vdw_radius': 186, 'color': (148, 224, 224), 'epsilon': 1.3},
    'Nb': {'name': 'Ниобий',  'period': 5, 'group': 5,  'mass': 92.906,   'vdw_radius': 186, 'color': (115, 194, 201), 'epsilon': 1.4},
    'Mo': {'name': 'Молибден','period': 5, 'group': 6,  'mass': 95.95,    'vdw_radius': 186, 'color': (84, 181, 181),  'epsilon': 1.5},
    'Tc': {'name': 'Технеций','period': 5, 'group': 7,  'mass': 98,       'vdw_radius': 186, 'color': (59, 158, 158),  'epsilon': 1.6},
    'Ru': {'name': 'Рутений','period': 5, 'group': 8,  'mass': 101.07,   'vdw_radius': 186, 'color': (36, 143, 143),  'epsilon': 1.7},
    'Rh': {'name': 'Родий',  'period': 5, 'group': 9,  'mass': 102.91,   'vdw_radius': 186, 'color': (10, 125, 140),  'epsilon': 1.8},
    'Pd': {'name': 'Палладий','period': 5, 'group': 10, 'mass': 106.42,   'vdw_radius': 163, 'color': (0, 105, 133),   'epsilon': 1.9},
    'Ag': {'name': 'Серебро',   'period': 5, 'group': 11, 'mass': 107.87,   'vdw_radius': 172, 'color': (192, 192, 192), 'epsilon': 2.0},
    'Cd': {'name': 'Кадмий',  'period': 5, 'group': 12, 'mass': 112.41,   'vdw_radius': 158, 'color': (255, 217, 143), 'epsilon': 2.1},
    'In': {'name': 'Индий',   'period': 5, 'group': 13, 'mass': 114.82,   'vdw_radius': 193, 'color': (166, 117, 115), 'epsilon': 1.4},
    'Sn': {'name': 'Олово',      'period': 5, 'group': 14, 'mass': 118.71,   'vdw_radius': 217, 'color': (102, 128, 128), 'epsilon': 1.5},
    'Sb': {'name': 'Сурьма', 'period': 5, 'group': 15, 'mass': 121.76,   'vdw_radius': 206, 'color': (158, 99, 181),  'epsilon': 1.6},
    'Te': {'name': 'Теллур','period': 5, 'group': 16, 'mass': 127.60,   'vdw_radius': 206, 'color': (212, 122, 0),   'epsilon': 1.7},
    'I':  {'name': 'Иод',   'period': 5, 'group': 17, 'mass': 126.90,   'vdw_radius': 198, 'color': (148, 0, 148),   'epsilon': 1.8},
    'Xe': {'name': 'Ксенон',    'period': 5, 'group': 18, 'mass': 131.29,   'vdw_radius': 216, 'color': (66, 158, 176),  'epsilon': 0.6},
    'Cs': {'name': 'Цезий',  'period': 6, 'group': 1,  'mass': 132.91,   'vdw_radius': 343, 'color': (87, 23, 143),   'epsilon': 0.7},
    'Ba': {'name': 'Барий',   'period': 6, 'group': 2,  'mass': 137.33,   'vdw_radius': 268, 'color': (0, 201, 0),     'epsilon': 0.8},
    'La': {'name': 'Лантан','period': 6, 'group': 3,  'mass': 138.91,   'vdw_radius': 243, 'color': (112, 212, 255), 'epsilon': 1.1},
    'Ce': {'name': 'Церий',   'period': 6, 'group': 19, 'mass': 140.12,   'vdw_radius': 242, 'color': (255, 255, 199), 'epsilon': 1.2},
    'Pr': {'name': 'Празеодим','period': 6, 'group': 19, 'mass': 140.91,   'vdw_radius': 240, 'color': (217, 255, 199), 'epsilon': 1.3},
    'Nd': {'name': 'Неодим','period': 6, 'group': 19, 'mass': 144.24,   'vdw_radius': 239, 'color': (199, 255, 199), 'epsilon': 1.4},
    'Pm': {'name': 'Прометий','period': 6, 'group': 19, 'mass': 145,      'vdw_radius': 238, 'color': (163, 255, 199), 'epsilon': 1.5},
    'Sm': {'name': 'Самарий', 'period': 6, 'group': 19, 'mass': 150.36,   'vdw_radius': 236, 'color': (143, 255, 199), 'epsilon': 1.6},
    'Eu': {'name': 'Европий', 'period': 6, 'group': 19, 'mass': 151.96,   'vdw_radius': 235, 'color': (97, 255, 199),  'epsilon': 1.7},
    'Gd': {'name': 'Гадолиний','period': 6, 'group': 19, 'mass': 157.25,   'vdw_radius': 234, 'color': (69, 255, 199),  'epsilon': 1.8},
    'Tb': {'name': 'Тербий',  'period': 6, 'group': 19, 'mass': 158.93,   'vdw_radius': 233, 'color': (48, 255, 199),  'epsilon': 1.9},
    'Dy': {'name': 'Диспрозий','period': 6, 'group': 19, 'mass': 162.50,   'vdw_radius': 231, 'color': (31, 255, 199),  'epsilon': 2.0},
    'Ho': {'name': 'Гольмий',  'period': 6, 'group': 19, 'mass': 164.93,   'vdw_radius': 230, 'color': (0, 255, 156),   'epsilon': 2.1},
    'Er': {'name': 'Эрбий',   'period': 6, 'group': 19, 'mass': 167.26,   'vdw_radius': 229, 'color': (0, 230, 117),   'epsilon': 2.2},
    'Tm': {'name': 'Тулий',  'period': 6, 'group': 19, 'mass': 168.93,   'vdw_radius': 227, 'color': (0, 212, 82),    'epsilon': 2.3},
    'Yb': {'name': 'Иттербий','period': 6, 'group': 19, 'mass': 173.05,   'vdw_radius': 226, 'color': (0, 191, 56),    'epsilon': 2.4},
    'Lu': {'name': 'Лютеций', 'period': 6, 'group': 19, 'mass': 174.97,   'vdw_radius': 224, 'color': (0, 171, 36),    'epsilon': 2.5},
    'Hf': {'name': 'Гафний',  'period': 6, 'group': 4,  'mass': 178.49,   'vdw_radius': 212, 'color': (77, 194, 255),  'epsilon': 1.5},
    'Ta': {'name': 'Тантал', 'period': 6, 'group': 5,  'mass': 180.95,   'vdw_radius': 207, 'color': (77, 166, 255),  'epsilon': 1.6},
    'W':  {'name': 'Вольфрам', 'period': 6, 'group': 6,  'mass': 183.84,   'vdw_radius': 207, 'color': (33, 148, 214),  'epsilon': 1.7},
    'Re': {'name': 'Рений',  'period': 6, 'group': 7,  'mass': 186.21,   'vdw_radius': 207, 'color': (38, 125, 171),  'epsilon': 1.8},
    'Os': {'name': 'Осмий',   'period': 6, 'group': 8,  'mass': 190.23,   'vdw_radius': 207, 'color': (38, 102, 150),  'epsilon': 1.9},
    'Ir': {'name': 'Иридий',  'period': 6, 'group': 9,  'mass': 192.22,   'vdw_radius': 207, 'color': (23, 84, 135),   'epsilon': 2.0},
    'Pt': {'name': 'Платина', 'period': 6, 'group': 10, 'mass': 195.08,   'vdw_radius': 175, 'color': (208, 208, 224), 'epsilon': 2.1},
    'Au': {'name': 'Золото',     'period': 6, 'group': 11, 'mass': 196.97,   'vdw_radius': 166, 'color': (255, 209, 35),  'epsilon': 2.2},
    'Hg': {'name': 'Ртуть',  'period': 6, 'group': 12, 'mass': 200.59,   'vdw_radius': 155, 'color': (184, 184, 208), 'epsilon': 2.3},
    'Tl': {'name': 'Таллий', 'period': 6, 'group': 13, 'mass': 204.38,   'vdw_radius': 196, 'color': (166, 84, 77),   'epsilon': 1.3},
    'Pb': {'name': 'Свинец',     'period': 6, 'group': 14, 'mass': 207.2,    'vdw_radius': 202, 'color': (87, 89, 97),    'epsilon': 1.4},
    'Bi': {'name': 'Висмут',  'period': 6, 'group': 15, 'mass': 208.98,   'vdw_radius': 207, 'color': (158, 79, 181),  'epsilon': 1.5},
    'Po': {'name': 'Полоний', 'period': 6, 'group': 16, 'mass': 209,      'vdw_radius': 197, 'color': (171, 92, 0),    'epsilon': 1.6},
    'At': {'name': 'Астат', 'period': 6, 'group': 17, 'mass': 210,      'vdw_radius': 202, 'color': (117, 79, 69),   'epsilon': 1.7},
    'Rn': {'name': 'Радон',    'period': 6, 'group': 18, 'mass': 222,      'vdw_radius': 220, 'color': (66, 130, 150),  'epsilon': 0.7},
    'Fr': {'name': 'Франций', 'period': 7, 'group': 1,  'mass': 223,      'vdw_radius': 348, 'color': (66, 0, 102),    'epsilon': 0.6},
    'Ra': {'name': 'Радий',   'period': 7, 'group': 2,  'mass': 226,      'vdw_radius': 283, 'color': (0, 125, 0),     'epsilon': 0.7},
    'Ac': {'name': 'Актиний', 'period': 7, 'group': 3,  'mass': 227,      'vdw_radius': 247, 'color': (112, 171, 250), 'epsilon': 1.0},
    'Th': {'name': 'Торий',  'period': 7, 'group': 19, 'mass': 232.04,   'vdw_radius': 245, 'color': (0, 186, 255),   'epsilon': 1.1},
    'Pa': {'name': 'Протактиний','period': 7, 'group': 19, 'mass': 231.04,   'vdw_radius': 243, 'color': (0, 161, 255),   'epsilon': 1.2},
    'U':  {'name': 'Уран',  'period': 7, 'group': 19, 'mass': 238.03,   'vdw_radius': 241, 'color': (0, 143, 255),   'epsilon': 1.3},
    'Np': {'name': 'Нептуний','period': 7, 'group': 19, 'mass': 237,      'vdw_radius': 239, 'color': (0, 128, 255),   'epsilon': 1.4},
    'Pu': {'name': 'Плутоний','period': 7, 'group': 19, 'mass': 244,      'vdw_radius': 237, 'color': (0, 107, 255),   'epsilon': 1.5},
    'Am': {'name': 'Америций','period': 7, 'group': 19, 'mass': 243,      'vdw_radius': 235, 'color': (84, 92, 242),   'epsilon': 1.6},
    'Cm': {'name': 'Кюрий',   'period': 7, 'group': 19, 'mass': 247,      'vdw_radius': 233, 'color': (120, 92, 227),  'epsilon': 1.7},
    'Bk': {'name': 'Берклий','period': 7, 'group': 19, 'mass': 247,      'vdw_radius': 231, 'color': (138, 79, 227),  'epsilon': 1.8},
    'Cf': {'name': 'Калифорний','period': 7, 'group': 19, 'mass': 251,      'vdw_radius': 229, 'color': (161, 54, 212),  'epsilon': 1.9},
    'Es': {'name': 'Эйнштейний','period': 7, 'group': 19, 'mass': 252,      'vdw_radius': 227, 'color': (179, 31, 212),  'epsilon': 2.0},
    'Fm': {'name': 'Фермий',  'period': 7, 'group': 19, 'mass': 257,      'vdw_radius': 225, 'color': (179, 31, 186),  'epsilon': 2.1},
    'Md': {'name': 'Менделевий','period': 7, 'group': 19, 'mass': 258,      'vdw_radius': 223, 'color': (179, 13, 166),  'epsilon': 2.2},
    'No': {'name': 'Нобелий', 'period': 7, 'group': 19, 'mass': 259,      'vdw_radius': 221, 'color': (189, 13, 135),  'epsilon': 2.3},
    'Lr': {'name': 'Лоуренсий','period': 7, 'group': 19, 'mass': 262,      'vdw_radius': 219, 'color': (199, 0, 102),   'epsilon': 2.4},
    'Rf': {'name': 'Резерфордий','period': 7, 'group': 4, 'mass': 267,      'vdw_radius': 200, 'color': (204, 0, 89),    'epsilon': 1.5},
    'Db': {'name': 'Дубний',  'period': 7, 'group': 5,  'mass': 268,      'vdw_radius': 200, 'color': (209, 0, 79),    'epsilon': 1.6},
    'Sg': {'name': 'Сиборгий','period': 7, 'group': 6,  'mass': 269,      'vdw_radius': 200, 'color': (214, 0, 69),    'epsilon': 1.7},
    'Bh': {'name': 'Борий',  'period': 7, 'group': 7,  'mass': 270,      'vdw_radius': 200, 'color': (219, 0, 59),    'epsilon': 1.8},
    'Hs': {'name': 'Хассий',  'period': 7, 'group': 8,  'mass': 269,      'vdw_radius': 200, 'color': (224, 0, 49),    'epsilon': 1.9},
    'Mt': {'name': 'Мейтнерий','period': 7, 'group': 9,  'mass': 278,      'vdw_radius': 200, 'color': (229, 0, 39),    'epsilon': 2.0},
    'Ds': {'name': 'Дармштадтий','period': 7, 'group': 10, 'mass': 281,      'vdw_radius': 200, 'color': (234, 0, 29),    'epsilon': 2.1},
    'Rg': {'name': 'Рентгений','period': 7, 'group': 11, 'mass': 282,      'vdw_radius': 200, 'color': (239, 0, 19),    'epsilon': 2.2},
    'Cn': {'name': 'Коперниций','period': 7, 'group': 12, 'mass': 285,      'vdw_radius': 200, 'color': (244, 0, 9),     'epsilon': 2.3},
    'Nh': {'name': 'Нихоний', 'period': 7, 'group': 13, 'mass': 286,      'vdw_radius': 200, 'color': (249, 0, 0),     'epsilon': 1.4},
    'Fl': {'name': 'Флеровий','period': 7, 'group': 14, 'mass': 289,      'vdw_radius': 200, 'color': (229, 229, 229), 'epsilon': 1.5},
    'Mc': {'name': 'Московий','period': 7, 'group': 15, 'mass': 290,      'vdw_radius': 200, 'color': (204, 204, 204), 'epsilon': 1.6},
    'Lv': {'name': 'Ливерморий','period': 7, 'group': 16, 'mass': 293,      'vdw_radius': 200, 'color': (179, 179, 179), 'epsilon': 1.7},
    'Ts': {'name': 'Теннессин','period': 7, 'group': 17, 'mass': 294,      'vdw_radius': 200, 'color': (153, 153, 153), 'epsilon': 1.8},
    'Og': {'name': 'Оганесон','period': 7, 'group': 18, 'mass': 294,      'vdw_radius': 200, 'color': (128, 128, 128), 'epsilon': 0.8},
}
ELEMENT_SYMBOLS = list(ELEMENT_DATA.keys())

BOND_LENGTHS = {
    ('H', 'H'): 7.4, ('H', 'O'): 9.6, ('H', 'N'): 10.1, ('H', 'C'): 10.9,
    ('C', 'C'): 15.4, ('C', 'O'): 14.3, ('C', 'N'): 14.7, ('O', 'O'): 14.8,
    ('N', 'N'): 14.5, ('O', 'N'): 14.0,
}
def get_bond_length(el1: str, el2: str) -> float:
    key = tuple(sorted([el1, el2]))
    return BOND_LENGTHS.get(key, 14.0)

PREFERRED_ANGLES = {
    ('H', 'O', 'H'): 104.5 * np.pi / 180,
    'default': 109.5 * np.pi / 180,
}

# ========== ГЕНЕРАТОР ТЕКСТУРЫ СФЕРЫ ==========
def create_sphere_surface(radius: int, base_color: Tuple[int, int, int]) -> pygame.Surface:
    size = radius * 2 + 4
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    center = (size // 2, size // 2)
    for y in range(size):
        for x in range(size):
            dx = x - center[0]
            dy = y - center[1]
            dist = np.hypot(dx, dy)
            if dist <= radius:
                t = dist / radius
                light_dir = np.array([-0.5, -0.7, 0.5])
                light_dir /= np.linalg.norm(light_dir)
                nx = dx / radius
                ny = dy / radius
                nz = np.sqrt(max(0, 1 - (nx*nx + ny*ny)))
                normal = np.array([nx, ny, nz])
                diffuse = max(0, np.dot(normal, light_dir))
                view_dir = np.array([0, 0, 1])
                half = (light_dir + view_dir) / np.linalg.norm(light_dir + view_dir)
                spec = max(0, np.dot(normal, half)) ** 16 * 0.8
                ambient = 0.25
                intensity = ambient + diffuse * 0.8 + spec
                intensity = np.clip(intensity, 0.3, 1.0)
                r = int(base_color[0] * intensity)
                g = int(base_color[1] * intensity)
                b = int(base_color[2] * intensity)
                alpha = 255 if dist < radius - 1 else int(255 * (radius - dist))
                surf.set_at((x, y), (r, g, b, alpha))
    return surf

# ========== КЛАСС СВЯЗИ ==========
class Bond:
    def __init__(self, a1: 'Atom', a2: 'Atom', secondary: 'Atom' = None):
        self.a1 = a1
        self.a2 = a2
        self.r0 = get_bond_length(a1.element, a2.element)
        self.k = BOND_STIFFNESS
        self.secondary = secondary if secondary else a2
        self.max_dist = self.r0 + self.secondary.radius
        self.id = (min(id(a1), id(a2)), max(id(a1), id(a2)))

    def compute_force(self):
        r_vec = self.a1.pos - self.a2.pos
        r = np.linalg.norm(r_vec)
        if r < 1e-6:
            return
        force_mag = -self.k * (r - self.r0)
        v_rel = self.a1.vel - self.a2.vel
        damping_force = -BOND_DAMPING * np.dot(v_rel, r_vec) / r if r > 0 else 0.0
        total_force = force_mag + damping_force
        if r > self.max_dist:
            extra_force = -self.k * MAX_BOND_FORCE_FACTOR * (r - self.max_dist)
            total_force += extra_force
        force = total_force * r_vec / r
        self.a1.force += force
        self.a2.force -= force

    def draw(self, screen, offset_y=0):
        start = self.a1.pos.astype(int)
        end = self.a2.pos.astype(int)
        r = np.linalg.norm(self.a1.pos - self.a2.pos)
        t = min(1.0, max(0.0, (r - self.r0) / (self.max_dist - self.r0))) if self.max_dist > self.r0 else 0.0
        color = (int(255 * t), int(255 * (1 - t)), 0)
        pygame.draw.line(screen, color, start, end, 3)

# ========== КЛАСС АТОМА ==========
class Atom:
    def __init__(self, element: str, x: float, y: float, vx: float = 0.0, vy: float = 0.0):
        self.element = element
        self.data = ELEMENT_DATA[element]
        self.mass = self.data['mass']
        self.radius = max(6, int(self.data['vdw_radius'] / 12.0))
        self.base_color = self.data['color']
        self.epsilon = self.data['epsilon']
        self.pos = np.array([x, y], dtype=float)
        self.vel = np.array([vx, vy], dtype=float)
        self.force = np.zeros(2, dtype=float)
        self.sprite = create_sphere_surface(self.radius, self.base_color)
        self.bonds: Set[Bond] = set()

    def kinetic_energy(self) -> float:
        return 0.5 * self.mass * np.dot(self.vel, self.vel)

    def add_energy(self, delta: float):
        if delta == 0: return
        ke = self.kinetic_energy()
        new_ke = max(ke + delta, 0.0)
        if ke > 0:
            self.vel *= np.sqrt(new_ke / ke)
        else:
            angle = random.uniform(0, 2 * np.pi)
            speed = np.sqrt(2 * new_ke / self.mass)
            self.vel = np.array([speed * np.cos(angle), speed * np.sin(angle)])

    def draw(self, screen, offset_y=0):
        shadow_rect = pygame.Rect(0, 0, int(self.radius * 1.6), int(self.radius * 0.6))
        shadow_rect.center = (int(self.pos[0]), int(self.pos[1] + self.radius * 0.7 + offset_y))
        shadow_surf = pygame.Surface(shadow_rect.size, pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 80), shadow_surf.get_rect())
        screen.blit(shadow_surf, shadow_rect)
        rect = self.sprite.get_rect(center=(int(self.pos[0]), int(self.pos[1] + offset_y)))
        screen.blit(self.sprite, rect)

# ========== КЛАСС СКРОЛЛИРУЕМОГО МЕНЮ С ПОДСКАЗКАМИ ==========
class ScrollableElementMenu:
    def __init__(self, rect: pygame.Rect, elements: List[str], initial_element: str = 'H',
                 callback: Callable[[str], None] = None):
        self.rect = rect
        self.elements = elements
        self.selected = initial_element
        self.callback = callback
        self.font = pygame.font.SysFont("Arial", 16)
        self.small_font = pygame.font.SysFont("Arial", 12)
        self.tooltip_font = pygame.font.SysFont("Arial", 14)
        
        self.item_width = 60
        self.item_spacing = 5
        self.scroll_x = 0
        self.max_scroll = max(0, len(elements) * (self.item_width + self.item_spacing) - rect.width + self.item_spacing)
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_scroll = 0
        
        self.hovered_element = None
        self.hover_start_time = 0
        self.tooltip_delay = 0.5

    def get_item_rect(self, index: int) -> pygame.Rect:
        x = self.rect.left + index * (self.item_width + self.item_spacing) - self.scroll_x
        return pygame.Rect(x, self.rect.top + 5, self.item_width, self.rect.height - 10)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(event.pos):
                    for i, elem in enumerate(self.elements):
                        item_rect = self.get_item_rect(i)
                        if item_rect.collidepoint(event.pos):
                            self.selected = elem
                            if self.callback:
                                self.callback(elem)
                            return
                    self.dragging = True
                    self.drag_start_x = event.pos[0]
                    self.drag_start_scroll = self.scroll_x
            elif event.button == 4:
                self.scroll_x = max(0, self.scroll_x - 30)
            elif event.button == 5:
                self.scroll_x = min(self.max_scroll, self.scroll_x + 30)
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
            
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                dx = event.pos[0] - self.drag_start_x
                self.scroll_x = max(0, min(self.max_scroll, self.drag_start_scroll - dx))
            else:
                if self.rect.collidepoint(event.pos):
                    new_hover = None
                    for i, elem in enumerate(self.elements):
                        item_rect = self.get_item_rect(i)
                        if item_rect.collidepoint(event.pos):
                            new_hover = elem
                            break
                    if new_hover != self.hovered_element:
                        self.hovered_element = new_hover
                        self.hover_start_time = pygame.time.get_ticks() / 1000.0
                else:
                    self.hovered_element = None

    def draw(self, screen):
        pygame.draw.rect(screen, (50, 60, 70), self.rect)
        pygame.draw.rect(screen, (100, 100, 100), self.rect, 2)
        
        clip_surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        clip_surf.fill((0, 0, 0, 0))
        
        mouse_pos = pygame.mouse.get_pos()
        current_hover = None
        
        for i, elem in enumerate(self.elements):
            item_rect = self.get_item_rect(i)
            if item_rect.right < self.rect.left or item_rect.left > self.rect.right:
                continue
            
            if item_rect.collidepoint(mouse_pos):
                current_hover = elem
                color = (100, 130, 160)
                border_color = (180, 200, 255)
            elif elem == self.selected:
                color = (100, 200, 100)
                border_color = (150, 255, 150)
            else:
                color = (70, 90, 110)
                border_color = (120, 120, 140)
            
            local_rect = pygame.Rect(item_rect.left - self.rect.left, item_rect.top - self.rect.top,
                                     item_rect.width, item_rect.height)
            pygame.draw.rect(clip_surf, color, local_rect, border_radius=6)
            pygame.draw.rect(clip_surf, border_color, local_rect, 2, border_radius=6)
            
            text = self.font.render(elem, True, (255, 255, 255))
            text_rect = text.get_rect(center=local_rect.center)
            clip_surf.blit(text, text_rect)
            
            name = ELEMENT_DATA[elem]['name']
            if len(name) > 10:
                name = name[:8] + ".."
            name_text = self.small_font.render(name, True, (200, 200, 200))
            name_rect = name_text.get_rect(center=(local_rect.centerx, local_rect.bottom - 8))
            clip_surf.blit(name_text, name_rect)
        
        screen.blit(clip_surf, self.rect)
        
        if current_hover is not None:
            now = pygame.time.get_ticks() / 1000.0
            if current_hover == self.hovered_element:
                if now - self.hover_start_time >= self.tooltip_delay:
                    self.draw_tooltip(screen, current_hover, mouse_pos)
            else:
                self.hovered_element = current_hover
                self.hover_start_time = now

    def draw_tooltip(self, screen, element: str, mouse_pos: Tuple[int, int]):
        data = ELEMENT_DATA[element]
        lines = [
            f"{data['name']} ({element})",
            f"Масса: {data['mass']:.2f} а.е.м.",
            f"Радиус Ван-дер-Ваальса: {data['vdw_radius']} пм",
            f"Период: {data['period']}, Группа: {data['group']}"
        ]
        
        max_width = 0
        total_height = 0
        rendered_lines = []
        for line in lines:
            surf = self.tooltip_font.render(line, True, (255, 255, 255))
            rendered_lines.append(surf)
            max_width = max(max_width, surf.get_width())
            total_height += surf.get_height() + 2
        
        padding = 8
        tooltip_width = max_width + 2 * padding
        tooltip_height = total_height + 2 * padding
        
        tooltip_x = mouse_pos[0] + 15
        tooltip_y = mouse_pos[1] - tooltip_height - 15
        
        if tooltip_x + tooltip_width > screen.get_width():
            tooltip_x = mouse_pos[0] - tooltip_width - 15
        if tooltip_x < 0:
            tooltip_x = 5
        
        if tooltip_y < 0:
            tooltip_y = mouse_pos[1] + 15
        
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        
        pygame.draw.rect(screen, (40, 45, 55), tooltip_rect, border_radius=6)
        pygame.draw.rect(screen, (120, 120, 140), tooltip_rect, 2, border_radius=6)
        
        y = tooltip_rect.y + padding
        for surf in rendered_lines:
            screen.blit(surf, (tooltip_rect.x + padding, y))
            y += surf.get_height() + 2

# ========== КЛАСС КНОПКИ ==========
class Button:
    def __init__(self, rect: pygame.Rect, text: str, color: Tuple[int, int, int],
                 hover_color: Tuple[int, int, int], text_color: Tuple[int, int, int] = (255, 255, 255),
                 font_size: int = 16, callback=None):
        self.rect = rect
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = pygame.font.SysFont("Arial", font_size)
        self.callback = callback
        self.hovered = False
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.callback:
                self.callback()

    def draw(self, screen):
        if self.active:
            color = (100, 200, 100)
        else:
            color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (100, 100, 100), self.rect, 2, border_radius=8)
        
        text_surf = self.font.render(self.text, True, self.text_color)
        if text_surf.get_width() > self.rect.width - 10:
            font_size = self.font.get_height()
            while font_size > 10 and text_surf.get_width() > self.rect.width - 10:
                font_size -= 1
                smaller_font = pygame.font.SysFont("Arial", font_size)
                text_surf = smaller_font.render(self.text, True, self.text_color)
        
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

# ========== КЛАСС ТЕКСТОВОГО ПОЛЯ ==========
class TextBox:
    def __init__(self, rect: pygame.Rect, text: str = "", font_size: int = 18,
                 active_color: Tuple[int, int, int] = (255, 255, 255),
                 inactive_color: Tuple[int, int, int] = (200, 200, 200),
                 bg_color: Tuple[int, int, int] = (60, 60, 80),
                 callback: Callable[[float], None] = None):
        self.rect = rect
        self.text = text
        self.font = pygame.font.SysFont("Arial", font_size)
        self.active_color = active_color
        self.inactive_color = inactive_color
        self.bg_color = bg_color
        self.callback = callback
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self._apply_value()
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isdigit() or event.unicode == '.':
                new_text = self.text + event.unicode
                if new_text.count('.') <= 1 and len(new_text) <= 8:
                    self.text = new_text

    def update(self):
        if self.active:
            self.cursor_timer += 1
            if self.cursor_timer >= 30:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
        else:
            self.cursor_visible = False

    def _apply_value(self):
        try:
            val = float(self.text) if self.text else 0.0
            val = max(0.1, min(5.0, val))
            self.text = f"{val:.1f}"
            if self.callback:
                self.callback(val)
        except ValueError:
            self.text = "1.0"
            if self.callback:
                self.callback(1.0)

    def set_value(self, value: float):
        self.text = f"{value:.1f}"

    def draw(self, screen):
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=4)
        border_color = self.active_color if self.active else self.inactive_color
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=4)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(midleft=(self.rect.left + 5, self.rect.centery))
        screen.blit(text_surf, text_rect)
        if self.active and self.cursor_visible:
            cursor_x = text_rect.right + 2
            pygame.draw.line(screen, (255, 255, 255),
                             (cursor_x, self.rect.top + 5),
                             (cursor_x, self.rect.bottom - 5), 2)

# ========== КЛАСС СЛАЙДЕРА ==========
class Slider:
    def __init__(self, rect: pygame.Rect, min_val: float, max_val: float, initial: float,
                 color: Tuple[int, int, int] = (100, 100, 100),
                 handle_color: Tuple[int, int, int] = (200, 200, 200),
                 callback: Callable[[float], None] = None):
        self.rect = rect
        self.min = min_val
        self.max = max_val
        self.value = initial
        self.color = color
        self.handle_color = handle_color
        self.callback = callback
        self.dragging = False
        self.handle_radius = 8

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            handle_x = self.rect.left + (self.value - self.min) / (self.max - self.min) * self.rect.width
            handle_center = (int(handle_x), self.rect.centery)
            if np.hypot(event.pos[0] - handle_center[0], event.pos[1] - handle_center[1]) <= self.handle_radius:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = max(0, min(event.pos[0] - self.rect.left, self.rect.width))
            self.value = self.min + rel_x / self.rect.width * (self.max - self.min)
            if self.callback:
                self.callback(self.value)

    def set_value(self, value: float):
        self.value = value

    def draw(self, screen, font):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=4)
        handle_x = self.rect.left + (self.value - self.min) / (self.max - self.min) * self.rect.width
        handle_center = (int(handle_x), self.rect.centery)
        pygame.draw.circle(screen, self.handle_color, handle_center, self.handle_radius)
        pygame.draw.circle(screen, (0, 0, 0), handle_center, self.handle_radius, 2)
        text = font.render(f"{self.value:.2f}", True, (255, 255, 255))
        text_rect = text.get_rect(midleft=(self.rect.right + 10, self.rect.centery))
        screen.blit(text, text_rect)

# ========== ГЛАВНЫЙ КЛАСС СИМУЛЯЦИИ ==========
class Simulation:
    def __init__(self):
        self.atoms: List[Atom] = []
        self.bonds: List[Bond] = []
        self.paused = False
        self.selected_atom: Optional[Atom] = None
        self.dragging = False
        self.drag_offset = np.zeros(2)
        self.time_scale = 1.0
        self.current_element = 'H'
        self.energy_delta = 1.0
        self.add_mode = False
        self.remove_mode = False
        self.bond_mode = False
        self.bond_first_atom: Optional[Atom] = None
        self.auto_heat = False
        self.auto_cool = False
        self.heat_cool_rate = 0.5
        self.repeat_timer = 0
        self.repeat_action = None
        self.last_mouse_pos = (0, 0)

    def add_atom(self, x: float, y: float, sim_rect: pygame.Rect):
        new_radius = max(6, int(ELEMENT_DATA[self.current_element]['vdw_radius'] / 12.0))
        min_dist = new_radius * 2

        too_close = False
        for atom in self.atoms:
            dist = np.hypot(x - atom.pos[0], y - atom.pos[1])
            if dist < min_dist:
                too_close = True
                break

        if too_close:
            for angle in np.linspace(0, 2*np.pi, 16):
                for d in [min_dist, min_dist * 1.5, min_dist * 2]:
                    new_x = x + d * np.cos(angle)
                    new_y = y + d * np.sin(angle)
                    if not (sim_rect.left + new_radius <= new_x <= sim_rect.right - new_radius and
                            sim_rect.top + new_radius <= new_y <= sim_rect.bottom - new_radius):
                        continue
                    valid = True
                    for atom in self.atoms:
                        if np.hypot(new_x - atom.pos[0], new_y - atom.pos[1]) < min_dist:
                            valid = False
                            break
                    if valid:
                        self.atoms.append(Atom(self.current_element, new_x, new_y))
                        return
            self.atoms.append(Atom(self.current_element, x, y))
        else:
            self.atoms.append(Atom(self.current_element, x, y))

    def remove_atom_at(self, x: float, y: float, sim_rect: pygame.Rect):
        atom = self.find_atom_at((x, y), sim_rect)
        if atom:
            self.remove_atom(atom)

    def remove_atom(self, atom: Atom):
        if atom in self.atoms:
            bonds_to_remove = [b for b in self.bonds if b.a1 is atom or b.a2 is atom]
            for b in bonds_to_remove:
                self.bonds.remove(b)
                b.a1.bonds.discard(b)
                b.a2.bonds.discard(b)
            self.atoms.remove(atom)

    def clear(self):
        self.atoms.clear()
        self.bonds.clear()

    def add_bond(self, a1: Atom, a2: Atom, teleport: bool = True):
        if a1 is a2: return
        for b in self.bonds:
            if (b.a1 is a1 and b.a2 is a2) or (b.a1 is a2 and b.a2 is a1):
                return

        secondary = a2
        secondary.vel = np.zeros(2)

        if teleport and len(a1.bonds) > 0:
            bonded_atoms = []
            for bond in a1.bonds:
                other = bond.a1 if bond.a2 is a1 else bond.a2
                bonded_atoms.append(other)

            angle_key = None
            if len(bonded_atoms) == 1:
                if (a1.element == 'O' and a2.element == 'H' and bonded_atoms[0].element == 'H') or \
                   (a1.element == 'O' and a2.element == 'H' and bonded_atoms[0].element == 'H'):
                    angle_key = ('H', 'O', 'H')
            pref_angle = PREFERRED_ANGLES.get(angle_key, PREFERRED_ANGLES['default'])

            if len(bonded_atoms) == 1:
                b0 = bonded_atoms[0]
                vec_ref = b0.pos - a1.pos
                dist_ref = np.linalg.norm(vec_ref)
                if dist_ref > 1e-6:
                    vec_ref /= dist_ref
                    cos_a = np.cos(pref_angle)
                    sin_a = np.sin(pref_angle)
                    candidates = []
                    for sign in [1, -1]:
                        rot_vec = np.array([
                            vec_ref[0] * cos_a - sign * vec_ref[1] * sin_a,
                            vec_ref[0] * sin_a + sign * vec_ref[1] * cos_a
                        ])
                        new_pos = a1.pos + rot_vec * get_bond_length(a1.element, a2.element)
                        candidates.append(new_pos)
                    best_pos = candidates[0]
                    best_min_dist = 0
                    for cand in candidates:
                        min_dist = float('inf')
                        for other in self.atoms:
                            if other is a1 or other is a2: continue
                            d = np.linalg.norm(cand - other.pos)
                            if d < min_dist:
                                min_dist = d
                        if min_dist > best_min_dist:
                            best_min_dist = min_dist
                            best_pos = cand
                    a2.pos = best_pos
                else:
                    dir_vec = a2.pos - a1.pos
                    dist = np.linalg.norm(dir_vec)
                    if dist > 1e-6:
                        new_pos = a1.pos + (dir_vec / dist) * get_bond_length(a1.element, a2.element)
                        a2.pos = new_pos
            else:
                dir_vec = a2.pos - a1.pos
                dist = np.linalg.norm(dir_vec)
                if dist > 1e-6:
                    new_pos = a1.pos + (dir_vec / dist) * get_bond_length(a1.element, a2.element)
                    a2.pos = new_pos
        else:
            dir_vec = a2.pos - a1.pos
            dist = np.linalg.norm(dir_vec)
            if dist > 1e-6:
                new_pos = a1.pos + (dir_vec / dist) * get_bond_length(a1.element, a2.element)
                a2.pos = new_pos

        bond = Bond(a1, a2, secondary=secondary)
        self.bonds.append(bond)
        a1.bonds.add(bond)
        a2.bonds.add(bond)

    def clear_bonds(self):
        self.bonds.clear()
        for atom in self.atoms:
            atom.bonds.clear()

    def stabilize(self):
        for atom in self.atoms:
            atom.vel = np.zeros(2)

    def get_connected_component(self, start_atom: Atom) -> List[Atom]:
        visited = set()
        stack = [start_atom]
        while stack:
            atom = stack.pop()
            if atom in visited: continue
            visited.add(atom)
            for bond in atom.bonds:
                other = bond.a1 if bond.a2 is atom else bond.a2
                if other not in visited:
                    stack.append(other)
        return list(visited)

    def compute_forces(self, sim_rect: pygame.Rect):
        for a in self.atoms:
            a.force = np.zeros(2)

        n = len(self.atoms)
        for i in range(n):
            for j in range(i + 1, n):
                a1 = self.atoms[i]
                a2 = self.atoms[j]
                if any(b.a1 is a1 and b.a2 is a2 or b.a1 is a2 and b.a2 is a1 for b in a1.bonds):
                    continue

                r_vec = a1.pos - a2.pos
                r = np.linalg.norm(r_vec)
                sigma = (a1.radius + a2.radius) * 0.85
                epsilon = np.sqrt(a1.epsilon * a2.epsilon) * 2.0
                cutoff = 2.5 * sigma
                if r > cutoff or r < 1e-6: continue
                sr = sigma / r
                sr6 = sr ** 6
                sr12 = sr6 ** 2
                force_mag = 24.0 * epsilon * (2.0 * sr12 - sr6) / r
                force = force_mag * r_vec / r
                a1.force += force
                a2.force -= force

        for bond in self.bonds:
            bond.compute_force()

        for atom in self.atoms:
            left = sim_rect.left + atom.radius
            right = sim_rect.right - atom.radius
            top = sim_rect.top + atom.radius
            bottom = sim_rect.bottom - atom.radius
            dx = atom.pos[0] - left
            if dx < WALL_THRESHOLD:
                atom.force[0] += WALL_STIFFNESS * (WALL_THRESHOLD - dx)
            dx = right - atom.pos[0]
            if dx < WALL_THRESHOLD:
                atom.force[0] -= WALL_STIFFNESS * (WALL_THRESHOLD - dx)
            dy = atom.pos[1] - top
            if dy < WALL_THRESHOLD:
                atom.force[1] += WALL_STIFFNESS * (WALL_THRESHOLD - dy)
            dy = bottom - atom.pos[1]
            if dy < WALL_THRESHOLD:
                atom.force[1] -= WALL_STIFFNESS * (WALL_THRESHOLD - dy)

    def update(self, dt: float, sim_rect: pygame.Rect):
        if self.paused: return
        effective_dt = dt * self.time_scale

        if self.auto_heat and not self.auto_cool:
            for atom in self.atoms:
                atom.add_energy(self.heat_cool_rate * effective_dt)
        elif self.auto_cool and not self.auto_heat:
            for atom in self.atoms:
                atom.add_energy(-self.heat_cool_rate * effective_dt)

        self.compute_forces(sim_rect)
        for atom in self.atoms:
            atom.vel += atom.force / atom.mass * effective_dt
            atom.pos += atom.vel * effective_dt
            left = sim_rect.left + atom.radius
            right = sim_rect.right - atom.radius
            top = sim_rect.top + atom.radius
            bottom = sim_rect.bottom - atom.radius
            atom.pos[0] = np.clip(atom.pos[0], left, right)
            atom.pos[1] = np.clip(atom.pos[1], top, bottom)

    def change_energy(self, delta: float):
        for atom in self.atoms:
            atom.add_energy(delta)

    def crystallize(self, sim_rect: pygame.Rect):
        """Упорядочивает атомы в гексагональную кристаллическую решётку."""
        if len(self.atoms) == 0:
            return
        
        # Находим центр масс и границы всех атомов
        center = np.mean([atom.pos for atom in self.atoms], axis=0)
        min_x = min(atom.pos[0] for atom in self.atoms)
        max_x = max(atom.pos[0] for atom in self.atoms)
        min_y = min(atom.pos[1] for atom in self.atoms)
        max_y = max(atom.pos[1] for atom in self.atoms)
        width = max_x - min_x
        height = max_y - min_y
        
        # Параметры гексагональной решётки
        spacing = CRYSTAL_LATTICE_SPACING
        a = spacing
        rows = int(height / (a * 0.866)) + 3
        cols = int(width / a) + 3
        
        # Генерируем узлы решётки
        lattice_points = []
        for i in range(rows):
            y = min_y - a*0.866 + i * a * 0.866
            offset = (a/2) if (i % 2 == 1) else 0
            for j in range(cols):
                x = min_x - a + j * a + offset
                lattice_points.append(np.array([x, y]))
        
        # Для каждого атома находим ближайший свободный узел
        atoms_to_place = self.atoms.copy()
        available_points = lattice_points.copy()
        for atom in atoms_to_place:
            if not available_points:
                break
            dists = [np.linalg.norm(atom.pos - p) for p in available_points]
            idx = np.argmin(dists)
            atom.pos = available_points[idx].copy()
            available_points.pop(idx)
        
        # Обнуляем скорости
        for atom in self.atoms:
            atom.vel = np.zeros(2)
        
        # Корректируем позиции, чтобы не выходили за границы
        for atom in self.atoms:
            left = sim_rect.left + atom.radius
            right = sim_rect.right - atom.radius
            top = sim_rect.top + atom.radius
            bottom = sim_rect.bottom - atom.radius
            atom.pos[0] = np.clip(atom.pos[0], left, right)
            atom.pos[1] = np.clip(atom.pos[1], top, bottom)

    def draw(self, screen, font, sim_rect: pygame.Rect):
        pygame.draw.rect(screen, BORDER_COLOR, sim_rect.inflate(4, 4), 4, border_radius=8)
        pygame.draw.rect(screen, BACKGROUND_COLOR, sim_rect)

        for bond in self.bonds:
            bond.draw(screen)
        for atom in self.atoms:
            atom.draw(screen)

        total_ke = sum(a.kinetic_energy() for a in self.atoms)
        total_pe = 0.0
        n = len(self.atoms)
        for i in range(n):
            for j in range(i + 1, n):
                a1 = self.atoms[i]
                a2 = self.atoms[j]
                if any(b.a1 is a1 and b.a2 is a2 or b.a1 is a2 and b.a2 is a1 for b in a1.bonds):
                    continue
                r = np.linalg.norm(a1.pos - a2.pos)
                sigma = (a1.radius + a2.radius) * 0.85
                epsilon = np.sqrt(a1.epsilon * a2.epsilon) * 2.0
                cutoff = 2.5 * sigma
                if r < cutoff and r > 1e-6:
                    sr = sigma / r
                    sr6 = sr ** 6
                    sr12 = sr6 ** 2
                    total_pe += 4.0 * epsilon * (sr12 - sr6)
        for bond in self.bonds:
            r = np.linalg.norm(bond.a1.pos - bond.a2.pos)
            total_pe += 0.5 * bond.k * (r - bond.r0) ** 2
        total_e = total_ke + total_pe

        energy_text = [
            f"Кинет.: {total_ke:.1f}",
            f"Потенц.: {total_pe:.1f}",
            f"Полная: {total_e:.1f}"
        ]
        y_pos = sim_rect.top - 5
        for i, line in enumerate(energy_text):
            surf = font.render(line, True, (220, 220, 220))
            x_pos = sim_rect.right - surf.get_width() - 10
            screen.blit(surf, (x_pos, y_pos - (len(energy_text)-1-i)*18))

        info_lines = [
            f"Атомы: {len(self.atoms)} | Связи: {len(self.bonds)}",
            f"Время: {self.time_scale:.2f}x | {'ПАУЗА' if self.paused else 'РАБОТА'}"
        ]
        y = sim_rect.bottom + 10
        for line in info_lines:
            surf = font.render(line, True, (220, 220, 220))
            screen.blit(surf, (sim_rect.left + 5, y))
            y += 18

    def find_atom_at(self, pos: Tuple[float, float], sim_rect: pygame.Rect) -> Optional[Atom]:
        x, y = pos
        if not sim_rect.collidepoint(pos): return None
        for atom in reversed(self.atoms):
            if np.hypot(atom.pos[0] - x, atom.pos[1] - y) <= atom.radius:
                return atom
        return None

# ========== СОЗДАНИЕ ИНТЕРФЕЙСА ==========
def create_ui_elements(width: int, height: int, sim: Simulation, callbacks: dict):
    element_menu_rect = pygame.Rect(10, 10, width - 20, ELEMENT_PANEL_HEIGHT)
    element_menu = ScrollableElementMenu(element_menu_rect, ELEMENT_SYMBOLS, 'H', callbacks['set_element'])

    button_y = ELEMENT_PANEL_HEIGHT + 20
    button_height = 38
    
    btn_widths = {
        'add': 85,
        'remove': 85,
        'bond': 75,
        'clear_bonds': 110,
        'clear_all': 110,
        'heat': 80,
        'cool': 90,
        'pause': 75,
        'auto_heat': 95,
        'auto_cool': 110,
        'stabilize': 110,
        'crystallize': 110,
        'exit': 70
    }
    
    spacing = 5
    start_x = 20
    
    btn_add = Button(pygame.Rect(start_x, button_y, btn_widths['add'], button_height), 
                     "+ Добавить", (60,80,120), (90,120,180), callback=callbacks['toggle_add'])
    btn_remove = Button(pygame.Rect(start_x + btn_widths['add'] + spacing, button_y, 
                      btn_widths['remove'], button_height), "- Удалить", (120,60,60), (180,90,90), 
                      callback=callbacks['toggle_remove'])
    btn_bond = Button(pygame.Rect(start_x + btn_widths['add'] + btn_widths['remove'] + spacing*2, button_y, 
                    btn_widths['bond'], button_height), "Связь", (128, 0, 128), (180, 60, 180), 
                    callback=callbacks['toggle_bond'])
    btn_clear_bonds = Button(pygame.Rect(start_x + btn_widths['add'] + btn_widths['remove'] + btn_widths['bond'] + spacing*3, button_y, 
                           btn_widths['clear_bonds'], button_height), "Очистить связи", (100,60,100), (140,90,140), 
                           callback=callbacks['clear_bonds'])
    btn_clear = Button(pygame.Rect(start_x + btn_widths['add'] + btn_widths['remove'] + btn_widths['bond'] + btn_widths['clear_bonds'] + spacing*4, button_y, 
                     btn_widths['clear_all'], button_height), "Очистить всё", (100,60,100), (140,90,140), 
                     callback=callbacks['clear_all'])
    btn_heat = Button(pygame.Rect(start_x + btn_widths['add'] + btn_widths['remove'] + btn_widths['bond'] + btn_widths['clear_bonds'] + btn_widths['clear_all'] + spacing*5, button_y, 
                    btn_widths['heat'], button_height), "Нагрев", (180,100,60), (220,140,80), 
                    callback=callbacks['heat'])
    btn_cool = Button(pygame.Rect(start_x + btn_widths['add'] + btn_widths['remove'] + btn_widths['bond'] + btn_widths['clear_bonds'] + btn_widths['clear_all'] + btn_widths['heat'] + spacing*6, button_y, 
                     btn_widths['cool'], button_height), "Охлаждение", (60,100,180), (80,140,220), 
                     callback=callbacks['cool'])
    btn_pause = Button(pygame.Rect(start_x + btn_widths['add'] + btn_widths['remove'] + btn_widths['bond'] + btn_widths['clear_bonds'] + btn_widths['clear_all'] + btn_widths['heat'] + btn_widths['cool'] + spacing*7, button_y, 
                      btn_widths['pause'], button_height), "Пауза", (80,80,80), (120,120,120), 
                      callback=lambda: callbacks['toggle_pause'](btn_pause))
    btn_auto_heat = Button(pygame.Rect(start_x + btn_widths['add'] + btn_widths['remove'] + btn_widths['bond'] + btn_widths['clear_bonds'] + btn_widths['clear_all'] + btn_widths['heat'] + btn_widths['cool'] + btn_widths['pause'] + spacing*8, button_y, 
                          btn_widths['auto_heat'], button_height), "Автонагрев", (200,120,60), (240,160,80), 
                          callback=callbacks['toggle_auto_heat'])
    btn_auto_cool = Button(pygame.Rect(start_x + btn_widths['add'] + btn_widths['remove'] + btn_widths['bond'] + btn_widths['clear_bonds'] + btn_widths['clear_all'] + btn_widths['heat'] + btn_widths['cool'] + btn_widths['pause'] + btn_widths['auto_heat'] + spacing*9, button_y, 
                          btn_widths['auto_cool'], button_height), "Автоохлаждение", (60,120,200), (80,160,240), 
                          callback=callbacks['toggle_auto_cool'])
    btn_stabilize = Button(pygame.Rect(start_x + btn_widths['add'] + btn_widths['remove'] + btn_widths['bond'] + btn_widths['clear_bonds'] + btn_widths['clear_all'] + btn_widths['heat'] + btn_widths['cool'] + btn_widths['pause'] + btn_widths['auto_heat'] + btn_widths['auto_cool'] + spacing*10, button_y, 
                          btn_widths['stabilize'], button_height), "Стабилизировать", (100,100,150), (140,140,200), 
                          callback=callbacks['stabilize'])
    btn_crystallize = Button(pygame.Rect(start_x + btn_widths['add'] + btn_widths['remove'] + btn_widths['bond'] + btn_widths['clear_bonds'] + btn_widths['clear_all'] + btn_widths['heat'] + btn_widths['cool'] + btn_widths['pause'] + btn_widths['auto_heat'] + btn_widths['auto_cool'] + btn_widths['stabilize'] + spacing*11, button_y, 
                            btn_widths['crystallize'], button_height), "Кристаллизация", (80,80,120), (120,120,160), 
                            callback=callbacks['crystallize'])
    btn_exit = Button(pygame.Rect(start_x + btn_widths['add'] + btn_widths['remove'] + btn_widths['bond'] + btn_widths['clear_bonds'] + btn_widths['clear_all'] + btn_widths['heat'] + btn_widths['cool'] + btn_widths['pause'] + btn_widths['auto_heat'] + btn_widths['auto_cool'] + btn_widths['stabilize'] + btn_widths['crystallize'] + spacing*12, button_y, 
                     btn_widths['exit'], button_height), "Выход", (160,60,60), (200,90,90), 
                     callback=callbacks['exit_app'])

    ui_buttons = [btn_add, btn_remove, btn_bond, btn_clear_bonds, btn_clear,
                  btn_heat, btn_cool, btn_pause, btn_auto_heat, btn_auto_cool, btn_stabilize, btn_crystallize, btn_exit]

    textbox_energy = TextBox(
        pygame.Rect(btn_exit.rect.right + 10, button_y + 4, 60, 30),
        text=f"{sim.energy_delta:.1f}",
        callback=callbacks['set_energy_delta']
    )

    slider_time = Slider(
        pygame.Rect(textbox_energy.rect.right + 30, button_y + 14, 180, 10),
        min_val=0.1, max_val=5.0, initial=sim.time_scale,
        callback=callbacks['set_time_scale']
    )

    sim_rect = pygame.Rect(BORDER, TOP_PANEL_HEIGHT + BORDER, width-2*BORDER, height-TOP_PANEL_HEIGHT-2*BORDER)
    return element_menu, ui_buttons, textbox_energy, slider_time, sim_rect

# ========== ГЛАВНЫЙ ЦИКЛ ==========
def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    width, height = screen.get_size()
    pygame.display.set_caption("Симуляция атомов 2.5D")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 14)

    sim = Simulation()
    running = True

    def exit_app():
        nonlocal running
        running = False
    def set_element(e): sim.current_element = e
    def toggle_add():
        sim.add_mode = not sim.add_mode
        if sim.add_mode:
            sim.remove_mode = sim.bond_mode = False
            remove_btn.active = bond_btn.active = False
            sim.bond_first_atom = None
        add_btn.active = sim.add_mode
    def toggle_remove():
        sim.remove_mode = not sim.remove_mode
        if sim.remove_mode:
            sim.add_mode = sim.bond_mode = False
            add_btn.active = bond_btn.active = False
            sim.bond_first_atom = None
        remove_btn.active = sim.remove_mode
    def toggle_bond():
        sim.bond_mode = not sim.bond_mode
        if sim.bond_mode:
            sim.add_mode = sim.remove_mode = False
            add_btn.active = remove_btn.active = False
            sim.bond_first_atom = None
        bond_btn.active = sim.bond_mode
    def clear_bonds():
        sim.clear_bonds()
    def clear_all():
        sim.clear()
        sim.add_mode = sim.remove_mode = sim.bond_mode = False
        add_btn.active = remove_btn.active = bond_btn.active = False
        sim.bond_first_atom = None
    def heat(): sim.change_energy(sim.energy_delta)
    def cool(): sim.change_energy(-sim.energy_delta)
    def toggle_pause(btn):
        sim.paused = not sim.paused
        btn.text = "Запуск" if sim.paused else "Пауза"
    def toggle_auto_heat():
        sim.auto_heat = not sim.auto_heat
        if sim.auto_heat:
            sim.auto_cool = False
            auto_cool_btn.active = False
        auto_heat_btn.active = sim.auto_heat
    def toggle_auto_cool():
        sim.auto_cool = not sim.auto_cool
        if sim.auto_cool:
            sim.auto_heat = False
            auto_heat_btn.active = False
        auto_cool_btn.active = sim.auto_cool
    def stabilize():
        sim.stabilize()
        sim.auto_heat = sim.auto_cool = False
        auto_heat_btn.active = auto_cool_btn.active = False
    def crystallize():
        sim.crystallize(sim_rect)
    def set_energy_delta(v):
        sim.energy_delta = v
        textbox_energy.set_value(v)
    def set_time_scale(v): sim.time_scale = v

    callbacks = {
        'set_element': set_element,
        'toggle_add': toggle_add,
        'toggle_remove': toggle_remove,
        'toggle_bond': toggle_bond,
        'clear_bonds': clear_bonds,
        'clear_all': clear_all,
        'heat': heat,
        'cool': cool,
        'toggle_pause': toggle_pause,
        'toggle_auto_heat': toggle_auto_heat,
        'toggle_auto_cool': toggle_auto_cool,
        'stabilize': stabilize,
        'crystallize': crystallize,
        'exit_app': exit_app,
        'set_energy_delta': set_energy_delta,
        'set_time_scale': set_time_scale,
    }

    element_menu, ui_buttons, textbox_energy, slider_time, sim_rect = create_ui_elements(width, height, sim, callbacks)
    add_btn = ui_buttons[0]
    remove_btn = ui_buttons[1]
    bond_btn = ui_buttons[2]
    auto_heat_btn = ui_buttons[8]
    auto_cool_btn = ui_buttons[9]

    mouse_held = False
    hold_timer = 0
    repeat_counter = 0

    while running:
        dt = DT
        mouse_pos = pygame.mouse.get_pos()
        mouse_in_sim = sim_rect.collidepoint(mouse_pos)

        if mouse_held and mouse_in_sim:
            hold_timer += dt
            if hold_timer >= REPEAT_DELAY:
                repeat_counter += 1
                if repeat_counter >= 60 / REPEAT_RATE:
                    if sim.add_mode:
                        sim.add_atom(*mouse_pos, sim_rect)
                    elif sim.remove_mode:
                        sim.remove_atom_at(*mouse_pos, sim_rect)
                    repeat_counter = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            element_menu.handle_event(event)
            for btn in ui_buttons:
                btn.handle_event(event)
            slider_time.handle_event(event)
            textbox_energy.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_held = True
                hold_timer = 0
                repeat_counter = 0

                if textbox_energy.active and not textbox_energy.rect.collidepoint(event.pos):
                    textbox_energy._apply_value()
                    textbox_energy.active = False

                if mouse_in_sim:
                    atom = sim.find_atom_at(event.pos, sim_rect)
                    if sim.bond_mode:
                        if atom:
                            if sim.bond_first_atom is None:
                                sim.bond_first_atom = atom
                            else:
                                if atom is not sim.bond_first_atom:
                                    sim.add_bond(sim.bond_first_atom, atom, teleport=True)
                                sim.bond_first_atom = None
                    elif atom:
                        sim.selected_atom = atom
                        sim.dragging = True
                        sim.drag_offset = atom.pos - np.array(event.pos)
                    elif sim.add_mode:
                        sim.add_atom(*event.pos, sim_rect)
                if sim.remove_mode and mouse_in_sim:
                    sim.remove_atom_at(*event.pos, sim_rect)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_held = False
                if sim.dragging:
                    sim.dragging = False
                    sim.selected_atom = None

            elif event.type == pygame.MOUSEMOTION:
                if sim.dragging and sim.selected_atom:
                    new_mouse_pos = np.array(event.pos)
                    target_pos = new_mouse_pos + sim.drag_offset
                    delta = target_pos - sim.selected_atom.pos
                    group = sim.get_connected_component(sim.selected_atom)
                    for atom in group:
                        atom.pos += delta
                        left = sim_rect.left + atom.radius
                        right = sim_rect.right - atom.radius
                        top = sim_rect.top + atom.radius
                        bottom = sim_rect.bottom - atom.radius
                        atom.pos[0] = np.clip(atom.pos[0], left, right)
                        atom.pos[1] = np.clip(atom.pos[1], top, bottom)
                    sim.drag_offset = sim.selected_atom.pos - new_mouse_pos

        textbox_energy.update()
        sim.update(dt, sim_rect)

        screen.fill((30, 30, 40))
        panel_rect = pygame.Rect(0, 0, width, TOP_PANEL_HEIGHT)
        pygame.draw.rect(screen, PANEL_COLOR, panel_rect)
        pygame.draw.line(screen, (80, 80, 80), (0, panel_rect.bottom), (width, panel_rect.bottom), 2)

        sim.draw(screen, font, sim_rect)

        element_menu.draw(screen)
        for btn in ui_buttons:
            btn.draw(screen)

        label_font = pygame.font.SysFont("Arial", 12)
        energy_label = label_font.render("ΔE:", True, (200, 200, 200))
        screen.blit(energy_label, (textbox_energy.rect.left-35, textbox_energy.rect.centery-8))
        textbox_energy.draw(screen)

        time_label = label_font.render("Время:", True, (200, 200, 200))
        screen.blit(time_label, (slider_time.rect.left-45, slider_time.rect.centery-8))
        slider_time.draw(screen, font)

        if sim.bond_mode:
            if sim.bond_first_atom:
                hint = f"Нажмите на второй атом (связь с {sim.bond_first_atom.element})"
            else:
                hint = "Нажмите на первый атом для связи"
            hint_surf = font.render(hint, True, (255, 200, 200))
            screen.blit(hint_surf, (width//2 - 180, TOP_PANEL_HEIGHT + 5))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()