import time
import tkinter as tk
import psutil


class Settings:
    topmost = True
    alpha = 0.9
    width, height = (84, 42)
    update_time = 1000
    click_close_time_ns = 0.35

    def colors(self, idx=-1):
        if idx == 0:
            return self.get_color_02x((255, 169, 36))
        elif idx == 1:
            return self.get_color_02x((139, 240, 39))
        else:
            return self.get_color_02x((10, 9, 12))

    @staticmethod
    def get_color_02x(color):
        if type(color) is str and len(color) == 7:
            return color
        if type(color) is tuple and len(color) == 3:
            return "#{:02x}{:02x}{:02x}".format(*color)
        raise TypeError("color error")

    @staticmethod
    def get_net_byte():
        net_byte = psutil.net_io_counters()
        return net_byte.bytes_sent, net_byte.bytes_recv


class DraggableWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.x = None
        self.y = None
        self.second_ns = time.time()
        self.win_width = self.winfo_screenwidth()
        self.win_height = self.winfo_screenheight()

        self.settings = Settings()
        self.content, self.content1 = self.settings.get_net_byte()
        self.max_x = self.win_width - self.settings.width
        self.max_y = self.win_height - self.settings.height

        # 隐藏默认标题栏
        self.overrideredirect(True)

        self.config(bg=self.settings.colors())
        self.attributes(
            "-topmost", self.settings.topmost,
            "-alpha", self.settings.alpha,
        )
        self.set_geometry()
        self.set_bind()
        # 添加自定义关闭按钮

        self.info = tk.Label(self, text="", bd=1.2,
                             fg=self.settings.colors(0), bg=self.settings.colors())
        self.info.grid(row=0, column=0, sticky='w', padx=(5, 0), pady=0)
        self.info1 = tk.Label(self, text="", bd=1.2,
                              fg=self.settings.colors(1), bg=self.settings.colors())
        self.info1.grid(row=1, column=0, sticky='w', padx=(5, 0), pady=0)

        self.while_update()

    def set_bind(self):
        # 绑定鼠标事件
        self.bind("<Button-1>", self.start_drag)
        self.bind("<B1-Motion>", self.on_drag)

    def set_geometry(self):
        self.geometry("{w}x{h}+{x}+{y}".format(
            w=self.settings.width, h=self.settings.height,
            x=self.win_width * 2 // 3, y=self.win_height * 2 // 3)
        )

    @staticmethod
    def update_info_content(label, content, idx):
        info_format = "↓ {val} {unit}/s" if idx == 1 else "↑ {val} {unit}/s"
        units = ['KB', 'MB', 'GB', 'TB', 'PB', 'EB']
        unit = 0
        content = float(content) / 1024.0

        while content >= 1024.0:
            content /= 1024.0
            unit += 1
        content = int(content) if content >= 100.0 else round(content, 1)

        content = info_format.format(val=content, unit=units[unit])
        label.config(text=content)

    def while_update(self):
        content, content1 = self.settings.get_net_byte()
        content -= self.content
        content1 -= self.content1

        self.update_info_content(self.info, content, 0)
        self.update_info_content(self.info1, content1, 1)

        self.content, self.content1 = self.settings.get_net_byte()
        self.after(self.settings.update_time, self.while_update)

    def on_close(self):
        # 在这里添加你希望在关闭时执行的任何代码
        self.destroy()

    def start_drag(self, event):
        second_ns = time.time()
        if second_ns - self.second_ns < self.settings.click_close_time_ns:
            self.on_close()
        else:
            self.second_ns = second_ns

        self.x = event.x
        self.y = event.y

    def on_drag(self, event):
        delta_x = event.x - self.x
        delta_y = event.y - self.y
        x = self.winfo_x() + delta_x
        y = self.winfo_y() + delta_y
        x = 0 if x < 0 else x
        y = 0 if y < 0 else y
        x = self.max_x if x > self.max_x else x
        y = self.max_y if y > self.max_y else y
        self.geometry(f"+{x}+{y}")


if __name__ == "__main__":
    app = DraggableWindow()
    app.mainloop()
