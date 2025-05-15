import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msg
import tkcalendar as tk_cal
from datetime import datetime
import json
import os
import math
import copy

colors = {'green':'#598C58', 'red':'#FF0B55'}
bg_colors = ('#E5D9F2','#C4D9FF','#578FCA', '#FDFAF6', '#F1E7E7', '#9ACBD0')
fg_colors = ('#27548A',)
date_format = "%d %b, %Y"
instruction_str = [("(Green -> He/She owes you money)", "(Green -> You have been paid)"), ("(Red -> You owe him/her money)", "(Red -> You have paid)")]
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

special_keys = ("#Borrow", "#Null", "#Not-Null", "#Return", "#Total")

def read_data():
    with open(os.path.dirname(__file__)+"/data.json") as f:
        return json.load(f)

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
        self.mainloop()

class HomeWindow:
    def __init__(self, main_frame):
        global instructions
        instructions[0].set(instruction_str[0][0])
        instructions[1].set(instruction_str[1][0])
        self.main_frame = main_frame
        self.create_elememts()
    
    def create_elememts(self):
        tk.Label(self.main_frame, text="Hello Home").pack()

class UnsettledWindow:
    def __init__(self, main_frame):
        global instructions
        instructions[0].set(instruction_str[0][0])
        instructions[1].set(instruction_str[1][0])
        self.main_frame = main_frame
        self.create_elememts()
    
    def create_elememts(self):
        tk.Label(self.main_frame, text="Hello Unset").pack()

class AddTransWindow:
    def __init__(self, main_frame):
        global instructions
        instructions[0].set(instruction_str[0][1])
        instructions[1].set(instruction_str[1][1])
        self.main_frame = main_frame
        self.popup = None
        if date_selected.get()=="":
            date_selected.set(datetime.today().strftime(date_format))
        self.create_elememts()
        self.show_elements()
    
    def create_elememts(self):
        # Canvas For Scrollbar
        self.canvas = tk.Canvas(self.main_frame, bg=bg_for_main_frame)
        self.scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.main_scrollable_frame = tk.Frame(self.canvas, bg=bg_for_main_frame)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.main_scrollable_frame, anchor='nw')

        self.main_scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

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
        self.addBorrBtn = tk.Button(self.options_frame, text="Add Borrowings", font=("Robota", 13), cursor="hand2")
        self.addRetBtn = tk.Button(self.options_frame, text="Add Returns", font=("Robota", 13), cursor="hand2")
        self.addTrnBtn = tk.Button(self.options_frame, text="Add Other Transactions", font=("Robota", 13), cursor="hand2")

        self.dataLbl = tk.Label(self.input_frame, text="Your Transactions on this day", font=("Robota",15), bg=bg_for_main_frame)
        self.data_frame = tk.Frame(self.main_scrollable_frame, bg=bg_for_main_frame)
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

    def showDatePopup(self):
        if self.popup:
            self.popup.destroy()
        self.popup = tk.Toplevel(self.main_frame)
        self.popup.title("Date Picker")
        self.popup.geometry("300x300+500+200")
        dateSelected = datetime.strptime(date_selected.get(), date_format).date()
        self.dateInp = tk_cal.Calendar(self.popup, selectmode='day', date_pattern='dd-mm-yyyy', width=10, bg=bg_for_main_frame, borderwidth=2,
                                       day=dateSelected.day, month=dateSelected.month, year=dateSelected.year)
        self.btn_frame = tk.Frame(self.popup)
        self.dateOkBtn = tk.Button(self.btn_frame, text="Set", font=("Robota", 10),command=lambda:self.setDate(0))
        self.dateCancelBtn = tk.Button(self.btn_frame, text="Reset", font=("Robota", 10),command=lambda:self.setDate(1))
        self.dateInp.pack()
        self.btn_frame.pack(pady=10)
        self.dateOkBtn.grid(row=0,column=0,ipadx=20,padx=15)
        self.dateCancelBtn.grid(row=0,column=1,ipadx=20,padx=15)
    
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
                            elemTitle = tk.Label(self.data_frame, font=("Times New Roman", 15), text="Someone paid for you", bg=bg_for_main_frame, fg=fg_for_sub_heading)
                            elemTitle.pack(anchor='w', pady=(10,0))
                        elif (not case_not_null_title and not isNull):
                            case_not_null_title=1
                            elemTitle = tk.Label(self.data_frame, font=("Times New Roman", 15), text="Someone lend/borrowed money", bg=bg_for_main_frame, fg=fg_for_sub_heading)
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
                        self.borrow_buttons.append([elemEditConfBtn, elemDelResetBtn])

                        for title in transactions[x][human].keys():
                            money.append([tk.StringVar(), tk.IntVar()])
                            money[-1][0].set(title)
                            money[-1][1].set(transactions[x][human][title])
                            money_sign.append(int(math.copysign(1,money[-1][1].get())))

                            elem_sub_frame = tk.Frame(elem_title_frame, bg=bg_for_main_frame)
                            elemTitle = tk.Entry(elem_sub_frame, font=("Times New Roman", 15), textvariable=money[-1][0], width=20, readonlybackground=bg_for_entry)
                            elemMoney = tk.Entry(elem_sub_frame, font=("Comicsans", 12, "bold"), textvariable=money[-1][1], width=8, readonlybackground=bg_for_entry)

                            elem_sub_frame.pack()
                            elemTitle.grid(row=0, column=0, padx=(30, 5), pady=5, ipadx=10, ipady=2)
                            elemMoney.grid(row=0, column=1, padx=(5, 30), pady=5, ipadx=10, ipady=2)

                            elemTitle.config(state='readonly')
                            elemMoney.config(state='readonly')
                            money_entry_element.append([elemTitle, elemMoney])

                            if not isNull:
                                self.set_transaction_color(money[-1][1], money_sign[-1], elemMoney)

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
                    self.transaction_buttons.append([elemEditConfBtn, elemDelResetBtn])

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
                            money_sign.append(int(math.copysign(1,money[-1][1].get())))

                            elem_money_sub_frame = tk.Frame(elem_money_frame, bg=bg_for_main_frame)
                            elemMoneyEntry = tk.Entry(elem_money_sub_frame, font=("Comicsans", 12, "bold"), textvariable=money[-1][1], width=8, readonlybackground=bg_for_entry)
                            elemPersonSelect = ttk.Combobox(elem_money_sub_frame, textvariable=money[-1][0], values=["Me"]+list(self.data_read_from_file["unsettled"].keys()), width=13, font=("Helvetica", 15))

                            elemMoneyEntry.config(state='readonly')
                            elemPersonSelect.config(state='disabled')
                            self.set_transaction_color(money[-1][1], money_sign[-1], elemMoneyEntry)
                            money_entry_element.append([elemMoneyEntry, elemPersonSelect])

                            elem_money_sub_frame.pack()
                            elemMoneyEntry.grid(row=0,column=0, padx=(30,5), pady=5, ipady=2, ipadx=10)
                            elemPersonSelect.grid(row=0,column=1, padx=(5,30), pady=5)

                    self.transaction_variables.append([title, money, money_sign])
                    self.transaction_inputs.append([elemTitle, money_entry_element])
                    transaction_sl_no+=1
    
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
            self.popup.destroy()
            self.show_transactions(date_selected.get())
    
    def edit_save_transaction(self, transaction_sl_no, net_sl_no):
        edit_ok_btn = self.transaction_buttons[transaction_sl_no][0]
        del_cancel_btn = self.transaction_buttons[transaction_sl_no][1]
        inputs = self.transaction_inputs[transaction_sl_no]

        if edit_ok_btn.cget('text') == 'Edit':
            #changing colors of all other inputs that are not editable now
            self.change_colors_of_cancelled()

            #changing button labels
            edit_ok_btn.config(text='Save')
            del_cancel_btn.config(text='Cancel')

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
        inputs = self.transaction_inputs[transaction_sl_no]

        if del_cancel_btn.cget('text') == 'Cancel' or called_from_other_function:
            edit_ok_btn.config(text='Edit')
            del_cancel_btn.config(text='Delete')
            
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
        inputs = self.borrow_inputs[borrow_sl_no]

        if edit_ok_btn.cget('text') == 'Edit':
            #changing colors of all other inputs that are not editable now
            self.change_colors_of_cancelled()

            #changing button labels
            edit_ok_btn.config(text='Save')
            del_cancel_btn.config(text='Cancel')

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
            self.change_colors_of_cancelled()

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
                    amount_var.set(data_for_title[person])
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

    def change_colors_of_cancelled(self):
        for i in range(len(self.transaction_inputs)):
            self.cancel_delete_transaction(i, called_from_other_function=True)
        
        for i in range(len(self.borrow_inputs)):
            self.cancel_delete_borrow(i, called_from_other_function=True)
        
        for i in range(len(self.return_inputs)):
            self.cancel_delete_return(i, called_from_other_function=True)

    def calculate_total(self):
        data = self.data_read_from_file["transaction"]
        data_to_be_totaled = data[date_selected.get()]
        total = 0

        for x in data_to_be_totaled:
            transaction = data_to_be_totaled[x]
            if x==special_keys[0]:
                transaction_not_null = transaction[special_keys[2]]
                for value in transaction_not_null.values():
                    total+=sum(value.values())
            elif x==special_keys[3]:
                total+=sum(transaction.values())
            elif x==special_keys[4]:
                self.data_read_from_file["transaction"][date_selected.get()][x] = total
            else:
                if type(transaction)==int:
                    total+=transaction
                else:
                    total+=sum(transaction.values())

    def write_data(self, data):
        self.calculate_total()
        with open(os.path.dirname(__file__)+"/data.json", 'w') as f:
            return json.dump(data, f, indent=4)

if __name__ == "__main__":
    obj = BroilerPlate()
    obj.show()


#sub-edit options needs to be added now