import cli
import os
import yaml
import converter
from spiral import *

class InduCalcCLI(cli.CLI):

    def __init__(self, helper=True, title="Cli"):
        super().__init__(helper, title)

        self.add_commands(
            cli.CliCommand(
                "project",
                arguments=[cli.CliArgument("project-name", help_message="project name", type_=str)],
                subcommands=[
                    cli.CliCommand(
                        "delete",
                        event=self.delete_project,
                    ),
                    cli.CliCommand(
                        "list",
                        allowed_arguments=[],
                        event=self.list_projects,
                    ),
                    cli.CliCommand(
                        "new",
                        event=self.create_new_project,
                    ),
                    cli.CliCommand(
                        "rename",
                        arguments=[cli.CliArgument("new-project-name", type_=str)],
                        event=self.rename_project,
                    ),
                ]
            ),
            cli.CliCommand(
                "inductor",
                arguments=[
                    cli.CliArgument(
                        "project-name",
                        type_=str,
                        help_message="name of the associated project",
                    ),
                    cli.CliArgument(
                        "inductor-name",
                        type_=str,
                        help_message="name of the inductor",
                    )
                ],
                subcommands=[
                    cli.CliCommand(
                        "list",
                        allowed_arguments=["project-name"],
                        confirmation=True,
                        event=self.list_inductors,
                    ),
                    cli.CliCommand(
                        "rename",
                        arguments=[
                            cli.CliArgument("new-inductor-name", type_=str),
                        ],
                        confirmation=True,
                        event=self.rename_inductor,
                    ),
                    cli.CliCommand(
                        "add",
                        confirmation=True,
                        event=self.add_inductor,
                        options=[
                            cli.CliOption("base-metal", type_=str),
                            cli.CliOption("exit-metal", type_=str),
                            cli.CliOption("length", type_=float),
                            cli.CliOption("width", type_=float),
                            cli.CliOption("space", type_=float),
                            cli.CliOption("turns", type_=float),
                            cli.CliOption("techfile-name", type_=str),
                            cli.CliOption("x", type_=float),
                            cli.CliOption("y", type_=float),
                        ],
                    ),
                    cli.CliCommand(
                        "edit",
                        confirmation=True,
                        event=self.edit_inductor,
                        options=[
                            cli.CliOption("base-metal", required=False, type_=str),
                            cli.CliOption("exit-metal", required=False, type_=str),
                            cli.CliOption("length", required=False, type_=float),
                            cli.CliOption("width", required=False, type_=float),
                            cli.CliOption("space", required=False, type_=float),
                            cli.CliOption("turns", required=False, type_=float),
                            cli.CliOption("techfile-name", required=False, type_=str),
                            cli.CliOption("x", required=False, type_=float),
                            cli.CliOption("y", required=False, type_=float),
                        ],
                    ),
                    cli.CliCommand(
                        "remove",
                        confirmation=True,
                        event=self.remove_inductor,
                    ),
                    cli.CliCommand(
                        "see-content",
                        confirmation=True,
                        event=self.see_inductor_content,
                    ),
                    cli.CliCommand(
                        "draw",
                        arguments=[
                            cli.CliArgument("output-file", type_=str)
                        ],
                        confirmation=True,
                        event=self.draw_inductor,
                    ),
                ],
            ),
            cli.CliCommand(
                "techfile",
                arguments=[
                    cli.CliArgument(
                        "project-name",
                        type_=str,
                        help_message="name of the associated project",
                    ),
                    cli.CliArgument("techfile-name", type_=str)
                ],
                event=self.list_tecfile,
                help_message="manage techfiles",
                subcommands=[
                    cli.CliCommand(
                        "import",
                        arguments=[
                            cli.CliArgument("input-file-name", type_=str),
                        ],
                        event=self.__import,
                    ),
                    cli.CliCommand(
                        "export",
                        arguments=[
                            cli.CliArgument("output-file-name", type_=str),
                        ],
                        event=self.__export,
                    ),
                    cli.CliCommand(
                        "list",
                        allowed_arguments=["project-name"],
                        event=self.list_techfiles_names,
                    ),
                    cli.CliCommand(
                        "add",
                        help_message="add layers, metals and vias",
                        subcommands=[
                            cli.CliCommand(
                                "layer",
                                confirmation=True,
                                event=lambda a, o: self.add_techfile_layer(a, o, "layer"),
                                help_message="add layer into techfile",
                                options=[
                                    cli.CliOption("id", required=False, type_=int),
                                    cli.CliOption("description", type_=str),
                                    cli.CliOption("resistivity", aliases=["conductivity"], help_message="\n".join(["resistivity (Ωcm)",
                                                                                                                   "conductivity (S/m)"]), type_=float),
                                    cli.CliOption("thickness", help_message="thickness (µm)", type_=float),
                                    cli.CliOption("permittivity", help_message="relative permittivity", type_=float),
                                ],
                            ),
                            cli.CliCommand(
                                "metal",
                                confirmation=True,
                                event=lambda a, o: self.add_techfile_layer(a, o, "metal"),
                                help_message="add metal into techfile",
                                options=[
                                    cli.CliOption("id", required=False, type_=int),
                                    cli.CliOption("description", type_=str),
                                    cli.CliOption("layer", help_message="layer id", type_=int),
                                    cli.CliOption("sheet-resistance", aliases=["resistivity", "conductivity"], help_message="\n".join(["resistivity (Ωcm)",
                                                                                                                                       "conductivity (S/m)",
                                                                                                                                       "sheet resistance (mΩ/sq)"]), type_=float),
                                    cli.CliOption("thickness", help_message="thickness (µm)", type_=float),
                                    cli.CliOption("distance", help_message="distance (µm)", type_=float),
                                    cli.CliOption("name", type_=str),
                                    cli.CliOption("color", type_=str),
                                    cli.CliOption("gds-number", type_=int),
                                    cli.CliOption("gds-datatype", type_=int),
                                ],
                            ),
                            cli.CliCommand(
                                "via",
                                confirmation=True,
                                event=lambda a, o: self.add_techfile_layer(a, o, "via"),
                                help_message="add via into techfile",
                                options=[
                                    cli.CliOption("id", required=False, type_=int),
                                    cli.CliOption("description", type_=str),
                                    cli.CliOption("top-metal", help_message="top metal id", type_=int),
                                    cli.CliOption("bottom-metal", help_message="bottom metal id", type_=int),
                                    cli.CliOption("resistance", aliases=["resistivity", "conductivity"], help_message="\n".join(["resistance (Ω)",
                                                                                                                                 "conductivity (S/m)",
                                                                                                                                 "resistivity (Ωcm)"]), type_=float),
                                    cli.CliOption("thickness", help_message="thickness (µm)", prerequisits=[["resistivity", "conductivity"]], type_=float),
                                    cli.CliOption("min-width", help_message="min width (µm)", type_=float),
                                    cli.CliOption("space", help_message="space (µm)", type_=float),
                                    cli.CliOption("enclosure", help_message="enclosure (µm)", type_=float),
                                    cli.CliOption("endcap-enclosure", help_message="endcap enclosure (µm)", type_=float),
                                    cli.CliOption("name", type_=str),
                                    cli.CliOption("color", type_=str),
                                    cli.CliOption("gds-number", type_=int),
                                    cli.CliOption("gds-datatype", type_=int),
                                ]
                            )
                        ]
                    ),
                    cli.CliCommand(
                        "create",
                        event=self.create_techfile,
                        help_message="create a techfile",
                        options=[
                            cli.CliOption("grid", type_=float)
                        ]
                    ),
                    cli.CliCommand(
                        "delete",
                        event=self.delete_techfile,
                        help_message="delete a techfile",
                    ),
                    cli.CliCommand(
                        "rename",
                        arguments=[cli.CliArgument("new-techfile-name", type_=str)],
                        event=self.rename_techfile,
                        help_message="rename a techfile"
                    ),
                    cli.CliCommand(
                        "edit",
                        subcommands=[
                            cli.CliCommand(
                                "chip",
                                confirmation=True,
                                event=self.edit_chip,
                                help_message="edit chip specs",
                                options=[
                                    cli.CliOption("grid", required=False, type_=float)
                                ],
                            ),
                            cli.CliCommand(
                                "layer",
                                arguments=[
                                    cli.CliArgument("id", type_=int)
                                ],
                                confirmation=True,
                                event=lambda a, o: self.edit_techfile_layer(a, o, "layer"),
                                help_message="edit an specifc layer inside a techfile",
                                options=[
                                    cli.CliOption("description", required=False, type_=str),
                                    cli.CliOption("resistivity", aliases=["conductivity"], help_message="\n".join(["resistivity (Ωcm)",
                                                                                                                   "conductivity (S/m)"]), required=False, type_=float),
                                    cli.CliOption("thickness", help_message="thickness (µm)", required=False, type_=float),
                                    cli.CliOption("permittivity", help_message="relative permittivity", required=False, type_=float),
                                ]
                            ),
                            cli.CliCommand(
                                "metal",
                                arguments=[
                                    cli.CliArgument("id", type_=int)
                                ],
                                confirmation=True,
                                event=lambda a, o: self.edit_techfile_layer(a, o, "metal"),
                                help_message="edit an specifc metal inside a techfile",
                                options=[
                                    cli.CliOption("description", required=False, type_=str),
                                    cli.CliOption("layer", help_message="layer id", required=False, type_=int),
                                    cli.CliOption("sheet-resistance", aliases=["resistivity", "conductivity"], help_message="\n".join(["resistivity (Ωcm)",
                                                                                                                                       "conductivity (S/m)",
                                                                                                                                       "sheet resistance (mΩ/sq)"]), required=False, type_=float),
                                    cli.CliOption("thickness", help_message="thickness (µm)", required=False, type_=float),
                                    cli.CliOption("distance", help_message="distance (µm)", required=False, type_=float),
                                    cli.CliOption("name", required=False, type_=str),
                                    cli.CliOption("color", required=False, type_=str),
                                    cli.CliOption("gds-number", required=False, type_=int),
                                    cli.CliOption("gds-datatype", required=False, type_=int),
                                ],
                            ),
                            cli.CliCommand(
                                "via",
                                arguments=[
                                    cli.CliArgument("id", type_=int)
                                ],
                                confirmation=True,
                                event=lambda a, o: self.edit_techfile_layer(a, o, "via"),
                                help_message="edit an specifc via inside a techfile",
                                options=[
                                    cli.CliOption("description", required=False, type_=str),
                                    cli.CliOption("top-metal", help_message="top metal id", required=False, type_=int),
                                    cli.CliOption("bottom-metal", help_message="bottom metal id", required=False, type_=int),
                                    cli.CliOption("resistance", aliases=["resistivity", "conductivity"], help_message="\n".join(["resistance (Ω)",
                                                                                                                                 "conductivity (S/m)",
                                                                                                                                 "resistivity (Ωcm)"]), required=False, type_=float),
                                    cli.CliOption("thickness", help_message="thickness (µm)", prerequisits=[["resistivity", "conductivity"]], type_=float),
                                    cli.CliOption("min-width", help_message="min width (µm)", required=False, type_=float),
                                    cli.CliOption("space", help_message="space (µm)", required=False, type_=float),
                                    cli.CliOption("enclosure", help_message="enclosure (µm)", required=False, type_=float),
                                    cli.CliOption("endcap-enclosure", help_message="endcap enclosure (µm)", required=False, type_=float),
                                    cli.CliOption("name", required=False, type_=str),
                                    cli.CliOption("color", required=False, type_=str),
                                    cli.CliOption("gds-number", required=False, type_=int),
                                    cli.CliOption("gds-datatype", required=False, type_=int),
                                ]
                            )
                        ]
                    ),
                    cli.CliCommand(
                        "remove",
                        subcommands=[
                            cli.CliCommand(
                                "layer",
                                event=lambda a, o: self.remove_techfile_layer(a, o, "layer"),
                                arguments=[
                                    cli.CliArgument("id", type_=int)
                                ],
                            ),
                            cli.CliCommand(
                                "metal",
                                event=lambda a, o: self.remove_techfile_layer(a, o, "metal"),
                                arguments=[
                                    cli.CliArgument("id", type_=int)
                                ],
                            ),
                            cli.CliCommand(
                                "via",
                                event=lambda a, o: self.remove_techfile_layer(a, o, "via"),
                                arguments=[
                                    cli.CliArgument("id", type_=int)
                                ],
                            )
                        ]
                    ),
                    cli.CliCommand(
                        "move",
                        subcommands=[
                            cli.CliCommand(
                                "layer",
                                event=lambda a, o: self.move(a, o, "layer"),
                                arguments=[
                                    cli.CliArgument("from", type_=int),
                                    cli.CliArgument("to", type_=int),
                                ],
                            ),
                            cli.CliCommand(
                                "metal",
                                event=lambda a, o: self.move(a, o, "metal"),
                                arguments=[
                                    cli.CliArgument("from", type_=int),
                                    cli.CliArgument("to", type_=int),
                                ],
                            ),
                            cli.CliCommand(
                                "via",
                                event=lambda a, o: self.move(a, o, "via"),
                                arguments=[
                                    cli.CliArgument("from", type_=int),
                                    cli.CliArgument("to", type_=int),
                                ],
                            )
                        ]
                    )
                ]
            )
        )

    def load_project(self, project_name:str) -> cli.CliMessage | dict[str, dict[str, dict]]:

        project_path = converter.process_user_path(project_name, ".indc")

        if not os.path.exists(project_path):
            return cli.CliMessage(f"Project not found: {project_name}", status="error")
        
        loaded_project: dict[str, dict[str, dict]] = None
        with open(project_path, "r") as file:
            loaded_project = yaml.safe_load(file)
        
        return loaded_project
    
    def save_project(self, project_data: dict[str, dict[str, dict]], project_name:str):

        project_path = converter.process_user_path(project_name, ".indc")

        with open(project_path, "w") as file:
            yaml.dump(project_data, file, allow_unicode=True, sort_keys=False)

    def create_new_project(self, arguments:dict[str], options:dict[str]):

        file_path = converter.process_user_path(arguments["project_name"], ".indc")

        try:
            with open(file_path, "x") as file:
                yaml.dump({"inductors": {}, "techfiles": {}}, file, allow_unicode=True, sort_keys=False)
        except:
            return cli.CliMessage(f"Project already exists: {arguments['project_name']}", status="error")

    def list_projects(self, *args):

        projects = [project.replace(".indc", "") for project in os.listdir(".") if project[-5:] == ".indc"]
        if projects:
            return cli.CliMessage("\n".join(projects))
        return cli.CliMessage("There are no projects")
        
    def delete_project(self, arguments:dict[str], options:dict[str]):

        file_path = converter.process_user_path(arguments['project_name'], ".indc")
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            return cli.CliMessage(f"Project do not exist: {arguments['project_name']}", status="error")
        
    def rename_project(self, arguments:dict[str], options:dict[str]):

        old_file_path = converter.process_user_path(arguments['project_name'], ".indc")
        new_file_path = converter.process_user_path(arguments['new_project_name'], ".indc")
        if not os.path.exists(old_file_path):
            return cli.CliMessage(f"Project not found: {arguments['project_name']}", status="error")
        
        if os.path.exists(new_file_path):
            return cli.CliMessage(f"Project already exists: {new_file_path}", status="error")
        
        try: os.rename(old_file_path, new_file_path)
        except: return cli.CliMessage("Permission denied", "warning")

    def rename_inductor(self, arguments: dict[str], options: dict[str]):

        loaded_project = self.load_project(project_name=arguments["project_name"])
        if isinstance(loaded_project, cli.CliMessage): return loaded_project

        aux = {}
        for key in loaded_project["inductors"]:

            if arguments["inductor_name"] == key:
                aux[arguments["new_inductor_name"]] = loaded_project["inductors"][arguments["inductor_name"]]
            else:
                aux[key] = loaded_project["inductors"][key]
        
        loaded_project["inductors"] = aux

        self.save_project(project_data=loaded_project, project_name=arguments["project_name"])

    def list_inductors(self, arguments: dict[str], options: dict[str]):

        loaded_project = self.load_project(project_name=arguments["project_name"])
        if isinstance(loaded_project, cli.CliMessage): return loaded_project

        return cli.CliMessage("\n".join(loaded_project["inductors"]))
            
    def add_inductor(self, arguments:dict[str], options:dict[str]):
        
        loaded_project = self.load_project(project_name=arguments["project_name"])
        if isinstance(loaded_project, cli.CliMessage): return loaded_project

        loaded_project["inductors"][arguments["inductor_name"]] = {**options}

        self.save_project(project_data=loaded_project, project_name=arguments["project_name"])

    def edit_inductor(self, arguments:dict[str], options:dict[str]):

        loaded_project = self.load_project(project_name=arguments["project_name"])
        if isinstance(loaded_project, cli.CliMessage): return loaded_project

        loaded_project["inductors"][arguments["inductor_name"]].update(options)

        self.save_project(project_data=loaded_project, project_name=arguments["project_name"])
    
    def remove_inductor(self, arguments:dict[str], options:dict[str]):

        loaded_project = self.load_project(project_name=arguments["project_name"])
        if isinstance(loaded_project, cli.CliMessage): return loaded_project

        loaded_project["inductors"].pop(arguments["inductor_name"], None)

        self.save_project(project_data=loaded_project, project_name=arguments["project_name"])
    
    def see_inductor_content(self, arguments: dict[str], options: dict[str]):

        loaded_project = self.load_project(project_name=arguments["project_name"])
        if isinstance(loaded_project, cli.CliMessage): return loaded_project

        return cli.CliMessage("".join(f"{chave} = {valor}\n" for chave, valor in loaded_project["inductors"][arguments["inductor_name"]].items()))
    
    def draw_inductor(self, arguments: dict[str], options: dict[str]):

        loaded_project = self.load_project(project_name=arguments["project_name"])
        if isinstance(loaded_project, cli.CliMessage): return loaded_project

        inductor = loaded_project["inductors"][arguments["inductor_name"]]
        techfile = loaded_project["techfiles"][inductor["techfile_name"]]

        inductor.pop("techfile_name")

        spiral = Spiral(self)

        spiral.draw_square(
            inductor_name=arguments["inductor_name"],
            output_file=arguments["output_file"],
            techfile=techfile,
            **inductor,
        )

        
    def create_techfile(self, arguments:dict[str], options:dict[str]):

        loaded_project = self.load_project(project_name=arguments["project_name"])
        if isinstance(loaded_project, cli.CliMessage): return loaded_project

        if arguments["techfile_name"] in loaded_project["techfiles"]:
            return cli.CliMessage(f"Techfile already exists: {arguments['techfile_name']}", "error")
        
        loaded_project["techfiles"][f"{arguments['techfile_name']}"] = {
            "chip": [
                {"grid": options["grid"]}
            ],
            "layer": [],
            "metal": [],
            "via": [],
        }
        self.save_project(project_data=loaded_project, project_name=arguments["project_name"])
        
    def delete_techfile(self, arguments:dict[str], options:dict[str]):

        loaded_project = self.load_project(project_name=arguments["project_name"])
        if isinstance(loaded_project, cli.CliMessage): return loaded_project

        if loaded_project["techfiles"].pop(arguments['techfile_name'], None) == None:
            return cli.CliMessage(f"Techfile do not exist: {arguments['techfile_name']}", "error")

        self.save_project(project_data=loaded_project, project_name=arguments["project_name"])
        
    def rename_techfile(self, arguments:dict[str], options:dict[str]):

        loaded_project = self.load_project(project_name=arguments["project_name"])
        if isinstance(loaded_project, cli.CliMessage): return loaded_project

        if not arguments["techfile_name"] in loaded_project["techfiles"]:
            return cli.CliMessage(f"Techfile do not exist: {arguments['techfile_name']}", "error")
        
        if arguments["new_techfile_name"] in loaded_project["techfiles"]:
            return cli.CliMessage(f"Techfile already exists: {arguments['new_techfile_name']}", "error")
        
        aux = {}
        for techfile_name in loaded_project["techfiles"]:
            if techfile_name == arguments["techfile_name"]:
                aux[arguments['new_techfile_name']] = loaded_project["techfiles"][techfile_name]
            else:
                aux[techfile_name] = loaded_project["techfiles"][techfile_name]

        loaded_project["techfiles"] = aux

        self.save_project(project_data=loaded_project, project_name=arguments["project_name"])

    def list_techfiles_names(self, arguments:dict[str], options:dict[str]):
        
        loaded_project = self.load_project(project_name=arguments["project_name"])
        if isinstance(loaded_project, cli.CliMessage): return loaded_project

        return cli.CliMessage("\n".join(loaded_project["techfiles"]))

    def __import(self, arguments:dict[str], options:dict[str]):

        loaded_project = self.load_project(project_name=arguments["project_name"])
        if isinstance(loaded_project, cli.CliMessage): return loaded_project

        if not os.path.isfile(arguments["input_file_name"]):
            return cli.CliMessage(f"File not found: {arguments['input_file_name']}", status="error")
        
        file_extension = os.path.splitext(arguments["input_file_name"])[-1]
        if not file_extension in (".tek", ".tech"):
            return cli.CliMessage(f"File type not supported. Only .tek and .tech files are allowed for import", status="error")

        if file_extension == ".tek": loaded_file = converter.load_tek(arguments["input_file_name"])
        else: loaded_file = converter.load_tech(arguments["input_file_name"])

        if arguments["techfile_name"] in loaded_project["techfiles"]: return cli.CliMessage(f"Techfile already exists: {arguments['techfile_name']}", status="error")
        loaded_project["techfiles"][arguments["techfile_name"]] = loaded_file

        self.save_project(project_data=loaded_project, project_name=arguments["project_name"])

    def __export(self, arguments:dict[str], options:dict[str]):

        loaded_project = self.load_project(arguments["project_name"])
        if isinstance(loaded_project, cli.CliMessage): return loaded_project

        file_extension = os.path.splitext(arguments["output_file_name"])[-1]
        if not file_extension in (".tek", ".tech"):
            return cli.CliMessage(f"File type not supported. Only .tek and .tech files are allowed for export", status="error")

        try: loaded_tech = loaded_project["techfiles"][arguments["techfile_name"]]
        except: return cli.CliMessage(f"Techfile does not exist: {arguments['techfile_name']}", status="error")

        if file_extension == ".tek":
            converter.write_tek(loaded_tech, arguments["output_file_name"])
        else:
            converter.write_tech(loaded_tech, arguments["output_file_name"])

    def add_techfile_layer(self, arguments:dict[str], options:dict[str], layer_type:str):

        loaded_project = self.load_project(arguments["project_name"])
        if isinstance(loaded_project, cli.CliMessage): return loaded_project

        if not arguments["techfile_name"] in loaded_project["techfiles"]:
            return cli.CliMessage(f"Techfile does not exist: {arguments['techfile_name']}", "error")
        
        if "id" in options:
            layer_id = options["id"]
            options.pop("id")
            loaded_project["techfiles"][arguments["techfile_name"]][layer_type].insert(layer_id, options)
        else:
            loaded_project["techfiles"][arguments["techfile_name"]][layer_type].append(options)

        self.save_project(project_data=loaded_project, project_name=arguments["project_name"])

        return self.list_tecfile(arguments, options)

    def edit_techfile_layer(self, arguments:dict[str], options:dict[str], layer_type:str):

        loaded_project = self.load_project(arguments["project_name"])
        if isinstance(loaded_project, cli.CliMessage): return loaded_project

        if not arguments["techfile_name"] in loaded_project["techfiles"]:
            return cli.CliMessage(f"Techfile do not exist: {arguments['techfile_name']}", "error")
        
        layer_id = arguments["id"]
        if not (0 <= layer_id < len(loaded_project["techfiles"][arguments["techfile_name"]][layer_type])):
            return cli.CliMessage(f"There are no {layer_type} layer with id: {layer_id}", status="error")
        
        selected_layer: dict[str] = loaded_project["techfiles"][arguments["techfile_name"]][layer_type][layer_id]

        if "resistance" in options and "thickness" in selected_layer:
            selected_layer.pop("thickness")

        if (
            "conductivity" in options and not "conductivity" in selected_layer or 
            "resistance" in options and not "resistance" in selected_layer or
            "resistivity" in options and not "resistivity" in selected_layer or
            "sheet_resistance" in options and not "sheet_resistance" in selected_layer
        ):
            selected_layer.pop("conductivity", None)
            selected_layer.pop("resistance", None)
            selected_layer.pop("resistivity", None)
            selected_layer.pop("sheet_resistance", None)

        selected_layer.update(options)

        key_order = converter.LAYER_KEY_ORDER if layer_type == "layer" else converter.METAL_KEY_ORDER if layer_type == "metal" else converter.VIA_KEY_ORDER
        loaded_project["techfiles"][arguments["techfile_name"]][layer_type][layer_id] = converter.reorder_dict(selected_layer, key_order)

        self.save_project(project_data=loaded_project, project_name=arguments["project_name"])

        return self.list_tecfile(arguments, options)

    def edit_chip(self, arguments: dict[str], options: dict[str]):

        loaded_project = self.load_project(arguments["project_name"])
        if isinstance(loaded_project, cli.CliMessage): return loaded_project

        if not arguments["techfile_name"] in loaded_project["techfiles"]:
            return cli.CliMessage(f"Techfile do not exist: {arguments['techfile_name']}", "error")

        if "grid" in options:
            loaded_project["techfiles"][arguments["techfile_name"]]["chip"] = [{"grid": options["grid"]}]

        self.save_project(project_data=loaded_project, project_name=arguments["project_name"])

        return self.list_tecfile(arguments, options)

    def remove_techfile_layer(self, arguments:dict[str], options:dict[str], layer_type:str):

        loaded_project = self.load_project(arguments["project_name"])
        if isinstance(loaded_project, cli.CliMessage): return loaded_project

        if not arguments["techfile_name"] in loaded_project["techfiles"]:
            return cli.CliMessage(f"Techfile do not exist: {arguments['techfile_name']}", "error")
        
        layer_id = arguments["id"]
        if not (0 <= layer_id < len(loaded_project["techfiles"][arguments["techfile_name"]][layer_type])):
            return cli.CliMessage(f"There are no {layer_type} layer with id: {layer_id}", status="error")
        
        loaded_project["techfiles"][arguments["techfile_name"]][layer_type].pop(layer_id)

        self.save_project(project_data=loaded_project, project_name=arguments["project_name"])

        return self.list_tecfile(arguments, options)

    def move(self, arguments:dict[str], options:dict[str], layer_type:str):

        loaded_project = self.load_project(project_name=arguments["project_name"])
        if isinstance(loaded_project, cli.CliMessage): return loaded_project

        if not arguments["techfile_name"] in loaded_project["techfiles"]:
            return cli.CliMessage(f"Techfile do not exist: {arguments['techfile_name']}", "error")
        
        from_ = arguments["from"]
        if not (0 <= from_ < len(loaded_project["techfiles"][arguments["techfile_name"]][layer_type])):
            return cli.CliMessage(f"There are no {layer_type} layer with id: {from_}", status="error")
        
        to_ = arguments["to"]
        if not (0 <= to_ < len(loaded_project["techfiles"][arguments["techfile_name"]][layer_type])):
            return cli.CliMessage(f"Can't move {layer_type} layer from {from_} to {to_}", status="error")
        
        aux = loaded_project["techfiles"][arguments["techfile_name"]][layer_type][from_]
        loaded_project["techfiles"][arguments["techfile_name"]][layer_type].pop(from_)
        loaded_project["techfiles"][arguments["techfile_name"]][layer_type].insert(to_, aux)

        self.save_project(project_data=loaded_project, project_name=arguments["project_name"])

        return self.list_tecfile(arguments, options)

    def list_tecfile(self, arguments:dict[str], options:dict[str]):

        def enumerate_lists(data):
            if isinstance(data, list):
                # Adiciona IDs para cada item na lista
                return [{"id": i, **enumerate_lists(item)} if isinstance(item, dict) else item
                        for i, item in enumerate(data)]
            elif isinstance(data, dict):
                # Aplica a função a cada valor do dicionário
                return {key: enumerate_lists(value) for key, value in data.items()}
            else:
                # Retorna outros tipos de dados sem alterações
                return data
            
        loaded_project = self.load_project(project_name=arguments["project_name"])

        if not arguments["techfile_name"] in loaded_project["techfiles"]:
            return cli.CliMessage(f"Techfile do not exist: {arguments['techfile_name']}", "error")

        enumerated_content = enumerate_lists(loaded_project["techfiles"][arguments["techfile_name"]])
        content_to_print = yaml.dump(enumerated_content, default_flow_style=False, allow_unicode=True, sort_keys=False)[:-1]

        return cli.CliMessage(content_to_print)
    
induCalcCLI = InduCalcCLI(title="InduCalcCLI")

induCalcCLI.mainloop()