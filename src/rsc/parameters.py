# -*- coding: utf-8 -*-

import struct

from tools import data2dict, split_bits, strip_0, msg, err


class Type(object):
    UNKNOWN = '--- UNKNOWN ---'
    LINE = 'LINE'  # Простая линия, код типа примитива  128.
    LINE_DASH = 'LINE_DASH'  # Пунктирная линия, код типа примитива  129.
    LINE_DASH_OFFSETED = 'LINE_DASH_OFFSETED'  # Смещенный пунктир, код типа примитива  148.
    AREA = 'AREA'  # Площадь, код типа примитива  135.
    AREA_DASHED = 'AREA_DASHED'  # Штрихованная площадь, код типа примитива  153.
    POINT = 'POINT'  # Точечный объект, код типа примитива  143.
    AREA_FILLED = 'AREA_FILLED'  # Площадь, заполненная знаками, код типа примитива  144.
    ROUND = 'ROUND'  # Окружность, код типа примитива  140.
    LIGTNESS = 'LIGTNESS'  # Освещение участка, код типа примитива  154.
    POINT_VECTOR = 'POINT_VECTOR'  # Векторный знак, код типа примитива  149.
    AREA_FILLED_VECTOR = 'AREA_FILLED_VECTOR'  # Площадь, заполненная векторными знаками, код типа примитива  155.
    LINE_DECORED = 'LINE_DECORED'  # Декорированная линия, код типа примитива  157.
    TEXT = 'TEXT'  # Текст, код типа примитива  142.
    TEXT_USER_DEFINED = 'TEXT_USER_DEFINED'  # Шрифт пользователя, код типа примитива  152.
    PATTERN = 'PATTERN'  # Шаблон, код типа примитива  150.
    POINT_TRUE_TYPE = 'POINT_TRUE_TYPE'  # Знак True-Type шрифта, код типа примитива  151.
    SET = 'SET'  # Набор примитивов, код типа примитива  147.
    LINE_DASH_CUSTOM = 'LINE_DASH_CUSTOM'  # Наборная штриховая линия, код типа примитива  158.
    POINT_BITMAP = 'POINT_BITMAP'  # Точечный знак _ графическое изображение, код типа примитива  165.
    USER_DEFINED = 'USER_DEFINED'  # Объект пользователя, код типа примитива  250. Используется для формирования объектов разнообразного вида. Пользователь может строить метрику объекта по существующующей и рисовать различные знаки, используя стандартнве примитивы. Для построения отображения таких объектов используются спещиально разработанные IML – библиотеки. Параметры же таких объектов описываются следующим образом.

    CODES = {
        128: LINE,
        129: LINE_DASH,
        148: LINE_DASH_OFFSETED,
        135: AREA,
        153: AREA_DASHED,
        143: POINT,
        144: AREA_FILLED,
        140: ROUND,
        154: LIGTNESS,
        149: POINT_VECTOR,
        155: AREA_FILLED_VECTOR,
        157: LINE_DECORED,
        142: TEXT,
        152: TEXT_USER_DEFINED,
        150: PATTERN,
        151: POINT_TRUE_TYPE,
        147: SET,
        158: LINE_DASH_CUSTOM,
        165: POINT_BITMAP,
        250: USER_DEFINED,
    }


PARAM_RECORD_HEADER_DESC = (
    ('I', 'length', 'Длина записи +0 4 В байтах, с учетом длины кодов семантик', ),
    ('h', 'code', 'Внутренний код объекта +4 2 Порядковый номер объекта', ),
    ('h', 'type', 'Номер функции отображения +6 2 Код типа примитива.', ),
    # Параметры отображения +8 ? Параметры примитива соответствующие типу Приложение А.
)  # ИТОГО: 8 байт + длина параметров примитива.


def parameters2dict(rsc):
    result = {
        'screen': {},
        'printer': {},
    }
    par_raw, par_offset, par_count = rsc.get_table_data('par')
    prn_raw, prn_offset, prn_count = rsc.get_table_data('prn')

    par_idx = 0
    for par_i in xrange(par_count):
        obj = data2dict(PARAM_RECORD_HEADER_DESC, par_raw[par_idx:par_idx + 8])
        obj['type'] = Type.CODES.get(obj['type'], Type.UNKNOWN)
        par_idx += obj['length']

        obj['parameters'] = []

        # cls_idx = cls_offset - obj['semantic_classifier_offset']
        # for cls_i in xrange(obj['semantic_classifier_records']):
        #     cl = data2dict(SEMANTIC_CLASSIFIER_RECORD_DESC, cls_raw[cls_idx:cls_idx + 84])
        #     cl['str'] = strip_0(cl['str']).decode('cp1251')
        #     cls_idx += 84
        #     obj['classifiers'].append(cl)

        result['screen'][obj['code']] = obj

    par_idx = 0
    for par_i in xrange(prn_count):
        obj = data2dict(PARAM_RECORD_HEADER_DESC, par_raw[par_idx:par_idx + 8])
        obj['type'] = Type.CODES.get(obj['type'], Type.UNKNOWN)
        par_idx += obj['length']

        obj['parameters'] = []

        # cls_idx = cls_offset - obj['semantic_classifier_offset']
        # for cls_i in xrange(obj['semantic_classifier_records']):
        #     cl = data2dict(SEMANTIC_CLASSIFIER_RECORD_DESC, cls_raw[cls_idx:cls_idx + 84])
        #     cl['str'] = strip_0(cl['str']).decode('cp1251')
        #     cls_idx += 84
        #     obj['classifiers'].append(cl)

        result['printer'][obj['code']] = obj

    rsc.parameters_dict = result
    # sys.stdout.write(yaml.dump(result, allow_unicode=True, default_flow_style=False))
    # sys.stdout.write(yaml.dump(result, allow_unicode=True))
