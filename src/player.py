import tkinter as tk
from tkinter import ttk


bg_color = '#2e3436'
btn_color = '#babdb6'


class Player(tk.Tk):

    def __init__(self):
        root_win = tk.Tk()
        root_win.geometry("600x600+0+0")
        root_win.wm_attributes("-fullscreen", True)
        root_win.update()

        ttk.Style().configure(
            "Custom.TFrame", background=bg_color
        )
        ttk.Style().configure(
            "Custom.TButton", background=btn_color
        )

        fw_width = int(root_win.winfo_width() * 0.8)
        fw_height = int(root_win.winfo_height() * 0.1)
        fw_x = int(root_win.winfo_x() + root_win.winfo_width() * 0.1)
        fw_y = int(root_win.winfo_y() + root_win.winfo_height() - fw_height)
        fade_win = tk.Toplevel(root_win)
        fade_win.geometry(f"{fw_width}x{fw_height}+{fw_x}+{fw_y}")
        fade_win.overrideredirect(True)
        fade_win.focus_set()
        fade_win.lift(aboveThis=root_win)
        fade_win.wm_attributes("-alpha", 0.0)

        main_frame = ttk.Frame(
            root_win, width=root_win.winfo_width(),
            height=root_win.winfo_height(), style='Custom.TFrame')
        main_frame.pack()
        main_frame.bind(
            '<Button-1>',
            lambda event: self.fade_out(event, fade_win)
        )
        fade_win.bind(
            '<Button-1>',
            lambda event: self.fade_out(event, fade_win)
        )
        b_frame = ttk.Frame(fade_win, style='Custom.TFrame')
        b_frame.pack(fill=tk.X)
        left_b = ttk.Button(b_frame, text='Left', style='Custom.TButton')
        left_b.pack(side=tk.LEFT)
        right_b = ttk.Button(b_frame, text='Right', style='Custom.TButton')
        right_b.pack(side=tk.RIGHT)
        fade_win.update()
        fade_win.geometry(f"{fw_width}x{b_frame.winfo_height()}")
        self.fiap = self.fiwtap = False
        root_win.mainloop()

    def fade_in(self, event, frame):
        alpha = frame.wm_attributes("-alpha")
        if alpha > 0:
            alpha -= 0.05
            frame.wm_attributes("-alpha", alpha)
            self.fiap = frame.after(50, self.fade_in, event, frame)

    def fade_in_with_timer(self, event, frame, wait=True):
        if wait:
            wait = False
            self.fiwtap = frame.after(5000, self.fade_in_with_timer, event,
                                      frame, wait)
        else:
            wait = True
            self.fade_in(event, frame)

    def fade_out(self, event, frame):
        if self.fiap:
            frame.after_cancel(self.fiap)
        if self.fiwtap:
            frame.after_cancel(self.fiwtap)
        alpha = frame.wm_attributes("-alpha")
        if alpha < 1:
            alpha += 0.2
            frame.wm_attributes("-alpha", alpha)
            frame.after(50, self.fade_out, event, frame)
        else:
            self.fade_in_with_timer(event, frame)


if __name__ == '__main__':
    player = Player()
