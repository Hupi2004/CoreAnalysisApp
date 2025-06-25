# 导入必要的库
import tkinter as tk  # 用于创建图形用户界面（GUI）
from tkinter import ttk, filedialog, messagebox, colorchooser  # 提供更多的GUI组件和对话框功能
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # 用于将matplotlib图形嵌入到Tkinter窗口中
import matplotlib.pyplot as plt  # 用于绘制图表
import cv2  # 用于图像处理
import numpy as np  # 用于数值计算
from matplotlib.figure import Figure  # 用于创建matplotlib图形对象
import csv  # 用于处理CSV文件
import datetime  # 用于处理日期和时间

# 解决matplotlib中文显示问题，设置字体为SimHei，同时解决负号显示问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 假设这几个分析模块函数已实现，若未实现需补充
from hole_analysis import process_stone_holes  # 导入孔洞分析函数
from crack_analysis import process_crack  # 导入裂缝分析函数
from grain_analysis import analyze_grains  # 导入粒度分析函数


class CoreAnalysisApp:
    def __init__(self):
        # 创建主窗口
        self.root = tk.Tk()
        # 设置窗口标题
        self.root.title("地质岩心图文分析系统")

        # 加载图标
        try:
            # 尝试加载图标文件
            self.icon = tk.PhotoImage(file='static/image/gdou.png')
            # 设置窗口图标
            self.root.iconphoto(True, self.icon)
        except Exception as e:
            # 如果加载图标失败，弹出提示框显示错误信息
            messagebox.showwarning("提示", f"图标加载失败：{str(e)}")

        # 设置窗口大小
        self.root.geometry("1200x800")

        # 初始化变量
        self.original_image = None  # 用于存储原始图像
        self.zoom_enabled = False  # 缩放功能开关，初始为关闭状态
        self.pan_enabled = False  # 移动功能开关，初始为关闭状态
        self.pen_enabled = False  # 画笔功能开关，初始为关闭状态
        self.pen_color = 'red'  # 画笔颜色，初始为红色
        self.pen_size = 2  # 画笔大小，初始为2
        self.is_drawing = False  # 是否正在画图的标志，初始为否
        self.last_x = None  # 上一个点的x坐标，初始为None
        self.last_y = None  # 上一个点的y坐标，初始为None
        self.analysis_result = None  # 存储分析结果，初始为None
        self.analysis_type = None  # 存储分析类型，初始为None
        self.plot_type = 'histogram'  # 默认图表类型为柱状图

        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        # 让主框架填充整个窗口并可扩展
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 调用设置菜单栏的函数
        self.setup_menu()
        # 调用设置GUI界面的函数
        self.setup_gui()

    def setup_menu(self):
        # 创建菜单栏
        menubar = tk.Menu(self.root)

        # 创建文件菜单
        filemenu = tk.Menu(menubar, tearoff=0)
        # 添加打开图像的菜单项，点击后调用open_image函数
        filemenu.add_command(label="打开图像", command=self.open_image)
        # 添加退出程序的菜单项，点击后关闭窗口
        filemenu.add_command(label="退出程序", command=self.root.quit)
        # 将文件菜单添加到菜单栏中
        menubar.add_cascade(label="文件", menu=filemenu)

        # 创建分析菜单
        analysis_menu = tk.Menu(menubar, tearoff=0)
        # 添加孔洞分析的菜单项，点击后调用run_analysis函数并传入'hole'参数
        analysis_menu.add_command(label="孔洞分析", command=lambda: self.run_analysis('hole'))
        # 添加裂缝分析的菜单项，点击后调用run_analysis函数并传入'crack'参数
        analysis_menu.add_command(label="裂缝分析", command=lambda: self.run_analysis('crack'))
        # 添加粒度分析的菜单项，点击后调用run_analysis函数并传入'grain'参数
        analysis_menu.add_command(label="粒度分析", command=lambda: self.run_analysis('grain'))
        # 将分析菜单添加到菜单栏中
        menubar.add_cascade(label="分析", menu=analysis_menu)

        # 创建视图菜单
        view_menu = tk.Menu(menubar, tearoff=0)
        # 添加开启缩放的菜单项，点击后调用toggle_zoom函数并传入True参数
        view_menu.add_command(label="开启缩放", command=lambda: self.toggle_zoom(True))
        # 添加关闭缩放的菜单项，点击后调用toggle_zoom函数并传入False参数
        view_menu.add_command(label="关闭缩放", command=lambda: self.toggle_zoom(False))
        # 添加开启移动的菜单项，点击后调用toggle_pan函数并传入True参数
        view_menu.add_command(label="开启移动", command=lambda: self.toggle_pan(True))
        # 添加关闭移动的菜单项，点击后调用toggle_pan函数并传入False参数
        view_menu.add_command(label="关闭移动", command=lambda: self.toggle_pan(False))
        # 将视图菜单添加到菜单栏中
        menubar.add_cascade(label="视图", menu=view_menu)

        # 创建画笔菜单
        pen_menu = tk.Menu(menubar, tearoff=0)
        # 添加开启画笔的菜单项，点击后调用toggle_pen函数并传入True参数
        pen_menu.add_command(label="开启画笔", command=lambda: self.toggle_pen(True))
        # 添加关闭画笔的菜单项，点击后调用toggle_pen函数并传入False参数
        pen_menu.add_command(label="关闭画笔", command=lambda: self.toggle_pen(False))

        # 创建选择颜色子菜单
        color_menu = tk.Menu(pen_menu, tearoff=0)
        # 添加选择颜色的菜单项，点击后调用choose_pen_color函数
        color_menu.add_command(label="选择颜色", command=self.choose_pen_color)
        # 将选择颜色子菜单添加到画笔菜单中
        pen_menu.add_cascade(label="选择颜色", menu=color_menu)

        # 创建选择大小子菜单
        size_menu = tk.Menu(pen_menu, tearoff=0)
        # 循环添加不同大小的菜单项，点击后调用set_pen_size函数并传入相应的大小参数
        for size in [1, 2, 3, 4, 5]:
            size_menu.add_command(label=f"{size}px", command=lambda s=size: self.set_pen_size(s))
        # 将选择大小子菜单添加到画笔菜单中
        pen_menu.add_cascade(label="选择大小", menu=size_menu)
        # 将画笔菜单添加到菜单栏中
        menubar.add_cascade(label="画笔", menu=pen_menu)

        # 创建图表类型菜单
        plot_menu = tk.Menu(menubar, tearoff=0)
        # 添加柱状图的菜单项，点击后调用change_plot_type函数并传入'histogram'参数
        plot_menu.add_command(label="柱状图", command=lambda: self.change_plot_type('histogram'))
        # 添加折线图的菜单项，点击后调用change_plot_type函数并传入'line'参数
        plot_menu.add_command(label="折线图", command=lambda: self.change_plot_type('line'))
        # 添加饼图的菜单项，点击后调用change_plot_type函数并传入'pie'参数
        plot_menu.add_command(label="饼图", command=lambda: self.change_plot_type('pie'))
        # 将图表类型菜单添加到菜单栏中
        menubar.add_cascade(label="图表类型", menu=plot_menu)

        # 创建导出菜单
        export_menu = tk.Menu(menubar, tearoff=0)
        # 添加导出分析结果的菜单项，点击后调用export_analysis_result函数
        export_menu.add_command(label="导出分析结果", command=self.export_analysis_result)
        # 将导出菜单添加到菜单栏中
        menubar.add_cascade(label="导出", menu=export_menu)

        # 将菜单栏设置到主窗口中
        self.root.config(menu=menubar)

    def setup_gui(self):
        # 创建一个2x1的网格布局
        # 图像区域占3份
        self.main_frame.grid_rowconfigure(0, weight=3)
        # 图表区域占1份
        self.main_frame.grid_rowconfigure(1, weight=1)
        # 占满整个宽度
        self.main_frame.grid_columnconfigure(0, weight=1)

        # 创建左侧控制面板
        control_frame = ttk.LabelFrame(self.main_frame, text="参数设置", padding=10)
        # 将控制面板放置在网格布局中
        control_frame.grid(row=0, column=0, rowspan=2, sticky="ns", padx=5, pady=5)

        # 创建孔洞参数框架
        hole_frame = ttk.LabelFrame(control_frame, text="孔洞分析参数", padding=5)
        # 将孔洞参数框架放置在控制面板中
        hole_frame.pack(fill=tk.X, pady=5)

        # 添加孔洞最小面积的标签
        ttk.Label(hole_frame, text="孔洞最小面积:").grid(row=0, column=0, sticky=tk.W, pady=2)
        # 创建孔洞最小面积的输入框
        self.hole_min_area = ttk.Entry(hole_frame, width=10)
        # 在输入框中插入默认值1
        self.hole_min_area.insert(0, "1")
        # 将输入框放置在孔洞参数框架中
        self.hole_min_area.grid(row=0, column=1, sticky=tk.W, pady=2)

        # 添加孔洞最大面积的标签
        ttk.Label(hole_frame, text="孔洞最大面积:").grid(row=1, column=0, sticky=tk.W, pady=2)
        # 创建孔洞最大面积的输入框
        self.hole_max_area = ttk.Entry(hole_frame, width=10)
        # 在输入框中插入默认值1000
        self.hole_max_area.insert(0, "1000")
        # 将输入框放置在孔洞参数框架中
        self.hole_max_area.grid(row=1, column=1, sticky=tk.W, pady=2)

        # 添加孔洞阈值的标签
        ttk.Label(hole_frame, text="孔洞阈值:").grid(row=2, column=0, sticky=tk.W, pady=2)
        # 创建孔洞阈值的输入框
        self.hole_threshold = ttk.Entry(hole_frame, width=10)
        # 在输入框中插入默认值100
        self.hole_threshold.insert(0, "100")
        # 将输入框放置在孔洞参数框架中
        self.hole_threshold.grid(row=2, column=1, sticky=tk.W, pady=2)

        # 创建裂缝参数框架
        crack_frame = ttk.LabelFrame(control_frame, text="裂缝分析参数", padding=5)
        # 将裂缝参数框架放置在控制面板中
        crack_frame.pack(fill=tk.X, pady=5)

        # 添加裂缝最小面积的标签
        ttk.Label(crack_frame, text="裂缝最小面积:").grid(row=0, column=0, sticky=tk.W, pady=2)
        # 创建裂缝最小面积的输入框
        self.crack_min_area = ttk.Entry(crack_frame, width=10)
        # 在输入框中插入默认值1000
        self.crack_min_area.insert(0, "1000")
        # 将输入框放置在裂缝参数框架中
        self.crack_min_area.grid(row=0, column=1, sticky=tk.W, pady=2)

        # 添加裂缝最大面积的标签
        ttk.Label(crack_frame, text="裂缝最大面积:").grid(row=1, column=0, sticky=tk.W, pady=2)
        # 创建裂缝最大面积的输入框
        self.crack_max_area = ttk.Entry(crack_frame, width=10)
        # 在输入框中插入默认值inf
        self.crack_max_area.insert(0, "inf")
        # 将输入框放置在裂缝参数框架中
        self.crack_max_area.grid(row=1, column=1, sticky=tk.W, pady=2)

        # 添加裂缝阈值的标签
        ttk.Label(crack_frame, text="裂缝阈值:").grid(row=2, column=0, sticky=tk.W, pady=2)
        # 创建裂缝阈值的输入框
        self.crack_threshold = ttk.Entry(crack_frame, width=10)
        # 在输入框中插入默认值100
        self.crack_threshold.insert(0, "100")
        # 将输入框放置在裂缝参数框架中
        self.crack_threshold.grid(row=2, column=1, sticky=tk.W, pady=2)

        # 创建右侧区域
        right_frame = ttk.Frame(self.main_frame)
        # 将右侧区域放置在网格布局中
        right_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=5, pady=5)
        # 图像区域占3份
        right_frame.grid_rowconfigure(0, weight=3)
        # 图表区域占1份
        right_frame.grid_rowconfigure(1, weight=1)
        # 占满整个宽度
        right_frame.grid_columnconfigure(0, weight=1)

        # 创建图像显示区域
        image_frame = ttk.LabelFrame(right_frame, text="图像显示", padding=5)
        # 将图像显示区域放置在右侧区域中
        image_frame.grid(row=0, column=0, sticky="nsew", pady=5)
        # 让图像显示区域在网格布局中可扩展
        image_frame.grid_rowconfigure(0, weight=1)
        # 让图像显示区域在网格布局中可扩展
        image_frame.grid_columnconfigure(0, weight=1)

        # 创建2x2网格的图像显示
        self.fig = Figure(figsize=(10, 8), dpi=100)
        # 创建4个子图
        self.axes = [
            self.fig.add_subplot(221),
            self.fig.add_subplot(222),
            self.fig.add_subplot(223),
            self.fig.add_subplot(224)
        ]
        # 将matplotlib图形嵌入到Tkinter窗口中
        self.canvas = FigureCanvasTkAgg(self.fig, master=image_frame)
        # 获取嵌入后的Tkinter组件
        self.canvas_widget = self.canvas.get_tk_widget()
        # 将组件放置在图像显示区域中
        self.canvas_widget.grid(row=0, column=0, sticky="nsew")

        # 创建图表显示区域
        chart_frame = ttk.LabelFrame(right_frame, text="分析结果图表", padding=5)
        # 将图表显示区域放置在右侧区域中
        chart_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        # 让图表显示区域在网格布局中可扩展
        chart_frame.grid_rowconfigure(0, weight=1)
        # 让图表显示区域在网格布局中可扩展
        chart_frame.grid_columnconfigure(0, weight=1)

        # 创建图表显示
        self.chart_fig = Figure(figsize=(10, 4), dpi=100)
        # 创建一个子图
        self.chart_ax = self.chart_fig.add_subplot(111)
        # 将matplotlib图表嵌入到Tkinter窗口中
        self.chart_canvas = FigureCanvasTkAgg(self.chart_fig, master=chart_frame)
        # 获取嵌入后的Tkinter组件
        self.chart_canvas_widget = self.chart_canvas.get_tk_widget()
        # 将组件放置在图表显示区域中
        self.chart_canvas_widget.grid(row=0, column=0, sticky="nsew")

        # 创建结果信息区域
        self.result_frame = ttk.LabelFrame(right_frame, text="分析结果信息", padding=5)
        # 将结果信息区域放置在右侧区域中
        self.result_frame.grid(row=2, column=0, sticky="ew", pady=5)

        # 创建结果信息文本框
        self.result_text = tk.Text(self.result_frame, height=3, wrap=tk.WORD)
        # 将文本框放置在结果信息区域中
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # 调用清空图像、图表和结果信息的函数
        self.clear_axes()

        # 绑定鼠标事件
        # 绑定鼠标滚动事件，调用zoom函数
        self.canvas.mpl_connect('scroll_event', self.zoom)
        # 绑定鼠标按下事件，调用on_mouse_press函数
        self.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        # 绑定鼠标释放事件，调用on_mouse_release函数
        self.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        # 绑定鼠标移动事件，调用on_mouse_motion函数
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_motion)

        # 初始化移动状态
        self.press = None

    def clear_axes(self):
        # 清空图像显示区域
        for ax in self.axes:
            # 清空子图
            ax.clear()
            # 关闭坐标轴显示
            ax.axis('off')
        # 调整布局参数
        self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        # 重新绘制图像
        self.canvas.draw()

        # 清空图表显示区域
        self.chart_ax.clear()
        # 关闭坐标轴显示
        self.chart_ax.axis('off')
        # 调整布局参数
        self.chart_fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        # 重新绘制图表
        self.chart_canvas.draw()

        # 清空结果信息区域
        self.result_text.delete(1.0, tk.END)

    def open_image(self):
        # 弹出文件选择对话框，选择图像文件
        file_path = filedialog.askopenfilename(
            filetypes=[("图像文件", "*.jpg *.png *.bmp *.jpeg *.tif")]
        )
        # 如果没有选择文件，直接返回
        if not file_path:
            return
        # 读取选择的图像文件
        self.original_image = cv2.imread(file_path)
        # 如果读取失败，弹出错误提示框
        if self.original_image is None:
            messagebox.showerror("错误", "无法读取图像文件")
            return
        # 清空之前的图像
        self.clear_axes()
        # 显示原始图像
        self.axes[0].imshow(cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB))
        # 设置子图标题
        self.axes[0].set_title("原图")
        # 调整布局参数
        self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        # 重新绘制图像
        self.canvas.draw()

    def run_analysis(self, analysis_type):
        # 如果没有打开图像，弹出提示框
        if self.original_image is None:
            messagebox.showwarning("提示", "请先打开图像")
            return
        try:
            if analysis_type == 'hole':
                # 获取孔洞最小面积的输入值并转换为浮点数
                min_area = float(self.hole_min_area.get())
                # 获取孔洞最大面积的输入值，如果是inf则转换为正无穷大
                max_area = float(self.hole_max_area.get()) if self.hole_max_area.get() != "inf" else np.inf
                # 获取孔洞阈值的输入值并转换为整数
                threshold_val = int(self.hole_threshold.get())
                # 调用孔洞分析函数进行分析
                result, gray, binary, marked = process_stone_holes(
                    self.original_image, min_area, max_area, threshold_val
                )
                # 存储分析结果
                self.analysis_result = result
                # 存储分析类型
                self.analysis_type = 'hole'
                # 更新图像显示
                self.axes[0].imshow(cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB))
                self.axes[0].set_title("原图")
                self.axes[1].imshow(gray, cmap='gray')
                self.axes[1].set_title("灰度图")
                self.axes[2].imshow(binary, cmap='gray')
                self.axes[2].set_title("二值图")
                self.axes[3].imshow(cv2.cvtColor(marked, cv2.COLOR_BGR2RGB))
                self.axes[3].set_title("孔洞标记图")
                # 调整布局参数
                self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
                # 重新绘制图像
                self.canvas.draw()
                # 更新结果信息
                info = (
                    f"孔洞数量: {result['孔洞数量']}\n"
                    f"总面积: {result['总面积']:.2f}\n"
                    f"平均面积: {result['平均面积']:.2f}\n"
                    f"平均圆形度: {result['平均圆形度']:.2f}"
                )
                # 清空结果信息文本框
                self.result_text.delete(1.0, tk.END)
                # 将结果信息插入到文本框中
                self.result_text.insert(tk.END, info)
                # 绘制孔洞面积分布图表
                self.plot_distribution(result['面积列表'], "孔洞面积分布", "面积")
            elif analysis_type == 'crack':
                # 获取裂缝最小面积的输入值并转换为浮点数
                min_area = float(self.crack_min_area.get())
                # 获取裂缝最大面积的输入值，如果是inf则转换为正无穷大
                max_area = float(self.crack_max_area.get()) if self.crack_max_area.get() != "inf" else np.inf
                # 获取裂缝阈值的输入值并转换为整数
                threshold_val = int(self.crack_threshold.get())
                # 调用裂缝分析函数进行分析
                result = process_crack(self.original_image, min_area, max_area, threshold_val)
                # 存储分析结果
                self.analysis_result = result
                # 存储分析类型
                self.analysis_type = 'crack'

                # 确保结果包含所有需要的图像
                if '二值图' not in result or '结果图' not in result:
                    messagebox.showerror("错误", "裂缝分析结果不完整，请检查分析函数")
                    return

                # 更新图像显示
                self.axes[0].imshow(cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB))
                self.axes[0].set_title("原图")
                self.axes[1].imshow(result['二值图'], cmap='gray')
                self.axes[1].set_title("二值图")
                self.axes[2].imshow(cv2.cvtColor(result['结果图'], cv2.COLOR_BGR2RGB))
                self.axes[2].set_title("裂缝标记图")
                self.axes[3].axis('off')
                # 调整布局参数
                self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
                # 重新绘制图像
                self.canvas.draw()

                # 更新结果信息
                if '特征' in result and result['特征']:
                    features = result['特征']

                    # 检查最大裂缝长度是否为0
                    if '最大裂缝长度' in features and features['最大裂缝长度'] <= 0:
                        # 如果为0，尝试从裂缝列表中计算
                        if '裂缝列表' in result and len(result['裂缝列表']) > 0:
                            max_length = 0
                            for crack in result['裂缝列表']:
                                if '长度' in crack and crack['长度'] > max_length:
                                    max_length = crack['长度']

                            if max_length > 0:
                                features['最大裂缝长度'] = max_length
                                messagebox.showinfo("提示", "已重新计算最大裂缝长度")
                            else:
                                messagebox.showinfo("提示", "无法计算最大裂缝长度，请检查裂缝分析算法")
                        else:
                            messagebox.showinfo("提示", "没有找到裂缝数据，请检查裂缝分析算法")

                    info = (
                        f"裂缝数量: {features['数量']}\n"
                        f"总面积: {features['总面积']:.2f} 像素\n"
                        f"平均面积: {features['平均面积']:.2f} 像素\n"
                        f"最大裂缝方向: {features['最大裂缝方向']}\n"
                        f"最大裂缝长度: {features['最大裂缝长度']:.2f} 像素\n"
                        f"最大裂缝最大宽度: {features['最大裂缝最大宽度']:.2f} 像素\n"
                        f"最大裂缝最小宽度: {features['最大裂缝最小宽度']:.2f} 像素"
                    )
                    # 清空结果信息文本框
                    self.result_text.delete(1.0, tk.END)
                    # 将结果信息插入到文本框中
                    self.result_text.insert(tk.END, info)
                else:
                    # 清空结果信息文本框
                    self.result_text.delete(1.0, tk.END)
                    # 将未检测到裂缝的信息插入到文本框中
                    self.result_text.insert(tk.END, "未检测到符合条件的裂缝")

                # 准备裂缝宽度数据用于图表
                if '裂缝宽度列表' in result and len(result['裂缝宽度列表']) > 0:
                    # 过滤掉零值和负值
                    width_data = [w for w in result['裂缝宽度列表'] if w > 0]

                    if len(width_data) > 0:
                        # 绘制裂缝宽度分布图表
                        self.plot_distribution(width_data, "裂缝宽度分布", "宽度")
                    else:
                        messagebox.showinfo("提示", "未检测到有效裂缝宽度数据")
                        # 清空图表
                        self.chart_ax.clear()
                        # 在图表中显示无有效数据的信息
                        self.chart_ax.text(0.5, 0.5, "无有效裂缝宽度数据", ha='center', va='center', fontsize=14)
                        # 关闭坐标轴显示
                        self.chart_ax.axis('off')
                        # 调整布局参数
                        self.chart_fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
                        # 重新绘制图表
                        self.chart_canvas.draw()
                else:
                    messagebox.showinfo("提示", "未检测到有效裂缝宽度数据")
                    # 清空图表
                    self.chart_ax.clear()
                    # 在图表中显示无有效数据的信息
                    self.chart_ax.text(0.5, 0.5, "无有效裂缝宽度数据", ha='center', va='center', fontsize=14)
                    # 关闭坐标轴显示
                    self.chart_ax.axis('off')
                    # 调整布局参数
                    self.chart_fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
                    # 重新绘制图表
                    self.chart_canvas.draw()
            elif analysis_type == 'grain':
                # 调用粒度分析函数进行分析
                result, gray, binary, marked = analyze_grains(self.original_image)
                # 存储分析结果
                self.analysis_result = result
                # 存储分析类型
                self.analysis_type = 'grain'
                # 更新图像显示
                self.axes[0].imshow(cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB))
                self.axes[0].set_title("原图")
                self.axes[1].imshow(gray, cmap='gray')
                self.axes[1].set_title("灰度图")
                self.axes[2].imshow(binary, cmap='gray')
                self.axes[2].set_title("二值图")
                self.axes[3].imshow(cv2.cvtColor(marked, cv2.COLOR_BGR2RGB))
                self.axes[3].set_title("粒子标记图")
                # 调整布局参数
                self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
                # 重新绘制图像
                self.canvas.draw()
                # 更新结果信息
                info = (
                    f"粒子数量: {result['粒子数量']}\n"
                    f"平均面积: {result['平均面积']:.2f} 像素"
                )
                # 清空结果信息文本框
                self.result_text.delete(1.0, tk.END)
                # 将结果信息插入到文本框中
                self.result_text.insert(tk.END, info)
                # 绘制粒度分布图表
                self.plot_distribution(result['面积列表'], "粒度分布", "面积")
        except ValueError:
            # 如果输入参数格式错误，弹出错误提示框
            messagebox.showerror("错误", "参数输入有误，请检查数值格式")
            return
        except Exception as e:
            # 如果分析过程中发生其他错误，弹出错误提示框
            messagebox.showerror("错误", f"分析过程中发生错误: {str(e)}")
            return

    def plot_distribution(self, data, title, xlabel):
        """通用图表绘制函数"""
        # 清空图表
        self.chart_ax.clear()

        # 如果数据为空，在图表中显示无有效数据的信息
        if not data or len(data) == 0:
            self.chart_ax.text(0.5, 0.5, "无有效数据", ha='center', va='center', fontsize=14)
            # 关闭坐标轴显示
            self.chart_ax.axis('off')
        else:
            # 打开坐标轴显示
            self.chart_ax.axis('on')
            # 设置图表标题
            self.chart_ax.set_title(title, fontsize=14, pad=10)

            # 过滤掉零值和负值
            filtered_data = [d for d in data if d > 0]

            # 如果过滤后的数据为空，在图表中显示数据无效的信息
            if len(filtered_data) == 0:
                self.chart_ax.text(0.5, 0.5, "数据无效", ha='center', va='center', fontsize=14)
                # 关闭坐标轴显示
                self.chart_ax.axis('off')
                # 调整布局参数
                self.chart_fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
                # 重新绘制图表
                self.chart_canvas.draw()
                return

            if self.plot_type == 'histogram':
                # 绘制直方图
                # 自动计算合适的分箱数
                if len(filtered_data) < 10:
                    bins = len(filtered_data)
                elif len(filtered_data) < 50:
                    bins = min(10, len(set(filtered_data)))
                else:
                    bins = min(20, len(set(filtered_data)))

                # 绘制直方图
                n, bins, patches = self.chart_ax.hist(filtered_data, bins=bins, edgecolor='black', color='skyblue',
                                                      alpha=0.8)
                # 设置x轴标签
                self.chart_ax.set_xlabel(xlabel, fontsize=12)
                # 设置y轴标签
                self.chart_ax.set_ylabel("数量", fontsize=12)

                # 添加网格线
                self.chart_ax.grid(axis='y', linestyle='--', alpha=0.7)

                # 添加数值标签
                for i in range(len(patches)):
                    if n[i] > 0:
                        self.chart_ax.text(
                            patches[i].get_x() + patches[i].get_width() / 2,
                            patches[i].get_height(),
                            f"{int(n[i])}",
                            ha='center', va='bottom', fontsize=10
                        )

                # 调整x轴范围，排除极端值
                q1 = np.percentile(filtered_data, 25)
                q3 = np.percentile(filtered_data, 75)
                iqr = q3 - q1
                lower_bound = max(0, q1 - 1.5 * iqr)
                upper_bound = q3 + 1.5 * iqr

                # 如果数据分布比较集中，稍微扩大范围
                if upper_bound - lower_bound < np.mean(filtered_data) * 0.1:
                    margin = np.mean(filtered_data) * 0.1
                    lower_bound = max(0, np.mean(filtered_data) - margin)
                    upper_bound = np.mean(filtered_data) + margin

                # 确保图表显示合理范围
                if len(filtered_data) > 5:  # 只有当有足够数据时才调整范围
                    self.chart_ax.set_xlim(lower_bound, upper_bound)
            elif self.plot_type == 'line':
                # 绘制折线图
                # 对数据进行排序
                sorted_data = sorted(filtered_data)
                # 绘制折线图
                self.chart_ax.plot(sorted_data, marker='o', linestyle='-', markersize=4, linewidth=2, color='blue')
                # 设置x轴标签
                self.chart_ax.set_xlabel("序号", fontsize=12)
                # 设置y轴标签
                self.chart_ax.set_ylabel(xlabel, fontsize=12)
                # 添加网格线
                self.chart_ax.grid(True, linestyle='--', alpha=0.7)

                # 调整y轴范围，排除极端值
                q1 = np.percentile(filtered_data, 25)
                q3 = np.percentile(filtered_data, 75)
                iqr = q3 - q1
                lower_bound = max(0, q1 - 1.5 * iqr)
                upper_bound = q3 + 1.5 * iqr

                # 如果数据分布比较集中，稍微扩大范围
                if upper_bound - lower_bound < np.mean(filtered_data) * 0.1:
                    margin = np.mean(filtered_data) * 0.1
                    lower_bound = max(0, np.mean(filtered_data) - margin)
                    upper_bound = np.mean(filtered_data) + margin

                # 确保图表显示合理范围
                if len(filtered_data) > 5:  # 只有当有足够数据时才调整范围
                    self.chart_ax.set_ylim(lower_bound, upper_bound)
            elif self.plot_type == 'pie':
                # 绘制饼图
                if self.analysis_type == 'hole':
                    # 可以将孔洞按面积大小分组
                    total_area = sum(filtered_data)
                    if total_area > 0:
                        small = sum(1 for d in filtered_data if d < np.mean(filtered_data) / 2)
                        medium = sum(
                            1 for d in filtered_data if np.mean(filtered_data) / 2 <= d < np.mean(filtered_data) * 2)
                        large = sum(1 for d in filtered_data if d >= np.mean(filtered_data) * 2)

                        sizes = [small, medium, large]
                        labels = ['小', '中', '大']
                        colors = ['#ff9999', '#66b3ff', '#99ff99']

                        # 确保没有空的部分
                        valid_sizes = []
                        valid_labels = []
                        valid_colors = []

                        for i, size in enumerate(sizes):
                            if size > 0:
                                valid_sizes.append(size)
                                valid_labels.append(labels[i])
                                valid_colors.append(colors[i])

                        if len(valid_sizes) > 0:
                            self.chart_ax.pie(valid_sizes, labels=valid_labels, colors=valid_colors, autopct='%1.1f%%',
                                              startangle=90, shadow=True,
                                              explode=(0.1, 0, 0) if len(valid_sizes) > 1 else None,
                                              textprops={'fontsize': 10})
                            self.chart_ax.set_title("孔洞大小分布", fontsize=14)
                        else:
                            self.chart_ax.text(0.5, 0.5, "数据不足以生成饼图", ha='center', va='center', fontsize=12)
                            # 关闭坐标轴显示
                            self.chart_ax.axis('off')
                elif self.analysis_type == 'crack':
                    # 可以将裂缝按宽度分组
                    if len(filtered_data) > 0:
                        narrow = sum(1 for d in filtered_data if d < np.mean(filtered_data) / 2)
                        medium = sum(
                            1 for d in filtered_data if np.mean(filtered_data) / 2 <= d < np.mean(filtered_data) * 2)
                        wide = sum(1 for d in filtered_data if d >= np.mean(filtered_data) * 2)

                        sizes = [narrow, medium, wide]
                        labels = ['窄', '中', '宽']
                        colors = ['#ff9999', '#66b3ff', '#99ff99']

                        # 确保没有空的部分
                        valid_sizes = []
                        valid_labels = []
                        valid_colors = []

                        for i, size in enumerate(sizes):
                            if size > 0:
                                valid_sizes.append(size)
                                valid_labels.append(labels[i])
                                valid_colors.append(colors[i])

                        if len(valid_sizes) > 0:
                            self.chart_ax.pie(valid_sizes, labels=valid_labels, colors=valid_colors, autopct='%1.1f%%',
                                              startangle=90, shadow=True,
                                              explode=(0.1, 0, 0) if len(valid_sizes) > 1 else None,
                                              textprops={'fontsize': 10})
                            self.chart_ax.set_title("裂缝宽度分布", fontsize=14)
                        else:
                            self.chart_ax.text(0.5, 0.5, "数据不足以生成饼图", ha='center', va='center', fontsize=12)
                            # 关闭坐标轴显示
                            self.chart_ax.axis('off')
                elif self.analysis_type == 'grain':
                    # 可以将粒子按面积大小分组
                    total_area = sum(filtered_data)
                    if total_area > 0:
                        small = sum(1 for d in filtered_data if d < np.mean(filtered_data) / 2)
                        medium = sum(
                            1 for d in filtered_data if np.mean(filtered_data) / 2 <= d < np.mean(filtered_data) * 2)
                        large = sum(1 for d in filtered_data if d >= np.mean(filtered_data) * 2)

                        sizes = [small, medium, large]
                        labels = ['小', '中', '大']
                        colors = ['#ff9999', '#66b3ff', '#99ff99']

                        # 确保没有空的部分
                        valid_sizes = []
                        valid_labels = []
                        valid_colors = []

                        for i, size in enumerate(sizes):
                            if size > 0:
                                valid_sizes.append(size)
                                valid_labels.append(labels[i])
                                valid_colors.append(colors[i])

                        if len(valid_sizes) > 0:
                            self.chart_ax.pie(valid_sizes, labels=valid_labels, colors=valid_colors, autopct='%1.1f%%',
                                              startangle=90, shadow=True,
                                              explode=(0.1, 0, 0) if len(valid_sizes) > 1 else None,
                                              textprops={'fontsize': 10})
                            self.chart_ax.set_title("粒子大小分布", fontsize=14)
                        else:
                            self.chart_ax.text(0.5, 0.5, "数据不足以生成饼图", ha='center', va='center', fontsize=12)
                            # 关闭坐标轴显示
                            self.chart_ax.axis('off')

        # 调整布局参数
        self.chart_fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        # 重新绘制图表
        self.chart_canvas.draw()

    def change_plot_type(self, plot_type):
        """更改图表类型"""
        # 如果已经是该类型，不做任何操作
        if plot_type == self.plot_type:
            return

        # 更新图表类型
        self.plot_type = plot_type
        if self.analysis_result and self.analysis_type:
            # 根据分析类型和结果绘制相应的图表
            if self.analysis_type == 'hole':
                if '面积列表' in self.analysis_result and len(self.analysis_result['面积列表']) > 0:
                    # 过滤掉零值和负值
                    area_data = [a for a in self.analysis_result['面积列表'] if a > 0]
                    if len(area_data) > 0:
                        # 绘制孔洞面积分布图表
                        self.plot_distribution(area_data, "孔洞面积分布", "面积")
                    else:
                        messagebox.showinfo("提示", "孔洞分析结果中没有有效面积数据")
                else:
                    messagebox.showinfo("提示", "孔洞分析结果中没有面积数据")
            elif self.analysis_type == 'crack':
                if '裂缝宽度列表' in self.analysis_result and len(self.analysis_result['裂缝宽度列表']) > 0:
                    # 过滤掉零值和负值
                    width_data = [w for w in self.analysis_result['裂缝宽度列表'] if w > 0]
                    if len(width_data) > 0:
                        # 绘制裂缝宽度分布图表
                        self.plot_distribution(width_data, "裂缝宽度分布", "宽度")
                    else:
                        messagebox.showinfo("提示", "裂缝分析结果中没有有效宽度数据")
                else:
                    messagebox.showinfo("提示", "裂缝分析结果中没有宽度数据")
            elif self.analysis_type == 'grain':
                if '面积列表' in self.analysis_result and len(self.analysis_result['面积列表']) > 0:
                    # 过滤掉零值和负值
                    area_data = [a for a in self.analysis_result['面积列表'] if a > 0]
                    if len(area_data) > 0:
                        # 绘制粒度分布图表
                        self.plot_distribution(area_data, "粒度分布", "面积")
                    else:
                        messagebox.showinfo("提示", "粒度分析结果中没有有效面积数据")
                else:
                    messagebox.showinfo("提示", "粒度分析结果中没有面积数据")
        else:
            messagebox.showinfo("提示", "请先进行分析，再查看图表")

    def zoom(self, event):
        # 检查缩放功能是否开启
        if not self.zoom_enabled:
            return
        # 获取鼠标所在的子图
        ax = event.inaxes
        if ax is None:
            return
        # 获取鼠标的x和y坐标
        x, y = event.xdata, event.ydata
        # 调整缩放因子以提升灵敏度
        scale_factor = 1.2 if event.button == 'up' else 1 / 1.2
        # 调整子图的x轴范围
        ax.set_xlim((x - (x - ax.get_xlim()[0]) * scale_factor,
                     x + (ax.get_xlim()[1] - x) * scale_factor))
        # 调整子图的y轴范围
        ax.set_ylim((y - (y - ax.get_ylim()[0]) * scale_factor,
                     y + (ax.get_ylim()[1] - y) * scale_factor))
        # 调整布局参数
        self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        # 重新绘制图像
        self.canvas.draw()

    def on_mouse_press(self, event):
        # 如果鼠标不在子图内，直接返回
        if event.inaxes is None:
            return

        # 处理画笔功能 - 左键按下开始画图
        if self.pen_enabled and event.button == 1:  # 1表示左键
            # 设置正在画图的标志为True
            self.is_drawing = True
            # 记录当前鼠标的x和y坐标
            self.last_x, self.last_y = event.xdata, event.ydata
            return

        # 处理图像移动功能
        if self.pan_enabled:  # 检查移动功能是否开启
            # 记录鼠标按下时的x和y坐标
            self.press = event.xdata, event.ydata

    def on_mouse_release(self, event):
        # 处理画笔功能 - 释放鼠标停止画图
        if self.is_drawing:
            # 设置正在画图的标志为False
            self.is_drawing = False
            # 重置上一个点的x和y坐标
            self.last_x = None
            self.last_y = None
            return

        # 处理图像移动功能
        if self.pan_enabled:  # 检查移动功能是否开启
            # 重置移动状态
            self.press = None

    def on_mouse_motion(self, event):
        # 如果鼠标不在子图内，直接返回
        if event.inaxes is None:
            return

        # 处理画笔功能 - 画图
        if self.is_drawing and self.last_x is not None and self.last_y is not None:
            # 获取鼠标所在的子图
            ax = event.inaxes
            # 获取当前鼠标的x和y坐标
            x, y = event.xdata, event.ydata
            # 在子图中绘制线段
            ax.plot([self.last_x, x], [self.last_y, y], color=self.pen_color, linewidth=self.pen_size)
            # 调整布局参数
            self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
            # 重新绘制图像
            self.canvas.draw()
            # 更新上一个点的x和y坐标
            self.last_x, self.last_y = x, y
            return

        # 处理图像移动功能
        if self.pan_enabled and self.press is not None:  # 检查移动功能是否开启
            # 计算鼠标移动的距离
            dx = event.xdata - self.press[0]
            dy = event.ydata - self.press[1]
            # 降低移动灵敏度
            sensitivity = 0.4  # 可以根据需要调整这个值，值越小越不灵敏
            dx *= sensitivity
            dy *= sensitivity
            # 获取鼠标所在的子图
            ax = event.inaxes
            # 获取子图的x轴范围
            xlim = ax.get_xlim()
            # 获取子图的y轴范围
            ylim = ax.get_ylim()
            # 调整子图的x轴范围
            ax.set_xlim(xlim[0] - dx, xlim[1] - dx)
            # 调整子图的y轴范围
            ax.set_ylim(ylim[0] - dy, ylim[1] - dy)
            # 更新鼠标按下时的x和y坐标
            self.press = event.xdata, event.ydata
            # 减少不必要的更新
            # 调整布局参数
            self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
            # 重新绘制图像
            self.canvas.draw()

    def toggle_zoom(self, enable):
        # 更新缩放功能开关状态
        self.zoom_enabled = enable

    def toggle_pan(self, enable):
        # 更新移动功能开关状态
        self.pan_enabled = enable
        if not enable:  # 如果关闭移动，重置移动状态
            self.press = None

    def toggle_pen(self, enable):
        # 更新画笔功能开关状态
        self.pen_enabled = enable
        # 如果关闭画笔，重置画图状态
        if not enable:
            self.is_drawing = False
            self.last_x = None
            self.last_y = None

    def choose_pen_color(self):
        # 弹出颜色选择对话框，获取选择的颜色
        color = colorchooser.askcolor()[1]
        if color:
            # 更新画笔颜色
            self.pen_color = color

    def set_pen_size(self, size):
        # 更新画笔大小
        self.pen_size = size

    def export_analysis_result(self):
        # 如果没有分析结果，弹出提示框
        if self.analysis_result is None:
            messagebox.showwarning("提示", "请先进行分析，再导出结果")
            return


if __name__ == "__main__":
    # 创建地质岩心图文分析系统的实例
    app = CoreAnalysisApp()
    # 进入主事件循环，保持窗口显示
    app.root.mainloop()
