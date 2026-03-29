import os
from ultralytics import YOLO

# 1. 站上巨人的肩膀 (使用 Nano 版本保证 M1 速度)
model = YOLO('yolov8n.pt') 

print("🚀 [VLA炼丹炉] 正在载入工业安防数据集...")
print("💥 [M1 Pro 引擎] 正在启动 MPS 硬件级加速...")

# 2. 核心训练指令
results = model.train(
    # 🔴 确认这一行路径和你 data.yaml 的真实位置对得上！
    data='/Users/mac/Downloads/hardhat_data/data.yaml', 
    epochs=50,
    imgsz=640,
    batch=16,
    device='mps',    # 显卡核心点火！
    workers=8,
    cache=True,      # 数据预处理缓存，提升训练效率
    amp=True,        # 混合精度训练，进一步加速
    project='vla_hardhat',
    name='version_fast'
)

print("\n🎉 [报告老板] 炼丹圆满结束！快去 runs 文件夹找 best.pt！")