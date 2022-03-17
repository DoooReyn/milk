Lang = dict({
    "menu_file": "文件",
    "item_file_open_cache": "打开缓存",
    "item_file_clear_cache": "清理缓存",
    "item_file_exit_app": "退出",
    "item_file_about_qt": "关于Qt",
    "item_file_about_me": "关于我",
    "item_file_help": "帮助",

    "menu_image": "图片",
    "item_image_split": "图片分割器",
    "item_image_compress": "图片压缩",
    "item_image_texture_packer": "Plist 合图生成器",
    "item_image_texture_unpacker": "Plist 合图提取器",
    "item_image_icon_generate": "多尺寸icon生成",
    "item_image_bmfont": "BMFont生成工具",
    "item_image_sprite_sheet": "序列帧动画",
    "item_image_spine": "Spine骨骼动画",
    "item_image_spine_atlas_extractor": "Spine Atlas 提取器",

    "menu_config": "配置",
    "item_config_i18n": "多语言配置",
    "item_config_xlsx": "表格配置转换器",

    "menu_tools": "工具",
    "item_tools_translate": "离线翻译",
    "item_tools_rename": "批量重命名",
    "item_tools_todo": "待办事项",
    "item_tools_random_wallpaper": "随机壁纸",
    "item_tools_audio": "音频处理",
    "item_tools_variable_name": "变量取名神器",
    "item_tools_plist_minify": "plist文件压缩",

    "menu_lua": "Lua",
    "item_lua_grammar": "语法检测",
    "item_lua_encoding": "编码检测",
    "item_lua_encrypt": "加密解密",
    "item_lua_compress": "代码压缩",
    "item_lua_garbage": "垃圾代码",

    "menu_doc": "API文档",
    "item_doc_cocos2dx": "Cocos2d-x",
    "item_doc_cocos_creator": "Cocos Creator",
    "item_doc_lua": "Lua",
    "item_doc_python": "Python",
    "item_doc_typescript": "TypeScript",
    "item_doc_qt": "Qt",
})


class LangUI:
    msg_clear_cache_ok = "清理缓存成功！"
    msg_not_implemented = "[ {0} > {1} ] 未实现！"
    msg_invalid_public_key = "无效的 Unsplash 公钥！"
    msg_invalid_private_key = "无效的 Unsplash 密钥！"
    msg_invalid_redirect_ui = "无效的 Unsplash 重定向地址！"
    msg_request_wallpaper_failed = "请求随机壁纸失败！"
    msg_can_not_save_file = "不能保存文件 {0}: {1}."
    msg_download_wallpaper_failed = "下载失败：{0}."
    msg_enabled = "已启用"
    msg_disabled = "已禁用"
    msg_atlas_not_found = "Spine Atlas 文件未找到，请检查目录是否正确"
    msg_all_extracted = "[{0}] 全部提取完成！"
    msg_one_extracted = "[{0}] 提取完成！"

    main_ui_btn_clear = "清空"
    main_ui_lab_log_level = "—————"
    main_ui_btn_trace = "Trace"
    main_ui_btn_debug = "Debug"
    main_ui_btn_info = "Info"
    main_ui_btn_warn = "Warn"
    main_ui_btn_error = "Error"
    main_ui_btn_fatal = "Fatal"

    wallpaper_ui_lab_public_key = "Access Key"
    wallpaper_ui_public_key = "请输入 unsplash 公钥"
    wallpaper_ui_lab_private_key = "Secret Key"
    wallpaper_ui_private_key = "请输入 unsplash 密钥"
    wallpaper_ui_lab_redirect_uri = "Redirect Uri"
    wallpaper_ui_redirect_uri = "请输入 unsplash 重定向地址"
    wallpaper_ui_lab_save = "位置"
    wallpaper_ui_save_at = "请选择壁纸保存目录"
    wallpaper_ui_btn_save = "选择保存目录"
    wallpaper_ui_btn_random = "随机壁纸"
    wallpaper_ui_btn_download = "设为壁纸"
    wallpaper_ui_msg_title = "下载文件"

    atlas_extractor_ui_edit_atlas_dir = "请选择 Spine Atlas 所在目录"
    atlas_extractor_ui_edit_out_dir = "请选择碎图输出目录"
    atlas_extractor_ui_btn_choose = "选择"
    atlas_extractor_ui_btn_parse = "解析"

    texture_unpacker_ui_tip = "请在此处拖入 .png/.plist 文件"
    texture_unpacker_ui_save_dir = "请选择图片保存位置"
    texture_unpacker_parse_fail = "[{0}] 解析 '{1}' 失败！"
    texture_unpacker_ui_btn_save = "保存"
    texture_unpacker_ui_btn_file = "文件"
    texture_unpacker_action_save_all = "保存所有图片"
    texture_unpacker_action_save_one = "保存选中图片"


