from enum import Enum, unique


@unique
class UIDef(Enum):
    FileAboutMe = 1
    FileHelp = 2
    FileTest = 99

    ImageSplit = 101
    ImageCompress = 102
    ImageTexturePacker = 103
    ImageTextureUnpacker = 104
    ImageIconGenerator = 105
    ImageSpriteSheet = 106
    ImageSpine = 107
    ImageBMFont = 108
    ImageSpineAtlasExtractor = 109

    ConfigI18n = 201
    ConfigXlsx = 202

    ToolsTranslate = 301
    ToolsRename = 302
    ToolsTodos = 303
    ToolsWallpaper = 304
    ToolsAudio = 305
    ToolsVarName = 306
    ToolsPlistMinifier = 307
    ToolsWeRead = 308

    LuaGrammarChecker = 401
    LuaEncodingChecker = 402
    LuaCrypto = 403
    LuaMinifier = 404
    LuaGarbage = 405

    DocCocos2dx = 501
    DocCocosCreator = 502
    DocLua = 503
    DocPython = 504
    DocTypeScript = 505
    DocQt = 506
