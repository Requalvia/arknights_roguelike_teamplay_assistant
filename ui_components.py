import tkinter as tk
from PIL import ImageTk, Image
import json
from logic import search,check_details
from member_info import MemberInfoPanel
from export_import import export_data
from tkinter import filedialog, messagebox

class AvatarGrid(tk.Frame):
    def __init__(self, master,rows=3,cols=4, cell_size=64, placeholder_color="#cccccc", on_change=None, **kwargs):
        super().__init__(master, **kwargs)

        self.on_change = on_change  # 添加这一行


        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.placeholder_color = placeholder_color

        self.avatar_images_refs = []  # 防止图片被回收
        self.labels = []
        self.names_grid = [[None]*self.cols for _ in range(self.rows)]

        # 生成纯色占位图
        placeholder_img = Image.new("RGB", (cell_size, cell_size), placeholder_color)
        self.placeholder_img = ImageTk.PhotoImage(placeholder_img)

        for r in range(self.rows):
            for c in range(self.cols):
                lbl = tk.Label(self, image=self.placeholder_img, bd=1, relief=tk.RIDGE, highlightthickness=2, highlightbackground="#f0f0f0")
                lbl.grid(row=r, column=c, padx=2, pady=2)
                self.labels.append(lbl)
                self.avatar_images_refs.append(self.placeholder_img)
                self.names_grid[r][c] = None

    def update_avatar(self, row, col, pil_img, name=None):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            tk_img = ImageTk.PhotoImage(pil_img.resize((self.cell_size, self.cell_size)))
            self.avatar_images_refs.append(tk_img)
            idx = row * self.cols + col
            self.labels[idx].config(image=tk_img)
            self.names_grid[row][col] = name

            if self.on_change:
                self.on_change()

    def get_name_by_position(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.names_grid[row][col]
        return None

    def set_avatar(self, row, col, img, name=None):
        idx = row * self.cols + col
        self.labels[idx].configure(image=img, highlightbackground="#f0f0f0", highlightthickness=2)
        self.avatar_images_refs.append(img)
        self.names_grid[row][col] = name
        if self.on_change:
            self.on_change()  # 回调通知变化


def make_must_update_callback(info_panel, must_grid, operators_dict):
    def update_hope():
        stars = []
        professions = []
        must_operator_names = [name for row in must_grid.names_grid for name in row if name]

        for row in must_grid.names_grid:
            for name in row:
                if name:
                    # 查找对应的干员信息
                    op_info = next((op for op in operators_dict if op["zh_name"] == name), None)
                    if op_info:
                        try:
                            rarity = int(op_info["rarity"])
                            prof = op_info["prof"]
                            stars.append(rarity)
                            professions.append(prof)
                        except (ValueError, KeyError):
                            pass  # 忽略异常数据

        # 示例 hope 计算公式
        count = len(stars)
        team_name=info_panel.get_team_choice()




        # 调试输出（可选）
        print(f"必选干员数: {count}")
        print(f"星级: {stars}")
        print(f"职业: {professions}")

        # 基础希望值
        hope = 0
        for star in stars:
            if star == 6:
                hope += 10
            elif star == 5:
                hope += 4
            elif star == 4:
                hope += 1
            # 1~3星不加希望

        # 职业减免处理
        for star, prof in zip(stars, professions):
            if team_name == "近锋" and prof in ["先锋", "近卫"]:
                if star in [5, 6]:
                    hope -= 3
            elif team_name == "重辅" and prof in ["重装", "辅助"]:
                if star in [5, 6]:
                    hope -= 3
            elif team_name == "狙医" and prof in ["狙击", "医疗"]:
                if star in [5, 6]:
                    hope -= 3
            elif team_name == "术特" and prof in ["术师", "特种"]:
                if star in [5, 6]:
                    hope -= 3

        # 高规格减免处理
        if team_name == "高规格":
            for star in stars:
                if star == 5:
                    hope -= 1

        # 阿米娅特判（需构筑中有“阿米娅”）
        if team_name in ["近锋", "狙医"] and "阿米娅" in must_operator_names:
            hope -= 3

        # 最终非负限制
        hope = max(hope, 0)

        info_panel.set_hope_value(hope)

    return update_hope


def build_gui(root, operators, avatars):



    # ----------- 读取rarity_groups_full.json -----------
    with open("rarity_groups_full.json", encoding="utf-8") as f:
        rarity_groups = json.load(f)



    root.title("你团队吗？仙术杯辅助工具_b站【想饮冻奶茶】")

    x, y = 1500, 900
    root.geometry(f"{x}x{y}")
    root.minsize(x, y)
    root.maxsize(x, y)
    root.resizable(False, False)

    selected_avatar = {"img": None, "name": None, "label": None, "grid": None, "row": None, "col": None}
    avatar_grids = []

    member_info_panels = []  # 存储每位成员的 info panel，用于后续访问

    # 队伍名称区域（放在最顶部）
    team_name_frame = tk.Frame(root)
    team_name_frame.pack(side=tk.TOP, fill=tk.X, padx=75, pady=10)

    tk.Label(team_name_frame, text="队伍名称：", font=("Helvetica", 14)).pack(side=tk.LEFT)

    team_name_var = tk.StringVar()
    team_name_entry = tk.Entry(team_name_frame, textvariable=team_name_var, font=("Helvetica", 14))
    team_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)


    main_pane = tk.PanedWindow(root, orient=tk.VERTICAL)
    main_pane.pack(fill=tk.BOTH, expand=True)

    top_frame = tk.Frame(main_pane)
    bottom_frame = tk.Frame(main_pane, bg="#f0f0f0")
    main_pane.add(top_frame, height=int(root.winfo_screenheight() * 2 / 3))
    main_pane.add(bottom_frame, height=int(root.winfo_screenheight() * 1 / 3))

    members_frame = tk.Frame(top_frame)
    members_frame.pack(fill=tk.BOTH, expand=True)

    for i in range(4):
        member_frame = tk.LabelFrame(members_frame, text=f"成员 {i + 1}", padx=5, pady=5)
        member_frame.grid(row=0, column=i, sticky="nsew", padx=5, pady=5)
        members_frame.columnconfigure(i, weight=1)

        list_frame = tk.Frame(member_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        must_label = tk.Label(list_frame, text="一定选取")
        must_label.pack()

        must_grid = AvatarGrid(list_frame,rows=3,cols=4)
        must_grid.pack(fill=tk.BOTH, expand=True)


        may_label = tk.Label(list_frame, text="可能选取")
        may_label.pack()

        may_grid = AvatarGrid(list_frame,rows=2,cols=4)
        may_grid.pack(fill=tk.BOTH, expand=True)

        # 添加信息面板
        info_panel = MemberInfoPanel(list_frame)
        info_panel.pack(fill=tk.X, pady=5)
        member_info_panels.append(info_panel)

        must_grid.on_change = make_must_update_callback(info_panel, must_grid, operators)

        update_hope = make_must_update_callback(info_panel, must_grid, operators)
        info_panel.set_update_callback(update_hope)

        avatar_grids.extend([must_grid, may_grid])

    status = tk.Label(bottom_frame, text=f"已加载头像：{len(avatars)} 张")
    status.pack(pady=4)

    # 创建滚动头像区和右侧筛选区的父容器
    bottom_content = tk.Frame(bottom_frame, bg="#f0f0f0")
    bottom_content.pack(fill=tk.BOTH, expand=True)

    # 左侧滚动头像区
    avatar_canvas = tk.Canvas(bottom_content, bg="#f0f0f0", width=800)
    avatar_scrollbar = tk.Scrollbar(bottom_content, orient=tk.VERTICAL, command=avatar_canvas.yview)
    avatar_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
    avatar_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    avatar_canvas.configure(yscrollcommand=avatar_scrollbar.set)

    avatar_inner_frame = tk.Frame(avatar_canvas, bg="#f0f0f0")
    avatar_canvas.create_window((0, 0), window=avatar_inner_frame, anchor="nw")

    root.avatar_images_refs = []
    columns = 12

    # 右侧筛选区
    filter_frame = tk.Frame(bottom_content, padx=40, pady=10)
    filter_frame.pack(side=tk.LEFT, fill=tk.Y)

    rarity_filters = {
        6: tk.BooleanVar(value=True),
        5: tk.BooleanVar(value=False),
        4: tk.BooleanVar(value=False),
        3: tk.BooleanVar(value=False),  # 代表 1/2/3星合并
    }

    # 添加按钮行
    button_frame = tk.Frame(filter_frame)
    button_frame.pack(side=tk.RIGHT, anchor="n", padx=(20, 0))

    import_button = tk.Button(button_frame, text="导入", width=8)
    import_button.pack(pady=5)

    check_button = tk.Button(button_frame, text="检查", width=8)
    check_button.pack(pady=5)

    export_button = tk.Button(button_frame, text="导出", width=8)
    export_button.pack(pady=5)

    reset_button = tk.Button(button_frame, text="重置", width=8)
    reset_button.pack(pady=5)


    def get_all_details():
        all_details = []
        for i in range(4):
            must_grid = avatar_grids[i * 2]  # 第 i 个成员的必选网格
            may_grid = avatar_grids[i * 2 + 1]  # 第 i 个成员的可能网格
            info_panel = member_info_panels[i]  # 第 i 个成员的信息面板

            must_operators = [name for row in must_grid.names_grid for name in row if name]
            may_operators = [name for row in may_grid.names_grid for name in row if name]
            info_data = info_panel.get_info()

            all_details.append({
                "must": must_operators,
                "may": may_operators,
                "info": info_data
            })

        all_details.append(  team_name_var.get())

        return all_details

    def on_check():
        all_details=get_all_details()
        # 现在调用 check_details 函数（你可以导入它或定义它）
        check_details(all_details)

    def on_export():
        all_details=get_all_details()
        print(all_details)
        # 现在调用 check_details 函数（你可以导入它或定义它）
        export_data(all_details)

    def on_import():
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON 文件", "*.json")],
            title="导入信息"
        )

        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for i in range(4):
                must_grid = avatar_grids[i * 2]
                may_grid = avatar_grids[i * 2 + 1]
                member_info = member_info_panels[i]

                # 填充 must 区
                must_names = data[i]["must"]
                idx = 0
                for r in range(must_grid.rows):
                    for c in range(must_grid.cols):
                        if idx < len(must_names):
                            name = must_names[idx]
                            img = ImageTk.PhotoImage(avatars[name].resize((must_grid.cell_size, must_grid.cell_size)))
                            must_grid.set_avatar(r, c, img, name)
                            root.avatar_images_refs.append(img)
                        else:
                            must_grid.set_avatar(r, c, must_grid.placeholder_img, None)
                        idx += 1

                # 填充 may 区
                may_names = data[i]["may"]
                idx = 0
                for r in range(may_grid.rows):
                    for c in range(may_grid.cols):
                        if idx < len(may_names):
                            name = may_names[idx]
                            img = ImageTk.PhotoImage(avatars[name].resize((may_grid.cell_size, may_grid.cell_size)))
                            may_grid.set_avatar(r, c, img, name)
                            root.avatar_images_refs.append(img)
                        else:
                            may_grid.set_avatar(r, c, may_grid.placeholder_img, None)
                        idx += 1

                # 恢复 info 信息
                member_info.set_info(data[i]["info"])

                team_name=data[-1]
                if isinstance(team_name,str):
                    team_name_var.set(team_name)

            messagebox.showinfo("导入成功", f"信息已从\n{file_path}\n成功导入")

        except Exception as e:
            messagebox.showerror("导入失败", f"导入过程中出错：\n{str(e)}")

    def reset_all_confirm():
        confirm_win = tk.Toplevel(root)
        confirm_win.title("确认重置")
        confirm_win.transient(root)
        confirm_win.grab_set()

        # 弹窗大小
        w, h = 400, 150

        # 获取父窗口位置和大小
        root.update_idletasks()  # 确保root的尺寸是最新的
        root_x = root.winfo_x()
        root_y = root.winfo_y()
        root_w = root.winfo_width()
        root_h = root.winfo_height()

        # 计算弹窗坐标，使其居中于父窗口
        x = root_x + (root_w // 2) - (w // 2)
        y = root_y + (root_h // 2) - (h // 2)

        confirm_win.geometry(f"{w}x{h}+{x}+{y}")
        confirm_win.resizable(False, False)

        label = tk.Label(confirm_win, text="提示：即将重置窗口内的所有选项\n（不会改动已经保存的json文件）",
                         font=("Helvetica", 12))
        label.pack(pady=20)

        btn_frame = tk.Frame(confirm_win)
        btn_frame.pack(pady=10)

        def on_no():
            confirm_win.destroy()

        def on_yes():
            reset_all()
            confirm_win.destroy()

        no_btn = tk.Button(btn_frame, text="否", width=10, command=on_no)
        no_btn.pack(side=tk.LEFT, padx=10)

        yes_btn = tk.Button(btn_frame, text="是", width=10, command=on_yes)
        yes_btn.pack(side=tk.LEFT, padx=10)

    def reset_all():
        # 清空所有avatar_grids（must和may）
        for grid in avatar_grids:
            for r in range(grid.rows):
                for c in range(grid.cols):
                    grid.set_avatar(r, c, grid.placeholder_img, name=None)

        # 清空所有成员信息面板
        for info_panel in member_info_panels:
            # 这里调用set_info清空，如果没有，可以根据你MemberInfoPanel结构手动清空
            info_panel.set_info({})  # 传空数据，或者你可以定义专门的清空方法

        # 清空选中头像信息
        selected_avatar.update({"img": None, "name": None, "label": None, "grid": None, "row": None, "col": None})

        # 清空队伍名称
        team_name_var.set("")

    # 按钮绑定
    check_button.config(command=on_check)
    import_button.config(command=on_import)
    export_button.config(command=on_export)
    reset_button.config(command=reset_all_confirm)

    # 在 filter_frame 中添加搜索框和标签
    search_var = tk.StringVar()

    def on_search_change(*args):
        update_avatar_display()

    search_var.trace_add("write", on_search_change)

    search_label = tk.Label(filter_frame, text="搜索干员")
    search_label.pack(pady=(10, 0))
    search_entry = tk.Entry(filter_frame, textvariable=search_var)
    search_entry.pack(fill=tk.X, pady=(0, 10))



    def on_avatar_click(event, img, name, lbl):
        if selected_avatar["label"]:
            selected_avatar["label"].config(highlightbackground="#f0f0f0", highlightthickness=2)
        lbl.config(highlightbackground="red", highlightthickness=2)
        selected_avatar.update({"img": img, "name": name, "label": lbl, "grid": None, "row": None, "col": None})

    def update_avatar_display():
        # 读取勾选状态
        selected_any = [v.get() for v in rarity_filters.values()]


        # 根据勾选项，先筛选出要显示的名字列表

        selected_names = []
        if selected_any[0] is True:
            # 要6星
            selected_names.extend([x['zh_name'] for x in rarity_groups['6']])
        if selected_any[1] is True:
            # 要5星
            selected_names.extend([x['zh_name'] for x in rarity_groups['5']])
        if selected_any[2] is True:
            # 要4星
            selected_names.extend([x['zh_name'] for x in rarity_groups['4']])
        if selected_any[3] is True:
            # 要321星
            selected_names.extend([x['zh_name'] for x in rarity_groups['1_2_3']])
        if selected_any[0] is False and selected_any[1] is False and selected_any[2] is False and selected_any[3] is False:
            # 全都要
            selected_names.extend([x['zh_name'] for x in rarity_groups['6']])
            selected_names.extend([x['zh_name'] for x in rarity_groups['5']])
            selected_names.extend([x['zh_name'] for x in rarity_groups['4']])
            selected_names.extend([x['zh_name'] for x in rarity_groups['1_2_3']])

        # print("筛选状态:", selected_any)
        # print(len(selected_names))

        # 搜索框
        search_text = search_var.get().strip().lower()
        if len(search_text)>0:
            selected_names=search(selected_names,operators,search_text)

        # 清空显示区
        for widget in avatar_inner_frame.winfo_children():
            widget.destroy()


        row = col = 0
        for name in selected_names:
            info = avatars[name]
            tk_img = ImageTk.PhotoImage(info.resize((64, 64)))
            root.avatar_images_refs.append(tk_img)

            frame = tk.Frame(avatar_inner_frame, padx=5, pady=5)
            frame.grid(row=row, column=col)
            lbl_img = tk.Label(frame, image=tk_img, highlightbackground="#f0f0f0", highlightthickness=2)
            lbl_img.pack()
            lbl_img.bind("<Button-1>", lambda e, img=tk_img, name=name, lbl=lbl_img: on_avatar_click(e, img, name, lbl))

            col += 1
            if col >= columns:
                col = 0
                row += 1

        avatar_inner_frame.update_idletasks()
        avatar_canvas.config(scrollregion=avatar_canvas.bbox("all"))

        status.config(text=f"已筛选 {len(selected_names)} / {len(avatars)} 张")

    # 右侧筛选复选框
    tk.Checkbutton(filter_frame, text="显示6星", variable=rarity_filters[6], command=update_avatar_display).pack(anchor="w")
    tk.Checkbutton(filter_frame, text="显示5星", variable=rarity_filters[5], command=update_avatar_display).pack(anchor="w")
    tk.Checkbutton(filter_frame, text="显示4星", variable=rarity_filters[4], command=update_avatar_display).pack(anchor="w")
    tk.Checkbutton(filter_frame, text="显示1/2/3星", variable=rarity_filters[3], command=update_avatar_display).pack(anchor="w")

    # 先显示空列表
    update_avatar_display()

    # 下面的网格绑定和其他逻辑维持不变（略），你可以把你之前的事件绑定和功能代码放这里

    # --- 网格点击和菜单绑定 示例 ---
    def on_grid_click(event, grid, row, col):
        current_name = grid.get_name_by_position(row, col)

        if selected_avatar["img"] and selected_avatar["grid"] is None:
            for r in range(grid.rows):
                for c in range(grid.cols):
                    if grid.get_name_by_position(r, c) == selected_avatar["name"]:
                        grid.set_avatar(r, c, grid.placeholder_img, name=None)
            grid.set_avatar(row, col, selected_avatar["img"], name=selected_avatar["name"])
            if selected_avatar["label"]:
                selected_avatar["label"].config(highlightbackground="#f0f0f0", highlightthickness=2)
            selected_avatar.update({"img": None, "name": None, "label": None, "grid": None, "row": None, "col": None})

        elif selected_avatar["grid"]:
            if selected_avatar["grid"] == grid and selected_avatar["row"] == row and selected_avatar["col"] == col:
                return
            for r in range(grid.rows):
                for c in range(grid.cols):
                    if grid.get_name_by_position(r, c) == selected_avatar["name"]:
                        grid.set_avatar(r, c, grid.placeholder_img, name=None)
            selected_avatar["grid"].set_avatar(selected_avatar["row"], selected_avatar["col"],
                                               selected_avatar["grid"].placeholder_img, name=None)
            grid.set_avatar(row, col, selected_avatar["img"], name=selected_avatar["name"])
            selected_avatar.update({"img": None, "name": None, "label": None, "grid": None, "row": None, "col": None})

        else:
            if current_name is not None:
                idx = row * grid.cols + col
                for g in avatar_grids:
                    for l in g.labels:
                        l.config(highlightbackground="#f0f0f0", highlightthickness=2)
                grid.labels[idx].config(highlightbackground="red", highlightthickness=2)
                selected_avatar.update({
                    "img": grid.labels[idx].cget("image"),
                    "name": current_name,
                    "label": grid.labels[idx],
                    "grid": grid,
                    "row": row,
                    "col": col
                })

    def show_context_menu(event, grid, row, col):
        if grid.get_name_by_position(row, col) is not None:
            menu = tk.Menu(root, tearoff=0)
            menu.add_command(label="删除", command=lambda: grid.set_avatar(row, col, grid.placeholder_img, name=None))
            menu.post(event.x_root, event.y_root)

    for grid in avatar_grids:
        for r in range(grid.rows):
            for c in range(grid.cols):
                idx = r * grid.cols + c
                lbl = grid.labels[idx]
                lbl.bind("<Button-1>", lambda e, g=grid, row=r, col=c: on_grid_click(e, g, row, col))
                lbl.bind("<Button-3>", lambda e, g=grid, row=r, col=c: show_context_menu(e, g, row, col))

    def _on_mousewheel(event):
        # Windows / Linux
        if event.num == 4 or event.delta > 0:
            avatar_canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            avatar_canvas.yview_scroll(1, "units")

    # Windows 和 Linux (一般支持 MouseWheel)
    avatar_canvas.bind_all("<MouseWheel>", lambda e: avatar_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
    # Linux 可能要绑定 Button-4/5
    avatar_canvas.bind_all("<Button-4>", lambda e: avatar_canvas.yview_scroll(-1, "units"))
    avatar_canvas.bind_all("<Button-5>", lambda e: avatar_canvas.yview_scroll(1, "units"))


