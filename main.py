from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from mofang import RubiksCube

app = FastAPI(title="RubiksCube API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cube = RubiksCube()


class MoveRequest(BaseModel):
    move: str


class ScrambleRequest(BaseModel):
    steps: int = 20


@app.get("/state")
def get_state() -> dict:
    return cube.state


@app.post("/move")
def do_move(req: MoveRequest) -> dict:
    move_str = req.move.strip()
    if not move_str:
        raise HTTPException(status_code=400, detail="move 不能为空")
    try:
        cube.move(move_str)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"非法公式: {e}")
    return cube.state


@app.get("/reset")
def reset() -> dict:
    global cube
    cube = RubiksCube()
    return cube.state


@app.post("/scramble")
def do_scramble(req: ScrambleRequest) -> dict:
    steps = int(req.steps)
    if steps <= 0 or steps > 200:
        raise HTTPException(status_code=400, detail="steps 必须在 1..200")
    seq = cube.scramble(steps)
    return {"scramble": seq, "state": cube.state}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)

