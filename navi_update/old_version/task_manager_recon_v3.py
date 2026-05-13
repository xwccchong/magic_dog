# -*- coding: utf-8 -*-
from enum import Enum
from typing import List, Dict, Optional
import threading

class TaskType(Enum):
    """原子操作任务类型定义"""
    NAVIGATE = "navigate"              # 导航
    SQUAT = "squat"                    # 蹲下
    SEND_GRASP_MSG = "send_grasp_msg"  # 给机械臂发抓取目标
    WAIT_FOR_BACK = "wait_for_back"    # 等待机械臂 back 信号
    STAND_UP = "stand_up"              # 站起
    RELEASE_ITEM = "release_item"      # 👇 新增：放下物品
    WAIT_FOR_PLAY = "wait_for_play"    # 👇 新增：等待机械臂 play 信号
    PLAY_AUDIO = "play_audio"          # 播放音效
    
    HELLO = "hello"                    # 打招呼
    ROTATE = "rotate"                  # 旋转
    LIE_DOWN = "lie_down"              # 趴下
    STRETCH = "stretch"                # 伸懒腰
    WALK_FORWARD = "walk_forward"      # 向前走
    WALK_BACKWARD = "walk_backward"    # 向后走
    WALK_LEFT = "walk_left"            # 向左移动
    WALK_RIGHT = "walk_right"          # 向右移动

    CAPTURE_PHOTO = "capture_photo"    # 拍照

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class SubTask:
    def __init__(self, task_type: TaskType, data: Dict):
        self.task_type = task_type
        self.data = data
        self.status = TaskStatus.PENDING
        
    def __repr__(self):
        return f"SubTask({self.task_type.value}, {self.data}, {self.status.value})"

class MainTask:
    def __init__(self, item: str, action_plan: List[Dict], task_id: int, departure_position: Dict = None):
        self.task_id = task_id
        self.item = item
        self.action_plan = action_plan
        self.departure_position = departure_position
        self.sub_tasks: List[SubTask] = []
        self.status = TaskStatus.PENDING
        
        self._build_from_plan()
    
    def _build_from_plan(self):
        """直接根据 LLM 规划的 Action Plan 构建原子子任务"""
        for action_dict in self.action_plan:
            action_name = action_dict.get("action")
            try:
                task_type = TaskType(action_name)
                # 如果这个动作需要用到出发点信息，塞入 data 中
                if action_dict.get("location") == "__DEPARTURE__" and self.departure_position:
                    action_dict["departure_position"] = self.departure_position
                
                self.sub_tasks.append(SubTask(task_type, action_dict))
            except ValueError:
                print(f"⚠️ 警告: 遇到未知的原子操作类型: {action_name}")
    
    def __repr__(self):
        return f"MainTask(#{self.task_id}, {self.item}, {len(self.sub_tasks)} actions)"

class TaskManager:
    # 保持原有的栈管理逻辑，只需修改 add_task 和 interrupt 的签名
    def __init__(self):
        self.preparation_stack: List[MainTask] = []
        self.execution_stack: List[SubTask] = []
        self.current_task: Optional[MainTask] = None
        self.paused_tasks: List[MainTask] = []
        self.task_counter = 0
        self.lock = threading.RLock()
    
    def add_task(self, item: str, action_plan: List[Dict], departure_position: Dict = None) -> int:
        with self.lock:
            self.task_counter += 1
            task = MainTask(item, action_plan, self.task_counter, departure_position)
            self.preparation_stack.append(task)
            
            print(f"\n📋 LLM 规划任务已加载到预备栈 ID: #{task.task_id}")
            return task.task_id

    def interrupt_and_execute(self, item: str, action_plan: List[Dict], departure_position: Dict = None) -> int:
        with self.lock:
            if self.current_task and self.current_task.status == TaskStatus.RUNNING:
                self.current_task.status = TaskStatus.PAUSED
                self.paused_tasks.append(self.current_task)
                self.current_task.remaining_sub_tasks = self.execution_stack.copy()
                self.execution_stack.clear()
            
            task_id = self.add_task(item, action_plan, departure_position)
            self._load_next_task()
            return task_id
            
    # ...existing code for _load_next_task, get_next_sub_task, complete_current_sub_task etc...
    # (这部分代码不需要任何改动，照抄您原有的逻辑即可)
    def _load_next_task(self):
        if not self.preparation_stack:
            return False
        task = self.preparation_stack.pop()
        self.current_task = task
        task.status = TaskStatus.RUNNING
        for sub_task in reversed(task.sub_tasks):
            self.execution_stack.append(sub_task)
        self._print_execution_stack()
        return True
    
    def get_next_sub_task(self) -> Optional[SubTask]:
        with self.lock:
            if not self.execution_stack:
                if self.preparation_stack:
                    self._load_next_task()
                elif self.paused_tasks:
                    self._resume_paused_task()
                else:
                    return None
            if self.execution_stack:
                return self.execution_stack[-1]
            return None
    
    def complete_current_sub_task(self):
        with self.lock:
            if self.execution_stack:
                completed = self.execution_stack.pop()
                completed.status = TaskStatus.COMPLETED
                print(f"✓ 原子任务完成: {completed.task_type.value}")
                if not self.execution_stack and self.current_task:
                    self.current_task.status = TaskStatus.COMPLETED
                    print(f"🎉 整体任务 #{self.current_task.task_id} 执行结束")
                    self.current_task = None
    
    def _resume_paused_task(self):
        if not self.paused_tasks: return
        task = self.paused_tasks.pop(0)
        self.current_task = task
        task.status = TaskStatus.RUNNING
        if hasattr(task, 'remaining_sub_tasks'):
            self.execution_stack = task.remaining_sub_tasks.copy()
            delattr(task, 'remaining_sub_tasks')
        print(f"\n▶️ 恢复暂停任务 #{task.task_id}")
    
    def _print_execution_stack(self):
        print(f"\n📚 动作执行栈 (栈顶->栈底):")
        for i, sub_task in enumerate(reversed(self.execution_stack)):
            print(f"  {'👉' if i==0 else '  '} {sub_task.task_type.value}")