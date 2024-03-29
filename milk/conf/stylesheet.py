class StyleSheet:
    TextBrowser = "QTextEdit { background-color: #282c34; color: #f8f8f8; }"
    CheckButton = """
        QPushButton { background-color: #e1e1e1; border: none;}
        QPushButton:checked { background-color: #bfdeb3; border: none;}
        QPushButton:hover { background-color: #dec3cb; border: none;}
        """
    HeaderView = """
        QHeaderView::section
        {
        spacing: 10px;
        border: 1px solid #ebebeb;
        margin: 1px;
        }
        QHeaderView::section::title
        {
        font: bold;
        text-align: center;
        }
        """
    TreeView = "QTreeView::item { padding: 4px }"
