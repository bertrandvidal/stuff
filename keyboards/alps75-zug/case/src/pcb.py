"""Reference model of the PCB outline and the Pico (from alps75-zug.kicad_pcb), for fit checks."""
from cadgen import srgb, step

from lib.case_geom import make_pcb


@step(out="../STEP/pcb.step")
def pcb():
    asm = make_pcb()
    board, pico = asm.children
    board.color = srgb("#1F6E3A")
    pico.color = srgb("#2B2B2B")
    return asm


if __name__ == "__main__":
    pcb()
