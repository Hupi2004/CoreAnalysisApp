# setup.py 文件用于定义项目的元数据和依赖关系，便于项目打包和分发
from setuptools import setup, find_packages


# 读取项目的长描述，通常从README.md文件获取
def readme():
    with open('README.md', encoding='utf-8') as f:
        return f.read()


# 项目的主要配置信息
setup(
    # 项目名称，应具有唯一性
    name='geological-core-analysis-system',
    # 项目版本号，遵循语义化版本规范
    version='1.0.0',
    # 项目作者信息
    author='hupi',
    author_email='qiafan2004@163.com',
    # 项目简短描述
    description='地质岩心图文分析系统 - 用于岩心图像的裂缝、孔洞和粒度分析',
    # 项目长描述，通常使用README.md的内容
    long_description=readme(),
    long_description_content_type='text/markdown',
    # 项目主页URL
    # url='https://github.com/yourusername/geological-core-analysis',
    # 自动发现项目中的所有包
    packages=find_packages(),
    # 项目分类标签，帮助用户在PyPI等平台找到项目
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Image Processing',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    # 项目的依赖列表，从requirements.txt中提取并整理
    install_requires=[
        # 核心Web框架
        'Flask==3.1.1',
        'Werkzeug==3.1.3',
        'itsdangerous==2.2.0',
        'Jinja2==3.1.6',
        'MarkupSafe==3.0.2',

        # 图像处理与科学计算库
        'opencv-python==4.11.0.86',
        'numpy==2.2.6',
        'scikit-image==0.25.2',
        'scipy==1.15.3',
        'matplotlib==3.10.3',

        # 网络与HTTP库
        'requests==2.32.4',
        'urllib3==2.5.0',
        'charset-normalizer==3.4.2',
        'idna==3.10',

        # 工具库
        'certifi==2025.6.15',  # SSL证书验证
        'gunicorn==23.0.0',  # 生产环境Web服务器
        'typing_extensions==4.14.0',  # 类型提示增强

        # 可选的开发工具（生产环境可移除）
        # 'pipreqs==0.5.0',     # 依赖生成工具
        # 'ipython==8.12.3',    # 交互式调试工具
    ],
    # 定义命令行入口点，方便通过命令行启动应用
    entry_points={
        'console_scripts': [
            'core-analysis=app:main',  # 假设app.py中有main函数作为入口
        ],
    },
    # 项目支持的Python版本
    python_requires='>=3.8',
    # 项目是否包含非Python文件（如模板、静态文件等）
    include_package_data=True,
    # 项目的额外要求，可用于分组管理依赖
    extras_require={
        'dev': [
            'pipreqs==0.5.0',
            'ipython==8.12.3',
            'pytest==7.4.3',  # 测试框架
            'coverage==7.3.2',  # 测试覆盖率
        ],
        'docs': [
            'sphinx==7.2.5',  # 文档生成工具
            'sphinx-rtd-theme==1.6.0',  # 文档主题
        ],
    }
)