import cv2
import numpy as np

class CVToolbox:
    @staticmethod
    def process(img, method, p1=None, p2=None):
        """核心处理矩阵：根据 UI 指令执行对应的 OpenCV 算子"""
        if method == "原图" or img is None: return img
        
        # 确保图片格式正确
        work_img = img.copy()

        try:
            # --- 1. 基础变换 ---
            if method == "灰度化": 
                return cv2.cvtColor(work_img, cv2.COLOR_BGR2GRAY)
            elif method == "反色": 
                return cv2.bitwise_not(work_img)
            elif method == "怀旧风":
                kernel = np.array([[0.272, 0.534, 0.131], [0.349, 0.686, 0.168], [0.393, 0.769, 0.189]])
                return cv2.transform(work_img, kernel)

            # --- 2. 滤波降噪 (p1 为核大小) ---
            elif method == "高斯模糊": 
                k = p1 if p1 % 2 != 0 else p1 + 1
                return cv2.GaussianBlur(work_img, (k, k), 0)
            elif method == "中值滤波": 
                k = p1 if p1 % 2 != 0 else p1 + 1
                return cv2.medianBlur(work_img, k)
            elif method == "双边滤波": 
                return cv2.bilateralFilter(work_img, 9, p1, 75)

            # --- 3. 边缘与特征提取 (p1, p2 为阈值) ---
            elif method == "Canny边缘": 
                return cv2.Canny(work_img, p1, p2)
            elif method == "Sobel算子": 
                gray = cv2.cvtColor(work_img, cv2.COLOR_BGR2GRAY)
                # 💥 军师防弹补丁：强制转绝对值并限制在 uint8，防止 YOLO 报错
                return cv2.convertScaleAbs(cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5))
            elif method == "Laplacian算子": 
                gray = cv2.cvtColor(work_img, cv2.COLOR_BGR2GRAY)
                # 💥 军师防弹补丁：强制转绝对值
                return cv2.convertScaleAbs(cv2.Laplacian(gray, cv2.CV_64F))

            # --- 4. 增强与二值化 (p1 为阈值) ---
            elif method == "直方图均衡":
                gray = cv2.cvtColor(work_img, cv2.COLOR_BGR2GRAY)
                return cv2.equalizeHist(gray)
            elif method == "CLAHE增强":
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                return clahe.apply(cv2.cvtColor(work_img, cv2.COLOR_BGR2GRAY))
            elif method == "二值化": 
                gray = cv2.cvtColor(work_img, cv2.COLOR_BGR2GRAY)
                _, res = cv2.threshold(gray, p1, 255, cv2.THRESH_BINARY)
                return res
            elif method == "OTSU阈值":
                gray = cv2.cvtColor(work_img, cv2.COLOR_BGR2GRAY)
                _, res = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                return res

            # --- 5. 形态学操作 (p1 为迭代次数) ---
            elif method == "膨胀": 
                return cv2.dilate(work_img, np.ones((5,5), np.uint8), iterations=p1)
            elif method == "腐蚀": 
                return cv2.erode(work_img, np.ones((5,5), np.uint8), iterations=p1)
            
            # --- 6. 几何变换 ---
            elif method == "水平翻转": return cv2.flip(work_img, 1)
            elif method == "垂直翻转": return cv2.flip(work_img, 0)

        except Exception as e:
            print(f"CV Error: {e}")
            return work_img
        
        return work_img