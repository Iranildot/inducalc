import customtkinter as ctk
import tkinter as tk
import loaded_icons as li

class Dashboard(ctk.CTkFrame):
    def __init__(self, master):

        super().__init__(master=master)

        # SETTING UP THE MAIN DASHBOARD FRAME
        self.configure(self, fg_color=("#EEEEEE", "#555555"), corner_radius=0)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # DASHBOARD FRAME
        self.dashboard = ctk.CTkFrame(self, corner_radius=0)
        self.dashboard.columnconfigure(0, weight=1)
        self.dashboard.rowconfigure(1, weight=1)
        self.dashboard.grid(padx=40, pady=40, sticky=tk.NSEW)

        # DASHBOARD HEADER
        self.dashboard_header_frame = ctk.CTkFrame(self.dashboard, fg_color=("#AAAAAA", "#222222"), corner_radius=0)
        self.dashboard_header_frame.grid(sticky=tk.NSEW)
        self.dashboard_header = ctk.CTkLabel(
            self.dashboard_header_frame,
            anchor=tk.W,
            compound="left",
            corner_radius=10,
            fg_color=("#333333", "#DDDDDD"),
            font=("Times", 18, "bold"),
            text="  Tech files",
            text_color=("#DDDDDD", "#333333"),
        )
        self.dashboard_header.grid(padx=(8, 0), pady=8, ipady=10, sticky=tk.EW)

        # DASHBOARD PANEL
        self.dashboard_panel = ctk.CTkScrollableFrame(self.dashboard, corner_radius=0)
        self.dashboard_panel.grid(sticky=tk.NSEW)

        # DASHBOARD BUTTONS
        self.dashboard_buttons_frame = ctk.CTkFrame(self.dashboard, corner_radius=0, fg_color=("#AAAAAA", "#222222"), height=35)
        self.dashboard_buttons_frame.columnconfigure(0, weight=1)
        self.dashboard_buttons_frame.rowconfigure(0, weight=1)
        self.dashboard_buttons_frame.grid(ipady=10, sticky=tk.EW)
    
    def create_panel(self):
        self.destroy_widgets(self.dashboard_panel)
        self.destroy_widgets(self.dashboard_buttons_frame)

        self.create_add_button = ctk.CTkButton(
            self.dashboard_buttons_frame,
            fg_color=("#333333", "#DDDDDD"),
            height=35,
            hover_color=("#777777", "#999999"),
            image=li.add_icon,
            text="",
            width=35
        )
        self.create_add_button.grid(padx=(10, 0), sticky=tk.W)
    
    def tech_files_panel(self):
        self.destroy_widgets(self.dashboard_panel)
        self.destroy_widgets(self.dashboard_buttons_frame)

        self.tech_files_add_button = ctk.CTkButton(
            self.dashboard_buttons_frame,
            fg_color=("#333333", "#DDDDDD"),
            height=35,
            hover_color=("#777777", "#999999"),
            image=li.add_icon,
            text="",
            width=35
        )
        self.tech_files_add_button.grid(padx=(10, 0), sticky=tk.W)
        
    def destroy_widgets(self, master:tk.Misc):
        elements = list(master.children.values())[1:]
        if elements:
            for element in elements:
                element.destroy()

class NavigationDrawer(ctk.CTkFrame):
    def __init__(self, master, dashboard:Dashboard):
        super().__init__(master=master)

        # DEFINING VARIABLES
        self.windows_is_visible: bool = False
        self.current_navigation: ctk.CTkButton = None
        self.dashboard: Dashboard = dashboard
        self.theme_mode: str = None

        # MAIN FRAME OF NAVIGATION DRAWER
        self.configure(corner_radius=0, fg_color=("#CCCCCC", "#333333"))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # THE HEADER TEXT
        self.header_text = ctk.CTkLabel(
            self,
            fg_color=("#333333", "#DDDDDD"),
            font=("Times", 17, "bold"),
            text="  InduCalc",
            text_color=("#DDDDDD", "#333333"),

            compound="left",
            corner_radius=10
        )
        self.header_text.grid(ipady=15, padx=5, pady=(5, 0), sticky=tk.EW)

        # DIVIDER
        ctk.CTkFrame(self, fg_color=("#333333", "#DDDDDD"), height=2).grid(column=0, pady=(5, 20), row=1, sticky=tk.EW)

        # NAVIGATION SECTION
        self.navigation_section = ctk.CTkFrame(self, fg_color="transparent")
        self.navigation_section.columnconfigure(0, weight=1)
        self.navigation_section.grid(column=0, row=2, sticky=tk.NSEW)

        self.navigation_buttons = [
            ctk.CTkButton( # INDUCTORS BUTTON
                self.navigation_section, 
                anchor=tk.W,
                fg_color="transparent", 
                font=("Times", 16, "bold"), 
                height=40, 
                hover_color=("#BBBBBB", "#555555"),
                image=li.create_icon, 
                text="Inductors", 
                text_color=("#333333", "#DDDDDD")
            ),
            ctk.CTkButton( # TECH FILES BUTTON
                self.navigation_section,
                anchor=tk.W,
                fg_color="transparent",
                font=("Times", 16, "bold"),
                height=40,
                hover_color=("#BBBBBB", "#555555"),
                image=li.tech_file_icon,
                text="Techfiles",
                text_color=("#333333", "#DDDDDD")
            )
        ]

        self.navigation_buttons[0].configure(command=lambda: self.dashboard_selection(self.navigation_buttons[0]))
        self.navigation_buttons[1].configure(command=lambda: self.dashboard_selection(self.navigation_buttons[1]))

        for button in self.navigation_buttons:
            button.grid(sticky=tk.EW)

        # DIVIDER
        ctk.CTkFrame(self, fg_color=("#333333", "#DDDDDD"), height=2).grid(column=0,row=3, sticky=tk.EW)

        self.theme_chooser_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.theme_chooser_frame.rowconfigure(0, weight=1)
        self.theme_chooser_frame.grid(column=0, pady=10, row=4)

        self.theme_chooser_label = ctk.CTkLabel(self.theme_chooser_frame, font=("Times", 14, "bold"), text=ctk.get_appearance_mode().upper())
        self.theme_chooser_label.grid(column=1)

        self.theme_chooser_button = ctk.CTkButton(
            self.theme_chooser_frame,
            command=self.change_theme,
            fg_color=("#333333", "#DDDDDD"),
            height=35,
            hover_color=("#777777", "#999999"),
            image=li.theme_icon,
            text="",
            width=35
        )
        self.theme_chooser_button.grid(column=0, padx=(0, 5), row=0)

        self.set_theme()

        master.bind("<Visibility>", lambda event: self.handle_visibility(self.navigation_buttons[1]))

    def set_theme(self, theme="AUTO"):
        match theme:    
            case "AUTO":
                self.theme_mode = "AUTO"
                ctk.set_appearance_mode("SYSTEM")
                self.theme_chooser_button.configure(image=li.theme_icon_system)
            case "LIGHT":
                self.theme_mode = "LIGHT"
                ctk.set_appearance_mode("LIGHT")
                self.theme_chooser_button.configure(image=li.theme_icon)
            case "DARK":
                self.theme_mode = "DARK"
                ctk.set_appearance_mode("DARK")
                self.theme_chooser_button.configure(image=li.theme_icon)
        self.theme_chooser_label.configure(text=theme)
    
    def change_theme(self):
        match self.theme_mode:    
            case "AUTO":
                self.theme_mode = "LIGHT"
                ctk.set_appearance_mode("LIGHT")
                self.theme_chooser_button.configure(image=li.theme_icon)
            case "LIGHT":
                self.theme_mode = "DARK"
                ctk.set_appearance_mode("DARK")
                self.theme_chooser_button.configure(image=li.theme_icon)
            case "DARK":
                self.theme_mode = "AUTO"
                ctk.set_appearance_mode("SYSTEM")
                self.theme_chooser_button.configure(image=li.theme_icon_system)
        self.theme_chooser_label.configure(text=self.theme_mode)

    def dashboard_selection(self, button:ctk.CTkButton):
        if self.current_navigation:

            icon = ctk.CTkImage(
                light_image=self.current_navigation._image._dark_image,
                dark_image=self.current_navigation._image._light_image,
                size=(25, 25)
            )

            self.current_navigation.configure(fg_color=("#CCCCCC", "#333333"), hover=True, image=icon, text_color=("#333333", "#DDDDDD"))

        icon = ctk.CTkImage(
            light_image=button._image._dark_image,
            dark_image=button._image._light_image,
            size=(25, 25)
        )

        button.configure(fg_color=("#333333", "#DDDDDD"), hover=False, image=icon, text_color=("#DDDDDD", "#333333"))

        self.current_navigation = button

        match button._text:
            case "Inductors":
                self.dashboard.dashboard_header.configure(image=button._image, text="  Inductors")
                self.dashboard.create_panel()
            case "Techfiles":
                self.dashboard.dashboard_header.configure(image=button._image, text="  Techfiles")
                self.dashboard.tech_files_panel()
        
    def handle_visibility(self, button:ctk.CTkButton):
        if not self.windows_is_visible:
            self.windows_is_visible = True
            button.invoke()


class App(ctk.CTk):
    def __init__(self, fg_color = None, **kwargs):
        super().__init__(fg_color, **kwargs)

        self.title("InduCalc")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.dashboard = Dashboard(self)
        self.dashboard.grid(column=1, row=0, sticky=tk.NSEW)

        self.navigation_drawer = NavigationDrawer(self, self.dashboard)
        self.navigation_drawer.grid(column=0, row=0, sticky=tk.NSEW)

if __name__ == "__main__":
    app = App()
    app.mainloop()
