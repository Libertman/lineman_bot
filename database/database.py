from datetime import datetime
from dataclasses import dataclass


@dataclass
class Deadline:
    name: str
    deadline: datetime
    reminder: list[int] = [21600, 86400]


deadlines = {'Физическая культура':
             (Deadline(name='Аттестация по модулю: Основы теории физической культуры', deadline=datetime(2024, 10, 6)),
              Deadline(name='Аттестация по модулю: Медико-биологические основы физической культуры', deadline=datetime(2024, 10, 13)),
              Deadline(name='Аттестация по модулю: Самостоятельные занятия физическими упражнениями', deadline=datetime(2024, 10, 24)),
              Deadline(name='Аттестация по модулю: Физическая культура в профессиональной деятельности специалиста', deadline=datetime(2024, 10, 28)),
              Deadline(name='Аттестация по модулю: Спорт как социальное явление', deadline=datetime(2024, 11, 3)),
              Deadline(name='Аттестация по модулю: Физическая культура при различных заболеваниях', deadline=datetime(2024, 11, 5)),
              Deadline(name='Промежуточная аттестация', deadline=datetime(2024, 11, 15)),
              Deadline(name='Итоговый тест с прокторингом', deadline=datetime(2024, 11, 30))),
             'Экономическая культура':
             (Deadline(name='Основные экономические категории', deadline=datetime(2024, 9, 22)),
              Deadline(name='Финансы домашних хозяйств', deadline=datetime(2024, 9, 29)),
              Deadline(name='Сбережения и инвестиции физических лиц', deadline=datetime(2024, 10, 6)),
              Deadline(name='Пенсионные сбережения', deadline=datetime(2024, 10, 13)),
              Deadline(name='Инвестирование на фондовом рынке', deadline=datetime(2024, 10, 20)),
              Deadline(name='Платежи и расчеты', deadline=datetime(2024, 10, 27)),
              Deadline(name='Кредиты и займы', deadline=datetime(2024, 11, 3)),
              Deadline(name='Налогооблажение физических лиц', deadline=datetime(2024, 11, 10)),
              Deadline(name='Страхование рисков и профессиональной деятельности', deadline=datetime(2024, 11, 17)),
              Deadline(name='Организационные аспекты индивидуальной предпринимательской деятельности и самозанятости в РФ', deadline=datetime(2024, 11, 24)),
              Deadline(name='Практическая реализация предпринимательской идеи', deadline=datetime(2024, 12, 1)),
              Deadline(name='Итоговая аттестация', deadline=datetime(2024, 12, 8))),
             'Россия: государственное основание и мировоззрение':
             (Deadline(name='\n1. Что такое Россия\n2. Российское государство-цивилизация\n3. Российское мировоззрение и ценности российской цивилизации\n4. Политическое устройство России\n5. Вызовы будущего и развитие страны', deadline=datetime(2024, 11, 29), reminder=[21600, 86400, 604800]),
              Deadline(name='Амнистия', deadline=datetime(2024, 12, 20)),
              Deadline(name='Итоговая аттестация', deadline=datetime(2024, 12, 22, 9))),
             'Цифровая грамотность':
             (Deadline(name='\n1. Компьютерные системы и сети\n2. Интернет вещей\n3. Цифровая городская среда\n4. Финансовые технологии\n5. Основы информационной безопасности\n6. Цифровая гигиена\n7. Технологии виртуальной, дополненной и смешанной реальности\n8. Коммуникационная безопасность\nАмнистия\nИтоговая аттестация', deadline=datetime(2024, 12, 22), reminder=[21600, 86400, 604800])),
             'Английский язык':
             (Deadline(name='Тест по модулю 1', deadline=(2024, 10, 8)),
              Deadline(name='Монолог по модулю 1 "Personality"', deadline=(2024, 10, 15), reminder=[21600, 86400, 604800]))}
