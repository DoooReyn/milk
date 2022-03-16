from enum import Enum, unique


@unique
class UIDef(Enum):
    FileAboutMe = 1
    FileHelp = 2

    ImageSplit = 11
    ImageCompress = 12
    ImageTexturePacker = 13
    ImageTextureUnpacker = 14
    ImageIconGenerator = 15
    ImageSpriteSheet = 16
    ImageSpine = 17
    ImageBMFont = 18

    ConfigI18n = 21
    ConfigXlsx = 22

    ToolsTranslate = 31
    ToolsRename = 32
    ToolsTodos = 33
    ToolsWallpaper = 34
    ToolsAudio = 35
    ToolsVarName = 36
    ToolsPlistMinifier = 37

    LuaGrammarChecker = 41
    LuaEncodingChecker = 42
    LuaCrypto = 43
    LuaMinifier = 44
    LuaGarbage = 45

    DocCocos2dx = 51
    DocCocosCreator = 52
    DocLua = 53
    DocPython = 54
    DocTypeScript = 55
    DocQt = 56
