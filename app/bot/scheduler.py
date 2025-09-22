"""Stage 1 调度模块占位。"""  # 当前仅占位，尚未提供调度功能
from __future__ import annotations  # 继续支持未来注解


class SchedulerService:  # 计划在 Stage 2 接入的调度包装类
    """后续会封装 PTB JobQueue 等调度逻辑。"""  # 提示当前为空实现

    def start(self) -> None:  # 启动调度器的接口
        """Stage 2 时实现定时任务启动。"""  # 注明时间线
        raise NotImplementedError("调度逻辑尚未开发")  # 明确状态

    def stop(self) -> None:  # 停止调度器的接口
        """Stage 2 时提供优雅停止逻辑。"""  # 注明未来工作
        raise NotImplementedError("调度逻辑尚未开发")  # 明确状态
