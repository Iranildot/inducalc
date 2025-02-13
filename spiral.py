import math
import gdsfactory as gf
import os
import cli
import time

def magnitude(number: float):
    if number == 0:
        return 0
    return int(math.floor(math.log10(abs(number))))

class Spiral:
    def __init__(self, cli: cli.CLI):
        
        self.cli = cli

    def draw_square(
            self,
            base_metal: str,
            exit_metal: str,
            inductor_name: str,
            length: float | int,
            output_file: str,
            space: float | int,
            techfile: dict[str, list[dict[str]]],
            turns: float | int,
            width: float | int,
            x: float | int,
            y: float | int,
        ):

        """
        Draw a square IC inductor.

        Args:
            base_metal: Name of the main inductor's structure.
            exit_metal: Name of the exit metal of the inductor.
            length: External length of the square inductor.
            spacing: Space between base metal traces.
            techfile: Some data of a tecnology file containing design rules, material properties, 
                    and process parameters required for chip fabrication.
            turns: Number of turns in the spiral inductor.
            width: Width of the metal traces forming the inductor.
            xy: Coordinates (x, y) of the inductor's starting position.
        """

        def get_metal_index(metal_name: str) -> int:

            """
            Gets metal list index of techfile metals.

            Args:
                metal_name: Name of a metal.
            """

            metal_name = metal_name.upper()
            metals = techfile["metal"]

            for i in range(len(metals)):
                if metals[i]["name"].upper() == metal_name:
                    return i
            return -1
        
        self.cli.progressbar.set(0)
        
        l = length
        s = space
        w = width

        gf.clear_cache()

        inductor = gf.Component(inductor_name)
        segments = round(turns * 4)

        base_metal_index = get_metal_index(metal_name=base_metal)
        base_metal_layer = (techfile["metal"][base_metal_index]["gds_number"], techfile["metal"][base_metal_index]["gds_datatype"])

        exit_metal_index = get_metal_index(metal_name=exit_metal)
        exit_metal_layer = (techfile["metal"][exit_metal_index]["gds_number"], techfile["metal"][exit_metal_index]["gds_datatype"])

        # DRAWING BASE METAL
        toggle = False
        for i in range(segments):

            if toggle:
                l -= (s + w) * (i % 2) 
            
            match (i % 4):
                case 0: # WEST
                    inductor.add_polygon(
                        (
                            (x, y),
                            (x + w, y),
                            (x + w, y + l),
                            (x, y + l),
                        ),
                        layer=base_metal_layer
                    )

                    y += l
                    
                case 1: # NORTH
                    inductor.add_polygon(
                        (
                            (x, y - w),
                            (x + l, y - w),
                            (x + l, y),
                            (x, y),
                        ),
                        layer=base_metal_layer
                    )

                    x += l

                case 2: # EAST
                    inductor.add_polygon(
                        (
                            (x - w, y - l),
                            (x, y - l),
                            (x, y),
                            (x - w, y),
                        ),
                        layer=base_metal_layer
                    )
                    
                    y -= l

                case 3: # SOUTH
                    if not toggle:
                        l -= (s + w)
                        toggle = True

                    inductor.add_polygon(
                        (
                            (x - l, y),
                            (x, y),
                            (x, y + w),
                            (x - l, y + w),
                        ),
                        layer=base_metal_layer
                    )

                    x -= l

            self.cli.progressbar.set((1/3) * (i/(segments - 1)))
            self.cli.update()

        # DRAWING VIAS
        start = min(base_metal_index, exit_metal_index)
        end = max(base_metal_index, exit_metal_index)

        top_or_bottom = "top_metal" if exit_metal_index > base_metal_index else "bottom_metal"

        last_segment_index = i

        via_range = end - start

        for i in range(start, end):

            via = techfile["via"][i]
            via_layer = (via["gds_number"], via["gds_datatype"])

            v_mw = via["min_width"]
            v_s = via["space"] + via["space"]
            max_enclosure = max(via["enclosure"], via["endcap_enclosure"])
            v_num = int((w - (2 * max_enclosure - v_s)) / (v_s + v_mw))

            via_componenet = gf.components.rectangle(
                size=(v_mw, v_mw),
                layer=via_layer,
            )
            via_ref = inductor.add_ref(
                gf.components.array(
                    via_componenet,
                    columns=v_num,
                    column_pitch=v_s + v_mw,
                    rows=v_num, 
                    row_pitch=v_s + v_mw,
                ),
            )

            external_spacing = (w - v_num * (v_s + v_mw) + v_s) / 2

            aux_metal = techfile["metal"][via[top_or_bottom]]
            aux_metal_layer = (aux_metal["gds_number"], aux_metal["gds_datatype"])

            aux_metal_ref = inductor.add_ref(
                gf.components.rectangle(
                    size=(w, w),
                    layer=aux_metal_layer,
                )
            )

            match last_segment_index % 4:
                case 0: # WEST
                    via_ref.move((x + external_spacing, y - w + external_spacing))
                    aux_metal_ref.move((x, y - w))
                case 1: # NORTH
                    via_ref.move((x - w + external_spacing, y - w + external_spacing))
                    aux_metal_ref.move((x - w, y - w))
                case 2: # EAST
                    via_ref.move((x - w + external_spacing, y + external_spacing))
                    aux_metal_ref.move((x - w, y))
                case 3: # SOUTH
                    via_ref.move((x + external_spacing, y + external_spacing))
                    aux_metal_ref.move((x, y))

            self.cli.progressbar.set((1 / 3) + ((1 / 3) * ((i - start)/(via_range))))
            self.cli.update()

        # DRAWING EXIT METAL
        e_l = round(turns) * (s + w)
        match last_segment_index % 4:
            case 0: # WEST
                inductor.add_polygon(
                    (
                        (x - e_l - (s + w), y - w),
                        (x, y - w),
                        (x, y),
                        (x - e_l - (s + w), y),
                    ),
                    layer=exit_metal_layer
                )
            case 1: # NORTH
                inductor.add_polygon(
                    (
                        (x - w, y),
                        (x, y),
                        (x, y + e_l),
                        (x - w, y + e_l),
                    ),
                    layer=exit_metal_layer
                )
            case 2: # EAST
                inductor.add_polygon(
                    (
                        (x, y),
                        (x + e_l, y),
                        (x + e_l, y + w),
                        (x, y + w),
                    ),
                    layer=exit_metal_layer
                )
            case 3: # SOUTH
                inductor.add_polygon(
                    (
                        (x, y),
                        (x + w, y),
                        (x + w, y - e_l),
                        (x, y - e_l),
                    ),
                    layer=exit_metal_layer
                )
        
        inductor.flatten()
        inductor.write_gds(output_file)
        self.cli.progressbar.set(1)
        self.cli.update()
        time.sleep(0.25)
        self.cli.progressbar.set(0)