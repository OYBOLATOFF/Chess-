from tkinter import PhotoImage

#КЛАССЫ ФИГУР
#Класс "Фигура" - родитель всех дочерних классов (Pawn, Horse, Elephant, Queen, King, Rook)
class Figure:
    figures = []
    def __init__(self, color=False, role=False):
        self._color = color
        self._role = role
        self.step = 0
        if self._role:
            self._image = PhotoImage(file=f'images/pieces/{self._color}_{self._role}.png')
            self._image_attack = PhotoImage(file=f'images/pieces/attack/{self._color}_{self._role}.png')
        else:
            self._image = PhotoImage(file=f'images/pieces/null.png')
            self._image_attack = PhotoImage(file=f'images/pieces/attack/null.png')

    @property
    def color(self):
        return self._color

    @property
    def role(self):
        return self._role
    
    

#Класс Пешки, наследуется от родительского класса Figure
class Pawn(Figure):
    def __init__(self, color):
        super().__init__(color, 'pawn')
        Figure.figures.append(self)

#Класс шашки, наследуется от родительского класса Figure
class Checker(Figure):
    def __init__(self, color):
        super().__init__(color, 'checker')
        Figure.figures.append(self)

#Класс Коня, наследуется от родительского класса Figure
class Horse(Figure):
    def __init__(self, color):
        super().__init__(color, 'horse')
        Figure.figures.append(self)

#Класс Слона, наследуется от родительского класса Figure
class Elephant(Figure):
    def __init__(self, color):
        super().__init__(color, 'elephant')
        Figure.figures.append(self)

#Класс Ферзя, наследуется от родительского класса Figure
class Queen(Figure):
    def __init__(self, color):
        super().__init__(color, 'queen')
        Figure.figures.append(self)

#Класс Короля, наследуется от родительского класса Figure
class King(Figure):
    def __init__(self, color):
        super().__init__(color, 'king')
        Figure.figures.append(self)

#Класс Ладьи, наследуется от родительского класса Figure
class Rook(Figure):
    def __init__(self, color):
        super().__init__(color, 'rook')
        Figure.figures.append(self)

#Класс Никиты, наследуется от родительского класса Figure
class Nikita(Figure):
    def __init__(self, color):
        super().__init__(color, 'nikita')
        Figure.figures.append(self)

#Класс Норда, наследуется от родительского класса Figure
class Nord(Figure):
    def __init__(self, color):
        super().__init__(color, 'nord')
        Figure.figures.append(self)

#Класс Ramazan, наследуется от родительского класса Figure
class Ramazan(Figure):
    def __init__(self, color):
        super().__init__(color, 'ramazan')
        Figure.figures.append(self)