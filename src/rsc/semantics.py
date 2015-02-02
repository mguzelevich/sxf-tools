# -*- coding: utf-8 -*-

import struct

from tools import data2dict, split_bits, strip_0, msg, err


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


SEM_OBJ_DESC = (
    ('I', 'code', 'Код семантики   0   4   Неизменяемый уникальный', ),
    ('h', 'semantic_type', 'Тип значения семантики  4   2', ),
    ('B', 'repeatable', 'Повторяемость семантики 6   1   1 - у объекта может быть несколько значений семантики с таким кодом', ),
    ('B', 'staff_semantic', 'Признак служебной семантики 7   1   1 - семантику можно использовать для всех объектов классификатора', ),
    ('32s', 'name', 'Название    8   32  ANSI', ),
    ('16s', 'short_name', 'Короткое имя семантики 40 16 Уникальное символьное имя (ANSI). Используется для подписей полей в базах данных', ),
    ('8s', 'unit', 'Единица измерения   56  8   ANSI', ),
    ('h', 'field_size', 'Размер поля семантики   64  2   Число от 0 до 255', ),
    ('B', 'accuracy', 'Точность семантики  66  1   Количество цифр после запятой (при выводе)', ),
    ('B', 'is_complex_semantic', 'Флаг    67  1   2 семантика составная', ),
    ('I', 'semantic_classifier_offset', 'Смещение на описание классификатора семантики   68  4   От начала файла Если нет записей – 0', ),
    ('I', 'semantic_classifier_records', 'Количество записей в классификаторе данной семантики    72  4   Если нет записей – 0', ),
    ('I', 'semantic_defaults_offset', 'Смещение на умалчиваемые значения семантики 76  4   От начала файла Если нет записей – 0.', ),
    ('I', 'semantic_defaults_records', 'Количество записей для умалчиваемых значений    80  4   Если нет записей – 0', ),
)  # ИТОГО:  84 байта


SEMANTIC_CLASSIFIER_RECORD_DESC = (
    ('I', 'int', 'Числовое значение семантики 0   4', ),
    ('32s', 'str', 'Символьное значение семантики   4   32  ANSI', ),
    ('48s', None, '', ),
)  # ИТОГО:   84 байта


SEMANTIC_DEFAULTS_RECORD_DESC = (
    ('I', 'id', 'Порядковый номер объекта    0   4   Если номер равен 0 – это умалчиваемое значение для семантики', ),
    ('I', 'sem_code', 'Код семантики   4   4  Из таблицы  2.4', ),
    ('d', 'min', 'Минимальное значение семантики  4   8', ),
    ('d', 'def', 'Значение семантики по умолчанию  8   8', ),
    ('d', 'max', '"Максимальное значение Семантики"  8   8', ),
)  # ИТОГО:  32 байта


def semantics2dict(rsc):
    result = {}
    sem_raw, sem_offset, sem_count = rsc.get_table_data('sem')
    cls_raw, cls_offset, cls_count = rsc.get_table_data('cls')
    def_raw, def_offset, def_count = rsc.get_table_data('def')

    sem_idx = 0
    for sem_i in xrange(sem_count):
        # Назначение поля Смещение    Длина   Комментарий
        obj = data2dict(SEM_OBJ_DESC, sem_raw[sem_idx:sem_idx + 84])

        obj['name'] = strip_0(obj['name']).decode('cp1251')
        obj['short_name'] = strip_0(obj['short_name']).decode('cp1251')
        obj['unit'] = strip_0(obj['unit']).decode('cp1251')
        obj['semantic_type'] = SemanticType.CODES.get(obj['semantic_type'], SemanticType.UNKNOWN)
        sem_idx += 84

        obj['classifiers'] = []
        obj['defaults'] = []

        cls_idx = cls_offset - obj['semantic_classifier_offset']
        for cls_i in xrange(obj['semantic_classifier_records']):
            cl = data2dict(SEMANTIC_CLASSIFIER_RECORD_DESC, cls_raw[cls_idx:cls_idx + 84])
            cl['str'] = strip_0(cl['str']).decode('cp1251')
            cls_idx += 84
            obj['classifiers'].append(cl)

        def_idx = def_offset - obj['semantic_defaults_offset']
        for def_i in xrange(obj['semantic_defaults_records']):
            df = data2dict(SEMANTIC_DEFAULTS_RECORD_DESC, def_raw[def_idx:def_idx + 32])
            def_idx += 32
            obj['defaults'].append(df)

        result[obj['code']] = obj
    rsc.semantics_dict = result
    # sys.stdout.write(yaml.dump(result, allow_unicode=True, default_flow_style=False))
    # sys.stdout.write(yaml.dump(result, allow_unicode=True))
