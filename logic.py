import json,csv
import tkinter as tk
from tkinter import messagebox


def search(ranges,dict,text):
    # 简单的搜索功能 ranges:范围 dict:字典 text:搜索文本
    # print(ranges,dict,text)
    text = text.lower()
    result = set()
    zh_name_set = set(ranges)  # 转为 set 加快查找

    for entry in dict:
        zh = entry['zh_name']
        en = entry['en_name']
        if zh in zh_name_set:
            if text in zh.lower() or text in en.lower():
                result.add(zh)

    return list(result)

def check_details(details):
    details = details[:4]
    operator_to_members = {}

    for i, member in enumerate(details):
        for op in member["must"]:
            if op not in operator_to_members:
                operator_to_members[op] = []
            operator_to_members[op].append(f"队员{i+1}")

    conflict_lines = []
    for op, members in operator_to_members.items():
        if len(members) > 1:
            conflict_lines.append(f"{'、'.join(members)} 在必选中同时选择了 {op}")

    # 主窗口引用（假设你用的是 root 作为主窗口）
    parent = tk._default_root  # 通常 root 是默认的主窗口
    top = tk.Toplevel(parent)
    top.title("检查结果")

    msg = "\n".join(conflict_lines) if conflict_lines else "必选干员均无重复"
    tk.Label(top, text=msg, justify="left", padx=10, pady=10, font=("Arial", 12)).pack()
    tk.Button(top, text="确定", command=top.destroy, width=10).pack(pady=(0, 10))

    # 居中弹窗位置到主窗口
    top.update_idletasks()
    parent_x = parent.winfo_x()
    parent_y = parent.winfo_y()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()
    top_width = top.winfo_width()
    top_height = top.winfo_height()

    x = parent_x + (parent_width // 2) - (top_width // 2)
    y = parent_y + (parent_height // 2) - (top_height // 2)
    top.geometry(f"+{x}+{y}")
