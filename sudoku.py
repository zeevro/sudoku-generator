import random


class BoardError(Exception):
    pass


class Board:
    def __init__(self, init=None):
        if init is None:
            self._cells = [None] * 81
        elif isinstance(init, Board):
            self._cells = init._cells.copy()
        elif isinstance(init, (list, tuple)):
            self._cells = init.copy()
            self._check_board()
        else:
            raise ValueError('Bad init value')

    @staticmethod
    def _gen_rand():
        get_next = lambda: random.SystemRandom().randint(1, 9)
        used = set()
        while len(used) < 9:
            if (n := get_next()) in used:
                continue
            used.add(n)
            yield n

    @staticmethod
    def _idx(x, y):
        assert 0 <= x <= 8
        assert 0 <= y <= 8
        return 9 * y + x

    def __getitem__(self, c):
        return self._cells[self._idx(*c)]

    def _check_board(self):
        for y in range(0, 72, 9):
            row = list(filter(None, self._cells[y:y + 9]))
            if len(row) != len(set(row)):
                raise BoardError('duplicate value in row {}'.format(y // 9 + 1))

        for x in range(9):
            col = list(filter(None, self._cells[x::9]))
            if len(col) != len(set(col)):
                raise BoardError('duplicate value in column {}'.format(x + 1))

        for b in range(0, 54, 27):
            box = sum((list(filter(None, self._cells[i:i + 3])) for i in range(b, b + 27, 9)), [])
            if len(box) != len(set(box)):
                raise BoardError('duplicate value in box {}'.format(b / 27))

    def _check_value(self, val, x, y):
        if not val:
            return

        row_start = y * 9
        if val in self._cells[row_start:row_start + 9]:
            raise BoardError('duplicate value in row {} ({})'.format(y + 1, val))
        if val in self._cells[x::9]:
            raise BoardError('duplicate value in column {} ({})'.format(x + 1, val))
        bx = (x // 3) * 3
        by = (y // 3) * 3
        for cy in range(by, by + 3):
            i = self._idx(bx, cy)
            if val in self._cells[i:i + 3]:
                raise BoardError('duplicate value in box {} ({})'.format(i // 27 + 1, val))

    def __setitem__(self, c, val):
        if (not isinstance(val, (int, None))) or (val is not None and (1 > val or val > 9)):
            raise ValueError('Value must be 1~9 or None')
        assert val is None or 1 <= val <= 9

        self._check_value(val, *c)

        self._cells[self._idx(*c)] = val

    def __str__(self):
        # return '\n'.join(''.join(str(self[x, y] or '.') for x in range(9)) for y in range(9))
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

        gen = self._gen_rand() if use_random else range(1, 10)
        for n in gen:
            b = Board(self)
            try:
                b[x, y] = n
                yield from b.solutions_iter(use_random)
            except BoardError:
                continue

    def solve(self, use_random=False):
        try:
            return next(self.solutions_iter(use_random))
        except StopIteration:
            raise BoardError('No solutions')

    def ensure_single_solution(self):
        g = self.solutions_iter()
        try:
            next(g)
        except StopIteration:
            raise BoardError('No solutions')

        try:
            next(g)
        except StopIteration:
            return True

        return False

    @property
    def solvable(self):
        try:
            self.solve()
        except BoardError:
            return False
        return True

    @property
    def grade(self):
        pass

    @classmethod
    def random(cls):
        return cls().solve(use_random=True)


def main():
    # print(Board.random())
    for b in Board().solutions_iter(True):
        print(b)
    return
    x = None
    b = Board([x, 8, x, x, 1, 5, x, x, x] +
              [6, x, x, x, 9, 2, x, x, 8] +
              [3, x, x, 4, x, x, x, 6, x] +
              [x, 9, 3, x, x, 6, x, x, 4] +
              [x, 5, x, x, x, x, x, 2, x] +
              [7, x, x, 5, x, x, 9, 1, x] +
              [x, 6, x, x, x, 4, x, x, 2] +
              [2, x, x, 8, 6, x, x, x, 5] +
              [x, x, x, 9, 2, x, x, 8, x])
    print(b)
    print(b.solve())


if __name__ == "__main__":
    main()
