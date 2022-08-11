# Шахматы
Проект Шахматы с уникальными фигурами (мной и моим знакомым)
Этот проект я выполнял в рамках программы обучения в Финансовом Университете. В разработке использовано множество библиотек, вот их перечень<br>
• subprocess (Для запуска обучающих видео, если игрок желает ознакомиться с правилами)<br>
• os (Для просмотра содержимого директории)<br>
• functools.reduce (Для объединения подмассивов с координатами шахмат)<br>
• tkinter (Графический модуль - основа всего проекта)<br>
• datetime (Расчёт времени)<br>
• random (Модуль для генерации рандомных чисел. Нужен для уникальной фигуры, появляющейся на случайно клетке поля)<br>
• pygame (Для симуляции звуков)<br>

**Концепция игры**<br>
Всё, как не странно, построено вокруг ООП<br>
Каждая клетка поля - отдельный класс Button, имеющий доп.атрибуты как цвет и figure<br>
В figure хранится объект фигуры, который я также разработал для каждой роли отдельно: ладьи, ферзя, короля и т.д<br>
При нажатии на фигуру, которая может сейчас ходить, на поле подсвечиваются подсказки с возможными ходами<br>
Также подсвечиваются фигуры, которые находятся под угрозой противника

**Возможности**<br>
• Загрузка/Сохранение игры<br>
• Просмотр обучающих видеороликов прямо через приложение<br>
• Откат ходов и их возобновление<br>
• Запуск режима "Шашки"<br>
• История ходов в панели справа<br>

**Недостатки**<br>
В этом проекте я не реализовал все правила игры в шахматы просто потому, что их не знаю :)
