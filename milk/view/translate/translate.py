from typing import Optional

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QButtonGroup, QComboBox, QFileDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, \
    QPushButton, QRadioButton, QTextBrowser, QTextEdit, QWidget
from system_hotkey import SystemHotkey

from milk.cmm import Cmm
from milk.conf import LangUI, ResMap, settings, UIDef, UserKey
from milk.gui import GUI
from milk.view.ui_base import UIBase
from .conf import BeamSize, SupportLanguages, TranslateMenus, URL_M2M_100_12B, URL_M2M_100_418M
from .translator import ModelTranslator


class TranslateView(UIBase):
    def __init__(self, parent: QWidget = None):
        self.ui_text_source: Optional[QTextEdit] = None
        self.ui_text_target: Optional[QTextBrowser] = None
        self.ui_btn_translate: Optional[QPushButton] = None
        self.ui_btn_copy: Optional[QPushButton] = None
        self.ui_combo_source: Optional[QComboBox] = None
        self.ui_combo_target: Optional[QComboBox] = None
        self.ui_radio_group: Optional[QButtonGroup] = None
        self.ui_edit_ctranslate2: Optional[QLineEdit] = None
        self.ui_edit_sentence_piece: Optional[QLineEdit] = None
        self.ui_edit_fasttext: Optional[QLineEdit] = None
        self.grid_layout: Optional[QGridLayout] = None

        self.translator: ModelTranslator = ModelTranslator()

        self.setup_window_code(UIDef.ToolsTranslate.value)
        self.setup_translate()

        super().__init__(parent)

    def setup_radios(self):
        radio_container = QFrame(self)
        radio_layout = QHBoxLayout()
        self.ui_radio_group = QButtonGroup(radio_container)
        ui_radio_1 = QRadioButton(LangUI.translate_quality_1, radio_container)
        ui_radio_2 = QRadioButton(LangUI.translate_quality_2, radio_container)
        ui_radio_3 = QRadioButton(LangUI.translate_quality_3, radio_container)
        ui_lab_radio = QLabel(LangUI.translate_quality)
        ui_font_radio = ui_radio_1.font()
        ui_font_radio.setPointSize(11)
        ui_radio_1.setFont(ui_font_radio)
        ui_radio_2.setFont(ui_font_radio)
        ui_radio_3.setFont(ui_font_radio)
        radio_layout.addWidget(ui_lab_radio)
        radio_layout.addWidget(ui_radio_1)
        radio_layout.addWidget(ui_radio_2)
        radio_layout.addWidget(ui_radio_3)
        radio_container.setLayout(radio_layout)
        self.ui_radio_group.addButton(ui_radio_1, BeamSize.Standard)
        self.ui_radio_group.addButton(ui_radio_2, BeamSize.Great)
        self.ui_radio_group.addButton(ui_radio_3, BeamSize.Excellent)
        self.ui_radio_group.setExclusive(True)
        self.ui_radio_group.button(BeamSize.Standard).setChecked(True)
        return radio_container

    def setup_ui(self):
        self.setWindowTitle(LangUI.translate_title)

        self.grid_layout = self.add_grid_layout(self)

        lab_ctranslate2 = QLabel('CTranslate2')
        self.ui_edit_ctranslate2 = QLineEdit()
        self.ui_edit_ctranslate2.setReadOnly(True)
        self.ui_edit_ctranslate2.setText(settings.value(UserKey.Translator.ctranslate2_model, '', str))
        self.ui_edit_ctranslate2.setCursorPosition(0)

        lab_sentence_piece = QLabel('SentencePiece')
        self.ui_edit_sentence_piece = QLineEdit()
        self.ui_edit_sentence_piece.setReadOnly(True)
        self.ui_edit_sentence_piece.setText(settings.value(UserKey.Translator.sentence_piece_model, '', str))
        self.ui_edit_sentence_piece.setCursorPosition(0)

        lab_fasttext = QLabel('FastText')
        self.ui_edit_fasttext = QLineEdit()
        self.ui_edit_fasttext.setReadOnly(True)
        self.ui_edit_fasttext.setText(settings.value(UserKey.Translator.fasttext_model, '', str))
        self.ui_edit_fasttext.setCursorPosition(0)

        self.ui_combo_source = QComboBox()
        self.ui_combo_source.setMinimumWidth(120)
        self.ui_combo_source.addItems([
            LangUI.translate_lang_en,
            LangUI.translate_lang_zh,
            LangUI.translate_lang_ja,
            LangUI.translate_lang_kr,
        ])
        self.ui_combo_source.setCurrentIndex(0)
        GUI.init_combo_box(self.ui_combo_source)

        btn_switch = QPushButton(QIcon(ResMap.img_switch), '')
        btn_switch.setCheckable(False)
        btn_switch.setStyleSheet('QPushButton { border: none; }')

        self.ui_combo_target = QComboBox()
        self.ui_combo_target.setMinimumWidth(120)
        self.ui_combo_target.addItems([
            LangUI.translate_lang_en,
            LangUI.translate_lang_zh,
            LangUI.translate_lang_ja,
            LangUI.translate_lang_kr,
        ])
        self.ui_combo_target.setCurrentIndex(1)
        GUI.init_combo_box(self.ui_combo_target)

        radio_container = self.setup_radios()

        self.ui_text_source = QTextEdit()
        self.ui_text_source.setFontFamily('Microsoft YeHei')
        self.ui_text_source.setFontPointSize(11)
        self.ui_text_source.setAcceptRichText(False)
        self.ui_text_source.setPlaceholderText(LangUI.translate_input)

        self.ui_text_target = QTextBrowser()
        self.ui_text_target.setPlaceholderText(LangUI.translate_display_result)
        self.ui_text_target.setFontFamily('Microsoft YeHei')
        self.ui_text_target.setAcceptRichText(False)
        self.ui_text_target.setFontPointSize(11)

        self.ui_btn_translate = QPushButton(LangUI.translate_translate)
        self.ui_btn_copy = QPushButton(LangUI.translate_copy_result)

        self.grid_layout.addWidget(lab_ctranslate2, 0, 0, 1, 1)
        self.grid_layout.addWidget(self.ui_edit_ctranslate2, 0, 1, 1, 5)

        self.grid_layout.addWidget(lab_sentence_piece, 1, 0, 1, 1)
        self.grid_layout.addWidget(self.ui_edit_sentence_piece, 1, 1, 1, 5)

        self.grid_layout.addWidget(lab_fasttext, 2, 0, 1, 1)
        self.grid_layout.addWidget(self.ui_edit_fasttext, 2, 1, 1, 5)

        self.grid_layout.addWidget(self.ui_text_source, 3, 0, 1, 6)

        self.grid_layout.addWidget(self.ui_combo_source, 4, 0, 1, 1)
        self.grid_layout.addWidget(btn_switch, 4, 1, 1, 1)
        self.grid_layout.addWidget(self.ui_combo_target, 4, 2, 1, 1)
        self.grid_layout.addWidget(radio_container, 4, 3, 1, 1)

        self.grid_layout.addWidget(self.ui_btn_translate, 5, 0, 1, 1)
        self.grid_layout.addWidget(self.ui_btn_copy, 5, 5, 1, 1)

        self.grid_layout.addWidget(self.ui_text_target, 6, 0, 1, 6)

        self.grid_layout.setRowStretch(3, 1)
        self.grid_layout.setRowStretch(6, 1)
        self.grid_layout.setColumnStretch(4, 1)

        self.setMinimumSize(640, 520)
        self.add_menu_bar(TranslateMenus)

    def setup_signals(self):
        self.ui_combo_target.currentIndexChanged.connect(self.on_translate)
        # self.ui_text_from.textChanged.connect(self.on_translate)
        self.ui_btn_translate.clicked.connect(self.on_translate)
        self.ui_btn_copy.clicked.connect(self.on_copy_result)
        self.ui_radio_group.idToggled.connect(self.on_radio_toggled)

        icon = QIcon(ResMap.img_folder_open)
        pos = QLineEdit.ActionPosition.TrailingPosition
        self.ui_edit_ctranslate2.addAction(icon, pos).triggered.connect(self.on_menu_select_ctranslate2_model)
        self.ui_edit_sentence_piece.addAction(icon, pos).triggered.connect(self.on_menu_select_sentence_piece_model)
        self.ui_edit_fasttext.addAction(icon, pos).triggered.connect(self.on_menu_select_fasttext_model)

        def bring_to_foreground(_=None):
            self.ui_text_source.paste()

        try:
            hk = SystemHotkey()
            hk.register(('control', 'shift', 'v'), callback=lambda x: bring_to_foreground(x))
        except Exception as e:
            print(e)

    def setup_translate(self):
        self.translator.set_c_model(settings.value(UserKey.Translator.ctranslate2_model, '', str))
        self.translator.set_s_model(settings.value(UserKey.Translator.sentence_piece_model, '', str))
        self.translator.set_f_model(settings.value(UserKey.Translator.fasttext_model, '', str))

    def error_result(self, text: str):
        self.ui_text_target.setText('<b style="color:red;">{0}</b>'.format(text))

    def on_translate(self):
        self.ui_text_target.setPlainText('')
        text = self.ui_text_source.toPlainText()
        source_code = SupportLanguages[self.ui_combo_source.currentIndex()]
        target_code = SupportLanguages[self.ui_combo_target.currentIndex()]
        results = self.translator.translate(source_code, target_code, text)
        if results:
            self.ui_text_target.setPlainText(results)
        else:
            self.error_result('翻译失败')

    def on_copy_result(self):
        if len(self.ui_text_target.toPlainText()) > 0:
            self.ui_text_target.selectAll()
            self.ui_text_target.copy()
            cursor = self.ui_text_target.textCursor()
            cursor.clearSelection()
            self.ui_text_target.setTextCursor(cursor)

    def on_radio_toggled(self, rid: int, toggled: bool):
        if toggled is True:
            self.translator.set_beam_size(rid)
            self.on_translate()

    def on_menu_select_ctranslate2_model(self):
        last_dir = settings.value(UserKey.Translator.ctranslate2_model, Cmm.user_document_dir(), str)
        choose_dir = QFileDialog.getExistingDirectory(self, "CTranslate2 模型", last_dir)
        if len(choose_dir) <= 0:
            return
        if self.translator.set_c_model(choose_dir):
            self.ui_edit_ctranslate2.setText(choose_dir)

    def on_menu_select_sentence_piece_model(self):
        last_dir = settings.value(UserKey.Translator.sentence_piece_model, Cmm.user_document_dir(), str)
        choose_filter = "SentencePiece Model(*.model)"
        [choose_dir, _] = QFileDialog.getOpenFileName(self, "SentencePiece 模型", last_dir, choose_filter)
        if len(choose_dir) <= 0:
            return
        if self.translator.set_s_model(choose_dir):
            self.ui_edit_sentence_piece.setText(choose_dir)

    def on_menu_select_fasttext_model(self):
        last_dir = settings.value(UserKey.Translator.fasttext_model, Cmm.user_document_dir(), str)
        choose_filter = "FastText Model(*.ftz)"
        [choose_dir, _] = QFileDialog.getOpenFileName(self, "FastText 模型", last_dir, choose_filter)
        if len(choose_dir) <= 0:
            return
        if self.translator.set_f_model(choose_dir):
            self.ui_edit_fasttext.setText(choose_dir)

    def on_menu_open_help(self):
        print('on_menu_open_help')
        pass

    def on_menu_open_about(self):
        print('on_menu_open_about')
        pass

    @staticmethod
    def on_menu_download_model_mini():
        Cmm.open_external_url(URL_M2M_100_418M)

    @staticmethod
    def on_menu_download_model_big():
        Cmm.open_external_url(URL_M2M_100_12B)
