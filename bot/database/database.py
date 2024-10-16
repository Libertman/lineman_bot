from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field


@dataclass
class Deadline:
    name: str
    deadline: datetime
    subject: str = field(default_factory=str)
    reminder: list[int] = field(default_factory=list)


deadlines = {'Физическая культура':
             [Deadline(name='Аттестация по модулю: Основы теории физической культуры', deadline=datetime(2024, 10, 6, tzinfo=timezone(timedelta(hours=3))), subject='Физическая культура'),
              Deadline(name='Аттестация по модулю: Медико-биологические основы физической культуры', deadline=datetime(2024, 10, 13, tzinfo=timezone(timedelta(hours=3))), subject='Физическая культура'),
              Deadline(name='Аттестация по модулю: Самостоятельные занятия физическими упражнениями', deadline=datetime(2024, 10, 24, tzinfo=timezone(timedelta(hours=3))), subject='Физическая культура'),
              Deadline(name='Аттестация по модулю: Физическая культура в профессиональной деятельности специалиста', deadline=datetime(2024, 10, 28, tzinfo=timezone(timedelta(hours=3))), subject='Физическая культура'),
              Deadline(name='Аттестация по модулю: Спорт как социальное явление', deadline=datetime(2024, 11, 3, tzinfo=timezone(timedelta(hours=3))), subject='Физическая культура'),
              Deadline(name='Аттестация по модулю: Физическая культура при различных заболеваниях', deadline=datetime(2024, 11, 5, tzinfo=timezone(timedelta(hours=3))), subject='Физическая культура'),
              Deadline(name='Промежуточная аттестация', deadline=datetime(2024, 11, 15, tzinfo=timezone(timedelta(hours=3))), subject='Физическая культура'),
              Deadline(name='Итоговый тест с прокторингом', deadline=datetime(2024, 11, 30, tzinfo=timezone(timedelta(hours=3))), subject='Физическая культура')],
             'Экономическая культура':
             [Deadline(name='Основные экономические категории', deadline=datetime(2024, 9, 22, tzinfo=timezone(timedelta(hours=3))), subject='Экономическая культура'),
              Deadline(name='Финансы домашних хозяйств', deadline=datetime(2024, 9, 29, tzinfo=timezone(timedelta(hours=3))), subject='Экономическая культура'),
              Deadline(name='Сбережения и инвестиции физических лиц', deadline=datetime(2024, 10, 6, tzinfo=timezone(timedelta(hours=3))), subject='Экономическая культура'),
              Deadline(name='Пенсионные сбережения', deadline=datetime(2024, 10, 13, tzinfo=timezone(timedelta(hours=3))), subject='Экономическая культура'),
              Deadline(name='Инвестирование на фондовом рынке', deadline=datetime(2024, 10, 20, tzinfo=timezone(timedelta(hours=3))), subject='Экономическая культура'),
              Deadline(name='Платежи и расчеты', deadline=datetime(2024, 10, 27, tzinfo=timezone(timedelta(hours=3))), subject='Экономическая культура'),
              Deadline(name='Кредиты и займы', deadline=datetime(2024, 11, 3, tzinfo=timezone(timedelta(hours=3))), subject='Экономическая культура'),
              Deadline(name='Налогооблажение физических лиц', deadline=datetime(2024, 11, 10, tzinfo=timezone(timedelta(hours=3))), subject='Экономическая культура'),
              Deadline(name='Страхование рисков и профессиональной деятельности', deadline=datetime(2024, 11, 17, tzinfo=timezone(timedelta(hours=3))), subject='Экономическая культура'),
              Deadline(name='Организационные аспекты индивидуальной предпринимательской деятельности и самозанятости в РФ', deadline=datetime(2024, 11, 24, tzinfo=timezone(timedelta(hours=3))), subject='Экономическая культура'),
              Deadline(name='Практическая реализация предпринимательской идеи', deadline=datetime(2024, 12, 1, tzinfo=timezone(timedelta(hours=3))), subject='Экономическая культура'),
              Deadline(name='Итоговая аттестация', deadline=datetime(2024, 12, 8, tzinfo=timezone(timedelta(hours=3))), subject='Экономическая культура')],
             'Россия: государственное основание и мировоззрение':
             [Deadline(name='\n1. Что такое Россия\n2. Российское государство-цивилизация\n3. Российское мировоззрение и ценности российской цивилизации\n4. Политическое устройство России\n5. Вызовы будущего и развитие страны', deadline=datetime(2024, 11, 29, tzinfo=timezone(timedelta(hours=3))), reminder=[280800, 626400], subject='Россия: государственное основание и мировоззрение'),
              Deadline(name='Амнистия', deadline=datetime(2024, 12, 20, tzinfo=timezone(timedelta(hours=3))), subject='Россия: государственное основание и мировоззрение'),
              Deadline(name='Итоговая аттестация', deadline=datetime(2024, 12, 22, tzinfo=timezone(timedelta(hours=3))), subject='Россия: государственное основание и мировоззрение')],
             'Цифровая грамотность':
             [Deadline(name='\n1. Компьютерные системы и сети\n2. Интернет вещей\n3. Цифровая городская среда\n4. Финансовые технологии\n5. Основы информационной безопасности\n6. Цифровая гигиена\n7. Технологии виртуальной, дополненной и смешанной реальности\n8. Коммуникационная безопасность\n9. Амнистия\n10. Итоговая аттестация', deadline=datetime(2024, 12, 22, tzinfo=timezone(timedelta(hours=3))), reminder=[280800], subject='Цифровая грамотность')],
             'Английский язык':
             [Deadline(name='Тест по модулю 1', deadline=datetime(2024, 10, 8, tzinfo=timezone(timedelta(hours=3))), subject='Английский язык'),
              Deadline(name='Монолог по модулю 1 "Personality"', deadline=datetime(2024, 10, 15, tzinfo=timezone(timedelta(hours=3))), reminder=[280800], subject='Английский язык'),
              Deadline(name='Тест по модулю 2', deadline=datetime(2024, 10, 22, tzinfo=timezone(timedelta(hours=3))), subject='Английский язык'),
              Deadline(name='Монолог по модулю 2 "Travel"', deadline=datetime(2024, 11, 6, tzinfo=timezone(timedelta(hours=3))), subject='Английский язык')]}
