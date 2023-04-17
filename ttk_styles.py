from tkinter.ttk import Style


class CustomStyle:
    def __init__(self, root):
        # init style
        self.style = Style(master=root)
        self.style.theme_create("custom_theme", parent="alt")
        self.style.theme_use("custom_theme")

        # load widget styles
        self.labelframe()
        self.label()
        self.checkbox()
        self.combobox()
        self.button()
        self.separator()

    def labelframe(self):
        self.style.configure(
            "TLabelframe",
            background="white",
        )
        self.style.configure(
            "TLabelframe.Label",
            background="white"
        )

    def label(self):
        self.style.configure(
            "TLabel", 
            background="white", 
        )

    def checkbox(self):
        self.style.configure(
            "TCheckbutton",
            background="white",
            focuscolor="white"
        )
    
    def combobox(self):
        self.style.configure(
            "TCombobox",
            selectbackground="white",
            selectforeground="black",
            fieldbackground="white",
            background="white"
        )
    
    def button(self):
        self.style.configure(
            "TButton",
            background="white"
        )
    
    def separator(self):
        self.style.configure(
            "TSeparator",
        )
