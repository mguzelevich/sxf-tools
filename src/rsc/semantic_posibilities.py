# -*- coding: utf-8 -*-

import struct
from tools import split_bits


class OBJECT_TYPE(object):
    LINE = 'LINE'
    VECTOR = 'VECTOR'
    AREA = 'AREA'
    POINT = 'POINT'
    LABEL = 'LABEL'
    LABEL_TEMPLATE = 'LABEL_TEMPLATE'


class RscSemanticPosibilitiesObject(object):

    def __init__(self):
        self.required_codes = []
        self.possible_codes = []

    @staticmethod
    def parse(data):
        record = RscSemanticPosibilitiesObject()
        record.parse_record(data)
        return record

    def info(self):
        print u'Semantic Posibilities Object [%s] %s + %s' % (
            self.code,
            self.required_semantics_count,
            self.posible_semantics_count,
        )

    def parse_record(self, data):
        """2.1.6 Структура таблицы возможных семантик объекта
        Для каждого объекта классификатора пользователь может назначить обязательную или возможную семантику.
        Если семантика возможная, заполнение ее при нанесении объекта на карту не обязательно.
        Если пользователь не заполнит значение обязательной семантики объекта, семантика будет записана с умалчиваемым значением.
        Все объекты серии имеют одну запись в таблице возможных семантик.
        Перед таблицей возможных семантик объекта находится идентификатор таблицы “.POS” (шестнадцатеричное число 0X00534F50)
        (не входит в длину таблицы). Записи таблицы умалчиваемых значений семантики переменной длины, более 20 байт."""

        # Назначение поля Смещение    Длина   Комментарий
        # Длина записи    0   4   В байтах, с учетом длины кодов семантик
        self.full_length = struct.unpack('<I', data[0:4])[0]

        # Классификационный код объекта   4   4
        self.code = struct.unpack('<I', data[4:8])[0]

        # Локализация 4   1
        self.localization = struct.unpack('<B', data[8:9])[0]

        # Резерв  5   3   0

        # Количество обязательных семантик    8   2   Число от 0 до 255 (N4)
        self.required_semantics_count = struct.unpack('<h', data[12:14])[0]

        # Количество возможных семантик   10  2   Число от 0 до 255 (N5)
        self.posible_semantics_count = struct.unpack('<h', data[14:16])[0]

        # Коды семантик   12  4
        idx = 16
        for i in xrange(self.required_semantics_count):
            code = struct.unpack('<I', data[idx:idx + 4])[0]
            self.required_codes.append(code)
            idx += 4
        for i in xrange(self.posible_semantics_count):
            code = struct.unpack('<I', data[idx:idx + 4])[0]
            self.possible_codes.append(code)
            idx += 4

        # ИТОГО:  16 байт + (N4+N5) * 4
