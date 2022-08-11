import subprocess # <--- Модуль для запуска обучающих видео
import traceback # <--- Модуль для корректного вывода исключения Try...Except
from os import listdir, remove # <--- Модуль для считывания .mp4 файлов(и не только) с директории
from functools import reduce #Функция нужна для объединения всех подмассивов с координатами в один массив одной строчкой
from tkinter import * # <--- Тут говорить не о чем, ТКИНТЕР ЕСТЬ ТКИНТЕР!
import datetime # <--- Модуль для расчёта времени
from random import * #Рандом
import contextlib
import time as vremya#Время
import pickle # <-- Pickle для сохранения истории в .txt файл
from figures import *
with contextlib.redirect_stdout(None): # <--- Выключает приветственное сообщение pygame в консоли при запуске программы (чтоб не засорять консоль)
    from pygame import mixer
mixer.init();
root = Tk()

#=============================================| Выполненные задания |===============================================#
#Задание №5 - 1 балл | Задание №6 - 1 балл | Задание №7 - 1 балл | Задание №8 - 1 балл

#===================| КЛАСС BUTTON, НАСЛЕДУЕМЫЙ ОТ TKINTER.BUTTON, ТОЛЬКО УСОВЕРШЕНСТВОВАННЫЙ |=====================#
#Переопределяем кнопку TKinter, добавляя к ней авторские полезные функции, которые облегчают процесс реализации ходов
class Button(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._figure = Figure()

    @property
    def figure(self):
        return self._figure

    @figure.setter
    def figure(self, figure):
        self._figure = figure
        self.configure(image=self._figure._image)

    @figure.deleter
    def figure(self):
        global buttons
        self.configure(image=null_png)
        self._figure = Figure()

    


#======================================| ОБЪЯВЛЕНИЕ ФУНКЦИЙ-АЛГОРИТМОВ |=============================================#
def check_the_cells_for_other_figures(from_pos, to_pos, diagonal_cells=[]):
    global buttons
    #Берём минимальную цифру и максимальную, чтобы циклом фор пройтись по всем горизонтальным клеткам между ними
    min_digit, max_digit = min( int(from_pos[1]), int(to_pos[1]) ), max( int(from_pos[1]), int(to_pos[1]) )
    coords = []
    #Если буквы начальной и конечной позиций одинаковы. Проще говоря - если фигура идёт по вертикали (вверх или вниз)
    if from_pos[0] == to_pos[0]:
        if all( not(buttons[i].figure.role) for i in [from_pos[0]+str(i) for i in range( min_digit+1, max_digit )] ):
            if isinstance(buttons[to_pos], (Pawn, Rook, Queen, Horse, Elephant, Nikita, Ramazan, Nord)):
                if buttons[to_pos].figure.color != buttons[from_pos].figure.color:
                    return True
            else:
                return True
        return False

    #Если цифры начальной и конечной позиций совпадают. Проще говоря - если фигура идёт по горизонтали (влево или вправо)
    elif from_pos[1] == to_pos[1]:
        if all( not(buttons[i].figure.role) for i in [ chr(j)+from_pos[1] for j in range( min(ord(from_pos[0]), ord(to_pos[0]))+1, max(ord(from_pos[0]), ord(to_pos[0])) ) ] ):
            if isinstance(buttons[to_pos], (Pawn, Rook, Queen, Horse, Elephant, Nikita, Ramazan, Nord)):
                if buttons[to_pos].figure.color != buttons[from_pos].figure.color:
                    return True
            else:
                return True
        return False

    #Если фигура идёт ВВЕРХ ВПРАВО по горизонтали
    elif to_pos[1] > from_pos[1] and to_pos[0] > from_pos[0]:
        coords = [ coord for coord in diagonal_cells if coord[1] > from_pos[1] and coord[0] > from_pos[0] and int(coord[1]) in range(min_digit+1, max_digit) ]
    
    #Если фигура идёт ВВЕРХ ВЛЕВО по горизонтали
    elif to_pos[1] > from_pos[1] and to_pos[0] < from_pos[0]:
        coords = [ coord for coord in diagonal_cells if coord[1] > from_pos[1] and coord[0] < from_pos[0] and int(coord[1]) in range(min_digit+1, max_digit) ]
    
    #Если фигура идёт ВНИЗ ВПРАВО по горизонтали
    elif to_pos[1] < from_pos[1] and to_pos[0] > from_pos[0]:
        coords = [ coord for coord in diagonal_cells if coord[1] < from_pos[1] and coord[0] > from_pos[0] and int(coord[1]) in range(min_digit+1, max_digit) ]
    
    #Если фигура идёт ВНИЗ ВЛЕВО по горизонтали
    elif to_pos[1] < from_pos[1] and to_pos[0] < from_pos[0]:
        coords = [ coord for coord in diagonal_cells if coord[1] < from_pos[1] and coord[0] < from_pos[0] and int(coord[1]) in range(min_digit+1, max_digit) ]
    
    #Возвращается конечный результат, который либо даст фигуре разрешение пойти, либо запретит
    return all( not(buttons[coord].figure.role) for coord in coords )


def even(list):
    return [list[cell] for cell in range(1, len(list), 2)] #<--- Возвращаем каждую вторую клетку, нужно для фигуры Рамазана


'''make_step принимает на вход координаты двух клеток - начальной и конечной. 
Фигура из начальной клетки перемещается на конечную и делает проверку: Если была съедена вражеская фигура - обновляется статистика'''
def make_step(from_pos, to_pos, time_from_log=False, taking_on_pass=False, checker_eat=False):
    global del_history, binary_history, eaten_figures, white_nord_status, black_nord_status

    #СЛЕДУЮЩИЕ СТРОЧКИ ГЕНЕРИРУЮТ ОПИСАНИЕ ХОДА И ДОБАВЛЯЮТ ЕГО В ДВУМЕРНЫЙ МАССИВ, КОТОРЫЕ ДАЛЕЕ МОЖЕТ БЫТЬ СОХРАНЁН В БИНАРНЫЙ ФАЙЛ
    binary_history.append([0, 0, False, ''])
    nord_spawn = True
    figures = {'rook': 'Ладья', 'pawn': 'Пешка', 'king': 'Король', 'queen': 'Ферзь', 'horse': 'Конь', 'elephant': 'Слон', 'ramazan': 'Рамазан', 'nikita': 'Никита', 'nord': 'Норд', 'checker': 'Шашка'}
    color = 'белого' if buttons[from_pos].figure.color == 'white' else 'чёрного'
    # print(f'Ход: {from_pos} --> {to_pos}  |  Фигура: { figures[buttons[from_pos].figure.role] } {color} цвета')
    time = datetime.datetime.now(); hour, minute, second = time.hour, time.minute, '0'+str(time.second) if len(str(time.second)) == 1 else time.second
    
    if time_from_log:
        log_message = f' {time_from_log}   {from_pos} --> {to_pos}  | { figures[buttons[from_pos].figure.role] } {color} цвета'
        binary_history[-1][3] = f'{time_from_log}'
        nord_spawn = False
    else:
        log_message = f' [{hour}:{minute}:{second}]   {from_pos} --> {to_pos}  | { figures[buttons[from_pos].figure.role] } {color} цвета'
        binary_history[-1][3] = f'[{hour}:{minute}:{second}]'
        del_history = []
        back_button.configure(state=DISABLED)
    log_window.insert(END, log_message)
    log_window.itemconfig(END, fg='black')
    binary_history[-1][2] = str(buttons[to_pos].figure.color)+'_'+str(buttons[to_pos].figure.role)
    binary_history[-1][1] = buttons[from_pos].figure.color+'_'+buttons[from_pos].figure.role
    binary_history[-1][0] = f'{from_pos}-->{to_pos}'

    if buttons[to_pos].figure.role != False:
        eaten_figures[ buttons[to_pos].figure.color ].append( buttons[to_pos].figure )
        if isinstance(buttons[to_pos].figure, Nord):
            if buttons[to_pos].figure.color == 'white':
                white_nord_status = False
                blow_up_the_white_nord.place_forget()
            else:
                blow_up_the_black_nord.place_forget()
    
    #Перемещение фигур
    buttons[to_pos].figure = buttons[from_pos].figure
    del buttons[from_pos].figure

    if checker_eat:
        binary_history[-1][2] = checker_eat

    #Если было совершено взятие на проходе - пожираем фигуру врага
    if taking_on_pass:
        taking_pos = [ to_pos[0]+str(int(to_pos[1])-1) , to_pos[0]+str(int(to_pos[1])+1) ][ buttons[from_pos].figure.color == 'white' ]
        binary_history[-1][2] = str(buttons[taking_pos].figure.color)+'_'+str(buttons[taking_pos].figure.role)
        binary_history[-1][0] += f',{taking_pos}'
        del buttons[ taking_pos ].figure

    #Включается звук хода. Увеличивается количество шагов у фигуры
    step_sound.play(); buttons[to_pos].figure.step += 1

    #Стираем подксказки для уже совершённого хода
    for coord in buttons:
        if isinstance(buttons[coord].figure, (Pawn, Rook, Queen, King, Elephant, Horse, Nikita, Ramazan, Nord, Checker)):
            buttons[coord].configure( image=buttons[coord].figure._image )
        else:
            buttons[coord].configure( image=null_png )

    #Проверяем: если съедено 3 фигуры - генерируем опасную машину-убийцу Норда
    eaten_count = len(eaten_figures[ ['white', 'black'][buttons[to_pos].figure.color == 'white'] ]);
    if eaten_count % 5 == 0 and eaten_count and binary_history[-1][2] != 'False_False' and nord_spawn:
        while True:
            random_coord_for_nord = choice('ABCDEFGH')+str(randint(1, 8))
            if buttons[random_coord_for_nord].figure.role == False:
                if buttons[to_pos].figure.color == 'white' and not(white_nord_status):
                    buttons[random_coord_for_nord].figure = Nord('white')
                    blow_up_the_white_nord.place(x=300, y=680, width=75, height=75)
                    white_nord_status = random_coord_for_nord
                elif buttons[to_pos].figure.color == 'black' and not(black_nord_status):
                    buttons[random_coord_for_nord].figure = Nord('black')
                    blow_up_the_black_nord.place(x=300, y=150, width=75, height=75)
                    black_nord_status = random_coord_for_nord
                binary_history[-1].append(random_coord_for_nord) 
                break

    if len(binary_history) >= 1:
        undo_button.configure(state=NORMAL)



#Название функции говорит само за себя: оно подсказывает (подсвечивает) те клетки, на которые может пойти выбранная на данный момент фигура
def show_available_cells(role, from_pos, check=False):
    global buttons, turn
    try:
        def GO(vectors, is_ramazan=False):
            for available_cells in vectors:
                for coord in available_cells:
                    if is_ramazan:
                        if not(buttons[coord].figure.role):
                            buttons[coord].configure( image=[null_png_attack, null_png][check] )
                        elif buttons[coord].figure.role != 'king' and buttons[coord].figure.color != buttons[from_pos].figure.color:
                            buttons[coord].configure( image=buttons[coord].figure._image_attack )
                    else:
                        if not(buttons[coord].figure.role):
                            buttons[coord].configure( image=[null_png_attack, null_png][check] )
                        else:
                            if buttons[coord].figure.color != buttons[from_pos].figure.color and buttons[coord].figure.role != 'king':
                                buttons[coord].configure( image=buttons[coord].figure._image_attack )
                                break
                            else:
                                break

        l, g = ord(from_pos[0]), int(from_pos[1])
        #Генерируются цифры от 1 до 10, добавляется к цифре координаты и увеличивают букву, таким образом генируются названия всех клеток, на которые можно пойти
        diagonal_cells = [ [ chr(l-i)+str(g-i), chr(l-i)+str(g+i), chr(l+i)+str(g-i), chr(l+i)+str(g+i), chr(l)+str(g+i), chr(l+i)+str(g), chr(l)+str(g-i), chr(l-i)+str(g) ] for i in range(1, 10) ]
                    
        #И всё же могут сформироваться такие названия, которых на поле нет, поэтому от них очищаем массив
        diagonal_cells = [ coord for coord in reduce(lambda massiv1, massiv2: massiv1+massiv2, diagonal_cells) if coord in buttons.keys() ]

        #Доступные клетки для коня
        cells_for_horse = [i for i in [ chr(l-2)+str(g+1), chr(l-2)+str(g-1), chr(l-1)+str(g+2), chr(l+1)+str(g+2), chr(l+2)+str(g+1), chr(l+2)+str(g-1), chr(l+1)+str(g-2), chr(l-1)+str(g-2) ] if i in buttons];

        #По отдельности генерируем каждое направление по диагонали
        up_right = [ coord for coord in diagonal_cells if coord[1] > from_pos[1] and coord[0] > from_pos[0]]
        up_left = [ coord for coord in diagonal_cells if coord[1] > from_pos[1] and coord[0] < from_pos[0]]
        down_right = [ coord for coord in diagonal_cells if coord[1] < from_pos[1] and coord[0] > from_pos[0]]
        down_left = [ coord for coord in diagonal_cells if coord[1] < from_pos[1] and coord[0] < from_pos[0]]

        #По отдельности генерируем каждое направление по вертикали или горизонтали (вверх, вниз, влево, вправо)
        up = [ from_pos[0]+str( int(from_pos[1])+i ) for i in range(1,11) if from_pos[0]+str( int(from_pos[1])+i ) in buttons ]
        down = [ from_pos[0]+str( int(from_pos[1])-i ) for i in range(1,11) if from_pos[0]+str( int(from_pos[1])-i ) in buttons ]
        left = [ chr( ord( from_pos[0] )-i )+from_pos[1] for i in range(1,11) if chr( ord( from_pos[0] )-i )+from_pos[1] in buttons ]
        right = [ chr( ord( from_pos[0] )+i )+from_pos[1] for i in range(1,11) if chr( ord( from_pos[0] )+i )+from_pos[1] in buttons ]

        if not(check):
            for coord in buttons:
                if isinstance(buttons[coord].figure, (Pawn, Rook, Queen, King, Elephant, Horse, Nikita, Ramazan, Nord, Checker)):
                    buttons[coord].configure( image=buttons[coord].figure._image )
                else:
                    buttons[coord].configure( image=null_png )

        if role == 'queen': GO([up_right, up_left, down_right, down_left, up, down, left, right]);
        elif role == 'elephant': GO([up_right, up_left, down_right, down_left]);
        elif role == 'rook': GO([up, down, left, right]);
        elif role == 'horse': 
            for coord in cells_for_horse:
                if isinstance(buttons[coord].figure, (Pawn, Rook, Queen, Elephant, Horse, King, Nikita, Ramazan, Nord)):
                    if buttons[coord].figure.color != buttons[from_pos].figure.color and buttons[coord].figure.role != 'king':
                        buttons[coord].configure( image=buttons[coord].figure._image_attack )
                else:
                    buttons[coord].configure( image=[null_png_attack, null_png][check] )
        elif role == 'king':
            x, y = from_pos[0], from_pos[1]
            cells_for_king = [ chr(ord(x)-1)+y, chr(ord(x)+1)+y, chr(ord(x)-1)+str(int(y)-1), chr(ord(x)-1)+str(int(y)  +1), chr(ord(x)+1)+str(int(y)+1), chr(ord(x)+1)+str(int(y)-1), x+str(int(y)-1), x+str(int(y)+1) ]
            for coord in cells_for_king:
                if coord[0] in 'ABCDEFGH' and coord[1] in '12345678':
                    if isinstance(buttons[coord].figure, (Pawn, Rook, Queen, Elephant, Horse, King, Nikita, Ramazan, Nord)):
                        if buttons[coord].figure.color != buttons[from_pos].figure.color and buttons[coord].figure.role != 'king':
                            buttons[coord].configure( image=buttons[coord].figure._image_attack )
                    else:
                        buttons[coord].configure( image=[null_png_attack, null_png][check] )
        elif role == 'pawn':
            diagonal_1 = chr(ord(from_pos[0])-1)+str( [int(from_pos[1])-1, int(from_pos[1])+1][buttons[from_pos].figure.color == 'white'] )
            diagonal_2 = chr(ord(from_pos[0])+1)+str( [int(from_pos[1])-1, int(from_pos[1])+1][buttons[from_pos].figure.color == 'white'] )
            next_cell1 = [from_pos[0]+str(int(from_pos[1])-1), from_pos[0]+str(int(from_pos[1])+1)][buttons[from_pos].figure.color == 'white']
            next_cell2 = [from_pos[0]+str(int(from_pos[1])-2), from_pos[0]+str(int(from_pos[1])+2)][buttons[from_pos].figure.color == 'white']
            pass_1, pass_2 = [[chr(ord(from_pos[0])-1)+str(int(from_pos[1])+1), chr(ord(from_pos[0])+1)+str(int(from_pos[1])+1)], [chr(ord(from_pos[0])-1)+str(int(from_pos[1])-1), chr(ord(from_pos[0])+1)+str(int(from_pos[1])-1)]][buttons[from_pos].figure.color == 'black']
            if next_cell1 in buttons:
                if not(buttons[next_cell1].figure.role):
                    buttons[next_cell1].configure( image=[null_png_attack, null_png][check] )
            
            #ПРОВЕРКА НА ТО, МОЖЕТ ЛИ ПЕШКА СДЕЛАТЬ ШАГ НА ДВЕ КЛЕТКИ ВПЕРЁД ПРИ ПЕРВОМ ХОДЕ
            if buttons[from_pos].figure.step == 0 and next_cell2 in buttons and not(buttons[next_cell1].figure.role) and ((from_pos[1]=='2' and next_cell2[1] == '4') or (from_pos[1]=='7' and next_cell2[1] == '5')):
                if not(buttons[next_cell2].figure.role):
                    buttons[next_cell2].configure( image=[null_png_attack, null_png][check] )
            
            #ПРОВЕРКА ВРАГОВ, СТОЯЩИХ ПО ДИАГОНАЛИ
            for coord in [diagonal_1, diagonal_2]:
                if isinstance(buttons[coord].figure, (Rook, Queen, Elephant, Horse, Pawn, Nikita, Ramazan, Nord)) and buttons[coord].figure.color != buttons[from_pos].figure.color:
                    buttons[coord].configure( image=buttons[coord].figure._image_attack )
            
            #ПРОВЕРКА НА ВЗЯТИЕ НА ПРОХОДЕ
            if buttons[from_pos].figure.color == 'white':
                if from_pos[1] == '5' and pass_1 in buttons:
                    if not(buttons[pass_1].figure.color) and buttons[pass_1[0]+str(int(pass_1[1])-1)].figure.color == 'black' and buttons[pass_1[0]+str(int(pass_1[1])-1)].figure.step == 1:
                        buttons[pass_1].configure( image=[null_png_attack, null_png][check] )
                if from_pos[1] == '5' and pass_2 in buttons:
                    if not(buttons[pass_2].figure.color) and buttons[pass_2[0]+str(int(pass_2[1])-1)].figure.color == 'black' and buttons[pass_2[0]+str(int(pass_2[1])-1)].figure.step == 1:
                        buttons[pass_2].configure( image=[null_png_attack, null_png][check] )

            if buttons[from_pos].figure.color == 'black':
                if from_pos[1] == '4' and pass_1 in buttons:
                    if not(buttons[pass_1].figure.color) and buttons[pass_1[0]+str(int(pass_1[1])+1)].figure.color == 'white' and buttons[pass_1[0]+str(int(pass_1[1])+1)].figure.step == 1:
                        buttons[pass_1].configure( image=[null_png_attack, null_png][check] )
                if from_pos[1] == '4' and pass_2 in buttons:
                    if not(buttons[pass_2].figure.color) and buttons[pass_2[0]+str(int(pass_2[1])+1)].figure.color == 'white' and buttons[pass_2[0]+str(int(pass_2[1])+1)].figure.step == 1:
                        buttons[pass_2].configure( image=[null_png_attack, null_png][check] )
        elif role == 'ramazan':
            #Функция even высвечивает каждую вторую клетку из всех, это нужно для хода для Рамазана, он ведь ходит как ладья, но через одну клетку
            GO([even(up), even(down), even(left), even(right)], is_ramazan = True);
        elif role == 'nikita':
            #Подсвечиваем всевозможные клетки для Никиты как Коня
            for coord in cells_for_horse:
                if isinstance(buttons[coord].figure, (Pawn, Rook, Queen, Elephant, Horse, King, Nikita, Ramazan, Nord)):
                    if buttons[coord].figure.color != buttons[from_pos].figure.color and buttons[coord].figure.role != 'king':
                        buttons[coord].configure( image=buttons[coord].figure._image_attack )
                else:
                    buttons[coord].configure( image=[null_png_attack, null_png][check] )
            #Подсвечиваем всевозможные клетки для Никиты как Слона
            GO([up_right, up_left, down_right, down_left]);
        elif role == 'nord':
            x, y = from_pos[0], from_pos[1]
            cells_for_king = [ chr(ord(x)-1)+y, chr(ord(x)+1)+y, chr(ord(x)-1)+str(int(y)-1), chr(ord(x)-1)+str(int(y)  +1), chr(ord(x)+1)+str(int(y)+1), chr(ord(x)+1)+str(int(y)-1), x+str(int(y)-1), x+str(int(y)+1) ]
            for coord in cells_for_king:
                if coord[0] in 'ABCDEFGH' and coord[1] in '12345678':
                    if not(isinstance(buttons[coord].figure, (Pawn, Rook, Queen, Elephant, Horse, King, Nikita, Ramazan, Nord))):
                        buttons[coord].configure( image=[null_png_attack, null_png][check] )
        elif role == 'checker':
            if 'is_queen' in buttons[from_pos].figure.__dict__:
                for coord in cells_for_horse:
                    GO([up_right, up_left, down_right, down_left]);
            #Следующие 4 строчки генерируют диагональные клетки. Код длинный, поскольку клетки генерируются относительно того, какого цвета шашка - чёрного или белого
            #Ведь если шашка белая, то идти она может только вперёд, если чёрная - наоборот. Эти условия как раз проверяются одной длинной строкой
            diagonal_1 = chr(ord(from_pos[0])-1)+str( [int(from_pos[1])-1, int(from_pos[1])+1][buttons[from_pos].figure.color == 'white'] )
            diagonal_2 = chr(ord(from_pos[0])+1)+str( [int(from_pos[1])-1, int(from_pos[1])+1][buttons[from_pos].figure.color == 'white'] )
            diagonal_1_1 = chr(ord(diagonal_1[0])-1)+str( [int(diagonal_1[1])-1, int(diagonal_1[1])+1][buttons[from_pos].figure.color == 'white'] )
            diagonal_2_1 = chr(ord(diagonal_2[0])+1)+str( [int(diagonal_2[1])-1, int(diagonal_2[1])+1][buttons[from_pos].figure.color == 'white'] )

            #Пытаемся подсветить первую диагональную клетку, если туда вообще МОЖНО пойти, поэтому нужен блок try... except...
            try:
                if not(buttons[diagonal_1].figure.role):
                    buttons[diagonal_1].configure( image=[null_png_attack, null_png][check] )
                elif not(buttons[diagonal_1_1].figure.role) and buttons[diagonal_1].figure.color != buttons[from_pos].figure.color:
                    buttons[diagonal_1_1].configure( image=[null_png_attack, null_png][check] )
            except Exception as error:
                pass

            #Та же самая процедура, только для второй диагональной клетки
            try:
                if not(buttons[diagonal_2].figure.role):
                    buttons[diagonal_2].configure( image=[null_png_attack, null_png][check] )
                elif not(buttons[diagonal_2_1].figure.role) and buttons[diagonal_2].figure.color != buttons[from_pos].figure.color:
                    buttons[diagonal_2_1].configure( image=[null_png_attack, null_png][check] )
            except Exception as error:
                pass
    #Обрабатываем всяческие исключения, выводя их на экран и нейтрализуя
    except Exception as error:
        pass
        # print(error)


'''
Функция срабатывает при нажатии на клетку-кнопку, каждая из которых в свою очередь содержит свою координату
Если from_pos переменная, отвечающая за начальную позицию уже выбрана, то координата присваивается переменной to_pos
Если нет, то сначала from_pos, а затем переходит в режим ожидания выбора следующей клетки
Как только from_pos(нач.позиция) и to_pos(кон.позиция) будут выбраны, срабатывает немаленький алгоритм, который проверяет:
[1] Не собирается ли игрок пойти на клетку, на которой уже стоит фигура его же цвета
[2] Может ли такая фигура вообще пойти на эту клетку, ведь каждая фигура имеет свои траектории хода
[3] Если все условия соблюдены: не стоит ли между начальной и конечными позициями другой фигуры, которая препятствует ходу? (для коня не работает, он ведь умеет прыгать)
Кстати о пункте 3, за проверку мешающих фигур отвечает отдельная функция check_for_extra_figures (проверка_на_лишние_фигуры)
'''
def choose_cell(position):
    global from_pos, to_pos, turn, white_nord_status, black_nord_status
    if from_pos in buttons:
        if position != from_pos:
            to_pos = position
            if buttons[from_pos].figure.color == buttons[to_pos].figure.color:
                from_pos, to_pos = to_pos, None
                show_available_cells(buttons[from_pos].figure.role, from_pos)
            else:
                step = False
                try:
                    taking = False
                    checker_eat = False #<--- Костыль, исправлять более эффективным способом было лень
                    #Если собирается идти пешка
                    if isinstance(buttons[from_pos].figure, Pawn):
                        diagonal_1 = chr(ord(from_pos[0])-1)+str( [int(from_pos[1])-1, int(from_pos[1])+1][buttons[from_pos].figure.color == 'white'] )
                        diagonal_2 = chr(ord(from_pos[0])+1)+str( [int(from_pos[1])-1, int(from_pos[1])+1][buttons[from_pos].figure.color == 'white'] )
                        pass_1, pass_2 = [[chr(ord(from_pos[0])-1)+str(int(from_pos[1])+1), chr(ord(from_pos[0])+1)+str(int(from_pos[1])+1)], [chr(ord(from_pos[0])-1)+str(int(from_pos[1])-1), chr(ord(from_pos[0])+1)+str(int(from_pos[1])-1)]][buttons[from_pos].figure.color == 'black']
                        if buttons[from_pos].figure.step == 0 and [int(from_pos[1])-int(to_pos[1]), int(to_pos[1])-int(from_pos[1])][buttons[from_pos].figure.color == 'white'] <= 2 and from_pos[0]==to_pos[0] and not(buttons[to_pos].figure.role):
                            if buttons[from_pos].figure.color == 'white' and buttons[ from_pos[0]+str(int(from_pos[1])+1) ].figure.color not in ['white', 'black']:
                                if from_pos[1] == '2': step = True
                            elif buttons[from_pos].figure.color == 'black' and buttons[ from_pos[0]+str(int(from_pos[1])-1) ].figure.color not in ['white', 'black']:
                                if from_pos[1] == '7': step = True
                        elif [int(from_pos[1])-int(to_pos[1]), int(to_pos[1])-int(from_pos[1])][buttons[from_pos].figure.color == 'white'] == 1 and from_pos[0]==to_pos[0] and not(buttons[to_pos].figure.role):
                            step = True
                        elif to_pos == diagonal_1 and isinstance(buttons[to_pos].figure, (Pawn, Rook, Queen, Elephant, Horse, Nikita, Ramazan, Nord)) and buttons[to_pos].figure.color != buttons[from_pos].figure.color:
                            step = True
                        elif to_pos == diagonal_2 and isinstance(buttons[to_pos].figure, (Pawn, Rook, Queen, Elephant, Horse, Nikita, Ramazan, Nord)) and buttons[to_pos].figure.color != buttons[from_pos].figure.color:
                            step = True

                        if buttons[from_pos].figure.color == 'white':
                            if from_pos[1] == '5' and pass_1 in buttons:
                                if not(buttons[pass_1].figure.color) and buttons[pass_1[0]+str(int(pass_1[1])-1)].figure.color == 'black' and buttons[pass_1[0]+str(int(pass_1[1])-1)].figure.step == 1:
                                    step, taking = True, to_pos in (pass_1, pass_2)
                            if from_pos[1] == '5' and pass_2 in buttons:
                                if not(buttons[pass_2].figure.color) and buttons[pass_2[0]+str(int(pass_2[1])-1)].figure.color == 'black' and buttons[pass_2[0]+str(int(pass_2[1])-1)].figure.step == 1:
                                    step, taking = True, to_pos in (pass_1, pass_2)

                        if buttons[from_pos].figure.color == 'black':
                            if from_pos[1] == '4' and pass_1 in buttons:
                                if not(buttons[pass_1].figure.color) and buttons[pass_1[0]+str(int(pass_1[1])+1)].figure.color == 'white' and buttons[pass_1[0]+str(int(pass_1[1])+1)].figure.step == 1:
                                    step, taking = True, to_pos in (pass_1, pass_2)
                            if from_pos[1] == '4' and pass_2 in buttons:
                                if not(buttons[pass_2].figure.color) and buttons[pass_2[0]+str(int(pass_2[1])+1)].figure.color == 'white' and buttons[pass_2[0]+str(int(pass_2[1])+1)].figure.step == 1:
                                    step, taking = True, to_pos in (pass_1, pass_2)

                    
                    #Если собирается идти ладья
                    if isinstance(buttons[from_pos].figure, Rook):
                        if buttons[to_pos].figure.role != 'king':
                            if from_pos[0] == to_pos[0] or from_pos[1] == to_pos[1]:
                                if check_the_cells_for_other_figures(from_pos, to_pos):
                                    step = True
                    
                    #Если собирается идти конь
                    if isinstance(buttons[from_pos].figure, Horse):
                        #l - номер первой буквы начальной позиции | g - цифра начальной позиции. Это нужно для сокращения записи
                        l, g = ord(from_pos[0]), int(from_pos[1])
                        #Массив available_cellc содержит координаты клеток, на которые может пойти конь, делается это специальными рассчётами вручную, потому и длинная строка
                        available_cells = [ chr(l-2)+str(g+1), chr(l-2)+str(g-1), chr(l-1)+str(g+2), chr(l+1)+str(g+2), chr(l+2)+str(g+1), chr(l+2)+str(g-1), chr(l+1)+str(g-2), chr(l-1)+str(g-2) ];
                        if to_pos in available_cells:
                            if isinstance(buttons[to_pos].figure, (Pawn, Rook, Queen, Horse, Elephant)):
                                if buttons[to_pos].figure.color != buttons[from_pos].figure.color and buttons[to_pos].figure.role != 'king':
                                    step = True
                            elif buttons[to_pos].figure.role != 'king':
                                step = True
                    
                    #Если собирается идти слон
                    if isinstance(buttons[from_pos].figure, Elephant):
                        l, g = ord(from_pos[0]), int(from_pos[1])
                        available_cells = [ [ chr(l-i)+str(g-i), chr(l-i)+str(g+i), chr(l+i)+str(g-i), chr(l+i)+str(g+i) ] for i in range(1, 10) ]
                        available_cells = [ coord for coord in reduce(lambda massiv1, massiv2: massiv1+massiv2, available_cells) if coord in buttons.keys() ]
                        if to_pos in available_cells:
                            if isinstance(buttons[to_pos].figure, (Pawn, Rook, Queen, Horse, Elephant, Nikita, Ramazan, Nord)):
                                if buttons[to_pos].figure.color != buttons[from_pos].figure.color and buttons[to_pos].figure.role != 'king':
                                    step = check_the_cells_for_other_figures(from_pos, to_pos, available_cells)
                            elif buttons[to_pos].figure.role != 'king':
                                step = check_the_cells_for_other_figures(from_pos, to_pos, available_cells)
                    
                    #Если собирается идти ферзь
                    if isinstance(buttons[from_pos].figure, Queen):
                        l, g = ord(from_pos[0]), int(from_pos[1])
                        #Генерируются цифры от 1 до 10, добавляется к цифре координаты и увеличивают букву, таким образом генируются названия всех клеток, на которые можно пойти
                        available_cells = [ [ chr(l-i)+str(g-i), chr(l-i)+str(g+i), chr(l+i)+str(g-i), chr(l+i)+str(g+i), chr(l)+str(g+i), chr(l+i)+str(g), chr(l)+str(g-i), chr(l-i)+str(g) ] for i in range(1, 10) ]
                        #И всё же могут сформироваться такие названия, которых на поле нет, поэтому от них очищаем массив
                        available_cells = [ coord for coord in reduce(lambda massiv1, massiv2: massiv1+massiv2, available_cells) if coord in buttons.keys() ]
                        #Проверка: если клетка, на которую игрок хочет пойти есть в списке доступных - идёт проверка на стоячие между ними мешающие фигуры
                        if to_pos in available_cells:
                            if isinstance(buttons[to_pos].figure, (Pawn, Rook, Queen, Horse, Elephant, Nikita, Ramazan, Nord)):
                                if buttons[to_pos].figure.color != buttons[from_pos].figure.color and buttons[to_pos].figure.role != 'king':
                                    step = check_the_cells_for_other_figures(from_pos, to_pos, available_cells)
                            elif buttons[to_pos].figure.role != 'king':
                                step = check_the_cells_for_other_figures(from_pos, to_pos, available_cells)
                    
                    #Если собирается идти король
                    if isinstance(buttons[from_pos].figure, King):
                        if abs(ord(to_pos[0])-ord(from_pos[0])) <= 1 and abs(int(to_pos[1])-int(from_pos[1])) <= 1:
                            if isinstance(buttons[to_pos].figure, (Pawn, Rook, Queen, Horse, Elephant, Nikita, Ramazan, Nord)):
                                if buttons[to_pos].figure.color != buttons[from_pos].figure.color and buttons[to_pos].figure.role != 'king':
                                    step = True
                            elif buttons[to_pos].figure.role != 'king':
                                step = True

                    #Если собирается идти Рамазан
                    if isinstance(buttons[from_pos].figure, Ramazan):
                        if buttons[to_pos].figure.role != 'king':
                            if from_pos[0] == to_pos[0] or from_pos[1] == to_pos[1]:
                                if abs(int(from_pos[1])-int(to_pos[1])) % 2 == 0 and from_pos[0] == to_pos[0]:
                                    step = True
                                elif abs(ord(from_pos[0])-ord(to_pos[0])) % 2 == 0 and from_pos[1] == to_pos[1]:
                                    step = True

                    #Если собирается идти Никита
                    if isinstance(buttons[from_pos].figure, Nikita):
                        l, g = ord(from_pos[0]), int(from_pos[1])
                        #Доступные клетки по диагоналям
                        diagonal_cells = [ [ chr(l-i)+str(g-i), chr(l-i)+str(g+i), chr(l+i)+str(g-i), chr(l+i)+str(g+i) ] for i in range(1, 10) ]
                        diagonal_cells = [ coord for coord in reduce(lambda massiv1, massiv2: massiv1+massiv2, diagonal_cells) if coord in buttons.keys() ]
                        #Доступные клетки для коня
                        cells_for_horse = [ chr(l-2)+str(g+1), chr(l-2)+str(g-1), chr(l-1)+str(g+2), chr(l+1)+str(g+2), chr(l+2)+str(g+1), chr(l+2)+str(g-1), chr(l+1)+str(g-2), chr(l-1)+str(g-2) ];
                        
                        #Если Никита идёт как слон / АХХАХАХААХАХ НИКИТА СЛОН АХАХАХАХХАХАХАХААХХАХАХА
                        if to_pos in diagonal_cells:
                            if isinstance(buttons[to_pos].figure, (Pawn, Rook, Queen, Horse, Elephant, Nikita, Ramazan, Nord)):
                                if buttons[to_pos].figure.color != buttons[from_pos].figure.color and buttons[to_pos].figure.role != 'king':
                                    step = check_the_cells_for_other_figures(from_pos, to_pos, diagonal_cells)
                            elif buttons[to_pos].figure.role != 'king':
                                step = check_the_cells_for_other_figures(from_pos, to_pos, diagonal_cells)
                        #Если Никита идёт как конь / АХХАХАХААХАХ НИКИТА КОНЬ АХАХАХАХХАХАХАХААХХАХАХА
                        elif to_pos in cells_for_horse:
                            if isinstance(buttons[to_pos].figure, (Pawn, Rook, Queen, Horse, Elephant)):
                                if buttons[to_pos].figure.color != buttons[from_pos].figure.color and buttons[to_pos].figure.role != 'king':
                                    step = True
                            elif buttons[to_pos].figure.role != 'king':
                                step = True

                    #Если собирается идти Норд
                    if isinstance(buttons[from_pos].figure, Nord):
                        if abs(ord(to_pos[0])-ord(from_pos[0])) <= 1 and abs(int(to_pos[1])-int(from_pos[1])) <= 1:
                            if not(isinstance(buttons[to_pos].figure, (Pawn, Rook, Queen, Horse, Elephant, King, Nikita, Ramazan, Nord))):
                                step = True
                                if buttons[from_pos].figure.color == 'white':
                                    white_nord_status = to_pos
                                else:
                                    black_nord_status = to_pos

                    #Если собирается идти Шашка
                    if isinstance(buttons[from_pos].figure, Checker):
                        if 'is_queen' in buttons[from_pos].figure.__dict__:
                            l, g = ord(from_pos[0]), int(from_pos[1])
                            available_cells = [ [ chr(l-i)+str(g-i), chr(l-i)+str(g+i), chr(l+i)+str(g-i), chr(l+i)+str(g+i) ] for i in range(1, 10) ]
                            available_cells = [ coord for coord in reduce(lambda massiv1, massiv2: massiv1+massiv2, available_cells) if coord in buttons.keys() ]
                            if to_pos in available_cells:
                                if isinstance(buttons[to_pos].figure, (Pawn, Rook, Queen, Horse, Elephant, Nikita, Ramazan, Nord)):
                                    if buttons[to_pos].figure.color != buttons[from_pos].figure.color and buttons[to_pos].figure.role != 'king':
                                        step = check_the_cells_for_other_figures(from_pos, to_pos, available_cells)
                                elif buttons[to_pos].figure.role != 'king':
                                    step = check_the_cells_for_other_figures(from_pos, to_pos, available_cells)
                        else:
                            diagonal_1 = chr(ord(from_pos[0])-1)+str( [int(from_pos[1])-1, int(from_pos[1])+1][buttons[from_pos].figure.color == 'white'] )
                            diagonal_2 = chr(ord(from_pos[0])+1)+str( [int(from_pos[1])-1, int(from_pos[1])+1][buttons[from_pos].figure.color == 'white'] )
                            diagonal_1_1 = chr(ord(diagonal_1[0])-1)+str( [int(diagonal_1[1])-1, int(diagonal_1[1])+1][buttons[from_pos].figure.color == 'white'] )
                            diagonal_2_1 = chr(ord(diagonal_2[0])+1)+str( [int(diagonal_2[1])-1, int(diagonal_2[1])+1][buttons[from_pos].figure.color == 'white'] )

                            if to_pos == diagonal_1:
                                if not(buttons[diagonal_1].figure.role):
                                    step = True
                            elif to_pos == diagonal_1_1:
                                if buttons[diagonal_1].figure.role and buttons[diagonal_1].figure.color != buttons[from_pos].figure.color and not(buttons[diagonal_1_1].figure.role):
                                    step = True; 
                                    checker_eat = buttons[diagonal_1].figure.color+'_'+buttons[diagonal_1].figure.role
                                    del buttons[diagonal_1].figure
                            elif to_pos == diagonal_2:
                                if not(buttons[diagonal_2].figure.role):
                                    step = True
                            elif to_pos == diagonal_2_1:
                                if buttons[diagonal_2].figure.role and buttons[diagonal_2].figure.color != buttons[from_pos].figure.color and not(buttons[diagonal_2_1].figure.role):
                                    step = True;
                                    checker_eat = buttons[diagonal_2].figure.color+'_'+buttons[diagonal_2].figure.role
                                    del buttons[diagonal_2].figure

                    #Если разрешено совершить ход
                    if step:
                        #Совершаем ход
                        make_step(from_pos, to_pos, taking_on_pass = taking, checker_eat = checker_eat) #<--- Вызываем функцию совершения хода. Если взятие на переходе - передаём значение True аргументу taking_on_pass
                        turn = ['white', 'black'][turn == 'white'] #<--- Меняем очередь на противоположную
                        color_label.configure(image=[turn_black, turn_white][turn=='white']) #<--- Меняем картинку, подсказывающую очередь
                        if isinstance(buttons[to_pos].figure, Pawn):
                            if (buttons[to_pos].figure.color == 'white' and to_pos[1] == '8') or (buttons[to_pos].figure.color == 'black' and to_pos[1] == '1'):
                                select_new_figure(buttons[to_pos].figure.color, to_pos) #<--- Если пешка дошла до противоположного фланга - выбираем новую фигуру
                        #Если дошла Шашка
                        elif isinstance(buttons[to_pos].figure, Checker):
                            if (buttons[to_pos].figure.color == 'white' and to_pos[1] == '8') or (buttons[to_pos].figure.color == 'black' and to_pos[1] == '1'):
                                buttons[to_pos].figure.is_queen = True
                                buttons[to_pos].figure._image = figure_images[f'{buttons[to_pos].figure.color}_queen']
                                buttons[to_pos].figure._image_attack = figure_images[f'{buttons[to_pos].figure.color}_queen']
                                buttons[to_pos].configure( image=buttons[to_pos].figure._image )
                    #Если нет, то заново выводим подсказки
                    else:
                        for cell in buttons:
                            buttons[cell].configure( image=[null_png, buttons[cell].figure._image][ isinstance(buttons[cell].figure, (Rook, Pawn, Horse, Elephant, Queen, King, Nikita, Ramazan, Nord, Checker)) ] )
                    
                    #Выводим подсказки угрожаемых фигур
                    for cell in buttons:
                        if buttons[cell].figure.color == ['white', 'black'][turn=='white']:
                            show_available_cells( buttons[cell].figure.role, cell, check=True )
                    from_pos, to_pos = None, None
                #Обрабатываем всевозможные исключения, выводя их на экран и решая проблемки. Вот такие вот пельмени
                except Exception as error:
                    pass
    #В противном случае (то есть если конечная позиция не выбрана - выбираем начальную и подсвечиваем клетки, на которые фигуры может пойти, если она там, конечно, вообще стоит)
    else:
        if isinstance(buttons[position].figure, (Pawn, Rook, Horse, Elephant, Queen, King, Nikita, Ramazan, Nord, Checker)) and buttons[position].figure.color == turn:
            from_pos = position
            show_available_cells( buttons[position].figure.role, from_pos )


'''Функция arrange_the_figures расставляет фигуры на поле в зависимости от того, какая игра запускается: Шахматы или Шашки
Для каждой фигуры создан класс: Pawn(пешка), Horse(конь), Elephant(слон), King(король), Queen(ферзь), Rook(ладья),
Ramazan(Рамазан), Nikita(Никита), Nord(норд - собака Насти) и отдельный класс для шашек ~ Checker(шашка)
'''
def arrange_the_figures(mode='Chess'):
    global buttons, label
    if mode == 'Chess':
        label.configure(image=background_image_chess)
        #Меняем цвета клеток в обратном порядке
        for digit in range(8, 0, -1):
            for letter in 'ABCDEFGH':
                x = {'A': 0, 'B': 75, 'C': 150, 'D': 225, 'E': 300, 'F': 375, 'G': 450, 'H': 525}[letter]
                y = (8-digit)*75
                buttons[letter+str(digit)].configure(bg=['#EBECD0', '#779556'][(digit+ord(letter))%2])
        for position in buttons:
            del buttons[position].figure
        #РАССТАВЛЯЕМ ФИГУРКИ ДЛЯ ШАХМАТ
        for position, cell in buttons.items():
            if '7' in cell.coord or '2' in cell.coord:
                cell.figure = Pawn(color=['white', 'black']['7' in cell.coord])
                cell.configure(image=cell.figure._image)
        buttons['A1'].figure = Rook('white'); buttons['A8'].figure = Rook('black');
        buttons['B1'].figure = Horse('white'); buttons['B8'].figure = Horse('black');
        buttons['C1'].figure = Elephant('white'); buttons['C8'].figure = Elephant('black');
        buttons['D1'].figure = Queen('white'); buttons['D8'].figure = Queen('black');
        buttons['E1'].figure = King('white'); buttons['E8'].figure = King('black');
        buttons['F1'].figure = Elephant('white'); buttons['F8'].figure = Elephant('black');
        buttons['G1'].figure = Horse('white'); buttons['G8'].figure = Horse('black');
        buttons['H1'].figure = Rook('white'); buttons['H8'].figure = Rook('black');

        #РАССТАВЛЯЕМ УНИКАЛЬНЫЕ ФИГУРЫ
        buttons['B2'].figure = Ramazan('white'); buttons['C2'].figure = Nikita('white')
        buttons['F2'].figure = Nikita('white'); buttons['G2'].figure = Ramazan('white')
        buttons['B7'].figure = Ramazan('black'); buttons['C7'].figure = Nikita('black')
        buttons['F7'].figure = Nikita('black'); buttons['G7'].figure = Ramazan('black')

    elif mode == 'Checkers':
        label.configure(image=background_image_checkers)
        #Меняем цвета клеток в обратном порядке
        for digit in range(8, 0, -1):
            for letter in 'ABCDEFGH':
                x = {'A': 0, 'B': 75, 'C': 150, 'D': 225, 'E': 300, 'F': 375, 'G': 450, 'H': 525}[letter]
                y = (8-digit)*75
                buttons[letter+str(digit)].configure(bg=['#9F5241', '#E4B088'][(digit+ord(letter))%2])
        
        #Перед расстановкой новых шашек очищаем поле
        for position in buttons:
            del buttons[position].figure

        #РАССТАВЛЯЕМ ФИГУРЫ ДЛЯ ШАШЕК
        for position, cell in buttons.items():
            if position in 'B8 D8 F8 H8 A7 C7 E7 G7 B6 D6 F6 H6':
                cell.figure = Checker('black')
            elif position in 'A3 C3 E3 G3 B2 D2 F2 H2 A1 C1 E1 G1':
                cell.figure = Checker('white')

'''Функция срабатывает в случае, если пешка дошла до вражеского врага
Как только пешка оказалась на вражеском фланге - открывается доп.окно, в котором
игроку предстоит выбрать одну из четырёх фигур, в которую он хочет превратить пешку
Выбирать можно из следующих фигур: Ферзь, ладья, слон, конь'''
def select_new_figure(color, to_pos, role='None', time_from_log=False):

    def set_figure(color, role, to_pos):
        global buttons, log_window, binary_history
        #УСТАНАВЛИВАЕМ НОВУЮ ФИГУРУ
        buttons[to_pos].figure = {'queen': Queen(color), 'rook': Rook(color), 'elephant': Elephant(color), 'horse': Horse(color)}[role]
        #После выбора новой фигуры окно автоматически закрывается до следующего появления
        window.destroy()
        #ПРОХОДИМСЯ ПО ВСЕМ КЛЕТКАМ И ВОЗВРАЩАЕМ ИМ ВОЗМОЖНОСТЬ ВЗАИМОДЕЙСТВОВАТЬ С ИГРОКОМ
        for coord in buttons:
            buttons[coord].configure(state=NORMAL)
        color = ['Белая', 'Чёрная'][color=='black']
        log_message = f'{color} Пешка превратилась в '+{'queen': 'Ферзь', 'rook': 'Ладью', 'horse': 'Коня', 'elephant': 'Слона'}[role]
        time = datetime.datetime.now(); hour, minute, second = time.hour, time.minute, '0'+str(time.second) if len(str(time.second)) == 1 else time.second
        if time_from_log:
            log_window.insert(END, f' {time_from_log}   {log_message}')
        else:
            log_window.insert(END, f' [{hour}:{minute}:{second}]   {log_message}')
        log_window.itemconfig(END, fg='red')
        binary_history[-1].append(role)

    window = Toplevel()
    if role=='None':
    
        #Проходимся по каждой кнопке и временно отключаем их, пока человек не выберет фигуру
        for coord in buttons:
            buttons[coord].configure(state=DISABLED)

        #Создаётся новое окно с фигурами-кнопками, которые вызывают функцию set_figure и устанавливают новую фигуру
        window['bg'] = '#996e17'
        window.title('Самое время менять пешку!')
        window.geometry(f'300x100+{ root.winfo_x()+625 }+{ root.winfo_y()+390 }');
        window.resizable(width=False, height=False)

        #Создаём кнопки, каждой приписываем характерный задний фон
        for number, role in enumerate(['queen', 'rook', 'elephant', 'horse']):
            image = PhotoImage(file='images/pieces/black_queen.png')
            Button(window, image=figure_images[f'{color}_{role}'], command=lambda role=role, color=color, to_pos=to_pos: set_figure(color, role, to_pos)).place(x=75*number, y=0, width=75, height=75)

        #Картинка "Время менять пешку"
        Label(window, image=its_time_to_change_the_pawn).place(x=-2, y=75)
    else:
        #Противный случай (блок else) означает, что ход совершается не в данный момент, а загружается из истории, в качестве доп.аргумента
        #Передаётся роль фигуры, в которую надо превратить пешку. Это нужно для автоматизации превращения
        set_figure(color, role, to_pos)


#ПРИ НАЖАТИИ НА КНОПКУ НОРД ВЗРЫВАЕТСЯ, УНОСЯ ЗА СОБОЙ ВРАЖЕСКИЕ ФИГУРЫ В РАДИУСЕ ОДНОЙ КЛЕТКИ
def blow_up_the_nord(coord, load=False):
    global binary_history, del_history, turn

    if not(load): 
        step_sound.stop(); nord_sound.play()

    color = {'white': 'Белый', 'black': 'Чёрный'}
    if turn == buttons[coord].figure.color:
        #Собираем бинарную запись хода норда, чтоб её можно было восстановить
        nord_action = [ coord, buttons[coord].figure.color ]
        x, y = coord[0], coord[1]
        cells_for_nord = [ chr(ord(x)-1)+y, chr(ord(x)+1)+y, chr(ord(x)-1)+str(int(y)-1), chr(ord(x)-1)+str(int(y)  +1), chr(ord(x)+1)+str(int(y)+1), chr(ord(x)+1)+str(int(y)-1), x+str(int(y)-1), x+str(int(y)+1) ]
        for cell in cells_for_nord:
            if cell in buttons:
                if buttons[cell].figure.color == ['white', 'black'][buttons[coord].figure.color == 'white'] and buttons[cell].figure.role != 'king':
                    nord_action.append([cell, f'{buttons[cell].figure.color}_{buttons[cell].figure.role}'])
                    del buttons[cell].figure

        #ПОСЛЕ ВЗРЫВА НОРДА УБИРАЕМ КНОПКУ, ПОТОМУ ЧТО ВЗРЫВАТЬСЯ НЕЧЕМУ
        if buttons[coord].figure.color == 'white':
            blow_up_the_white_nord.place_forget()
        else:
            blow_up_the_black_nord.place_forget()
        #Сообщение о взрыве выводим на экран
        time = datetime.datetime.now(); hour, minute, second = time.hour, time.minute, '0'+str(time.second) if len(str(time.second)) == 1 else time.second
        log_message = f' [{hour}:{minute}:{second}]  {color[buttons[coord].figure.color]} Норд был слишком милым для них'
        log_window.insert(END, log_message)
        log_window.itemconfig(END, fg='yellow', bg='black')
        #Убираем норда с клетки. Норд был хорошим...
        del buttons[coord].figure
        binary_history.append(nord_action)
        turn = ['white', 'black'][turn=='white']
        color_label.configure(image=[turn_black, turn_white][turn=='white'])




#=================================| ОБЪЯВЛЕНИЕ ФУНКЦИЙ ДЛЯ РАБОТЫ С ИНТЕРФЕЙСОМ |=====================================#
#ФУНКЦИЯ, СРАБАТЫВАЮЩИЕ ПРИ НАЖАТИИ НА КНОПКУ "СОХРАНИТЬ"
def save():
    global history
    
    now = datetime.datetime.now()
    day = '0'+str(now.day) if len( str(now.day) )==1 else str(now.day)
    month = '0'+str(now.month) if len( str(now.month) )==1 else str(now.month)
    year = str(now.year)
    hour = '0'+str(now.hour) if len( str(now.hour) )==1 else str(now.hour)
    minute = '0'+str(now.minute) if len( str(now.minute) )==1 else str(now.minute)
    
    with open( f'history/{day}.{month}.{year} {hour};{minute}_bin.txt', 'wb' ) as file:
        pickle.dump(binary_history, file)

#ФУНКЦИЯ, СРАБАТЫВАЮЩИЕ ПРИ НАЖАТИИ НА КНОПКУ "ЗАГРУЗИТЬ/УДАЛИТЬ"
def load():

    def delete():
        try:
            try:
                history_id = history_list.curselection()[0]
            except Exception as error:
                history_id = 0
            history_list.delete(history_id)
            file_name = histories[history_id]
            del histories[history_id]
            remove(f'history/{file_name}');
        except Exception as error:
            print(f'[ERROR] Удалять нечего, в истории нет ни одной записи')

    
    def place():
        try:
            global buttons, log_window, turn, color_label, binary_history, text_history, white_nord_status, black_nord_status
            try:
                history = histories[list(history_list.curselection())[0]][:-4]
            except Exception as error:
                history = histories[0][:-4]

            with open('history/'+history+'.txt', 'rb') as file:
                history = pickle.load(file)
            
            window.destroy()
            
            text_history = ''
            binary_history = []

            log_window.delete(10, END)
            arrange_the_figures() # <-- Генерируем поле заново, чтоб расставить фигурки так, как надо
            for action in history:
                if action[0] not in buttons:
                    from_pos, to_pos = action[0].split('-->')[0], action[0].split('-->')[1]
                    time = action[3]
                    make_step(from_pos, to_pos, time)
                    if len(action)==5 and action[-1] in ('queen', 'horse', 'elephant', 'rook'):
                        select_new_figure( buttons[to_pos].figure.color, to_pos, action[-1], time )
                    
                    #Если последним записана координата, значит это координата появившегося Норда
                    if action[-1] in buttons:
                        binary_history[-1].append(action[-1])
                        buttons[action[-1]].figure = Nord( action[1].split('_')[0] )
                        if action[1].split('_')[0] == 'white' and not(white_nord_status):
                            blow_up_the_white_nord.place(x=300, y=680, width=75, height=75)
                            white_nord_status = action[-1]

                        elif action[1].split('_')[0] == 'black' and not(black_nord_status):
                            blow_up_the_black_nord.place(x=300, y=150, width=75, height=75)
                            black_nord_status = action[-1]
                else:
                    blow_up_the_nord( action[0], load=True )

            turn = ['white', 'black'][len(history)%2]
            color_label.configure(image=[turn_black, turn_white][turn=='white'])
        except Exception as error:
            print(error)
            print('[ERROR] Загружать нечего, в записи нет ни одной истории')

    histories = [ file for file in listdir('history')[::-1] if 'bin' in file]

    window = Toplevel()
    window['bg'] = '#996e17'
    window.title('Загрузка сохранений')
    window.geometry(f'600x200+{root.winfo_x()+450}+{root.winfo_y()+350}');
    window.resizable(width=False, height=False)
    history_list = Listbox(window, selectmode=SINGLE, height=len(histories), font=('Arial', 13, 'bold'), bg='#a2a2ac', fg='black');
    for history in histories:
        history_list.insert(END, ' '*40 + f'{history}')
    scroll = Scrollbar(history_list, command=history_list.yview)
    scroll.pack(side=RIGHT, fill=Y);
    history_list.config(yscrollcommand=scroll.set)
    history_list.place(x=0, y=0, width=600, height=150)

    load_the_placement = Button(window, command=place, image=load_the_placement_image, relief=FLAT)
    load_the_placement.place(x=0, y=150, width=300, height=50)

    remove_the_placement = Button(window, command=delete, image=remove_the_placement_image, relief=FLAT)
    remove_the_placement.place(x=300, y=150, width=300, height=50)

#ФУНКЦИЯ, ОТКРЫВАЮЩАЯ ДОП.ОКНО С ОБУЧАЮЩИМИ ВИДЕОРОЛИКАМИ
def help_window():

    def turn_on_the_video():
        global lessons
        try:
            video_name = lessons[list(lessons_list.curselection())[0]][:-4]
        except Exception as error:
            video_name = lessons[0][:-4]
        subprocess.call(f"videos/{video_name}.mp4", shell=True)


    global lessons
    #Создаём доп.окно с выбором новой фигуры, которое будет появляться в середине родительского окна Root
    window = Toplevel()
    window['bg'] = '#996e17' #<--- Устанавливаем характеристики окну. Задний фон, название(title), размер и положение относительно родительского окна Root
    window.title('Обучающие видеоролики')
    window.geometry(f'600x200+{root.winfo_x()+450}+{root.winfo_y()+350}');
    window.resizable(width=False, height=False)

    lessons_list = Listbox(window, selectmode=SINGLE, height=len(lessons), font=('Arial', 13, 'bold'), bg='#3d3770', fg='white');
    for number, lesson in enumerate(lessons, 1):
        lessons_list.insert(END, ' '+f'[{number}] {lesson[:-4]}');
    scroll = Scrollbar(lessons_list, command=lessons_list.yview)
    scroll.pack(side=RIGHT, fill=Y);
    lessons_list.config(yscrollcommand=scroll.set)
    lessons_list.place(x=0, y=0, width=600, height=150)

    turn_the_video_btn = Button(window, command=turn_on_the_video, image=watch_the_video_image)
    turn_the_video_btn.place(x=0, y=150, width=600, height=50)


#ФУНКЦИЯ ОТКАТЫВАЕТ ХОДЫ, ПОСЛЕДОВАТЕЛЬНО С ПОСЛЕДНЕГО И ДО ПЕРВОГО
def undo():
    global binary_history, turn, color_label, undo_button, del_history

    figures = { 'rook': Rook, 'pawn': Pawn, 'queen': Queen, 'king': King, 'horse': Horse, 'elephant': Elephant, 'ramazan': Ramazan, 'nikita': Nikita, 'nord': Nord, 'False': Figure, 'checker': Checker }
    #ПО НАЖАТИЮ НА КНОПКУ "НАЗАД" КРАСНЫЕ КРУЖКИ-ПОДСКАЗКИ ДОЛЖНЫ УДАЛИТЬСЯ
    for coord in buttons:
        if isinstance(buttons[coord].figure, (Pawn, Rook, Queen, King, Elephant, Horse, Nikita, Ramazan, Nord)):
            buttons[coord].configure( image=buttons[coord].figure._image )
        else:
            buttons[coord].configure( image=null_png )

    #Если запись началась с --> это значит, что какая-то фигура совершила ход. В противном случае это означает взрыв Норда, который мы возобновляем
    if '-->' in binary_history[-1][0]:
        #Следующие строчки разбивают массив на начальную позицию, конечную и доп.инфу, которая поможет восстановить хронологию
        from_pos = binary_history[-1][0].split('-->')[0]
        to_pos = binary_history[-1][0].split('-->')[1].split(',')[0]
        taking_pos = binary_history[-1][0].split('-->')[1].split(',')[1] if len(binary_history[-1][0].split('-->')[1].split(',')) == 2 else False
        figure_from_pos = binary_history[-1][1]
        figure_to_pos = binary_history[-1][2]
        from_pos_role, from_pos_color = figure_from_pos.split('_')[1], figure_from_pos.split('_')[0]
        to_pos_role, to_pos_color = figure_to_pos.split('_')[1], figure_to_pos.split('_')[0]
        del buttons[from_pos].figure; del buttons[to_pos].figure #<--- Перекидываем ход из обычной истории в историю удалённых ходов
        buttons[from_pos].figure = figures[from_pos_role](from_pos_color)

        #Если на предыдущем шаге появился Норд
        if binary_history[-1][-1] in buttons:
            if buttons[ binary_history[-1][-1] ].figure.color == 'white':
                blow_up_the_white_nord.place_forget()
            else:
                blow_up_the_black_nord.place_forget()
            del buttons[ binary_history[-1][-1] ].figure

        if to_pos_color == 'False':
            buttons[to_pos].figure = Figure()   
        else:
            #Если было совершено взятие на проходе
            if taking_pos:
                buttons[taking_pos].figure = figures[to_pos_role](to_pos_color)
                buttons[taking_pos].figure.step = 1
            else:
                buttons[to_pos].figure = figures[to_pos_role](to_pos_color)
                if isinstance(buttons[to_pos].figure, Nord):
                    if buttons[to_pos].figure.color == 'white':
                        buttons[to_pos].figure = Nord('white')
                        blow_up_the_white_nord.place(x=300, y=680, width=75, height=75)
                        white_nord_status = to_pos
                    else:
                        buttons[to_pos].figure = Nord('black')
                        blow_up_the_white_nord.place(x=300, y=160, width=75, height=75)
                        white_nord_status = to_pos
                if binary_history[-1][2] != 'False_False':
                    coord_between_two_cells = chr((ord(from_pos[0])+ord(to_pos[0]))//2)+str( (int(from_pos[1])+int(to_pos[1]))//2 )
                    buttons[coord_between_two_cells].figure = Checker( binary_history[-1][2].split('_')[0] )
    else:
        #Возвращаем Норда
        buttons[binary_history[-1][0]].figure = Nord(binary_history[-1][1])
        #Восстанавливаем все фигуры, которые Норд съел
        for figure in binary_history[-1][2:]:
            buttons[ figure[0] ].figure = figures[ figure[1].split('_')[1] ]( figure[1].split('_')[0] )

        #Восстанавливаем кнопку взрыва в зависимости от Норда
        if binary_history[-1][1] == 'white':
            blow_up_the_white_nord.place(x=300, y=680, width=75, height=75)
            white_nord_status = binary_history[-1][0]
        else:
            blow_up_the_black_nord.place(x=300, y=150, width=75, height=75)
            black_nord_status = binary_history[-1][0]

    del_history.append( binary_history[-1] ); del binary_history[-1] #<--- Перемещаем запись из удалённых в обычных

    step_sound.play()
    turn = ['white', 'black'][turn=='white']
    color_label.configure(image=[turn_black, turn_white][turn=='white'])

    for cell in buttons:
        buttons[cell].configure( image=buttons[cell].figure._image )

    for cell in buttons:
        if buttons[cell].figure.color == ['white', 'black'][turn=='white']:
            show_available_cells( buttons[cell].figure.role, cell, check=True )

    print( buttons['C1'].figure.__dict__ )

    if len(binary_history) == 0:
        undo_button.configure(state=DISABLED)
    back_button.configure(state=NORMAL)
    if 'превратил' in log_window.get(END):
        log_window.delete(END); log_window.delete(END);
    else:
        log_window.delete(END);


#Функция back возвращает ход, восстанавливает хронологию перемещений и превращений
def back():
    global binary_history, buttons, null_png, turn, color_label, undo_button, del_history
    if '-->' in del_history[-1][0]:
        from_pos, to_pos = del_history[-1][0].split('-->')[0], del_history[-1][0].split('-->')[1].split(',')[0]
        taking_pos = del_history[-1][0].split('-->')[1].split(',')[1] if len(del_history[-1][0].split('-->')[1].split(',')) == 2 else False
        color = del_history[-1][1].split('_')[0]
        time = del_history[-1][3]
        make_step(from_pos, to_pos, time, taking_on_pass = bool(taking_pos))
        if del_history[-1][-1] not in buttons and del_history[-1][-1] in ('rook', 'horse', 'queen', 'elephant'):
            select_new_figure(color, to_pos, del_history[-1][-1], time )

        #Если последний элемент истории - координата, значит возвращаем Норда на клетку
        if del_history[-1][-1] in buttons:
            buttons[ del_history[-1][-1] ].figure = Nord( del_history[-1][1].split('_')[0] )
            binary_history[-1].append( del_history[-1][-1] )
            
            if del_history[-1][1].split('_')[0] == 'white':
                blow_up_the_white_nord.place(x=300, y=680, width=75, height=75)
                white_nord_status = binary_history[-1][0]
            else:
                blow_up_the_black_nord.place(x=300, y=150, width=75, height=75)
                black_nord_status = binary_history[-1][0]

        turn = ['white', 'black'][turn=='white'] #<--- Меняем очередь ходящей фигуры
        color_label.configure(image=[turn_black, turn_white][turn=='white'])  #<--- Меняем картинку текст подсказки

    else:
        blow_up_the_nord( del_history[-1][0] ) #<--- В противном случае это означает взрыв Норда
    

    del del_history[-1] #Переносим запись из "Удалённых" в "Текущие"
    #Если в "удалённых" не осталось записей - вперёд пойти нельзя, блокируем кнопку`
    if len(del_history) == 0:
        back_button.configure(state=DISABLED)

    for cell in buttons:
        if buttons[cell].figure.color == ['white', 'black'][turn=='white']:
            show_available_cells( buttons[cell].figure.role, cell, check=True )


#Функция play_chess подготавливает поле для игры в "Шахматы"
def play_chess():
    global buttons, from_pos, to_Pos, turn, binary_history, del_history, eaten_figures, white_nord_status, black_nord_status
    global log_window

    from_pos, to_pos = None, None
    turn = 'white'
    binary_history = []
    del_history = []
    eaten_figures = {'white': [], 'black': []}
    white_nord_status, black_nord_status = False, False
    blow_up_the_white_nord.place_forget(); blow_up_the_black_nord.place_forget()

    #Окно с логами
    log_window = Listbox(root, bg='#e8e8e8', selectmode=SINGLE, font=('Arial', 10, 'bold'), fg='blue', relief=RIDGE, bd=10)
    scroll = Scrollbar(log_window, command=log_window.yview)
    scroll.pack(side=RIGHT, fill=Y);
    log_window.config(yscrollcommand=scroll.set)
    log_window.place(x=1065, y=200, width=420, height=500)
    log_window.insert(END, '-'*100); log_window.itemconfig(END, bg='#efedff');
    log_window.insert(END, '           Добро пожаловать в проект "Шахматы"'); log_window.itemconfig(END, bg='#efedff');
    log_window.insert(END, '  Если вы вдруг не знаете правил этой замечательной'); log_window.itemconfig(END, bg='#efedff');
    log_window.insert(END, '  игры, то специально для вас в правом нижнем углу'); log_window.itemconfig(END, bg='#efedff');
    log_window.insert(END, '  Расположена кнопка "Обучающие видео"'); log_window.itemconfig(END, bg='#efedff');
    log_window.insert(END, '  Перейдя по которой можно с ними ознакомиться'); log_window.itemconfig(END, bg='#efedff');
    log_window.insert(END, '  P.S. Гуру шахмат вы не станете, но играть научитесь :)'); log_window.itemconfig(END, bg='#efedff');
    log_window.insert(END, '-'*100); log_window.itemconfig(END, bg='#efedff');
    log_window.insert(END, ' '*35+'История ходов'); log_window.itemconfig(END, bg='#efedff');
    log_window.insert(END, ' '*100);

    arrange_the_figures(mode='Chess')


#Функция play_checkers подготавливает поле для игры в "Шахматы"
def play_checkers():
    global buttons, from_pos, to_Pos, turn, binary_history, del_history, eaten_figures, white_nord_status, black_nord_status
    global log_window
    from_pos, to_pos = None, None
    turn = 'white'
    binary_history = []
    del_history = []
    eaten_figures = {'white': [], 'black': []}
    white_nord_status, black_nord_status = False, False
    blow_up_the_white_nord.place_forget(); blow_up_the_black_nord.place_forget()

    #Окно с логами
    log_window = Listbox(root, bg='#e8e8e8', selectmode=SINGLE, font=('Arial', 10, 'bold'), fg='blue', relief=RIDGE, bd=10)
    scroll = Scrollbar(log_window, command=log_window.yview)
    scroll.pack(side=RIGHT, fill=Y);
    log_window.config(yscrollcommand=scroll.set)
    log_window.place(x=1065, y=200, width=420, height=500)
    log_window.insert(END, '-'*100); log_window.itemconfig(END, bg='#efedff');
    log_window.insert(END, '           Добро пожаловать в проект "Шашки"'); log_window.itemconfig(END, bg='#efedff');
    log_window.insert(END, '  Если вы вдруг не знаете правил этой замечательной'); log_window.itemconfig(END, bg='#efedff');
    log_window.insert(END, '  игры, то специально для вас в правом нижнем углу'); log_window.itemconfig(END, bg='#efedff');
    log_window.insert(END, '  Расположена кнопка "Обучающие видео"'); log_window.itemconfig(END, bg='#efedff');
    log_window.insert(END, '  Перейдя по которой можно с ними ознакомиться'); log_window.itemconfig(END, bg='#efedff');
    log_window.insert(END, '  P.S. Гуру шахмат вы не станете, но играть научитесь :)'); log_window.itemconfig(END, bg='#efedff');
    log_window.insert(END, '-'*100); log_window.itemconfig(END, bg='#efedff');
    log_window.insert(END, ' '*35+'История ходов'); log_window.itemconfig(END, bg='#efedff');
    log_window.insert(END, ' '*100);

    arrange_the_figures(mode='Checkers')


#====================================| ПОДГОТОВКА НЕОБХОДИМЫХ ПЕРЕМЕННЫХ |===========================================#
buttons = {} #<--- В этом словаре хранятся все кнопки по своим адресам: A1, C6 и т.д
from_pos, to_pos = None, None #<--- Переменные начальных и конечных позиций. Нужно для удобной координации
step_sound = mixer.Sound("sounds/step-sound.wav") #<--- Звук хода
nord_sound = mixer.Sound("sounds/nord-sound.wav") #<--- Звук Норда
null_png = PhotoImage(file='images/pieces/null.png')
null_png_attack = PhotoImage(file='images/pieces/attack/null.png')
turn = 'white' #Переменная будет меняться с white на black и обратно. Нужно для того, чтобы фигуры ходили строко по очереди
lessons = listdir('videos')[::-1] #<--- Массив, содержащий названия видеороликов (нужно для запуска)
binary_history = [] #<--- Двумерный массив, в подмассивах которого хранится вся информация о ходах. Далее при желании игрока сохраняется в файл модулем Pickle
del_history = [] #<--- Тот же двумерный массив, но сюда будут записывать ходы "назад", чтоб потом можно было к ним снова вернуться
figure_images = { f'{color}_{role}': PhotoImage(file=f'images/pieces/{color}_{role}.png') for color in ['white', 'black'] for role in ['queen', 'rook', 'elephant', 'horse', 'pawn', 'nikita', 'ramazan', 'nord', 'checker'] }
eaten_figures = {'white': [], 'black': []}
white_nord_status, black_nord_status = False, False




#=====================================| ПОДГОТОВКА НЕОБХОДИМЫХ КАРТИНОК |============================================#
#КАРТИНКИ, ГОВОРЯЩИЕ, ЧЕЙ ХОД СЕЙЧАС: БЕЛЫХ ИЛИ ЧЁРНЫХ. ОТОБРАЖАЮТСЯ С БОКУ ОКНА
turn_white = PhotoImage(file='images/turn_white.png')
turn_black = PhotoImage(file='images/turn_black.png')

#НАСТРОЙКА ОКНА ПРИЛОЖЕНИЯ
root['bg'] = '#996e17'
root.title('Проект "Шахматы" | Рамазан, Настя, Никита')
root.geometry('1500x850+200+100');
root.resizable(width=False, height=False)

#НАСТРОЙКА ЗАДНЕГО ФОНА ОКНА
background_image_chess = PhotoImage(file='images/background_chess.png')
background_image_checkers = PhotoImage(file='images/background_checkers.png')
label = Label(root, image=background_image_chess)
label.place(x=-2, y=0)

#КАРТИНКИ ДЛЯ КНОПОК "СОХРАНИТЬ"
save_the_placement_button_image = PhotoImage(file='images/save_the_placement_button.png')
load_the_placement_button_image = PhotoImage(file='images/load_the_placement_button.png')
load_the_placement_image = PhotoImage(file='images/load_the_placement.png')
remove_the_placement_image = PhotoImage(file='images/remove_the_placement.png')

#КАРТИНКИ ДЛЯ КНОПКИ "ОБУЧАЮЩИЕ ВИДЕОРОЛИКИ" И "СМОТРЕТЬ ВИДЕО"
help_button_image = PhotoImage(file='images/open_the_help_window.png')
watch_the_video_image = PhotoImage(file='images/watch_the_video.png')

#КАРТИНКА ДЛЯ КНОПКИ "ВЫБРАТЬ ФИГУРУ"
its_time_to_change_the_pawn = PhotoImage(file='images/its_time_to_change_the_pawn.png')

#КАРТИНКИ ДЛЯ КНОПОК "ХОД НАЗАД" И "ХОД ВПЕРЁД"
undo_button_image = PhotoImage(file='images/undo_btn.png')
back_button_image = PhotoImage(file='images/back_btn.png')





#============================================| ОСТАЛЬНЫЕ ВИДЖЕТЫ |===================================================#
#Label, который горит либо белым цветом, либо чёрным (чтоб знать, чья очередь ходить в конкретный момент времени)
color_label = Label(root, image=turn_white)
color_label.place(x=0, y=0, width=100, height=900)

#КНОПКА "СОХРАНИТЬ" РАССТАНОВКУ
save_the_placement = Button(root, image=save_the_placement_button_image, command=save, relief=FLAT)
save_the_placement.place( x=1148, y=702, width=120, height=45 )

#КНОПКА "ЗАГРУЗИТЬ" РАССТАНОВКУ
load_the_placement = Button(root, image=load_the_placement_button_image, command=load, relief=FLAT)
load_the_placement.place( x=1275, y=702, width=120, height=45 )

#КНОПКА, ОТКРЫВАЮЩАЯ ОКНО С ОБУЧАЮЩИМИ ВИДЕОРОЛИКАМИ
help_button = Button(root, command=help_window, image=help_button_image, relief=RIDGE)
help_button.place(x=1200, y=800, width=300, height=50)

#КНОПКА "ХОД НАЗАД"
undo_button = Button(root, image=undo_button_image, command=undo, relief=FLAT, state=DISABLED)
undo_button.place(x=970, y=108, width=35, height=35)

#КНОПКА "ХОД ВПЕРЁД"
back_button = Button(root, image=back_button_image, command=back, relief=FLAT, state=DISABLED)
back_button.place(x=1010, y=108, width=35, height=35)

#КНОПКИ "ВЗОРВАТЬ НОРДА"
blow_up_the_white_nord = Button(root, image = Nord('white')._image, bg='white', command=lambda: blow_up_the_nord(white_nord_status))
blow_up_the_black_nord = Button(root, image = Nord('black')._image, bg='black', command=lambda: blow_up_the_nord(black_nord_status))

#КНОПКИ "ШАХМАТЫ" и "ШАШКИ"
choose_the_chess_mode = Button(root, image=figure_images['white_pawn'], command=play_chess)
choose_the_checkers_mode = Button(root, image=figure_images['white_checker'], command=play_checkers)
choose_the_chess_mode.place(x=200, y=400, width=75, height=75)
choose_the_checkers_mode.place(x=200, y=500, width=75, height=75)

#УДОБНАЯ КНОПКА ДЛЯ ТЕСТИРОВКИ. ВЫВОДИТ ВИД БИНАРНОЙ ИСТОРИИ И УДАЛЁННОЙ БИНАРНОЙ ИСТОРИИ
def a():
    print('\n'*3)
    print( '='*124 + f'\n{binary_history}\n\n\n{del_history}\n' + '='*124 )

# Button(root, bg='red', command=a).place(x=500, y=20, width=400, height=30)






#===================================| СОЗДАНИЕ ИГРОВОГО ПОЛЯ И ЗАПУСК ИГРЫ |==========================================#
#СОЗДАНИЕ ОБЛАСТЬ ИГРОВОГО ПОЛЯ
game_field = Frame(root, padx=0, pady=0)
game_field.place(x=450, y=150, width=600, height=600)

#ГЕНЕРИРУЕМ КЛЕТКИ ИГРОВОГО ПОЛЯ
for digit in range(8, 0, -1):
    for letter in 'ABCDEFGH':
        x = {'A': 0, 'B': 75, 'C': 150, 'D': 225, 'E': 300, 'F': 375, 'G': 450, 'H': 525}[letter]
        y = (8-digit)*75
        button = Button(game_field, bg=['#EBECD0', '#779556'][(digit+ord(letter))%2])
        button.coord = letter+str(digit)
        button.configure(command = lambda coord=button.coord: choose_cell(coord))
        button.x, button.y = x, y
        buttons |= {letter+str(digit): button}
        button.place(x=x, y=y, width=75, height=75)

play_chess() #<--- Вызываем функцию расстановки фигур по клеткам

# buttons['A5'].figure = Nikita('white')
# buttons['B5'].figure = Nikita('black')
# buttons['C5'].figure = Nord('white')
# buttons['D5'].figure = Nord('black')
# buttons['E5'].figure = Ramazan('white')
# buttons['F5'].figure = Ramazan('black')

root.mainloop() #<--- Финальная стадия: запускаем игровое окно