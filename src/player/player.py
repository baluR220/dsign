from os import path

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from yaml import safe_load

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

# Needed for set_window_handle():
gi.require_version('GstVideo', '1.0')
from gi.repository import GstVideo


import cli


class VidViewer():
    def __init__(self):
        pass

    def set_frame_handle(seld, bus, message, frame_id):
        if not message.get_structure() is None:
            if message.get_structure().get_name() == 'prepare-window-handle':
                display_frame = message.src
                display_frame.set_property('force-aspect-ratio', True)
                display_frame.set_window_handle(frame_id)

    def show_vid(self, parent, path_to_vid):
        Gst.init(None)
        GObject.threads_init()
        display_frame = ttk.Frame(parent, style='Frame.TFrame')
        frame_id = display_frame.winfo_id()
        player = Gst.ElementFactory.make('playbin', None)
        player.set_property('uri', 'file://%s' % path_to_vid)
        player.set_state(Gst.State.PLAYING)
        bus = player.get_bus()
        bus.enable_sync_message_emission()
        bus.connect(
            'sync-message::element', self.set_frame_handle, frame_id
        )

        return(display_frame, player)


class ImgViewer():
    def __init__(self):
        pass

    def show_pic(self, parent, geom, path_to_pic):
        width, height = geom
        with Image.open(path_to_pic) as pic_pil_r:
            img_w, img_h = pic_pil_r.size
            ratio = min(width / img_w, height / img_h)
            width, height = int(img_w * ratio), int(img_h * ratio)
            pic_pil = pic_pil_r.resize(
                (width, height), Image.ANTIALIAS
            )
        pic_tk = ImageTk.PhotoImage(pic_pil)
        label = ttk.Label(parent, image=pic_tk)
        label.image = pic_tk
        pic_pil_r.close()
        del pic_pil_r
        pic_pil.close()
        del pic_pil
        del pic_tk
        return(label)


class Player(ImgViewer, VidViewer):

    def __init__(self):
        root_win = tk.Tk()
        self.set_styles()
        self.fiap = False
        self.rsap = False
        self.vid_player = []
        main_frame = self.set_main_wins(root_win)
        fade_wins = self.set_fade_wins(root_win)

        if not conf.fade_to == 0:
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
        self.show, self.media = self.get_show(conf.show)
        if self.show:
            self.show_current = 0
            self.show_last = len(self.show) - 1
            self.show_frame = main_frame
            self.show_frame.update()
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
            height=self.root_win_h, style='Frame.TFrame')
        main_frame.pack()
        return(main_frame)

    def set_styles(self):
        ttk.Style().configure(
            "Frame.TFrame", background=conf.bg_color
        )
        ttk.Style().configure(
            "Button.TFrame", background=conf.btn_color
        )

    def set_fade_wins(self, root_win):
        fw_x = root_win.winfo_x()
        fw_y = root_win.winfo_y()
        width = int(self.root_win_w * 0.1)
        height = self.root_win_h
        fade_win_back = tk.Toplevel(root_win)
        fade_win_back.geometry(f"{width}x{height}+{fw_x}+{fw_y}")

        fade_win_forw = tk.Toplevel(root_win)
        fw_x += int(width + self.root_win_w * 0.8)
        fade_win_forw.geometry(f"{width}x{height}+{fw_x}+{fw_y}")

        fade_wins = (fade_win_back, fade_win_forw)
        for win in fade_wins:
            win.overrideredirect(True)
            win.lift(aboveThis=root_win)
            win.wm_attributes("-alpha", conf.max_alpha)

        back_b = ttk.Frame(fade_win_back, style='Button.TFrame', width=width,
                           height=height)
        back_b.bind('<Button-1>',
                    lambda event: self.next_scene(event, back=True))
        back_b.pack()
        forw_b = ttk.Frame(fade_win_forw, style='Button.TFrame', width=width,
                           height=height)
        forw_b.bind('<Button-1>',
                    lambda event: self.next_scene(event, forw=True))
        forw_b.pack()
        return(fade_wins)

    def fade_in(self, event, fade_wins, wait=True):
        if wait:
            wait = False
            delay = conf.fade_to
        else:
            for frame in fade_wins:
                alpha = frame.wm_attributes("-alpha")
                delay = 50
                if alpha > conf.min_alpha:
                    alpha -= conf.fade_in_sp
                    frame.wm_attributes("-alpha", alpha)
        self.fiap = fade_wins[0].after(delay, self.fade_in, event,
                                       fade_wins, wait)

    def fade_out(self, event, fade_wins):
        if self.fiap:
            fade_wins[0].after_cancel(self.fiap)
        for frame in fade_wins:
            alpha = frame.wm_attributes("-alpha")
            if alpha < conf.max_alpha:
                alpha += conf.fade_out_sp
                frame.wm_attributes("-alpha", alpha)
                fade_wins[0].after(50, self.fade_out, event, fade_wins)
        else:
            self.fade_in(event, fade_wins)

    def next_scene(self, event=None, back=False, forw=False):
        if self.show:
            if self.rsap:
                self.show_frame.after_cancel(self.rsap)
            k = 1 if forw else -1
            count = self.show_current + k
            if count < 0:
                self.show_current = self.show_last
            elif count > self.show_last:
                self.show_current = 0
            else:
                self.show_current = count
            self.run_show(k=k)

    def get_show(self, path_to_show):
        if path_to_show:
            with open(path_to_show) as file:
                data = safe_load(file)
            return(data['scenes'], data['media'])
        else:
            return(None, None)

    def get_obj(self, obj, media):
        for file in media:
            if file['name'] == obj['name']:
                return(file['type'], file['path'])

    def run_show(self, k=1):
        for child in self.show_frame.winfo_children():
            self.move_away(child, k)
            if self.vid_player:
                for player in self.vid_player:
                    player.set_state(Gst.State.NULL)
                self.vid_player = []
        current = self.show[self.show_current]
        duration = current['duration']
        for obj in current['objects']:
            obj_type, path_to_media = self.get_obj(obj, self.media)
            path_to_obj = path.join(conf.media, path_to_media)
            layout = obj['layout']
            width, height = layout.split('|')[0].split('x')
            x, y = layout.split('|')[1].split(',')
            width, height, x, y = (int(width), int(height), int(x), int(y))
            if not width or not height:
                width, height = self.root_win_w, self.root_win_h
            if obj_type == 'img':
                geom = (width, height)
                obj = self.show_pic(self.show_frame, geom, path_to_obj)
                obj.place(x=k * (self.show_frame.winfo_width()), y=y)
            if obj_type == 'vid':
                obj, player = self.show_vid(
                    self.show_frame, path_to_obj
                )
                obj.place(x=k * (
                    self.show_frame.winfo_width()), y=y, width=width,
                    height=height
                )
                self.vid_player.append(player)

            self.show_frame.update()
            self.move_in(obj, x, k)
            if self.vid_player:
                for player in self.vid_player:
                    while True:
                        try:
                            dur = player.query_duration(Gst.Format.TIME)
                        except Exception:
                            pass
                        if dur[0]:
                            dur = int(dur[1] / 10 ** 9)
                            break
                    if dur > duration:
                        duration = dur
        if duration:
            self.rsap = self.show_frame.after(
                duration * 1000,
                lambda: self.next_scene(forw=True)
            )

    def move_away(self, widget, k):
        x = widget.winfo_x()
        if (x < -(widget.winfo_width()) or x > self.show_frame.winfo_width()):
            widget.destroy()
        elif x != -k * (widget.winfo_width()):
            widget.place_configure(x=(widget.winfo_x() + -k * 10))
            self.show_frame.after(10, self.move_away, widget, k)

    def move_in(self, widget, x, k):
        if widget.winfo_x() != x:
            widget.place_configure(x=(widget.winfo_x() + -k * 10))
            self.show_frame.after(10, self.move_in, widget, x, k)


if __name__ == '__main__':
    conf = cli.Conf()
    player = Player()
