# 地质岩心图文分析系统使用说明书

## 一、系统简介

### 1.1 系统概述

地质岩石图文分析系统是一款专为地质研究设计的图像分析工具，可对岩石图像进行自动化处理与特征提取，支持孔洞分析、裂缝分析和粒度分析三大核心功能。系统提供 Web 版和桌面 GUI 版两种使用方式，具备图像上传、参数调节、结果可视化及数据导出等功能，帮助地质研究人员高效分析岩心结构特征。

### 1.2 系统功能

- **图像分析功能**：
  - 孔洞分析：检测岩心中的孔洞结构，计算数量、面积、圆形度等参数
  - 裂缝分析：识别裂缝特征，测量长度、宽度、方向等指标
  - 粒度分析：分析岩石颗粒分布，统计粒子数量与面积分布
- **可视化功能**：
  - 原始图像、灰度图、二值图、标记图多视图展示
  - 分析结果数据表格展示
  - 特征分布直方图生成
- **数据导出**：
  - 支持 JSON、CSV 格式分析数据导出
  - 可导出带标记的分析图像

## 二、系统安装

### 2.1 环境要求

- **硬件要求**：
  - 处理器：Intel Core i5 及以上
  - 内存：8GB 及以上
  - 存储空间：500MB 可用空间
- **软件要求**：
  - Python 3.8+
  - Web 版：支持 Chrome、Firefox、Edge 等现代浏览器
  - GUI 版：Windows 10/macOS 10.15+

### 2.2 安装步骤（Web 版）

**克隆项目代码**：

```bash
git clone https://github.com/your-repo/core-analysis-system.git
cd core-analysis-system
```

**创建虚拟环境**：

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

**安装依赖**：

```bash
pip install -r requirements.txt
```

**启动服务**：

```bash
python app.py
```

**访问系统**：
打开浏览器访问 `http://localhost:5000`

### 2.3 安装步骤（GUI 版）

**安装依赖**：

```bash
pip install -r requirements.txt
```

**运行程序**：

```bash
python gui_main.py
```

### 2.4 部署步骤（Web 版）

要在内网服务器上部署 Flask 应用，我们需要使用 Gunicorn 作为 WSGI 服务器，并配置 Nginx 作为反向代理服务器，以下是Ubuntu 环境下 Flask 应用部署指南：

#### 2.4.1 安装必要的依赖

首先更新系统并安装所需的软件包：

```bash
# 更新系统
sudo apt update
sudo apt upgrade -y

# 安装Nginx
sudo apt install nginx -y

# 安装Python和pip
sudo apt install python3 python3-pip python3-venv -y

# 安装虚拟环境
python3 -m venv venv
```

#### 2.4.2 配置 Gunicorn

在你的 Flask 项目目录中，我们需要配置 Gunicorn 来运行你的应用。假设你的 Flask 应用入口文件是`app.py`：

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装Gunicorn和项目依赖
pip install gunicorn

# 测试Gunicorn是否能正常运行你的应用
gunicorn -w 4 -b 127.0.0.1:8000 app:app 
# `-w 4`：使用 4 个工作进程;`-b 127.0.0.1:8000`：绑定到本地 8000 端口;`app:app`：假设你的 Flask 应用在`app.py`文件中，并且 Flask 实例名为`app`

```

如果你的应用入口文件或 Flask 实例名称不同，请相应调整。

#### 2.4.3 创建 Systemd 服务

为了确保 Gunicorn 在系统启动时自动运行，并在崩溃时自动重启，我们创建一个 systemd 服务：

```bash
# 创建服务文件
sudo nano /etc/systemd/system/rock.service
```

在打开的文件中添加以下内容：

```ini
[Unit]
Description=Gunicorn instance to serve rock application
After=network.target

[Service]
User=hupi
Group=www-data
WorkingDirectory=/home/hupi/rock
Environment="PATH=/home/hupi/rock/venv/bin"
ExecStart=/home/hupi/rock/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app

[Install]
WantedBy=multi-user.target
```

保存并退出文件，然后执行以下命令：

```bash
# 重新加载systemd管理器配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start rock

# 设置开机自启
sudo systemctl enable rock

# 检查服务状态
sudo systemctl status rock
```

#### 2.4.4 配置 Nginx 作为反向代理

接下来配置 Nginx 来代理请求到 Gunicorn：

```bash
# 创建Nginx配置文件
sudo nano /etc/nginx/sites-available/rock
```

在打开的文件中添加以下内容：

```nginx
server {
    listen 80;
    server_name 你的服务器IP地址;  # 使用你的服务器IP地址

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

确认内网 IP 可以通过执行 `ip a` 查看内网 IP：

```bash
ip a | grep inet | grep -v 127.0.0.1
```

保存并退出，然后执行：

```bash
# 创建符号链接启用配置
sudo ln -s /etc/nginx/sites-available/rock /etc/nginx/sites-enabled/

# 检查Nginx配置语法
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx

# 允许HTTP流量通过防火墙
sudo ufw allow 'Nginx HTTP'
```

#### 2.4.5 验证部署

现在你的 Flask 应用应该已经通过 Nginx 和 Gunicorn 部署好了。你可以通过以下方式验证：

```bash
# 检查服务状态
sudo systemctl status rock
sudo systemctl status nginx

# 查看Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# 查看Gunicorn日志
sudo journalctl -u rock.service -f
```

如果你在浏览器中访问服务器 IP 地址，应该能看到你的 Flask 应用运行起来了。

#### 2.4.6 部署后的管理

```bash
# 重启应用
sudo systemctl restart rock

# 查看应用日志
sudo journalctl -u rock.service

# 更新应用代码后重启
cd /home/hupi/rock
git pull  # 如果使用Git
sudo systemctl restart rock
```

以上步骤完成后，你的 Flask 应用就已经在内网服务器上成功部署了。





## 三、快速入门

### 3.1 Web 版操作流程

1. **上传图像**：
   - 点击左侧 "图像上传" 区域，选择 JPG/PNG/TIF 等格式的岩心图像
2. **设置分析参数**：
   - **孔洞分析**：设置最小面积、最大面积和阈值
   - **裂缝分析**：调整裂缝最小面积、阈值等参数
   - **粒度分析**：直接点击 "粒度分析" 按钮
3. **执行分析**：
   - 点击对应分析按钮（如 "孔洞分析"），系统自动处理图像
4. **查看结果**：
   - 右侧显示原始图像、二值图、标记图等
   - 下方展示分析数据表格和分布直方图
5. **导出数据**：
   - 点击 "导出 JSON 数据" 或 "导出 CSV 数据" 按钮

### 3.2 GUI 版操作流程

1. **打开图像**：
   - 点击菜单栏 "文件 - 打开图像"，选择岩心图像文件
2. **设置参数**：
   - 在左侧面板输入各分析模块的参数值
3. **运行分析**：
   - 点击菜单栏 "分析" 选择对应功能（孔洞 / 裂缝 / 粒度）
4. **结果可视化**：
   - 上方显示多视图图像
   - 下方展示分析图表和数据文本
5. **导出结果**：
   - 点击菜单栏 "导出 - 导出分析结果" 选择保存位置

## 四、详细功能说明

### 4.1 图像上传模块

- **支持格式**：JPG、PNG、BMP、TIF/TIFF

- **文件大小**：最大 16MB

- **上传方式**：
  - Web 版：拖放或点击上传区域
  - GUI 版：文件菜单或工具栏按钮

### 4.2 结果解读指南

- **孔洞分析结果**：
  - 孔洞数量：岩心中有效孔洞的总数
  - 平均圆形度：越接近 1 表示孔洞越圆
  - 面积分布：直方图展示孔洞大小分布
- **裂缝分析结果**：
  - 裂缝数量：检测到的裂缝条数
  - 最大裂缝长度：最长裂缝的像素长度
  - 宽度分布：裂缝宽度的统计分布
- **粒度分析结果**：
  - 粒子数量：岩石颗粒总数
  - 平均面积：颗粒的平均像素面积
  - 粒度分布：颗粒大小的频率分布

## 五、高级功能使用

### 5.1 图像交互操作

- **Web 版**：
  - 视图模式：勾选菜单栏 "视图模式" 后，可通过鼠标滚轮缩放图像，左键拖动移动
  - 画笔模式：启用后可在图像上绘制标记，支持颜色和粗细调整
- **GUI 版**：
  - 缩放功能：菜单栏 "视图 - 开启缩放"，鼠标滚轮控制缩放
  - 移动功能："视图 - 开启移动"，左键拖动图像
  - 画笔工具："画笔 - 开启画笔"，支持自定义颜色和大小

### 5.2 图表自定义

- **图表类型切换**：
  - Web 版：当前仅支持直方图
  - GUI 版：可切换柱状图、折线图、饼图
  - 操作：GUI 版菜单栏 "图表类型" 选择对应选项
- **参数调整**：
  - 可通过修改分析参数重新生成图表
  - GUI 版支持实时更新图表

### 5.3 数据导出选项

- **JSON 格式**：
  - 包含完整分析数据结构
  - 适用于后续编程处理
- **CSV 格式**：
  - 表格化数据，可直接导入 Excel
  - 包含统计数据和详细列表
- **图像导出**：
  - 右键点击分析图像可保存为 PNG 格式

## 六、常见问题与解决方案

### 6.1 图像上传问题

- **问题**：文件上传失败
  - 解决方案：
    - 检查文件格式是否支持
    - 确认文件大小不超过 16MB
    - 尝试重新上传或更换浏览器
- **问题**：图像显示异常
  - 解决方案：
    - 确保图像为标准 RGB 格式
    - 尝试转换图像格式后重新上传

### 6.2 分析结果异常

- **问题**：分析结果为空
  - 解决方案：
    - 检查参数设置是否合理
    - 确认图像中存在可识别的特征
    - 调整阈值或面积范围
- **问题**：结果不准确
  - 解决方案：
    - 优化图像质量（亮度、对比度）
    - 微调分析参数（如阈值、面积范围）
    - 尝试不同分析模块对比结果

### 6.3 系统运行问题

- **问题**：Web 服务启动失败
  - 解决方案：
    - 检查 Python 环境是否正确配置
    - 确认端口 5000 未被占用
    - 重新安装依赖包
- **问题**：GUI 界面卡顿
  - 解决方案：
    - 关闭其他占用内存的程序
    - 缩小图像尺寸后再分析
    - 升级硬件配置

## 七、技术支持与反馈

### 7.1 联系方式

- **技术支持邮箱**：1472978449@qq.com

### 7.2 版本更新

- 该版本为初始版本 V1.0.0

### 7.3 安全提示

- 请勿上传包含敏感信息的图像
- 定期备份分析数据
- 保持软件更新以获取安全补丁

## 八、附录：技术规格

### 8.1 系统架构

- **Web 版**：
  - 前端：HTML5/CSS3/JavaScript
  - 后端：Flask Python 框架
  - 图像处理：OpenCV/numpy
- **GUI 版**：
  - 界面：Tkinter
  - 绘图：Matplotlib
  - 核心算法：Python 科学计算库

### 8.2 性能指标

- **处理速度**：
  - 单张图像分析：500ms-2s（取决于图像复杂度）
  - 大数据集处理：支持批量处理
- **资源占用**：
  - 内存：50-200MB（单实例）
  - CPU：单核利用率 20-50%

### 8.3 兼容列表

- **操作系统**：
  - Windows 10/11
  - Linux (Ubuntu 20.04+)
- **浏览器支持**：
  - Google Chrome 80+
  - Microsoft Edge 80+







