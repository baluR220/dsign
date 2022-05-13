from os import path

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from yaml import safe_load

import conf


class VidViewer():
    def __init__(self):
        pass


class ImgViewer():
    def __init__(self):
        pass

    def show_pic(self, parent, obj, path_to_pic):
        path_to_pic = path.join(conf.MEDIA, path_to_pic)
        layout = obj['layout']
        width, height = layout.split('|')[0].split('x')
        x, y = layout.split('|')[1].split(',')
        width, height, x, y = (int(width), int(height), int(x), int(y))
        with Image.open(path_to_pic) as pic_pil_r:
            img_w, img_h = pic_pil_r.size
            if not width or not height:
                width, height = self.root_win_w, self.root_win_h
            ratio = min(width / img_w, height / img_h)
            width, height = int(img_w * ratio), int(img_h * ratio)
            pic_pil = pic_pil_r.resize(
                (width, height), Image.ANTIALIAS
            )
        pic_tk = ImageTk.PhotoImage(pic_pil)
        label = ttk.Label(parent, image=pic_tk)
        label.image = pic_tk
        label.place(x=x, y=y)
        pic_pil_r.close()
        del pic_pil_r
        pic_pil.close()
        del pic_pil
        del pic_tk


class Player(ImgViewer, VidViewer):

    def __init__(self):
        root_win = tk.Tk()
        self.set_styles()
        self.fiap = False
        main_frame = self.set_main_wins(root_win)
        fade_wins = self.set_fade_wins(root_win)

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
        self.show, self.media = self.get_show(conf.SHOW)
        self.show_current = 0
        self.show_last = len(self.show) - 1
        self.show_frame = main_frame
        self.run_show()
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

        back_b = ttk.Button(fade_win_back, text='Back', style='Custom.TButton',
                            command=lambda: self.next_scene(back=True))
        back_b.pack()
        forw_b = ttk.Button(fade_win_forw, text='Forw', style='Custom.TButton',
                            command=lambda: self.next_scene(forw=True))
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

    def next_scene(self, back=False, forw=False):
        k = 1 if forw else -1
        count = self.show_current + k
        if count < 0:
            self.show_current = self.show_last
        elif count > self.show_last:
            self.show_current = 0
        else:
            self.show_current = count
        self.run_show()

    def get_show(self, path_to_show):
        with open(path_to_show) as file:
            data = safe_load(file)
        return(data['scenes'], data['media'])

    def get_obj(self, obj, media):
        for file in media:
            if file['name'] == obj['name']:
                return(file['type'], file['path'])

    def run_show(self):
        for child in self.show_frame.winfo_children():
            child.destroy()
        current = self.show[self.show_current]
        for obj in current['objects']:
            obj_type, path_to_media = self.get_obj(obj, self.media)
            if obj_type == 'img':
                self.show_pic(self.show_frame, obj, path_to_media)
            if obj_type == 'vid':
                # call show video
                pass
        #self.show_frame.after(current['duration'] * 1000,
        #                      lambda: self.next_scene(forw=True))


if __name__ == '__main__':
    player = Player()
