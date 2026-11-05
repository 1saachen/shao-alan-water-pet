STYLE = """
QWidget { font-family: 'Microsoft YaHei UI'; font-size: 13px; color: #203a59; }
QMainWindow, QWidget#content, QWidget#page { background: #ffffff; }
QFrame#header { background: #ffffff; border-bottom: 1px solid #e4edf6; }
QLabel { background: transparent; }
QLabel#brand { font-size: 23px; font-weight: 700; color: #1768d5; }
QLabel#title { font-size: 28px; font-weight: 700; color: #203a59; }
QLabel#headline { font-size: 36px; font-weight: 700; color: #203a59; }
QLabel#section { font-size: 16px; font-weight: 700; }
QLabel#muted, QLabel#eyebrow { color: #5e728c; font-size: 12px; }
QLabel#quote { font-size: 17px; color: #355779; }
QLabel#status { color: #1768d5; background: #edf7ff; padding: 6px 12px; border-radius: 12px; font-size: 12px; }
QLabel#metric { font-family: 'Segoe UI'; font-size: 34px; font-weight: 600; color: #1768d5; }
QLabel#timer { font-family: 'Segoe UI'; font-size: 27px; font-weight: 600; color: #203a59; }
QFrame#card { background: #f6faff; border: 1px solid #e2edf8; border-radius: 14px; }
QFrame#rule { background: #e5edf6; border: none; min-height: 1px; max-height: 1px; }
QFrame#schedule { background: #edf7ff; border: none; border-radius: 12px; }
QFrame#quoteBox { background: #edf7ff; border: none; border-radius: 14px; }
QFrame#form { background: #ffffff; border: none; }
QPushButton { border: 1px solid #d2dfef; background: #ffffff; border-radius: 8px; padding: 9px 14px; color: #365477; }
QPushButton:hover { background: #f0f7ff; border-color: #94b9e8; }
QPushButton:pressed { background: #deeeff; }
QPushButton:focus { border: 2px solid #5b99e8; padding: 8px 13px; }
QPushButton#primary { background: #1768d5; color: #ffffff; border: 1px solid #1768d5; font-weight: 700; padding: 11px 20px; }
QPushButton#primary:hover { background: #0f58bb; }
QPushButton#primary:focus { border: 2px solid #83baff; padding: 10px 19px; }
QPushButton#nav { color: #71839a; background: transparent; border: none; border-bottom: 3px solid transparent; border-radius: 0; padding: 19px 18px 16px; }
QPushButton#nav:checked { color: #1768d5; border-bottom: 3px solid #1768d5; font-weight: 700; }
QPushButton#nav:focus { background: #edf7ff; }
QPushButton#subtle { border: none; background: transparent; color: #1768d5; padding: 5px 0; }
QPushButton#subtle:hover { color: #0e4d9e; }
QPushButton:disabled { color: #a3afbd; border-color: #e5ecf4; background: #f8fafc; }
QProgressBar { background: #e5f0fc; border: none; border-radius: 4px; height: 8px; }
QProgressBar::chunk { background: #3c8bea; border-radius: 4px; }
QSpinBox, QTimeEdit, QComboBox { border: 1px solid #d5e1ef; border-radius: 7px; padding: 8px; background: #ffffff; }
QSpinBox:focus, QTimeEdit:focus, QComboBox:focus, QPlainTextEdit:focus { border-color: #4b8fe6; }
QPlainTextEdit { border: 1px solid #d5e1ef; border-radius: 10px; padding: 12px; background: #fbfdff; selection-background-color: #cce5ff; }
QCheckBox { spacing: 10px; padding-top: 4px; padding-bottom: 4px; }
QCheckBox::indicator { width: 17px; height: 17px; border: 1px solid #aabed6; border-radius: 4px; background: #ffffff; }
QCheckBox::indicator:checked { background: #1768d5; border: 3px solid #d6e9ff; }
QCheckBox::indicator:focus { border-color: #1768d5; }
QSlider::groove:horizontal { background: #dfebf8; height: 5px; border-radius: 2px; }
QSlider::sub-page:horizontal { background: #3c8bea; border-radius: 2px; }
QSlider::handle:horizontal { width: 17px; height: 17px; margin: -6px 0; background: #1768d5; border: 2px solid #ffffff; border-radius: 9px; }
QScrollArea { border: none; background: transparent; }
QScrollArea > QWidget > QWidget { background: transparent; }
QScrollBar:vertical { background: transparent; width: 7px; margin: 0; }
QScrollBar::handle:vertical { background: #d1deed; border-radius: 3px; min-height: 24px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QMenu { background: #ffffff; border: 1px solid #d5e1ef; padding: 5px; }
QMenu::item { padding: 7px 18px; }
QMenu::item:selected { background: #edf7ff; color: #1768d5; }
"""
