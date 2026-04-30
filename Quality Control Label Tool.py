import os
import datetime
from datetime import datetime
import time
import sys
import tkinter as tk
from tkinter import messagebox
from PIL import Image
import zpl
from zebra import Zebra
# Import writer class from csv module
from csv import writer

# Create File
try:
    if not os.path.exists(fr'QC_Data.csv'):
        header = ['Barcode', 'Date', 'Time', 'Location']
        with open(fr'QC_Data.csv', 'w', newline='') as f_object:
            writer_object = writer(f_object)
            writer_object.writerow(header)
            f_object.close()
except Exception as ex:
    messagebox.showerror("FATAL ERROR", f"Failed to create CSV file:\n{ex}\n\nPlease Notify Your Nearest Shift Manager")
    sys.exit(1)


class QualityControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quality Control Label Tool")
        self.root.geometry("450x300")
        self.root.resizable(False, False)
        
        self.scanned_barcodes = []
        self.location = tk.StringVar()
        self.barcode = tk.StringVar()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        title = tk.Label(self.root, text="Quality Control Label Tool", font=("Arial", 14, "bold"))
        title.pack(pady=15)
        
        # Location
        loc_frame = tk.Frame(self.root)
        loc_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(loc_frame, text="Location:", width=12, anchor=tk.W).pack(side=tk.LEFT)
        tk.Entry(loc_frame, textvariable=self.location, width=30).pack(side=tk.LEFT)
        
        # Barcode
        bar_frame = tk.Frame(self.root)
        bar_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(bar_frame, text="Barcode:", width=12, anchor=tk.W).pack(side=tk.LEFT)
        barcode_entry = tk.Entry(bar_frame, textvariable=self.barcode, width=30, font=("Arial", 11))
        barcode_entry.pack(side=tk.LEFT)
        barcode_entry.bind("<Return>", lambda e: self.print_label())
        
        # Status
        self.status = tk.Label(self.root, text="", font=("Arial", 9), fg="#27ae60")
        self.status.pack(pady=10)
        
        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Print", command=self.print_label, width=12, bg="#3498db", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Clear", command=self.clear_fields, width=12, bg="#95a5a6", fg="white").pack(side=tk.LEFT, padx=5)
        
    def print_label(self):
        location = self.location.get().strip()
        barcode = self.barcode.get().strip()
        
        if not location or not barcode:
            messagebox.showwarning("Warning", "Please enter location and barcode")
            return
        
        # Check for duplicate
        if barcode in self.scanned_barcodes:
            messagebox.showwarning("Duplicate", "This barcode has already been scanned!")
            return
        
        self.scanned_barcodes.append(barcode)
        
        now = datetime.now()
        date_str = now.strftime("%d/%m/%Y")
        time_str = now.strftime("%H:%M:%S")
        
        # Save to CSV
        try:
            with open(fr'QC_Data.csv', 'a', newline='') as f_object:
                writer_object = writer(f_object)
                writer_object.writerow([barcode, date_str, time_str, location])
                f_object.close()
        except Exception as ex:
            messagebox.showerror("Error", f"Failed to save:\n{ex}")
            return
        
        # Print label
        try:
            z = Zebra()
            Q = z.getqueues()
            z.setqueue(Q[0])
            z.setup()
            z.output(f"""^XA
^FX Top section with logo, name and address.
^CF0,60

^FO120,50^FDQuality Checked^FS
^CF0,40
^FO40,115^FDDate: {date_str}^FS
^FO40,155^FDLocation: {location}^FS

^FX Third section with bar code.
^BY3,2,140
^FO40,210^BC^FD{barcode}^FS
^XZ""")
            
            self.status.config(text=f"✓ Label printed: {barcode}")
            self.barcode.set("")
            
        except Exception as ex:
            messagebox.showerror("Printer Error", f"Failed to print:\n{ex}")
    
    def clear_fields(self):
        self.location.set("")
        self.barcode.set("")
        self.status.config(text="")


if __name__ == "__main__":
    root = tk.Tk()
    app = QualityControlApp(root)
    root.mainloop()
    