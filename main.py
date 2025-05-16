import tkinter as tk
from data_loader import load_operators, load_avatars
from ui_components import build_gui

if __name__ == "__main__":
    root = tk.Tk()

    operator_data = load_operators()
    avatar_data = load_avatars(operator_data)

    build_gui(root, operator_data, avatar_data)
    root.mainloop()
