from typing import Union

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget

from milk.conf import signals, UIDef
from milk.view.ui_base import UIBase

ABOUT_ME = """
### Hi, there! ð¤  I'm DoooReyn.

-   ð¼  A game developer from China
-   ð·âï¸ A repeat wheel maker
-   ð  A faithful fan of PyQt
-   ð§âï¸ Currently focusing on `Cocos2d-x / Cocos Creator`


### Projects

-   ð [å¾®ä¿¡è¯»ä¹¦èªå¨éè¯»å¨ Webç](https://github.com/DoooReyn/WxRead-WebAutoReader) 
-   ð [å¾®ä¿¡è¯»ä¹¦èªå¨éè¯»å¨ PCç](https://github.com/DoooReyn/WxRead-PC-AutoReader)
-   ð [æå¿è¯å«ä¸è®­ç»æ¨¡å](https://wu57.cn/Game/gestures/)
-   ð [Cocos Creator æå¿è¯å«](https://github.com/DoooReyn/ccc-gesture-recognition) > [å¨çº¿æ¼ç¤º](https://wu57.cn/games/gesture/web-desktop/)
-   ð [Cocos2d-x ç®å½çè§å¨](https://github.com/DoooReyn/cocos2d-x-dir-monitor)
-   ð¤ï¸ [Cocos2d-x åç½® WebSocket æå¡å¨](https://github.com/DoooReyn/cocos2d-x-lws)
-   ð» [Cocos2d-x åç½® HTTP æå¡å¨](https://github.com/DoooReyn/cocos2d-x-lhs)
-   ð¸ [Cocos2d-x Fmod éææå](https://github.com/DoooReyn/fmod-for-cocos2dx)
-   ð [Cocos2d-x ä½¿ç¨ spdlog](https://github.com/DoooReyn/cocos2d-x-spdlog)
-   ð [Cocos2d-x æ¥å¥ lua-protobuf](https://github.com/DoooReyn/cocos2d-x-lua-protobuf)
-   ð¹ï¸ [Console for Cocos2d-x based on PyQt5](https://github.com/DoooReyn/Console)
-   ð§° [ä½å¾å­ä½å·¥å·ç®± BMFontToolbox](https://github.com/DoooReyn/BMFontToolbox)
-   ð° [ç»äººäºçå·¥èµæç»å©æ](https://wu57.cn/Game/SalaryBook/)
-   âï¸ [Lua å­ç¬¦ä¸²æå¼](https://github.com/DoooReyn/lua-string-interpolate)
-   ð¬ [Formatted log for Lua](https://github.com/DoooReyn/lua_format_log)
-   ð [IT çµå­ä¹¦æ¶èå¤¹](https://github.com/DoooReyn/dbooks-links.git)
-   ð [å¾®ä¿¡/æ¯ä»å®è´¦åè½¬æ¢å¨](https://github.com/DoooReyn/wechat-alipay-bill-converter)
-   ð¾ [è¾è¾è¾é¼æ£ç Web Game Demo](https://wu57.cn/Game/games/)

### Find Me

-   âï¸ [Blog](https://wu57.cn/)
-   ð [ç®ä¹¦](https://www.jianshu.com/u/5b3708fe7f63)
-   ð jl88744653@gmail.com

"""


class AboutMe(UIBase):
    def __init__(self, parent: QWidget = None):
        self.ui_text_browser: Union[QTextBrowser, None] = None
        super().__init__(parent)

    def setup_ui(self):
        self.add_vertical_layout(self)
        self.ui_text_browser = self.add_text_browser(self)
        self.ui_text_browser.setReadOnly(True)
        self.ui_text_browser.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse)
        self.ui_text_browser.setAcceptRichText(True)
        self.ui_text_browser.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.ui_text_browser.setOpenExternalLinks(True)
        self.ui_text_browser.setMarkdown(ABOUT_ME)
        self.setFixedSize(520, 520)

    def closeEvent(self, event):
        event.accept()
        signals.window_closed.emit(UIDef.FileAboutMe.value)
