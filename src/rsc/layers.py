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


class RscSemanticDefaultsObject(object):

    def __init__(self):
        self.errors = []
        self.id = None
        self.connected_labels = []

    @staticmethod
    def parse(data):
        record = RscSemanticClassifierObject()
        record.parse_record(data)
        return record

    def info(self):
        print u'Classifier Object %s <%s> "%s"' % (
            self.id,
            self.short_name.decode('cp1251'),
            self.name.decode('cp1251'),
        )

    def parse_record(self, data):
        """2.1.7 Структура таблицы  слоев
        Таблица слоев классификатора находится по смещению на таблицу слоев. Имеет общую длину, указанную в заголовке классификатора.
        Перед таблицей слоев (сегментов) находится идентификатор таблицы “.SEG” (шестнадцатеричное число 0X00474553)  (не входит в длину таблицы).  Записи таблицы слоев (сегментов) переменной длины, более 60 байт."""

        # Назначение поля Смещение    Длина   Комментарий
        # Длина записи    0   4   В байтах, с учетом длины кодов семантик
        # Название слоя   4   32  ANSI
        # Короткое название слоя  36  16  ANSI. Для связи с названием полей в базах данных
        # Номер слоя (сегмента)   52  1   Соответствует номеру, из таблицы объектов
        # Порядок отображения объектов слоя   53  1   Число от 0 до 255 Меньший номер будет отображаться раньше
        # Количество семантик слоя    54  2   Число от 0 до 255 (N6)
        # Коды семантик   56  4   Семантики слоя используются при переходе к другим ГИС
        # ИТОГО:  Если N6 <= 1 60 байт иначе 60 байт + (N6 – 1) * 4       
        self.full_length = struct.unpack('<I', data[0:4])[0]
