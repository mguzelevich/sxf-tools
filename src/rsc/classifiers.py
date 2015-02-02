# -*- coding: utf-8 -*-

import struct

from tools import (
    data2dict,
    # err,
    # msg,
    # print_hex,
    # split_bits,
    strip_0,
)


class OBJECT_TYPE(object):
    UNKNOWN = '--- UNKNOWN ---'
    LINE = 'LINE'  # 0х00 - линейный,
    VECTOR = 'VECTOR'  # 0х01 – площадной,
    AREA = 'AREA'  # 0х02 – точечный,
    POINT = 'POINT'  # 0х03 – подпись,
    LABEL = 'LABEL'  # 0х04 - векторный (точечный ориентированный объект, содержит две точки в   метрике),
    LABEL_TEMPLATE = 'LABEL_TEMPLATE'  # 0x05 - шаблон подписи (первая точка метрики является точкой привязки шаблона, метрика подобъектов задает расположение подписей и вспомогательных линий).

    CODES = {
        0x00: LINE,
        0x01: AREA,
        0x02: POINT,
        0x03: LABEL,
        0x04: VECTOR,
        0x05: LABEL_TEMPLATE,
    }


class DIGITIZE_DIRECTION(object):
    UNKNOWN = '--- UNKNOWN ---'
    UNDEFINED = 'UNDEFINED'  # 0x00-произвольное,
    DEFINED = 'DEFINED'  # 0x01-определенное,
    ON_RIGHT = 'ON_RIGHT'  # 0х02-объект справа,
    ON_LEFT = 'ON_LEFT'  # 0x04-объект слева.

    CODES = {
        0x00: UNDEFINED,
        0x01: DEFINED,
        0x02: ON_RIGHT,
        0x04: ON_LEFT,
    }


OBJ_HEADER_DESC = (
    # datatype, name, comment (# Назначение поля / Смещение / Длина / Комментарий)
    ('I', 'full_length', 'Длина записи объекта    0   4   В байтах', ),
    ('I', 'classifier_code', 'Классификационный код   4   4', ),
    ('I', 'internal_code', 'Внутренний код объекта  8   4   Порядковый номер объекта (может меняться) (с 1)', ),
    ('I', 'id', 'Идентификационный код   12  4   Неизменяемый уникальный номер объекта', ),
    ('32s', 'short_name', 'Короткое имя объекта    16  32  Уникальное символьное имя (ANSI)', ),
    ('32s', 'name', 'Название    48  32  ANSI', ),
    ('B', 'localization', 'Характер локализации    80  1', ),
    ('B', 'segment', 'Номер слоя (сегмента)   81  1   Число от 0 до 255', ),
    ('B', 'is_scalable', 'Признак масштабируемости    82  1   0 - условный знак объекта не масштабируемый; 1 - знак масштабируется;', ),
    ('B', 'visibility_low', 'Нижняя граница видимости    83  1   Число от 0 до 15 (N1)', ),
    ('B', 'visibility_high', 'Верхняя граница видимости   84  1   "Число от 0 до 15 (15 – N2)"', ),
    ('B', 'localization_extention', 'Расширение локализации  85  1  "1 - при создании линейных объектов учитывать две точки метрики 0 – все точки метрики"', ),
    ('B', 'digitize_direction', 'Направление цифрования  86  1', ),
    ('B', 'display_with_semantic', 'Отображение с учетом семантики  87  1   1- для объектов с внешним видом пользователя, учитывающих семантику', ),
    ('h', 'object_number', 'Номер расширения +88 2 Для объектов из серии – номер объекта в серии, для остальных 0.', ),
    ('B', 'connected_label_count', 'Количество связанных подписей   90  1   Число от 0 до 16', ),
    ('B', 'compressable', 'Признак сжатия объекта  91  1   "Возможность сжатия объекта при уменьшении масштаба 1 – не сжимать"', ),
    ('B', 'max_scale', 'Максимальное увеличение 92  1   "Максимальное увеличение объекта (от 1 до 25.0 раз) Значения от 0 до 250"', ),
    ('B', 'min_scale', 'Максимальное уменьшение 93  1   "Максимальное уменьшение объекта (от 1 до 25.0 раз) Значения от 0 до 250"', ),
    ('B', 'is_view_borders', 'Флаг включения границ   94  1   Флаг включения границ видимости', ),
    ('B', None, 'Резерв  95  1', ),
)

OBJ_CONNECTED_LABEL_DESC = (
    # Связанная подпись объекта определяет шрифт, предназначенный для нанесения подписей объекта,
    # текст которых содержится в качестве семантической характеристики этого объекта.
    ('I', 'label_id', 'Идентификационный код связанной подписи 0   4   Неизменяемый уникальный номер подписи', ),
    ('I', 'semantic_id', 'Классификационный код семантики 4   4   Код семантики объекта, содержащей текст подписи', ),
    ('7s', 'prefix', 'Постоянный префикс для подписи  8   7   В байтах', ),
    ('B', 'decimal_points', 'Количество десятичных знаков после запятой  15  1   Используется при печати подписи', ),
)


def classifiers2dict(rsc):
    result = {}
    obj_raw, obj_offset, obj_count = rsc.get_table_data('obj')
    pos_raw, pos_offset, pos_count = rsc.get_table_data('pos')

    obj_idx = 0
    for i in xrange(obj_count):
        obj = data2dict(OBJ_HEADER_DESC, obj_raw[obj_idx:obj_idx + 96])

        raw = obj_raw[obj_idx:obj_idx + obj['full_length']]
        obj['short_name'] = strip_0(obj['short_name']).decode('cp1251')
        obj['name'] = strip_0(obj['name']).decode('cp1251')
        obj['localization'] = OBJECT_TYPE.CODES.get(obj['localization'], OBJECT_TYPE.UNKNOWN)

        # Для площадных объектов возможны направления цифрования объект слева (обход объекта против часовой стрелки: используется для водоемов и углублений рельефа) и объект справа (обход объекта по часовой стрелке).
        # Для линейных объектов можно определенное (для тех объектов, для которых имеет смысл различать начало и конец метрики, например реки, цифруются от истока к устью) и произвольное для всех остальных случаев.
        # Точечные объекты имеют только произвольное направление цифрования.
        # Все остальные произвольное или определенное.
        # Связанные подписи объектов предназначены для нанесения на карту подписей по семантическим характеристикам объекта, определенным видом шрифта. Шрифт выбирается из существующих подписей классификатора.
        obj['digitize_direction'] = DIGITIZE_DIRECTION.CODES.get(obj['digitize_direction'], DIGITIZE_DIRECTION.UNKNOWN)
        obj_idx += obj['full_length']

        if obj['connected_label_count']:
            obj['connected_labels'] = []

        idx = 96
        for li in xrange(obj['connected_label_count']):
            label = data2dict(OBJ_CONNECTED_LABEL_DESC, raw[idx:idx + 16])
            idx += 16
            obj['connected_labels'].append(label)
        result[obj['classifier_code']] = obj

    pos_idx = 0
    for i in xrange(pos_count):
        # Назначение поля Смещение    Длина   Комментарий
        (
            full_length,  # Длина записи    0   4   В байтах, с учетом длины кодов семантик
            obj_code,  # Классификационный код объекта   4   4
            localization,  # Локализация 4   1
            reserve,  # Резерв  5   3   0
            required_semantics_count,  # Количество обязательных семантик    8   2   Число от 0 до 255 (N4)
            posible_semantics_count,  # Количество возможных семантик   10  2   Число от 0 до 255 (N5)
        ) = struct.unpack('<IIB3shh', pos_raw[pos_idx:pos_idx + 16])

        localization = OBJECT_TYPE.CODES.get(localization, OBJECT_TYPE.UNKNOWN)

        raw = obj_raw[pos_idx:pos_idx + full_length]

        pos_idx += full_length

        result[obj_code]['semantics'] = {
            'localization': localization,
            'required': [],
            'optional': [],
        }

        # Коды семантик   12  4
        idx = 0
        for i in xrange(required_semantics_count):
            sem_code = struct.unpack('<I', raw[idx:idx + 4])[0]
            result[obj_code]['semantics']['required'].append(sem_code)
            idx += 4
        for i in xrange(posible_semantics_count):
            sem_code = struct.unpack('<I', raw[idx:idx + 4])[0]
            result[obj_code]['semantics']['optional'].append(sem_code)
            idx += 4
        # ИТОГО:  16 байт + (N4+N5) * 4

    rsc.objects_dict = result
    # sys.stdout.write(yaml.dump(result, allow_unicode=True, default_flow_style=False))
    # sys.stdout.write(yaml.dump(result, allow_unicode=True))
