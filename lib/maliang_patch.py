from maliang.core import containers


# 防御性补丁：某些 macOS 环境下 maliang widget 的事件处理会访问到
# 尚未完全初始化的 widget，导致 'capture_events' 属性缺失。
# 这里把直接属性访问改为 getattr，避免 AttributeError 弹窗，同时保留原方法的其它副作用。
def _safe_on_click(self, event, name):
    self.focus_set()
    self.hide_focus()
    self.trigger_focus.reset()
    for widget in reversed(self.widgets):
        if hasattr(widget, 'feature') and not widget.disappeared:
            if widget.feature.get_method(name)(event):
                self._focus_widget = widget
                if getattr(widget, 'capture_events', None):
                    event.x = 9999
    self.trigger_focus.update(True, "")


def _safe_on_release(self, event, name):
    for widget in reversed(self.widgets):
        if hasattr(widget, 'feature') and not widget.disappeared:
            if widget.feature.get_method(name)(event) and getattr(widget, 'capture_events', None):
                event.x = 9999

def patch():
	containers.Canvas.on_click = _safe_on_click
	containers.Canvas.on_release = _safe_on_release