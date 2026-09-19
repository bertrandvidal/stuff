"""Full stack: bottom case, PCB + Pico, plate, top frame and keycap envelope, all in the shared frame."""
from cadgen import build123d as bd
from cadgen import step

from case_bottom import case_bottom
from case_top import case_top
from keycaps import keycaps
from pcb import pcb
from plate import plate


@step(out="../STEP/assembly.step")
def assembly():
    parts = [case_bottom(), pcb(), plate(), case_top(), keycaps()]
    for p, name in zip(parts, ["bottom_case", "pcb_assembly", "plate", "top_frame", "keycaps"]):
        p.label = name
    return bd.Compound(children=parts, label="alps75_zug_case")


if __name__ == "__main__":
    assembly()
