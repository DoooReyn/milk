from os import cpu_count
from os.path import exists, isdir, isfile, join
from typing import Optional

from ctranslate2 import contains_model, Translator
from fasttext import FastText, load_model
from indicnlp.tokenize.sentence_tokenize import sentence_split
from numpy import array, array_split
from pysbd import Segmenter
from sentence_splitter import split_text_into_sentences
from sentencepiece import SentencePieceProcessor

from milk.conf import LangUI
from milk.gui import GUI
from .conf import BeamSize, DETECT_CHARS_LIMIT, SHARED_VOCABULARY_NAME, SupportLanguages, TRANSLATOR_DEVICE


def paragraph_tokenizer(text, language="en"):
    """Replace sentences with their indexes, and store indexes of newlines
    Args:
        text (str): Text to be indexed
        language (str): Language to be indexed

    Returns:
        sentences (list): List of sentences
        breaks (list): List of indexes of sentences and newlines
    """

    languages_splitter = ["ca", "cs", "da", "de", "el", "en", "es", "fi", "fr", "hu", "is", "it",
                          "lt", "lv", "nl", "no", "pl", "pt", "ro", "ru", "sk", "sl", "sv", "tr"]
    languages_indic = ["as", "bn", "gu", "hi", "kK", "kn", "ml", "mr", "ne", "or", "pa", "sa",
                       "sd", "si", "ta", "te"]
    languages_pysbd = ["en", "hi", "mr", "zh", "es", "am", "ar", "hy", "bg", "ur", "ru", "pl",
                       "fa", "nl", "da", "fr", "my", "el", "it", "ja", "de", "kk", "sk"]

    languages = languages_splitter + languages_indic + languages_pysbd
    language = language if language in languages else "en"

    text = text.strip()
    paragraphs = text.splitlines(True)

    breaks = []
    sentences = []

    for paragraph in paragraphs:
        if paragraph == "\n":
            breaks.append("\n")
        else:
            paragraph_sentences = []
            if language in languages_pysbd:
                segmenter = Segmenter(language=language, clean=True)
                paragraph_sentences = segmenter.segment(paragraph)
            elif language in languages_splitter:
                paragraph_sentences = split_text_into_sentences(paragraph, language)
            elif language in languages_indic:
                paragraph_sentences = sentence_split(paragraph, language)

            breaks.extend(
                list(range(len(sentences), len(sentences) + len(paragraph_sentences)))
            )
            breaks.append("\n")
            sentences.extend(paragraph_sentences)

    # Remove the last newline
    breaks = breaks[:-1]

    return sentences, breaks


def paragraph_detokenizer(sentences: list[str], breaks):
    """Restore original paragraph format from indexes of sentences and newlines

    Args:
        sentences (list): List of sentences
        breaks (list): List of indexes of sentences and newlines

    Returns:
        text (str): Text with original format
    """
    output = []

    for br in breaks:
        if br == "\n":
            output.append("\n")
        else:
            output.append(sentences[br] + " ")

    text = "".join(output)
    return text


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
        GUI.MsgBox.msg(msg, LangUI.translate_title)

    def set_c_model(self, model_at: str):
        try:
            if exists(model_at) and isdir(model_at):
                if not exists(join(model_at, 'model.bin')):
                    self.dump(LangUI.translate_ctranslate2_not_found)
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
                    self.dump(LangUI.translate_vocabulary_not_found.format(SHARED_VOCABULARY_NAME))
                self.c_translator = Translator(
                    model_at,
                    TRANSLATOR_DEVICE,
                    inter_threads=self.inter_threads,
                    intra_threads=self.intra_threads
                )
                self.c_model_at = model_at
                return True
            else:
                self.dump(LangUI.translate_invalid_ctranslate2.format(model_at))
                return False
        except Exception as e:
            self.dump(LangUI.translate_invalid_ctranslate2.format(model_at))
            self.dump(str(e))
            return False

    def set_s_model(self, model_at: str):
        if exists(model_at) and isfile(model_at):
            self.s_processor = SentencePieceProcessor()
            self.s_processor.Init(model_at)
            self.s_model_at = model_at
            return True
        else:
            self.dump(LangUI.translate_invalid_sentence_piece.format(model_at))
            return False

    def set_f_model(self, model_at: str):
        if exists(model_at) and isfile(model_at):
            self.f_prediction = load_model(model_at)
            self.f_model_at = model_at
            return True
        else:
            self.dump(LangUI.translate_invalid_fasttext.format(model_at))
            return False

    def detect_language(self, text: str):
        if self.f_prediction is None:
            self.dump(LangUI.translate_unset_of_fasttext)
            return ()

        text = text[:DETECT_CHARS_LIMIT] if len(text) > DETECT_CHARS_LIMIT else text
        text = text.lower().replace("\n", "")
        prediction = self.f_prediction.predict(text, k=2)
        code1 = prediction[0][0][9:]
        code2 = prediction[0][1][9:]
        # print('预测：', prediction)
        return code1, code2

    def set_beam_size(self, size: int):
        self.beam_size = size

    def translate(self, source_code: str, target_code: str, text: str):
        if len(text) == 0:
            self.dump(LangUI.translate_input_content)
            return

        if self.s_processor is None:
            self.dump(LangUI.translate_unset_of_sentence_piece)
            return

        if self.c_translator is None:
            self.dump(LangUI.translate_unset_of_ctranslate2)
            return

        if self.f_prediction is None:
            self.dump(LangUI.translate_unset_of_fasttext)
            return

        if target_code not in SupportLanguages:
            self.dump(LangUI.translate_unsupported_language.format(target_code))
            return

        sentences, breaks = paragraph_tokenizer(text, source_code)
        n_splits = round((len(sentences) / 8) + 0.5)
        splits = array_split(array(sentences), n_splits)
        splits = [split.tolist() for split in splits]
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
                ' '.join(tokens[0]['tokens']).replace(' ', '').replace('▁', ' ')[start_pos:].strip()
                for tokens in translation_tokens
            ]
            # [print(tokens) for tokens in translation_tokens]
            translations_formatted = paragraph_detokenizer(translations_so_far, breaks)
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
        return LangUI.translate_convert_failed
