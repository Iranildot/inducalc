import customtkinter as ctk
import tkinter as tk
import tkinter.font as tkFont
import re
import os
import yaml

class ToolTip:
    def __init__(self, widget, text:str, font:tuple=("Verdana", 15), delay:int=500):

        """
        Args:
            widget: Widget associated with tooltip.
            text: Tooltip text.
            font: Tooltip text font.
            delay: Time (ms) before tooltip appears.
        """

        self.widget = widget 
        self.text = text
        self.font = font
        self.delay = delay  # DELAY TIME IN MILLISECONDS
        self.tooltip_window = None
        self.timer_id = None  # TIMER ID

        # BIND MOUSE EVENTS
        self.widget.bind("<Enter>", self.start_timer)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def start_timer(self, event):

        """
        Initialize timer to show the tooltip.
        """

        self.cancel_timer()  # CANCEL ANY ACTIVE TIMER
        self.timer_id = self.widget.after(self.delay, self.show_tooltip)

    def cancel_timer(self):

        """
        Cancel timer if it is active.
        """

        if self.timer_id:
            self.widget.after_cancel(self.timer_id)
            self.timer_id = None

    def show_tooltip(self):

        """
        Shows tooltip near to the mouse cursor.
        """

        self.cancel_timer()  # RESET TIMER

        if self.tooltip_window is not None:
            return

        # CREATE A SEPARATED WINDOW TO TOOLTIP
        self.tooltip_window = ctk.CTkToplevel(self.widget)
        self.tooltip_window.configure(fg_color=("gray12", "gray90"))
        self.tooltip_window.wm_overrideredirect(True)  # REMOVES WINDOW BORDERS

        # POSITION OF TOOLTIP (NEAR THE MOUSE CURSOR)
        x = self.tooltip_window.winfo_pointerx() + 10
        y = self.tooltip_window.winfo_pointery() + 10

        # ADJUST POSITION TO PREVENT THE TOOLTIP FROM LEAVING THE SCREEN
        screen_width = self.widget.winfo_screenwidth()
        screen_height = self.widget.winfo_screenheight()

        font = tkFont.Font(family=self.font[0], size=self.font[1])
        lines = self.text.split("\n")
        width = max(font.measure(line) for line in lines) + 20  # PIXELS
        height = (len(lines) * font.metrics("linespace")) + 20  # PIXELS
        if x + width - 10 > screen_width:
            x = x - width
        if y + height - 10 > screen_height:
            y = y - height

        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        # CAPTURE SCROLL EVENTS
        self.tooltip_window.bind("<MouseWheel>", self._disable_scroll)  # WINDOWS
        self.tooltip_window.bind("<Button-4>", self._disable_scroll)  # LINUX
        self.tooltip_window.bind("<Button-5>", self._disable_scroll)  # LINUX

        # CREATE TEXT WIDGET WITH ADJUSTED DIMENSIONS
        text_box = tk.Text(
            self.tooltip_window,
            font=self.font,
            width=width // font.measure("0"),
            height=height // font.metrics("linespace"),
            bg="gray12" if ctk.get_appearance_mode() == "Light" else "gray90",
            fg="gray90" if ctk.get_appearance_mode() == "Light" else "gray12",
            borderwidth=0,
            highlightthickness=0,
        )
        text_box.insert(tk.END, self.text)
        text_box.config(state="disabled")  # DISABLE TEXT EDITION
        text_box.grid(padx=10, pady=10)

    def _disable_scroll(self, event):

        """
        Prevents the tooltip scroll event from affecting the main widget.
        """

        return "break"

    def hide_tooltip(self, event=None):

        """
        Hides tooltip if cursor leaves the widget and tooltip.
        """

        self.cancel_timer()
        if self.tooltip_window:
            # VERIFIES CONTINUASLY CURSOR POSITION
            self.widget.unbind("<Motion>")
            self.tooltip_window.unbind("<Motion>")
            self._check_cursor_position()

    def _check_cursor_position(self):

        """
        Verifica se o cursor está fora do widget e do tooltip.
        """

        if self.tooltip_window:

            # CURSOR COORDINATES
            x, y = self.widget.winfo_pointerx(), self.widget.winfo_pointery()

            # WIDGET COORDINATES AND DIMENSIONS
            widget_x1 = self.widget.winfo_rootx()
            widget_y1 = self.widget.winfo_rooty()
            widget_x2 = widget_x1 + self.widget.winfo_width()
            widget_y2 = widget_y1 + self.widget.winfo_height()

            # TOOLTIP COORDINATES AND DIMENSIONS
            tooltip_x1 = self.tooltip_window.winfo_rootx()
            tooltip_y1 = self.tooltip_window.winfo_rooty()
            tooltip_x2 = tooltip_x1 + self.tooltip_window.winfo_width()
            tooltip_y2 = tooltip_y1 + self.tooltip_window.winfo_height()

            # IF CURSOR IS NEITHER ON WIDGET NOR TOOLTIP, DESTROY THE TOOLTIP
            if not ((widget_x1 <= x <= widget_x2 and widget_y1 <= y <= widget_y2) or
                    (tooltip_x1 <= x <= tooltip_x2 and tooltip_y1 <= y <= tooltip_y2)):
                self.tooltip_window.destroy()
                self.tooltip_window = None
            else:
                # CONTINUES VERIFING WHILE CURSOR IS NEAR
                self.tooltip_window.after(100, self._check_cursor_position)

class CliMessage:
    def __init__(self, message:str="", status:str="success"):
        """
        message: Message to show up on text area.
        status: Status of message. It can be: success, error, hint or warning.
        """
        self.message: str = message
        self.status: str = status

class CliArgument:

    """
    Represents a command-line interface (CLI) argument with validation and constraints.

    This class allows defining and validating CLI arguments, including allowed values 
    and data types.

    Attributes:
        name (str): The name of the argument.
        type_ (type): The expected data type for the argument value.
        allowed_values (list[list]): A list of lists containing valid values for the argument.
        help_message (str): A message to assist the CLI user.
        information (str): A formatted string summarizing the argument's details.

    Methods:
        __getitem__(key): Allows dictionary-style access to instance attributes.
        __repr__(): Returns a string representation of the instance.

    Raises:
        TypeError: If `type_` is not a valid type.
        TypeError: If `allowed_values` is not a list of lists.
        TypeError: If `allowed_values` contains elements that do not match the expected type.
    """

    def __init__(self, name:str, type_:type, allowed_values:list[list]=list(), help_message:str=""):

        """
        Initializes a CLI argument with validation checks.

        Args:
            name (str): The name of the argument.
            type_ (type): The expected type of the argument value.
            allowed_values (list[list], optional): Valid values for the argument. Defaults to an empty list.
            help_message (str, optional): Help description for the argument. Defaults to an empty string.

        Raises:
            TypeError: If `type_` is not a valid type.
            TypeError: If `allowed_values` is not structured correctly.
            TypeError: If elements in `allowed_values` do not match the expected type.
        """

        # CHECK IF TYPE_ VARIABLE RECIEVE A TYPE
        if not isinstance(type_, type):
            error_message = f"type_ parameter must recive a type"
            raise TypeError(error_message)
        
        # IF TYPE IS BOOL AND NOT ALLOWED VALUES
        if type_ == bool:
            if not allowed_values:
                allowed_values = [["0", "false"], ["1", "true"]]
        
        if allowed_values:
            
            # CHECKING IF ALLOWED VALUES ITEMS ARE LIST
            if not all(
                isinstance(sublist, list)
                for sublist in allowed_values
            ):
                error_message = f"All items of allowed values must be a list"
                raise TypeError(error_message)

            required_type = type_
            required_type = str if type_ == bool else required_type
            required_type = int if type_ in {float, int} else required_type
            
            # CHECKING IF SUBLIST ITEMS OF ALLOWED VALUES LIST ARE OF CORRECT TYPE
            try:
                for item in allowed_values:
                    for subitem in item:
                        required_type(subitem)
            except:
                error_message = f"All allowed values must be of type: {required_type.__name__}"
                raise TypeError(error_message)          
            
            # IF TYPE_ IS EQUALS TO INT OR FLOAT CHECK IF ALL SUBITEMS HAS LENGTH OF 2
            if type_ == int or type_ == float:
                if not all(
                    len(item) == 2 for item in allowed_values
                ):
                    error_message = f"All sublist of allowed values of type {type_.__name__} must have length of 2"
                    raise TypeError(error_message)
            else:
                for i in range(len(allowed_values)):
                    for j in range(len(allowed_values[i])):
                        allowed_values[i][j] = allowed_values[i][j].lower()

        self.name: str = name
        self.allowed_values: list[list] = allowed_values
        self.help_message: str = help_message
        self.information: str = ""
        self.information += f'{help_message}\n' if help_message else ""
        self.information += f'allowed values: {", ".join("(" + ", ".join(str(subitem) for subitem in item) + ")" for item in allowed_values)}\n' if allowed_values else ""
        self.information += f'type: {type_.__name__}'
        self.type_: type = type_

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        return f'CliArgument(name="{self.name}")'

class CliOption:

    """
    Represents a command-line interface (CLI) option with various constraints and attributes.

    This class allows defining and validating CLI options, including allowed values, 
    prerequisites, and aliases.

    Attributes:
        name (str): The name of the CLI option.
        type_ (type): The expected data type for the option's value.
        aliases (tuple[str]): Alternative names for the option.
        value (Any): The current assigned value of the option.
        allowed_values (list[list]): A list of lists containing valid values for the option.
        help_message (str | None): An optional help message describing the option.
        information (str): A formatted string summarizing the option's details.
        prerequisits (list[list[str]]): A list of prerequisite options that must be set.
        required (bool): Indicates whether the option is required.

    Methods:
        __getitem__(key): Allows accessing instance attributes using dictionary-like syntax.
        __repr__(): Returns a string representation of the instance.

    Raises:
        TypeError: If any argument does not meet the expected type or structure constraints.
    """

    def __init__(self, name:str, type_:type, aliases:set[str]=set(), allowed_values:list[list]=list(), value=None, help_message:str=None, prerequisits:list[list[str]]=list(), required=True):
        
        """
        Initializes a CLI option with validation checks.

        Args:
            name (str): The name of the option.
            type_ (type): The expected type of the option's value.
            aliases (set[str], optional): Alternative names for the option. Defaults to an empty set.
            allowed_values (list[list], optional): Valid values for the option. Defaults to an empty list.
            value (Any, optional): Initial value of the option. Defaults to None.
            help_message (str, optional): Help description for the option. Defaults to None.
            prerequisits (list[list[str]], optional): List of prerequisites required for this option. Defaults to an empty list.
            required (bool, optional): Whether the option is required. Defaults to True.

        Raises:
            TypeError: If `type_` is not a valid type.
            TypeError: If `value` does not match the expected `type_`.
            TypeError: If `prerequisits` is not a list of lists containing strings.
            TypeError: If `allowed_values` does not meet expected constraints.
        """

        # VALIDATING TYPE_ VARIABLE VALUE
        if not isinstance(type_, type):
            error_message = f"type_ parameter must recive a type"
            raise TypeError(error_message)
        
        # VALIDATING THE CONTENT OF THE VALUE VARIABLE
        if value != None:
            if not isinstance(value, type_):
                error_message = f"value parameter must receive an object as a type specified in type_"
                raise TypeError(error_message)

        # VALIDATING PREREQUISITS STRUCTURE
        if not all(
            isinstance(sublist, list) and all(isinstance(item, str) for item in sublist)
            for sublist in prerequisits
        ):
            error_message = f"Prerequisits must be: list[list[str]]"
            raise TypeError(error_message)
        
        if type_ == bool:
            if not allowed_values:
                allowed_values = [["0", "FALSE"], ["1", "TRUE"]]
            required = False
        
        # VALIDATING ALLOWED VALUES
        if allowed_values:
            
            # CHECKING IF ALLOWED VALUES ITEMS ARE LIST
            if not all(
                isinstance(sublist, list)
                for sublist in allowed_values
            ):
                error_message = f"All items of allowed values must be a list"
                raise TypeError(error_message)
            
            required_type = type_
            required_type = str if type_ == bool else required_type
            required_type = int if type_ in {float, int} else required_type
            
            # CHECKING IF SUBLIST ITEMS OF ALLOWED VALUES LIST ARE OF CORRECT TYPE
            try:
                for item in allowed_values:
                    for subitem in item:
                        required_type(subitem)
            except:
                error_message = f"All allowed values must be of type: {required_type.__name__}"
                raise TypeError(error_message)  
            
            if type_ == int or type_ == float:
                if not all(
                    len(item) == 2 for item in allowed_values
                ):
                    error_message = f"All sublist of allowed values of type {type_.__name__} must have length of 2"
                    raise TypeError(error_message)
            else:
                for i in range(len(allowed_values)):
                    for j in range(len(allowed_values[i])):
                        allowed_values[i][j] = allowed_values[i][j].lower()

        self.name: str = name
        self.type_: type = type_
        self.aliases: tuple[str] = tuple(aliases)
        self.value = value
        self.allowed_values: list[list] = allowed_values
        self.help_message = help_message
        self.information: str = ""
        self.information += f'{help_message}\n' if help_message else ""
        self.information += f'prerequisits: {", ".join("(" + ", ".join(item) + ")" for item in prerequisits)}\n' if prerequisits else ""
        self.information += f'allowed values: {", ".join("(" + ", ".join(str(subitem) for subitem in item) + ")" for item in allowed_values)}\n' if allowed_values else ""
        self.information += f'type: {type_.__name__}'
        self.prerequisits: list[list[str]] = prerequisits
        self.required: bool = required
    
    def __getitem__(self, key):
        return self.__dict__[key]
    
    def __repr__(self):
        return f'CliOption(name="{self.name}", aliases={chr(123)}{", ".join([alias for alias in self.aliases])}{chr(125)}, type={self.type_.__name__}, value={self.value})'

class CliCommand:
    def __init__(
            self,
            name:str,
            allowed_arguments:list[str]=None,
            allowed_options:list[str]=None,
            aliases:set[str]=set(),
            arguments:tuple["CliArgument"]|list["CliArgument"]=list(),
            confirmation:bool=False,
            event:callable=lambda arguments, options:f"Add an event to this command.",
            help_message:str=None,
            options:list["CliOption"]|tuple["CliOption"]=list(),
            subcommands:list["CliCommand"]|tuple["CliCommand"]=list()
    ) -> None:

        self.allowed_arguments = allowed_arguments
        self.allowed_options = allowed_options
        self.aliases: set[str] = {item.strip() for item in aliases}
        self.confirmation = confirmation
        self.event: callable = lambda arguments, options: event(arguments, options)
        self.help_message: str = help_message
        self.name: str = name.strip()
        self.options: list["CliOption"] = list()
        self.arguments: list["CliArgument"] = list()
        self.parent = None

        # HANDLE CLASS ENDLESS RECURSION AT __INIT__
        if name != "help":
            self.subcommands: list["CliCommand"] = [CliCommand("help", allowed_arguments=[], allowed_options=[], event=self.help, help_message="Show this message.")]
        else:
            self.subcommands: list["CliCommand"] = list()
        
        # ADDING SUBCOMMANDS
        if subcommands:
            self.add_subcommands(*subcommands)

        # ADDING ARGUMENTS
        if arguments:
            self.add_arguments(*arguments)

        # ADDING OPTIONS
        if options:
            self.add_options(*options)

    def add_subcommands(self, *subcommands:"CliCommand"):
        for subcommand in subcommands:
            subcommand.parent = self
            self.subcommands.append(subcommand)
    
    def add_arguments(self, *arguments:"CliArgument"):
        for argument in arguments:
            self.arguments.append(argument)

    def add_options(self, *options:"CliOption"):
        for option in options:
            self.options.append(option)

    def __getitem__(self, key):
        for value in self.subcommands:
            if value.name == key:
                return value
            
    def help(self, *args):
        collected_options = []
        filtered_options = []
        valid_option_names = set(self.allowed_options or [])

        current_command = self
        while current_command:
            collected_options.extend(current_command.options)
            filtered_options.extend(
                option for option in current_command.options
                if option.name in valid_option_names or valid_option_names.intersection(option.aliases or [])
            )
            current_command = current_command.parent

        collected_options = filtered_options if self.allowed_options is not None else collected_options
        collected_options.sort(key=lambda c: c.name)


        # BUILD OPTIONS
        options = ""
        if collected_options:
            options = "\nOptions:\n\n" + "\n".join([
                f"    --{option['name']}: {(option['help_message'] or 'No description provided.').replace(chr(10), ' ')}\n"
                f"{'        aliases = [--' + ', --'.join(option['aliases']) + ']' + chr(10) if option['aliases'] else ''}"
                f"{'        prerequisits = ' + ', '.join(['(' + ', '.join(['--' + subitem for subitem in item]) + ')' for item in option['prerequisits']]) + chr(10) if option['prerequisits'] else ''}"
                f"{'        allowed_values = ' + ', '.join('[' + ', '.join(str(allowed_value) for allowed_value in allowed_values) + ']' for allowed_values in option['allowed_values']) + chr(10) if option['allowed_values'] else ''}"
                f"{'        type = ' + option['type_'].__name__}\n"
                for option in collected_options
            ])

        collected_arguments = []
        filtered_arguments = []

        current_command = self
        while current_command:
            collected_arguments.extend(current_command.arguments)
            filtered_arguments.extend(
                argument for argument in current_command.arguments
                if argument.name in (self.allowed_arguments or [])
            )
            current_command = current_command.parent

        collected_arguments = filtered_arguments if self.allowed_arguments is not None else collected_arguments
        collected_arguments.sort(key=lambda c: c.name)


        # BUILD ARGUMENTS
        arguments = ""
        if collected_arguments:
            arguments = "\nArguments:\n\n" + "\n".join([
                f"    {argument['name']}: {(argument['help_message'] or 'No description provided.').replace(chr(10), ' ')}\n"
                f"        type = {argument['type_'].__name__}\n"
                for argument in collected_arguments
            ])

        # BUILD SUBCOMMANDS
        all_subcommands = sorted(self.subcommands, key=lambda c: c.name)
        subcommands = ""
        if self.subcommands:
            subcommands = "\nCommands:\n\n" + "\n".join([
                f"    {subcommand.name}: {subcommand.help_message or 'No description provided.'}"
                f"{(chr(10) + '        aliases = ' + ', '.join(subcommand.aliases)) if subcommand.aliases else ''}{chr(10) if not subcommand == all_subcommands[-1] else ''}"
                for subcommand in all_subcommands
            ])

        # RETURN FORMATTED MESSAGE
        return (
            f"Usage: {self.name} (aliases: {', '.join(self.aliases) if self.aliases else 'no aliases'}) [COMMAND] [ARGUMENTS] [OPTIONS]\n\n"
            f"    {self.help_message or 'No description available.'}\n"
            f"{arguments}"
            f"{options}"
            f"{subcommands}"
        )
    
    def __repr__(self):
        return f"""CliCommand(
    name="{self.name}",
    aliases={chr(123)}{", ".join([alias for alias in self.aliases])}{chr(125)},
    arguments={chr(123)}{", ".join([argument for argument in self.arguments])}{chr(125)},
    options={chr(123)}{", ".join([item.name for item in self.options])}{chr(125)},
    subcommands={self.subcommands},
)"""

class CLI(ctk.CTk):
    """
    CLI (Command Line Interface) is a graphical interface built with CustomTkinter (ctk) designed to mimic the behavior of a traditional terminal.

    Features:
    - Supports custom commands, arguments, and options with clear definitions.
    - Provides helper functionality for helping on typing arguments and options.
    - Includes a scrollable form area for displaying detailed input forms dynamically.
    - Maintains a history of executed commands for easy navigation.
    - Allows theme customization and displays the current working directory.
    - Predefined commands like `clear`, `exit`, `cd`, `ls`, `theme`, and `helper`.
    - Built-in autocompletion and hints when Tab is pressed.

    Attributes:
    - helper (bool): Enables or disables command hints and auto-completion.
    - title (str): Title of the application window.
    - commands_history (list[str]): Stores the history of executed commands.
    - form_arguments (list[dict]): Stores form components for CLI arguments.
    - form_options (list[dict]): Stores form components for CLI options.
    - clicommands (CliCommand): The root command containing all subcommands.
    - current_working_directory (str): Tracks the current working directory.
    - current_theme (str): Tracks the current appearance theme (dark, light, or system).

    The CLI is interactive and extensible, allowing users to add custom commands with events, arguments, and options.
    """
    def __init__(self, helper:bool=True, title:str="Cli"):

        """
        Initializes the CLI interface with default settings, predefined commands, and UI components.

        Args:
        - helper (bool): If True, enables the helper functionality.
        - title (str): The title of the application window.
        """

        super().__init__()
        self.title(title)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.geometry("600x400")

        # DEFINING CLIVARIABLES
        self.program_path = os.path.dirname(os.path.abspath(__file__))
        self.clidata = {
            "commands_history": [], # list[str]
            "current_theme": ctk.get_appearance_mode(), # str
            "current_working_directory": os.getcwd(), # str
            "helper": helper, # bool
        }

        if os.path.exists(os.path.join(self.program_path, "clidata.yaml")):
            with open(os.path.join(self.program_path, "clidata.yaml"), "r") as file:
                self.clidata = yaml.safe_load(file)

        os.chdir(self.clidata["current_working_directory"])

        ctk.set_appearance_mode(self.clidata["current_theme"])

        self.current_history_index: int = -1
        self.confirmed = False
        self.form_arguments: list[dict[ctk.CTkButton, ctk.CTkEntry, ctk.CTkLabel, ctk.CTkLabel]] = []
        self.form_options: list[dict[ctk.CTkButton, ctk.CTkEntry, ctk.CTkLabel, ctk.CTkLabel, list[tuple[ctk.CTkLabel]]]] = []

        self.clicommands = CliCommand(
            name="", # MAIN COMMAND
        )

        self.clicommands.add_subcommands(CliCommand("clear", aliases=["clr"], event=self.__clear, help_message="Clears the terminal."))
        self.clicommands.add_subcommands(CliCommand("exit", event=lambda *args: self.quit(), help_message="Exit the program."))
        self.clicommands.add_subcommands(
            CliCommand(
                "cd",
                arguments=[CliArgument("path", help_message="Path to change to.", type_=str)],
                event=self.__change_directory,
                help_message="Change directory."
            )
        )
        self.clicommands.add_subcommands(
            CliCommand(
                "ls",
                arguments=[CliArgument("path", help_message="Path to list its files and folders.", type_=str)],
                event=self.__list,
                help_message="List elements of current directory.",
            )
        )
        self.clicommands.add_subcommands(
            CliCommand(
                "theme",
                event=lambda *args: self.clidata["current_theme"],
                help_message="Show the current theme name.",
                subcommands=[
                    CliCommand(
                        "set",
                        event=self.set_theme,
                        help_message="Set the theme mode to that specified by user.",
                        options=[CliOption("theme-mode", allowed_values=[["LIGHT", "DARK", "SYSTEM"]], help_message="Theme mode.", required=True, type_=str)]
                    )
                ]
            )
        )
        self.clicommands.add_subcommands(CliCommand(
            "helper",
            event=self.change_helper_state,
            help_message="Turn on/off helper.",
            options=[CliOption("on", type_=bool, required=False), CliOption("off", type_=bool, required=False)],
            )
        )

        self.current_working_directory_label = ctk.CTkLabel(
            self,
            anchor=tk.W,
            corner_radius=20,
            fg_color=("gray85", "gray20"),
            font=("Verdana", 13),
            text=self.clidata["current_working_directory"],
        )
        self.current_working_directory_label.grid(padx=10, pady=(10, 0), sticky=tk.EW)

        # TEXT AREA
        self.text_area = ctk.CTkTextbox(
            self, 
            font=("Verdana", 15), 
            text_color=("#222222", "#DDDDDD"), 
            width=580, 
            height=300, 
            wrap="word"
        )
        self.text_area.configure(state="disabled")
        self.text_area.grid(column=0, row=1, padx=10, pady=(10, 5), sticky=tk.NSEW)

        self.progressbar = ctk.CTkProgressBar(self.text_area)
        self.progressbar.place(relx=0.5, rely=1, relwidth=1, anchor="center")
        self.progressbar.set(0)

        # DEFINING TEXT TAGS
        self.text_area.tag_config("error", foreground="#ff0d29")
        self.text_area.tag_config("command", foreground="#e08e00")
        self.text_area.tag_config("warning", foreground="#e64c00")
        self.text_area.tag_config("hint", foreground="#0077e6")

        # FORM AREA
        self.form_area = ctk.CTkScrollableFrame(self, width=580, height=300)
        self.form_area.grid(column=0, row=1, padx=10, pady=(10, 5), sticky=tk.NSEW)
        self.form_area.grid_forget()

        # TO MOUSE WHEEL EVENT WORK ON LINUX
        self.form_area.bind_all("<Button-4>", lambda event: self.form_area._parent_canvas.yview("scroll", -1, "units"))
        self.form_area.bind_all("<Button-5>", lambda event: self.form_area._parent_canvas.yview("scroll", 1, "units"))

        self.string_var = tk.StringVar()

        # ENTRY FOR COMMANDS
        self.command_entry = ctk.CTkEntry(self, width=580, font=("Verdana", 15), placeholder_text="Type a command", takefocus=True, textvariable=self.string_var)
        self.command_entry.grid(padx=10, pady=(5, 10), sticky=tk.EW)
        self.bind("<Return>", lambda event: self.run(commands_line=self.command_entry.get().strip()))
        self.bind("<KP_Enter>", lambda event: self.run(commands_line=self.command_entry.get().strip()))
        self.after(100, self.command_entry.focus_set)

        # BINDING EVENTS TO CLI

        ## HISTORY
        self.command_entry.bind("<Up>", lambda event: self.select_old_commands(
            entry=self.command_entry,
            event=event,
        ))
        self.command_entry.bind("<Down>", lambda event: self.select_old_commands(
            entry=self.command_entry,
            event=event,
        ))

        ## AUTOCOMPLETE
        self.bind("<Tab>", lambda event: self.command_entry_has_changed(event=event, entry=self.command_entry), add="+")
        self.bind("<Key>", self.typer_helper, add="+")
        self.bind("<Control-c>", lambda event: self.cancel())
        self.bind("<Control-C>", lambda event: self.cancel())

    def change_helper_state(self, arguments: dict[str], options: dict[str]):

        """
        Toggle or query the state of the CLI helper (auto-completion and hints).

        This method checks for specific options to either enable or disable the helper mode.
        - If the "on" option is present, it sets the helper mode to True.
        - If the "off" option is present, it toggles the helper mode to False (by negating the given value).
        - If neither is provided, it returns a CliMessage indicating the current state ("On" or "Off").

        After modifying the state, the method writes the updated configuration to the 'clidata.yaml' file.

        Parameters:
            arguments (dict[str, Any]): A dictionary of command arguments (unused in this method).
            options (dict[str, Any]): A dictionary of options to control the helper state.

        Returns:
            CliMessage: When no state change is specified, returns a message with the current helper status.
        """


        if "on" in options:
            self.clidata["helper"] = options["on"]
        elif "off" in options:
            self.clidata["helper"] = not options["off"]
        else:
            return CliMessage("On" if self.clidata["helper"] else "Off")
        
        with open(os.path.join(self.program_path, "clidata.yaml"), "w") as file:
            yaml.dump(self.clidata, file, allow_unicode=True, sort_keys=False)

    def add_commands(self, *commands: "CliCommand"):

        """
        Add custom commands to the CLI's command structure.

        Each provided command is added as a subcommand of the main CLI command.

        Parameters:
            *commands (CliCommand): One or more CliCommand objects to be added.
        """

        for command in commands:
            self.clicommands.add_subcommands(command)

    def __activate_form_area(self):

        """
        Activate the form area for dynamic input forms.

        If the text area is currently displayed, it is removed.
        Then, the form area is displayed (if it is not already visible) with appropriate grid configuration.
        """

        if self.text_area.winfo_ismapped():
            self.text_area.grid_forget()

        if not self.form_area.winfo_ismapped():
            self.form_area.grid(column=0, row=1, padx=10, pady=(10, 5), sticky=tk.NSEW)

    def __activate_text_area(self):

        """
        Activate the text area for displaying command output.

        If the form area is visible, it is hidden.
        Then, the text area is displayed (if it is not already visible) with the proper grid settings.
        """

        if self.form_area.winfo_ismapped():
            self.form_area.grid_forget()

        if not self.text_area.winfo_ismapped():
            self.text_area.grid(column=0, row=1, padx=10, pady=(10, 5), sticky=tk.NSEW)

    def __activate_commands_entry(self):

        """
        Activate and prepare the command entry field for new input.

        This method enables the command entry widget, clears any existing text, and sets the focus
        so that the user can immediately begin typing a new command.
        """

        self.command_entry.configure(state=tk.NORMAL)
        self.command_entry.delete(0, tk.END)
        self.command_entry.focus()

    def cancel(self):

        """
        Cancel the current operation or command.

        This method resets the confirmation flag, reactivates the text area,
        and prepares the command entry for further input.
        """

        self.confirmed = False
        self.__activate_text_area()
        self.__activate_commands_entry()
    
    def set_theme(self, arguments:dict[str], options:dict[str]):

        """
        Set the appearance theme of the CLI interface.

        Changes the current theme based on the provided 'theme_mode' option. Supported themes are:
        - "dark": Switch to Dark mode.
        - "light": Switch to Light mode.
        - "system": Use the system's default theme.
        
        If an unsupported theme is specified, a warning CliMessage is returned. The method also updates
        the configuration in 'clidata.yaml' with the new theme.

        Parameters:
            arguments (dict[str, Any]): A dictionary of command arguments (unused in this method).
            options (dict[str, Any]): A dictionary containing the "theme_mode" option, e.g., {"theme_mode": "dark"}.

        Returns:
            CliMessage: A warning message if an invalid theme mode is provided.
        """

        match options["theme_mode"].lower():
            case "dark":
                self.clidata["current_theme"] = "Dark"
                self.after(100, lambda: ctk.set_appearance_mode("Dark"))
            case "light":
                self.clidata["current_theme"] = "Light"
                self.after(100, lambda: ctk.set_appearance_mode("Light"))
            case "system":
                self.clidata["current_theme"] = "System"
                self.after(100, lambda: ctk.set_appearance_mode("System"))
            case _:
                return CliMessage(message="Available themes mode: dark, light or system", status="warning")
        
        with open(os.path.join(self.program_path, "clidata.yaml"), "w") as file:
            yaml.dump(self.clidata, file, allow_unicode=True, sort_keys=False)

    def typer_helper(self, event: tk.Event):

        """
        Assist with faster typing in the command entry field.

        This method listens for key events and automatically duplicates certain characters under the right conditions:
        - Duplicates a dash ('-') to facilitate quick typing of options.
        - Duplicates single (') and double (") quotes to help with typing arguments.

        The behavior is determined by the current position in the command entry and the surrounding text.

        Parameters:
            event (tk.Event): The key event triggered by the user's input.
        """

        key = event.char

        if key in ("'", '"', "-"):
            commands_line = self.command_entry.get()
            current_index = self.command_entry.index(tk.INSERT)
            commands_line_length = self.command_entry.index(tk.END)

            if commands_line:

                if key == "-" and (commands_line[current_index - 2] == " " or commands_line_length == 1):
                    self.command_entry.insert(tk.INSERT, "-")

                elif key == "'" and (commands_line[current_index - 2] == " " or commands_line_length == 1):
                    self.command_entry.insert(current_index, "'")
                    self.command_entry.icursor(current_index)
                
                elif key == '"' and (commands_line[current_index - 2] == " " or commands_line_length == 1):
                    self.command_entry.insert(current_index, '"')
                    self.command_entry.icursor(current_index)
    
    def __change_directory(self, arguments: dict[str], options: dict[str]):

        """
        Change the current working directory of the CLI.

        Attempts to change the directory to the path provided in the 'arguments' dictionary.
        On success, updates the current working directory in the configuration and refreshes the display label.
        If the directory change fails (e.g., the path is not found), returns a CliMessage with an error status.

        Parameters:
            arguments (dict[str, Any]): A dictionary containing the "path" key with the target directory.
            options (dict[str, Any]): A dictionary of additional options (unused in this method).

        Returns:
            CliMessage: An error message if the specified path is not found.
        """

        try:
            os.chdir(arguments["path"])
            self.clidata["current_working_directory"] = os.getcwd()
            self.current_working_directory_label.configure(text=self.clidata["current_working_directory"])
        except:
            return CliMessage("Path not found.", status="error")
        
        with open(os.path.join(self.program_path, "clidata.yaml"), "w") as file:
            yaml.dump(self.clidata, file, allow_unicode=True, sort_keys=False)

    def __clear(self, *args):

        """
        Clear the content of the text area.

        This method enables the text area, deletes all text, and then disables it again to prevent further editing.

        Parameters:
            *args: Additional arguments (not used).
        """

        self.text_area.configure(state="normal")
        self.text_area.delete("0.0", tk.END)
        self.text_area.configure(state="disabled")

    def __list(self, arguments: dict[str], options: dict[str]):

        """
        List the contents of a specified directory.

        Retrieves the list of files and directories within the path provided in the 'arguments' dictionary.
        - If the specified path does not exist, returns a CliMessage with an error status.
        - If access is forbidden or another error occurs during listing, returns a CliMessage with a warning.
        - On success, returns a CliMessage containing a newline-separated list of directory contents.

        Parameters:
            arguments (dict[str, Any]): A dictionary containing the "path" key with the directory to list.
            options (dict[str, Any]): A dictionary of additional options (unused in this method).

        Returns:
            CliMessage: A message containing the directory listing, or an error/warning if applicable.
        """

        if not os.path.exists(arguments["path"]):
            return CliMessage("Path not found.", status="error")
        try:
            return CliMessage("\n".join(os.listdir(arguments["path"])))
        except:
            return CliMessage("Forbiden access.", status="warning")

    def append_message(self, commands_line: str, climessage: CliMessage | None | str, end: str = "\n\n"):

        """
        Append a command and its resulting message to the text area.

        Displays the entered command prefixed with "> " using a designated tag.
        Then, based on the type of the provided message (CliMessage or str), it displays:
        - Status-specific tags (e.g., error, warning, hint) for a CliMessage.
        - A simple string message if a plain text message is provided.
        The text area is then updated and scrolled to the end for visibility.

        Note: If the command is "clear" or "clr", no message is appended.

        Parameters:
            commands_line (str): The command input that was executed.
            climessage (CliMessage | None | str): The output message associated with the command.
                It can be an instance of CliMessage or a simple string.
            end (str, optional): A string appended to the end of the message (default is two newline characters).
        """

        if not commands_line.strip() in {"clear", "clr"}:
            self.text_area.configure(state="normal")
            self.text_area.insert(tk.END, f"> {commands_line}\n", tags="command") # COMMANDS

            if isinstance(climessage, CliMessage):
                match climessage.status:
                    case "error":
                        self.text_area.insert(tk.END, f"({climessage.status}) ", tags=climessage.status)
                    case "warning":
                        self.text_area.insert(tk.END, f"({climessage.status}) ", tags=climessage.status)
                    case "hint":
                        self.text_area.insert(tk.END, f"({climessage.status}) ", tags=climessage.status)
                
                self.text_area.insert(tk.END, f"{climessage.message}{end}")
            elif isinstance(climessage, str):
                self.text_area.insert(tk.END, f"{climessage}{end}")
            else:
                self.text_area.insert(tk.END, "\n")

            self.text_area.configure(state="disabled")
            self.text_area.see(tk.END)

    def update_commands_history(self, commands_line: str):

        """
        Updates the command history by adding a new command.

        This method ensures that the command history is maintained efficiently by:
        - Preventing duplicate consecutive entries.
        - Keeping the history within a limit of 1000 commands.
        - Storing the updated history in a YAML file.

        Args:
            commands_line (str): The command entered by the user.

        Side Effects:
            - Modifies `self.clidata["commands_history"]`.
            - Writes updated history to `clidata.yaml`.

        """

        if self.clidata["commands_history"] != []:
            if commands_line != self.clidata["commands_history"][0]:
                self.clidata["commands_history"] = [commands_line] + self.clidata["commands_history"]
            if len(self.clidata["commands_history"]) >= 1000:
                self.clidata["commands_history"].pop()
        else:
            self.clidata["commands_history"].append(commands_line)

        with open(os.path.join(self.program_path, "clidata.yaml"), "w") as file:
            yaml.dump(self.clidata, file, allow_unicode=True, sort_keys=False)
        
        self.current_history_index = -1

    def split_commands_line(self, commands_line: str) -> tuple[list[str], list[str], dict[str, list]]:

        """
        Parses a command-line input string into commands, arguments, and options.

        This method uses regex to properly extract:
        - Commands (words outside of quotes)
        - Arguments (values inside quotes)
        - Options (key-value pairs prefixed with "--")

        Args:
            commands_line (str): The command-line string entered by the user.

        Returns:
            tuple:
                - list[str]: Extracted commands.
                - list[str]: Extracted arguments.
                - dict[str, list]: Extracted options, structured as {"keys": [...], "values": [...]}.
        """

        commands: list[str] = []
        arguments: list[str] = []
        options: dict[str, list] = {"keys": [], "values": []}

        # Atualizado: Regex para capturar opções, comandos e argumentos
        pattern = r'--([\w\-]+)(?:=(?:"([^"]*)"|\'([^\']*)\'|([^\s]+)))?|([^\s"\']+)|["\']([^"\']*)["\']'

        # Dividindo a linha de comando com o padrão regex
        command_parts = re.findall(pattern, commands_line.strip())

        for part in command_parts:
            if part[0]:  # OPTION (e.g., --option or --option=value)
                key = part[0]
                value = part[1] or part[2] or part[3] or None  # Captura o valor da opção (se existir)
                options["keys"].append(key)
                options["values"].append(value)
            elif part[4]:  # COMMAND ou PARTE DO COMANDO (fora de aspas)
                commands.append(part[4])
            elif part[5]:  # ARGUMENT (dentro de aspas simples ou duplas)
                arguments.append(part[5])

        return commands, arguments, options

    
    def validate_commands(self, extracted_commands: list["CliCommand"], user_commands: list[str]) -> CliMessage | None:

        """
        Validates if the user-provided commands exist.

        Compares the parsed user commands against known CLI commands and 
        returns an error message if any commands are unrecognized.

        Args:
            extracted_commands (list["CliCommand"]): List of recognized commands.
            user_commands (list[str]): List of user-entered commands.

        Returns:
            CliMessage | None: An error message if unknown commands are found, otherwise None.
        """

        commands_not_found = user_commands[len(extracted_commands) - 1:]
        if commands_not_found:
            return CliMessage(message=f"Commands not found: {', '.join(commands_not_found)}", status="error")
    
    def validate_arguments(self, extracted_arguments: list["CliArgument"], user_arguments: list[str], prepared_arguments: dict[str]) -> CliMessage | None:
        
        """
        Validates the arguments provided by the user.

        This method ensures:
        - The correct number of arguments are provided.
        - Arguments are of the expected data type.
        - Numeric arguments fall within allowed ranges.
        - Boolean arguments are properly interpreted.
        - Arguments are stored in `prepared_arguments` if valid.

        Args:
            extracted_arguments (list["CliArgument"]): Expected argument definitions.
            user_arguments (list[str]): Arguments entered by the user.
            prepared_arguments (dict[str]): Dictionary where validated arguments are stored.

        Returns:
            CliMessage | None: An error message if validation fails, otherwise None.
        """

        def value_is_of_correct_type() -> bool:
            try:
                if type_ == bool:
                    if not user_arguments[i].lower() in sum(extracted_arguments[i].allowed_values, []):
                        raise
                elif type_ == int:
                    if "." in user_arguments[i]:
                        raise
                    value = type_(float(user_arguments[i]))
                    if extracted_arguments[i].allowed_values:
                        if not any(
                            allowed_value[0] <= value <= allowed_value[1]
                            for allowed_value in extracted_arguments[i].allowed_values
                        ):
                            raise
                elif type_ == float:
                    value = type_(user_arguments[i])
                    if extracted_arguments[i].allowed_values:
                        if not any(
                            allowed_value[0] <= value <= allowed_value[1]
                            for allowed_value in extracted_arguments[i].allowed_values
                        ):
                            raise
                else:
                    if extracted_arguments[i].allowed_values:
                        if not user_arguments[i].lower() in sum(extracted_arguments[i].allowed_values, []):
                            raise
            except:
                return False
            return True

        missing_arguments: list["CliArgument"] = []; overflow_arguments: list[str] = []; arguments_with_invalid_value: list[list[str]] = []

        missing_arguments = extracted_arguments[len(user_arguments):]
        overflow_arguments = user_arguments[len(extracted_arguments):]

        if not (missing_arguments and overflow_arguments):
            for i in range(len(extracted_arguments)):

                key = extracted_arguments[i].name.replace("-", "_")
                type_ = extracted_arguments[i].type_
                value = user_arguments[i] if i < len(user_arguments) else None
                try:
                    if not value_is_of_correct_type():
                        raise
                    value = False if type_ == bool and user_arguments[i] in extracted_arguments[i].allowed_values[0] else type_(user_arguments[i])
                except:
                    arguments_with_invalid_value.append([extracted_arguments[i].name, user_arguments[i] if i < len(user_arguments) else None, type_.__name__])
                if value != None:
                    prepared_arguments[key] = value

        if missing_arguments:
            return CliMessage(message=f"Missing arguments: {', '.join([item.name for item in missing_arguments])}", status="error")
        elif overflow_arguments:
            return CliMessage(message=f"Overflow arguments: {', '.join(overflow_arguments)}", status="error")
        elif arguments_with_invalid_value:
            return CliMessage(message=f"Arguments with invalid value: {', '.join(f'{item[0]}={item[1]} ({item[2]})' for item in arguments_with_invalid_value)}", status="error")

    def validate_options(self, extracted_options: list["CliOption"], user_options: dict[str, list[str]], prepared_options: dict[str]) -> CliMessage | None:
        
        """
        Validates user-provided options against expected CLI options.

        Ensures:
        - Options exist and match predefined ones.
        - Values provided for options are of the correct type.
        - Required options are present.
        - Options with dependencies (prerequisites) meet their conditions.
        - Non-existent options are flagged as errors.

        Args:
            extracted_options (list["CliOption"]): Expected option definitions.
            user_options (dict[str, list[str]]): User-entered options.
            prepared_options (dict[str]): Dictionary where validated options are stored.

        Returns:
            CliMessage | None: An error message if validation fails, otherwise None.
        """

        def get_prerequisits() -> tuple[list[list[str]], list[list[str]]]:
            satisfied_prerequisits = []; non_satisfied_prerequisits = []
            for item in extracted_option.prerequisits:
                if any(subitem in user_options_names for subitem in item):
                    satisfied_prerequisits.append(item)
                else:
                    non_satisfied_prerequisits.append(item)

            return satisfied_prerequisits, non_satisfied_prerequisits

        def value_is_of_correct_type() -> bool:
            try:
                if type_ == bool:
                    if not user_options["values"][i].lower() in sum(extracted_option.allowed_values, []):
                        raise
                elif type_ == int:
                    if "." in user_options["values"][i]:
                        raise
                    value = type_(float(user_options["values"][i]))
                    if extracted_option.allowed_values:
                        if not any(
                            allowed_value[0] <= value <= allowed_value[1]
                            for allowed_value in extracted_option.allowed_values
                        ):
                            raise

                elif type_ == float:
                    value = type_(user_options["values"][i])
                    if extracted_option.allowed_values:
                        if not any(
                            allowed_value[0] <= value <= allowed_value[1]
                            for allowed_value in extracted_option.allowed_values
                        ):
                            raise
                else:
                    if extracted_option.allowed_values:
                        if not user_options["values"][i].lower() in sum(extracted_option.allowed_values, []):
                            raise
            except:
                return False
            return True

        def required():
            nonlocal option_is_missing, options_with_invalid_value
            value = None
            if user_options["values"][i] != None:
                try:
                    if not value_is_of_correct_type():
                        raise
                    option_is_missing = False
                    value = False if type_ == bool and user_options["values"][i].lower() in extracted_option.allowed_values[0] else type_(user_options["values"][i])
                except:
                    options_with_invalid_value.append(["--" + extracted_option.name, user_options["values"][i], type_.__name__])

            return value
        
        def optional():
            nonlocal option_is_missing, options_with_invalid_value

            value = None
            try:
                if user_options["values"][i] != None:
                    if not value_is_of_correct_type():
                        raise
                    option_is_missing = False
                    value = False if type_ == bool and user_options["values"][i].lower() in extracted_option.allowed_values[0] else  type_(user_options["values"][i])
                else:
                    if type_ == bool:
                        if extracted_option.value == None: value = True
                        else: value = not value
                        option_is_missing = False
            except:
                options_with_invalid_value.append(["--" + extracted_option.name, user_options["values"][i], type_.__name__])
            
            return value

        missing_required_options: list["CliOption"] = []; non_existing_options: list[str] = []
        options_with_invalid_value: list[list[str]] = []; missing_option_prerequisits: list[list[str]] = []

        user_options_names: set[str] = set(tuple(user_options["keys"]))

        # EXTRACTING MISSING OPTIONS
        for extracted_option in extracted_options:
            option_is_missing = True
            type_ = extracted_option.type_

            # GETTING PREREQUISITS
            satisfied_prerequisits, non_satisfied_prerequisits = get_prerequisits()

            for i in range(len(user_options["keys"])):
                if user_options["keys"][i] == extracted_option.name or user_options["keys"][i] in extracted_option.aliases:
                    key = user_options["keys"][i].replace("-", "_")
                    value = user_options["values"][i]
                    prepared_options[key] = value
                    if satisfied_prerequisits == extracted_option.prerequisits:
                        if extracted_option.required: # REQUIRED
                            value = required()
                        else: # OPTIONAL
                            value = optional()
                        if value != None:
                            prepared_options[key] = value 
                        break
                    else:
                        missing_option_prerequisits.append(["--" + user_options["keys"][i], ", ".join(["(" + ", ".join(["--" + subitem for subitem in item]) + ")" for item in non_satisfied_prerequisits])])
                        option_is_missing = False

            if option_is_missing: # OPTIONAL
                if satisfied_prerequisits != extracted_option.prerequisits:
                    option_is_missing = False
                elif not extracted_option.required:
                    option_is_missing = False
                

            if option_is_missing:
                missing_required_options.append(extracted_option)

        # EXTRACTING NON EXISTING OPTIONS
        for user_option_name in user_options["keys"]:
            if not any(
                user_option_name == extracted_option.name or user_option_name in extracted_option.aliases
                for extracted_option in extracted_options
            ):
                non_existing_options.append(user_option_name)

        if options_with_invalid_value:
            return CliMessage(message=f"Options with invalid value: {', '.join([f'{item[0]}={item[1]} ({item[2]})' for item in options_with_invalid_value])}", status="error")
        elif missing_required_options:
            return CliMessage(message=f"Missing required options: {', '.join([item.name for item in missing_required_options])}", status="error")
        elif non_existing_options:
            return CliMessage(message=f"Non existing options: {', '.join(['--' + item for item in non_existing_options])}", status="error")
        elif missing_option_prerequisits:
            return CliMessage(message=f"Missing option prerequisits: {', '.join(f'{item[0]} ({item[1]})' for item in missing_option_prerequisits)}", status="error")
    
    def extract_arguments_and_options_from_form(self) -> str:

        """
        Extracts arguments and options from the form UI.

        This method retrieves user-entered values from form fields,
        ensuring that:
        - Only enabled fields are considered.
        - Arguments are formatted with quotes if needed.
        - Options are formatted as key-value pairs (e.g., `--option="value"`).

        Returns:
            str: A formatted string of extracted arguments and options.
        """

        arguments_and_options = ""
        for form_argument in self.form_arguments:
            if form_argument["value"]._state == "normal":
                value = form_argument["value"].get().strip()
                if value:
                    arguments_and_options += f' "{value}"'


        for form_option in self.form_options:
            if form_option["value"]._state == "normal":
                value = form_option["value"].get().strip()
                if value:
                    arguments_and_options += f' --{form_option["key"].get()}="{value}"' 

        return arguments_and_options

    def run(self, commands_line:str):

        """
        Processes a command-line input string, extracts commands, arguments, and options,
        validates them, and executes the corresponding command event.

        Args:
            commands_line (str): The command-line input provided by the user.

        Behavior:
        - Extracts commands, arguments, and options.
        - Validates extracted commands, arguments, and options.
        - If errors are found, they are displayed, and a form may be activated for corrections.
        - If no errors are found, the command event is executed.
        """

        if commands_line or self.form_area.winfo_ismapped():

            if self.form_area.winfo_ismapped():
                commands, arguments, options = self.split_commands_line(commands_line=self.clidata["commands_history"][0])
                commands_line = " ".join(commands) + self.extract_arguments_and_options_from_form()
                commands, arguments, options = self.split_commands_line(commands_line=commands_line)
            else:
                commands, arguments, options = self.split_commands_line(commands_line=commands_line)

            # CHECKING IF COMMANDS EXISTS
            extracted_commands, extracted_arguments, extracted_options = self.extract_commands_arguments_and_options(commands=commands)

            extracted_arguments = self.filtering_extracted_arguments(extracted_arguments=extracted_arguments, last_command=extracted_commands[-1])
            extracted_options = self.filtering_extracted_options(extracted_options=extracted_options, last_command=extracted_commands[-1])

            prepared_arguments = dict(); prepared_options = dict()

            command_error_message = arguments_error_message = options_error_message = None
                
            command_error_message = self.validate_commands(extracted_commands, commands)
            arguments_error_message = self.validate_arguments(extracted_arguments, arguments, prepared_arguments)
            options_error_message = self.validate_options(extracted_options, options, prepared_options)
            
            if command_error_message or arguments_error_message or options_error_message or extracted_commands[-1].confirmation and not self.confirmed:
                error_message = command_error_message or arguments_error_message or options_error_message

                if not self.form_area.winfo_ismapped():
                    
                    if not command_error_message and self.clidata["helper"]:
                        if extracted_arguments or extracted_options:
                            self.confirmed = True
                            self.__activate_form_area()
                            self.form_arguments = []; self.form_options = []
                            self.setup_form(extracted_arguments, extracted_options, prepared_arguments, prepared_options)
                    else:
                        self.append_message(commands_line, error_message)

                    self.update_commands_history(commands_line=commands_line)
                    self.command_entry.delete(0, tk.END)
                else:
                    self.next_option_or_argument()
                    self.bell()
            else:
                self.confirmed = False
                self.__activate_text_area()
                self.__activate_commands_entry()
                command_message: "CliMessage"|None = extracted_commands[-1].event(prepared_arguments, prepared_options)
                self.append_message(commands_line, command_message)
                self.update_commands_history(commands_line=commands_line)
                
            self.current_history_index = -1

    def next_option_or_argument(self):

        """
        Moves the focus to the next required argument or option in the form UI if the previous one is incomplete.

        Behavior:
        - Identifies the next input field that needs user input.
        - Highlights or selects the field if it is required and not filled.
        """

        for form_option in self.form_options:
            if form_option["value"]._state == "normal":
                if form_option["required"]._text == "*" and form_option["value"].get().strip() == "" or form_option["value"]._border_color == ("red", "red"):
                    form_option["value"].focus()
                    form_option["value"].select_range(0, tk.END)
                    break  

        for form_argument in self.form_arguments:
            if form_argument["value"].get().strip() == "" or form_argument["value"]._border_color == ("red", "red"):
                form_argument["value"].focus()
                form_argument["value"].select_range(0, tk.END)
                break    
    
    def setup_form(self, extracted_arguments:list["CliArgument"], extracted_options:list["CliOption"], prepared_arguments:dict[str], prepared_options:dict[str]):
        
        """
        Configures the command input form with extracted arguments and options,
        providing a UI for user input and validation.

        Args:
            extracted_arguments (list[CliArgument]): The list of extracted command arguments.
            extracted_options (list[CliOption]): The list of extracted command options.
            prepared_arguments (dict[str]): Dictionary of validated argument values.
            prepared_options (dict[str]): Dictionary of validated option values.

        Behavior:
        - Initializes a graphical form to assist users in entering command parameters.
        - Provides validation mechanisms to ensure correct input.
        - Displays additional information such as required fields and prerequisites.
        """
        
        def validate_input(
            validation_object:str="BOTH",
            index:int=None,
        ):
            if validation_object == "ARGUMENT":
                form_objects = [self.form_arguments]
            elif validation_object == "OPTION":
                form_objects = [self.form_options]
            else:
                form_objects = [self.form_arguments, self.form_options]
            
            for form_object in form_objects:
                start =  0 if index == None else index
                stop = len(form_object) if index == None else index + 1
                extracted_object = extracted_arguments if form_object == self.form_arguments else extracted_options
                for i in range(start, stop):
                    if form_object[i]["value"].get().strip():
                        try:
                            
                            if form_object[i]["type_"]._text == "bool":
                                if not form_object[i]["value"].get().lower() in sum(extracted_object[i].allowed_values, []):
                                    raise
                            elif form_object[i]["type_"]._text == "int":
                                if "." in form_object[i]["value"].get():
                                    raise
                                value = int(float(form_object[i]["value"].get()))
                                if extracted_object[i].allowed_values:
                                    if not any(
                                        allowed_value[0] <= value <= allowed_value[1]
                                        for allowed_value in extracted_object[i].allowed_values
                                    ):
                                        raise
                            elif form_object[i]["type_"]._text == "float":
                                value = float(form_object[i]["value"].get())
                                if extracted_object[i].allowed_values:
                                    if not any(
                                        allowed_value[0] <= value <= allowed_value[1]
                                        for allowed_value in extracted_object[i].allowed_values
                                    ):
                                        raise
                            else:
                                if extracted_object[i].allowed_values:
                                    if not form_object[i]["value"].get().lower() in sum(extracted_object[i].allowed_values, []):
                                        raise
                
                            form_object[i]["value"].configure(border_color=("#73cf27", "lightgreen"))
                        except:
                            form_object[i]["value"].configure(border_color=("red", "red"))
                    else:
                        form_object[i]["value"].configure(border_color=("#979DA2", "#565B5E"))

        def check_prerequisits():            
            
            for i in range(len(self.form_options)):
                satisfied_prerequisits = []
                prerequisits_1 = self.form_options[i]["prerequisits"]
                
                for j in range(len(prerequisits_1)):
                    subprerequisit_1 = prerequisits_1[j]
                    subprerequisit_is_satisfied = False
                    for k in range(len(self.form_options)):
                        if i != k:
                            key_2 = self.form_options[k]["key"].get()
                            if key_2 in subprerequisit_1._text and self.form_options[k]["value"].get().strip() != "" and self.form_options[k]["value"]._border_color != ("red", "red"):
                                subprerequisit_is_satisfied = True
                                break
                    
                    ##d85300
                    if subprerequisit_is_satisfied:
                        subprerequisit_1.configure(fg_color=("#d92f00", "#d92f00"))
                        satisfied_prerequisits.append(subprerequisit_1)
                    else:
                        subprerequisit_1.configure(fg_color=("#979da2", "#4a4a4a"))
            
                if tuple(satisfied_prerequisits) == prerequisits_1:
                    self.form_options[i]["value"].configure(state=tk.NORMAL)
                else:
                    self.form_options[i]["value"].configure(border_color=("#979DA2", "#565B5E"))
                    self.form_options[i]["value"].delete(0, tk.END)
                    self.form_options[i]["value"].configure(state=tk.DISABLED)
        
        self.command_entry.delete(0, tk.END)
        self.form_area.grid(column=0, row=1, padx=10, pady=(10, 5), sticky=tk.NSEW)
        self.command_entry.configure(state=tk.DISABLED)

        for child in self.form_area.winfo_children():
            child.destroy()

        # LEGEND
        ctk.CTkLabel(self.form_area, font=("Verdana", 15), text="Legend").grid(padx=(10, 0), sticky=tk.W)

        # INFORMATION
        ctk.CTkLabel(self.form_area, corner_radius=5, fg_color="purple", font=("Verdana", 15), text="information", text_color="white").grid(padx=(20, 0), pady=(10, 0), sticky=tk.W)
        # NAME AND ALIASES
        ctk.CTkLabel(self.form_area, corner_radius=20, fg_color=("#3b8ed0", "#1f6aa5"), font=("Verdana", 15), text="name and aliases", text_color="white").grid(padx=(20, 0), pady=(10, 0), sticky=tk.W)
        # PREREQUISITS
        ctk.CTkLabel(self.form_area, corner_radius=5, fg_color="darkorange", font=("Verdana", 15), text="prerequisits", text_color="white").grid(padx=(20, 0), pady=(10, 0), sticky=tk.W)
        # TYPE
        ctk.CTkLabel(self.form_area, corner_radius=5, fg_color="#00a35f", font=("Verdana", 15), text="type", text_color="white").grid(padx=(20, 0), pady=(10, 10), sticky=tk.W)
        

        # ARGUMENTS
        row_counter = 0
        if extracted_arguments:
            ctk.CTkLabel(self.form_area, font=("Verdana", 15), text="Arguments").grid(padx=(10, 0), sticky=tk.W)

            arguments_frame = ctk.CTkFrame(self.form_area); arguments_frame.grid(pady=(0, 14), sticky=tk.W)
            for argument in extracted_arguments:
                frame = ctk.CTkFrame(arguments_frame, fg_color="transparent"); frame.rowconfigure(0, weight=1)
                frame.grid(column=0, padx=10, pady=(10, 0), row=row_counter, sticky=tk.W)

                # INFO LABEL
                info_label= ctk.CTkLabel(frame, corner_radius=10, fg_color="purple", font=("Verdana", 15), text="i", text_color="white")
                info_label.grid(column=0, ipadx=3, row=0)
                ToolTip(
                    info_label,
                    argument.information
                )

                self.form_arguments.append(
                    {
                        "key": ctk.CTkSegmentedButton(frame, corner_radius=15, font=("Verdana", 15), values=[argument.name], text_color="white"),
                        "value": ctk.CTkEntry(frame, font=("Verdana", 15)),
                        "type_": ctk.CTkLabel(frame, corner_radius=5, fg_color="#00a35f", font=("Verdana", 15), text=argument.type_.__name__, text_color="white"),
                        "required": ctk.CTkLabel(frame, font=("Verdana", 15), height=0, text="*"),
                    }
                )

                # SEGMENTED BUTTON (KEY)
                self.form_arguments[-1]["key"].set(argument.name)
                self.form_arguments[-1]["key"].grid(column=1, padx=(8, 0), row=0, sticky=tk.NS)

                # TYPE
                self.form_arguments[-1]["type_"].grid(column=2, ipadx=5, padx=(8, 0), row=0, sticky=tk.W)

                # ENTRY
                variable = tk.StringVar(value="")
                self.form_arguments[-1]["value"].configure(textvariable=variable)
                self.form_arguments[-1]["value"].grid(column=3, padx=(8, 0), row=0, sticky=tk.W)

                for argument_name in prepared_arguments:
                    replaced_argument_name = argument_name.replace("_", "-")
                    if replaced_argument_name == argument.name:
                        self.form_arguments[-1]["key"].set(replaced_argument_name)
                        variable.set(prepared_arguments[argument_name])

                type_ = argument.type_
                variable.trace_add("write", lambda *event, validation_object="ARGUMENT", index=row_counter, type_=type_:validate_input(validation_object, index))
                
                # REQUIRED
                self.form_arguments[-1]["required"].grid(column=4, padx=(2, 0), row=0, sticky=tk.NW)

                row_counter += 1
        
        # OPTIONS
        row_counter = 0
        if extracted_options:
            ctk.CTkLabel(self.form_area, font=("Verdana", 15), text="Options").grid(padx=(10, 0), sticky=tk.W)

            options_frame = ctk.CTkFrame(self.form_area); options_frame.columnconfigure(0, weight=1); options_frame.rowconfigure(0, weight=1); options_frame.grid(sticky=tk.NSEW)
            for option in extracted_options:
                frame = ctk.CTkFrame(options_frame, fg_color="transparent"); frame.rowconfigure(0, weight=1)
                frame.grid(column=0, padx=10, pady=(10, 0), row=row_counter, sticky=tk.EW)

                # INFO LABEL
                info_label= ctk.CTkLabel(frame, corner_radius=10, fg_color="purple", font=("Verdana", 15), text="i", text_color="white")
                info_label.grid(column=0, ipadx=3, row=0)
                ToolTip(
                    info_label,
                    option.information
                )

                # ADDING PREREQUISITS
                prerequisits: list[ctk.CTkLabel] = []
                if option.prerequisits:
                    prerequisits_frame = ctk.CTkFrame(frame, fg_color="darkorange")
                    prerequisits_frame.rowconfigure(0, weight=1)
                    prerequisits_frame.grid(column=2, ipady=2, padx=(8, 0), row=0)
                    for i in range(len(option.prerequisits)):
                        option_prerequisits = option.prerequisits[i]
                        label = ctk.CTkLabel(prerequisits_frame, corner_radius=5, fg_color="#ff6200", font=("Verdana", 15), text=", ".join(option_prerequisits), text_color="white")
                        label.grid(column=i, ipadx=10, padx=(3, 0), row=0)
                        prerequisits.append(label)
                    prerequisits[0].grid_forget(); prerequisits[0].grid(column=0, ipadx=10, padx=(2, 0), row=0)
                    prerequisits[-1].grid_forget(); prerequisits[-1].grid(column=i, ipadx=10, padx=(3, 2), row=0)

                type_ = option.type_
                self.form_options.append(
                    {
                        "key": ctk.CTkSegmentedButton(frame, corner_radius=20, font=("Verdana", 15), values=[option.name] + list(option.aliases), command=lambda event: check_prerequisits(), text_color="white"),
                        "value": ctk.CTkEntry(frame, font=("Verdana", 15)),
                        "type_": ctk.CTkLabel(frame, corner_radius=5, fg_color="#00a35f", font=("Verdana", 15), text=option.type_.__name__, text_color="white"),
                        "required": ctk.CTkLabel(frame, font=("Verdana", 15), height=0, text="*" if option.required else " "),
                        "prerequisits": tuple(prerequisits),
                    }
                )

                # SEGMENTED BUTTON
                self.form_options[-1]["key"].set(option.name)
                self.form_options[-1]["key"].grid(column=1, padx=(8, 0), row=0, sticky=tk.NS)

                # TYPE
                self.form_options[-1]["type_"].grid(column=3, ipadx=5, padx=(8, 0), row=0, sticky=tk.NS)

                # ENTRY
                variable = tk.StringVar(value="")
                self.form_options[-1]["value"].configure(textvariable=variable)
                self.form_options[-1]["value"].grid(column=4, padx=(8, 0), row=0, sticky=tk.W)

                for option_name in prepared_options:
                    replaced_option_name = option_name.replace("_", "-")
                    if replaced_option_name == option.name or replaced_option_name in option.aliases:
                        self.form_options[-1]["key"].set(replaced_option_name)
                        variable.set(prepared_options[option_name])


                variable.trace_add("write", lambda *event, validation_object="OPTION", index=row_counter, type_=type_:validate_input(validation_object, index))

                # REQUIRED
                self.form_options[-1]["required"].grid(column=5, padx=(2, 0), row=0, sticky=tk.NW)

                row_counter += 1
            self.bind("<Key>", lambda event: check_prerequisits(), add="+")
            if self.form_area.winfo_ismapped():
                check_prerequisits()
                validate_input()
            else:
                self.after(100, check_prerequisits)
                self.after(100, validate_input)
            

    def disable_auto_select(self, entry:ctk.CTkEntry, cursor_index:int):

        """
        Disable automatic text selection in the entry field.
        
        Args:
            entry (ctk.CTkEntry): The entry widget where text selection should be cleared.
            cursor_index (int): The cursor position to be set after clearing selection.
        """

        def clear_selection():
            entry.select_clear()
            entry.icursor(cursor_index)
        self.after(0, clear_selection)
    
    def select_old_commands(self, event:tk.Event, entry:ctk.CTkEntry):

        """
        Navigate through the command history using the Up and Down arrow keys.
        
        Args:
            event (tk.Event): The event triggered by key press.
            entry (ctk.CTkEntry): The entry widget where the command is being typed.
        """

        if self.clidata["commands_history"] != [] and entry._state == "normal":

            commands_history_length = len(self.clidata["commands_history"]) 

            entry.delete(0, tk.END)

            if event.keysym == "Up":
                if self.current_history_index < commands_history_length - 1:
                    self.current_history_index += 1
            elif event.keysym == "Down":
                if self.current_history_index >= 0:
                    self.current_history_index -= 1
            
            if self.current_history_index != -1:
                entry.insert(0, self.clidata["commands_history"][self.current_history_index] + " ")

    def extract_commands_arguments_and_options(self, commands:list[str]) -> tuple[list["CliCommand"], list["CliArgument"], list["CliOption"]]:

        """
        Extract commands, arguments, and options from a given command list.
        
        Args:
            commands (list[str]): List of command strings.

        Returns:
            tuple: A tuple containing extracted commands, arguments, and options.
        """

        extracted_commands: list["CliCommand"] = [self.clicommands]
        extracted_options: list["CliOption"] = []
        extracted_arguments: list["CliArgument"] = []
        clicommands: list["CliCommand"] = self.clicommands.subcommands
        for command in commands:
            command_exist = False
            for clicommand in clicommands:
                if clicommand.name == command or command in clicommand.aliases:

                    # EXTRACTING COMMANDS
                    extracted_commands.append(clicommand)
                    clicommands = clicommand.subcommands
                    command_exist = True

                    # EXTRACTING ARGUMENTS
                    for argument in clicommand.arguments:
                        extracted_arguments.append(argument)

                    # EXTRACTING OPTIONS
                    for option in clicommand.options:
                        extracted_options.append(option)

                    break
            
            if not command_exist:
                return extracted_commands, extracted_arguments, extracted_options

        return extracted_commands, extracted_arguments, extracted_options

    def filtering_extracted_arguments(self, extracted_arguments:list["CliArgument"], last_command:"CliCommand"):

        """
        Filter extracted arguments based on the allowed arguments of the last command.
        
        Args:
            extracted_arguments (list[CliArgument]): List of extracted arguments.
            last_command (CliCommand): The last executed command.

        Returns:
            list[CliArgument]: Filtered list of allowed arguments.
        """

        aux = []
        if last_command.allowed_arguments != None:
            for extracted_argument in extracted_arguments:
                if extracted_argument.name in last_command.allowed_arguments:
                    aux.append(extracted_argument)

            return aux
        else:
            return extracted_arguments
    
    def filtering_extracted_options(self, extracted_options:list["CliOption"], last_command:"CliCommand"):

        """
        Filter extracted options based on the allowed options of the last command.
        
        Args:
            extracted_options (list[CliOption]): List of extracted options.
            last_command (CliCommand): The last executed command.

        Returns:
            list[CliOption]: Filtered list of allowed options.
        """

        aux = []
        if last_command.allowed_options != None:
            allowed_options_set = set(last_command.allowed_options)
            for extracted_option in extracted_options:
                extracted_option_aliases_set = set(extracted_option.aliases)
                if extracted_option.name in allowed_options_set or extracted_option_aliases_set.intersection(allowed_options_set):
                    aux.append(extracted_option)
            return aux
        else:
            return extracted_options

    def extract_commands_autocomplete(self, commands:list[str]=[""]) -> dict:

        """
        Extract commands for autocompletion.
        
        Args:
            commands (list[str]): List of command strings.

        Returns:
            dict: Extracted commands for autocomplete suggestions.
        """

        extracted_commands: list["CliCommand"] = [self.clicommands]
        clicommands: set["CliCommand"] = self.clicommands.subcommands
        for command in commands:
            command_exist = False
            for clicommand in clicommands:
                if clicommand.name == command:
                    extracted_commands.append(clicommand)
                    clicommands = clicommand.subcommands
                    command_exist = True
                    break
            
            if not command_exist:
                return extracted_commands
        
        return extracted_commands

    def command_entry_has_changed(self, event:tk.Event, entry:ctk.CTkEntry):

        """
        Handle text changes in the command entry, triggering autocompletion or hints.
        
        Args:
            event (tk.Event): The event triggered by text change.
            entry (ctk.CTkEntry): The entry widget where the command is typed.
        """
        
        def get_current(commands_line:str, cursor_index:int) -> str:
            current = ""

            commands_line_lenght = len(commands_line)

            isargument = False
            for i in range(cursor_index, commands_line_lenght):
                if commands_line[i] in {"'", '"'}:
                    isargument = True
            
            if isargument:
                isargument = False
                for i in range(cursor_index - 1, -1, -1):
                    if commands_line[i] in {"'", '"'}:
                        isargument = True
                        current = commands_line[i] + current
                        break
                    current = commands_line[i] + current
            
            if not isargument:
                current = ""
                for i in range(cursor_index - 1, -1, -1):
                    if commands_line[i] == " ":
                        break
                    current = commands_line[i] + current
            
            return current
        
        def get_matching_commands(current:str, extracted_commands:list["CliCommand"]) -> tuple[list[str], list[str]]:

            matching_names: list[str] = []
            hints_names: list[str] = []
            
            for subcommand in extracted_commands[-1].subcommands:
                if current == "":
                    for inner_subcommand in extracted_commands[-1].subcommands:
                        hints_names.append(inner_subcommand.name)
                    break
                elif subcommand.name.startswith(current):
                    matching_names.append(subcommand.name)

            if len(matching_names) > 1:
                hints_names = matching_names
            
            return matching_names, hints_names

        def get_matching_options(current:str, extracted_commands:list["CliCommand"]) -> list[str]:

            matching_names: list[str] = []
            hints_name: list[str] = []

            for subcommand in extracted_commands:
                for option in subcommand.options:
                    option_name = "--" + option.name
                    if option_name.startswith(current) and not current in {"-", "--"}:
                        matching_names.append(option_name)
                    hints_name.append(option_name)
            
            return matching_names, hints_name

        def apply_autocompletion(entry:ctk.CTkEntry, hints_names:list[str], matching_names:list[str], cursor_index:int, end=" ", is_command:bool=True):

            if matching_names == [] and hints_names == []:

                self.bell()

            elif len(matching_names) == 1:

                current_length = len(current)
                matching_name = matching_names[0][current_length:] + (end if is_command else "")
                entry.insert(cursor_index, matching_name)
                cursor_index += len(matching_name)

                if matching_names[0] == current:

                    self.bell()

            else:

                """if matching_names:
                    current_length = len(current)
                    matching_name = min(matching_names, key=len)[current_length:]
                    if all(item.startswith(matching_name) for item in matching_names):
                        entry.insert(cursor_index, matching_name)
                        cursor_index += len(matching_name)

                    self.append_message(commands_line, CliMessage(message=f"{', '.join(matching_names)}", status="hint"))

                else:"""

                self.append_message(commands_line, CliMessage(message=f"{', '.join(hints_names)}", status="hint"))

            self.disable_auto_select(entry=entry, cursor_index=cursor_index)

        if self.text_area.winfo_ismapped():
            cursor_index = entry.index(tk.INSERT) # CURSOR INDEX
            commands_line = entry.get()
            
            current = get_current(commands_line=commands_line, cursor_index=cursor_index)
        
            if commands_line != "":
                if current.startswith("-"):
                    commands, arguments, options = self.split_commands_line(commands_line=commands_line)
                    extracted_commands: list["CliCommand"] = self.extract_commands_autocomplete(commands)
                else:
                    commands, arguments, options = self.split_commands_line(commands_line=commands_line[0:cursor_index])
                    extracted_commands: list["CliCommand"] = self.extract_commands_autocomplete(commands if current == "" else commands[:-1])
            else:
                extracted_commands: list["CliCommand"] = self.extract_commands_autocomplete()

            if current.startswith("-"):
                matching_names, hints_names = get_matching_options(current=current, extracted_commands=extracted_commands)
                apply_autocompletion(entry=entry, hints_names=hints_names, matching_names=matching_names, cursor_index=cursor_index, is_command=False)
            elif current.startswith("'") or current.startswith('"'):
                self.disable_auto_select(entry=entry, cursor_index=cursor_index)
                regex_absolute_path = re.compile(
                    r"""
                    ^(?:
                        (?P<absolute_path>    # GROUP FOR ABSOLUTE PATHS
                            (?:[a-zA-Z]:\\|/) # ABSOLUTE PATH: WINDOWS (C:\) OR UNIX (/)
                            (?:[^/\\]+[\\/])* # INTERMIDIATE FOLDERS WITH SEPARATORS
                        )
                    )?
                    (?P<current> # GROUP FOR CURRENT USER INPUT
                        [^/\\]*  # FOLDER OR FILE NAME
                    )?$          # PATTERN END
                    """,
                    re.VERBOSE
                )

                regex_relative_path = re.compile(
                    r"""
                    ^(?:
                        (?P<relative_path>    # GROUP FOR RELATIVE PATHS
                            (?:\.{1,2}[\\/])* # ./ OR ../ WITH OPTIONAL SEPARATORS, REPEATED
                            (?:[^/\\]+[\\/])* # FOLDER NAMES FOLLOWED BY / OR \ (OPTIONAL)
                        )
                    )?
                    (?P<current> # GROUP FOR CURRENT FOLDER OR FILE
                        [^/\\]*  # FOLDER OR FILE NAME
                    )?$
                    """,
                    re.VERBOSE
                )


                matching_names = []
                hints_names = []
                
                absolute_path = None
                relative_path = None
                if os.path.isabs(current[1:]):
                    match = regex_absolute_path.match(current[1:])
                    if match:
                        absolute_path = match.group("absolute_path")
                        current = match.group("current") or ""
                else:
                    match = regex_relative_path.match(current[1:])
                    if match:
                        relative_path = match.group("relative_path")
                        current = match.group("current") or ""
                try:
                    for dir_or_file in os.listdir(absolute_path or relative_path or os.getcwd()):
                        if dir_or_file.startswith(current):
                            matching_names.append(dir_or_file)
                        
                    if len(matching_names) > 1:
                        hints_names = matching_names
                except:
                    ...
                
                apply_autocompletion(entry=entry, hints_names=hints_names, matching_names=matching_names, cursor_index=cursor_index, end="")
                
            else:
                matching_names, hints_names = get_matching_commands(current=current, extracted_commands=extracted_commands)
                apply_autocompletion(entry=entry, hints_names=hints_names, matching_names=matching_names, cursor_index=cursor_index)
            
