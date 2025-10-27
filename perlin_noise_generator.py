import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import matplotlib
import matplotlib.font_manager as fm

# 使用非交互式后端，提高兼容性
matplotlib.use('TkAgg')

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

class PerlinNoiseGenerator:
    def __init__(self):
        # 初始化参数
        self.width = 64
        self.height = 64
        self.scale = 10.0
        self.octaves = 3
        self.persistence = 0.5
        self.lacunarity = 2.0
        self.seed = np.random.randint(0, 10000)
        self.color_map = 'viridis'
        
        # 预计算梯度向量
        np.random.seed(self.seed)
        self.gradients = self._generate_gradients()
        
        # 初始化图形界面
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        plt.subplots_adjust(bottom=0.35)
        
        # 创建滑块控制区域
        self.ax_scale = plt.axes([0.25, 0.25, 0.65, 0.03])
        self.ax_octaves = plt.axes([0.25, 0.2, 0.65, 0.03])
        self.ax_persistence = plt.axes([0.25, 0.15, 0.65, 0.03])
        self.ax_lacunarity = plt.axes([0.25, 0.1, 0.65, 0.03])
        
        # 创建按钮区域
        self.ax_reset = plt.axes([0.1, 0.04, 0.2, 0.05])
        self.ax_new_seed = plt.axes([0.35, 0.04, 0.2, 0.05])
        self.ax_help = plt.axes([0.6, 0.04, 0.2, 0.05])
        
        # 创建滑块和按钮
        self.slider_scale = Slider(self.ax_scale, '缩放比例', 1.0, 50.0, valinit=self.scale)
        self.slider_octaves = Slider(self.ax_octaves, '八度数量', 1, 6, valinit=self.octaves, valstep=1)
        self.slider_persistence = Slider(self.ax_persistence, '持久性', 0.1, 1.0, valinit=self.persistence)
        self.slider_lacunarity = Slider(self.ax_lacunarity, '稀疏度', 1.0, 4.0, valinit=self.lacunarity)
        self.button_reset = Button(self.ax_reset, '重置')
        self.button_new_seed = Button(self.ax_new_seed, '新种子')
        self.button_help = Button(self.ax_help, '帮助')
        
        # 连接事件处理
        self.slider_scale.on_changed(self.update)
        self.slider_octaves.on_changed(self.update)
        self.slider_persistence.on_changed(self.update)
        self.slider_lacunarity.on_changed(self.update)
        self.button_reset.on_clicked(self.reset)
        self.button_new_seed.on_clicked(self.generate_new_seed)
        self.button_help.on_clicked(self.show_help)
        
        # 优化matplotlib性能设置
        plt.rcParams['toolbar'] = 'None'
        plt.ion()
        
        # 初始生成噪声图
        self.update(None)
    
    def _generate_gradients(self):
        # 生成梯度向量和排列表
        p = np.arange(256, dtype=int)
        np.random.shuffle(p)
        p = np.stack([p, p]).flatten()
        return p
    
    def fade(self, t):
        # 缓动函数，用于平滑插值
        return 6 * t**5 - 15 * t**4 + 10 * t**3
    
    def lerp(self, a, b, t):
        # 线性插值
        return a + t * (b - a)
    
    def gradient(self, hash_value, x, y):
        # 根据哈希值选择梯度方向
        h = hash_value & 7
        
        # 使用向量化操作而不是条件语句
        result = np.zeros_like(x)
        
        # 为每个可能的哈希值创建掩码并应用相应的梯度
        result += (h == 0) * (x + y)
        result += (h == 1) * (-x + y)
        result += (h == 2) * (x - y)
        result += (h == 3) * (-x - y)
        result += (h == 4) * (y + x)
        result += (h == 5) * (-y + x)
        result += (h == 6) * (y - x)
        result += (h == 7) * (-y - x)
        
        return result
    
    def perlin(self, x, y):
        # 柏林噪声核心算法
        xi = x.astype(int)
        yi = y.astype(int)
        
        xf = x - xi
        yf = y - yi
        
        # 应用缓动函数
        u = self.fade(xf)
        v = self.fade(yf)
        
        # 使用预计算的梯度
        p = self.gradients
        
        # 计算四个角的哈希值
        n00 = self.gradient(p[p[xi & 255] + (yi & 255)], xf, yf)
        n01 = self.gradient(p[p[xi & 255] + ((yi + 1) & 255)], xf, yf - 1)
        n11 = self.gradient(p[p[(xi + 1) & 255] + ((yi + 1) & 255)], xf - 1, yf - 1)
        n10 = self.gradient(p[p[(xi + 1) & 255] + (yi & 255)], xf - 1, yf)
        
        # 在x方向上插值
        x1 = self.lerp(n00, n10, u)
        x2 = self.lerp(n01, n11, u)
        
        # 在y方向上插值
        return self.lerp(x1, x2, v)
    
    def generate_perlin_noise(self):
        # 生成多层柏林噪声
        x = np.linspace(0, self.scale, self.width, endpoint=False)
        y = np.linspace(0, self.scale, self.height, endpoint=False)
        x, y = np.meshgrid(x, y)
        
        # 生成不同频率的噪声并叠加
        noise = np.zeros_like(x, dtype=np.float32)
        amplitude = 1.0
        frequency = 1.0
        
        for _ in range(int(self.octaves)):
            nx = x * frequency
            ny = y * frequency
            noise += amplitude * self.perlin(nx, ny)
            amplitude *= self.persistence
            frequency *= self.lacunarity
        
        return noise
    
    def update(self, val):
        # 更新函数 - 处理参数变更和图像刷新
        if val is not None:
            if hasattr(val, 'name'):
                if val.name == 'scale':
                    self.scale = val
                elif val.name == 'octaves':
                    self.octaves = int(val)
                elif val.name == 'persistence':
                    self.persistence = val
                elif val.name == 'lacunarity':
                    self.lacunarity = val
            else:
                if self.slider_scale == val:
                    self.scale = val
                elif self.slider_octaves == val:
                    self.octaves = int(val)
                elif self.slider_persistence == val:
                    self.persistence = val
                elif self.slider_lacunarity == val:
                    self.lacunarity = val
        
        # 生成噪声
        noise = self.generate_perlin_noise()
        
        # 清除当前图形并绘制新图
        self.ax.clear()
        self.ax.imshow(noise, cmap=self.color_map, interpolation='bilinear')
        self.ax.set_title(f'柏林噪声生成器 (种子: {self.seed})')
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        
        # 强制更新图形
        self.fig.canvas.draw()
        plt.pause(0.01)
    
    def reset(self, event):
        # 释放鼠标捕获以避免冲突
        try:
            event.canvas.release_mouse(event.inaxes)
        except:
            pass
            
        # 重置所有参数到初始值
        self.scale = 10.0
        self.octaves = 3
        self.persistence = 0.5
        self.lacunarity = 2.0
        
        # 更新滑块
        self.slider_scale.set_val(self.scale)
        self.slider_octaves.set_val(self.octaves)
        self.slider_persistence.set_val(self.persistence)
        self.slider_lacunarity.set_val(self.lacunarity)
        
        # 重新生成图形
        self.update(None)
    
    def generate_new_seed(self, event):
        # 释放鼠标捕获以避免冲突
        try:
            event.canvas.release_mouse(event.inaxes)
        except:
            pass
            
        # 生成新的随机种子
        self.seed = np.random.randint(0, 10000)
        np.random.seed(self.seed)
        self.gradients = self._generate_gradients()
        self.update(None)
    
    def show_help(self, event):
        # 释放鼠标捕获以避免冲突
        try:
            event.canvas.release_mouse(event.inaxes)
        except:
            pass
            
        # 显示帮助对话框
        help_text = """
        柏林噪声生成器使用说明：
        
        缩放比例 (Scale): 控制噪声的比例大小，值越大图案越粗糙。
        八度数量 (Octaves): 控制噪声的细节层次，值越大细节越丰富。
        持久性 (Persistence): 控制每个八度的振幅衰减速率。
        稀疏度 (Lacunarity): 控制每个八度的频率增长速率。
        
        按钮功能：
        - 重置：将所有参数恢复到默认值
        - 新种子：生成新的随机噪声图案
        - 帮助：显示此帮助信息
        
        柏林噪声广泛应用于：
        - 地形生成
        - 纹理创建
        - 程序化内容生成
        - 游戏开发
        """
        
        # 创建帮助对话框
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import tkinter as tk
        from tkinter import scrolledtext
        
        # 创建新窗口
        help_window = tk.Toplevel()
        help_window.title("使用帮助")
        help_window.geometry("500x400")
        help_window.resizable(True, True)
        
        # 创建滚动文本框
        text_area = scrolledtext.ScrolledText(
            help_window,
            wrap=tk.WORD,
            width=50,
            height=20,
            font=("SimHei", 10)
        )
        text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # 插入帮助文本
        text_area.insert(tk.END, help_text)
        text_area.config(state=tk.DISABLED)
        
        # 创建关闭按钮
        close_button = tk.Button(
            help_window,
            text="关闭",
            command=help_window.destroy,
            font=("SimHei", 10)
        )
        close_button.pack(pady=10)
        
        # 确保中文显示正常
        help_window.option_add("*Font", ("SimHei", 10))
    
    def show(self):
        # 显示函数
        plt.show(block=True)

if __name__ == "__main__":
    # 主程序入口
    print("正在初始化柏林噪声生成器...")
    generator = PerlinNoiseGenerator()
    print("生成器初始化完成，正在显示UI...")
    print("提示：点击'帮助'按钮查看使用说明")
    generator.show()
    print("程序已结束。")