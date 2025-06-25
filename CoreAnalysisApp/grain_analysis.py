# 导入必要的库
# cv2是OpenCV库，用于图像处理和计算机视觉任务
import cv2
# numpy是Python的一个科学计算库，用于处理数组和矩阵
import numpy as np

# 定义粒度分析函数
# 该函数用于分析图像中的颗粒，输入参数包括图像、阈值、最小面积和最大面积
def analyze_grains(image, threshold_val=120, min_area=5, max_area=5000):
    # 如果输入图像为空，返回空字典和None值
    if image is None:
        return {}, None, None, None

    # 将图像转换为灰度图
    # 灰度图只包含一个通道，便于后续处理
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 使用中值滤波去除噪声
    # 中值滤波可以有效地去除椒盐噪声
    blurred = cv2.medianBlur(gray, 5)
    # 使用固定阈值进行二值化
    # 二值化将图像转换为只有0和255两种像素值的图像
    _, binary = cv2.threshold(blurred, threshold_val, 255, cv2.THRESH_BINARY_INV)

    # 使用开操作去除小颗粒
    # 开操作先腐蚀后膨胀，可以去除小的噪声点
    kernel = np.ones((3, 3), np.uint8)
    opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)

    # 查找轮廓
    # 轮廓是图像中连续的点集，代表物体的边界
    contours, _ = cv2.findContours(opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # 复制原始图像用于绘制结果
    result_img = image.copy()
    # 初始化面积列表
    areas = []

    # 遍历每个轮廓
    for cnt in contours:
        # 计算轮廓面积
        area = cv2.contourArea(cnt)
        # 筛选面积在指定范围内的颗粒
        if min_area <= area <= max_area:
            # 将符合条件的面积添加到面积列表中
            areas.append(area)
            # 在结果图中标记颗粒
            # 绘制蓝色的轮廓线
            cv2.drawContours(result_img, [cnt], -1, (255, 0, 0), 1)

    # 计算分析结果
    result = {
        # 颗粒数量
        "粒子数量": len(areas),
        # 平均面积，如果面积列表为空则为0
        "平均面积": np.mean(areas) if areas else 0,
        # 面积列表
        "面积列表": areas
    }

    # 返回分析结果和中间图像
    return result, gray, opened, result_img