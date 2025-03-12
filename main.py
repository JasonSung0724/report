import tkinter as tk
from tkinter import filedialog, messagebox
from generate_report import generate_report


def select_input_file():
    file_path = filedialog.askopenfilename(title="選擇輸入的 Excel 檔案", filetypes=(("Excel files", "*.xls;*.xlsx"), ("All files", "*.*")))
    input_file_var.set(file_path)


def output_file():
    file_path = filedialog.asksaveasfilename(title="輸出檔案名", defaultextension=".xlsx", filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*")))
    output_file_var.set(file_path)


def generate_report_handler():
    input_path = input_file_var.get()
    output_path = output_file_var.get()

    if not input_path or not output_path:
        messagebox.showerror("錯誤", "請選擇輸入檔案路徑和輸出檔案檔名")
        return

    try:
        generate_report(input_path, output_path)
        messagebox.showinfo("成功", f"報告已成功生成！\n儲存於：{output_path}")
    except Exception as e:
        messagebox.showerror("錯誤", f"生成報告時發生錯誤：{e}")


root = tk.Tk()
root.title("訂單整理")

input_file_var = tk.StringVar()
tk.Label(root, text="選擇輸入檔案：").grid(row=0, column=0, padx=10, pady=5, sticky="e")
tk.Entry(root, textvariable=input_file_var, width=50).grid(row=0, column=1, padx=10, pady=5)
tk.Button(root, text="瀏覽", command=select_input_file).grid(row=0, column=2, padx=10, pady=5)

output_file_var = tk.StringVar()
tk.Label(root, text="輸出檔案檔名：").grid(row=1, column=0, padx=10, pady=5, sticky="e")
tk.Entry(root, textvariable=output_file_var, width=50).grid(row=1, column=1, padx=5, pady=5)

tk.Button(root, text="生成報告", command=generate_report_handler, bg="green", fg="white").grid(row=2, column=1, pady=10)

root.mainloop()
