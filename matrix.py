# -*- coding: utf-8 -*-
from typing import List, Callable, Union


class Matrix:
    """行列クラス。

    行列の演算をここで定義します。

    例えば 2 行 3 列の行列を作りたい場合、次のようにします。 ::

        matrix = Matrix([
            [1, 2, 3],
            [4, 5, 6],
        ])

    **各行の長さはすべて同じでなければなりません。**

    :ivar count_row: 行数
    :ivar count_col: 列数
    :ivar rows: 行列自身
    """

    def __init__(self, rows: List[List[float]]) -> None:
        """

        :param rows:
        :raises ValueError if the matrix is invalid.
        """
        self.__set_rows(rows)

    def __set_rows(self, rows: List[List[float]]) -> None:
        """バリデーションを行い、インスタンス変数を設定します。

        :param rows:
        :raises ValueError if the matrix is invalid.
        """
        # validate input
        count_row = len(rows)
        if count_row == 0:
            raise ValueError('matrix cannot be empty')
        count_col = len(rows[0])
        if count_col == 0:
            raise ValueError('matrix cannot be empty')
        for i in range(1, len(rows)):
            if len(rows[i]) != count_col:
                raise ValueError('all rows must be the same length')

        self.count_row = count_row
        self.count_col = count_col
        self.rows = rows

    def __str__(self) -> str:
        """行列を表示します。

        :return: str to display.
        """
        return '\n'.join(' '.join(map(str, row)) for row in self.rows)

    def __validate_size(self, other: 'Matrix') -> None:
        """配列のサイズが一致しているかどうか調べます。

        :param other:
        :raises ValueError if the counts of row or col of two matrices are different.
        """
        if self.count_row != other.count_row:
            raise ValueError('row count must be the same')
        if self.count_col != other.count_col:
            raise ValueError('col count must be the same')

    def __calculate_each_element(self, other: 'Matrix', operation: Callable[[float, float], float]) -> 'Matrix':
        """配列の行番号・列番号が一致する要素同士で計算をします。

        :param other:
        :param operation:
        :return: new matrix.
        """
        rows = []
        for i in range(self.count_row):
            row = []
            for j in range(self.count_col):
                row.append(operation(float(self.rows[i][j]), float(other.rows[i][j])))  # 番号が一致する要素同士を計算する
            rows.append(row)

        return Matrix(rows)

    def __add__(self, other: 'Matrix') -> 'Matrix':
        """足し算「+」の動作を定義します。

        :param other:
        :return: new matrix.
        """
        self.__validate_size(other)  # 行列のサイズを調べて
        return self.__calculate_each_element(other, float.__add__)  # 各成分を数値の足し算のルールで計算する

    def __sub__(self, other: 'Matrix') -> 'Matrix':
        """引き算「－」の動作を定義します。

        :param other:
        :return: new matrix.
        """
        self.__validate_size(other)  # 行列のサイズを調べて
        return self.__calculate_each_element(other, float.__sub__)  # 各成分を数値の引き算のルールで計算する

    def __matmul__(self, other: 'Matrix') -> 'Matrix':
        """行列同士の掛け算を定義します。

        :param other:
        :return: new matrix.
        """
        if self.count_col != other.count_row:
            raise ValueError('the col count in the first matrix must be equal to the row count in the second matrix')

        rows = []
        for i in range(self.count_row):
            row = []
            for j in range(other.count_col):
                col = Matrix.__calculate_each_element(
                    Matrix([self.rows[i]]),  # 左側の行列の i 行目と
                    Matrix([[other.rows[k][j] for k in range(other.count_row)]]),  # 右側の行列の j 列目で
                    float.__mul__,  # 各成分を掛け算したものを
                )
                row.append(sum(col.rows[0]))  # 合わせる
            rows.append(row)

        return Matrix(rows)

    def __mul__(self, other: 'Scalar') -> 'Matrix':
        """行列にスカラーを掛ける演算を定義します。

        :param other:
        :return: new matrix.
        """
        if type(other) == Matrix:
            raise TypeError('matrix multiplication via * is not supported (use @ instead)')

        scalar = [[other.value for _ in range(self.count_col)] for _ in range(self.count_row)]
        return self.__calculate_each_element(Matrix(scalar), float.__mul__)

    def __rmul__(self, other: 'Scalar') -> 'Matrix':
        return self.__mul__(other)

    def __abs__(self) -> float:
        """行列式を求める演算を定義します。

        :return:
        """
        if self.count_row != self.count_col:
            raise AttributeError('determinant supports only square matrix')

        if self.count_row == 1:
            return self.rows[0][0]
        return sum(
            (-1) ** i * self.rows[i][0] * abs(Matrix([
                [col for _j, col in enumerate(row) if _j != 0]
                for _i, row in enumerate(self.rows) if _i != i
            ]))
            for i in range(self.count_row)
        )

    def __get_inverse_matrix(self) -> 'Matrix':
        """逆行列を取得します。

        :return:
        """
        if self.count_row != self.count_col:
            raise AttributeError('determinant supports only square matrix')
        self.__validate_size(self)

        det = self.__abs__()
        if det == 0:
            raise ZeroDivisionError('determinant is 0')
        return Matrix([
            [
                (-1) ** (i + j) * abs(Matrix([
                    # 転置するのでインデックスは逆にする
                    [col for _i, col in enumerate(row) if _i != i]
                    for _j, row in enumerate(self.rows) if _j != j
                ]))
                for j in range(self.count_col)
            ]
            for i in range(self.count_row)
        ]) / Scalar(det)

    def __truediv__(self, other: Union['Scalar', 'Matrix']) -> 'Matrix':
        """行列の割り算を定義します。

        逆行列を掛けることに相当します。

        :param other:
        :return:
        """
        t = type(other)

        if t == Scalar:
            other: Scalar
            return self.__calculate_each_element(
                Matrix([[other.value for _ in range(self.count_col)] for row in range(self.count_row)]),
                float.__truediv__,
            )

        if t == Matrix:
            other: Matrix
            return self @ other.__get_inverse_matrix()

        raise TypeError('matrix cannot be divided the given object')

    def __pow__(self, power: 'Scalar', modulo=None) -> 'Matrix':
        """行列のべき乗を定義します。

        :param power:
        :param modulo: 使用しません。
        :return:
        """
        if modulo is not None:
            raise ValueError('modulo is not supported')
        if type(power) != Scalar:
            raise TypeError('power supports Scalar only')
        if not power.value.is_integer():
            raise ValueError('power supports only integer')

        if power.value == 0:
            if self.count_row != self.count_col:
                raise ValueError('power 0 supports only square matrix')
            # 単位行列
            return Matrix([
                [1 if j == i else 0 for j in range(self.count_col)]
                for i in range(self.count_row)
            ])
        if power.value == 1:
            return self
        if power.value >= 2:
            return self.__pow__(Scalar(power.value - 1)) @ self
        if power.value < 0:
            return self.__get_inverse_matrix().__pow__(Scalar(-power.value))

        raise Exception('unexpected error')


class Scalar(float):
    """Scalar クラス。

    行列との掛け算を定義するために用意します。

    :ivar value: 値
    """

    def __init__(self, v: float) -> None:
        self.value = float(v)  # 整数が来た場合も内部的に変換しておく

    # def __mul__(self, other):
    #     if type(other) == Matrix:
    #         return Matrix.__mul__(other, self)
    #     return super().__mul__(other)
