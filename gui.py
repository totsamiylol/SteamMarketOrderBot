from customtkinter import *
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox

import database
import user_data
from item_class import Item, SkinItem
from script import main, save_old_collections
import threading

class GUI:
    """ GUI Class """
    number_of_items = {
        "Case Skins": {"Mil-Spec Grade": 7, "Restricted": 5, "Classified": 3, "Covert": 2},
        "Op Skins": {"Consumer Grade": 15, "Industrial Grade": 12, "Mil-Spec Grade": 12, "Restricted": 9, "Classified": 6, "Covert": 3},
        "Agents": {"Mil-Spec Grade": 5, "Restricted": 5, "Classified": 5, "Covert": 5},
        "Stickers": {"Mil-Spec Grade": 8, "Restricted": 4, "Classified": 2, "Covert": 0},
        "Patches": {"Mil-Spec Grade": 6, "Restricted": 4, "Classified": 3, "Covert": 0}
    }

    # To do:
    # - Calibration run  +++ (Needs testing)
    # - Instructions
    # - Update listener

    #Later
    # - Multiple account support
    # - "Add" .get() requests


    # - Add item queue???
    # - Built-in proxies???
    # - Multiple Seleniums???

    # - Combine 2 programs into 1

    # - Add souvenir Anubis collection to program

    headers = ["Account ID", "Type", "Rarity", "Price", "Quantity", "Total", "Wear", "StatTrak", "Estimated no. of items"]
    colors = ["#b0c3e9", "#5e98d9", "#4b69ff", "#8847ff", "#d32ce6", "#eb4b4b"]
    rarities = ["Consumer Grade", "Industrial Grade", "Mil-Spec Grade", "Restricted", "Classified", "Covert"]
    types = ["Op Skins", "Case Skins", "Agents", "Stickers", "Patches"]
    wears = ["Factory New", "Minimal Wear", "Field-Tested", "Well-Worn", "Battle-Scarred"]
    stattrak = ["No", "Yes"]

    accounts = user_data.get_data()["accounts"]
    proxies = user_data.get_data()["proxy"]

    def __init__(self):
        self.root = CTk()
        self.root.title("GUI")


        self.root.minsize(1200, 800)
        self.root.config(bg="#FFFFFF")

        self.create_style()

        self.variables()

        self.create_notebook()

        self.root.bind("<Return>", lambda *args: self.add_record())

        self.update_displayed_records()

        self.root.mainloop()

    def variables(self):
        self.dark_mode_var = BooleanVar(value=False)
        self.driver_path_var = StringVar(value=user_data.get_data()["driver_path"])
        self.sort_by_var = StringVar()
        self.total_value_var = StringVar(value="0")
        self.displayable_columns_vars = [IntVar(value=1) for _ in range(len(self.headers))]
        self.displayable_rarities_vars = [IntVar(value=1) for _ in range(6)]
        self.displayable_types_vars = [IntVar(value=1) for _ in range(5)]
        self.displayable_wear_vars = [IntVar(value=1) for _ in range(5)]
        self.displayable_stattrak_vars = [IntVar(value=1) for _ in range(2)]

        self.adding_account_var = StringVar()
        self.adding_type_var = StringVar()
        self.adding_rarity_var = StringVar()
        self.adding_price_var = StringVar()
        self.adding_quantity_var = StringVar()
        self.adding_wear_var = StringVar()
        self.adding_stattrak_var = StringVar()

    def create_style(self):
        self.style = Style()
        self.style.theme_create("LIGHT", parent="alt", settings=
        {
            "TNotebook": {
                "configure": {"background": "#cfcfcf"}},
            "TNotebook.Tab":
                {
                    "configure": {"background": "#cfcfcf"},
                    "map": {"background": [("selected", "#dbdbdb"), ('!active', "#cfcfcf"), ('active', "#cfcfcf")],
                            "expand": [("selected", [1, 1, 1, 0])]}
                },
            "Treeview":
                {
                    "configure":
                        {
                            "background": "white",
                            "foreground": "black",
                            "fieldbackground": "white"
                        },
                    "map":
                        {
                            "background": [("selected", "#0483FF")],
                            "foreground": [("selected", "white")]
                        },
                },
            "Treeview.Heading":
                {
                    "configure":
                        {
                            "background": "white",
                            "foreground": "black",
                            "fieldbackground": "white"
                        }
                }
        })
        self.style.theme_create("DARK", parent="alt", settings=
        {
            "TNotebook": {
                "configure": {"background": "#333333"}},
            "TNotebook.Tab":
                {
                    "configure": {"background": "#333333", "foreground": "white"},
                    "map": {"background": [("selected", "#333333"), ('!active', "#2B2B2B"), ('active', "#2B2B2B")],
                            "expand": [("selected", [1, 1, 1, 0])]}
                },
            "Treeview":
                {
                    "configure":
                        {
                            "background": "#3e3e3e",
                            "foreground": "#dcdcdc",
                            "fieldbackground": "#3e3e3e"
                        },
                    "map":
                        {
                            "background": [("selected", "#0061ac")],
                            "foreground": [("selected", "#dcdcdc")]
                        },
                },
            "Treeview.Heading":
                {
                    "configure":
                        {
                            "background": "#43586b",
                            "foreground": "white",
                        }
                }
        })

        self.style.layout("Tab",
                          [('Notebook.tab', {'sticky': 'nswe', 'children':
                              [('Notebook.padding', {'side': 'top', 'sticky': 'nswe', 'children':
                                  [('Notebook.label', {'side': 'top', 'sticky': ''})],
                                                     })], })])

    def switch_theme(self):
        if self.dark_mode_var.get():
            self.style.theme_use("DARK")
            set_appearance_mode("dark")
        else:
            self.style.theme_use("LIGHT")
            set_appearance_mode("light")

    def ask_path(self):
        path = filedialog.askopenfilename(title="Select chromedriver path", filetypes=(("ChromeDriver", "*.exe"),))
        if not path:
            return
        self.driver_path_var.set(path)
        user_data.save_data("driver_path", self.driver_path_var.get())
        self.driver_frame_text.configure(text=self.driver_path_var.get()[:20] + "..." if len(self.driver_path_var.get()) > 20 else self.driver_path_var.get())

    def save_accounts(self):
        accounts = self.account_frame_text.get("1.0", END).split("\n")
        accounts = list(filter(None, accounts))
        user_data.save_data("accounts", accounts)

    def save_proxies(self):
        proxy = self.proxy_frame_text.get("1.0", END).split("\n")
        proxy = list(filter(None, proxy))
        proxy.insert(0, "")
        user_data.save_data("proxy", proxy)

    def change_fields(self):
        type_ = self.adding_type_var.get()
        if type_ == "Case Skins":
            self.adding_wear_combobox.configure(state="readonly")
            self.adding_stattrak_combobox.configure(state="readonly")
            self.adding_rarity_combobox.configure(values=self.rarities[2:])
        elif type_ == "Op Skins":
            self.adding_wear_combobox.configure(state="readonly")
            self.adding_stattrak_combobox.configure(state=DISABLED)
            self.adding_rarity_combobox.configure(values=self.rarities)
        else:
            self.adding_wear_combobox.configure(state=DISABLED)
            self.adding_stattrak_combobox.configure(state=DISABLED)
            self.adding_rarity_combobox.configure(values=self.rarities[2:])

    def add_record(self):
        account_id = self.adding_account_var.get()
        type_ = self.adding_type_var.get()
        rarity = self.adding_rarity_var.get()
        price = self.adding_price_var.get()
        quantity = self.adding_quantity_var.get()
        wear = self.adding_wear_var.get()
        stat_trak = self.adding_stattrak_var.get()
        try:
            price = float(price)
            quantity = int(quantity)
        except ValueError:
            messagebox.showerror("Error", "Price and quantity must be numbers!")
            return
        if quantity < 1:
            messagebox.showerror("Error", "Quantity must be greater than 0!")
            return
        if price < 0.03:
            messagebox.showerror("Error", "Price must be greater than 0.03!")
            return
        if not account_id:
            messagebox.showerror("Error", "Account must be selected!")
            return
        if not type_:
            messagebox.showerror("Error", "Type must be selected!")
            return
        if not rarity:
            messagebox.showerror("Error", "Rarity must be selected!")
            return
        if type_ in ["Op Skins", "Case Skins"]:
            if not wear:
                messagebox.showerror("Error", "Wear must be selected!")
                return
            if not stat_trak and type_ == "Case Skins":
                messagebox.showerror("Error", "StatTrak must be selected!")
                return
        if not database.add_data(account_id, type_, rarity, price=round(price, 2), quantity=quantity, wear=wear, stat_trak=stat_trak):
            response = messagebox.askyesno("Error", "This record already exists! Do you want to update it?")
            if response:
                database.delete_data(type_=type_, rarity=rarity, account_id=account_id, wear=wear, stat_trak=stat_trak)
                database.add_data(account_id, type_, rarity, price=round(price, 2), quantity=quantity, wear=wear, stat_trak=stat_trak)
        self.update_displayed_records()

    def delete_record(self):
        for selected_item in self.treeview.selection():
            data = self.treeview.item(selected_item)["values"]
            database.delete_data(type_=data[1], rarity=data[2], account_id=data[0], wear=data[6], stat_trak=data[7])
            self.treeview.delete(selected_item)

    def delete_all_records(self):
        response = messagebox.askyesno("Delete all", "Are you sure you want to delete all records?")
        if response:
            for item in self.treeview.get_children():
                database.delete_all_data()
                self.treeview.delete(item)

    def copy_to_clipboard(self, event):
        item = self.treeview.identify_row(event.y)
        if item:
            column = self.treeview.identify_column(event.x)
            if column:
                value = self.treeview.item(item, "values")[int(column[1:]) - 1]
                self.root.clipboard_clear()
                self.root.clipboard_append(value)

    def create_data_frame(self):  # ---------------------------- Data Frame
        self.data_frame = CTkFrame(self.root)
        self.data_frame.pack(fill=Y)
        self.data_frame.columnconfigure(1, weight=1)
        self.data_frame.rowconfigure(1, weight=1)

        self.create_left_frame()
        self.create_filter_frame()
        self.create_treeview_frame()
        self.create_total_value_frame()
        self.create_adding_frame()

    def create_left_frame(self):
        self.left_side = CTkFrame(self.data_frame)
        self.left_side.grid(row=0, column=0, sticky=NSEW, rowspan=4)

        self.account_frame = CTkFrame(self.left_side)
        self.proxy_frame = CTkFrame(self.left_side)
        self.driver_frame = CTkFrame(self.left_side)
        self.dark_mode_frame = CTkFrame(self.left_side)
        self.account_frame.grid(row=0, column=0, sticky=NSEW, padx=10, pady=10)
        self.proxy_frame.grid(row=1, column=0, sticky=NSEW, padx=10, pady=10)
        self.driver_frame.grid(row=2, column=0, sticky=NSEW, padx=10, pady=10)

        CTkLabel(self.account_frame, text="Dolphin accounts").pack()
        CTkLabel(self.proxy_frame, text="Proxies").pack()
        CTkLabel(self.driver_frame, text="Drivers").pack()

        self.account_frame_text = CTkTextbox(self.account_frame, height=200)
        self.account_frame_text.insert(END, "\n".join(user_data.get_data()["accounts"]))
        self.accounnt_frame_button = CTkButton(self.account_frame, text="Save", command=self.save_accounts)
        self.proxy_frame_text = CTkTextbox(self.proxy_frame, height=300)
        self.proxy_frame_text.insert(END, "\n".join(user_data.get_data()["proxy"]))
        self.proxy_frame_button = CTkButton(self.proxy_frame, text="Save", command=self.save_proxies)
        self.driver_frame_text = CTkLabel(self.driver_frame, text=self.driver_path_var.get()[:20] + "..." if len(self.driver_path_var.get()) > 20 else self.driver_path_var.get())
        self.save_path_button = CTkButton(self.driver_frame, text="Change Path", command=self.ask_path)
        self.dark_mode_frame_text = CTkSwitch(self.left_side, text="Dark Mode", variable=self.dark_mode_var, command=self.switch_theme)

        self.account_frame_text.pack()
        self.accounnt_frame_button.pack(pady=10)
        self.proxy_frame_text.pack()
        self.proxy_frame_button.pack(pady=10)
        self.driver_frame_text.pack()
        self.save_path_button.pack(pady=10)
        self.dark_mode_frame_text.grid(row=3, column=0, padx=10, pady=10)

    def create_treeview_frame(self):
        self.treeview_side = CTkFrame(self.data_frame)
        self.treeview_side.grid(row=1, column=1, sticky=NSEW)
        self.treeview = Treeview(self.treeview_side, columns=self.headers, show="headings")
        for col_index, col_name in enumerate(self.headers):
            self.treeview.heading(col_index, text=col_name)
            self.treeview.column(col_index, width=100, stretch=NO)
        self.treeview.pack(fill=BOTH, expand=True)

        self.treeview.bind("<Double-1>", self.copy_to_clipboard)
        self.treeview.bind("<Delete>", lambda *args: self.delete_record())

    def sort_table(self):
        # I put this s**t here because of f*****g tkinter kludge that converts float to str
        data = self.treeview.get_children()
        data = [[self.treeview.item(child)["values"][0],
                 self.treeview.item(child)["values"][1],
                 self.treeview.item(child)["values"][2],
                 float(self.treeview.item(child)["values"][3]),
                 self.treeview.item(child)["values"][4],
                 float(self.treeview.item(child)["values"][5]),
                 self.treeview.item(child)["values"][6],
                 self.treeview.item(child)["values"][7],
                 self.treeview.item(child)["values"][8]]
                for child in data]
        sorting_by = self.sort_by_var.get()
        try:
            data.sort(key=lambda x: x[self.headers.index(sorting_by)])
        except ValueError:
            pass
        self.treeview.delete(*self.treeview.get_children())
        for row in data:
            self.treeview.insert("", "end", values=row)

    def update_columns(self):
        for i in range(len(self.displayable_columns_vars)):
            if self.displayable_columns_vars[i].get():
                self.treeview.column(self.headers[i], width=100, stretch=NO)
            else:
                self.treeview.column(self.headers[i], width=0, stretch=NO)

    def update_displayed_records(self):
        data = database.get_all_data()
        self.treeview.delete(*self.treeview.get_children())
        total_price = 0
        for row in data:
            id_, type_, rarity, wear, stat_track, price, quantity = row
            num_of_positions = self.number_of_items[type_][rarity]
            if not self.rarities.index(rarity) in [i for i, v in enumerate(self.displayable_rarities_vars) if v.get()]:
                continue
            if not self.types.index(type_) in [i for i, v in enumerate(self.displayable_types_vars) if v.get()]:
                continue
            if wear is not None:
                if not self.wears.index(wear) in [i for i, v in enumerate(self.displayable_wear_vars) if v.get()]:
                    continue
            if stat_track is not None:
                if not self.stattrak.index(stat_track) in [i for i, v in enumerate(self.displayable_stattrak_vars) if v.get()]:
                    continue
            total_price += price * quantity * num_of_positions
            self.treeview.insert("", "end", values=(id_, type_, rarity,  price, quantity, round(price*quantity, 2), wear, stat_track, num_of_positions))
        self.sort_table()
        self.total_value_var.set(str(round(total_price, 2)))

    def create_filter_frame(self):
        self.filter_side = CTkFrame(self.data_frame)
        self.filter_side.grid(row=0, column=1, sticky=NSEW)


        # Display columns
        self.display_columns_frame = CTkFrame(self.filter_side)
        self.display_columns_frame.pack(side=LEFT, padx=5, pady=5, anchor="n")
        CTkLabel(self.display_columns_frame, text="Display columns:").grid(row=0, column=0, padx=10)
        CTkCheckBox(self.display_columns_frame, variable=self.displayable_columns_vars[0], text=self.headers[0]).grid(row=1, column=0, sticky="w", pady=2, padx=5)
        CTkCheckBox(self.display_columns_frame, variable=self.displayable_columns_vars[1], text=self.headers[1]).grid(row=1, column=1, sticky="w", pady=2, padx=5)
        CTkCheckBox(self.display_columns_frame, variable=self.displayable_columns_vars[2], text=self.headers[2]).grid(row=2, column=0, sticky="w", pady=2, padx=5)
        CTkCheckBox(self.display_columns_frame, variable=self.displayable_columns_vars[3], text=self.headers[3]).grid(row=2, column=1, sticky="w", pady=2, padx=5)
        CTkCheckBox(self.display_columns_frame, variable=self.displayable_columns_vars[4], text=self.headers[4]).grid(row=3, column=0, sticky="w", pady=2, padx=5)
        CTkCheckBox(self.display_columns_frame, variable=self.displayable_columns_vars[5], text=self.headers[5]).grid(row=3, column=1, sticky="w", pady=2, padx=5)
        CTkCheckBox(self.display_columns_frame, variable=self.displayable_columns_vars[6], text=self.headers[6]).grid(row=4, column=0, sticky="w", pady=2, padx=5)
        CTkCheckBox(self.display_columns_frame, variable=self.displayable_columns_vars[7], text=self.headers[7]).grid(row=4, column=1, sticky="w", pady=2, padx=5)
        CTkCheckBox(self.display_columns_frame, variable=self.displayable_columns_vars[8], text=self.headers[8]).grid(row=5, column=0, columnspan=2, sticky="w", pady=2, padx=5)

        self.displayable_columns_vars[0].trace("w", lambda *args: self.update_columns())
        self.displayable_columns_vars[1].trace("w", lambda *args: self.update_columns())
        self.displayable_columns_vars[2].trace("w", lambda *args: self.update_columns())
        self.displayable_columns_vars[3].trace("w", lambda *args: self.update_columns())
        self.displayable_columns_vars[4].trace("w", lambda *args: self.update_columns())
        self.displayable_columns_vars[5].trace("w", lambda *args: self.update_columns())
        self.displayable_columns_vars[6].trace("w", lambda *args: self.update_columns())
        self.displayable_columns_vars[7].trace("w", lambda *args: self.update_columns())
        self.displayable_columns_vars[8].trace("w", lambda *args: self.update_columns())

        # Display rarities
        self.display_rarities_frame = CTkFrame(self.filter_side)
        self.display_rarities_frame.pack(side=LEFT, padx=5, pady=5, anchor="n")
        CTkLabel(self.display_rarities_frame, text="Rarities:").grid(row=0, column=0, padx=10)
        CTkCheckBox(self.display_rarities_frame, variable=self.displayable_rarities_vars[0], text=self.rarities[0], text_color=self.colors[0]).grid(row=1, column=0, sticky="w", pady=2, padx=5)
        CTkCheckBox(self.display_rarities_frame, variable=self.displayable_rarities_vars[1], text=self.rarities[1], text_color=self.colors[1]).grid(row=2, column=0, sticky="w", pady=2, padx=5)
        CTkCheckBox(self.display_rarities_frame, variable=self.displayable_rarities_vars[2], text=self.rarities[2], text_color=self.colors[2]).grid(row=3, column=0, sticky="w", pady=2, padx=5)
        CTkCheckBox(self.display_rarities_frame, variable=self.displayable_rarities_vars[3], text=self.rarities[3], text_color=self.colors[3]).grid(row=4, column=0, sticky="w", pady=2, padx=5)
        CTkCheckBox(self.display_rarities_frame, variable=self.displayable_rarities_vars[4], text=self.rarities[4], text_color=self.colors[4]).grid(row=5, column=0, sticky="w", pady=2, padx=5)
        CTkCheckBox(self.display_rarities_frame, variable=self.displayable_rarities_vars[5], text=self.rarities[5], text_color=self.colors[5]).grid(row=6, column=0, sticky="w", pady=2, padx=5)

        self.displayable_rarities_vars[0].trace("w", lambda *args: self.update_displayed_records())
        self.displayable_rarities_vars[1].trace("w", lambda *args: self.update_displayed_records())
        self.displayable_rarities_vars[2].trace("w", lambda *args: self.update_displayed_records())
        self.displayable_rarities_vars[3].trace("w", lambda *args: self.update_displayed_records())
        self.displayable_rarities_vars[4].trace("w", lambda *args: self.update_displayed_records())
        self.displayable_rarities_vars[5].trace("w", lambda *args: self.update_displayed_records())

        # Display types
        self.display_types_frame = CTkFrame(self.filter_side)
        self.display_types_frame.pack(side=LEFT, padx=5, pady=5, anchor="n")
        CTkLabel(self.display_types_frame, text="Types:").grid(row=0, column=0, padx=10, columnspan=2)
        CTkCheckBox(self.display_types_frame, variable=self.displayable_types_vars[0], text=self.types[0]).grid(row=1, column=0, sticky="w", pady=2, padx=5)
        CTkCheckBox(self.display_types_frame, variable=self.displayable_types_vars[1], text=self.types[1]).grid(row=2, column=0, sticky="w", pady=2, padx=5)
        CTkCheckBox(self.display_types_frame, variable=self.displayable_types_vars[2], text=self.types[2]).grid(row=3, column=0, sticky="w", pady=2, padx=5)
        CTkCheckBox(self.display_types_frame, variable=self.displayable_types_vars[3], text=self.types[3]).grid(row=4, column=0, sticky="w", pady=2, padx=5)
        CTkCheckBox(self.display_types_frame, variable=self.displayable_types_vars[4], text=self.types[4]).grid(row=5, column=0, sticky="w", pady=2, padx=5)

        self.displayable_types_vars[0].trace("w", lambda *args: self.update_displayed_records())
        self.displayable_types_vars[1].trace("w", lambda *args: self.update_displayed_records())
        self.displayable_types_vars[2].trace("w", lambda *args: self.update_displayed_records())
        self.displayable_types_vars[3].trace("w", lambda *args: self.update_displayed_records())
        self.displayable_types_vars[4].trace("w", lambda *args: self.update_displayed_records())

        # Display wear
        self.display_wear_frame = CTkFrame(self.filter_side)
        self.display_wear_frame.pack(side=LEFT, padx=5, pady=5, anchor="n")
        CTkLabel(self.display_wear_frame, text="Wear:").grid(row=0, column=0, padx=5, columnspan=2)
        CTkCheckBox(self.display_wear_frame, variable=self.displayable_wear_vars[0], text=self.wears[0]).grid(row=1, column=0, sticky="w", pady=2, padx=5)
        CTkCheckBox(self.display_wear_frame, variable=self.displayable_wear_vars[1], text=self.wears[1]).grid(row=2, column=0, sticky="w", pady=2, padx=5)
        CTkCheckBox(self.display_wear_frame, variable=self.displayable_wear_vars[2], text=self.wears[2]).grid(row=3, column=0, sticky="w", pady=2, padx=5)
        CTkCheckBox(self.display_wear_frame, variable=self.displayable_wear_vars[3], text=self.wears[3]).grid(row=4, column=0, sticky="w", pady=2, padx=5)
        CTkCheckBox(self.display_wear_frame, variable=self.displayable_wear_vars[4], text=self.wears[4]).grid(row=5, column=0, sticky="w", pady=2, padx=5)

        self.displayable_wear_vars[0].trace("w", lambda *args: self.update_displayed_records())
        self.displayable_wear_vars[1].trace("w", lambda *args: self.update_displayed_records())
        self.displayable_wear_vars[2].trace("w", lambda *args: self.update_displayed_records())
        self.displayable_wear_vars[3].trace("w", lambda *args: self.update_displayed_records())
        self.displayable_wear_vars[4].trace("w", lambda *args: self.update_displayed_records())

        # Display stattrak
        self.display_stattrak_frame = CTkFrame(self.filter_side)
        self.display_stattrak_frame.pack(side=LEFT, padx=5, pady=5, anchor="n")
        CTkLabel(self.display_stattrak_frame, text="StatTrak:").grid(row=0, column=0, padx=10, columnspan=2)
        CTkCheckBox(self.display_stattrak_frame, variable=self.displayable_stattrak_vars[0], text=self.stattrak[0]).grid(row=1, column=0, sticky="w", pady=2, padx=5)
        CTkCheckBox(self.display_stattrak_frame, variable=self.displayable_stattrak_vars[1], text=self.stattrak[1]).grid(row=2, column=0, sticky="w", pady=2, padx=5)

        self.displayable_stattrak_vars[0].trace("w", lambda *args: self.update_displayed_records())
        self.displayable_stattrak_vars[1].trace("w", lambda *args: self.update_displayed_records())

        # Sort by
        self.sort_by_frame = CTkFrame(self.filter_side)
        self.sort_by_frame.pack(side=LEFT, padx=5, pady=5, anchor="n")
        CTkLabel(self.sort_by_frame, text="Sort by:").grid(row=0, column=0, padx=5)
        self.sort_by_combobox = CTkComboBox(self.sort_by_frame, values=self.headers, variable=self.sort_by_var, state="readonly")
        self.sort_by_combobox.grid(row=1, column=0, padx=5, pady=5)
        self.sort_by_var.trace("w", lambda *args: self.sort_table())

    def create_adding_frame(self):
        self.adding_frame = CTkFrame(self.data_frame)
        self.adding_frame.grid(row=3, column=1, sticky=NSEW)
        CTkLabel(self.adding_frame, text="Account ID").grid(row=0, column=0, sticky="we")
        CTkLabel(self.adding_frame, text="Type").grid(row=0, column=1, sticky="we")
        CTkLabel(self.adding_frame, text="Rarity").grid(row=0, column=2, sticky="we")
        CTkLabel(self.adding_frame, text="Price").grid(row=0, column=3, sticky="we")
        CTkLabel(self.adding_frame, text="Quantity").grid(row=0, column=4, sticky="we")
        CTkLabel(self.adding_frame, text="Wear").grid(row=0, column=5, sticky="we")
        CTkLabel(self.adding_frame, text="StatTrak").grid(row=0, column=6, sticky="we")

        self.adding_account_combobox = CTkComboBox(self.adding_frame, values=self.accounts, variable=self.adding_account_var, width=100, state="readonly")
        self.adding_account_combobox.grid(row=1, column=0, padx=10, pady=10)
        self.adding_type_combobox = CTkComboBox(self.adding_frame, values=self.types, variable=self.adding_type_var, width=120, state="readonly")
        self.adding_type_combobox.grid(row=1, column=1, padx=10, pady=10)
        self.adding_rarity_combobox = CTkComboBox(self.adding_frame, values=self.rarities, variable=self.adding_rarity_var, state="readonly")
        self.adding_rarity_combobox.grid(row=1, column=2, padx=10, pady=10)
        CTkEntry(self.adding_frame, textvariable=self.adding_price_var, width=80).grid(row=1, column=3, padx=10, pady=10)
        CTkEntry(self.adding_frame, textvariable=self.adding_quantity_var, width=80).grid(row=1, column=4, padx=10, pady=10)
        self.adding_wear_combobox = CTkComboBox(self.adding_frame, values=self.wears, variable=self.adding_wear_var, width=120, state="readonly")
        self.adding_wear_combobox.grid(row=1, column=5, padx=10, pady=10)
        self.adding_stattrak_combobox = CTkComboBox(self.adding_frame, values=self.stattrak, variable=self.adding_stattrak_var, width=80, state="readonly")
        self.adding_stattrak_combobox.grid(row=1, column=6, padx=10, pady=10)

        self.adding_type_var.trace("w", lambda *args: self.change_fields())

        CTkButton(self.adding_frame, text="Delete all", command=self.delete_all_records).grid(row=2, column=0, sticky="we", padx=10, pady=10, columnspan=1)
        CTkButton(self.adding_frame, text="Delete", command=self.delete_record).grid(row=2, column=1, sticky="we", padx=10, pady=10, columnspan=2)
        CTkButton(self.adding_frame, text="Add", command=self.add_record).grid(row=2, column=3, sticky="we", padx=10, pady=10, columnspan=5)

    def create_total_value_frame(self):
        self.total_value_frame = CTkFrame(self.data_frame)
        self.total_value_frame.grid(row=2, column=1, sticky=NSEW)
        CTkLabel(self.total_value_frame, text="Estimated Total Value: ").pack(side=LEFT)
        CTkLabel(self.total_value_frame, textvariable=self.total_value_var).pack(side=LEFT)

    def start_script(self):
        thread1 = threading.Thread(target=main)
        thread1.start()
        CTkLabel(self.start_frame, text="Script started!").pack()

    def calibrate(self):
        save_old_collections()
        CTkLabel(self.start_frame, text="Calibration complete!").pack()
        print("Calibration complete!")

    def create_start_frame(self):  # ---------------------------- Start Frame
        self.start_frame = CTkFrame(self.root)
        self.start_frame.pack(fill=BOTH, expand=True)

        self.start_button = CTkButton(self.start_frame, text="Start", command=lambda *args: self.start_script(), width=200, height=100)

        self.calibration_button = CTkButton(self.start_frame, text="Calibrate", command=self.calibrate)

        self.start_button.pack(padx=10, pady=10)
        self.calibration_button.pack(padx=10, pady=10)

    def create_help_frame(self):  # ---------------------------- Help Frame
        self.help_frame = CTkFrame(self.root)
        self.help_frame.pack(fill=BOTH, expand=True)

        self.help_frame.columnconfigure(0, minsize=200, weight=1)

        CTkLabel(self.help_frame, text="How do I use StickerAutoOrder?", font=("Arial", 25)).grid(row=0, column=0,
                                                                                                  sticky="n", padx=10,
                                                                                                  pady=5)
        CTkLabel(self.help_frame, text="How do I create orders?", font=("Arial", 20)).grid(row=1, column=0, sticky="w",
                                                                                           padx=10, pady=5)
        CTkLabel(self.help_frame, text="""
            1-st area - you need to fill in information about tournament
            - tournament year;
            - tournament city;
            - teams or players that will participate in the tournament, one team per line.
              If you are not sure about name of the team, 
              you can check it on the stickers from previous tournaments.
              It is important to fill in the name of the team exactly as it is written on the sticker, 
              otherwise order will not be created!
            - after filling in the information, click the "Save" button.
            - Also, you need to choose a your Chromedriver path, previously installed it.

            2-nd area - this is just a filers for comfortable displaying of data in the table.

            3-rd area - this is a table where you can see all the orders you created.
            Tips for working with the table:
            - you can change width of columns by dragging the edges of the columns;
            - you can click on the records to select and delete them;

            4-th area - this is an area where you can create a new order.
            -choose the team name from the drop-down list;
            -choose the rarity of the sticker you want to order;
            -choose the number of stickers you want to order;
            -choose the price of the sticker you want to order;
            -press the "Add" button to add the order to the table.
            """, font=("Arial", 15), justify="left").grid(row=2, column=0, sticky="n", padx=10)

        CTkLabel(self.help_frame, text="How do I start the script?", font=("Arial", 20)).grid(row=3, column=0, sticky="w",
                                                                                              padx=10, pady=5)
        CTkLabel(self.help_frame, text="""Go to the "Start" tab and read the instructions carefully.""", font=("Arial", 15),
                 justify="left").grid(row=4, column=0, sticky="w", padx=10)

        CTkLabel(self.help_frame, text="What is Chromedriver and how to install it?", font=("Arial", 20)).grid(row=5,
                                                                                                               column=0,
                                                                                                               sticky="w",
                                                                                                               padx=10,
                                                                                                               pady=5)
        CTkLabel(self.help_frame, text="""Chromedriver is a WebDriver, in other words - a browser with ability to be automated.
            To download Chromedriver, simply find it in the Internet or go directly to https://chromedriver.chromium.org/
            Download "Latest stable release" and make sure you have latest version of Google Chrome.
            After downloading, choose a Chromedriver path is "Orders" tab in the left section. Now you are ready to go!
            """, font=("Arial", 15), justify="left").grid(row=6, column=0, sticky="w", padx=10)

        CTkLabel(self.help_frame, text=
        """In case you have any other questions or you want to report a bug,
        send them to my Telegram or email: 
        @luminexautoordering / cherkdmy@fel.cvut.cz
        """, font=("Arial", 17), justify="left").grid(row=7, column=0, sticky="w", padx=10, pady=5)

    def create_notebook(self):
        self.notebook = Notebook(self.root)
        self.notebook.pack(fill=BOTH, expand=True)

        self.create_data_frame()
        self.create_start_frame()
        self.create_help_frame()

        self.notebook.add(self.data_frame, text="  Data  ")
        self.notebook.add(self.start_frame, text="  Start  ")
        self.notebook.add(self.help_frame, text="  Help  ")


if __name__ == "__main__":
    GUI()
