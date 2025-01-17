"""ToolDelta 启动器"""

import os
import time
import traceback

from .color_print import Print
from .frame import GameCtrl, ToolDelta
from .plugin_load.PluginGroup import plugin_group
from .sys_args import sys_args_to_dict
from .urlmethod import check_update
from .utils import timer_event_boostrap, tmpjson_save

tooldelta = ToolDelta()


def start_tool_delta() -> None:
    """启动 ToolDelta"""
    try:
        tooldelta.welcome()
        if "no-update-check" not in sys_args_to_dict():
            check_update()
        else:
            Print.print_war("将不会进行自动更新。")
        tooldelta.basic_operation()
        tooldelta.loadConfiguration()
        tooldelta.launcher.init()
        game_control = GameCtrl(tooldelta)
        tooldelta.set_game_control(game_control)
        tooldelta.set_plugin_group(plugin_group)
        plugin_group.set_frame(tooldelta)
        plugin_group.read_all_plugins()
        timer_event_boostrap()
        tmpjson_save()
        tooldelta.launcher.listen_launched(game_control.system_inject)
        game_control.set_listen_packets()
        raise tooldelta.launcher.launch()
    except (KeyboardInterrupt, SystemExit, EOFError) as err:
        Print.print_inf(f"ToolDelta 已关闭，退出原因：{err}")
        pass
    except Exception:
        Print.print_err(f"ToolDelta 运行过程中出现问题：{traceback.format_exc()}")
        input(Print.clean_fmt("§c按回车键退出..."))


def safe_jump(out_task: bool = True, exit_directly: bool = True) -> None:
    """安全退出

    Args:
        out_task (bool, optional): frame 框架系统是否退出
        exit_directly (bool, optional): 是否三秒强制直接退出
    """
    if out_task:
        tooldelta.system_exit()
    tooldelta.safelyExit()
    if exit_directly:
        for _ in range(3, -1, -1):
            Print.print_war(f"{_}秒后强制退出...", end="\r")
            time.sleep(1)
        Print.print_suc("ToolDelta 已退出。")
        os._exit(0)
    Print.print_suc("ToolDelta 已退出。")
