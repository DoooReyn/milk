from os import cpu_count
from os.path import exists, isdir, isfile, join
from typing import Optional

from ctranslate2 import contains_model, Translator
from fasttext import FastText, load_model
from numpy import array, array_split
from sentencepiece import SentencePieceProcessor

from milk.conf import settings, signals, UserKey
from .conf import BeamSize, DETECT_CHARS_LIMIT, SHARED_VOCABULARY_NAME, SupportLanguages, TRANSLATOR_DEVICE
from .paragraph_splitter import paragraph_detokenizer, paragraph_tokenizer
from milk.cmm import MsgBox


class ModelTranslator:
    def __init__(self):
        self.c_model_at: str = ''
        self.s_model_at: str = ''
        self.f_model_at: str = ''
        self.c_translator: Optional[Translator] = None
        self.s_processor: Optional[SentencePieceProcessor] = None
        # noinspection PyProtectedMember
        self.f_prediction: Optional[FastText._FastText] = None
        self.v_m2m_100: bool = False
        self.beam_size: int = BeamSize.Standard
        self.inter_threads = cpu_count()
        self.intra_threads = int(self.inter_threads / 2)

    @staticmethod
    def dump(msg: str):
        MsgBox.msg(msg, '离线翻译')

    def setup(self):
        self.set_c_model(settings.value(UserKey.Translator.ctranslate2_model, '', str))
        self.set_s_model(settings.value(UserKey.Translator.sentence_piece_model, '', str))
        self.set_f_model(settings.value(UserKey.Translator.fasttext_model, '', str))

    def set_c_model(self, model_at: str):
        try:
            if exists(model_at) and isdir(model_at):
                if not exists(join(model_at, 'model.bin')):
                    self.dump('Ctranslate2 模型 model.bin 未找到')
                    return False

                if contains_model(model_at):
                    shared_vocabulary_at = join(model_at, SHARED_VOCABULARY_NAME)
                    if exists(shared_vocabulary_at):
                        with open(shared_vocabulary_at, 'rb') as vb:
                            vb.seek(-300, 2)
                            line = vb.readlines()[-8].decode('utf-8').strip()
                            self.v_m2m_100 = True if 'madeupwordforbt' == line else False
                    else:
                        self.v_m2m_100 = False
                if self.v_m2m_100 is False:
                    self.dump('无效的 M2M-100 模型: {0}'.format(SHARED_VOCABULARY_NAME))
                self.c_translator = Translator(
                    model_at,
                    TRANSLATOR_DEVICE,
                    inter_threads=self.inter_threads,
                    intra_threads=self.intra_threads
                )
                self.c_model_at = model_at
                settings.setValue(UserKey.Translator.ctranslate2_model, model_at)
                return True
            else:
                self.dump('无效的 Ctranslate2 模型: {0}'.format(model_at))
                return False
        except Exception as e:
            self.dump('无效的 Ctranslate2 模型: {0}'.format(model_at))
            self.dump(str(e))
            return False

    def set_s_model(self, model_at: str):
        if exists(model_at) and isfile(model_at):
            self.s_processor = SentencePieceProcessor()
            self.s_processor.Init(model_at)
            self.s_model_at = model_at
            settings.setValue(UserKey.Translator.sentence_piece_model, model_at)
            return True
        else:
            self.dump('无效的 SentencePiece 模型: {0}'.format(model_at))
            return False

    def set_f_model(self, model_at: str):
        if exists(model_at) and isfile(model_at):
            self.f_prediction = load_model(model_at)
            self.f_model_at = model_at
            settings.setValue(UserKey.Translator.fasttext_model, model_at)
            return True
        else:
            self.dump('无效的 Fasttext 模型路径: {0}'.format(model_at))
            return False

    def detect_language(self, text: str):
        if self.f_prediction is None:
            self.dump('FastText 模型未设置')
            return ()

        text = text[:DETECT_CHARS_LIMIT] if len(text) > DETECT_CHARS_LIMIT else text
        text = text.lower().replace("\n", "")
        prediction = model.predict(text, k=2)
        code1 = prediction[0][0][9:]
        code2 = prediction[0][1][9:]
        print('预测：', prediction)
        return code1, code2

    def set_beam_size(self, size: int):
        self.beam_size = size

    def translate(self, source_code: str, target_code: str, text: str):
        if len(text) == 0:
            self.dump('请输入需要翻译的内容')
            return

        if self.s_processor is None:
            self.dump('SentencePiece 模型未设置')
            return

        if self.c_translator is None:
            self.dump('Ctranslate2 模型未设置')
            return

        if self.f_prediction is None:
            self.dump('FastText 模型未设置')
            return

        if target_code not in SupportLanguages:
            self.dump('不支持的目标语言: {}'.format(target_code))
            return

        sentences, breaks = paragraph_tokenizer(text, source_code)
        n_splits = round((len(sentences) / 8) + 0.5)
        splits = array_split(array(sentences), n_splits)
        splits = [split.tolist() for split in splits]
        translations = []
        results = []
        for split in splits:
            tgt_prefix = [[target_code]] * len(split)
            src_prefix = source_code
            start_pos = 6
            max_batch_size = 1024

            sentence_tokens = self.s_processor.Encode(split, out_type=str)
            sentence_tokens = [[src_prefix] + token for token in sentence_tokens]
            translation_tokens = self.c_translator.translate_batch(
                source=sentence_tokens,
                beam_size=self.beam_size,
                max_batch_size=max_batch_size,
                replace_unknowns=True,
                repetition_penalty=1.2,
                target_prefix=tgt_prefix,
            )
            translations_so_far = [
                ' '.join(tokens[0]['tokens']).replace(' ', '').replace('▁', '')[start_pos:].strip()
                for tokens in translation_tokens
            ]
            translations.extend(translations_so_far)
            translations_formatted = paragraph_detokenizer(translations, breaks)
            results.append(translations_formatted)
        return '\n'.join(results)

    def auto_translate(self, target_code: str, text: str):
        source_codes = self.detect_language(text)
        if len(source_codes) > 0:
            source_code = None
            for code in source_codes:
                _code = "__{0}__".format(code)
                if _code in SupportLanguages:
                    source_code = _code
                    break
            return self.translate(source_code, target_code, text)
        return '<b style="color:red;">翻译失败</b>'
