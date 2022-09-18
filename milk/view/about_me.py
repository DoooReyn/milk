from PyQt5.QtWidgets import QWidget

from milk.conf import LangUI
from milk.view.about_view_base import AboutBaseView

ABOUT_ME = """
### Hi, there! 🤠 I'm DoooReyn.

-   🐼  A game developer from China
-   👷‍️ A repeat wheel maker
-   😘  A faithful fan of PyQt
-   🧙‍️ Currently focusing on `Cocos2d-x / Cocos Creator`


### Projects

-   📘 [微信读书自动阅读器 Web版](https://github.com/DoooReyn/WxRead-WebAutoReader) 
-   📗 [微信读书自动阅读器 PC版](https://github.com/DoooReyn/WxRead-PC-AutoReader)
-   👌 [手势识别与训练模型](https://wu57.cn/Game/gestures/)
-   🖕 [Cocos Creator 手势识别](https://github.com/DoooReyn/ccc-gesture-recognition) > [在线演示](https://wu57.cn/games/gesture/web-desktop/)
-   😎 [Cocos2d-x 目录监视器](https://github.com/DoooReyn/cocos2d-x-dir-monitor)
-   🛤️ [Cocos2d-x 内置 WebSocket 服务器](https://github.com/DoooReyn/cocos2d-x-lws)
-   💻 [Cocos2d-x 内置 HTTP 服务器](https://github.com/DoooReyn/cocos2d-x-lhs)
-   🎸 [Cocos2d-x Fmod 集成指南](https://github.com/DoooReyn/fmod-for-cocos2dx)
-   📓 [Cocos2d-x 使用 spdlog](https://github.com/DoooReyn/cocos2d-x-spdlog)
-   🌕 [Cocos2d-x 接入 lua-protobuf](https://github.com/DoooReyn/cocos2d-x-lua-protobuf)
-   🕹️ [Console for Cocos2d-x based on PyQt5](https://github.com/DoooReyn/Console)
-   🧰 [位图字体工具箱 BMFontToolbox](https://github.com/DoooReyn/BMFontToolbox)
-   💰 [给人事的工资明细助手](https://wu57.cn/Game/SalaryBook/)
-   ⚔️ [Lua 字符串插值](https://github.com/DoooReyn/lua-string-interpolate)
-   📬 [Formatted log for Lua](https://github.com/DoooReyn/lua_format_log)
-   📚 [IT 电子书收藏夹](https://github.com/DoooReyn/dbooks-links.git)
-   📒 [微信/支付宝账单转换器](https://github.com/DoooReyn/wechat-alipay-bill-converter)
-   👾 [虾虾虾鼓捣的 Web Game Demo](https://wu57.cn/Game/games/)

### Find Me

-   ✍️ [Blog](https://wu57.cn/)
-   📚 [简书](https://www.jianshu.com/u/5b3708fe7f63)
-   💌 jl88744653@gmail.com

"""


class AboutMe(AboutBaseView):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent, ABOUT_ME)

        self.setWindowTitle(LangUI.view_about_me)
        self.setFixedSize(600, 472)
