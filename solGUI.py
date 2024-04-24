import pandas as pd
from tkinter import *
from tkinter import messagebox, filedialog

def apriori(transactions, min_support):
    item_counts = {}
    all_frequent_items = [] # Array of dictionaries


    for transaction in transactions:
        unique_items = set(transaction)  # Get unique items in each transaction
        for item in unique_items:
            if item in item_counts:
                item_counts[item] += 1
            else:
                item_counts[item] = 1
    
    frequent_items = {frozenset([item]): support for item, support in item_counts.items() if support >= min_support}
    


    all_frequent_items.append(dict(frequent_items)) 
    
    frequent_item_sets = list(frequent_items.keys())
    

    k = 2

    while True:
        candidate_item_sets = []
        for i in range(len(frequent_item_sets)):
            for j in range(i + 1, len(frequent_item_sets)):
                joined_set = frequent_item_sets[i].union(frequent_item_sets[j])
                
                if len(joined_set) == k and joined_set not in candidate_item_sets:
                    candidate_item_sets.append(joined_set)
        
        item_counts = {item_set: 0 for item_set in candidate_item_sets}
        for transaction in transactions:
            unique_items = set(transaction)  # Get unique items in each transaction
            for item_set in candidate_item_sets:
                if item_set.issubset(unique_items):
                    item_counts[item_set] += 1
        
        frequent_item_sets = [item_set for item_set, support in item_counts.items() if support >= min_support]
        
        if not frequent_item_sets:
            break
        
        frequent_items.clear()
        for item_set in frequent_item_sets:
            frequent_items[item_set] = item_counts[item_set]
            #all_frequent_items_dict[item_set] = item_counts[item_set]

        all_frequent_items.append(dict(frequent_items)) 
        k += 1

    return frequent_items, all_frequent_items

def generate_association_rules(frequent_itemsets):
    association_rules = []

    for itemset in frequent_itemsets:
        if len(itemset) > 1:  # Only generate rules if itemset has more than one item
            antecedent_candidates = []
            generate_antecedents(itemset, 0, [], antecedent_candidates)
            for antecedent in antecedent_candidates:
                consequent = itemset.difference(antecedent)
                if(len(consequent) == 0 or len(antecedent) == 0): continue
                association_rules.append((frozenset(antecedent), frozenset(consequent), itemset))

    return association_rules

def generate_antecedents(itemset, start, current, antecedent_candidates):
    if start == len(itemset):
        return
    for i in range(start, len(itemset)):
        current.append(list(itemset)[i])
        antecedent_candidates.append(current[:])
        generate_antecedents(itemset, i + 1, current, antecedent_candidates)
        current.pop()

def get_confidence(association_rules, all_frequent_items):
    for i, (antecedent, consequent, item) in enumerate(association_rules):
        itemSize = len(item)
        antecedentSize = len(antecedent)
        confidence = (all_frequent_items[itemSize - 1][item] / all_frequent_items[antecedentSize - 1][antecedent]) 
        association_rules[i] = (antecedent, consequent, item, confidence)
    return association_rules

def generate_output(file_path, min_support, min_confidence, percentage, problem):
    try:
        if problem == 1:
            data = pd.read_csv(file_path)
        elif problem == 2:
            data = pd.read_excel(file_path)

        num_records = int(len(data) * (percentage / 100))
        data = data.head(num_records)

        if problem == 1:
            transactions = data.groupby('TransactionNo')['Items'].apply(list).tolist()
        elif problem == 2:
            transactions = data.values.tolist()
            filtered_transactions = []
            for transaction in transactions:
                valid_transaction = True
                for i in range(len(transaction)):
                    sport = ""
                    if i == 0: 
                        sport = "Tennis"
                    elif i == 1: 
                        sport = "Basketball"
                    elif i == 2:
                        sport = "Swimming"
                    if 65 <= transaction[i] <= 74:
                        transaction[i] = "Ranking " + sport 
                    elif 75 <= transaction[i] <= 84:
                        transaction[i] = "Top level " + sport
                    elif 85 <= transaction[i] <= 100:
                        transaction[i] = "Superior " + sport
                    else:
                        valid_transaction = False
                        break 
                if valid_transaction:
                    filtered_transactions.append(transaction)
            transactions = filtered_transactions


        frequent_items, all_frequent_items = apriori(transactions, min_support)

        association_rules = generate_association_rules(frequent_items)
        association_rules = get_confidence(association_rules, all_frequent_items)

        output = ""
        for i in range(len(all_frequent_items)):
            output += f"Level: {i + 1}\n"
            if(i == len(all_frequent_items) - 1):
                output += "Frequent Item Sets:\n"
            for itemset, support in all_frequent_items[i].items():
                output += f"{set(itemset)} : {support}\n"
            output += "########################\n"

        output += "\nStrong Association Rules with Confidence:\n"
        for antecedent, consequent, _, confidence, in association_rules:
            if(confidence >= min_confidence):
                output += f"{set(antecedent)} => {set(consequent)} : {confidence * 100:.2f}% \n"

        return output
    except Exception as e:
        return str(e)

def run_program():
    def browse_file():
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
        file_entry.delete(0, END)
        file_entry.insert(END, file_path)

    def generate_output_command():
        try:
            file_path = file_entry.get()
            percentage = int(percentage_entry.get())
            min_support = int(min_support_entry.get())
            min_confidence = float(min_confidence_entry.get()) / 100  # Divide by 100 to convert to percentage
            problem = int(problem_var.get())

            output_text.delete('1.0', END)  # Clear previous output
            output = generate_output(file_path, min_support, min_confidence, percentage, problem)
            output_text.insert(END, output)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    window = Tk()
    window.title("Apriori Algorithm")
    window.configure(background="#f0f0f0")

    problem_label = Label(window, text="Select Problem:")
    problem_label.grid(row=0, column=0, padx=5, pady=5)
    problem_var = StringVar(window)
    problem_var.set("1")  # Default value
    problem_dropdown = OptionMenu(window, problem_var, "1", "2")
    problem_dropdown.config(bg="#ffffff")
    problem_dropdown.grid(row=0, column=1, padx=5, pady=5)

    file_label = Label(window, text="Select CSV or Excel File:")
    file_label.grid(row=1, column=0, padx=5, pady=5)
    file_entry = Entry(window)
    file_entry.grid(row=1, column=1, padx=5, pady=5)
    browse_button = Button(window, text="Browse", command=browse_file)
    browse_button.grid(row=1, column=2, padx=5, pady=5)

    percentage_label = Label(window, text="Percentage of Data (%):")
    percentage_label.grid(row=2, column=0, padx=5, pady=5)
    percentage_entry = Entry(window)
    percentage_entry.grid(row=2, column=1, padx=5, pady=5)

    min_support_label = Label(window, text="Minimum Support Count:")
    min_support_label.grid(row=3, column=0, padx=5, pady=5)
    min_support_entry = Entry(window)
    min_support_entry.grid(row=3, column=1, padx=5, pady=5)

    min_confidence_label = Label(window, text="Minimum Confidence (%):")
    min_confidence_label.grid(row=4, column=0, padx=5, pady=5)
    min_confidence_entry = Entry(window)
    min_confidence_entry.grid(row=4, column=1, padx=5, pady=5)

    generate_button = Button(window, text="Generate Output", command=generate_output_command)
    generate_button.grid(row=5, columnspan=3, padx=5, pady=5)

    output_text = Text(window, height=20, width=50, bg="#ffffff", fg="blue")
    output_text.grid(row=6, columnspan=3, padx=5, pady=5, sticky="nsew")  # Use sticky to make the widget expand

    scrollbar = Scrollbar(window, command=output_text.yview)
    scrollbar.grid(row=6, column=3, sticky='ns')
    output_text.config(yscrollcommand=scrollbar.set)

    
    window.grid_rowconfigure(6, weight=1)
    window.grid_columnconfigure(0, weight=1)
    window.grid_columnconfigure(1, weight=1)
    window.grid_columnconfigure(2, weight=1)
    window.grid_columnconfigure(3, weight=0)  # Adjusted column weight for the scrollbar
    
    window.mainloop()

run_program()
