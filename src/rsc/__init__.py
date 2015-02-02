# -*- coding: utf-8 -*-

from tools import split_bits

import struct
import yaml

from rsc.classifiers import classifiers2dict
from rsc.semantics import semantics2dict
from rsc.parameters import parameters2dict

from tools import msg, err, data2dict, print_hex


def unicode_representer(dumper, uni):
    node = yaml.ScalarNode(tag=u'tag:yaml.org,2002:str', value=uni)
    return node
yaml.add_representer(unicode, unicode_representer)

RSC_TABLES = (
    'obj',
    'sem',
    'cls',
    'def',
    'pos',
    'seg',
    'lim',
    'par',
    'prn',
    'pal',
    'txt',
    'iml',
    'tab',
    'cmy',
    'grs',
    # FNM
)

RSC_FILE_HEADER_DESC = (
    ('4s', 'prefix', 'Идентификатор файла 0   4   0x00435352 (RSC)'),
    ('I', 'full_length', 'Длина файла 4   4   В байтах'),
    ('I', 'version', 'Версия структуры RSC    8   4   0x0700'),
    ('I', 'encoding', 'Кодировка   12  4   Для всего файла'),
    ('I', 'state_number', 'Номер состояния файла   16  4   Учет корректировок, требующих перегрузки данных'),
    ('I', 'correction', 'Номер модификации состояния 20  4   Учет корректировок'),
    ('I', 'language', 'Используемый язык   24  4   1-английский, 2-русский'),
    ('I', 'max_id', 'Максимальный идентификатор таблицы объектов 28  4   Идентификатор для нового объекта'),
    ('8s', 'created_at', 'Дата создания файла 32  8   ГГГГММДД'),
    ('32s', 'map_type', 'Тип карты   40  32 символьное поле 32 байта'),
    ('32s', 'name', 'Условное название классификатора    72  32  ANSI'),
    ('8s', 'classifier_code', 'Код классификатора  104 8   ANSI'),
    ('I', 'scale', 'Масштаб карты   112 4   Базовый масштаб карты, на который составлен классификатор.'),
    ('I', 'scale_line', 'Масштабный ряд  116 4'),

    ('I', 'obj_offset', 'Смещение на таблицу объектов    120 4   От начала файла'),
    ('I', 'obj_length', 'Длина таблицы объектов  124 4   В байтах'),
    ('I', 'obj_count', 'Число записей   128 4   Записи переменной длины'),

    ('I', 'sem_offset', 'Смещение на таблицу семантики (от начала файла)'),
    ('I', 'sem_length', 'Длина таблицы (в байтах'),
    ('I', 'sem_count', 'Число записей (Записи постоянной длины)'),

    ('I', 'cls_offset', 'Смещение на таблицу классификатор семантики (от начала файла)'),
    ('I', 'cls_length', 'Длина таблицы (в байтах'),
    ('I', 'cls_count', 'Число записей (Записи постоянной длины)'),

    ('I', 'def_offset', 'Смещение на таблицу умолчаний (от начала файла)'),
    ('I', 'def_length', 'Длина таблицы (в байтах'),
    ('I', 'def_count', 'Число записей (Записи постоянной длины)'),

    ('I', 'pos_offset', 'Смещение на таблицу возможных семантик (от начала файла)'),
    ('I', 'pos_length', 'Длина таблицы (в байтах'),
    ('I', 'pos_count', 'Число записей (Записи постоянной длины)'),

    ('I', 'seg_offset', 'Смещение на таблицу сегментов (слоев) (от начала файла)'),
    ('I', 'seg_length', 'Длина таблицы (в байтах'),
    ('I', 'seg_count', 'Число записей (Записи постоянной длины)'),

    ('I', 'lim_offset', 'Смещение на таблицу Порогов (от начала файла)'),
    ('I', 'lim_length', 'Длина таблицы (в байтах'),
    ('I', 'lim_count', 'Число записей (Записи переменной длины)'),

    ('I', 'par_offset', 'Смещение на таблицу параметров (от начала файла)'),
    ('I', 'par_length', 'Длина таблицы (в байтах'),
    ('I', 'par_count', 'Число записей (Записи переменной длины)'),

    ('I', 'prn_offset', 'Смещение на таблицу параметров печати (от начала файла)'),
    ('I', 'prn_length', 'Длина таблицы (в байтах'),
    ('I', 'prn_count', 'Число записей (Записи переменной длины)'),

    ('I', 'pal_offset', 'Смещение на таблицу палитр (от начала файла)'),
    ('I', 'pal_length', 'Длина таблицы (в байтах'),
    ('I', 'pal_count', 'Число записей (Записи постоянной длины)'),

    ('I', 'txt_offset', 'Смещение на таблицу шрифтов (от начала файла)'),
    ('I', 'txt_length', 'Длина таблицы (в байтах'),
    ('I', 'txt_count', 'Число записей (Записи постоянной длины)'),

    ('I', 'iml_offset', 'Смещение на таблицу библиотек (от начала файла)'),
    ('I', 'iml_length', 'Длина таблицы (в байтах'),
    ('I', 'iml_count', 'Число записей (Записи постоянной длины)'),

    ('I', 'grs_offset', 'Смещение на таблицу изображений семантики (от начала файла)'),
    ('I', 'grs_length', 'Длина таблицы (в байтах'),
    ('I', 'grs_count', 'Число записей (Записи постоянной длины)'),

    ('I', 'tab_offset', 'Смещение на таблицу таблиц (от начала файла)'),
    ('I', 'tab_length', 'Длина таблицы (в байтах'),
    ('I', 'tab_count', 'Число записей (Записи постоянной длины)'),

    ('B', 'keys_as_codes', 'Флаг использования ключей как кодов'),
    ('B', 'palettes_modifications', 'Флаг модификации палитры    269 1   Учет корректировок'),

    ('h', None, 'Резерв  270 2   0'),
    ('I', None, 'Резерв  272 4   Не использовать'),
    ('I', None, 'Резерв  276 4   Не использовать'),
    ('20s', None, 'Резерв  280 20  0'),

    ('I', 'fonts_encoding', 'Кодировка шрифтов   300 4'),
    ('I', 'palettes_clolors', 'Количество цветов в палитрах    304 4   Не более 256, одинаково для всех палитр'),
)  # ИТОГО: 308 байт  # в исходной спеке на формат - ошибка. в реальности тут 328 байт


class RSC(object):

    records = []

    @staticmethod
    def parse(data):
        rsc = RSC(data)
        rsc.parse_header()

        rsc.init_tables()
        rsc.check_tables()

        rsc.parse_classifier_objects()
        rsc.parse_semantics()

        rsc.parse_semantic_images()
        rsc.parse_table_tbl()
        rsc.parse_colors()
        rsc.parse_fonts()
        rsc.parse_libraries()
        rsc.parse_limits()
        rsc.parse_palettes()
        rsc.parse_parameters()
        rsc.parse_segments()
        return rsc

    def __init__(self, filehandler):
        self.corrupted_tables = {}
        self.filehandler = filehandler

    def info(self):
        err(
            'RSC v.%(version)s - %(obj_count)s classifier objects' % self.header
        )

    def dump(self):
        with open(self.args.obj_file, 'w+') as f:
            f.write(yaml.dump(self.objects_dict, allow_unicode=True))
        with open(self.args.sem_file, 'w+') as f:
            f.write(yaml.dump(self.semantics_dict, allow_unicode=True))
        with open(self.args.par_file, 'w+') as f:
            f.write(yaml.dump(self.parameters_dict, allow_unicode=True))

    def init_tables(self):
        # расположение таблицы цветов хранится в таблице таблиц
        self.filehandler.seek(self.header['tab_offset'], 0)
        raw = self.filehandler.read(self.header['tab_length'])
        idx = 0
        for i in xrange(self.header['tab_count']):
            (
                self.header['cmy_offset'], self.header['cmy_length'], self.header['cmy_count']
            ) = struct.unpack('<III', raw[idx:idx + 12])
            idx += 12

        self.TABLES = {}
        for prefix in RSC_TABLES:
            self.TABLES[prefix] = (
                self.header['%s_offset' % prefix],
                self.header['%s_length' % prefix],
                self.header['%s_count' % prefix],
            )

    def check_tables(self):
        for prefix in RSC_TABLES:
            offset, length, count = self.TABLES[prefix]

            self.filehandler.seek(offset - 4, 0)
            raw = self.filehandler.read(length + 4)

            table_prefix = struct.unpack('<4s', raw[0:4])[0]
            if ('%s\0' % prefix).upper() != table_prefix:
                err(
                    'Incorrect section prefix [%s] != [%s]\n' % (table_prefix, prefix)
                )
                self.corrupted_tables[prefix] = True
                # raise RuntimeError('Incorrect section prefix [%s] != [%s]' % (table_prefix, prefix))

    def get_table_data(self, prefix):
        offset, length, count = self.TABLES[prefix]
        self.filehandler.seek(offset, 0)
        raw = self.filehandler.read(length)
        return raw, offset, count

    def parse_header(self):
        # Назначение поля Смещение    Длина   Комментарий
        data = self.filehandler.read(328)
        raw = data2dict(RSC_FILE_HEADER_DESC, data)

        if raw['prefix'] != 'RSC\0':
            raise RuntimeError('Incorrect file begin signature')

        self.header = raw

    def parse_classifier_objects(self):
        """
        2.1.2 Структура таблицы объектов  классификатора
        Таблица объектов классификатора находится по смещению на таблицу объектов, имеет общую длину,
        указанную в заголовке классификатора.
        Перед таблицей объектов классификатора находится идентификатор таблицы “OBJ” (шестнадцатеричное число 0X004A424F)  (не входит в длину таблицы).
        Записи таблицы объектов переменной длины, не менее 112 байт. Одна запись на один объект классификатора.
        """
        fail = False
        for tbl in ('obj', 'pos',):
            fail = fail and tbl in self.corrupted_tables

        if fail:
            raise RuntimeError('Errors in one of classifier tables')

        classifiers2dict(self)

    def parse_semantics(self):
        fail = False
        for tbl in ('sem', 'cls', 'def', ):
            fail = fail and tbl in self.corrupted_tables

        if fail:
            raise RuntimeError('Errors in one of semantics tables')

        semantics2dict(self)

    def parse_segments(self):
        """
        2.1.7 Структура таблицы  слоев
        Таблица слоев классификатора находится по смещению на таблицу слоев. Имеет общую длину, указанную в заголовке классификатора.
        Перед таблицей слоев (сегментов) находится идентификатор таблицы “.SEG” (шестнадцатеричное число 0X00474553)  (не входит в длину таблицы).  Записи таблицы слоев (сегментов) переменной длины, более 60 байт.
        """
        raw, offset, count = self.get_table_data('seg')

    def parse_limits(self):
        """
        2.1.8 Структура таблицы  порогов
        Таблица порогов представляет собой двоичное описание серии объектов.
        Серия объектов это несколько объектов с одинаковым кодом, локализацией и семантикой. Серия предназначена для отображения объектов классификатора в тех случаях, когда объект должен менять внешний вид в зависимости от значений семантики (одной или двух). Описание каждого объекта серии лежит отдельно, а таблица порогов позволяет узнать, какой именно объект серии соответствует данному сочетанию значений семантических характеристик.
        Перед таблицей порогов находится идентификатор таблицы “.LIM” (шестнадцатеричное число 0X004D494C)  (не входит в длину таблицы).  Записи таблицы порогов переменной длины.
        """
        raw, offset, count = self.get_table_data('lim')

    def parse_parameters(self):
        """
        2.1.9 Структура таблиц параметров экрана и  печати
        Таблица параметров  классификатора находится по смещению на таблицу параметров.
        Имеет общую длину, указанную в заголовке классификатора.
        Перед таблицей параметров находится идентификатор таблицы “.PAR” (шестнадцатеричное число 0X00524150)  (не входит в длину таблицы).
        Записи таблицы параметров переменной длины, более 8 байт.
        Таблица параметров печати  классификатора находится по смещению на таблицу параметров печати.
        Имеет общую длину, указанную в заголовке классификатора.
        Перед таблицей параметров находится идентификатор таблицы “.PRN “(шестнадцатеричное число 0X004E5250)  (не входит в длину таблицы).
        Записи таблицы параметров переменной длины, более 8 байт.
        Таблицы имеют одинаковую структуру.
        Для каждого объекта классификатора обязательно есть экранные параметры, а параметров печати может не быть.
        При записи в файл длина записи выравнивается на 4.
        """
        parameters2dict(self)

    def parse_palettes(self):
        """
        2.1.10 Структура таблицы  палитр
        Таблица палитр классификатора находится по смещению на таблицу палитр. Имеет общую длину, указанную в заголовке классификатора.
        Перед таблицей палитр находится идентификатор таблицы “.PAL” (шестнадцатеричное число 0X004C4150)  (не входит в длину таблицы).  Записи таблицы палитр постоянной длины 1056 байт.
        """
        raw, offset, count = self.get_table_data('pal')

    def parse_fonts(self):
        """
        2.1.11 Структура таблицы  шрифтов
        Таблица шрифтов классификатора находится по смещению на таблицу шрифтов. Имеет общую длину, указанную в заголовке классификатора.
        Перед таблицей шрифтов находится идентификатор таблицы “.TXT” (шестнадцатеричное число 0X00545854)  (не входит в длину таблицы).  Записи таблицы шрифтов постоянной длины 72 байта.
        """
        raw, offset, count = self.get_table_data('txt')

    def parse_libraries(self):
        """
        2.1.12 Структура таблицы  библиотек
        Таблица библиотек классификатора находится по смещению на таблицу библиотек. Имеет общую длину, указанную в заголовке классификатора.
        Перед таблицей библиотек находится идентификатор таблицы “.IML” (шестнадцатеричное число 0X004C4D49)  (не входит в длину таблицы).  Записи таблицы библиотек постоянной длины 120 байт.
        """
        raw, offset, count = self.get_table_data('iml')

    def parse_semantic_images(self):
        """

        """
        raw, offset, count = self.get_table_data('grs')

    def parse_colors(self):
        """
        2.1.12 Структура таблицы  CMYK цветов для печати
        Таблица цветов для печати классификатора находится по смещению на таблицу цветов печати, указанную в таблице таблиц.
        Имеет общую длину, указанную в таблице таблиц классификатора.
        Перед таблицей цветов для печати находится идентификатор таблицы “.СMY” (шестнадцатеричное число 0X00594D43)  (не входит в длину таблицы).
        Записи таблицы цветов для печати постоянной длины 1024 байта.
        """
        raw, offset, count = self.get_table_data('cmy')

    def parse_table_tbl(self):
        """
        2.1.12 Структура таблицы  таблиц
        Таблица таблиц  классификатора находится по смещению на таблицу таблиц.
        Имеет общую длину, указанную в заголовке классификатора.
        Перед таблицей библиотек находится идентификатор таблицы “.TAB” (шестнадцатеричное число 0X00424154) (не входит в длину таблицы).
        Запись таблицы таблиц постоянной длины 72 байта.
        """
        raw, offset, count = self.get_table_data('tab')
