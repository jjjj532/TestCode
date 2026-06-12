from importlib.metadata import entry_points

from testcode_core.tools.registry import ToolRegistry
from testcode_plugin.hooks import PluginHooks


class PluginLoader:
    def __init__(self, group: str = "testcode.plugins"):
        self.group = group
        self._plugins: list[PluginHooks] = []

    def discover(self) -> list[PluginHooks]:
        eps = entry_points(group=self.group)
        self._plugins = []
        for ep in eps:
            obj = ep.load()
            if isinstance(obj, PluginHooks):
                self._plugins.append(obj)
        return self._plugins

    @property
    def plugins(self) -> list[PluginHooks]:
        return self._plugins

    def load_tools(self, registry: ToolRegistry) -> int:
        count = 0
        for plugin in self._plugins:
            for func in plugin.tools:
                meta = getattr(func, "_testcode_tool", None)
                if meta:
                    registry.register(
                        description=meta["description"],
                        parameters=meta["parameters"],
                    )(func)
                    count += 1
        return count
