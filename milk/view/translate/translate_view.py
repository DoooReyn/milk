from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QWidget

from milk.cmm import Cmm
from milk.conf import LangUI, ResMap, settings, UserKey
from milk.conf import UIDef
from milk.gui import GUI
from .about_view import AboutView
from .conf import SupportLanguages, URL_FASTTEXT_MODEL, URL_M2M_100_12B, URL_M2M_100_418M
from .conf import TRANSLATE_BEAM_DEFAULT_ID, TRANSLATE_BEAM_IDS, TRANSLATE_BEAM_SIZES, TRANSLATE_LANGUAGE_ITEMS, \
    TranslateMenus
from .translator import ModelTranslator


class _View(GUI.View):
    def __init__(self, parent: QWidget = None):
        super(_View, self).__init__(parent)

        # setup window property
        self.setWindowTitle(LangUI.translate_title)
        self.setMinimumSize(640, 520)

        # create widgets
        self.ui_lab_ctranslate = GUI.create_label('CTranslate2')
        self.ui_edit_ctranslate = GUI.create_line_edit(self.ctranslate_at(), True)

        self.ui_lab_sentence = GUI.create_label('SentencePiece')
        self.ui_edit_sentence = GUI.create_line_edit(self.sentence_at(), True)

        self.ui_lab_fasttext = GUI.create_label('FastText')
        self.ui_edit_fasttext = GUI.create_line_edit(self.fasttext_at(), True)

        self.ui_combo_source = GUI.create_combo_box(TRANSLATE_LANGUAGE_ITEMS)
        self.ui_combo_target = GUI.create_combo_box(TRANSLATE_LANGUAGE_ITEMS, 1)
        self.ui_icon_switch = GUI.create_icon_btn(ResMap.img_switch)
        self.ui_radio_box, self.ui_radio_group = GUI.create_radio_group(LangUI.translate_quality,
                                                                        TRANSLATE_BEAM_SIZES,
                                                                        TRANSLATE_BEAM_IDS,
                                                                        TRANSLATE_BEAM_DEFAULT_ID)

        self.ui_btn_translate = GUI.create_push_btn(LangUI.translate_translate)
        self.ui_btn_copy = GUI.create_push_btn(LangUI.translate_copy_result)

        self.ui_edit_source = GUI.create_text_edit(LangUI.translate_input, False)
        self.ui_edit_target = GUI.create_text_edit(LangUI.translate_display_result, False)

        # layout widgets
        self.ui_layout = GUI.create_grid_layout(self)
        GUI.add_grid_in_rows(self.ui_layout, (
            (
                GUI.GridItem(self.ui_lab_ctranslate, 0, 1),
                GUI.GridItem(self.ui_edit_ctranslate, 1, 5),
            ),
            (
                GUI.GridItem(self.ui_lab_sentence, 0, 1),
                GUI.GridItem(self.ui_edit_sentence, 1, 5),
            ),
            (
                GUI.GridItem(self.ui_lab_fasttext, 0, 1),
                GUI.GridItem(self.ui_edit_fasttext, 1, 5),
            ),
            (
                GUI.GridItem(self.ui_edit_source, 0, 6),
            ),
            (
                GUI.GridItem(self.ui_combo_source, 0, 1),
                GUI.GridItem(self.ui_icon_switch, 1, 1),
                GUI.GridItem(self.ui_combo_target, 2, 1),
                GUI.GridItem(self.ui_radio_box, 3, 1),
            ),
            (
                GUI.GridItem(self.ui_btn_translate, 0, 1),
                GUI.GridItem(self.ui_btn_copy, 5, 1),
            ),
            (
                GUI.GridItem(self.ui_edit_target, 0, 6),
            ),
        ))
        GUI.set_grid_span(self.ui_layout, rows=[4, 7], cols=[4])

        # menu bar
        self.ui_layout.setMenuBar(GUI.create_menu_bar(TranslateMenus, self))

    @staticmethod
    def ctranslate_at(default: str = ''):
        return settings.value(UserKey.Translator.ctranslate2_model, default, str)

    @staticmethod
    def sentence_at(default: str = ''):
        return settings.value(UserKey.Translator.sentence_piece_model, default, str)

    @staticmethod
    def fasttext_at(default: str = ''):
        return settings.value(UserKey.Translator.fasttext_model, default, str)

    @staticmethod
    def set_ctranslate_at(at: str):
        settings.setValue(UserKey.Translator.ctranslate2_model, at)

    @staticmethod
    def set_sentence_at(at: str):
        settings.setValue(UserKey.Translator.sentence_piece_model, at)

    @staticmethod
    def set_fasttext_at(at: str):
        settings.setValue(UserKey.Translator.fasttext_model, at)


class TranslateView(_View):
    def __init__(self, parent: QWidget = None):
        super(TranslateView, self).__init__(parent)
        self.translator: ModelTranslator = ModelTranslator()
        self.setup_window_code(UIDef.ToolsTranslate.value)
        self.setup_resize_keys(UserKey.Translator.window_width, UserKey.Translator.window_height)
        self.setup_ui_signals()
        self.setup_translation()

    def setup_ui_signals(self):
        icon = GUI.icon(ResMap.img_folder_open)
        pos = QLineEdit.TrailingPosition
        self.ui_edit_ctranslate.addAction(icon, pos).triggered.connect(self.on_menu_select_ctranslate2_model)
        self.ui_edit_sentence.addAction(icon, pos).triggered.connect(self.on_menu_select_sentence_piece_model)
        self.ui_edit_fasttext.addAction(icon, pos).triggered.connect(self.on_menu_select_fasttext_model)
        self.ui_combo_source.currentIndexChanged.connect(self.on_translate)
        self.ui_combo_target.currentIndexChanged.connect(self.on_translate)
        self.ui_btn_translate.clicked.connect(self.on_translate)
        self.ui_radio_group.idToggled.connect(self.on_radio_toggled)
        self.ui_btn_copy.clicked.connect(self.on_copy_result)

    def setup_translation(self):
        self.translator.set_c_model(self.ctranslate_at())
        self.translator.set_s_model(self.sentence_at())
        self.translator.set_f_model(self.fasttext_at())

    def on_translate(self):
        if len(self.ui_edit_source.toPlainText()) == 0:
            return
        self.ui_edit_target.clear()
        text = self.ui_edit_source.toPlainText()
        source_code = SupportLanguages[self.ui_combo_source.currentIndex()]
        target_code = SupportLanguages[self.ui_combo_target.currentIndex()]
        result = self.translator.translate(source_code, target_code, text)
        if result:
            self.ui_edit_target.setPlainText(result)

    def on_radio_toggled(self, rid: int, toggled: bool):
        if toggled is True:
            self.translator.set_beam_size(rid)
            # self.on_translate()

    def on_copy_result(self):
        if len(self.ui_edit_target.toPlainText()) > 0:
            self.ui_edit_target.selectAll()
            self.ui_edit_target.copy()
            cursor = self.ui_edit_target.textCursor()
            cursor.clearSelection()
            self.ui_edit_target.setTextCursor(cursor)

    def on_menu_select_ctranslate2_model(self):
        title = "Ctranslate2 model"
        where = self.ctranslate_at(Cmm.user_document_dir())
        chosen = GUI.dialog_for_directory_selection(self, title, where)
        origin = self.ui_edit_ctranslate.text()
        if chosen and origin != chosen and self.translator.set_c_model(chosen):
            self.ui_edit_ctranslate.setText(chosen)

    def on_menu_select_sentence_piece_model(self):
        title = "SentencePiece Model"
        where = self.sentence_at(Cmm.user_document_dir())
        filtered = "SentencePiece Model (*.model)"
        origin = self.ui_edit_sentence.text()
        chosen = GUI.dialog_for_file_selection(self, title, where, filtered)
        if chosen is not None and origin != chosen and self.translator.set_s_model(chosen):
            self.ui_edit_sentence.setText(chosen)

    def on_menu_select_fasttext_model(self):
        title = "FastText model"
        where = self.fasttext_at(Cmm.user_document_dir())
        filtered = "FastText Model(*.ftz)"
        origin = self.ui_edit_fasttext.text()
        chosen = GUI.dialog_for_file_selection(self, title, where, filtered)
        if chosen and origin != chosen and self.translator.set_f_model(chosen):
            self.set_fasttext_at(chosen)
            self.ui_edit_fasttext.setText(chosen)

    def on_menu_open_help(self):
        print('on_menu_open_help', self)
        pass

    def on_menu_open_about(self):
        AboutView(self).exec()

    @staticmethod
    def on_menu_download_model_mini():
        Cmm.open_external_url(URL_M2M_100_418M)

    @staticmethod
    def on_menu_download_model_big():
        Cmm.open_external_url(URL_M2M_100_12B)

    @staticmethod
    def on_menu_download_fasttext_model():
        Cmm.open_external_url(URL_FASTTEXT_MODEL)
