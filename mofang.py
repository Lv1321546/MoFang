from __future__ import annotations

"""mofang.py
纯 Python 三阶魔方模型（RubiksCube）。
作者: Cascade AI
"""

import random
from typing import Dict, List, Tuple

Face = List[List[str]]  # 3x3 矩阵
State = Dict[str, Face]

# 顺/逆方向常量
CW = 1   # clockwise
CCW = -1  # counter-clockwise


class RubiksCube:
    """三阶魔方模型，支持基本旋转、打乱与展示。"""

    _face_order = ["U", "L", "F", "R", "B", "D"]  # 展示时使用固定顺序

    _default_colors = {
        "U": "W",  # White
        "D": "Y",  # Yellow
        "L": "G",  # Green
        "R": "B",  # Blue
        "F": "R",  # Red
        "B": "O",  # Orange
    }

    def __init__(self) -> None:
        """初始化魔方为复原状态。"""
        self.state: State = {
            face: [[color] * 3 for _ in range(3)]
            for face, color in self._default_colors.items()
        }

    # ------------------------------------------------------------------
    # 基础工具
    # ------------------------------------------------------------------
    @staticmethod
    def _rotate_face(face: Face, direction: int) -> Face:
        """旋转单个面 90°。
        direction: CW(1) 顺时针, CCW(-1) 逆时针
        """
        if direction not in {CW, CCW}:
            raise ValueError("direction must be 1 (CW) or -1 (CCW)")
        if direction == CW:
            # 逆序转置
            return [list(row) for row in zip(*face[::-1])]
        else:  # CCW
            # 转置逆序
            return [list(row) for row in zip(*face)][::-1]

    # ------------------------------------------------------------------
    # 旋转逻辑核心
    # ------------------------------------------------------------------
    def rotate(self, face: str, direction: int = CW) -> None:
        """旋转指定面的层。仅支持 90° CW/CCW。
        face: 'U','D','L','R','F','B'
        direction: 1 顺时针, -1 逆时针
        """
        if face not in self.state:
            raise ValueError(f"Invalid face: {face}")
        if direction not in {CW, CCW}:
            raise ValueError("direction must be 1 or -1")

        # 1. 旋转自身面
        self.state[face] = self._rotate_face(self.state[face], direction)

        # 2. 处理邻边条带循环（依据官方 sticker 编号）
        self._cycle_edges(face, direction)

    # 每个面相邻四条带的定义 (face -> list[ (adj_face, index_getter, index_setter) ])
    # 为简化，使用辅助函数在 _cycle_edges 内部一次性 hard-code 逻辑。
    def _cycle_edges(self, face: str, direction: int) -> None:
        """按照 WCA 定义（从该面正对观察者看过去的顺时针）循环交换邻边。

        说明：
        - 每次旋转某一面，除了该面 3x3 自身旋转外，还会影响与其相邻的 4 个面的 1 条边（行/列）。
        - 这里把“受影响的 4 条边”抽取出来，按顺/逆时针做循环，再写回。
        - 对于 B 面，由于观察方向与我们存储的面朝向相反，需要在映射时显式处理反转。
        """
        s = self.state

        def get_row(f: str, r: int) -> List[str]:
            return s[f][r][:]

        def set_row(f: str, r: int, vals: List[str]) -> None:
            s[f][r] = vals[:]

        def get_col(f: str, c: int) -> List[str]:
            return [s[f][r][c] for r in range(3)]

        def set_col(f: str, c: int, vals: List[str]) -> None:
            for r in range(3):
                s[f][r][c] = vals[r]

        # 为避免“读一边写一边”导致串扰：先把 4 条边完整取出
        if face == "U":
            # 受影响边：F 顶行、R 顶行、B 顶行、L 顶行
            # U 顺时针：L -> F -> R -> B -> L
            a = get_row("F", 0)
            b = get_row("R", 0)
            c = get_row("B", 0)
            d = get_row("L", 0)
            if direction == CW:
                set_row("F", 0, d)
                set_row("R", 0, a)
                set_row("B", 0, b)
                set_row("L", 0, c)
            else:
                set_row("F", 0, b)
                set_row("R", 0, c)
                set_row("B", 0, d)
                set_row("L", 0, a)
            return

        if face == "D":
            # 受影响边：F 底行、R 底行、B 底行、L 底行
            # D 顺时针（从 D 面看）：L -> F -> R -> B -> L
            a = get_row("F", 2)
            b = get_row("R", 2)
            c = get_row("B", 2)
            d = get_row("L", 2)
            if direction == CW:
                set_row("F", 2, d)
                set_row("R", 2, a)
                set_row("B", 2, b)
                set_row("L", 2, c)
            else:
                set_row("F", 2, b)
                set_row("R", 2, c)
                set_row("B", 2, d)
                set_row("L", 2, a)
            return

        if face == "R":
            # 受影响边：U 右列、F 右列、D 右列、B 左列（注意 B 需要反向）
            # R 顺时针：U -> F -> D -> B -> U
            a = get_col("U", 2)
            b = get_col("F", 2)
            c = get_col("D", 2)
            d = get_col("B", 0)[::-1]
            if direction == CW:
                set_col("F", 2, a)
                set_col("D", 2, b)
                set_col("B", 0, c[::-1])
                set_col("U", 2, d)
            else:
                set_col("F", 2, c)
                set_col("D", 2, d)
                set_col("B", 0, a[::-1])
                set_col("U", 2, b)
            return

        if face == "L":
            # 受影响边：U 左列、F 左列、D 左列、B 右列（注意 B 需要反向）
            # L 顺时针：U -> B -> D -> F -> U（等价写成 U<-F<-D<-B<-U 的反向）
            a = get_col("U", 0)
            b = get_col("F", 0)
            c = get_col("D", 0)
            d = get_col("B", 2)[::-1]
            if direction == CW:
                set_col("B", 2, a[::-1])
                set_col("D", 0, d)
                set_col("F", 0, c)
                set_col("U", 0, b)
            else:
                set_col("B", 2, c[::-1])
                set_col("D", 0, b)
                set_col("F", 0, a)
                set_col("U", 0, d)
            return

        if face == "F":
            # 受影响边：U 底行、R 左列、D 顶行、L 右列（其中两处需要反向）
            # F 顺时针：U -> R -> D -> L -> U
            a = get_row("U", 2)
            b = get_col("R", 0)
            c = get_row("D", 0)
            d = get_col("L", 2)
            if direction == CW:
                set_col("R", 0, a[::-1])
                set_row("D", 0, b)
                set_col("L", 2, c[::-1])
                set_row("U", 2, d)
            else:
                set_col("R", 0, c)
                set_row("D", 0, d[::-1])
                set_col("L", 2, a)
                set_row("U", 2, b[::-1])
            return

        if face == "B":
            # 受影响边：U 顶行、L 左列、D 底行、R 右列（多处需要反向）
            # B 顺时针（从 B 面看）：U -> L -> D -> R -> U
            a = get_row("U", 0)
            b = get_col("L", 0)
            c = get_row("D", 2)
            d = get_col("R", 2)
            if direction == CW:
                set_col("L", 0, a)
                set_row("D", 2, b[::-1])
                set_col("R", 2, c)
                set_row("U", 0, d[::-1])
            else:
                set_col("L", 0, c[::-1])
                set_row("D", 2, d)
                set_col("R", 2, a[::-1])
                set_row("U", 0, b)
            return

        raise NotImplementedError

    # ------------------------------------------------------------------
    # 高级接口
    # ------------------------------------------------------------------
    def move(self, sequence: str) -> None:
        """按 WCA 标准公式字符串执行多个基础转动。
        例如: "R U R' U'" 或 "F2 D L'"。
        """
        tokens = sequence.strip().split()
        for tok in tokens:
            if tok[-1] == "2":
                turns = 2
                face = tok[:-1]
                dir_sign = CW
            elif tok.endswith("'"):
                turns = 1
                face = tok[0]
                dir_sign = CCW
            else:
                turns = 1
                face = tok[0]
                dir_sign = CW
            for _ in range(turns):
                self.rotate(face, dir_sign)

    def scramble(self, steps: int = 20) -> str:
        """生成随机打乱序列并执行。返回 scramble 字符串。"""
        faces = list(self.state.keys())
        seq: List[str] = []
        prev_face = ""
        for _ in range(steps):
            face = random.choice([f for f in faces if f != prev_face])
            mod = random.choice(["", "'", "2"])
            seq.append(face + mod)
            prev_face = face
        scramble_str = " ".join(seq)
        self.move(scramble_str)
        return scramble_str

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------
    def is_solved(self) -> bool:
        """检查每个面是否全部为同一颜色。"""
        for face, grid in self.state.items():
            center = grid[1][1]
            if any(cell != center for row in grid for cell in row):
                return False
        return True

    def __str__(self) -> str:  # noqa: D401
        return self._build_display()

    def _build_display(self) -> str:
        """生成十字展开字符串。"""
        s = self.state
        def fmt_face(f: Face) -> List[str]:
            return [" ".join(row) for row in f]
        U, L, F, R, B, D = (fmt_face(s[f]) for f in ["U", "L", "F", "R", "B", "D"])
        # 拼接
        lines: List[str] = []
        spacer = " " * 6
        for r in range(3):
            lines.append(spacer + U[r])
        for r in range(3):
            lines.append(" ".join([L[r], F[r], R[r], B[r]]))
        for r in range(3):
            lines.append(spacer + D[r])
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # 复制与比较
    # ------------------------------------------------------------------
    def copy(self) -> "RubiksCube":
        new_cube = RubiksCube()
        new_cube.state = {f: [row[:] for row in face] for f, face in self.state.items()}
        return new_cube


# ----------------------------------------------------------------------
# Demo
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # 最小自检：每个基本转动做 4 次应回到初始状态；X 后 X' 应复原
    for f in ["U", "D", "L", "R", "F", "B"]:
        c = RubiksCube()
        c.move(f"{f} {f} {f} {f}")
        assert c.is_solved(), f"自检失败: {f}^4 应复原"
        c = RubiksCube()
        c.move(f"{f} {f}'")
        assert c.is_solved(), f"自检失败: {f} 后 {f}' 应复原"

    cube = RubiksCube()
    print("初始状态:")
    print(cube)
    print("已还原?", cube.is_solved())

    formula = "R U R' U'"
    cube.move(formula)
    print("\n执行公式:", formula)
    print(cube)
    print("已还原?", cube.is_solved())

    # 复原后打乱
    cube = RubiksCube()
    scramble_seq = cube.scramble(20)
    print("\nScramble:", scramble_seq)
    print(cube)
    print("已还原?", cube.is_solved())

