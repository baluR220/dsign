from os import path

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

import conf


path_to_media = '/home/player/python/dsign/media'
show = ['1.jpg', '2.jpg', '3.jpg', '4.jpg']


class Player():

    def __init__(self):
        root_win = tk.Tk()
        self.set_styles()
        self.fiap = False
        main_frame = self.set_main_wins(root_win)
        fade_wins = self.set_fade_wins(root_win)
        self.load_sample_pic(main_frame)

        if not conf.FADE_TO == 0:
            for win in fade_wins:
                win.wm_attributes("-alpha", 0.0)
                win.bind_all(
                    '<Button-1>',
                    lambda event: self.fade_out(event, fade_wins)
                )
            main_frame.bind_all(
                '<Button-1>',
                lambda event: self.fade_out(event, fade_wins)
            )

        root_win.mainloop()

    def set_main_wins(self, root_win):
        root_win.geometry("600x600+0+0")
        #root_win.wm_attributes("-fullscreen", True)
        root_win.update()
        self.root_win_w = root_win.winfo_width()
        self.root_win_h = root_win.winfo_height()

        main_frame = ttk.Frame(
            root_win, width=self.root_win_w,
            height=self.root_win_h, style='Custom.TFrame')
        main_frame.pack()
        return(main_frame)

    def set_styles(self):
        ttk.Style().configure(
            "Custom.TFrame", background=conf.BG_COLOR
        )
        ttk.Style().configure(
            "Custom.TButton", background=conf.BTN_COLOR
        )

    def set_fade_wins(self, root_win):
        fw_x = int(root_win.winfo_x() + self.root_win_w * 0.1)
        fw_y = int(root_win.winfo_y() + self.root_win_h - int(
            self.root_win_h * 0.1)
        )
        fade_win_back = tk.Toplevel(root_win)
        fade_win_back.geometry(f"+{fw_x}+{fw_y}")

        fade_win_forw = tk.Toplevel(root_win)
        fade_wins = (fade_win_back, fade_win_forw)
        for win in fade_wins:
            win.overrideredirect(True)
            win.lift(aboveThis=root_win)
            win.wm_attributes("-alpha", 1)

        back_b = ttk.Button(fade_win_back, text='Back', style='Custom.TButton')
        back_b.pack()
        forw_b = ttk.Button(fade_win_forw, text='Forw', style='Custom.TButton')
        forw_b.pack()
        forw_b.update()
        fw_x_forw = int(self.root_win_w * 0.9 - forw_b.winfo_width())
        fade_win_forw.geometry(f"+{fw_x_forw}+{fw_y}")
        return(fade_wins)

    def fade_in(self, event, fade_wins, wait=True):
        if wait:
            wait = False
            delay = conf.FADE_TO
        else:
            for frame in fade_wins:
                alpha = frame.wm_attributes("-alpha")
                delay = 50
                if alpha > 0:
                    alpha -= conf.FADE_IN_SP
                    frame.wm_attributes("-alpha", alpha)
        self.fiap = fade_wins[0].after(delay, self.fade_in, event,
                                       fade_wins, wait)

    def fade_out(self, event, fade_wins):
        if self.fiap:
            fade_wins[0].after_cancel(self.fiap)
        for frame in fade_wins:
            alpha = frame.wm_attributes("-alpha")
            if alpha < 1:
                alpha += conf.FADE_OUT_SP
                frame.wm_attributes("-alpha", alpha)
                fade_wins[0].after(50, self.fade_out, event, fade_wins)
        else:
            self.fade_in(event, fade_wins)

    def show_pic(self, parent, path_to_pic, geom):
        pic_pil = Image.open(path_to_pic).resize(
            (geom['width'], geom['height']), Image.ANTIALIAS
        )
        pic_tk = ImageTk.PhotoImage(pic_pil)
        label = ttk.Label(parent, image=pic_tk)
        label.image = pic_tk
        label.place(x=geom['x'], y=geom['y'])

    def load_sample_pic(self, parent):
        pic = path.join(path_to_media, show[0])
        geom = {'width': self.root_win_w, 'height': self.root_win_h,
                'x': 0, 'y': 0}
        self.show_pic(parent, pic, geom)


if __name__ == '__main__':
    player = Player()
