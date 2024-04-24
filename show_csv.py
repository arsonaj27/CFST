import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import csv

class CSVViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Viewer")

        # Create a Treeview widget
        self.tree = ttk.Treeview(root)
        self.tree["columns"] = ("#1", "#2")  # Columns for the treeview
        self.tree.heading("#0", text="Row Number")
        self.tree.heading("#1", text="Strain Value")
        self.tree.heading("#2", text="Stress Value")

        self.tree.pack(fill="both", expand=True)

        # Add a scrollbar to the treeview
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Load and display the CSV data
        self.load_csv("strain_stress_value.csv")

        # Add a button to download CSV file
        self.download_button = ttk.Button(root, text="Download CSV", command=self.download_csv)
        self.download_button.pack()

    def load_csv(self, filename):
        with open(filename, "r") as file:
            csv_reader = csv.reader(file)
            for i, row in enumerate(csv_reader):
                if i == 0:  # Skip header row
                    continue
                self.tree.insert("", "end", text=f"{i}", values=row)

    def download_csv(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filename:
            with open(filename, "w", newline="") as file:
                csv_writer = csv.writer(file)
                for child in self.tree.get_children():
                    row = self.tree.item(child)["values"]
                    csv_writer.writerow(row)

def main():
    root = tk.Tk()
    app = CSVViewerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()