from ultralytics import YOLO
import cv2

class YOLOEngine:
    def __init__(self, model_path="yolov8n.pt"):
        # 加载模型，首次运行会自动从 GitHub 下载权重文件
        self.model = YOLO(model_path, task='detect')

    def detect(self, img_cv2, conf=0.25):
        """执行推理，返回渲染后的图和标签列表"""
        # 如果是单通道灰度图，先转回三通道 BGR 才能喂给 YOLO
        if len(img_cv2.shape) == 2:
            img_input = cv2.cvtColor(img_cv2, cv2.COLOR_GRAY2BGR)
        else:
            img_input = img_cv2

        results = self.model.predict(img_input, conf=conf, verbose=False)
        
        # 获取渲染图（带有 Bounding Box 的彩色图）
        res_img = results[0].plot()
        
        # 提取画面中不重复的标签名
        labels = []
        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            labels.append(self.model.names[cls_id])
            
        return res_img, list(set(labels))