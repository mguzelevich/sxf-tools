# -*- coding: utf-8 -*-

import struct

from tools import split_bits, strip_0, msg, err


class SemanticType(object):
    UNKNOWN = '--- UNKNOWN ---'
    STRING = 'str'  # 0х00 - символьная строка,
    INT = 'int'  # 0х01 - числовое значение или значение в виде числового кода из классификатора значений
    FILENAME = 'filename'  # 0х09 - имя файла зарегистрированного типа
    FILENAME_BMP = 'filename_bmp'  # 0х0А - имя файла BMP
    FILENAME_OLE = 'filename_ole'  # 0x0B - имя файла, обрабатываемого OLE-сервером
    MAP_ITEM = 'map_item'  # 0x0C - ссылка на произвольный объект карты (уникальный номер объекта)
    FILENAME_REG_PASSPORT = 'filename_regpassport'  # 0x0D - имя файла-паспорта района
    FILENAME_TXT = 'filename_txt'  # 0x0E - имя текстового файла
    FILENAME_PCX = 'filename_pcx'  # 0x0F - имя файла PCX

    CODES = {
        0x00: STRING,
        0x01: INT,
        0x09: FILENAME,
        0x0a: FILENAME_BMP,
        0x0b: FILENAME_OLE,
        0x0c: MAP_ITEM,
        0x0d: FILENAME_REG_PASSPORT,
        0x0e: FILENAME_TXT,
        0x0f: FILENAME_PCX,
    }


def semantics2dict(rsc):
    result = {}
    sem_raw, sem_offset, sem_count = rsc.get_table_data('SEM\0')
    cls_raw, cls_offset, cls_count = rsc.get_table_data('CLS\0')
    def_raw, def_offset, def_count = rsc.get_table_data('DEF\0')

    sem_idx = 0
    for sem_i in xrange(sem_count):
        # Назначение поля Смещение    Длина   Комментарий
        (
            code,  # Код семантики   0   4   Неизменяемый уникальный
            semantic_type,  # Тип значения семантики  4   2
            repeatable,  # Повторяемость семантики 6   1   1 - у объекта может быть несколько значений семантики с таким кодом
            staff_semantic,  # Признак служебной семантики 7   1   1 - семантику можно использовать для всех объектов классификатора
            name,  # Название    8   32  ANSI
            short_name,  # Короткое имя семантики 40 16 Уникальное символьное имя (ANSI). Используется для подписей полей в базах данных
            unit,  # Единица измерения   56  8   ANSI
            field_size,  # Размер поля семантики   64  2   Число от 0 до 255
            accuracy,  # Точность семантики  66  1   Количество цифр после запятой (при выводе)
            is_complex_semantic,  # Флаг    67  1   2 семантика составная
            semantic_classifier_offset,  # Смещение на описание классификатора семантики   68  4   От начала файла Если нет записей – 0
            semantic_classifier_records,  # Количество записей в классификаторе данной семантики    72  4   Если нет записей – 0
            semantic_defaults_offset,  # Смещение на умалчиваемые значения семантики 76  4   От начала файла Если нет записей – 0.
            semantic_defaults_records,  # Количество записей для умалчиваемых значений    80  4   Если нет записей – 0
        ) = struct.unpack('<IhBB32s16s8shBBIIII', sem_raw[sem_idx:sem_idx + 84])  # ИТОГО:  84 байта

        name = strip_0(name).decode('cp1251')
        short_name = strip_0(short_name).decode('cp1251')
        unit = strip_0(unit).decode('cp1251')
        semantic_type = SemanticType.CODES.get(semantic_type, SemanticType.UNKNOWN)
        sem_idx += 84

        result[code] = {
            'code': code,
            'semantic_type': semantic_type,
            'repeatable': repeatable,
            'staff_semantic': staff_semantic,
            'name': name,
            'short_name': short_name,
            'unit': unit,
            'field_size': field_size,
            'accuracy': accuracy,
            'is_complex_semantic': is_complex_semantic,
            'classifiers': [],
            'defaults': [],
        }

        cls_idx = cls_offset - semantic_classifier_offset
        for cls_i in xrange(semantic_classifier_records):
            (
                int_value,  # Числовое значение семантики 0   4
                string_value,  # Символьное значение семантики   4   32  ANSI
                reserved,
            ) = struct.unpack('<I32s48s', cls_raw[cls_idx:cls_idx + 84])  # ИТОГО:   84 байта
            string_value = strip_0(string_value).decode('cp1251')
            cls_idx += 84
            result[code]['classifiers'].append([int_value, string_value, ])

        def_idx = def_offset - semantic_defaults_offset
        for def_i in xrange(semantic_defaults_records):
            (
                id,  # Порядковый номер объекта    0   4   Если номер равен 0 – это умалчиваемое значение для семантики
                sem_code,  # Код семантики   4   4  Из таблицы  2.4
                min_value,  # Минимальное значение семантики  4   8
                default_value,  # "Значение семантики по умолчанию "  8   8
                max_value,  # "Максимальное значение Семантики"  8   8
            ) = struct.unpack('<IIddd', def_raw[def_idx:def_idx + 32])  # ИТОГО:  32 байта
            def_idx += 32

            p = {
                'id': id,
                'code': sem_code,
                'min_value': min_value,
                'default_value': default_value,
                'max_value': max_value,
            }
            result[code]['defaults'].append(p)
    rsc.semantics_dict = result
    # sys.stdout.write(yaml.dump(result, allow_unicode=True, default_flow_style=False))
    # sys.stdout.write(yaml.dump(result, allow_unicode=True))
