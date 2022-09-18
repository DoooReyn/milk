from PyQt5.QtWidgets import QWidget

from milk.view.about_view_base import AboutBaseView
from milk.conf import LangUI

ABOUT = """
# 离线翻译

## 一、是什么？

- 此工具是以机器学习的训练模型为基础的离线翻译工具

## 二、怎么用？

1. 载入 [Ctranslate2/SentencePiece/FastText] 训练模型
2. 设置源语言和目标语言
3. 翻译

## 三、参考

- [Ctranslate2](https://github.com/OpenNMT/CTranslate2)
- [SentencePiece](https://github.com/google/sentencepiece)
- [FastText](https://github.com/facebookresearch/fastText)
- [DesktopTranslator](https://github.com/ymoslem/DesktopTranslator)
"""


class AboutView(AboutBaseView):
    def __init__(self, parent: QWidget = None):
        super(AboutView, self).__init__(parent, ABOUT)

        self.setWindowTitle(LangUI.translate_title)
        self.setFixedSize(520, 480)
