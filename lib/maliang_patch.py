from maliang import Canvas
from tkinter import Event
from maliang.color import convert


# 防御性补丁：某些 macOS 环境下 maliang widget 的事件处理会访问到
# 尚未完全初始化的 widget，导致 'capture_events' 属性缺失。
# 这里把直接属性访问改为 getattr，避免 AttributeError 弹窗，同时保留原方法的其它副作用。
def _safe_on_click(self: Canvas, event: Event, name: str):
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


def _safe_on_release(self: Canvas, event: Event, name: str):
    for widget in reversed(self.widgets):
        if hasattr(widget, 'feature') and not widget.disappeared:
            if widget.feature.get_method(name)(event) and getattr(widget, 'capture_events', None):
                event.x = 9999


def _safe_on_motion(self: Canvas, event: Event, name: str):
    self.trigger_config.reset()
    for widget in reversed(self.widgets):
        if hasattr(widget, 'feature') and not widget.disappeared:
            flag = widget.feature.get_method(name)(event)
            capture = getattr(widget, 'capture_events', None)
            if capture is None:
                if flag:
                    event.x = 9999
            elif capture:
                event.x = 9999
    self.trigger_config.update(cursor="arrow")


def _safe_on_wheel(self: Canvas, event: Event, type_: bool | None):
    if type_ is not None:
        event.delta = 120 if type_ else -120
    for widget in reversed(self.widgets):
        if hasattr(widget, 'feature') and not widget.disappeared:
            if widget.feature.get_method("<MouseWheel>")(event) and getattr(widget, 'capture_events', None):
                event.x = 9999


def _safe_on_key_press(self: Canvas, event: Event):
    for widget in reversed(self.widgets):
        if hasattr(widget, 'feature') and not widget.disappeared:
            if widget.feature.get_method("<KeyPress>")(event) and getattr(widget, 'capture_events', None):
                event.x = 9999


def _safe_on_key_release(self: Canvas, event: Event):
    for widget in reversed(self.widgets):
        if hasattr(widget, 'feature') and not widget.disappeared:
            if widget.feature.get_method("<KeyRelease>")(event) and getattr(widget, 'capture_events', None):
                event.x = 9999


def _safe_register_event(self: Canvas, name: str, *, add=None):
    def handle_event(event: Event) -> None:
        for widget in reversed(self.widgets):
            if hasattr(widget, 'feature'):
                if widget.feature.get_method(name)(event) and getattr(widget, 'capture_events', None):
                    pass

    return self.bind(name, handle_event, add)


# 颜色安全补丁：macOS 上 tkinter.winfo_rgb 会返回 16 位颜色值，
# 而 maliang 的 rgb_to_hex 期望 8 位值，导致生成类似 #00408F40BF 的非法颜色字符串。
# 这里对颜色值做裁剪/归一化，确保最终生成的十六进制颜色始终合法。
def _clamp_rgb(value):
    return tuple(max(0, min(255, int(v))) for v in value)


_orig_rgb_to_hex = convert.rgb_to_hex


def _safe_rgb_to_hex(value, /):
    return _orig_rgb_to_hex(_clamp_rgb(value))


_orig_rgba_to_hex = convert.rgba_to_hex


def _safe_rgba_to_hex(value, /):
    r, g, b, a = value
    return _orig_rgba_to_hex((*_clamp_rgb((r, g, b)), max(0.0, min(1.0, a))))


_orig_name_to_rgb = convert.name_to_rgb


def _safe_name_to_rgb(value, /):
    result = _orig_name_to_rgb(value)
    # winfo_rgb 在 macOS 上可能返回 16 位 RGB（0~65535），需要归一化为 8 位
    if any(v > 255 for v in result):
        return tuple(int(v / 256) for v in result)
    return result


def patch():
    Canvas.on_click = _safe_on_click
    Canvas.on_release = _safe_on_release
    Canvas.on_motion = _safe_on_motion
    Canvas.on_wheel = _safe_on_wheel
    Canvas.on_key_press = _safe_on_key_press
    Canvas.on_key_release = _safe_on_key_release
    Canvas.register_event = _safe_register_event
    convert.rgb_to_hex = _safe_rgb_to_hex
    convert.rgba_to_hex = _safe_rgba_to_hex
    convert.name_to_rgb = _safe_name_to_rgb
