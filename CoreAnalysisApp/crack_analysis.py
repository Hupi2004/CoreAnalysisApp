# 导入必要的库
# cv2是OpenCV库，用于图像处理和计算机视觉任务
import cv2
# numpy是Python的一个科学计算库，用于处理数组和矩阵
import numpy as np
# ndimage是scipy库中的一个模块，用于图像处理
from scipy import ndimage
# measure是skimage库中的一个模块，用于图像特征测量
from skimage import measure

# 定义裂缝处理函数
# 该函数用于处理图像中的裂缝，输入参数包括图像、最小面积、最大面积和阈值
def process_crack(image, min_area=1000, max_area=np.inf, threshold_val=100):
    # 如果输入图像为空，返回空字典
    if image is None:
        return {}

    # 使用更高效的灰度转换方法
    # 灰度图只包含一个通道，便于后续处理
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 自适应直方图均衡化增强对比度
    # 可以使图像的亮度分布更均匀
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced_gray = clahe.apply(gray)

    # 优化高斯模糊参数，使用双边滤波保留边缘
    # 双边滤波可以在去除噪声的同时保留图像的边缘信息
    blurred = cv2.bilateralFilter(enhanced_gray, 9, 75, 75)

    # 自适应阈值处理
    # 根据图像的局部特征进行阈值处理
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)

    # 结合全局阈值作为备用方案
    # 确保在自适应阈值处理效果不好时也能得到较好的结果
    _, global_thresh = cv2.threshold(blurred, threshold_val, 255, cv2.THRESH_BINARY_INV)
    thresh = cv2.bitwise_or(thresh, global_thresh)

    # 优化形态学操作
    # 开操作去除小噪声，闭操作填充小孔洞
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

    # 使用区域生长法去除小噪声
    # 标记连通区域，并计算每个区域的大小
    labeled, num_features = ndimage.label(thresh)
    sizes = ndimage.sum(thresh, labeled, range(num_features + 1))
    # 筛选出面积大于最小面积/10的区域
    mask = sizes > min_area / 10
    thresh = mask[labeled]

    # 使用更精确的轮廓分析方法
    # 查找二值图像中的轮廓
    contours, _ = cv2.findContours(thresh.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 初始化裂缝计数
    crack_count = 0
    # 初始化总裂缝面积
    total_crack_area = 0
    # 复制原始图像用于绘制结果
    result_img = image.copy()
    # 初始化裂缝轮廓列表
    crack_contours = []
    # 初始化裂缝宽度列表
    crack_widths = []
    # 初始化裂缝长度列表
    crack_lengths = []
    # 初始化裂缝宽度分布列表
    crack_width_distributions = []

    # 遍历每个轮廓
    for contour in contours:
        # 计算轮廓面积
        area = cv2.contourArea(contour)
        # 筛选面积在指定范围内的裂缝
        if min_area <= area <= max_area:
            # 更精确的面积计算，考虑孔洞
            # 计算凸包面积
            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)
            # 计算实体度
            solidity = float(area) / hull_area if hull_area > 0 else 0

            # 过滤非裂缝形状
            # 裂缝通常实体度较低
            if solidity < 0.7:
                # 裂缝计数加1
                crack_count += 1
                # 总裂缝面积增加
                total_crack_area += area
                # 将裂缝轮廓添加到列表中
                crack_contours.append(contour)

                # 绘制轮廓
                # 绘制绿色的轮廓线
                cv2.drawContours(result_img, [contour], -1, (0, 255, 0), 2)

                # 创建仅包含当前裂缝的二值图像
                crack_mask = np.zeros_like(thresh, dtype=np.uint8)
                cv2.drawContours(crack_mask, [contour], -1, 1, -1)

                # 对单个裂缝进行距离变换
                # 计算每个像素到裂缝边界的距离
                dist_transform = cv2.distanceTransform(crack_mask, cv2.DIST_L2, 5)

                # 获取宽度分布
                # 距离变换返回的是半径，乘以2得到宽度
                width_values = dist_transform[crack_mask > 0] * 2

                if len(width_values) > 0:
                    # 计算当前裂缝的宽度统计信息
                    min_width = np.min(width_values)
                    max_width = np.max(width_values)
                    mean_width = np.mean(width_values)

                    # 将宽度统计信息添加到宽度分布列表中
                    crack_width_distributions.append({
                        'min': min_width,
                        'max': max_width,
                        'mean': mean_width,
                        'distribution': width_values
                    })

                    # 使用最大宽度作为该裂缝的代表宽度
                    crack_widths.append(max_width)
                else:
                    # 如果没有宽度值，将宽度设为0
                    crack_widths.append(0)

                # 计算裂缝长度，使用轮廓的弧长
                length = cv2.arcLength(contour, True)
                # 将裂缝长度添加到长度列表中
                crack_lengths.append(length)

                # 优化多边形近似绘制
                # 简化轮廓，减少绘制的点数
                epsilon = 0.005 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                # 绘制红色的近似多边形
                cv2.polylines(result_img, [approx], True, (0, 0, 255), 2)

    # 初始化裂缝特征字典
    crack_features = {}
    if crack_count > 0:
        # 使用区域属性分析最大裂缝
        props = measure.regionprops(labeled.astype(int))
        # 找到面积最大的区域
        largest_prop = max(props, key=lambda x: x.area) if props else None

        if largest_prop and crack_width_distributions:
            # 找到面积最大的裂缝对应的索引
            largest_area = largest_prop.area
            largest_crack_idx = np.argmax([cv2.contourArea(c) for c in crack_contours])

            # 获取最大裂缝的宽度分布
            largest_crack_widths = crack_width_distributions[largest_crack_idx]

            # 计算裂缝方向
            orientation = largest_prop.orientation
            crack_direction = "横向裂缝" if abs(orientation) < np.pi / 4 else "纵向裂缝"

            # 更精确的特征计算
            crack_features = {
                '数量': crack_count,
                '总面积': total_crack_area,
                '平均面积': total_crack_area / crack_count,
                '最大裂缝方向': crack_direction,
                '最大裂缝长度': max(crack_lengths) if crack_lengths else 0,
                '最大裂缝最大宽度': largest_crack_widths['max'],
                '最大裂缝最小宽度': largest_crack_widths['min'],
                '最大裂缝平均宽度': largest_crack_widths['mean'],
                '平均宽度': np.mean(crack_widths) if crack_widths else 0,
                '长度宽度比': max(crack_lengths) / largest_crack_widths['max']
                if largest_crack_widths['max'] > 0 else 0
            }

    return {
        '原图': gray,
        '二值图': thresh.astype(np.uint8) * 255,
        '结果图': result_img,
        '裂缝轮廓': crack_contours,
        '特征': crack_features,
        '裂缝宽度列表': crack_widths,
        '裂缝宽度分布': crack_width_distributions
    }