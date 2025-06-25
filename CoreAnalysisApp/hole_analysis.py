# 导入必要的库
# cv2是OpenCV库，用于图像处理和计算机视觉任务
import cv2
# numpy是Python的一个科学计算库，用于处理数组和矩阵
import numpy as np

# 定义孔洞分析函数
# 该函数用于分析图像中的孔洞，输入参数包括图像、最小面积、最大面积和阈值
def process_stone_holes(image, min_area=1, max_area=1000, threshold_val=100):
    # 如果输入图像为空，返回错误信息和None值
    if image is None:
        return "错误：图像为空", None, None, None

    # 保持原始灰度转换
    # 灰度图只包含一个通道，便于后续处理
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 优化高斯模糊参数
    # 高斯模糊可以去除图像中的噪声
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 保持固定阈值但优化参数处理
    # 固定阈值将图像转换为二值图像
    _, thresh = cv2.threshold(blurred, threshold_val, 255, cv2.THRESH_BINARY_INV)

    # 优化形态学操作核形状
    # 开操作去除小噪声，闭操作填充小孔洞
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # 使用更高效的轮廓分析方法
    # 查找二值图像中的轮廓
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 预分配列表空间
    # 初始化孔洞计数
    hole_count = 0
    # 初始化总孔洞面积
    total_hole_area = 0
    # 复制原始图像用于绘制结果
    result_img = image.copy()
    # 初始化圆形度列表
    circularities = []
    # 初始化面积列表
    areas = []

    # 遍历每个轮廓
    for contour in contours:
        # 计算轮廓面积
        area = cv2.contourArea(contour)
        # 筛选面积在指定范围内的孔洞
        if min_area <= area <= max_area:
            # 孔洞计数加1
            hole_count += 1
            # 总孔洞面积增加
            total_hole_area += area
            # 计算轮廓周长
            perimeter = cv2.arcLength(contour, True)
            if perimeter > 0:
                # 计算圆形度
                circularity = (4 * np.pi * area) / (perimeter ** 2 + 1e-10)
                # 将圆形度添加到圆形度列表中
                circularities.append(circularity)
            # 优化绘制方法
            # 绘制绿色的轮廓线
            cv2.drawContours(result_img, [contour], -1, (0, 255, 0), 2)
            # 将面积添加到面积列表中
            areas.append(area)

    # 计算分析结果
    result = {
        "孔洞数量": hole_count,
        "总面积": total_hole_area,
        "平均面积": total_hole_area / hole_count if hole_count > 0 else 0,
        "平均圆形度": np.mean(circularities) if circularities else 0,
        "面积列表": areas
    }

    # 返回分析结果和中间图像
    return result, gray, thresh, result_img