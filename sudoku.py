import random


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
    def _rand_gen():
        get_next = lambda: random.SystemRandom().randint(1, 9)
        used = set()
        while len(used) < 9:
            if (n := get_next()) in used:
                continue
            used.add(n)
            yield n

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
        if val is not None and (not isinstance(val, int)) or (val is not None and (1 > val or val > 9)):
            raise ValueError('Value must be 1~9 or None')

        self._check_value(val, *xy)

        super().__setitem__(xy, val)

    def empty_cells_iter(self):
        for y in range(9):
            for x in range(9):
                if not self[x, y]:
                    yield (x, y)

    def solutions_iter(self, use_random=False):
        try:
            x, y = next(self.empty_cells_iter())
        except StopIteration:
            yield self
            return

        gen = self._rand_gen() if use_random else range(1, 10)
        for n in gen:
            b = Sudoku(self)
            try:
                b[x, y] = n
            except SudokuError:
                continue
            yield from b.solutions_iter(use_random)

    def solve(self, use_random=False):
        try:
            return next(self.solutions_iter(use_random))
        except StopIteration:
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
        pass

    @classmethod
    def random(cls):
        return cls().solve(use_random=True)


def main():
    # print(Sudoku.random())
    # for b in Sudoku().solutions_iter(True):
    #     print(b)
    # return
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
                # print(f'{len(list(nb.solutions_iter()))} solutions')
    return
    for n, solution in enumerate(b.solutions_iter(), 1):
        print(f'Solution #{n}:')
        print(solution)


if __name__ == "__main__":
    main()
