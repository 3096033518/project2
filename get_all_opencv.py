import cv2
import inspect

# 1. 提取 cv2 模块下所有的属性和方法名
all_attributes = dir(cv2)

print(f"🔄 正在疯狂挖掘 OpenCV 底层 API，共发现 {len(all_attributes)} 个可用接口...")

# 2. 创建一个巨大的本地字典文件
with open("OpenCV_Ultimate_Dictionary.txt", "w", encoding="utf-8") as f:
    valid_count = 0
    for name in all_attributes:
        # 3. 过滤掉双下划线开头的系统私有垃圾，只保留咱们能调用的实战 API！
        if not name.startswith('__'):
            try:
                func = getattr(cv2, name)
                # 4. 强行扒出底层 C++ 源码里自带的官方参数说明！
                doc = inspect.getdoc(func) 
                
                f.write(f"【核心算子】: cv2.{name}\n")
                if doc:
                    f.write(f"【参数与作用】:\n{doc}\n")
                else:
                    f.write("【参数与作用】: 常量或无官方文档释义\n")
                f.write("=" * 60 + "\n")
                valid_count += 1
            except Exception:
                pass

print(f"✅ 报告老板！挖掘完毕！成功提取 {valid_count} 个未淘汰的实战 API！")
print("👉 请在左侧文件夹查看 OpenCV_Ultimate_Dictionary.txt！")