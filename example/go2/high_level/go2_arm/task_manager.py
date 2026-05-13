# -*- coding: utf-8 -*-
"""
任务管理器：实现双栈任务调度
"""
from enum import Enum
from typing import List, Dict, Optional
import threading

class TaskType(Enum):
    """任务类型"""
    NAVIGATE = "navigate"  # 导航到指定位置
    GRASP = "grasp"        # 抓取物品（蹲下+通信+站起）

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class SubTask:
    """子任务"""
    def __init__(self, task_type: TaskType, data: Dict):
        self.task_type = task_type
        self.data = data
        self.status = TaskStatus.PENDING
        
    def __repr__(self):
        return f"SubTask({self.task_type.value}, {self.data}, {self.status.value})"

class MainTask:
    """主任务"""
    def __init__(self, item: str, locations: List[str], task_id: int, delivery_location: str = None):
        self.task_id = task_id
        self.item = item
        self.locations = locations
        self.delivery_location = delivery_location  # 👈 新增：送达地点
        self.sub_tasks: List[SubTask] = []
        self.status = TaskStatus.PENDING
        
        # 构建子任务
        self._build_sub_tasks()
    
    # def _build_sub_tasks(self):
    #     """将主任务拆分为子任务"""
    #     if len(self.locations) < 1:
    #         print(f"⚠️ 警告: 任务 #{self.task_id} 没有地点，添加默认起始位置")
    #         self.locations = ["初始位置"]
        
    #     # 1. 导航到第一个位置（取物品的地方）
    #     self.sub_tasks.append(SubTask(
    #         TaskType.NAVIGATE,
    #         {
    #             "location": self.locations[0], 
    #             "purpose": "取物品",
    #             "item": self.item,
    #             "obj_name": self._get_obj_name(self.item)
    #         }
    #     ))
        
    #     # 2. 导航到后续位置
    #     for i in range(1, len(self.locations)):
    #         location = self.locations[i]
            
    #         # 👇 判断是否为送达地点
    #         if self.delivery_location and location == self.delivery_location:
    #             purpose = "送物品"
    #         else:
    #             purpose = "中转"
            
    #         self.sub_tasks.append(SubTask(
    #             TaskType.NAVIGATE,
    #             {
    #                 "location": location, 
    #                 "purpose": purpose
    #             }
    #         ))
        
    #     # 3. 如果没有送达地点，最后一个位置默认为送达
    #     if self.delivery_location is None and len(self.locations) > 1:
    #         # 修改最后一个子任务的 purpose
    #         self.sub_tasks[-1].data["purpose"] = "送物品"
        
    #     # 4. 如果只有一个地点（只有取物品的地方），自动添加返回
    #     if len(self.locations) == 1:
    #         print(f"   自动添加返回 '初始位置' 任务")
    #         self.sub_tasks.append(SubTask(
    #             TaskType.NAVIGATE,
    #             {"location": "初始位置", "purpose": "返回"}
    #         ))
    
    def _build_sub_tasks(self):
        """将主任务拆分为子任务"""
        if len(self.locations) < 1:
            print(f"⚠️ 警告: 任务 #{self.task_id} 没有地点，添加默认起始位置")
            self.locations = ["初始位置"]
        
        # 1. 导航到第一个位置（取物品的地方）
        self.sub_tasks.append(SubTask(
            TaskType.NAVIGATE,
            {
                "location": self.locations[0], 
                "purpose": "取物品",
                "item": self.item,  # 👈 存储物品名称
                "obj_name": self._get_obj_name(self.item)
            }
        ))
        
        # 2. 导航到后续位置
        for i in range(1, len(self.locations)):
            location = self.locations[i]
            
            # 判断是否为送达地点
            if self.delivery_location and location == self.delivery_location:
                purpose = "送物品"
            else:
                purpose = "中转"
            
            self.sub_tasks.append(SubTask(
                TaskType.NAVIGATE,
                {
                    "location": location, 
                    "purpose": purpose,
                    "item": self.item  # 👈 每个子任务都存储物品名称
                }
            ))
        
        # 3. 如果没有送达地点，最后一个位置默认为送达
        if self.delivery_location is None and len(self.locations) > 1:
            self.sub_tasks[-1].data["purpose"] = "送物品"
        
        # 4. 如果只有一个地点，自动添加返回
        if len(self.locations) == 1:
            print(f"   自动添加返回 '初始位置' 任务")
            self.sub_tasks.append(SubTask(
                TaskType.NAVIGATE,
                {
                    "location": "初始位置", 
                    "purpose": "返回",
                    "item": self.item  # 👈 返回任务也存储物品名称
                }
            ))
        
    def _get_obj_name(self, item: str) -> str:
        """获取物品对应的对象名称"""
        mapping = {"水": "bottle", "纸": "tissue", "糖": "cup", "雨伞": "red umbrella", "咖啡": "bottle","外卖":"brown bag","饮料":"bottle"}
        return mapping.get(item, "unknown")
    
    def __repr__(self):
        return f"MainTask(#{self.task_id}, {self.item}, {self.locations}, {self.status.value})"

class TaskManager:
    """任务管理器：双栈调度"""
    
    def __init__(self):
        self.preparation_stack: List[MainTask] = []  # 预备栈
        self.execution_stack: List[SubTask] = []     # 执行栈
        self.current_task: Optional[MainTask] = None  # 当前执行的主任务
        self.paused_tasks: List[MainTask] = []       # 暂停的任务列表
        self.task_counter = 0
        self.lock = threading.RLock()
    
    def add_task(self, item: str, locations: List[str], delivery_location: str = None) -> int:
        """
        添加新任务到预备栈
        
        Args:
            item: 物品名称
            locations: 地点列表
            delivery_location: 送达地点（"送到"后的第一个地点）
            
        Returns:
            task_id: 任务ID
        """
        with self.lock:
            self.task_counter += 1
            task = MainTask(item, locations, self.task_counter, delivery_location)
            self.preparation_stack.append(task)
            
            print(f"\n📋 新任务已添加到预备栈:")
            print(f"   任务ID: #{task.task_id}")
            print(f"   物品: {item}")
            print(f"   地点: {' -> '.join(locations)}")
            if delivery_location:
                print(f"   送达地点: {delivery_location} ⭐")
            print(f"   子任务数: {len(task.sub_tasks)}")
            
            return task.task_id

    def interrupt_and_execute(self, item: str, locations: List[str], delivery_location: str = None) -> int:
        """
        中断当前任务，执行紧急任务
        
        Args:
            item: 物品名称
            locations: 地点列表
            delivery_location: 送达地点
            
        Returns:
            task_id: 新任务ID
        """
        with self.lock:
            # 1. 如果有正在执行的任务，暂停它
            if self.current_task and self.current_task.status == TaskStatus.RUNNING:
                print(f"\n⏸️  暂停当前任务 #{self.current_task.task_id}")
                self.current_task.status = TaskStatus.PAUSED
                self.paused_tasks.append(self.current_task)
                
                # 保存当前执行栈的剩余任务到暂停任务中
                self.current_task.remaining_sub_tasks = self.execution_stack.copy()
                self.execution_stack.clear()
            
            # 2. 添加紧急任务并立即加载到执行栈
            task_id = self.add_task(item, locations, delivery_location)
            self._load_next_task()
            
            print(f"🚨 紧急任务 #{task_id} 已加载到执行栈")
            return task_id
    
    def _load_next_task(self):
        """从预备栈加载下一个任务到执行栈"""
        if not self.preparation_stack:
            print("⚠️ 预备栈为空，没有任务可加载")
            return False
        
        # 从预备栈顶部取出任务
        task = self.preparation_stack.pop()
        self.current_task = task
        task.status = TaskStatus.RUNNING
        
        # 将子任务逆序压入执行栈（这样栈顶就是第一个要执行的任务）
        for sub_task in reversed(task.sub_tasks):
            self.execution_stack.append(sub_task)
        
        print(f"\n✅ 任务 #{task.task_id} 已加载到执行栈")
        print(f"   执行栈大小: {len(self.execution_stack)}")
        self._print_execution_stack()
        
        return True
    
    def get_next_sub_task(self) -> Optional[SubTask]:
        """
        获取下一个要执行的子任务（执行栈栈顶）
        
        Returns:
            SubTask 或 None
        """
        with self.lock:
            if not self.execution_stack:
                # 执行栈为空，尝试加载下一个主任务
                if self.preparation_stack:
                    self._load_next_task()
                elif self.paused_tasks:
                    # 恢复暂停的任务
                    self._resume_paused_task()
                else:
                    print("\n✅ 所有任务已完成")
                    return None
            
            if self.execution_stack:
                sub_task = self.execution_stack[-1]  # 获取栈顶（但不出栈）
                return sub_task
            
            return None
    
    def complete_current_sub_task(self):
        """标记当前子任务为已完成，并出栈"""
        with self.lock:
            if self.execution_stack:
                completed = self.execution_stack.pop()
                completed.status = TaskStatus.COMPLETED
                
                print(f"\n✓ 子任务已完成: {completed}")
                print(f"   剩余子任务: {len(self.execution_stack)}")
                
                # 检查主任务是否完成
                if not self.execution_stack and self.current_task:
                    self.current_task.status = TaskStatus.COMPLETED
                    print(f"\n🎉 主任务 #{self.current_task.task_id} 已完成")
                    self.current_task = None
    
    def _resume_paused_task(self):
        """恢复暂停的任务"""
        if not self.paused_tasks:
            return
        
        task = self.paused_tasks.pop(0)  # FIFO恢复
        self.current_task = task
        task.status = TaskStatus.RUNNING
        
        # 恢复执行栈
        if hasattr(task, 'remaining_sub_tasks'):
            self.execution_stack = task.remaining_sub_tasks.copy()
            delattr(task, 'remaining_sub_tasks')
        
        print(f"\n▶️  恢复暂停的任务 #{task.task_id}")
        print(f"   剩余子任务: {len(self.execution_stack)}")
        self._print_execution_stack()
    
    def _print_execution_stack(self):
        """打印执行栈状态（调试用）"""
        print(f"\n📚 执行栈 (栈顶->栈底):")
        for i, sub_task in enumerate(reversed(self.execution_stack)):
            prefix = "  👉 " if i == 0 else "     "
            print(f"{prefix}{sub_task}")
        print()
    
    def get_status(self) -> Dict:
        """获取任务管理器状态"""
        with self.lock:
            return {
                "current_task": self.current_task.task_id if self.current_task else None,
                "execution_stack_size": len(self.execution_stack),
                "preparation_stack_size": len(self.preparation_stack),
                "paused_tasks_count": len(self.paused_tasks)
            }