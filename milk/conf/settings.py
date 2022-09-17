from PyQt5.QtCore import QSettings, QStandardPaths
from os import path, makedirs
from .res_map import ResMap


class Settings:
    class Names:
        app = "Milk & Bread"
        setting_company = "wu57.cn"
        setting_application = "milk&bread"

    class Sizes:
        ori_width = 960
        ori_height = 640
        min_width = 640
        min_height = 640
        ori_off_x = 0
        ori_off_y = 0

    class UI:
        DefaultFontName = "微软雅黑"
        DefaultFontSize = 12

    class Websocket:
        default_server_addr = "ws://localhost:8000/websocket"

    class Menus:
        class MenuFile:
            Name = "menu_file"
            Actions = (
                {
                    "name": "item_file_open_cache",
                    "icon": ResMap.img_folder_open,
                    "trigger": "on_menu_open_cache"
                },
                {
                    "name": "item_file_clear_cache",
                    "icon": ResMap.img_clear,
                    "trigger": "on_menu_clear_cache"
                },
                {
                    "name": "item_file_about_qt",
                    "icon": ResMap.img_cursor,
                    "trigger": "on_menu_open_about_qt"
                },
                {
                    "name": "item_file_about_me",
                    "icon": ResMap.img_home,
                    "trigger": "on_menu_open_about_me"
                },
                {
                    "name": "item_file_help",
                    "icon": ResMap.img_helpcenter,
                    "trigger": "on_menu_open_help"
                },
                {
                    "name": "item_file_exit_app",
                    "icon": ResMap.img_logout,
                    "trigger": "on_menu_exit_app"
                },
                {
                    "name": "item_file_test_view",
                    "icon": ResMap.img_bug,
                    "trigger": "on_menu_test_view"
                }
            )

        class MenuImage:
            Name = "menu_image"
            Actions = (
                {
                    "name": "item_image_split",
                    "trigger": "on_menu_image_split",
                    "icon": ResMap.img_rectangular_circular_separation
                },
                {
                    "name": "item_image_compress",
                    "trigger": "on_menu_image_compress",
                    "icon": ResMap.img_compression
                },
                {
                    "name": "item_image_texture_packer",
                    "trigger": "on_menu_image_texture_packer",
                    "icon": ResMap.img_merge
                },
                {
                    "name": "item_image_texture_unpacker",
                    "trigger": "on_menu_image_texture_unpacker",
                    "icon": ResMap.img_split_branch
                },
                {
                    "name": "item_image_icon_generate",
                    "trigger": "on_menu_image_icon_generate",
                    "icon": ResMap.img_click_to_fold
                },
                {
                    "name": "item_image_sprite_sheet",
                    "trigger": "on_menu_image_sprite_sheet",
                    "icon": ResMap.img_more_four
                },
                {
                    "name": "item_image_spine",
                    "trigger": "on_menu_image_spine",
                    "icon": ResMap.img_preview_open
                },
                {
                    "name": "item_image_spine_atlas_extractor",
                    "trigger": "on_menu_image_spine_atlas_extractor",
                    "icon": ResMap.img_split_branch
                },
                {
                    "name": "item_image_bmfont",
                    "trigger": "on_menu_image_bmfont",
                    "icon": ResMap.img_add_text_two
                }
            )

        class MenuConfig:
            Name = "menu_config"
            Actions = (
                {
                    "name": "item_config_i18n",
                    "trigger": "on_menu_config_i18n",
                    "icon": ResMap.img_chinese
                },
                {
                    "name": "item_config_xlsx",
                    "trigger": "on_menu_config_xlsx",
                    "icon": ResMap.img_excel_file_excel
                }
            )

        class MenuTools:
            Name = "menu_tools"
            Actions = (
                {
                    "name": "item_tools_translate",
                    "trigger": "on_menu_tools_translate",
                    "icon": ResMap.img_translate
                },
                {
                    "name": "item_tools_rename",
                    "trigger": "on_menu_tools_rename",
                    "icon": ResMap.img_edit
                },
                {
                    "name": "item_tools_todo",
                    "trigger": "on_menu_tools_todo",
                    "icon": ResMap.img_ordered_list
                },
                {
                    "name": "item_tools_random_wallpaper",
                    "trigger": "on_menu_tools_random_wallpaper",
                    "icon": ResMap.img_landscape
                },
                {
                    "name": "item_tools_audio",
                    "trigger": "on_menu_tools_audio",
                    "icon": ResMap.img_audio_file
                },
                {
                    "name": "item_tools_variable_name",
                    "trigger": "on_menu_tools_variable_name",
                    "icon": ResMap.img_tag_one
                },
                {
                    "name": "item_tools_plist_minify",
                    "trigger": "on_menu_tools_plist_minify",
                    "icon": ResMap.img_compression
                },
                {
                    "name": "item_tools_weread",
                    "trigger": "on_menu_tools_weread",
                    "icon": ResMap.img_bookmark_one
                }
            )

        class MenuLua:
            Name = "menu_lua"
            Actions = (
                {
                    "name": "item_lua_grammar",
                    "trigger": "on_menu_lua_grammar",
                    "icon": ResMap.img_bug
                },
                {
                    "name": "item_lua_encoding",
                    "trigger": "on_menu_lua_encoding",
                    "icon": ResMap.img_file_code_one
                },
                {
                    "name": "item_lua_encrypt",
                    "trigger": "on_menu_lua_encrypt",
                    "icon": ResMap.img_file_lock
                },
                {
                    "name": "item_lua_compress",
                    "trigger": "on_menu_lua_compress",
                    "icon": ResMap.img_compression
                },
                {
                    "name": "item_lua_garbage",
                    "trigger": "on_menu_lua_garbage",
                    "icon": ResMap.img_shuffle_one
                },
            )

        class MenuDoc:
            Name = "menu_doc"
            Actions = (
                {
                    "name": "item_doc_cocos2dx",
                    "trigger": "on_menu_doc_cocos2dx",
                    "icon": ResMap.img_api
                },
                {
                    "name": "item_doc_cocos_creator",
                    "trigger": "on_menu_doc_cocos_creator",
                    "icon": ResMap.img_api
                },
                {
                    "name": "item_doc_lua",
                    "trigger": "on_menu_doc_lua",
                    "icon": ResMap.img_api
                },
                {
                    "name": "item_doc_python",
                    "trigger": "on_menu_doc_python",
                    "icon": ResMap.img_api
                },
                {
                    "name": "item_doc_qt",
                    "trigger": "on_menu_doc_qt",
                    "icon": ResMap.img_api
                },
                {
                    "name": "item_doc_html",
                    "trigger": "on_menu_doc_html",
                    "icon": ResMap.img_api
                },
                {
                    "name": "item_doc_css",
                    "trigger": "on_menu_doc_css",
                    "icon": ResMap.img_api
                },
                {
                    "name": "item_doc_canvas",
                    "trigger": "on_menu_doc_canvas",
                    "icon": ResMap.img_api
                },
                {
                    "name": "item_doc_javascript",
                    "trigger": "on_menu_doc_javascript",
                    "icon": ResMap.img_api
                },
                {
                    "name": "item_doc_typescript",
                    "trigger": "on_menu_doc_typescript",
                    "icon": ResMap.img_api
                },
                {
                    "name": "item_doc_go",
                    "trigger": "on_menu_doc_go",
                    "icon": ResMap.img_api
                },
            )

        all = (MenuFile, MenuImage, MenuConfig, MenuTools, MenuLua, MenuDoc)


class UserKey:
    class Wallpaper:
        public_key = "public_key"
        private_key = "private_key"
        redirect_uri = "redirect_uri"
        save_at = "save_at"

    class Main:
        log_trace = "log_trace"
        log_debug = "log_debug"
        log_info = "log_info"
        log_warn = "log_warn"
        log_error = "log_error"
        log_fatal = "log_fatal"

    class SpineAtlasExtractor:
        atlas_locate_dir = "atlas_locate_dir"
        atlas_out_dir = "atlas_out_dir"

    class TextureUnpacker:
        last_save_at = "last_save_at"

    class Translator:
        ctranslate2_model = "ctranslate2_model"
        sentence_piece_model = "sentence_piece_model"
        fasttext_model = "fasttext_model"


local_dir = QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)
app_dir = path.join(local_dir, Settings.Names.app)
makedirs(app_dir, exist_ok=True)
config_path = path.join(app_dir, "config.ini")
settings = QSettings(config_path, QSettings.IniFormat)
