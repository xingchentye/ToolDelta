import os, sys, traceback
from ...color_print import Print
from ...builtins import Builtins
from ...cfg import Cfg
from ..funcs import unzip_plugin

class Plugin:
    name = "<未命名插件>"
    version = (0, 0, 1)
    author = "?"

    def __init__(self):
        self.require_listen_packets = []
        self.dotcs_old_type = False

    def _add_req_listen_packet(self, pktID):
        if not pktID in self.require_listen_packets:
            self.require_listen_packets.append(pktID)


class PluginAPI:
    name = "<未命名插件api>"
    version = (0, 0, 1)

    def __init__(self, _):
        raise Exception("需要初始化__init__方法")

def read_plugin_from_new(plugin_grp, root_env: dict):
    PLUGIN_PATH = os.path.join(os.getcwd(), "插件文件/ToolDelta组合式插件")
    for plugin_dir in os.listdir(PLUGIN_PATH):
        if (
            not os.path.isdir(os.path.join(PLUGIN_PATH, plugin_dir.strip(".zip")))
            and os.path.isfile(os.path.join(PLUGIN_PATH, plugin_dir))
            and plugin_dir.endswith(".zip")
        ):
            Print.print_with_info(f"§6正在解压插件{plugin_dir}, 请稍后", "§6 解压 ")
            unzip_plugin(
                os.path.join(PLUGIN_PATH, plugin_dir),
                os.path.join("插件文件/ToolDelta组合式插件", plugin_dir.strip(".zip"))
            )
            Print.print_suc(f"§a成功解压插件{plugin_dir} -> 插件目录")
            plugin_dir = plugin_dir.strip(".zip")
        if os.path.isdir(os.path.join(PLUGIN_PATH, plugin_dir)):
            sys.path.append(os.path.join(PLUGIN_PATH, plugin_dir))
            plugin_grp.plugin_added_cache["plugin"] = None
            plugin_grp.plugin_added_cache["packets"].clear()
            plugin_grp.pluginAPI_added_cache.clear()
            try:
                if os.path.isfile(
                    os.path.join("插件文件/ToolDelta组合式插件", plugin_dir, "__init__.py")
                ):
                    with open(
                        os.path.join("插件文件/ToolDelta组合式插件", plugin_dir, "__init__.py"),
                        "r",
                        encoding="utf-8",
                    ) as f:
                        code = f.read()
                    exec(code, root_env)
                    # 理论上所有插件共享一个整体环境
                else:
                    Print.print_war(f"{plugin_dir} 文件夹 未发现插件文件, 跳过加载")
                    continue
                assert plugin_grp.plugin_added_cache["plugin"] is not None, 2
                plugin = plugin_grp.plugin_added_cache["plugin"]
                plugin_body: Plugin = plugin(plugin_grp.linked_frame)
                plugin_grp.plugins.append([plugin_body.name, plugin_body])
                _v0, _v1, _v2 = plugin_body.version  # type: ignore
                if hasattr(plugin_body, "on_def"):
                    plugin_grp.plugins_funcs["on_def"].append(
                        [plugin_body.name, plugin_body.on_def]
                    )
                if hasattr(plugin_body, "on_inject"):
                    plugin_grp.plugins_funcs["on_inject"].append(
                        [plugin_body.name, plugin_body.on_inject]
                    )
                if hasattr(plugin_body, "on_player_prejoin"):
                    plugin_grp.plugins_funcs["on_player_prejoin"].append(
                        [plugin_body.name, plugin_body.on_player_prejoin]
                    )
                if hasattr(plugin_body, "on_player_join"):
                    plugin_grp.plugins_funcs["on_player_join"].append(
                        [plugin_body.name, plugin_body.on_player_join]
                    )
                if hasattr(plugin_body, "on_player_message"):
                    plugin_grp.plugins_funcs["on_player_message"].append(
                        [plugin_body.name, plugin_body.on_player_message]
                    )
                if hasattr(plugin_body, "on_player_death"):
                    plugin_grp.plugins_funcs["on_player_death"].append(
                        [plugin_body.name, plugin_body.on_player_death]
                    )
                if hasattr(plugin_body, "on_player_leave"):
                    plugin_grp.plugins_funcs["on_player_leave"].append(
                        [plugin_body.name, plugin_body.on_player_leave]
                    )
                Print.print_suc(
                    f"成功载入插件 {plugin_body.name} 版本: {_v0}.{_v1}.{_v2} 作者：{plugin_body.author}"
                )
                plugin_grp.normal_plugin_loaded_num += 1
                if plugin_grp.plugin_added_cache["packets"] != []:
                    for pktType, func in plugin_grp.plugin_added_cache["packets"]:  # type: ignore
                        plugin_grp._add_listen_packet_id(pktType)
                        plugin_grp._add_listen_packet_func(
                            pktType, getattr(plugin_body, func.__name__)
                        )
                if plugin_grp.pluginAPI_added_cache is not None:
                    for _api in plugin_grp.pluginAPI_added_cache:
                        if isinstance(_api, str):
                            plugin_grp.plugins_api[_api] = plugin_body
                        else:
                            (apiName, api) = _api
                            plugin_grp.plugins_api[apiName] = api(plugin_grp.linked_frame)
            except AssertionError as err:
                if err.args[0] == 2:
                    Print.print_err(
                        f"插件 {plugin_dir} 不合法: 只能调用一次 @plugins.add_plugin, 实际调用了0次或多次"
                    )
                    raise SystemExit
                if len(err.args[0]) == 2:
                    Print.print_err(f"插件 {plugin_dir} 不合法: {err.args[0][1]}")
                    raise SystemExit
                else:
                    raise
            except Cfg.ConfigError as err:
                Print.print_err(f"插件 {plugin_dir} 配置文件报错：{err}")
                Print.print_err(f"你也可以直接删除配置文件, 重新启动ToolDelta以自动生成配置文件")
                raise SystemExit
            except Builtins.SimpleJsonDataReader.DataReadError as err:
                Print.print_err(f"插件 {plugin_dir} 读取数据失败: {err}")
            except plugin_grp.linked_frame.SystemVersionException:
                Print.print_err(f"插件 {plugin_dir} 需要更高版本的ToolDelta加载: {err}")
            except Exception as err:
                if "() takes no arguments" in str(err):
                    Print.print_err(f"插件 {plugin_dir} 不合法： 主类初始化时应接受 1 个参数: Frame")
                else:
                    Print.print_err(f"加载插件 {plugin_dir} 出现问题, 报错如下: ")
                    Print.print_err("§c" + traceback.format_exc())
                    raise SystemExit