import random
import statistics


class Matrix9x9:
    def __init__(self):
        self._cells = [None] * 81

    def __str__(self):
        #return '\n'.join(''.join(str(self[x, y] or '.') for x in range(9)) for y in range(9))
        ret = '╔═══╤═══╤═══╦═══╤═══╤═══╦═══╤═══╤═══╗\n'
        for i in range(0, 81, 9):
            sep = iter('││║' * 3)
            ret += '║' + ''.join(' ' + str(v or ' ') + ' ' + next(sep) for v in self._cells[i:i + 9]) + '\n'
            if i == 72:
                ret += '╚═══╧═══╧═══╩═══╧═══╧═══╩═══╧═══╧═══╝'
            elif i % 27 == 18:
                ret += '╠═══╪═══╪═══╬═══╪═══╪═══╬═══╪═══╪═══╣\n'
            else:
                ret += '╟───┼───┼───╫───┼───┼───╫───┼───┼───╢\n'
        return ret

    @staticmethod
    def _idx(x, y):
        assert 0 <= x <= 8
        assert 0 <= y <= 8
        return 9 * y + x

    def __getitem__(self, xy):
        return self._cells[self._idx(*xy)]

    def __setitem__(self, xy, val):
        self._cells[self._idx(*xy)] = val

    def get_row(self, y):
        return self._cells[9 * y:9 * (y + 1)]

    def get_column(self, x):
        return self._cells[x::9]


class SudokuError(Exception):
    pass


class Sudoku(Matrix9x9):
    @staticmethod
    def _number_gen(choices=None, randomize=False):
        choices = list(choices or [1, 2, 3, 4, 5, 6, 7, 8, 9])
        if randomize:
            choices.sort(key=lambda x: random.SystemRandom().random())
        while choices:
            yield choices.pop(0)

    def __init__(self, init=None):
        if init is None:
            self._cells = [None] * 81
        elif isinstance(init, Sudoku):
            self._cells = init._cells.copy()
        elif isinstance(init, (list, tuple)):
            self._cells = init.copy()
            self._check_board()
        else:
            raise ValueError('Bad init value')

    def get_box(self, n):
        i = n % 3 * 3 + n // 3 * 27
        return sum((self._cells[i+k*9:i+k*9+3] for k in range(3)), [])

    @staticmethod
    def get_box_number(x, y):
        return x // 3 + y // 3 * 3

    def get_box_xy(self, x, y):
        return self.get_box(self.get_box_number(x, y))

    def _check_board(self):
        for y in range(9):
            row = list(filter(None, self.get_row(y)))
            if len(row) != len(set(row)):
                raise SudokuError('duplicate value in row {}'.format(y + 1))

        for x in range(9):
            col = list(filter(None, self.get_column(x)))
            if len(col) != len(set(col)):
                raise SudokuError('duplicate value in column {}'.format(x + 1))

        for b in range(9):
            box = list(filter(None, self.get_box(b)))
            if len(box) != len(set(box)):
                raise SudokuError('duplicate value in box {}'.format(b + 1))

    def _check_value(self, val, x, y):
        if not val:
            return

        if val in self.get_row(y):
            raise SudokuError('duplicate value in row {} ({})'.format(y + 1, val))

        if val in self.get_column(x):
            raise SudokuError('duplicate value in column {} ({})'.format(x + 1, val))

        bn = self.get_box_number(x, y)
        if val in self.get_box(bn):
            raise SudokuError('duplicate value in box {} ({})'.format(bn + 1, val))

    def __setitem__(self, xy, val):
        if val is not None and (not isinstance(val, int)) or (val is not None and (val < 1 or val > 9)):
            raise ValueError('Value must be 1~9 or None')

        self._check_value(val, *xy)

        super().__setitem__(xy, val)

    def possible_values(self, x, y):
        return ({1, 2, 3, 4, 5, 6, 7, 8, 9}
                .difference(
                    self.get_row(y) +
                    self.get_column(x) +
                    self.get_box_xy(x, y)
                )
                .union([self[x, y]])
                .difference([None]))

    def empty_cells_iter(self):
        for y in range(9):
            for x in range(9):
                if not self[x, y]:
                    yield (x, y)

    def solutions_iter(self, randomize=False):
        # Make a list of all holes and their possible values
        # sorted by number of possible values
        # [ [] (x, y), possible_values, generator ], ... ]
        possibles = []
        for x, y in self.empty_cells_iter():
            pv = self.possible_values(x, y)
            possibles.append([
                (x, y),
                pv,
                None,
            ])

        # No holes - solved board
        if not possibles:
            yield self
            return

        possibles = list(sorted(possibles, key=lambda x: len(x[1])))

        # A hole can hold no value - unsolvable board
        if not possibles[0][1]:
            return

        # Copy board for solving
        b = Sudoku(self)

        cur = 0

        while cur >= 0:
            p = possibles[cur]
            (x, y), pv, gen = p
            if gen is None:
                gen = self._number_gen(b.possible_values(x, y), randomize)
                p[2] = gen

            for n in gen:
                try:
                    b[x, y] = n
                except SudokuError:
                    continue
                cur += 1
                break
            else:
                b[x, y] = None
                p[2] = None
                cur -= 1
                continue

            if cur == len(possibles):
                yield b
                cur -= 1

    def solve(self, randomize=False):
        for solution in self.solutions_iter(randomize):
            return solution
        raise SudokuError('No solutions')

    def only_one_solution(self):
        g = self.solutions_iter()

        try:
            next(g)
        except StopIteration:
            raise SudokuError('No solutions')

        try:
            next(g)
        except StopIteration:
            return True

        return False

    @property
    def solvable(self):
        try:
            self.solve()
        except SudokuError:
            return False
        return True

    @property
    def grade(self):
        m = statistics.mean(
            [self._cells.count(d) for d in range(1, 10)] +
            [
                statistics.mean(
                    [len(list(filter(None, self.get_row(y)))) for y in range(9)] +
                    [len(list(filter(None, self.get_column(x)))) for x in range(9)] +
                    [len(list(filter(None, self.get_box(b)))) for b in range(9)]
                )
            ]
        )
        return 1 - (m / 9)

    @classmethod
    def random(cls):
        return cls().solve(randomize=True)

    @classmethod
    def generate_puzzle(cls, min_grade, parent=None):
        b = parent or cls.random()

        while 1:
            nb = cls(b)
            nb[random.randint(0, 8), random.randint(0, 8)] = None
            print(nb)
            print(f'Grade: {nb.grade}')
            if nb.only_one_solution():
                break
            print('No single solution. Backtrack.')

        if b.grade >= min_grade:
            return b

        return cls.generate_puzzle(min_grade, nb)


def main():
    if 0:
        print(Sudoku.random())
        return

    if 0:
        for b in Sudoku().solutions_iter(randomize=True):
            print(b)
        return

    if 0:
        b = Sudoku.generate_puzzle(1)
        print(b)
        print(f'Grade: {b.grade}')
        return

    x = None
    b = Sudoku([x, 8, x, x, 1, 5, x, x, x] +
               [6, x, x, x, 9, 2, x, x, 8] +
               [3, x, x, 4, x, x, x, 6, x] +
               [x, 9, 3, x, x, 6, x, x, 4] +
               [x, 5, x, x, x, x, x, 2, x] +
               [7, x, x, 5, x, x, 9, 1, x] +
               [x, 6, x, x, x, 4, x, x, 2] +
               [2, x, x, 8, 6, x, x, x, 5] +
               [x, x, x, 9, 2, x, x, 8, x])
    print(b)
    print(f'Grade: {b.grade}')
    print(b.solve())


if __name__ == "__main__":
    main()
