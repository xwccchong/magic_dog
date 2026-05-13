import json
import numpy as np
from scipy.spatial.transform import Rotation as R

def quat_pos_to_matrix(pos, quat):
    """
    将 Position (x, y, z) 和 Quaternion (qx, qy, qz, qw) 转换为 4x4 齐次变换矩阵
    """
    # 1. 提取平移向量
    t = np.array(pos)
    
    # 2. 提取四元数并转为旋转矩阵 (scipy 默认四元数顺序为 [x, y, z, w])
    rot = R.from_quat(quat)
    rot_matrix = rot.as_matrix()
    
    # 3. 构建 4x4 齐次变换矩阵
    T = np.eye(4)
    T[:3, :3] = rot_matrix
    T[:3, 3] = t
    
    return T

# 指定你的文件路径
file_path = "/home/unitree/unitree_sdk2_python/agent/utils/poses.json"

def main():
    try:
        # 1. 读取原始 JSON 数据
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print("成功读取数据，开始转换...")

        # 2. 遍历每个位姿，计算 4x4 矩阵并追加
        for pose_name, pose_data in data.get("poses", {}).items():
            pos = pose_data["position"]
            quat = pose_data["quaternion"]
            
            # 计算 4x4 矩阵
            matrix_4x4 = quat_pos_to_matrix(pos, quat)
            
            # NumPy 数组无法直接序列化为 JSON，需要调用 .tolist() 转换为标准列表
            pose_data["matrix"] = matrix_4x4.tolist()
            
        # 3. 将包含 matrix 的新数据写回原 JSON 文件
        with open(file_path, 'w', encoding='utf-8') as f:
            # indent=4 让输出的 JSON 文件具有良好的缩进和可读性
            json.dump(data, f, indent=4)
            
        print(f"转换完成！已将 4x4 矩阵追加到每个位姿中，并更新保存至: {file_path}")

    except FileNotFoundError:
        print(f"错误: 找不到文件 {file_path}。请确认文件路径是否正确以及文件是否存在。")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()