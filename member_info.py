import tkinter as tk
from tkinter import ttk

STARTING_SUPPLY=[
    "未选择","2构想","2构想 或 2希望","2希望","热水壶","3护盾","5源石锭","不需要"
]

TEAM_CHOICE=[
    "未选择","魂灵护送","近锋","重辅","狙医","术特","高规格","点刺成锭","拟态学者","专业人士","异想天开","矛头","后勤分队","集群分队","指挥分队","蓝图测绘","博闻广记"
]

ENCOUNTER_CHOICE=[
    "未选择","死仇时代的恨意","希望时代的涂鸦","美愿时代的留恋","无","不确定"
]

ENDINGS=[
    "未选择",
    "245 不滚 一级蛋",
    "245 滚动 一级蛋",
    "245 不滚 二级蛋",
    "245 滚动 二级蛋",
    "245 不滚 三级蛋",
    "245 滚动 三级蛋",
    "不确定",
    "其他"
]

class MemberInfoPanel(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        # 个人ID
        tk.Label(self, text="个人ID：").grid(row=0, column=0, sticky="w")
        self.entry_id = tk.Entry(self)
        self.entry_id.grid(row=0, column=1, sticky="ew", columnspan=3, padx=2, pady=2)

        # 个人宣言
        tk.Label(self, text="个人宣言：").grid(row=1, column=0, sticky="nw")
        self.text_declaration = tk.Text(self, height=4, width=20, wrap="word")
        self.text_declaration.grid(row=1, column=1, columnspan=3, sticky="ew", padx=2, pady=2)

        # 四个下拉的容器
        options_frame = tk.Frame(self)
        options_frame.grid(row=3, column=0, columnspan=2, sticky="we", padx=2, pady=5)

        # 补给
        tk.Label(options_frame, text="开局补给", width=15).grid(row=0, column=0, sticky="e", padx=2, pady=2)
        self.starting_supply = ttk.Combobox(options_frame, values=STARTING_SUPPLY,state="readonly")
        self.starting_supply.grid(row=0, column=1, sticky="we", padx=2, pady=2)

        # 分队
        tk.Label(options_frame, text="选择分队", width=15).grid(row=0, column=2, sticky="e", padx=2, pady=2)
        self.team_choice = ttk.Combobox(options_frame, values=TEAM_CHOICE,state="readonly")
        self.team_choice.grid(row=0, column=3, sticky="we", padx=2, pady=2)

        # self.team_choice.bind("<<ComboboxSelected>>", lambda event: update_hope())

        # 相遇
        tk.Label(options_frame, text="选择相遇", width=15).grid(row=1, column=0, sticky="e", padx=2, pady=2)
        self.encounter = ttk.Combobox(options_frame, values=ENCOUNTER_CHOICE,state="readonly")
        self.encounter.grid(row=1, column=1, sticky="we", padx=2, pady=2)

        # 结局
        tk.Label(options_frame, text="选择结局", width=15).grid(row=1, column=2, sticky="e", padx=2, pady=2)
        self.ending = ttk.Combobox(options_frame, values=ENDINGS,state="readonly")
        self.ending.grid(row=1, column=3, sticky="we", padx=2, pady=2)

        self.starting_supply.current(0)
        self.team_choice.current(0)
        self.encounter.current(0)
        self.ending.current(0)

        # 列权重分配，确保下拉框横向拉伸
        for col in range(4):
            options_frame.columnconfigure(col, weight=1)

        # 必选干员消耗总希望
        tk.Label(self, text="必抓干员的总希望消耗：").grid(row=6, column=0, sticky="w")
        self.hope_label = tk.Label(self, text="0")
        self.hope_label.grid(row=6, column=1, sticky="w", padx=2, pady=2)

        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

    def get_info(self):
        return {
            "id": self.entry_id.get(),
            "declaration": self.text_declaration.get("1.0", tk.END).strip(),
            "supply": self.starting_supply.get(),
            "team": self.team_choice.get(),
            "encounter": self.encounter.get(),
            "ending": self.ending.get(),
            "hope": self.hope_label.cget("text")
        }

    def set_info(self, info: dict):
        self.entry_id.delete(0, tk.END)
        self.entry_id.insert(0, info.get("id", ""))

        self.text_declaration.delete("1.0", tk.END)
        self.text_declaration.insert("1.0", info.get("declaration", ""))

        # 设置 Combobox 的值，若不存在则设为“未选择”
        def set_combobox_value(combobox, value, choices):
            if value in choices:
                combobox.set(value)
            else:
                combobox.set("未选择")

        set_combobox_value(self.starting_supply, info.get("supply", "未选择"), STARTING_SUPPLY)
        set_combobox_value(self.team_choice, info.get("team", "未选择"), TEAM_CHOICE)
        set_combobox_value(self.encounter, info.get("encounter", "未选择"), ENCOUNTER_CHOICE)
        set_combobox_value(self.ending, info.get("ending", "未选择"), ENDINGS)

        self.hope_label.config(text=str(info.get("hope", "0")))

    def set_hope_value(self, value):
        self.hope_label.config(text=str(value))

    def get_team_choice(self):
        return self.team_choice.get()

    def set_update_callback(self, update_func):
        # 保存回调函数
        self._update_callback = update_func
        # 绑定事件：分队选择变更时调用
        self.team_choice.bind("<<ComboboxSelected>>", lambda event: update_func())

