import os
import json
from tkinter import filedialog, messagebox

def export_data(data):
    save_dir = os.path.join(os.getcwd(), "save")
    os.makedirs(save_dir, exist_ok=True)


    file_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        initialdir=save_dir,
        filetypes=[("JSON 文件", "*.json")],
        title="导出信息"
    )

    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("导出成功", f"信息已保存到\n{file_path}")



