# -*- coding: utf-8 -*-

import struct
from tools import split_bits

from rsc.classifiers import RscClassifierObject
from rsc.semantics import RscSemanticObject
from rsc.semantic_classifiers import RscSemanticClassifierObject
from rsc.semantic_defaults import RscSemanticDefaultsObject
from rsc.semantic_posibilities import RscSemanticPosibilitiesObject


class RSC(object):

    records = []

    @staticmethod
    def parse(data):
        rsc = RSC()
        raw = data.read(308)
        rsc.parse_header(raw)
        rsc.init_tables(data)

        rsc.check_tables(data)

        rsc.parse_tables(data)

        rsc.parse_classifier_objects(data)

        rsc.parse_semantics(data)
        rsc.parse_semantic_classifiers(data)
        rsc.parse_semantic_defaults(data)
        rsc.parse_semantic_images(data)
        rsc.parse_semantics_posibilities(data)

        rsc.parse_colors(data)
        rsc.parse_fonts(data)
        rsc.parse_libraries(data)
        rsc.parse_limits(data)
        rsc.parse_palettes(data)
        rsc.parse_parameters(data)
        rsc.parse_printing(data)
        rsc.parse_segments(data)

        rsc.info()
        return rsc

    def __init__(self):
        self.corrupted_tables = {}

    def info(self):
        print 'RSC v.%s - %s classifier objects' % (
            self.version,
            self.classifier_objects[2],
        )

    def check_tables(self, data):
        tables = [
            'OBJ\0',
            'SEM\0',
            'CLS\0',
            'DEF\0',
            'POS\0',
            'SEG\0',
            'LIM\0',
            'PAR\0',
            'PRN\0',
            'PAL\0',
            'TXT\0',
            'IML\0',
            'TAB\0',
            'CMY\0',
            # self.semantic_images
            # FNM
            # GRS
        ]

        for prefix in tables:
            offset, length, count = self.TABLES[prefix]

            data.seek(offset - 4, 0)
            raw = data.read(length + 4)

            table_prefix = struct.unpack('<4s', raw[0:4])[0]
            if prefix != table_prefix:
                print 'Incorrect section prefix [%s] != [%s]' % (table_prefix, prefix)
                self.corrupted_tables[prefix]
                # raise RuntimeError('Incorrect section prefix [%s] != [%s]' % (table_prefix, prefix))

    def get_table_data(self, prefix, data):
        offset, length, count = self.TABLES[prefix]
        data.seek(offset, 0)
        raw = data.read(length)
        return raw, count

    def init_tables(self, data):
        offset, length, count = self.tables
        data.seek(offset, 0)
        raw = data.read(length)
        idx = 0
        for i in xrange(count):
            self.cmyk_colors = struct.unpack('<III', raw[idx:idx + 12])
            idx += 12

        self.TABLES = {
            'OBJ\0': self.classifier_objects,
            'SEM\0': self.semantics,
            'CLS\0': self.semantic_classifiers,
            'DEF\0': self.semantic_defaults,
            'POS\0': self.semantics_posibilities,
            'SEG\0': self.segments,
            'LIM\0': self.limits,
            'PAR\0': self.parameters,
            'PRN\0': self.printing,
            'PAL\0': self.palettes,
            'TXT\0': self.fonts,
            'IML\0': self.libraries,
            # 'DEF\0': self.semantic_images,
            'TAB\0': self.tables,
            'CMY\0': self.cmyk_colors,
            # FNM
            # GRS
        }

    def parse_header(self, data):
        # Назначение поля Смещение    Длина   Комментарий
        # Идентификатор файла 0   4   0x00435352 (RSC)
        prefix = struct.unpack('<4s', data[0:4])[0]
        if prefix != 'RSC\0':
            raise RuntimeError('Incorrect file begin signature')

        # Длина файла 4   4   В байтах
        self.full_length = struct.unpack('<I', data[4:8])[0]

        # Версия структуры RSC    8   4   0x0700
        self.version = struct.unpack('<I', data[8:12])[0]

        # Кодировка   12  4   Для всего файла
        self.encoding = struct.unpack('<I', data[12:16])[0]

        # Номер состояния файла   16  4   Учет корректировок, требующих перегрузки данных
        self.state_number = struct.unpack('<I', data[16:20])[0]

        # Номер модификации состояния 20  4   Учет корректировок
        self.correction = struct.unpack('<I', data[20:24])[0]

        # Используемый язык   24  4   1-английский, 2-русский
        self.language = struct.unpack('<I', data[24:28])[0]

        # Максимальный идентификатор таблицы объектов 28  4   Идентификатор для нового объекта
        self.max_id = struct.unpack('<I', data[28:32])[0]

        # Дата создания файла 32  8   ГГГГММДД
        self.created_at = struct.unpack('<8s', data[32:40])[0]

        # Тип карты   40  32 символьное поле 32 байта
        # Тип карты/ Значение поля  не влияет на применение с картами других типов.
        # Возможные значения:
        # - не установлено;
        # - топографическая;
        # - обзорно-географическая;
        # - космонавигационная ("Глобус");
        # - топографический план города;
        # - крупномасштабный план местности;
        # - аэронавигационная;
        # - морская навигационная;
        # - авиационная
        self.map_type = struct.unpack('<32B', data[40:72])[0]

        # Условное название классификатора    72  32  ANSI
        self.name = struct.unpack('<32s', data[72:104])[0]

        # Код классификатора  104 8   ANSI
        self.header_len = struct.unpack('<8s', data[104:112])[0]

        # Масштаб карты   112 4   Базовый масштаб карты, на который составлен классификатор.
        # Значение поля не накладывает ограничений на применение с картами другого базового масштаба.
        self.scale = struct.unpack('<I', data[112:116])[0]

        # Масштабный ряд  116 4
        # Границы видимости объектов на карте задаются двумя списками масштабов - для мелкомасштабных карт и для крупномасштабных.
        # Для карт масштабов от 1:1 до 1:10000 целесообразно выбирать значение 1 - крупномасштабная, для остальных карт – 0- мелкомасштабная.
        # Для мелкомасштабных карт границы видимости объектов могут принимать значения:
        # - 1:1000, 1:2000, 1:5000, 1:10000, 1:25000, 1:50000, 1:100000, 1:200000, 1:500000,
        # - 1:1000000, 1:2500000, 1:5000000, 1:10000000, 1:20000000, 1:40000000.
        # Для крупномасштабных карт границы видимости объектов могут принимать значения:
        # - 1:1, 1:10, 1:25, 1:50, 1:100, 1:200, 1:500, 1:1000, 1:2000, 1:5000, 1:10000,
        # - 1:25000, 1:50000, 1:100000, 1:200000, 1:500000.
        self.scale_line = struct.unpack('<I', data[116:120])[0]

        # Смещение на таблицу объектов    120 4   От начала файла
        # Длина таблицы объектов  124 4   В байтах
        # Число записей   128 4   Записи переменной длины
        self.classifier_objects = struct.unpack('<III', data[120:132])

        # Смещение на таблицу семантики   132 4   От начала файла
        # Длина таблицы семантики 136 4   В байтах
        # Число записей   140 4   Записи постоянной длины
        self.semantics = struct.unpack('<III', data[132:144])

        # Смещение на таблицу классификатор семантики     144 4   От начала файла
        # Длина таблицы классификатор семантики   148 4   В байтах
        # Число записей   152 4   Записи постоянной длины
        self.semantic_classifiers = struct.unpack('<III', data[144:156])

        # Смещение на таблицу умолчаний   156 4   От начала файла
        # Длина таблицы умолчаний 160 4   В байтах
        # Число записей   164 4   Записи постоянной длины
        self.semantic_defaults = struct.unpack('<III', data[156:168])

        # Смещение на таблицу возможных семантик  168 4   От начала файла
        # Длина таблицы возможных семантик    152 4   В байтах
        # Число записей   156 4   Записи переменной длины
        self.semantics_posibilities = struct.unpack('<III', data[168:180])

        # Смещение на таблицу сегментов (слоев)   160 4   От начала файла
        # Длина таблицы сегментов (слоев) 164 4   В байтах
        # Число записей   168 4   Записи переменной длины
        self.segments = struct.unpack('<III', data[180:192])

        # Смещение на таблицу Порогов 172 4   От начала файла
        # Длина таблицы порогов   176 4   В байтах
        # Число записей   180 4   Записи переменной длины
        self.limits = struct.unpack('<III', data[192:204])

        # Смещение на таблицу параметров  184 4   От начала файла
        # Длина таблицы параметров    188 4   В байтах
        # Число записей   192 4   Записи переменной длины
        self.parameters = struct.unpack('<III', data[204:216])

        # Смещение на таблицу параметров печати   196 4   От начала файла
        # Длина таблицы параметров печати 200 4   В байтах
        # Число записей   204 4   Записи переменной длины
        self.printing = struct.unpack('<III', data[216:228])

        # Смещение на таблицу палитр  208 4   От начала файла
        # Длина таблицы палитр    212 4   В байтах
        # Число записей   216 4   Записи постоянной длины
        self.palettes = struct.unpack('<III', data[228:240])

        # Смещение на таблицу шрифтов 220 4   От начала файла
        # Длина таблицы шрифтов   224 4   В байтах
        # Число записей   228 4   Записи постоянной длины
        self.fonts = struct.unpack('<III', data[240:252])

        # Смещение на таблицу библиотек   232 4   От начала файла
        # Длина таблицы библиотек 236 4   В байтах
        # Число записей   240 4   Записи постоянной длины
        self.libraries = struct.unpack('<III', data[252:264])

        # Смещение на таблицу изображений семантики   244 4   От начала файла
        # Длина таблицы изображений семантики 248 4   В байтах
        # Число записей   252 4   Записи постоянной длины
        self.semantic_images = struct.unpack('<III', data[264:276])

        # Смещение на таблицу таблиц  256 4   От начала файла
        # Длина таблицы таблиц    260 4   В байтах
        # Число записей   264 4   Записи постоянной длины
        self.tables = struct.unpack('<III', data[276:288])

        # Флаг использования ключей как кодов 268 1
        self.keys_as_codes = struct.unpack('<B', data[288:289])[0]

        # Флаг модификации палитры    269 1   Учет корректировок
        self.palettes_modifications = struct.unpack('<B', data[289:290])[0]

        # Резерв  270 2   0
        # Резерв  272 4   Не использовать
        # Резерв  276 4   Не использовать
        # Резерв  280 20  0

        # Кодировка шрифтов   300 4
        # 125 - строка (KOI8), ограниченная нулем;
        # 126 - строка (ANSI, WINDOWS), ограниченная нулем.
        self.fonts_encoding = struct.unpack('<I', data[300:304])[0]

        # Количество цветов в палитрах    304 4   Не более 256, одинаково для всех палитр
        self.palettes_clolors = struct.unpack('<I', data[304:308])[0]
        # ИТОГО:  308 байт

    def parse_classifier_objects(self, data):
        """
        2.1.2 Структура таблицы объектов  классификатора
        Таблица объектов классификатора находится по смещению на таблицу объектов, имеет общую длину,
        указанную в заголовке классификатора.
        Перед таблицей объектов классификатора находится идентификатор таблицы “OBJ” (шестнадцатеричное число 0X004A424F)  (не входит в длину таблицы).
        Записи таблицы объектов переменной длины, не менее 112 байт. Одна запись на один объект классификатора.
        """
        if 'OBJ\0' in self.corrupted_tables:
            return
        
        raw, count = self.get_table_data('OBJ\0', data)

        idx = 0
        for i in xrange(count):
            record_length = struct.unpack('<I', raw[idx:idx + 4])[0]
            record_raw = raw[idx:idx + record_length]
            idx += record_length

            record = RscClassifierObject.parse(record_raw)
            record.info()
            # self.records.append(record)

    def parse_semantics(self, data):
        """
        2.1.3 Структура таблицы семантик классификатора
        Таблица семантик классификатора находится по смещению на таблицу семантик,
        имеет общую длину, указанную в заголовке классификатора.
        Перед таблицей семантик классификатора находится идентификатор таблицы “.SEM” (шестнадцатеричное число 0X004D4553)
        (не входит в длину таблицы). Записи таблицы семантики постоянной длины, 84 байт.
        Одна запись на одну семантику классификатора.
        """
        if 'SEM\0' in self.corrupted_tables:
            return
        
        raw, count = self.get_table_data('SEM\0', data)

        idx = 0
        for i in xrange(count):
            record = RscSemanticObject.parse(raw[idx:idx + 84])
            record.info()
            idx += 84

    def parse_semantic_classifiers(self, data):
        """
        2.1.4 Структура таблицы  классификатора значений семантики
        Для каждой семантической характеристики может быть создан классификатор значений.
        При этом для числовых характеристик одному коду обычно соответствует диапазон значений (например, ширина реки: до 5м - 1, от 5 до 10 - 2 и т.д.),
        для символьных характеристик одному коду соответствует одно значение (материал строения: дерево - 1, кирпич - 2 и т.д.).
        Если для характеристики создается классификатор значений, то в таблице семантики она объявляется числовой
        (физически ее значение - числовой код, но при работе с этой характеристикой в системе электронных карт будет отображаться логическое значение, соответствующее текущему коду).
        Записи классификатора значений относящиеся к конкретной семантике лежат в таблице подряд.
        Таблица классификатора значений семантики находится по смещению на таблицу классификатора значений семантики.
        Имеет общую длину, указанную в заголовке классификатора.
        Перед таблицей классификатора значений семантики находится идентификатор таблицы “.CLS” (шестнадцатеричное число 0X00534С43)
        (не входит в длину таблицы). Записи таблицы классификатора значений семантики постоянной длины, 36 байт.
        Количество записей на одну семантику классификатора указывается в таблице семантики.
        Смещение на записи классификатора значений для конкретной семантики, указываются в таблице семантики.
        """
        if 'CLS\0' in self.corrupted_tables:
            return
        
        raw, count = self.get_table_data('CLS\0', data)

        idx = 0
        for i in xrange(count):
            record = RscSemanticClassifierObject.parse(raw[idx:idx + 36])
            record.info()
            idx += 36

    def parse_semantic_defaults(self, data):
        """
        2.1.5 Структура таблицы  умалчиваемых значений семантики
        Каждой семантической характеристике с числовым значением (в том числе и классификатором значений) можно назначить максимальное, минимальное и умалчиваемое значение. Для каждой возможной семантики отдельного объекта тоже можно назначить максимальное, минимальное и умалчиваемое значение семантики для данного объекта классификатора.   Все эти значения лежат в одной таблице.    Записи умалчиваемых значений  относящиеся к конкретной семантике лежат в таблице подряд.
        Таблица умалчиваемых значений семантики находится по смещению на таблицу умолчаний семантики.
        Имеет общую длину, указанную в заголовке классификатора.
        Перед таблицей умалчиваемых значений семантики находится идентификатор таблицы “.DEF” (шестнадцатеричное число 0X00464544)
        (не входит в длину таблицы).
        Записи таблицы умалчиваемых значений семантики постоянной длины, 32 байта. Количество записей на одну семантику классификатора указывается в таблице семантики. Смещение на записи умалчиваемых значений для конкретной семантики, указываются в таблице семантики.
        """
        if 'DEF\0' in self.corrupted_tables:
            return
        
        raw, count = self.get_table_data('DEF\0', data)

        idx = 0
        for i in xrange(count):
            record = RscSemanticDefaultsObject.parse(raw[idx:idx + 32])
            record.info()
            idx += 32

    def parse_semantics_posibilities(self, data):
        """
        2.1.6 Структура таблицы  возможных  семантик объекта
        Для каждого объекта классификатора пользователь может назначить обязательную или возможную семантику. Если семантика возможная, заполнение ее при нанесении объекта на карту не обязательно. Если пользователь не заполнит значение обязательной семантики объекта, семантика будет записана с умалчиваемым значением.
        Все объекты серии имеют одну запись в таблице возможных семантик.
        Перед таблицей возможных семантик объекта находится идентификатор таблицы “.POS” (шестнадцатеричное число 0X00534F50)  (не входит в длину таблицы).  Записи таблицы умалчиваемых значений семантики переменной длины, более 20 байт.
        """
        if 'POS\0' in self.corrupted_tables:
            return
        
        raw, count = self.get_table_data('POS\0', data)

        idx = 0
        for i in xrange(count):
            record_length = struct.unpack('<I', raw[idx:idx + 4])[0]
            record_raw = raw[idx:idx + record_length]
            idx += record_length

            record = RscSemanticPosibilitiesObject.parse(record_raw)
            record.info()

    def parse_segments(self, data):
        """
        2.1.7 Структура таблицы  слоев
        Таблица слоев классификатора находится по смещению на таблицу слоев. Имеет общую длину, указанную в заголовке классификатора.
        Перед таблицей слоев (сегментов) находится идентификатор таблицы “.SEG” (шестнадцатеричное число 0X00474553)  (не входит в длину таблицы).  Записи таблицы слоев (сегментов) переменной длины, более 60 байт.
        """
        offset, length, count = self.segments
        data.seek(offset - 4, 0)
        raw = data.read(length + 4)

        prefix = struct.unpack('<4s', raw[0:4])[0]
        if prefix != 'SEG\0':
            raise RuntimeError('Incorrect segments section prefix [%s]' % prefix)

    def parse_limits(self, data):
        """
        2.1.8 Структура таблицы  порогов
        Таблица порогов представляет собой двоичное описание серии объектов.
        Серия объектов это несколько объектов с одинаковым кодом, локализацией и семантикой. Серия предназначена для отображения объектов классификатора в тех случаях, когда объект должен менять внешний вид в зависимости от значений семантики (одной или двух). Описание каждого объекта серии лежит отдельно, а таблица порогов позволяет узнать, какой именно объект серии соответствует данному сочетанию значений семантических характеристик.
        Перед таблицей порогов находится идентификатор таблицы “.LIM” (шестнадцатеричное число 0X004D494C)  (не входит в длину таблицы).  Записи таблицы порогов переменной длины.
        """
        offset, length, count = self.limits
        data.seek(offset - 4, 0)
        raw = data.read(length + 4)

        prefix = struct.unpack('<4s', raw[0:4])[0]
        if prefix != 'LIM\0':
            raise RuntimeError('Incorrect limits section prefix [%s]' % prefix)

    def parse_parameters(self, data):
        """
        2.1.9 Структура таблиц параметров экрана и  печати
        Таблица параметров  классификатора находится по смещению на таблицу параметров. Имеет общую длину, указанную в заголовке классификатора.
        Перед таблицей параметров находится идентификатор таблицы “.PAR” (шестнадцатеричное число 0X00524150)  (не входит в длину таблицы).  Записи таблицы параметров переменной длины, более 8 байт.
        """
        offset, length, count = self.parameters
        data.seek(offset - 4, 0)
        raw = data.read(length + 4)

        prefix = struct.unpack('<4s', raw[0:4])[0]
        if prefix != 'PAR\0':
            raise RuntimeError('Incorrect parameters section prefix [%s]' % prefix)

    def parse_printing(self, data):
        """
        Таблица параметров печати  классификатора находится по смещению на таблицу параметров печати. Имеет общую длину, указанную в заголовке классификатора.
        Перед таблицей параметров находится идентификатор таблицы “.PRN “(шестнадцатеричное число 0X004E5250)  (не входит в длину таблицы).  Записи таблицы параметров переменной длины, более 8 байт.  Таблицы имеют одинаковую структуру.
        Для каждого объекта классификатора обязательно есть экранные параметры, а параметров печати может не быть. При записи в файл длина записи выравнивается на 4.
        """
        offset, length, count = self.printing
        data.seek(offset - 4, 0)
        raw = data.read(length + 4)

        prefix = struct.unpack('<4s', raw[0:4])[0]
        if prefix != 'PRN\0':
            raise RuntimeError('Incorrect printing parameters section prefix [%s]' % prefix)

    def parse_palettes(self, data):
        """
        2.1.10 Структура таблицы  палитр
        Таблица палитр классификатора находится по смещению на таблицу палитр. Имеет общую длину, указанную в заголовке классификатора.
        Перед таблицей палитр находится идентификатор таблицы “.PAL” (шестнадцатеричное число 0X004C4150)  (не входит в длину таблицы).  Записи таблицы палитр постоянной длины 1056 байт.
        """
        offset, length, count = self.palettes
        data.seek(offset - 4, 0)
        raw = data.read(length + 4)

        prefix = struct.unpack('<4s', raw[0:4])[0]
        if prefix != 'PAL\0':
            raise RuntimeError('Incorrect palettes section prefix [%s]' % prefix)

    def parse_fonts(self, data):
        """
        2.1.11 Структура таблицы  шрифтов
        Таблица шрифтов классификатора находится по смещению на таблицу шрифтов. Имеет общую длину, указанную в заголовке классификатора.
        Перед таблицей шрифтов находится идентификатор таблицы “.TXT” (шестнадцатеричное число 0X00545854)  (не входит в длину таблицы).  Записи таблицы шрифтов постоянной длины 72 байта.
        """
        offset, length, count = self.fonts
        data.seek(offset - 4, 0)
        raw = data.read(length + 4)

        prefix = struct.unpack('<4s', raw[0:4])[0]
        if prefix != 'TXT\0':
            raise RuntimeError('Incorrect fonts section prefix [%s]' % prefix)

    def parse_libraries(self, data):
        """
        2.1.12 Структура таблицы  библиотек
        Таблица библиотек классификатора находится по смещению на таблицу библиотек. Имеет общую длину, указанную в заголовке классификатора.
        Перед таблицей библиотек находится идентификатор таблицы “.IML” (шестнадцатеричное число 0X004C4D49)  (не входит в длину таблицы).  Записи таблицы библиотек постоянной длины 120 байт.
        """
        offset, length, count = self.libraries
        data.seek(offset - 4, 0)
        raw = data.read(length + 4)

        prefix = struct.unpack('<4s', raw[0:4])[0]
        if prefix != 'IML\0':
            raise RuntimeError('Incorrect libraries section prefix [%s]' % prefix)

    def parse_semantic_images(self, data):
        """

        """
        offset, length, count = self.semantic_images
        if not (length and count):
            print 'Empty semantic images section'
            return
        data.seek(offset - 4, 0)
        raw = data.read(length + 4)

        prefix = struct.unpack('<4s', raw[0:4])[0]
        if prefix != 'DEF\0':
            raise RuntimeError('Incorrect images section prefix [%s]' % prefix)

    def parse_tables(self, data):
        """
        2.1.12 Структура таблицы  таблиц
        Таблица таблиц  классификатора находится по смещению на таблицу таблиц. Имеет общую длину, указанную в заголовке классификатора.
        Перед таблицей библиотек находится идентификатор таблицы “.TAB” (шестнадцатеричное число 0X00424154) (не входит в длину таблицы).
        Запись таблицы таблиц постоянной длины 72 байта.
        """
        if 'TAB\0' in self.corrupted_tables:
            return
        
        raw, count = self.get_table_data('TAB\0', data)

        if count > 1:
            print 'Incorrtct tables data'

        idx = 0
        for i in xrange(count):
            self.cmyk_colors = struct.unpack('<III', raw[idx:idx + 12])
            idx += 12
            # reserved = struct.unpack('<60B', raw[idx + 12:idx + 72])

    def parse_colors(self, data):
        """
        2.1.12 Структура таблицы  CMYK цветов для печати
        Таблица цветов для печати классификатора находится по смещению на таблицу цветов печати, указанную в таблице таблиц. Имеет общую длину, указанную в таблице таблиц классификатора.
        Перед таблицей цветов для печати находится идентификатор таблицы “.СMY” (шестнадцатеричное число 0X00594D43)  (не входит в длину таблицы).  Записи таблицы цветов для печати постоянной длины 1024 байта.
        """
        offset, length, count = self.cmyk_colors
        data.seek(offset - 4, 0)
        raw = data.read(length + 4)

        prefix = struct.unpack('<4s', raw[0:4])[0]
        if prefix != 'CMY\0':
            raise RuntimeError('Incorrect CMYC colors section prefix [%s]' % prefix)
