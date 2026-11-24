import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
import os
from datetime import date, datetime, timedelta

# ==============================
# BUS PASS EXPIRY TRACKER
# ==============================

APP_TITLE = "Bus Pass Expiry Tracker"
DATA_FILE = "bus_passes.json"
TODAY = date.today()


# ==============================
# DATA MANAGEMENT
# ==============================

def get_status(expiry_date):
    expiry = datetime.strptime(expiry_date, "%Y-%m-%d").date()
    days = (expiry - date.today()).days

    if days < 0:
        return "Expired"
    elif days <= 7:
        return "Expiring Soon"
    return "Active"


def generate_sample_data():
    names = [
        "Ravi", "Kiran", "Priya", "Arun", "Sita",
        "Rahul", "Sneha", "Vijay", "Anjali", "Manoj",
        "Divya", "Ramesh", "Pooja", "Sai", "Kavya",
        "Ajay", "Neha", "Varun", "Meena", "Rohit",
        "Suresh", "Lakshmi", "Nikhil", "Swathi", "Teja",
        "Harsha", "Keerthi", "Abhi", "Sanjay", "Deepika",
        "Charan", "Mounika", "Praveen", "Anusha", "Naveen",
        "Bhavya", "Gopal", "Sravani", "Mahesh", "Akash",
        "Rani", "Tarun", "Akhila", "Vamsi", "Sowmya",
        "Dinesh", "Lavanya", "Karthik", "Shiva", "Nandini"
    ]

    records = []

    # Different expiry dates for testing all statuses
    offsets = [-30, -15, -5, -1, 0, 1, 3, 5, 7,
               8, 10, 15, 20, 30, 45, 60, 90]

    for i, name in enumerate(names):
        expiry = date.today() + timedelta(
            days=offsets[i % len(offsets)]
        )

        start = expiry - timedelta(days=90)

        records.append({
            "pass_id": f"BP{i + 101}",
            "name": name,
            "phone": f"987654{1000 + i}",
            "route": f"Route {(i % 10) + 1}",
            "pass_type": "Student",
            "start_date": start.isoformat(),
            "expiry_date": expiry.isoformat()
        })

    return records


def load_data():
    if not os.path.exists(DATA_FILE):
        records = generate_sample_data()
        save_data(records)
        return records

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            records = json.load(file)

        if not isinstance(records, list):
            raise ValueError("Invalid data format")

        for record in records:
            required = [
                "pass_id", "name", "phone", "route",
                "pass_type", "start_date", "expiry_date"
            ]
            if not isinstance(record, dict):
                raise ValueError("Invalid record")
            if any(key not in record for key in required):
                raise ValueError("Missing record fields")

            datetime.strptime(record["start_date"], "%Y-%m-%d")
            datetime.strptime(record["expiry_date"], "%Y-%m-%d")

        return records

    except (json.JSONDecodeError, ValueError, TypeError, OSError) as error:
        messagebox.showwarning(
            "Storage Warning",
            f"Could not read the data file.\n{error}\n"
            "Starting with an empty dataset."
        )
        return []


def save_data(records):
    temp_file = DATA_FILE + ".tmp"

    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4)

    os.replace(temp_file, DATA_FILE)


# ==============================
# MAIN APPLICATION
# ==============================

class BusPassApp:

    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1150x720")
        self.root.minsize(900, 600)

        self.records = load_data()

        self.setup_style()
        self.create_header()
        self.create_dashboard()
        self.create_form()
        self.create_search()
        self.create_table()
        self.create_footer()

        self.refresh_table()
        self.update_dashboard()

    # ==========================
    # STYLE
    # ==========================

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            rowheight=30,
            font=("Arial", 10)
        )

        style.configure(
            "Treeview.Heading",
            font=("Arial", 10, "bold")
        )

        style.configure(
            "TButton",
            font=("Arial", 10, "bold"),
            padding=6
        )

    # ==========================
    # HEADER
    # ==========================

    def create_header(self):
        header = tk.Frame(
            self.root,
            bg="#123456",
            height=85
        )
        header.pack(fill="x")

        tk.Label(
            header,
            text="BUS PASS EXPIRY TRACKER",
            font=("Arial", 22, "bold"),
            fg="white",
            bg="#123456"
        ).pack(pady=(15, 2))

        tk.Label(
            header,
            text="Manage your bus passes smartly and never miss an expiry date",
            font=("Arial", 10),
            fg="white",
            bg="#123456"
        ).pack()

    # ==========================
    # DASHBOARD
    # ==========================

    def create_dashboard(self):
        frame = tk.Frame(self.root, bg="#edf2f7")
        frame.pack(fill="x", padx=15, pady=12)

        self.total_label = self.create_card(
            frame, "Total Passes", "#2563eb"
        )

        self.active_label = self.create_card(
            frame, "Active Passes", "#16a34a"
        )

        self.soon_label = self.create_card(
            frame, "Expiring Soon", "#d97706"
        )

        self.expired_label = self.create_card(
            frame, "Expired Passes", "#dc2626"
        )

    def create_card(self, parent, title, color):
        card = tk.Frame(
            parent,
            bg=color,
            padx=20,
            pady=12
        )
        card.pack(side="left", expand=True, fill="x", padx=5)

        tk.Label(
            card,
            text=title,
            bg=color,
            fg="white",
            font=("Arial", 10, "bold")
        ).pack()

        label = tk.Label(
            card,
            text="0",
            bg=color,
            fg="white",
            font=("Arial", 22, "bold")
        )
        label.pack()

        return label

    def update_dashboard(self):
        total = len(self.records)
        active = 0
        soon = 0
        expired = 0

        for record in self.records:
            status = get_status(record["expiry_date"])

            if status == "Active":
                active += 1
            elif status == "Expiring Soon":
                soon += 1
            else:
                expired += 1

        self.total_label.config(text=str(total))
        self.active_label.config(text=str(active))
        self.soon_label.config(text=str(soon))
        self.expired_label.config(text=str(expired))

    # ==========================
    # ADD PASS FORM
    # ==========================

    def create_form(self):
        frame = ttk.LabelFrame(
            self.root,
            text=" Add New Bus Pass ",
            padding=10
        )
        frame.pack(fill="x", padx=20, pady=5)

        self.entries = {}

        fields = [
            ("Pass ID", "pass_id"),
            ("Student Name", "name"),
            ("Phone Number", "phone"),
            ("Route", "route"),
            ("Pass Type", "pass_type"),
            ("Start Date (YYYY-MM-DD)", "start_date"),
            ("Expiry Date (YYYY-MM-DD)", "expiry_date")
        ]

        for index, (label, key) in enumerate(fields):
            row = index // 4
            col = (index % 4) * 2

            ttk.Label(frame, text=label).grid(
                row=row, column=col,
                sticky="w", padx=5, pady=5
            )

            entry = ttk.Entry(frame, width=19)
            entry.grid(
                row=row, column=col + 1,
                padx=5, pady=5
            )

            self.entries[key] = entry

        # Default dates
        self.entries["start_date"].insert(
            0, date.today().isoformat()
        )

        self.entries["expiry_date"].insert(
            0, (date.today() + timedelta(days=90)).isoformat()
        )

        ttk.Button(
            frame,
            text="Add Bus Pass",
            command=self.add_pass
        ).grid(
            row=2, column=0,
            columnspan=2, padx=5, pady=10
        )

        ttk.Button(
            frame,
            text="Clear Form",
            command=self.clear_form
        ).grid(
            row=2, column=2,
            columnspan=2, padx=5, pady=10
        )

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    # ==========================
    # VALIDATION
    # ==========================

    def validate_pass(self, data):
        for key, value in data.items():
            if not value:
                raise ValueError(
                    f"{key.replace('_', ' ').title()} cannot be empty."
                )

        if not data["pass_id"].isalnum():
            raise ValueError(
                "Pass ID must contain only letters and numbers."
            )

        if len(data["name"]) > 60:
            raise ValueError("Student name is too long.")

        if not all(
            char.isalpha() or char.isspace()
            for char in data["name"]
        ):
            raise ValueError(
                "Student name must contain only letters and spaces."
            )

        if not data["phone"].isdigit() or len(data["phone"]) != 10:
            raise ValueError(
                "Enter a valid 10-digit phone number."
            )

        if len(data["route"]) > 50:
            raise ValueError("Route name is too long.")

        if data["pass_type"] not in [
            "Student", "General", "Monthly", "Quarterly"
        ]:
            raise ValueError("Invalid pass type.")

        try:
            start = date.fromisoformat(data["start_date"])
            expiry = date.fromisoformat(data["expiry_date"])
        except ValueError:
            raise ValueError(
                "Dates must be valid and use YYYY-MM-DD format."
            )

        if expiry < start:
            raise ValueError(
                "Expiry date cannot be before start date."
            )

        if any(
            record["pass_id"].lower() == data["pass_id"].lower()
            for record in self.records
        ):
            raise ValueError("This Pass ID already exists.")

    # ==========================
    # ADD RECORD
    # ==========================

    def add_pass(self):
        data = {
            key: entry.get().strip()
            for key, entry in self.entries.items()
        }

        try:
            self.validate_pass(data)

            self.records.append(data)
            save_data(self.records)

            messagebox.showinfo(
                "Success",
                "Bus pass added successfully!"
            )

            self.clear_form()
            self.refresh_table()
            self.update_dashboard()

        except ValueError as error:
            messagebox.showerror("Validation Error", str(error))

        except OSError as error:
            self.records.pop()
            messagebox.showerror(
                "Storage Error",
                f"Could not save record: {error}"
            )

    # ==========================
    # SEARCH
    # ==========================

    def create_search(self):
        frame = tk.Frame(self.root)
        frame.pack(fill="x", padx=20, pady=8)

        ttk.Label(
            frame,
            text="Search Pass:"
        ).pack(side="left", padx=5)

        self.search_entry = ttk.Entry(frame, width=35)
        self.search_entry.pack(side="left", padx=5)

        self.search_entry.bind(
            "<KeyRelease>",
            lambda event: self.refresh_table()
        )

        ttk.Button(
            frame,
            text="Show All",
            command=self.show_all
        ).pack(side="left", padx=5)

        ttk.Button(
            frame,
            text="Export CSV",
            command=self.export_csv
        ).pack(side="right", padx=5)

        ttk.Button(
            frame,
            text="Delete Selected",
            command=self.delete_pass
        ).pack(side="right", padx=5)

    def show_all(self):
        self.search_entry.delete(0, tk.END)
        self.refresh_table()

    # ==========================
    # TABLE
    # ==========================

    def create_table(self):
        frame = ttk.LabelFrame(
            self.root,
            text=" Bus Pass Records ",
            padding=8
        )
        frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=5
        )

        columns = (
            "pass_id", "name", "phone", "route",
            "pass_type", "start_date", "expiry_date",
            "days_left", "status"
        )

        self.tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "pass_id": "Pass ID",
            "name": "Student Name",
            "phone": "Phone",
            "route": "Route",
            "pass_type": "Pass Type",
            "start_date": "Start Date",
            "expiry_date": "Expiry Date",
            "days_left": "Days Left",
            "status": "Status"
        }

        widths = {
            "pass_id": 75,
            "name": 105,
            "phone": 100,
            "route": 85,
            "pass_type": 85,
            "start_date": 95,
            "expiry_date": 95,
            "days_left": 70,
            "status": 105
        }

        for column in columns:
            self.tree.heading(
                column,
                text=headings[column]
            )
            self.tree.column(
                column,
                width=widths[column],
                anchor="center"
            )

        scrollbar = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(side="right", fill="y")

        self.tree.tag_configure(
            "Active", foreground="green"
        )
        self.tree.tag_configure(
            "Expiring Soon", foreground="#d97706"
        )
        self.tree.tag_configure(
            "Expired", foreground="red"
        )

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        keyword = self.search_entry.get().lower().strip()

        for record in self.records:
            status = get_status(record["expiry_date"])

            searchable = " ".join([
                record["pass_id"],
                record["name"],
                record["phone"],
                record["route"],
                record["pass_type"],
                status
            ]).lower()

            if keyword and keyword not in searchable:
                continue

            expiry = date.fromisoformat(record["expiry_date"])
            days_left = (expiry - date.today()).days

            self.tree.insert(
                "",
                tk.END,
                values=(
                    record["pass_id"],
                    record["name"],
                    record["phone"],
                    record["route"],
                    record["pass_type"],
                    record["start_date"],
                    record["expiry_date"],
                    days_left,
                    status
                ),
                tags=(status,)
            )

    # ==========================
    # DELETE RECORD
    # ==========================

    def delete_pass(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning(
                "Warning",
                "Please select a bus pass first."
            )
            return

        values = self.tree.item(selected[0], "values")
        pass_id = values[0]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete bus pass {pass_id}?"
        )

        if not confirm:
            return

        old_records = self.records[:]
        self.records = [
            record for record in self.records
            if record["pass_id"] != pass_id
        ]

        try:
            save_data(self.records)
        except OSError as error:
            self.records = old_records
            messagebox.showerror(
                "Storage Error", str(error)
            )
            return

        self.refresh_table()
        self.update_dashboard()

        messagebox.showinfo(
            "Deleted",
            "Bus pass deleted successfully."
        )

    # ==========================
    # CSV EXPORT
    # ==========================

    def export_csv(self):
        if not self.records:
            messagebox.showwarning(
                "No Data",
                "There are no records to export."
            )
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile="bus_pass_report.csv"
        )

        if not path:
            return

        try:
            fields = [
                "pass_id", "name", "phone", "route",
                "pass_type", "start_date", "expiry_date",
                "days_left", "status"
            ]

            with open(
                path, "w", newline="", encoding="utf-8-sig"
            ) as file:
                writer = csv.DictWriter(
                    file, fieldnames=fields
                )
                writer.writeheader()

                for record in self.records:
                    expiry = date.fromisoformat(
                        record["expiry_date"]
                    )
                    days = (expiry - date.today()).days

                    row = record.copy()
                    row["days_left"] = days
                    row["status"] = get_status(
                        record["expiry_date"]
                    )

                    writer.writerow(row)

            messagebox.showinfo(
                "Export Successful",
                f"Report saved successfully:\n{path}"
            )

        except OSError as error:
            messagebox.showerror(
                "Export Error", str(error)
            )

    # ==========================
    # FOOTER
    # ==========================

    def create_footer(self):
        footer = tk.Frame(
            self.root,
            bg="#123456",
            height=35
        )
        footer.pack(fill="x", side="bottom")

        tk.Label(
            footer,
            text="GreenFuture Hack | Project #53 | "
                 "Bus Pass Expiry Tracker",
            fg="white",
            bg="#123456",
            font=("Arial", 9)
        ).pack(pady=8)


# ==============================
# START APPLICATION
# ==============================

if __name__ == "__main__":
    root = tk.Tk()
    app = BusPassApp(root)
    root.mainloop()