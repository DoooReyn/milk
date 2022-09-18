from milk.conf import LangUI, ResMap

Languages = {
    "Afrikaans": "__af__",
    "Amharic": "__am__",
    "Arabic": "__ar__",
    "Asturian": "__ast__",
    "Azerbaijani": "__az__",
    "Bashkir": "__ba__",
    "Belarusian": "__be__",
    "Bulgarian": "__bg__",
    "Bengali": "__bn__",
    "Breton": "__br__",
    "Bosnian": "__bs__",
    "Catalan": "__ca__",
    "Cebuano": "__ceb__",
    "Czech": "__cs__",
    "Welsh": "__cy__",
    "Danish": "__da__",
    "German": "__de__",
    "Greek": "__el__",
    "English": "__en__",
    "Spanish": "__es__",
    "Estonian": "__et__",
    "Persian": "__fa__",
    "Fulah": "__ff__",
    "Finnish": "__fi__",
    "French": "__fr__",
    "Western Frisian": "__fy__",
    "Irish": "__ga__",
    "Gaelic": "__gd__",
    "Galician": "__gl__",
    "Gujarati": "__gu__",
    "Hausa": "__ha__",
    "Hebrew": "__he__",
    "Hindi": "__hi__",
    "Croatian": "__hr__",
    "Haitian": "__ht__",
    "Hungarian": "__hu__",
    "Armenian": "__hy__",
    "Indonesian": "__id__",
    "Igbo": "__ig__",
    "Iloko": "__ilo__",
    "Icelandic": "__is__",
    "Italian": "__it__",
    "Japanese": "__ja__",
    "Javanese": "__jv__",
    "Georgian": "__ka__",
    "Kazakh": "__kk__",
    "Central Khmer": "__km__",
    "Kannada": "__kn__",
    "Korean": "__ko__",
    "Luxembourgish": "__lb__",
    "Ganda": "__lg__",
    "Lingala": "__ln__",
    "Lao": "__lo__",
    "Lithuanian": "__lt__",
    "Latvian": "__lv__",
    "Malagasy": "__mg__",
    "Macedonian": "__mk__",
    "Malayalam": "__ml__",
    "Mongolian": "__mn__",
    "Marathi": "__mr__",
    "Malay": "__ms__",
    "Burmese": "__my__",
    "Nepali": "__ne__",
    "Dutch": "__nl__",
    "Norwegian": "__no__",
    "Northern Sotho": "__ns__",
    "Occitan (post 1500)": "__oc__",
    "Oriya": "__or__",
    "Panjabi": "__pa__",
    "Polish": "__pl__",
    "Pushto": "__ps__",
    "Portuguese": "__pt__",
    "Romanian": "__ro__",
    "Russian": "__ru__",
    "Sindhi": "__sd__",
    "Sinhala": "__si__",
    "Slovak": "__sk__",
    "Slovenian": "__sl__",
    "Somali": "__so__",
    "Albanian": "__sq__",
    "Serbian": "__sr__",
    "Swati": "__ss__",
    "Sundanese": "__su__",
    "Swedish": "__sv__",
    "Swahili": "__sw__",
    "Tamil": "__ta__",
    "Thai": "__th__",
    "Tagalog": "__tl__",
    "Tswana": "__tn__",
    "Turkish": "__tr__",
    "Ukrainian": "__uk__",
    "Urdu": "__ur__",
    "Uzbek": "__uz__",
    "Vietnamese": "__vi__",
    "Wolof": "__wo__",
    "Xhosa": "__xh__",
    "Yiddish": "__yi__",
    "Yoruba": "__yo__",
    "Chinese": "__zh__",
    "Zulu": "__zu__"
}

SupportLanguages = (
    Languages.get('English'),
    Languages.get('Chinese'),
    Languages.get('Japanese'),
    Languages.get('Korean')
)


class TranslateMenus:
    class MenuFile:
        Name = "translate:menu_file"
        Actions = (
            {
                "name": "translate:menu_file:item_download_model_mini",
                "icon": ResMap.img_arrow_down,
                "trigger": "on_menu_download_model_mini"
            },
            {
                "name": "translate:menu_file:item_download_model_big",
                "icon": ResMap.img_arrow_down,
                "trigger": "on_menu_download_model_big"
            },
            {
                "name": "translate:menu_file:item_download_fasttext_model",
                "icon": ResMap.img_arrow_down,
                "trigger": "on_menu_download_fasttext_model"
            },
            {
                "name": "translate:menu_help:item_about",
                "icon": ResMap.img_home,
                "trigger": "on_menu_open_about"
            },
        )

    all = (MenuFile,)


class BeamSize:
    Standard = 2
    Great = 3
    Excellent = 5


SHARED_VOCABULARY_NAME = 'shared_vocabulary.txt'

TRANSLATOR_DEVICE = 'cpu'

DETECT_CHARS_LIMIT = 100

URL_M2M_100_418M = 'https://pretrained-nmt-models.s3.us-west-2.amazonaws.com/CTranslate2/m2m100/m2m100_ct2_418m.zip'

URL_M2M_100_12B = 'https://pretrained-nmt-models.s3.us-west-2.amazonaws.com/CTranslate2/m2m100/m2m100_ct2_12b.zip'

URL_FASTTEXT_MODEL = 'https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz'

TRANSLATE_LANGUAGE_ITEMS = (
    LangUI.translate_lang_en,
    LangUI.translate_lang_zh,
    LangUI.translate_lang_ja,
    LangUI.translate_lang_kr,
)

TRANSLATE_BEAM_SIZES = (
    LangUI.translate_quality_3,
    LangUI.translate_quality_2,
    LangUI.translate_quality_1,
)

TRANSLATE_BEAM_IDS = (
    BeamSize.Excellent,
    BeamSize.Great,
    BeamSize.Standard,
)

TRANSLATE_BEAM_DEFAULT_ID = BeamSize.Excellent
