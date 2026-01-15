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
        "L": "O",  # Orange
        "R": "R",  # Red
        "F": "G",  # Green
        "B": "B",  # Blue
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
        """按照给定面的旋转方向，对四条邻边 sticker 进行循环。"""
        s = self.state  # shorthand

        def row(f: str, idx: int) -> List[str]:
            return s[f][idx]

        def col(f: str, idx: int) -> List[str]:
            return [s[f][r][idx] for r in range(3)]

        def set_row(f: str, idx: int, vals: List[str]) -> None:
            s[f][idx] = vals[:]  # copy

        def set_col(f: str, idx: int, vals: List[str]) -> None:
            for r in range(3):
                s[f][r][idx] = vals[r]

        if face == "U":
            strips = [row("B", 0)[::-1], col("R", 0), row("F", 0), col("L", 2)[::-1]]
            # 顺时针视角: F->R->B->L
            order = ["F", "R", "B", "L"]
            data = [row("F", 0), col("R", 0), row("B", 0)[::-1], col("L", 2)[::-1]]
            if direction == CW:
                rot = data[-1:] + data[:-1]
            else:
                rot = data[1:] + data[:1]
            set_row("F", 0, rot[0])
            set_col("R", 0, rot[1])
            set_row("B", 0, rot[2][::-1])
            set_col("L", 2, rot[3][::-1])
            return
        if face == "D":
            data = [row("F", 2), col("R", 2), row("B", 2)[::-1], col("L", 0)[::-1]]
            if direction == CW:
                rot = data[-1:] + data[:-1]
            else:
                rot = data[1:] + data[:1]
            set_row("F", 2, rot[0])
            set_col("R", 2, rot[1])
            set_row("B", 2, rot[2][::-1])
            set_col("L", 0, rot[3][::-1])
            return
        if face == "F":
            data = [row("U", 2), col("R", 0), row("D", 0)[::-1], col("L", 2)[::-1]]
            if direction == CW:
                rot = data[-1:] + data[:-1]
            else:
                rot = data[1:] + data[:1]
            set_row("U", 2, rot[0])
            set_col("R", 0, rot[1])
            set_row("D", 0, rot[2][::-1])
            set_col("L", 2, rot[3][::-1])
            return
        if face == "B":
            # 注意背面方向，索引有镜像
            data = [row("U", 0), col("L", 0), row("D", 2)[::-1], col("R", 2)[::-1]]
            # 背面对观察者而言顺时针=实际逆向，因此 direction 取反
            eff_dir = -direction
            if eff_dir == CW:
                rot = data[-1:] + data[:-1]
            else:
                rot = data[1:] + data[:1]
            set_row("U", 0, rot[0])
            set_col("L", 0, rot[1])
            set_row("D", 2, rot[2][::-1])
            set_col("R", 2, rot[3][::-1])
            return
        if face == "L":
            data = [col("U", 0), row("F", 0), col("D", 0)[::-1], row("B", 2)]
            if direction == CW:
                rot = data[-1:] + data[:-1]
            else:
                rot = data[1:] + data[:1]
            set_col("U", 0, rot[0])
            set_row("F", 0, rot[1])
            set_col("D", 0, rot[2][::-1])
            set_row("B", 2, rot[3])
            return
        if face == "R":
            data = [col("U", 2), row("B", 0)[::-1], col("D", 2)[::-1], row("F", 2)]
            if direction == CW:
                rot = data[-1:] + data[:-1]
            else:
                rot = data[1:] + data[:1]
            set_col("U", 2, rot[0])
            set_row("B", 0, rot[1][::-1])
            set_col("D", 2, rot[2][::-1])
            set_row("F", 2, rot[3])
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

