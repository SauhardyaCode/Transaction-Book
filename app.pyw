import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msg
import tkcalendar as tk_cal
from datetime import datetime
from PIL import Image, ImageTk
import json
import os
import math
import copy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

MONTHS = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
colors = {'green':'#598C58', 'red':'#FF0B55'}
bg_colors = ('#E5D9F2','#C4D9FF','#578FCA', '#FDFAF6', "#F5E6E6", '#9ACBD0')
# bg_colors = ("#3A383D","#353C4A","#2D4C6D", "#574E43", "#6D4F4F", "#43595C")
# text_color = 'white'
fg_colors = ('#27548A', "#547792")
date_format = "%d %b, %Y"
instruction_str = [("(Green -> He/She owes you money)", "(Green -> You have been paid)", "(Green -> Money Credited)"), ("(Red -> You owe him/her money)", "(Red -> You have paid)", "(Red -> Money Debited)")]
date_selected = None
instructions = []
data_to_be_written = None

bg_for_top_frame = bg_colors[0]
bg_for_left_frame = bg_colors[1]
bg_for_left_frame_btn_clk = bg_colors[2]
bg_for_main_frame = bg_colors[3]
bg_for_entry = bg_colors[4]
bg_for_heading = bg_colors[5]
fg_for_sub_heading = fg_colors[0]
fg_for_unsettled_heading = fg_colors[1]

select_text = "-Select-"
null_options = ["Someone paid for you", "Someone lend/borrowed money"]
special_keys = ("#Borrow", "#Null", "#Not-Null", "#Return", "#Total")

PATH = os.path.dirname(__file__)
delete_image = Image.open(PATH+"/delete.png").resize((25,25))

def read_data(path="/data.json"):
    with open(PATH+path) as f:
        return json.load(f)

def write_data(data=None, retrieve=False):
    with open(PATH+"/data.json", 'w') as f:
        if retrieve:
            backup = read_data("/../transaction_book_data.json")
            json.dump(backup, f, indent=4)
            return
        else:
            json.dump(data, f, indent=4)
    with open(PATH+"/../transaction_book_data.json", 'w') as f:
        json.dump(data, f, indent=4)

def calculate_unsettled():
    data = read_data()
    persons = list(data["unsettled"].keys())
    unsettled_dict = {}
    for person in persons:
        unsettled_dict[person] = 0
        
    for transactions in list(data["transaction"].values()):
        for key, value in list(transactions.items()):
            if key==special_keys[0]:
                for null_value, trans in list(value.items()):
                    factor=1
                    if null_value==special_keys[1]:factor=-1
                    for person, amounts in list(trans.items()):
                        amount = sum(amounts.values())
                        try:
                            unsettled_dict[person] += amount*factor
                        except KeyError:
                            print(f"Person ({person}) removed from LIST (nothing unsettled)")
            else:
                if type(value)==dict:
                    for person, amount in list(value.items()):
                        if person!="Me":
                            try:
                                unsettled_dict[person] += amount
                            except KeyError:
                                print(f"Person ({person}) removed from LIST (nothing unsettled)")

    return unsettled_dict

def create_canvas_scrollbar(object):
    object.canvas = tk.Canvas(object.main_frame, bg=bg_for_main_frame)
    object.scrollbar = tk.Scrollbar(object.main_frame, orient="vertical", command=object.canvas.yview)
    object.scrollbar.pack(side='right', fill='y')
    object.canvas.pack(side='left', fill='both', expand=True)
    object.canvas.configure(yscrollcommand=object.scrollbar.set)

    object.main_scrollable_frame = tk.Frame(object.canvas, bg=bg_for_main_frame)
    object.canvas_window = object.canvas.create_window((0, 0), window=object.main_scrollable_frame, anchor='nw')

    object.main_scrollable_frame.bind("<Configure>", lambda e: object.canvas.configure(scrollregion=object.canvas.bbox("all")))
    object.canvas.bind('<Configure>', lambda e: object.canvas.itemconfig(object.canvas_window, width=e.width))
    object.canvas.bind_all("<MouseWheel>", lambda e: object.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

class BroilerPlate(tk.Tk):
    def __init__(self):
        global date_selected, instructions
        super().__init__()
        self.windows = [HomeWindow, UnsettledWindow, AddTransWindow]
        date_selected = tk.StringVar()
        instructions = [tk.StringVar(), tk.StringVar()]
        instructions[0].set(instruction_str[0][0])
        instructions[1].set(instruction_str[1][0])

        self.adjust_window()
        self.create_elements()
        self.show_elements()
    
    def adjust_window(self):
        self.title("Transaction Book")
        self.state("zoomed")

    def create_elements(self):
        self.top_frame = tk.Frame(self, bg=bg_for_top_frame)
        self.heading = tk.Label(self.top_frame, text="Transaction Book", font= ("Helvetica", 20), bg=bg_for_top_frame)
        self.info_frame = tk.Frame(self.top_frame, bg=bg_for_top_frame)
        self.greenInfo = tk.Label(self.info_frame, textvariable=instructions[0], font= ("Comicsans", 14), fg=colors['green'], bg=bg_for_top_frame)
        self.redInfo = tk.Label(self.info_frame, textvariable=instructions[1], font= ("Comicsans", 14), fg=colors['red'], bg=bg_for_top_frame)

        self.left_frame  = tk.Frame(self, bg=bg_for_left_frame)
        self.home_btn = tk.Button(self.left_frame, text="Home", font=("Verdana", 12), bd=0, bg=bg_for_left_frame, activebackground=bg_for_left_frame_btn_clk)
        self.unsettled_btn = tk.Button(self.left_frame, text="Unsettled", font=("Verdana", 12), bd=0, bg=bg_for_left_frame, activebackground=bg_for_left_frame_btn_clk)
        self.addTrans_btn = tk.Button(self.left_frame, text="Add Transaction", font=("Verdana", 12), bd=0, bg=bg_for_left_frame, activebackground=bg_for_left_frame_btn_clk)
        self.home_btn.config(state='disabled')
        self.nav_btns = [self.home_btn, self.unsettled_btn, self.addTrans_btn]
        for i in range(len(self.nav_btns)):
            self.nav_btns[i].config(command=lambda i=i:self.switchWindow(self.windows[i],self.nav_btns[i]))

        self.main_frame = tk.Frame(self, bg=bg_for_main_frame)

    def show_elements(self):
        self.top_frame.pack(fill="x",ipady=10)
        self.heading.pack()
        self.info_frame.pack()
        self.greenInfo.grid(row=0,column=0,padx=10)
        self.redInfo.grid(row=0,column=1,padx=10)

        self.left_frame.pack(fill='y',ipadx=20, ipady=10, side='left')
        self.home_btn.pack(fill='x',ipady=5)
        self.unsettled_btn.pack(fill='x',ipady=5)
        self.addTrans_btn.pack(fill='x',ipady=5)

        self.main_frame.pack(fill='both', expand=True, ipadx=20, ipady=10)

    def switchWindow(self, WindowClass, btnClicked):
        for btn in self.nav_btns:
            btn.config(state='normal')
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        btnClicked.config(state='disabled')
        WindowClass(self.main_frame)
    
    def show(self):
        HomeWindow(self.main_frame)
        self.mainloop()

class HomeWindow:
    def __init__(self, main_frame):
        global instructions
        instructions[0].set(instruction_str[0][2])
        instructions[1].set(instruction_str[1][2])
        self.current_month = datetime.now().strftime("%b")
        self.current_year = datetime.now().strftime("%Y")
        self.chosen_month = self.current_month
        self.chosen_year = self.current_year
        self.chosen_year_alone = self.current_year
        self.total_years = set()
        for dates in read_data()["transaction"].keys():
            self.total_years.add(dates.split(', ')[1])
        self.total_years = list(map(str, sorted(list(map(int, self.total_years)))))
        self.main_frame = main_frame
        self.create_elememts()
    
    def create_elememts(self):
        create_canvas_scrollbar(self)

        # Main Elements
        self.title = tk.Label(self.main_scrollable_frame, text="Home", font=("Verdana", 18, "underline"), bg=bg_for_main_frame)
        self.display_frame = tk.Frame(self.main_scrollable_frame, bg=bg_for_main_frame)
        self.title.pack()
        self.display_frame.pack(pady=60, fill='x')

        self.show_monthly_stats()
        self.show_yearly_stats()
    
    def show_monthly_stats(self):
        #creating elements
        self.monthAnalysisLabel = tk.Label(self.display_frame, text=f"Monthly Stats ({self.chosen_month}, {self.chosen_year})", font=("Robota",15,"underline"), bg=bg_for_main_frame, fg=fg_colors[0])

        self.month_stats_frame = tk.Frame(self.display_frame, bg=bg_for_main_frame)
        self.month_analysis_frame = tk.Frame(self.month_stats_frame, bg=bg_for_main_frame)

        self.monthDebitLabel = tk.Label(self.month_analysis_frame, text="Net Debit: ", font=("Robota",15), bg=bg_for_main_frame)
        self.monthDebitValueLabel = tk.Label(self.month_analysis_frame, text= self.calculate_month_total(self.chosen_month, self.chosen_year, debit=True), font=("Robota",15), bg=bg_for_main_frame, fg=colors["red"])
        self.monthCreditLabel = tk.Label(self.month_analysis_frame, text="Net Credit: ", font=("Robota",15), bg=bg_for_main_frame)
        self.monthCreditValueLabel = tk.Label(self.month_analysis_frame, text= self.calculate_month_total(self.chosen_month, self.chosen_year, credit=True), font=("Robota",15), bg=bg_for_main_frame, fg=colors["green"])

        month_total = self.calculate_month_total(self.chosen_month, self.chosen_year)
        self.monthTotalLabel = tk.Label(self.month_analysis_frame, text="Month's Total:", font=("Robota",15), bg=bg_for_main_frame)
        self.monthTotalValueLabel = tk.Label(self.month_analysis_frame, text= abs(month_total), font=("Robota",15), bg=bg_for_main_frame, fg=colors["green" if month_total<=0 else "red"])

        self.month_select_frame = tk.Frame(self.display_frame, bg=bg_for_main_frame)
        self.monthSelectLabel = tk.Label(self.month_select_frame, text="Select Month and Year:", font=("Robota",15), bg=bg_for_main_frame)

        month = tk.StringVar()
        year = tk.StringVar()
        month.set(self.chosen_month)
        year.set(self.chosen_year)
        self.monthSelect = ttk.Combobox(self.month_select_frame, textvariable=month, values=MONTHS, width=15, font=("Helvetica", 15))
        self.yearSelect = ttk.Combobox(self.month_select_frame, textvariable=year, values=[str(y) for y in range(int(self.current_year), 1964, -1)], width=15, font=("Helvetica", 15))
        self.monthSelect.config(state='readonly')
        self.yearSelect.config(state='readonly')
        self.changeMonthBtn = tk.Button(self.month_select_frame, text="Show", font=("Robota", 12), command=lambda:self.refresh_monthly_stats(month.get()[:3], year.get()))

        #showing elements
        self.monthAnalysisLabel.pack()
        self.month_stats_frame.pack(pady=30, padx=120)
        self.month_analysis_frame.grid(row=0, column=0, padx=(0, 50))
        self.monthDebitLabel.grid(row=0, column=0, padx=20)
        self.monthDebitValueLabel.grid(row=0, column=1)
        self.monthCreditLabel.grid(row=1, column=0, padx=20)
        self.monthCreditValueLabel.grid(row=1, column=1)
        self.monthTotalLabel.grid(row=2, column=0, padx=20)
        self.monthTotalValueLabel.grid(row=2, column=1)
        self.plot_daily_graph()
        self.month_select_frame.pack(fill='x', padx=120, pady=30)
        self.monthSelectLabel.grid(row=0, column=0, padx=(0, 30))
        self.monthSelect.grid(row=0, column=1, padx=30)
        self.yearSelect.grid(row=0, column=2, padx=30)
        self.changeMonthBtn.grid(row=0, column=3, padx=(30,0))
    
    def refresh_monthly_stats(self, month, year):
        if self.chosen_month!=month or self.chosen_year!=year:
            self.chosen_month = month
            self.chosen_year = year
            self.monthAnalysisLabel.destroy()
            self.month_stats_frame.destroy()
            self.month_select_frame.destroy()
            self.show_monthly_stats()

    def calculate_month_total(self, month, year, debit=False, credit=False):
        total=0
        debit_total=0
        credit_total=0
        data = read_data()
        transactions = data["transaction"]
        for date, value in transactions.items():
            if date.endswith(f"{month}, {year}"):
                if debit or credit:
                    for title, expense in value.items():
                        if title not in special_keys:
                            if type(expense)==int:
                                if expense>0: debit_total+=expense
                                else: credit_total-=expense
                            else:
                                for money in expense.values():
                                    if money>0: debit_total+=money
                                    else: credit_total-=money
                        elif title==special_keys[0]:
                            for subtype, trans in expense.items():
                                if subtype==special_keys[2]:
                                    for purpose in trans.values():
                                        for money in purpose.values():
                                            if money>0: debit_total+=money
                                            else: credit_total-=money
                        elif title==special_keys[3]:
                            for money in expense.values():
                                if money>0: debit_total+=money
                                else: credit_total-=money
                else:
                    total+=transactions[date][special_keys[4]]
        if debit: return debit_total
        if credit: return credit_total
        return total
    
    def plot_daily_graph(self):
        plot_data = [[],[]]
        data = read_data()
        transactions = data["transaction"]
        for date, value in transactions.items():
            if date.endswith(f"{self.chosen_month}, {self.chosen_year}"):
                plot_data[0].append(date.split()[0])
                plot_data[1].append(value[special_keys[4]])

        figure = plt.Figure(figsize=(10,5), dpi=70)
        figure_plot = figure.add_subplot(1, 1, 1)

        sorted_indices = np.argsort(np.array(plot_data[0]))
        x = np.array(plot_data[0])[sorted_indices]
        y = np.array(plot_data[1])[sorted_indices]

        figure_plot.plot(x, y, color='blue', linestyle='-', marker='o', label='Line 1')
        figure_plot.axhline(0, color='black', linewidth=1, linestyle='--') 
        figure_plot.fill_between(x, y, where= (y<0), color='green', alpha=0.5, interpolate=True)
        figure_plot.fill_between(x, y, where= (y>0), color='red', alpha=0.5, interpolate=True)

        figure_plot.set_title("Net Transaction Each Day")
        figure_plot.set_xlabel("Day")
        figure_plot.set_ylabel("Net Transaction")
        figure_plot.legend()

        canvas = FigureCanvasTkAgg(figure, master=self.month_stats_frame)
        figure.tight_layout()
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=1)

    def show_yearly_stats(self):
        #creating elements
        self.yearAnalysisLabel = tk.Label(self.display_frame, text=f"Yearly Stats ({self.chosen_year_alone})", font=("Robota",15,"underline"), bg=bg_for_main_frame, fg=fg_colors[0])

        self.year_stats_frame = tk.Frame(self.display_frame, bg=bg_for_main_frame)
        self.year_analysis_frame = tk.Frame(self.year_stats_frame, bg=bg_for_main_frame)

        self.yearDebitLabel = tk.Label(self.year_analysis_frame, text="Net Debit: ", font=("Robota",15), bg=bg_for_main_frame)
        self.yearDebitValueLabel = tk.Label(self.year_analysis_frame, text= self.calculate_year_total(self.chosen_year_alone, debit=True), font=("Robota",15), bg=bg_for_main_frame, fg=colors["red"])
        self.yearCreditLabel = tk.Label(self.year_analysis_frame, text="Net Credit: ", font=("Robota",15), bg=bg_for_main_frame)
        self.yearCreditValueLabel = tk.Label(self.year_analysis_frame, text= self.calculate_year_total(self.chosen_year_alone, credit=True), font=("Robota",15), bg=bg_for_main_frame, fg=colors["green"])

        year_total = self.calculate_year_total(self.chosen_year_alone)
        self.yearTotalLabel = tk.Label(self.year_analysis_frame, text="Year's Total:" if self.chosen_year_alone!="ALL" else "Grand Total: ", font=("Robota",15), bg=bg_for_main_frame)
        self.yearTotalValueLabel = tk.Label(self.year_analysis_frame, text= abs(year_total), font=("Robota",15), bg=bg_for_main_frame, fg=colors["green" if year_total<=0 else "red"])

        self.year_select_frame = tk.Frame(self.display_frame, bg=bg_for_main_frame)
        self.yearSelectLabel = tk.Label(self.year_select_frame, text="Select Year:", font=("Robota",15), bg=bg_for_main_frame)

        year = tk.StringVar()
        year.set(self.chosen_year_alone)
        self.yearSelect = ttk.Combobox(self.year_select_frame, textvariable=year, values=["ALL"]+[str(y) for y in range(int(self.current_year), 1964, -1)], width=15, font=("Helvetica", 15))
        self.yearSelect.config(state='readonly')
        self.changeYearBtn = tk.Button(self.year_select_frame, text="Show", font=("Robota", 12), command=lambda:self.refresh_yearly_stats(year.get()))

        #showing elements
        self.yearAnalysisLabel.pack(pady=(50,0))
        self.year_stats_frame.pack(pady=30, padx=120)
        self.year_analysis_frame.grid(row=0, column=0, padx=(0, 50))
        self.yearDebitLabel.grid(row=0, column=0, padx=20)
        self.yearDebitValueLabel.grid(row=0, column=1)
        self.yearCreditLabel.grid(row=1, column=0, padx=20)
        self.yearCreditValueLabel.grid(row=1, column=1)
        self.yearTotalLabel.grid(row=2, column=0, padx=20)
        self.yearTotalValueLabel.grid(row=2, column=1)
        self.plot_monthly_graph()
        self.year_select_frame.pack(padx=120, pady=30)
        self.yearSelectLabel.grid(row=0, column=0, padx=(0, 30))
        self.yearSelect.grid(row=0, column=1, padx=30)
        self.changeYearBtn.grid(row=0, column=2, padx=(30,0))
    
    def refresh_yearly_stats(self, year):
        if self.chosen_year_alone!=year:
            self.chosen_year_alone = year
            self.yearAnalysisLabel.destroy()
            self.year_stats_frame.destroy()
            self.year_select_frame.destroy()
            self.show_yearly_stats()
    
    def calculate_year_total(self, year, debit=False, credit=False):
        total=0
        if year=="ALL":
            for y in self.total_years:
                total += self.calculate_year_total(y, debit, credit)
        else:
            for month_name in MONTHS:
                month = month_name[:3]
                total += self.calculate_month_total(month, year, debit=debit, credit=credit)
        return total
    
    def plot_monthly_graph(self):
        plot_data = [[],[]]
        if self.chosen_year_alone=="ALL":
            for y in self.total_years:
                for month_name in MONTHS:
                    month = month_name[:3]
                    money = self.calculate_month_total(month, y)
                    if money:
                        plot_data[0].append(f"{month}\n{y}")
                        plot_data[1].append(money)
        else:
            for month_name in MONTHS:
                month = month_name[:3]
                money = self.calculate_month_total(month, self.chosen_year_alone)
                if money:
                    plot_data[0].append(month)
                    plot_data[1].append(money)

        figure = plt.Figure(figsize=(10,5), dpi=70)
        figure_plot = figure.add_subplot(1, 1, 1)

        x = np.array(plot_data[0])
        y = np.array(plot_data[1])
        colors = ["green" if money<=0 else "red" for money in y]
    
        # Create bars with different colors
        figure_plot.axhline(0, color='black', linewidth=1, linestyle='--') 
        bars = figure_plot.bar(x, y, width=0.6, color=colors)
        for bar in bars:
            bar.set_alpha(0.5)
        
        # Customize the plot
        figure_plot.set_title('Net Transaction Per Month', pad=20)
        figure_plot.set_xlabel('Month')
        figure_plot.set_ylabel('Net Transaction')
        
        # Embed the plot in Tkinter
        canvas = FigureCanvasTkAgg(figure, master=self.year_stats_frame)
        figure.tight_layout()
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=1)
    
class UnsettledWindow:
    def __init__(self, main_frame):
        global instructions
        instructions[0].set(instruction_str[0][0])
        instructions[1].set(instruction_str[1][0])
        self.main_frame = main_frame
        self.new_person = tk.StringVar()
        self.create_elememts()
        self.show_elements()
        self.show_unsettled()
    
    def create_elememts(self):
        create_canvas_scrollbar(self)

        # Main Elements
        self.title = tk.Label(self.main_scrollable_frame, text="Unsettled Amounts", font=("Verdana", 18, "underline"), bg=bg_for_main_frame)
        self.display_frame = tk.Frame(self.main_scrollable_frame, bg=bg_for_main_frame)
        self.add_person_frame = tk.Frame(self.main_scrollable_frame, bg=bg_for_main_frame)
        self.personEntry = tk.Entry(self.add_person_frame, textvariable=self.new_person, font=("Comicsans", 15), justify='center')
        self.savePersonBtn = tk.Button(self.add_person_frame, text="Save", font=("Robota", 12), command=lambda:self.add_person(1))
        self.btn_frame = tk.Frame(self.main_scrollable_frame, bg=bg_for_main_frame)
        self.refreshBtn = tk.Button(self.btn_frame, text="Refresh", font=("Robota", 15), command=self.refresh)
        self.addPersonBtn = tk.Button(self.btn_frame, text="Add Person", font=("Robota", 15), command=lambda:self.add_person(0))

        self.slnoLabel= tk.Label(self.display_frame, text="SL NO.", font=("Robota",15, "bold", "underline"), bg=bg_for_main_frame, fg=fg_for_unsettled_heading)
        self.personLabel = tk.Label(self.display_frame, text="PERSON", font=("Robota",15, "bold", "underline"), bg=bg_for_main_frame, fg=fg_for_unsettled_heading)
        self.amountLabel = tk.Label(self.display_frame, text="AMOUNT UNSETTLED", font=("Robota",15, "bold", "underline"), bg=bg_for_main_frame, fg=fg_for_unsettled_heading)
    
    def show_elements(self):
        self.title.pack()
        self.display_frame.pack(pady=60, fill='x')
        self.btn_frame.pack(pady=50)
        self.refreshBtn.grid(row=0, column=0, padx=30, ipady=2, ipadx=5)
        self.addPersonBtn.grid(row=0, column=1, padx=30, ipady=2, ipadx=5)
        self.display_frame.grid_columnconfigure(1, weight=1)
        self.slnoLabel.grid(row=0, column=0, padx=(300,0), pady=5)
        self.personLabel.grid(row=0, column=1, pady=5)
        self.amountLabel.grid(row=0, column=2, padx=(0,300), pady=5)
        self.personEntry.grid(row=0, column=0, padx=20, ipady=5)
        self.savePersonBtn.grid(row=0, column=1, padx=20)
    
    def show_unsettled(self):
        unsettled_dict = read_data()["unsettled"]
        self.unsettled_elements = []
        for person, amount in list(unsettled_dict.items()):
            slno = len(self.unsettled_elements)+1

            slnoValue = tk.Label(self.display_frame, text=f"{slno}.", font=("Robota", 15), bg=bg_for_main_frame)
            personValue = tk.Label(self.display_frame, text=person, font=("Robota", 15), bg=bg_for_main_frame)
            amountValue = tk.Label(self.display_frame, text=abs(amount), font=("Robota", 15, "bold"), bg=bg_for_main_frame)
            if amount>0:
                amountValue.config(fg=colors["green"])
            elif amount<0:
                amountValue.config(fg=colors["red"])
            else:
                amountValue.config(text='None', font=("Robota", 10))

            slnoValue.grid(row=slno, column=0, padx=(300,0), pady=5)
            personValue.grid(row=slno, column=1, pady=5)
            amountValue.grid(row=slno, column=2, padx=(0,300), pady=5)
            self.unsettled_elements.append([slnoValue, personValue, amountValue])
        self.canvas.yview_moveto(0.0)
    
    def add_person(self, flag):
        if flag==0:
            self.btn_frame.pack_forget()
            self.add_person_frame.pack(pady=50)
        else:
            data_to_be_written = read_data()
            person = self.new_person.get().strip()
            if person in data_to_be_written["unsettled"]:
                msg.showerror(f"Duplicate Person ({person})", "This person already exists!")
            else:
                if person:
                    data_to_be_written["unsettled"][person] = 0
                    write_data(data_to_be_written)
                    self.show_unsettled()
                self.add_person_frame.pack_forget()
                self.btn_frame.pack(pady=50)
    
    def refresh(self):
        data = read_data()
        data["unsettled"] = calculate_unsettled()
        write_data(data)
        self.show_unsettled()

class AddTransWindow:
    def __init__(self, main_frame):
        global instructions
        instructions[0].set(instruction_str[0][1])
        instructions[1].set(instruction_str[1][1])
        self.main_frame = main_frame
        self.date_popup = None
        self.transaction_popup = None
        self.borrow_popup = None
        self.return_popup = None
        if date_selected.get()=="":
            date_selected.set(datetime.today().strftime(date_format))
        self.create_elememts()
        self.show_elements()
    
    def create_elememts(self):
        create_canvas_scrollbar(self)
        
        # Main Elements
        self.title = tk.Label(self.main_scrollable_frame, text="Add Transaction", font=("Verdana", 18, "underline"), bg=bg_for_main_frame)
        self.input_frame = tk.Frame(self.main_scrollable_frame, bg=bg_for_main_frame)

        self.dateLbl = tk.Label(self.input_frame, text="Choose Transaction Date", font=("Robota",15), bg=bg_for_main_frame)
        self.entry_frame = tk.Frame(self.input_frame, bg=bg_for_main_frame)
        self.dateEntry = tk.Entry(self.entry_frame, textvariable=date_selected, font=("Comicsans", 12), readonlybackground=bg_for_entry)
        self.dateEntry.config(state='readonly')
        self.dateBtn = tk.Button(self.entry_frame, text="Set Date", font=("Robota", 10), command=self.showDatePopup)

        self.addLbl = tk.Label(self.input_frame, text="Add Transactions on this Day", font=("Robota",15), bg=bg_for_main_frame)
        self.options_frame = tk.Frame(self.input_frame, bg=bg_for_main_frame)
        self.addBorrBtn = tk.Button(self.options_frame, text="Add Borrowings", font=("Robota", 13), cursor="hand2", command=self.add_borrow_transaction)
        self.addRetBtn = tk.Button(self.options_frame, text="Add Returns", font=("Robota", 13), cursor="hand2", command=self.add_return_transaction)
        self.addTrnBtn = tk.Button(self.options_frame, text="Add Other Transactions", font=("Robota", 13), cursor="hand2", command=self.add_general_transaction)

        self.dataLbl = tk.Label(self.input_frame, text="Your Transactions on this day", font=("Robota",15), bg=bg_for_main_frame)
        self.data_frame = tk.Frame(self.main_scrollable_frame, bg=bg_for_main_frame)
        self.deleteAllBtn = tk.Button(self.main_scrollable_frame, text="Delete All", font=("Robota", 13, "bold"), cursor="hand2", command=self.delete_all_transaction, bg='red', fg='white', activebackground=colors['red'], activeforeground='white')
        self.show_transactions(date_selected.get())
    
    def show_elements(self):
        self.title.pack()
        self.input_frame.pack(fill='x',pady=60,padx=50)
        self.dateLbl.grid(row=0, column=0, padx=30)

        self.entry_frame.grid(row=0, column=1, padx=30)
        self.dateEntry.grid(row=0, column=0, padx=30, ipadx=10, ipady=5)
        self.dateBtn.grid(row=0, column=1, padx=30)

        self.addLbl.grid(row=1, column=0, padx=30, pady=40)

        self.options_frame.grid(row=1, column=1, padx=30, pady=40)
        self.addBorrBtn.grid(row=0, column=0, padx=30, ipadx=20, ipady=5)
        self.addRetBtn.grid(row=0, column=1, padx=30, ipadx=20, ipady=5)
        self.addTrnBtn.grid(row=0, column=2, padx=30, ipadx=20, ipady=5)

        self.dataLbl.grid(row=2, column=0, padx=30)
        self.data_frame.pack(padx=30, ipadx=100, ipady=10)
        self.deleteAllBtn.pack(ipadx=10, ipady=3, pady=10)
    
    def delete_all_transaction(self):
        data_to_be_written = self.data_read_from_file
        if date_selected.get() not in data_to_be_written["transaction"] or data_to_be_written["transaction"][date_selected.get()] == {special_keys[0]: {special_keys[1]: {},special_keys[2]: {}},special_keys[3]: {},special_keys[4]: 0}:
            msg.showinfo("No Data", "Nothing to delete on this day!")
        else:
            if msg.askyesno("Delete Transactions", f"Are you sure you want to delete all transactions on {date_selected.get()}?"):
                del data_to_be_written["transaction"][date_selected.get()]
                self.write_data(data_to_be_written)
                self.show_transactions(date_selected.get())

    def showDatePopup(self):
        if self.date_popup:
            self.date_popup.destroy()
        self.date_popup = tk.Toplevel(self.main_frame)
        self.date_popup.title("Date Picker")
        self.date_popup.geometry("300x300+500+200")
        self.date_popup.resizable(0,0)
        dateSelected = datetime.strptime(date_selected.get(), date_format).date()
        self.dateInp = tk_cal.Calendar(self.date_popup, selectmode='day', date_pattern='dd-mm-yyyy', width=10, bg=bg_for_main_frame, borderwidth=2,
                                       day=dateSelected.day, month=dateSelected.month, year=dateSelected.year)
        self.btn_frame = tk.Frame(self.date_popup)
        self.dateOkBtn = tk.Button(self.btn_frame, text="Set", font=("Robota", 10),command=lambda:self.setDate(0))
        self.dateCancelBtn = tk.Button(self.btn_frame, text="Reset", font=("Robota", 10),command=lambda:self.setDate(1))
        self.dateInp.pack()
        self.btn_frame.pack(pady=10)
        self.dateOkBtn.grid(row=0,column=0,ipadx=20,padx=15)
        self.dateCancelBtn.grid(row=0,column=1,ipadx=20,padx=15)

    def delete_title_from_person_borrow(self, unique_title, borrow_sl_no):
        if msg.askyesno("Confirm Delete", "Are you sure you want to delete this sub-transaction?"):
            data_to_be_written = self.data_read_from_file
            person, _, _, isNull = self.borrow_variables[borrow_sl_no]
            del data_to_be_written["transaction"][date_selected.get()][special_keys[0]][special_keys[2-isNull]][person.get()][unique_title]
            self.write_data(data_to_be_written)
            self.show_transactions(date_selected.get())
    
    def delete_person_from_title_borrow(self, unique_person, transaction_sl_no):
        if msg.askyesno("Confirm Delete", "Are you sure you want to delete this sub-transaction?"):
            data_to_be_written = self.data_read_from_file
            title = self.transaction_variables[transaction_sl_no][0]
            del data_to_be_written["transaction"][date_selected.get()][title.get()][unique_person]
            self.write_data(data_to_be_written)
            self.show_transactions(date_selected.get())

    def show_transactions(self, date):
        self.return_inputs = []
        self.return_buttons = []
        self.return_variables = []

        self.borrow_inputs = []
        self.borrow_buttons = []
        self.borrow_variables = []

        self.transaction_inputs = []
        self.transaction_buttons = []
        self.transaction_variables = []

        for widget in self.data_frame.winfo_children():
            widget.destroy()

        self.data_read_from_file = read_data()
        all_transactions = copy.deepcopy(self.data_read_from_file["transaction"])

        if date in all_transactions:
            total_transaction = all_transactions[date][special_keys[4]]
        else:
            total_transaction = 0
        total_frame = tk.Frame(self.data_frame, bg=bg_for_main_frame)
        totalLabel = tk.Label(total_frame, text="Net Transaction:", bg=bg_for_main_frame, font=("Times New Roman", 15, "bold", "underline"))
        totalAmout = tk.Label(total_frame, text=abs(total_transaction), bg=bg_for_main_frame, font=("Times New Roman", 15, "bold"))
        total_frame.pack(pady=(0,10))
        totalLabel.grid(row=0, column=0, padx=10)
        totalAmout.grid(row=0, column=1, padx=10)
        if total_transaction>0:
            totalAmout.config(fg=colors["red"])
        else:
            totalAmout.config(fg=colors["green"])


        if date in all_transactions:
            transactions = all_transactions[date]
            borrow_transactions = transactions[special_keys[0]]
            for key, value in borrow_transactions.items():
                transactions[key] = value
            del transactions[special_keys[0]]

            case_transaction_title = 0
            case_borrow_title = 0
            case_null_title = 0
            case_not_null_title = 0
            case_return_title = 0

            transaction_sl_no=0
            borrow_sl_no=0
            borrow_null_sl_no=0
            borrow_not_null_sl_no=0
            return_sl_no=0

            for i,x in enumerate(transactions.keys()):
                if (x in special_keys[1:3]):
                    for human in (transactions[x].keys()):
                        isNull = (x==special_keys[1])
                        money = []
                        money_sign = []
                        money_entry_element = []
                        person = tk.StringVar()
                        person.set(human)

                        if not case_borrow_title:
                            case_borrow_title=1
                            heading = tk.Label(self.data_frame, font=("Verdana", 15, 'bold'), text="Borrow Transactions", bg=bg_for_heading)
                            heading.pack(fill='x', pady=(30,10), ipady=10)

                        if (not case_null_title and isNull):
                            case_null_title=1
                            elemTitle = tk.Label(self.data_frame, font=("Times New Roman", 15), text=null_options[0], bg=bg_for_main_frame, fg=fg_for_sub_heading)
                            elemTitle.pack(anchor='w', pady=(10,0))
                        elif (not case_not_null_title and not isNull):
                            case_not_null_title=1
                            elemTitle = tk.Label(self.data_frame, font=("Times New Roman", 15), text=null_options[1], bg=bg_for_main_frame, fg=fg_for_sub_heading)
                            elemTitle.pack(anchor='w', pady=(10,0))

                        elem = tk.Frame(self.data_frame, bg=bg_for_main_frame, borderwidth=1, relief="solid")
                        elemPersonSelect = ttk.Combobox(elem, textvariable=person, values=list(self.data_read_from_file["unsettled"].keys()), width=15, font=("Helvetica", 15))
                        elem_title_frame = tk.Frame(elem, bg=bg_for_main_frame)
                        elem_btn_frame = tk.Frame(elem, bg=bg_for_main_frame)
                        elemEditConfBtn = tk.Button(elem_btn_frame, text="Edit", font=("Robota", 10), command= lambda borrow_index=borrow_sl_no, self_index=[borrow_null_sl_no, borrow_not_null_sl_no]: self.edit_save_borrow(borrow_index, self_index))
                        elemDelResetBtn = tk.Button(elem_btn_frame, text="Delete", font=("Robota", 10), command= lambda borrow_index=borrow_sl_no, self_index=[borrow_null_sl_no, borrow_not_null_sl_no]: self.cancel_delete_borrow(borrow_index, self_index))

                        elem.pack(fill='x', pady=10)
                        elemPersonSelect.grid(row=0, column=0, padx=30, pady=10, ipadx=10, ipady=10)
                        elem.grid_columnconfigure(2, weight=1)
                        elem_title_frame.grid(row=0, column=1)
                        elem_btn_frame.grid(row=0, column=3)
                        elemEditConfBtn.grid(row=0,column=0, padx=15, pady=10, ipadx=15)
                        elemDelResetBtn.grid(row=0,column=1, padx=15, pady=10, ipadx=15)

                        elemPersonSelect.config(state='disabled')

                        delBtnList = []
                        for title in transactions[x][human].keys():
                            money.append([tk.StringVar(), tk.IntVar()])
                            money[-1][0].set(title)
                            money[-1][1].set(transactions[x][human][title])
                            money_sign.append(int(math.copysign(1,money[-1][1].get())))

                            elem_sub_frame = tk.Frame(elem_title_frame, bg=bg_for_main_frame)
                            elemTitle = tk.Entry(elem_sub_frame, font=("Times New Roman", 15), textvariable=money[-1][0], width=20, readonlybackground=bg_for_entry)
                            elemMoney = tk.Entry(elem_sub_frame, font=("Comicsans", 12, "bold"), textvariable=money[-1][1], width=8, readonlybackground=bg_for_entry)
                            photo = ImageTk.PhotoImage(delete_image)
                            elemDelBtn = tk.Button(elem_sub_frame, image=photo, bd=0, bg=bg_for_main_frame, command=lambda unique_title=title, borrow_index=borrow_sl_no:self.delete_title_from_person_borrow(unique_title, borrow_index))
                            elemDelBtn.image = photo

                            elem_sub_frame.pack()
                            elemTitle.grid(row=0, column=0, padx=(30, 5), pady=5, ipadx=10, ipady=2)
                            elemMoney.grid(row=0, column=1, padx=30, pady=5, ipadx=10, ipady=2)

                            elemTitle.config(state='readonly')
                            elemMoney.config(state='readonly')
                            money_entry_element.append([elemTitle, elemMoney])
                            delBtnList.append(elemDelBtn)

                            if not isNull:
                                self.set_transaction_color(money[-1][1], money_sign[-1], elemMoney)

                        self.borrow_buttons.append([elemEditConfBtn, elemDelResetBtn, delBtnList])
                        self.borrow_variables.append([person, money, money_sign, isNull])
                        self.borrow_inputs.append([elemPersonSelect, money_entry_element])
                        borrow_sl_no+=1
                        if isNull:borrow_null_sl_no+=1
                        else:borrow_not_null_sl_no+=1
     
                elif x == special_keys[3]:
                    for human in (transactions[x].keys()):
                        person = tk.StringVar()
                        money = tk.IntVar()
                        person.set(human)
                        money.set(transactions[x][human])
                        money_sign = int(math.copysign(1,money.get()))

                        if not case_return_title:
                            case_return_title=1
                            heading = tk.Label(self.data_frame, font=("Verdana", 15, 'bold'), text="Return Transactions", bg=bg_for_heading)
                            heading.pack(fill='x', pady=(30,10), ipady=10)
                        
                        elem = tk.Frame(self.data_frame, bg=bg_for_main_frame, borderwidth=1, relief="solid")
                        elemPersonSelect = ttk.Combobox(elem, textvariable=person, values=list(self.data_read_from_file["unsettled"].keys()), width=15, font=("Helvetica", 15))
                        elemMoneyEntry = tk.Entry(elem, font=("Comicsans", 12, "bold"), textvariable=money, width=8, readonlybackground=bg_for_entry)
                        elem_btn_frame = tk.Frame(elem, bg=bg_for_main_frame)
                        elemEditConfBtn = tk.Button(elem_btn_frame, text="Edit", font=("Robota", 10), command=lambda index=return_sl_no: self.edit_save_return(index))
                        elemDelResetBtn = tk.Button(elem_btn_frame, text="Delete", font=("Robota", 10), command=lambda index=return_sl_no: self.cancel_delete_return(index))
                        
                        elem.pack(fill='x', pady=10)
                        elemPersonSelect.grid(row=0, column=0, padx=30, pady=10, ipadx=10, ipady=10)
                        elem.grid_columnconfigure(2, weight=1)
                        elemMoneyEntry.grid(row=0, column=1, padx=48, pady=5, ipady=2, ipadx=10)
                        elem_btn_frame.grid(row=0, column=3)
                        elemEditConfBtn.grid(row=0,column=0, padx=15, pady=10, ipadx=15)
                        elemDelResetBtn.grid(row=0,column=1, padx=15, pady=10, ipadx=15)

                        elemPersonSelect.config(state='disabled')
                        elemMoneyEntry.config(state='readonly')

                        self.set_transaction_color(money, money_sign, elemMoneyEntry)

                        self.return_buttons.append([elemEditConfBtn, elemDelResetBtn])
                        self.return_variables.append([person, money, money_sign])
                        self.return_inputs.append([elemPersonSelect, elemMoneyEntry])
                        return_sl_no+=1

                elif x == special_keys[4]:
                    pass

                else:
                    title = tk.StringVar()
                    title.set(x)
                    if not case_transaction_title:
                        case_transaction_title=1
                        heading = tk.Label(self.data_frame, font=("Verdana", 15, 'bold'), text="General Transaction", bg=bg_for_heading)
                        heading.pack(fill='x', pady=10, ipady=10)

                    elem = tk.Frame(self.data_frame, bg=bg_for_main_frame, borderwidth=1, relief="solid")
                    elemTitle = tk.Entry(elem, font=("Times New Roman", 15), textvariable=title, width=20, readonlybackground=bg_for_entry)
                    elem_btn_frame = tk.Frame(elem, bg=bg_for_main_frame)
                    elemEditConfBtn = tk.Button(elem_btn_frame, text="Edit", font=("Robota", 10), command= lambda self_index=transaction_sl_no, index=i: self.edit_save_transaction(self_index, index))
                    elemDelResetBtn = tk.Button(elem_btn_frame, text="Delete", font=("Robota", 10), command= lambda self_index=transaction_sl_no, index=i: self.cancel_delete_transaction(self_index, index))
                    
                    elem.pack(fill='x', pady=10)
                    elemTitle.grid(row=0,column=0, padx=30, pady=10, ipadx=10, ipady=10)
                    elem.grid_columnconfigure(2, weight=1)
                    elem_btn_frame.grid(row=0, column=3)
                    elemEditConfBtn.grid(row=0,column=0, padx=15, pady=10, ipadx=15)
                    elemDelResetBtn.grid(row=0,column=1, padx=15, pady=10, ipadx=15)

                    elemTitle.config(state='readonly')

                    delBtnList = []
                    if type(transactions[x]) == int:
                        money = tk.IntVar()
                        money.set(transactions[x])
                        money_sign = int(math.copysign(1,money.get()))
                        elemMoney = tk.Entry(elem, font=("Comicsans", 12, "bold"), textvariable=money, width=8, readonlybackground=bg_for_entry)
                        elemMoney.grid(row=0,column=1, padx=30, pady=10, ipadx=10, ipady=2)
                        elemMoney.config(state='readonly')
                        self.set_transaction_color(money, money_sign, elemMoney)
                        money_entry_element = elemMoney
                    else:
                        money = []
                        money_sign = []
                        money_entry_element = []
                        sub_transactions = transactions[x]
                        elem_money_frame = tk.Frame(elem, bg=bg_for_main_frame)
                        elem_money_frame.grid(row=0,column=1)

                        for person in sub_transactions.keys():
                            money.append([tk.StringVar(), tk.IntVar()])
                            money[-1][0].set(person)
                            money[-1][1].set(sub_transactions[person])

                            elem_money_sub_frame = tk.Frame(elem_money_frame, bg=bg_for_main_frame)
                            elemMoneyEntry = tk.Entry(elem_money_sub_frame, font=("Comicsans", 12, "bold"), textvariable=money[-1][1], width=8, readonlybackground=bg_for_entry)
                            elemPersonSelect = ttk.Combobox(elem_money_sub_frame, textvariable=money[-1][0], values=["Me"]+list(self.data_read_from_file["unsettled"].keys()), width=13, font=("Helvetica", 15))
                            money_sign.append(int(math.copysign(1,money[-1][1].get())))
                            photo = ImageTk.PhotoImage(delete_image)
                            elemDelBtn = tk.Button(elem_money_sub_frame, image=photo, bd=0, bg=bg_for_main_frame, command=lambda unique_person=person, transaction_index=transaction_sl_no:self.delete_person_from_title_borrow(unique_person, transaction_index))
                            elemDelBtn.image = photo

                            elemMoneyEntry.config(state='readonly')
                            elemPersonSelect.config(state='disabled')
                            self.set_transaction_color(money[-1][1], money_sign[-1], elemMoneyEntry)
                            money_entry_element.append([elemMoneyEntry, elemPersonSelect])
                            delBtnList.append(elemDelBtn)

                            elem_money_sub_frame.pack()
                            elemMoneyEntry.grid(row=0,column=0, padx=(30,5), pady=5, ipady=2, ipadx=10)
                            elemPersonSelect.grid(row=0,column=1, padx=(5,30), pady=5)

                    self.transaction_buttons.append([elemEditConfBtn, elemDelResetBtn, delBtnList])
                    self.transaction_variables.append([title, money, money_sign])
                    self.transaction_inputs.append([elemTitle, money_entry_element])
                    transaction_sl_no+=1
        self.canvas.yview_moveto(0.0)

    def add_return_transaction(self):
        self.add_return_variables = []
        self.add_return_elements = []

        if self.return_popup:
            self.return_popup.destroy()
        self.return_popup = tk.Toplevel(self.main_frame, bg=bg_for_left_frame)
        self.return_popup.title(f"Add Return Transaction - {date_selected.get()}")
        self.return_popup.geometry("500x300+500+200")
        self.return_popup.resizable(0, 0)

        # Scrollable Canvas Setup
        canvas = tk.Canvas(self.return_popup, bg=bg_for_left_frame)
        scrollbar = tk.Scrollbar(self.return_popup, orient="vertical", command=canvas.yview, width=20)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollable_frame = tk.Frame(canvas, bg=bg_for_left_frame)
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        scrollable_frame.bind("<Configure>",lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_window, width=e.width))

        entry_frame = tk.Frame(scrollable_frame, bg=bg_for_left_frame)
        personLabel = tk.Label(entry_frame, text="Person", font=("Verdana", 12), bg=bg_for_left_frame)
        amountLabel = tk.Label(entry_frame, text="Amount", font=("Verdana", 12), bg=bg_for_left_frame)
        photo = ImageTk.PhotoImage(delete_image)
        space_occupier = tk.Button(entry_frame, image=photo, bg=bg_for_left_frame, bd=0, activebackground=bg_for_left_frame)
        self.add_return_label = [personLabel, amountLabel, space_occupier] 
        
        add_btn_frame = tk.Frame(scrollable_frame, bg=bg_for_left_frame)
        addTitleBtn = tk.Button(add_btn_frame, text="+ Add Person", font=("Verdana", 10), command= lambda:self.add_person_to_return_add(entry_frame))
        saveBtn = tk.Button(add_btn_frame, text="Save Changes", font=("Verdana", 10), command=self.save_return_add)

        # Packing elements into scrollable frame
        add_btn_frame.pack(pady=15)
        addTitleBtn.grid(row=0, column=0, ipadx=10, ipady=2, padx=10)
        saveBtn.grid(row=0, column=1, ipadx=10, ipady=2, padx=10)
        entry_frame.pack(pady=5, padx=20)
    
    def add_person_to_return_add(self, entry_frame):
        variables = [tk.StringVar(), tk.IntVar()]
        personSelect = ttk.Combobox(entry_frame, textvariable=variables[0], values=list(self.data_read_from_file["unsettled"].keys()), width=13, font=("Helvetica", 13))
        amountEntry = tk.Entry(entry_frame, font=("Times New Roman", 15), textvariable=variables[1], width=8, justify='center')

        photo = ImageTk.PhotoImage(delete_image)
        deleteBtn = tk.Button(entry_frame, image=photo, bg=bg_for_left_frame, bd=0, command=lambda index=len(self.add_return_variables): self.del_person_from_return_add(index))
        deleteBtn.image = photo

        self.add_return_variables.append(variables)
        self.add_return_elements.append([personSelect, amountEntry, deleteBtn])

        row_no = len(self.add_return_elements)
        self.add_return_label[0].grid(row=0, column=0, padx=(0,30), pady=5)
        self.add_return_label[1].grid(row=0, column=1, padx=30, pady=5)
        self.add_return_label[2].grid(row=0, column=2, padx=(30,0), pady=5)
        personSelect.grid(row=row_no, column=0, padx=(0,30), pady=5)
        amountEntry.grid(row=row_no, column=1, padx=30, pady=5)
        deleteBtn.grid(row=row_no, column=2, padx=(30,0), pady=5)

        personSelect.config(state='readonly')
        variables[0].set(select_text)
    
    def del_person_from_return_add(self, sl_no):
        for elem in self.add_return_elements[sl_no]:
            elem.destroy()
        self.add_return_variables[sl_no] = None
        self.add_return_elements[sl_no] = None

        for i,x in enumerate(self.add_return_elements):
            if x:
                return
        self.add_return_elements = []
        self.add_return_variables = []
        for elem in self.add_return_label:
            elem.grid_forget()
    
    def save_return_add(self):
        data_to_be_written = read_data()
        try:
            data_by_date = data_to_be_written["transaction"][date_selected.get()]
        except KeyError:
            data_to_be_written["transaction"][date_selected.get()] = {special_keys[0]: {special_keys[1]: {},special_keys[2]: {}},special_keys[3]: {},special_keys[4]: 0}
            data_by_date = {special_keys[0]: {special_keys[1]: {},special_keys[2]: {}},special_keys[3]: {},special_keys[4]: 0}
        
        data_list_by_date = list(data_by_date[special_keys[3]].items())
        existing_persons = []
        for key, _ in data_list_by_date:
            existing_persons.append(key)
        
        if (self.add_return_variables):
            person_list = []
            for variables in self.add_return_variables:
                if variables:
                    person, amount = variables
                    if person.get()==select_text or not amount.get():
                        msg.showerror(f"Empty Fields", "Fill out all fields else delete the fields!")
                        return
                    person_list.append(person.get())
                    data_to_be_written["transaction"][date_selected.get()][special_keys[3]][person.get()] = amount.get()

            if len(person_list)!=len(set(person_list)):
                msg.showerror("Duplicate Persons", "Remove same person from multiple fields")
                return
            for person in person_list:
                if person in existing_persons:
                    msg.showerror(f"Duplicate Person ({person})", "This person already exists on this day's return transaction!")
                    return
        else:
           self.return_popup.destroy()

        self.write_data(data_to_be_written)
        self.return_popup.destroy()
        self.show_transactions(date_selected.get())

    def add_borrow_transaction(self):
        self.add_borrow_variables = []
        self.add_borrow_elements = []

        if self.borrow_popup:
            self.borrow_popup.destroy()
        self.borrow_popup = tk.Toplevel(self.main_frame, bg=bg_for_left_frame)
        self.borrow_popup.title(f"Add Borrow Transaction - {date_selected.get()}")
        self.borrow_popup.geometry("500x300+500+200")
        self.borrow_popup.resizable(0, 0)

        # Scrollable Canvas Setup
        canvas = tk.Canvas(self.borrow_popup, bg=bg_for_left_frame)
        scrollbar = tk.Scrollbar(self.borrow_popup, orient="vertical", command=canvas.yview, width=20)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollable_frame = tk.Frame(canvas, bg=bg_for_left_frame)
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        scrollable_frame.bind("<Configure>",lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_window, width=e.width))

        # Your transaction input fields
        self.null_var_for_add_borrow = tk.StringVar()
        self.person_var_for_add_borrow = tk.StringVar()
        self.null_var_for_add_borrow.set(select_text)
        self.person_var_for_add_borrow.set(select_text)

        nullLabel = tk.Label(scrollable_frame, text="Choose Transaction Type", font=("Verdana", 15), bg=bg_for_left_frame)
        nullSelect = ttk.Combobox(scrollable_frame, textvariable=self.null_var_for_add_borrow, values=null_options, font=("Helvetica", 13), justify='center')
        personLabel = tk.Label(scrollable_frame, text="Choose Person", font=("Verdana", 15), bg=bg_for_left_frame)
        personSelect = ttk.Combobox(scrollable_frame, textvariable=self.person_var_for_add_borrow, values=list(self.data_read_from_file["unsettled"].keys()), font=("Helvetica", 13), justify='center')
        entry_frame = tk.Frame(scrollable_frame, bg=bg_for_left_frame)
        add_btn_frame = tk.Frame(scrollable_frame, bg=bg_for_left_frame)
        addTitleBtn = tk.Button(add_btn_frame, text="+ Add Title", font=("Verdana", 10), command= lambda:self.add_title_to_borrow_add(entry_frame))
        saveBtn = tk.Button(add_btn_frame, text="Save Changes", font=("Verdana", 10), command=self.save_borrow_add)

        # Packing elements into scrollable frame
        nullLabel.pack(pady=(10, 5))
        nullSelect.pack(padx=20, ipady=5, fill='x')
        personLabel.pack(pady=(10, 5))
        personSelect.pack(padx=50, ipady=5, fill='x')
        add_btn_frame.pack(pady=15)
        addTitleBtn.grid(row=0, column=0, ipadx=10, ipady=2, padx=10)
        saveBtn.grid(row=0, column=1, ipadx=10, ipady=2, padx=10)
        entry_frame.pack(pady=5, fill='x')

        nullSelect.config(state='readonly')
        personSelect.config(state='readonly')

    def add_title_to_borrow_add(self, entry_frame):
        variables = [tk.StringVar(), tk.IntVar()]

        entry_sub_frame = tk.Frame(entry_frame, bg=bg_for_left_frame)
        titleEntry = tk.Entry(entry_sub_frame, font=("Times New Roman", 15), textvariable=variables[0], justify='center')
        amountEntry = tk.Entry(entry_sub_frame, font=("Times New Roman", 15), textvariable=variables[1], width=8, justify='center')
        photo = ImageTk.PhotoImage(delete_image)
        deleteBtn = tk.Button(entry_sub_frame, image=photo, bg=bg_for_left_frame, bd=0, command=lambda index=len(self.add_borrow_variables): self.del_title_from_borrow_add(index))
        deleteBtn.image = photo

        entry_sub_frame.pack(pady=5)
        titleEntry.grid(row=0, column=0, padx=10)
        amountEntry.grid(row=0, column=1, padx=10)
        deleteBtn.grid(row=0, column=3, padx=10)

        self.add_borrow_variables.append(variables)
        self.add_borrow_elements.append(entry_sub_frame)
    
    def del_title_from_borrow_add(self, sl_no):
        self.add_borrow_elements[sl_no].destroy()
        self.add_borrow_variables[sl_no] = None
        self.add_borrow_elements[sl_no] = None

        for i,x in enumerate(self.add_borrow_elements):
            if x:
                return
        self.add_borrow_elements = []
        self.add_borrow_variables = []

    def save_borrow_add(self):
        data_to_be_written = read_data()
        try:
            data_by_date = data_to_be_written["transaction"][date_selected.get()]
        except KeyError:
            data_to_be_written["transaction"][date_selected.get()] = {special_keys[0]: {special_keys[1]: {},special_keys[2]: {}},special_keys[3]: {},special_keys[4]: 0}
            data_by_date = {special_keys[0]: {special_keys[1]: {},special_keys[2]: {}},special_keys[3]: {},special_keys[4]: 0}
        
        try:
            null_value = special_keys[1+null_options.index(self.null_var_for_add_borrow.get())]
        except ValueError:
            msg.showerror(f"No Transaction Type", "Transaction Type is a required field!")
            return

        data_list_by_date = list(data_by_date[special_keys[0]][null_value].items())
        existing_persons = []
        for key, _ in data_list_by_date:
            existing_persons.append(key)
        
        new_person = self.person_var_for_add_borrow.get()
        if new_person==select_text:
            msg.showerror(f"No Person Selected", "Person for borrow transaction can't be empty!")
            return

        if (self.add_borrow_variables):
            title_list = []
            title_dict = {}
            for variables in self.add_borrow_variables:
                if variables:
                    title, amount = variables
                    title_value = title.get().replace('#', '').strip()
                    if title_value=='' or not amount.get():
                        msg.showerror(f"Empty Fields", "Fill out all fields else delete the fields!")
                        return
                    title_dict[title_value] = amount.get()
                    title_list.append(title_value)
            if len(title_list)!=len(set(title_list)):
                msg.showerror(f"Duplicate Titles", "Remove same titles from multiple fields")
                return
            
            if new_person in existing_persons:
                for title in title_list:
                    if title in data_to_be_written["transaction"][date_selected.get()][special_keys[0]][null_value][new_person].keys():
                        msg.showerror(f"Duplicate Titles", "This title for this person's transaction already exists!")
                        return
                data_to_be_written["transaction"][date_selected.get()][special_keys[0]][null_value][new_person].update(title_dict)
            else:
                data_to_be_written["transaction"][date_selected.get()][special_keys[0]][null_value][new_person] = title_dict

        else:
           self.borrow_popup.destroy()

        self.write_data(data_to_be_written)
        self.borrow_popup.destroy()
        self.show_transactions(date_selected.get())

    def add_general_transaction(self):
        self.add_transaction_variables = []
        self.add_transaction_elements = []

        if self.transaction_popup:
            self.transaction_popup.destroy()
        self.transaction_popup = tk.Toplevel(self.main_frame, bg=bg_for_left_frame)
        self.transaction_popup.title(f"Add General Transaction - {date_selected.get()}")
        self.transaction_popup.geometry("500x300+500+200")
        self.transaction_popup.resizable(0, 0)

        # Scrollable Canvas Setup
        canvas = tk.Canvas(self.transaction_popup, bg=bg_for_left_frame)
        scrollbar = tk.Scrollbar(self.transaction_popup, orient="vertical", command=canvas.yview, width=20)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollable_frame = tk.Frame(canvas, bg=bg_for_left_frame)
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        scrollable_frame.bind("<Configure>",lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_window, width=e.width))

        # Your transaction input fields
        self.title_var_for_add_transaction = tk.StringVar()
        self.amount_var_for_add_transaction = tk.IntVar()

        titleLabel = tk.Label(scrollable_frame, text="Enter Title", font=("Verdana", 15), bg=bg_for_left_frame)
        titleEntry = tk.Entry(scrollable_frame, font=("Times New Roman", 15), textvariable=self.title_var_for_add_transaction, justify='center')
        moneyLabel = tk.Label(scrollable_frame, text="Enter Amount", font=("Verdana", 15), bg=bg_for_left_frame)
        moneyEntry = tk.Entry(scrollable_frame, font=("Times New Roman", 15), textvariable=self.amount_var_for_add_transaction, width=8, justify='center')
        entry_frame = tk.Frame(scrollable_frame, bg=bg_for_left_frame)
        btn_frame = tk.Frame(scrollable_frame, bg=bg_for_left_frame)
        addPersonBtn = tk.Button(btn_frame, text="+ Add Person", font=("Verdana", 10), command= lambda:self.add_person_to_transaction_add(moneyEntry, entry_frame, btn_frame))
        saveBtn = tk.Button(btn_frame, text="Save Changes", font=("Verdana", 10), command=self.save_transaction_add)

        # Packing elements into scrollable frame
        titleLabel.pack(pady=(10, 5))
        titleEntry.pack(padx=20, ipady=5, fill='x')
        moneyLabel.pack(pady=(10, 5))
        moneyEntry.pack(padx=20, ipady=5)
        btn_frame.pack(pady=15)
        addPersonBtn.grid(row=0, column=0, ipadx=10, ipady=2, padx=10)
        saveBtn.grid(row=0, column=1, ipadx=10, ipady=2, padx=10)
    
    def add_person_to_transaction_add(self, moneyEntry, entry_frame, add_btn_frame):
        moneyEntry.pack_forget()
        entry_frame.pack(pady=5, fill='x')
        variables = [tk.StringVar(), tk.IntVar()]
        variables[0].set(select_text)
        combobox_values = list(self.data_read_from_file["unsettled"].keys())
        if len(self.add_transaction_variables):
            combobox_values.insert(0, "Me")

        entry_sub_frame = tk.Frame(entry_frame, bg=bg_for_left_frame)
        personSelect = ttk.Combobox(entry_sub_frame, textvariable=variables[0], values=combobox_values, width=13, font=("Helvetica", 13))
        amountEntry = tk.Entry(entry_sub_frame, font=("Times New Roman", 15), textvariable=variables[1], width=8, justify='center')
        photo = ImageTk.PhotoImage(delete_image)
        deleteBtn = tk.Button(entry_sub_frame, image=photo, bg=bg_for_left_frame, bd=0, command=lambda index=len(self.add_transaction_variables): self.del_person_from_transaction_add(index, moneyEntry, entry_frame, add_btn_frame))
        deleteBtn.image = photo

        entry_sub_frame.pack(pady=5)
        personSelect.grid(row=0, column=0, padx=10)
        amountEntry.grid(row=0, column=1, padx=10)
        deleteBtn.grid(row=0, column=3, padx=10)

        personSelect.config(state='readonly')
        self.add_transaction_variables.append(variables)
        self.add_transaction_elements.append(entry_sub_frame)
    
    def del_person_from_transaction_add(self, sl_no, moneyEntry, entry_frame, add_btn_frame):
        self.add_transaction_elements[sl_no].destroy()
        self.add_transaction_variables[sl_no] = None
        self.add_transaction_elements[sl_no] = None

        for i,x in enumerate(self.add_transaction_elements):
            if x:
                combobox = x.winfo_children()[0]
                combobox_values = list(self.data_read_from_file["unsettled"].keys())
                combobox.config(values=combobox_values)
                if self.add_transaction_variables[i][0].get() == "Me":
                    self.add_transaction_variables[i][0].set(select_text)
                return
        self.add_transaction_elements = []
        self.add_transaction_variables = []
        entry_frame.pack_forget()
        add_btn_frame.pack_forget()
        moneyEntry.pack(padx=20, ipady=5)
        add_btn_frame.pack(pady=15)

    def save_transaction_add(self):
        data_to_be_written = read_data()
        try:
            data_by_date = data_to_be_written["transaction"][date_selected.get()]
        except KeyError:
            data_to_be_written["transaction"][date_selected.get()] = {special_keys[0]: {special_keys[1]: {},special_keys[2]: {}},special_keys[3]: {},special_keys[4]: 0}
            data_by_date = {special_keys[0]: {special_keys[1]: {},special_keys[2]: {}},special_keys[3]: {},special_keys[4]: 0}
        
        data_list_by_date = list(data_by_date.items())
        existing_titles = []
        for key, _ in data_list_by_date:
            if not key.startswith('#'):
                existing_titles.append(key)
        
        new_title = self.title_var_for_add_transaction.get().strip().replace('#','')
        if new_title=='':
            msg.showerror(f"No Title", "Title for transaction can't be empty!")
            return
        

        if (self.add_transaction_variables):
            person_list = []
            person_dict = {}
            for variables in self.add_transaction_variables:
                if variables:
                    person, amount = variables
                    if person.get()==select_text or not amount.get():
                        msg.showerror(f"Empty Fields", "Fill out all fields else delete the fields!")
                        return
                    person_dict[person.get()] = amount.get()
                    person_list.append(person.get())
            if len(person_list)!=len(set(person_list)):
                msg.showerror(f"Duplicate Person", "Remove same person names from multiple fields")
                return
            
            if new_title in existing_titles:
                data = data_to_be_written["transaction"][date_selected.get()][new_title]
                if type(data)==int:
                    data = {"Me": data}
                    data_to_be_written["transaction"][date_selected.get()][new_title] = data
                for person in person_list:
                    if person in data.keys():
                        msg.showerror(f"Duplicate Persons", "This person for this title's transaction already exists!")
                        return
                data_to_be_written["transaction"][date_selected.get()][new_title].update(person_dict)
            else:
                data_to_be_written["transaction"][date_selected.get()][new_title] = person_dict

        else:
            if new_title in existing_titles:
                data = data_to_be_written["transaction"][date_selected.get()][new_title]
                if type(data)==dict and "Me" not in data.keys():
                    data_to_be_written["transaction"][date_selected.get()][new_title].update({"Me": self.amount_var_for_add_transaction.get()})
                else:
                    msg.showerror(f"Duplicate Title ({new_title})", "This title already exists on this day's transaction")
                    return
            else:
                data_to_be_written["transaction"][date_selected.get()][new_title] = self.amount_var_for_add_transaction.get() 
        
        for key, _ in data_list_by_date:
            if key.startswith('#'):
                del data_to_be_written["transaction"][date_selected.get()][key]

        for key, value in data_list_by_date:
            if key.startswith('#'):
                data_to_be_written["transaction"][date_selected.get()][key] = value
        self.write_data(data_to_be_written)
        self.transaction_popup.destroy()
        self.show_transactions(date_selected.get())
   
    def set_transaction_color(self, amount, sign, element, neutralize=False):
        amount_value = abs(amount.get())*sign
        if neutralize:
            element.config(fg='black')
            amount.set(amount_value)
        else:
            if amount_value>0:
                element.config(fg=colors["red"])
            else:
                element.config(fg=colors["green"])
            amount.set(abs(amount_value))
    
    def setDate(self, flag):
        if flag:
            self.dateInp.selection_set(datetime.today())
        else:
            date_selected.set(self.dateInp.selection_get().strftime(date_format))
            self.date_popup.destroy()
            self.show_transactions(date_selected.get())
    
    def edit_save_transaction(self, transaction_sl_no, net_sl_no):
        edit_ok_btn = self.transaction_buttons[transaction_sl_no][0]
        del_cancel_btn = self.transaction_buttons[transaction_sl_no][1]
        delBtns = self.transaction_buttons[transaction_sl_no][2]
        inputs = self.transaction_inputs[transaction_sl_no]

        if edit_ok_btn.cget('text') == 'Edit':
            #changing colors of all other inputs that are not editable now
            self.cancel_editing_others()

            #changing button labels
            edit_ok_btn.config(text='Save')
            del_cancel_btn.config(text='Cancel')

            #enabling the delete buttons for all
            if len(delBtns)>1:
                for delBtn in delBtns:
                    delBtn.grid(row=0, column=2, padx=(5, 30))

            #making the inputs editable
            for inp in inputs:
                if type(inp)==list:
                    for sub_inp in inp:
                        sub_inp[0].config(state='normal')
                        sub_inp[1].config(state='readonly')
                else:
                    inp.config(state='normal')

            #changing colors of the entry inputs that are editable now
            _, money_var, money_sign = self.transaction_variables[transaction_sl_no]
            if type(money_var)==list:
                for j in range(len(money_var)):
                    self.set_transaction_color(money_var[j][1], money_sign[j], inputs[1][j][0], neutralize=True)
            else:
                self.set_transaction_color(money_var, money_sign, inputs[1], neutralize=True)

        else:
            global data_to_be_written
            data_to_be_written = self.data_read_from_file

            transaction_data_by_date = data_to_be_written["transaction"][date_selected.get()]
            transaction_list_by_date = list(transaction_data_by_date.items())
            transaction_to_be_edited = transaction_list_by_date[net_sl_no]
            title_var, money_var, money_sign = self.transaction_variables[transaction_sl_no]

            title_stripped = title_var.get().replace('#', '').strip()
            if title_stripped in transaction_data_by_date.keys() and title_stripped!=transaction_to_be_edited[0]:
                msg.showerror(f"Duplicate Title ({title_stripped})", "Change the title of the transaction!")
                return

            edit_ok_btn.config(text='Edit')
            del_cancel_btn.config(text='Delete')

            if type(money_var)==list:
                money_dict = {}
                for person, _ in money_var:
                    money_dict[person.get()] = 0
                for person, amount in money_var:
                    money_dict[person.get()] += amount.get()
                
                if list(money_dict.keys()) == ["Me"]:
                    money_dict = money_dict["Me"]

                edited_transaction = (title_stripped, money_dict)
            else:
                edited_transaction = (title_stripped, money_var.get())
            

            for key, _ in transaction_list_by_date[net_sl_no+1:]:
                del data_to_be_written["transaction"][date_selected.get()][key]
            
            del data_to_be_written["transaction"][date_selected.get()][transaction_to_be_edited[0]]
            data_to_be_written["transaction"][date_selected.get()][edited_transaction[0]] = edited_transaction[1]

            for key, value in transaction_list_by_date[net_sl_no+1:]:
                data_to_be_written["transaction"][date_selected.get()][key] = value

            if edited_transaction!=transaction_to_be_edited:
                self.write_data(data_to_be_written)
            self.show_transactions(date_selected.get())
    
    def cancel_delete_transaction(self, transaction_sl_no, net_sl_no=None, called_from_other_function=False):
        edit_ok_btn = self.transaction_buttons[transaction_sl_no][0]
        del_cancel_btn = self.transaction_buttons[transaction_sl_no][1]
        delBtns = self.transaction_buttons[transaction_sl_no][2]
        inputs = self.transaction_inputs[transaction_sl_no]

        if del_cancel_btn.cget('text') == 'Cancel' or called_from_other_function:
            edit_ok_btn.config(text='Edit')
            del_cancel_btn.config(text='Delete')

            #disabling the delete buttons for all
            for delBtn in delBtns:
                delBtn.grid_forget()
            
            for inp in inputs:
                if type(inp)==list:
                    for sub_inp in inp:
                        sub_inp[0].config(state='readonly')
                        sub_inp[1].config(state='disabled')
                else:
                    inp.config(state='readonly')
            
            self.restore_data_on_cancel()
            if type(inputs[1]) == list:
                for i, sub_inp in enumerate(inputs[1]):
                    self.set_transaction_color(self.transaction_variables[transaction_sl_no][1][i][1], self.transaction_variables[transaction_sl_no][2][i], sub_inp[0])
            else:
                self.set_transaction_color(self.transaction_variables[transaction_sl_no][1], self.transaction_variables[transaction_sl_no][2], inputs[1])

        else:
            global data_to_be_written
            data_to_be_written = self.data_read_from_file

            transaction_data_by_date = data_to_be_written["transaction"][date_selected.get()]
            transaction_list_by_date = list(transaction_data_by_date.items())
            transaction_to_be_deleted = transaction_list_by_date[net_sl_no]

            if msg.askyesno(f"Delete Transaction ({transaction_to_be_deleted[0]})", "Are you sure you want to delete this transaction?"):
                del data_to_be_written["transaction"][date_selected.get()][transaction_to_be_deleted[0]]
                self.write_data(data_to_be_written)
                self.show_transactions(date_selected.get())
    
    def edit_save_borrow(self, borrow_sl_no, sl_no_options):
        edit_ok_btn = self.borrow_buttons[borrow_sl_no][0]
        del_cancel_btn = self.borrow_buttons[borrow_sl_no][1]
        delBtns = self.borrow_buttons[borrow_sl_no][2]
        inputs = self.borrow_inputs[borrow_sl_no]

        if edit_ok_btn.cget('text') == 'Edit':
            #changing colors of all other inputs that are not editable now
            self.cancel_editing_others()

            #changing button labels
            edit_ok_btn.config(text='Save')
            del_cancel_btn.config(text='Cancel')

            #enabling the delete options for each
            if len(delBtns)>1:
                for delBtn in delBtns:
                    delBtn.grid(row=0, column=2, padx=(5, 30))

            #making the inputs editable
            for inp in inputs:
                if type(inp)==list:
                    for sub_inp in inp:
                        sub_inp[0].config(state='normal')
                        sub_inp[1].config(state='normal')
                else:
                    inp.config(state='readonly')

            _, money_var, money_sign, isNull = self.borrow_variables[borrow_sl_no]
            if not isNull:
                for j in range(len(money_var)):
                    self.set_transaction_color(money_var[j][1], money_sign[j], inputs[1][j][1], neutralize=True)

        else:
            global data_to_be_written
            data_to_be_written = self.data_read_from_file
            transaction_data_by_date = data_to_be_written["transaction"][date_selected.get()]
            borrow_data_by_date = transaction_data_by_date[special_keys[0]]
            person_var, money_var, money_sign, isNull = self.borrow_variables[borrow_sl_no]

            category = special_keys[1] if isNull else special_keys[2]
            borrow_category_list = list(borrow_data_by_date[category].items())
            category_sl_no = sl_no_options[int(not isNull)]
            borrow_to_be_edited = borrow_category_list[category_sl_no]

            new_title_list = []
            for title, _ in money_var:
                title_stripped = title.get().strip()
                new_title_list.append(title_stripped)
            if len(new_title_list)!=len(set(new_title_list)):
                msg.showerror("Duplicate Title", "Remove same titles from the transaction!")
                return
            
            person_check_list = []
            for variables in self.borrow_variables:
                if (isNull==variables[3]):
                    person_check_list.append(variables[0].get())
            if len(person_check_list)!=len(set(person_check_list)):
                msg.showerror(f"Duplicate Person ({person_var.get()})", "Remove same person names from same group of transactions!")
                return

            edit_ok_btn.config(text='Edit')
            del_cancel_btn.config(text='Delete')

            #disabling the delete options for each
            for delBtn in delBtns:
                delBtn.grid_forget()

            money_dict = {}
            for title, amount in money_var:
                amount_value = amount.get()
                if isNull:amount_value=abs(amount_value)
                money_dict[title.get().strip()] = amount_value
            edited_borrow = (person_var.get(), money_dict)

            for key, _ in borrow_category_list[category_sl_no+1:]:
                del data_to_be_written["transaction"][date_selected.get()][special_keys[0]][category][key]

            del data_to_be_written["transaction"][date_selected.get()][special_keys[0]][category][borrow_to_be_edited[0]]
            data_to_be_written["transaction"][date_selected.get()][special_keys[0]][category][edited_borrow[0]] = edited_borrow[1]

            for key, value in borrow_category_list[category_sl_no+1:]:
                data_to_be_written["transaction"][date_selected.get()][special_keys[0]][category][key] = value

            if edited_borrow!=borrow_to_be_edited:
                self.write_data(data_to_be_written)
            self.show_transactions(date_selected.get())
    
    def cancel_delete_borrow(self, borrow_sl_no, sl_no_options=None, called_from_other_function=False):
        edit_ok_btn = self.borrow_buttons[borrow_sl_no][0]
        del_cancel_btn = self.borrow_buttons[borrow_sl_no][1]
        delBtns = self.borrow_buttons[borrow_sl_no][2]
        inputs = self.borrow_inputs[borrow_sl_no]

        if del_cancel_btn.cget('text') == 'Cancel' or called_from_other_function:
            edit_ok_btn.config(text='Edit')
            del_cancel_btn.config(text='Delete')
            
            for inp in inputs:
                if type(inp)==list:
                    for sub_inp in inp:
                        sub_inp[0].config(state='readonly')
                        sub_inp[1].config(state='readonly')
                else:
                    inp.config(state='disabled')
            
            #disabling the delete options for each
            for delBtn in delBtns:
                delBtn.grid_forget()

            self.restore_data_on_cancel()
            for i, sub_inp in enumerate(inputs[1]):
                if not self.borrow_variables[borrow_sl_no][3]:
                    self.set_transaction_color(self.borrow_variables[borrow_sl_no][1][i][1], self.borrow_variables[borrow_sl_no][2][i], sub_inp[1])
        
        else:
            global data_to_be_written
            data_to_be_written = self.data_read_from_file
            transaction_data_by_date = data_to_be_written["transaction"][date_selected.get()]
            borrow_data_by_date = transaction_data_by_date[special_keys[0]]
            isNull = self.borrow_variables[borrow_sl_no][3]

            category = special_keys[1] if isNull else special_keys[2]
            borrow_category_list = list(borrow_data_by_date[category].items())
            category_sl_no = sl_no_options[int(not isNull)]
            borrow_to_be_deleted = borrow_category_list[category_sl_no]

            if msg.askyesno(f"Delete Transaction ({borrow_to_be_deleted[0]})", "Are you sure you want to delete this transaction?"):
                del data_to_be_written["transaction"][date_selected.get()][special_keys[0]][category][borrow_to_be_deleted[0]]
                self.write_data(data_to_be_written)
                self.show_transactions(date_selected.get())

    def edit_save_return(self, return_sl_no):
        edit_ok_btn = self.return_buttons[return_sl_no][0]
        del_cancel_btn = self.return_buttons[return_sl_no][1]
        inputs = self.return_inputs[return_sl_no]

        if edit_ok_btn.cget('text') == 'Edit':
            self.cancel_editing_others()

            #changing button labels
            edit_ok_btn.config(text='Save')
            del_cancel_btn.config(text='Cancel')

            #making the inputs editable
            inputs[0].config(state='readonly')
            inputs[1].config(state='normal')
            
            variables = self.return_variables[return_sl_no]
            self.set_transaction_color(variables[1], variables[2], inputs[1], neutralize=True)
        else:
            global data_to_be_written
            data_to_be_written = self.data_read_from_file

            return_data_by_date = data_to_be_written["transaction"][date_selected.get()][special_keys[3]]
            return_list_by_date = list(return_data_by_date.items())
            return_to_be_edited = return_list_by_date[return_sl_no]
            person_var, money_var, money_sign = self.return_variables[return_sl_no]

            person_check_list = []
            for variables in self.return_variables:
                person_check_list.append(variables[0].get())
            
            if len(person_check_list)!=len(set(person_check_list)):
                msg.showerror(f"Duplicate Person ({person_var.get()})", "Remove same person names from same group of transactions!")
                return

            edit_ok_btn.config(text='Edit')
            del_cancel_btn.config(text='Delete')
            edited_transaction = (person_var.get(), money_var.get())

            for key, _ in return_list_by_date[return_sl_no+1:]:
                del data_to_be_written["transaction"][date_selected.get()][special_keys[3]][key]
            
            del data_to_be_written["transaction"][date_selected.get()][special_keys[3]][return_to_be_edited[0]]
            data_to_be_written["transaction"][date_selected.get()][special_keys[3]][edited_transaction[0]] = edited_transaction[1]

            for key, value in return_list_by_date[return_sl_no+1:]:
                data_to_be_written["transaction"][date_selected.get()][special_keys[3]][key] = value

            if edited_transaction!=return_to_be_edited:
                self.write_data(data_to_be_written)
            self.show_transactions(date_selected.get())

    def cancel_delete_return(self, return_sl_no, called_from_other_function=False):
        edit_ok_btn = self.return_buttons[return_sl_no][0]
        del_cancel_btn = self.return_buttons[return_sl_no][1]
        inputs = self.return_inputs[return_sl_no]

        if del_cancel_btn.cget('text') == 'Cancel' or called_from_other_function:
            edit_ok_btn.config(text='Edit')
            del_cancel_btn.config(text='Delete')
            
            inputs[0].config(state='disabled')
            inputs[1].config(state='readonly')

            self.restore_data_on_cancel()
            self.set_transaction_color(self.return_variables[return_sl_no][1], self.return_variables[return_sl_no][2], inputs[1])
        
        else:
            global data_to_be_written
            data_to_be_written = self.data_read_from_file
            transaction_data_by_date = data_to_be_written["transaction"][date_selected.get()]
            return_data_by_date = transaction_data_by_date[special_keys[3]]
            return_data_list = list(return_data_by_date.items())
            return_to_be_deleted = return_data_list[return_sl_no]

            if msg.askyesno(f"Delete Transaction ({return_to_be_deleted[0]})", "Are you sure you want to delete this transaction?"):
                del data_to_be_written["transaction"][date_selected.get()][special_keys[3]][return_to_be_deleted[0]]
                self.write_data(data_to_be_written)
                self.show_transactions(date_selected.get())
        
    def restore_data_on_cancel(self):
        data = self.data_read_from_file["transaction"]
        data_to_be_restored = data[date_selected.get()]
        for i, variables in enumerate(self.transaction_variables):
            title_var, money_var, _ = variables
            title = list(data_to_be_restored.keys())[i]
            title_var.set(title)
            data_for_title = data_to_be_restored[title]
            
            if type(money_var)==list:
                for j, sub_variables in enumerate(money_var):
                    person_var, amount_var = sub_variables
                    person = list(data_for_title.keys())[j]
                    person_var.set(person)
                    amount_var.set(abs(data_for_title[person]))
            else:
                money_var.set(abs(data_for_title))
        
        data_borrow = data_to_be_restored[special_keys[0]]
        null_sl_no = 0
        not_null_sl_no = 0
        for i, variables in enumerate(self.borrow_variables):
            person_var, money_var, _, isNull = variables
            if isNull:
                category = special_keys[1]
                category_sl_no = null_sl_no
                null_sl_no+=1
            else:
                category = special_keys[2]
                category_sl_no = not_null_sl_no
                not_null_sl_no+=1
            
            person = list(data_borrow[category].keys())[category_sl_no]
            person_var.set(person)
            data_for_person = data_borrow[category][person]

            for j, sub_variables in enumerate(money_var):
                title_var, amount_var = sub_variables
                title = list(data_for_person.keys())[j]
                title_var.set(title)
                amount_var.set(abs(data_for_person[title]))
        
        data_return = data_to_be_restored[special_keys[3]]
        for i, variables in enumerate(self.return_variables):
            person_var, money_var, _ = variables
            person = list(data_return.keys())[i]
            person_var.set(person)
            money_var.set(abs(data_return[person]))

    def cancel_editing_others(self):
        for i in range(len(self.transaction_inputs)):
            self.cancel_delete_transaction(i, called_from_other_function=True)
        
        for i in range(len(self.borrow_inputs)):
            self.cancel_delete_borrow(i, called_from_other_function=True)
        
        for i in range(len(self.return_inputs)):
            self.cancel_delete_return(i, called_from_other_function=True)

    def calculate_total(self, data):
        if date_selected.get() in list(data["transaction"].keys()):
            total = 0
            data_to_be_totaled = data["transaction"][date_selected.get()]
            for x in data_to_be_totaled:
                transaction = data_to_be_totaled[x]
                if x==special_keys[0]:
                    transaction_not_null = transaction[special_keys[2]]
                    for value in transaction_not_null.values():
                        total+=sum(value.values())
                elif x==special_keys[3]:
                    total+=sum(transaction.values())
                elif x==special_keys[4]:
                    data["transaction"][date_selected.get()][x] = total
                else:
                    if type(transaction)==int:
                        total+=transaction
                    else:
                        total+=sum(transaction.values())
        return data

    def write_data(self, data):
        data = self.calculate_total(data)
        write_data(data)
        data["unsettled"] = calculate_unsettled()
        write_data(data)


if __name__ == "__main__":
    try:
        transaction_data = read_data()
    except FileNotFoundError:
        print("Main Data File Doesn't Exist!")
        print("Creating the File...")
        try:
            transaction_data = read_data("../../transaction_book_data.json")
        except FileNotFoundError:
            print("Backup Data File Doesn't Exist too!")
            print("Creating the File...")
            write_data({"unsettled":{}, "transaction":{}})
            print("Empty data.json and transaction_book_data.json file created successfully!")
        else:
            write_data(retrieve=True)
            print("Data retrieved from transaction_book_data.json to new data.json file successfully!")
    obj = BroilerPlate()
    obj.show()