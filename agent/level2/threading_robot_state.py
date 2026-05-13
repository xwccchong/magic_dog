import threading
import copy
from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
from unitree_sdk2py.idl.unitree_go.msg.dds_ import LowState_
from unitree_sdk2py.idl.unitree_go.msg.dds_ import SportModeState_

class RobotStateObserver:
    def __init__(self, network_interface="eth0"):
        self.network_interface = network_interface
        
        # 内部维护的机器人状态字典
        self._robot_data = {
            "battery_soc": 0,
            "voltage": 0.0,
            "position": [0.0, 0.0, 0.0],
            "velocity": [0.0, 0.0, 0.0],
            "yaw": 0.0
        }
        
        # 线程锁：防止主线程读取和DDS后台线程写入发生冲突
        self._lock = threading.Lock()
        self._is_initialized = False

    def start(self):
        """启动底层数据订阅 (非阻塞)"""
        if self._is_initialized:
            print("[Warning] Observer 已经启动，无需重复调用。")
            return

        print(f"[Observer] 正在通过 {self.network_interface} 初始化 DDS 通道...")
        ChannelFactoryInitialize(0, self.network_interface)
        
        # 初始化订阅者，传入类内部的方法作为回调
        self.sub_low = ChannelSubscriber("rt/lowstate", LowState_)
        self.sub_low.Init(self._low_state_handler, 10)
        
        self.sub_sport = ChannelSubscriber("rt/sportmodestate", SportModeState_)
        self.sub_sport.Init(self._sport_state_handler, 10)
        
        self._is_initialized = True
        print("[Observer] ✅ 后台订阅已就绪，状态更新中...")

    # ================= DDS 回调函数 (后台自动触发) =================
    
    def _low_state_handler(self, msg: LowState_):
        # 写入数据前加锁
        with self._lock:
            self._robot_data["battery_soc"] = msg.bms_state.soc
            self._robot_data["voltage"] = msg.bms_state.voltage

    def _sport_state_handler(self, msg: SportModeState_):
        with self._lock:
            self._robot_data["position"] = [msg.position[0], msg.position[1], msg.position[2]]
            self._robot_data["velocity"] = [msg.velocity[0], msg.velocity[1], msg.velocity[2]]
            self._robot_data["yaw"] = msg.imu_state.rpy[2]

    # ================= 对外暴露的无阻塞 Getter 方法 =================
    
    def get_battery(self):
        """获取当前电量与电压"""
        with self._lock:
            return self._robot_data["battery_soc"], self._robot_data["voltage"]

    def get_posture(self):
        """获取当前位置、速度与偏航角"""
        with self._lock:
            return {
                # 使用 copy() 防止外部直接修改导致内部状态被破坏
                "position": self._robot_data["position"].copy(),
                "velocity": self._robot_data["velocity"].copy(),
                "yaw": self._robot_data["yaw"]
            }
            
    def get_all_state(self):
        """一次性获取所有状态快照"""
        with self._lock:
            return copy.deepcopy(self._robot_data)