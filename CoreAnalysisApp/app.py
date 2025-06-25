# 导入必要的库
import os
import cv2
import numpy as np
import json
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io
import base64
import sys
import time
import importlib.metadata  # 用于获取Flask版本

# 尝试导入裂缝分析模块
print("正在导入裂缝分析模块...")
try:
    # 从crack_analysis模块导入process_crack函数
    from crack_analysis import process_crack
    print("裂缝分析模块导入成功")

except ImportError as e:
    # 如果导入失败，打印错误信息
    print(f"裂缝分析模块导入失败: {e}")
    # 定义一个模拟函数用于测试
    def process_crack(image, min_area, max_area, threshold):
        print("使用模拟裂缝分析函数")
        # 返回模拟的分析结果
        return {
            '特征': {
                '数量': 0,
                '总面积': 0,
                '平均面积': 0,
                '最大裂缝方向': 0,
                '最大裂缝长度': 0,
                '最大裂缝最大宽度': 0,
                '最大裂缝最小宽度': 0
            },
            '原图': image,
            '二值图': image,
            '结果图': image,
            '裂缝宽度列表': []
        }

# 尝试导入粒度分析模块
print("正在导入粒度分析模块...")
try:
    # 从grain_analysis模块导入analyze_grains函数
    from grain_analysis import analyze_grains
    print("粒度分析模块导入成功")
except ImportError as e:
    # 如果导入失败，打印错误信息
    print(f"粒度分析模块导入失败: {e}")
    # 定义一个模拟函数用于测试
    def analyze_grains(image):
        print("使用模拟粒度分析函数")
        # 返回模拟的分析结果
        return {
            '粒子数量': 0,
            '平均面积': 0,
            '面积列表': []
        }, image, image, image

# 尝试导入孔洞分析模块
print("正在导入孔洞分析模块...")
try:
    # 从hole_analysis模块导入process_stone_holes函数
    from hole_analysis import process_stone_holes
    print("孔洞分析模块导入成功")
except ImportError as e:
    # 如果导入失败，打印错误信息
    print(f"孔洞分析模块导入失败: {e}")
    # 定义一个模拟函数用于测试
    def process_stone_holes(image, min_area, max_area, threshold):
        print("使用模拟孔洞分析函数")
        # 返回模拟的分析结果
        return {
            '孔洞数量': 0,
            '总面积': 0,
            '平均面积': 0,
            '平均圆形度': 0,
            '面积列表': []
        }, image, image, image

# 配置Flask应用
app = Flask(__name__)
# 设置上传文件的保存目录
app.config['UPLOAD_FOLDER'] = 'uploads'
# 限制上传文件的最大大小为16MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# 确保上传目录存在，如果不存在则创建
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 设置matplotlib支持中文
# 使用黑体字体来显示中文
plt.rcParams['font.sans-serif'] = ['SimHei']
# 解决负号显示问题
plt.rcParams['axes.unicode_minus'] = False

# 定义一个函数，将OpenCV图像转换为Base64编码字符串
def image_to_base64(image):
    """将OpenCV图像转换为Base64编码字符串"""
    try:
        # 如果图像是彩色图像，将其从BGR格式转换为RGB格式
        if len(image.shape) == 3:
            img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # 如果图像是灰度图像，将其转换为RGB格式
        else:
            img_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        # 将图像编码为PNG格式
        _, buffer = cv2.imencode('.png', img_rgb)
        # 将编码后的图像数据转换为Base64编码字符串
        return base64.b64encode(buffer).decode('utf-8')
    except Exception as e:
        # 如果转换失败，打印错误信息
        print(f"图像转换为Base64失败: {e}")
        return None

# 定义一个函数，创建直方图并返回Base64编码字符串
def create_histogram(data, title, x_label, y_label):
    """创建直方图并返回Base64编码字符串"""
    try:
        # 如果数据为空，打印警告信息并返回None
        if not data or len(data) == 0:
            print("警告: 直方图数据为空")
            return None
        # 创建一个图形和坐标轴对象
        fig, ax = plt.subplots(figsize=(10, 6))
        # 绘制直方图
        ax.hist(data, bins=20, alpha=0.7, color='skyblue')
        # 设置图形的标题
        ax.set_title(title)
        # 设置x轴的标签
        ax.set_xlabel(x_label)
        # 设置y轴的标签
        ax.set_ylabel(y_label)
        # 显示网格线
        ax.grid(True, linestyle='--', alpha=0.7)
        # 将图形转换为Base64编码字符串
        canvas = FigureCanvas(fig)
        output = io.BytesIO()
        canvas.print_png(output)
        plt.close(fig)
        return base64.b64encode(output.getvalue()).decode('utf-8')
    except Exception as e:
        # 如果创建直方图失败，打印错误信息
        print(f"创建直方图失败: {e}")
        return None

# 定义一个函数，递归转换数据为可序列化格式
def convert_to_serializable(data):
    """递归转换数据为可序列化格式"""
    try:
        # 如果数据是NumPy数组，将其转换为列表
        if isinstance(data, np.ndarray):
            return data.tolist()
        # 如果数据是NumPy浮点型，将其转换为Python浮点型
        elif isinstance(data, np.float32):
            return float(data)
        # 如果数据是NumPy整型，将其转换为Python整型
        elif isinstance(data, np.int32):
            return int(data)
        # 如果数据是字典，递归转换字典中的每个值
        elif isinstance(data, dict):
            return {key: convert_to_serializable(value) for key, value in data.items()}
        # 如果数据是列表，递归转换列表中的每个元素
        elif isinstance(data, list):
            return [convert_to_serializable(item) for item in data]
        # 如果数据是集合，将其转换为列表
        elif isinstance(data, set):
            return list(data)
        # 如果数据是基本数据类型，直接返回
        elif isinstance(data, (int, float, str, bool, type(None))):
            return data
        else:
            # 如果数据类型无法序列化，打印警告信息并将其转换为字符串
            print(f"警告: 无法序列化类型 {type(data)}")
            return str(data)
    except Exception as e:
        # 如果序列化数据失败，打印错误信息
        print(f"序列化数据失败: {e}")
        return None

# 定义根路由，返回主页面
@app.route('/')
def index():
    """返回主页面"""
    return render_template('index.html')

# 定义文件上传路由，处理文件上传请求
@app.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传"""
    try:
        print("[文件上传] 接收到上传请求")
        # 检查请求中是否包含文件
        if 'file' not in request.files:
            return jsonify({'error': '没有文件'}), 400
        # 获取上传的文件
        file = request.files['file']
        # 检查文件名是否为空
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        # 确保文件名安全
        filename = secure_filename(file.filename)
        # 构建文件保存的路径
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # 保存文件
        print(f"[文件上传] 保存文件: {filepath}")
        file.save(filepath)
        # 读取图像
        print(f"[文件上传] 读取图像: {filepath}")
        image = cv2.imread(filepath)
        # 检查图像是否读取成功
        if image is None:
            return jsonify({'error': f'无法读取图像: {filepath}'}), 400
        # 将图像转换为Base64编码字符串
        base64_image = image_to_base64(image)
        print(f"[文件上传] 上传成功: {filename}")
        # 返回上传成功的信息
        return jsonify({
            'success': True,
            'filename': filename,
            'image': base64_image
        })
    except Exception as e:
        # 如果上传失败，打印错误信息并返回错误响应
        print(f"[文件上传] 错误: {e}")
        return jsonify({'error': f'文件上传失败: {str(e)}'}), 500

# 定义裂缝分析路由，处理裂缝分析请求
@app.route('/analyze/cracks', methods=['POST'])
def analyze_cracks_route():
    """处理裂缝分析请求"""
    try:
        # 记录请求开始时间
        start_time = time.time()
        print("\n" + "=" * 50)
        print("[裂缝分析] 接收到分析请求")
        # 获取请求数据
        data = request.get_json()
        # 检查请求数据是否为空
        if not data:
            print("[裂缝分析] 错误: 空请求数据")
            return jsonify({'error': '请求数据为空'}), 400
        # 提取请求数据中的参数
        filename = data.get('filename')
        min_area = data.get('min_area', 1000)
        max_area = data.get('max_area', 'inf')
        threshold_val = data.get('threshold', 100)
        # 打印参数信息
        print(
            f"[裂缝分析] 参数 - filename: {filename}, min_area: {min_area}, max_area: {max_area}, threshold: {threshold_val}")
        # 检查文件名是否为空
        if not filename:
            print("[裂缝分析] 错误: 缺少文件名")
            return jsonify({'error': '缺少文件名参数'}), 400
        # 构建图像文件的路径
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # 读取图像
        print(f"[裂缝分析] 读取图像: {filepath}")
        image = cv2.imread(filepath)
        # 检查图像是否读取成功
        if image is None:
            print(f"[裂缝分析] 错误: 无法读取图像: {filepath}")
            return jsonify({'error': f'无法读取图像: {filepath}'}), 400
        # 打印图像的尺寸信息
        print(f"[裂缝分析] 图像尺寸: {image.shape}")
        # 参数类型转换与校验
        try:
            # 将最小面积和阈值转换为整数
            min_area = int(min_area)
            threshold_val = int(threshold_val)
            # 处理最大面积参数
            if max_area is None or (isinstance(max_area, str) and max_area.lower() in ['inf', 'infinity', '']):
                max_area = float('inf')
            else:
                max_area = int(max_area)
            # 确保最小面积不大于最大面积（除非最大面积是无穷大）
            if min_area > max_area and max_area != float('inf'):
                raise ValueError("最小面积不能大于最大面积")
        except ValueError as e:
            # 如果参数类型错误，打印错误信息并返回错误响应
            print(f"[裂缝分析] 参数类型错误: {e}")
            return jsonify({'error': f'参数错误: {str(e)}，请确保输入有效数字或inf'}), 400
        # 参数范围校验
        if min_area < 1:
            print("[裂缝分析] 错误: 最小面积必须≥1")
            return jsonify({'error': '最小面积必须≥1'}), 400
        if threshold_val < 0 or threshold_val > 255:
            print("[裂缝分析] 错误: 阈值必须在0-255之间")
            return jsonify({'error': '阈值必须在0-255之间'}), 400
        # 执行裂缝分析
        print("[裂缝分析] 开始执行裂缝分析...")
        result = process_crack(image, min_area, max_area, threshold_val)
        # 检查分析结果是否为空
        if result is None:
            print("[裂缝分析] 错误: 分析返回空结果")
            return jsonify({'error': '裂缝分析返回空结果，请检查图像质量或参数设置'}), 500
        # 生成结果图像
        print("[裂缝分析] 生成结果图像...")
        images = {
            'original': image_to_base64(image),
            'gray': image_to_base64(result.get('原图', image)),
            'binary': image_to_base64(result.get('二值图', image)),
            'result': image_to_base64(result.get('结果图', image))
        }
        # 生成直方图
        print("[裂缝分析] 生成直方图...")
        width_data = result.get('裂缝宽度列表', [])
        histogram = create_histogram(
            width_data,
            '裂缝宽度分布',
            '裂缝宽度(像素)',
            '数量'
        )
        # 将分析结果转换为可序列化格式
        print("[裂缝分析] 序列化结果数据...")
        serializable_result = convert_to_serializable(result)
        # 计算分析耗时
        elapsed_time = time.time() - start_time
        print(f"[裂缝分析] 分析完成，耗时: {elapsed_time:.2f}秒")
        print("=" * 50 + "\n")
        # 返回分析结果
        return jsonify({
            'success': True,
            'result': serializable_result.get('特征', {}),
            'images': images,
            'histogram': histogram
        })
    except Exception as e:
        # 如果出现未捕获的异常，打印详细异常信息并返回错误响应
        import traceback
        print(f"[裂缝分析] 未捕获异常: {e}")
        traceback.print_exc()
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

# 定义粒度分析路由，处理粒度分析请求
@app.route('/analyze/grains', methods=['POST'])
def analyze_grains_route():
    """处理粒度分析请求"""
    try:
        print("\n" + "=" * 50)
        print("[粒度分析] 接收到分析请求")
        # 获取请求数据
        data = request.get_json()
        # 提取请求数据中的文件名
        filename = data.get('filename')
        # 检查文件名是否为空
        if not filename:
            print("[粒度分析] 错误: 缺少文件名")
            return jsonify({'error': '缺少文件名参数'}), 400
        # 构建图像文件的路径
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # 读取图像
        print(f"[粒度分析] 读取图像: {filepath}")
        image = cv2.imread(filepath)
        # 检查图像是否读取成功
        if image is None:
            print(f"[粒度分析] 错误: 无法读取图像: {filepath}")
            return jsonify({'error': '无法读取图像'}), 400
        # 执行粒度分析
        print("[粒度分析] 开始执行粒度分析...")
        result, gray, binary, marked = analyze_grains(image)
        # 生成结果图像
        print("[粒度分析] 生成结果图像...")
        images = {
            'original': image_to_base64(image),
            'gray': image_to_base64(gray),
            'binary': image_to_base64(binary),
            'marked': image_to_base64(marked)
        }
        # 生成直方图
        print("[粒度分析] 生成直方图...")
        area_data = result.get('面积列表', [])
        histogram = create_histogram(
            area_data,
            '粒度分布',
            '粒度面积(像素²)',
            '数量'
        )
        print("[粒度分析] 分析完成")
        print("=" * 50 + "\n")
        # 返回分析结果
        return jsonify({
            'success': True,
            'result': result,
            'images': images,
            'histogram': histogram
        })
    except Exception as e:
        # 如果出现错误，打印错误信息并返回错误响应
        print(f"[粒度分析] 错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'粒度分析失败: {str(e)}'}), 500

# 定义孔洞分析路由，处理孔洞分析请求
@app.route('/analyze/holes', methods=['POST'])
def analyze_holes_route():
    """处理孔洞分析请求"""
    try:
        print("\n" + "=" * 50)
        print("[孔洞分析] 接收到分析请求")
        # 获取请求数据
        data = request.get_json()
        # 提取请求数据中的参数
        filename = data.get('filename')
        min_area = data.get('min_area', 1)
        max_area = data.get('max_area', 1000)
        threshold_val = data.get('threshold', 100)
        # 检查文件名是否为空
        if not filename:
            print("[孔洞分析] 错误: 缺少文件名")
            return jsonify({'error': '缺少文件名参数'}), 400
        # 构建图像文件的路径
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # 读取图像
        print(f"[孔洞分析] 读取图像: {filepath}")
        image = cv2.imread(filepath)
        # 检查图像是否读取成功
        if image is None:
            print(f"[孔洞分析] 错误: 无法读取图像: {filepath}")
            return jsonify({'error': '无法读取图像'}), 400
        # 执行孔洞分析
        print("[孔洞分析] 开始执行孔洞分析...")
        result, gray, binary, marked = process_stone_holes(image, min_area, max_area, threshold_val)
        # 生成结果图像
        print("[孔洞分析] 生成结果图像...")
        images = {
            'original': image_to_base64(image),
            'gray': image_to_base64(gray),
            'binary': image_to_base64(binary),
            'marked': image_to_base64(marked)
        }
        # 生成直方图
        print("[孔洞分析] 生成直方图...")
        area_data = result.get('面积列表', [])
        histogram = create_histogram(
            area_data,
            '孔洞面积分布',
            '孔洞面积(像素²)',
            '数量'
        )
        print("[孔洞分析] 分析完成")
        print("=" * 50 + "\n")
        # 返回分析结果
        return jsonify({
            'success': True,
            'result': result,
            'images': images,
            'histogram': histogram
        })
    except Exception as e:
        # 如果出现错误，打印错误信息并返回错误响应
        print(f"[孔洞分析] 错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'孔洞分析失败: {str(e)}'}), 500

# 主程序入口
if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("地质岩心图文分析系统启动中...")
    # 打印Python版本信息
    print(f"Python版本: {sys.version}")
    # 打印OpenCV版本信息
    print(f"OpenCV版本: {cv2.__version__}")
    # 打印NumPy版本信息
    print(f"NumPy版本: {np.__version__}")
    try:
        # 打印Flask版本信息
        print(f"Flask版本: {importlib.metadata.version('flask')}")
    except Exception:
        print("无法通过importlib获取Flask版本，使用旧方法")
        import flask
        print(f"Flask版本: {flask.__version__}")
    print("=" * 50 + "\n")
    # 启动Flask应用，开启调试模式，监听5000端口
    app.run(debug=True, port=5000)