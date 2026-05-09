from ultralytics import YOLO
model = YOLO('runs/detect/vla_hardhat/version_fast/weights/last.pt')
results = model.train(resume=True)