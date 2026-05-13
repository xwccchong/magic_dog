import json

# 配置数据
pos = [3.50625, -2.89206, -0.0104287]
quat = [0.00827102, 0.0593758, -0.112281, 0.991866]
total_frames = 245

# 生成字典数据
data = {
    "poses": {f"p{i}": {"position": pos, "quaternion": quat} for i in range(total_frames)}
}

# 写入文件
with open('poses.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("生成成功！已保存为 poses.json")