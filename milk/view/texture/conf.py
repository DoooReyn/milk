from conf import ResMap


class UnpackerMenus:
    class MenuFile:
        Name = "menu_file"
        Actions = (
            {
                "name": "texture_unpacker:menu_file:item_file_save_all",
                "icon": ResMap.img_save_one,
                "trigger": "on_save_all",
                "hotkey": "Ctrl+S"

            },
            {
                "name": "texture_unpacker:menu_file:item_file_save_one",
                "icon": ResMap.img_save_one,
                "trigger": "on_save_one",
                "hotkey": "Ctrl+Shift+S"
            },
        )

    all = (MenuFile,)
