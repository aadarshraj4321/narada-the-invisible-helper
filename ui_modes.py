# from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QScrollArea, QPushButton, QListWidget, QSplitter
# from PyQt6.QtCore import Qt

# def create_main_content_layout():
#     """
#     Creates a two-pane layout with a history sidebar and a content display area.
#     """
#     main_widget = QWidget()
#     history_pane = QWidget()
#     history_layout = QVBoxLayout(history_pane)
#     history_layout.setContentsMargins(5, 10, 5, 10)
#     history_title = QLabel("History")
#     history_title.setStyleSheet("color: white; font-size: 18px; font-weight: bold; padding-bottom: 5px;")
    
#     history_list_widget = QListWidget()
#     history_list_widget.setStyleSheet("""
#         QListWidget { background-color: rgba(0, 0, 0, 0.2); border: none; border-radius: 5px; }
#         QListWidget::item { color: white; padding: 8px; }
#         QListWidget::item:selected { background-color: rgba(0, 150, 255, 0.3); }
#         QListWidget::item:hover { background-color: rgba(255, 255, 255, 0.1); }
#     """)
#     history_layout.addWidget(history_title)
#     history_layout.addWidget(history_list_widget)

#     content_pane = QWidget()
#     content_layout = QVBoxLayout(content_pane)
#     content_layout.setContentsMargins(10, 10, 10, 10)
    
#     title_label = QLabel("...")
#     title_label.setWordWrap(True)
#     title_label.setStyleSheet("color: #d1d1d1; font-size: 16px; font-weight: bold; border-bottom: 1px solid rgba(255, 255, 255, 0.2); padding: 5px; margin-bottom: 5px;")

#     body_scroll_area = QScrollArea()
#     body_scroll_area.setWidgetResizable(True)
#     body_scroll_area.setStyleSheet("""
#         QScrollArea { background: transparent; border: none; }
#         QScrollBar:vertical { background: transparent; width: 8px; }
#         QScrollBar::handle:vertical { background: rgba(255, 255, 255, 0.5); border-radius: 4px; }
#     """)
    
#     body_label = QLabel("...")
#     body_label.setWordWrap(True)
#     body_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
#     body_label.setStyleSheet("color: white; font-size: 15px; background: transparent; padding: 10px;")
#     body_scroll_area.setWidget(body_label)

#     dismiss_button = QPushButton("Dismiss")
#     dismiss_button.setStyleSheet("padding: 5px;")

#     content_layout.addWidget(title_label)
#     content_layout.addWidget(body_scroll_area)
#     content_layout.addWidget(dismiss_button, alignment=Qt.AlignmentFlag.AlignRight)

#     splitter = QSplitter(Qt.Orientation.Horizontal)
#     splitter.addWidget(history_pane)
#     splitter.addWidget(content_pane)
#     splitter.setSizes([150, 400])
#     splitter.setStyleSheet("QSplitter::handle { background-color: rgba(255, 255, 255, 0.2); }")

#     main_layout = QVBoxLayout(main_widget)
#     main_layout.setContentsMargins(0, 0, 0, 0)
#     main_layout.addWidget(splitter)
    
#     return main_widget, history_list_widget, title_label, body_label, dismiss_button
















from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QScrollArea, QPushButton, QListWidget, QSplitter, QHBoxLayout
from PyQt6.QtCore import Qt

def create_main_content_layout():
    """
    Creates a two-pane layout with a history sidebar and a content display area.
    """
    main_widget = QWidget()
    history_pane = QWidget()
    history_layout = QVBoxLayout(history_pane)
    history_layout.setContentsMargins(5, 10, 5, 10)
    history_title = QLabel("History")
    history_title.setStyleSheet("color: white; font-size: 18px; font-weight: bold; padding-bottom: 5px;")
    
    history_list_widget = QListWidget()
    history_list_widget.setStyleSheet("""
        QListWidget { background-color: rgba(0, 0, 0, 0.2); border: none; border-radius: 5px; }
        QListWidget::item { color: white; padding: 8px; }
        QListWidget::item:selected { background-color: rgba(0, 150, 255, 0.3); }
        QListWidget::item:hover { background-color: rgba(255, 255, 255, 0.1); }
    """)
    history_layout.addWidget(history_title)
    history_layout.addWidget(history_list_widget)

    content_pane = QWidget()
    content_layout = QVBoxLayout(content_pane)
    content_layout.setContentsMargins(10, 10, 10, 10)
    
    title_label = QLabel("...")
    title_label.setWordWrap(True)
    title_label.setStyleSheet("color: #d1d1d1; font-size: 16px; font-weight: bold; border-bottom: 1px solid rgba(255, 255, 255, 0.2); padding: 5px; margin-bottom: 5px;")

    body_scroll_area = QScrollArea()
    body_scroll_area.setWidgetResizable(True)
    body_scroll_area.setStyleSheet("""
        QScrollArea { background: transparent; border: none; }
        QScrollBar:vertical { background: transparent; width: 8px; }
        QScrollBar::handle:vertical { background: rgba(255, 255, 255, 0.5); border-radius: 4px; }
    """)
    
    body_label = QLabel("...")
    body_label.setWordWrap(True)
    body_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    body_label.setStyleSheet("color: white; font-size: 15px; background: transparent; padding: 10px;")
    body_scroll_area.setWidget(body_label)

    dismiss_button = QPushButton("Dismiss")
    dismiss_button.setStyleSheet("padding: 5px;")

    content_layout.addWidget(title_label)
    content_layout.addWidget(body_scroll_area)
    content_layout.addWidget(dismiss_button, alignment=Qt.AlignmentFlag.AlignRight)

    splitter = QSplitter(Qt.Orientation.Horizontal)
    splitter.addWidget(history_pane)
    splitter.addWidget(content_pane)
    splitter.setSizes([150, 400])
    splitter.setStyleSheet("QSplitter::handle { background-color: rgba(255, 255, 255, 0.2); }")

    main_layout = QVBoxLayout(main_widget)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.addWidget(splitter)
    
    return main_widget, history_list_widget, title_label, body_label, dismiss_button

def create_stealth_mode():
    """Creates the widget for the ultra-minimalist 'teleprompter' mode."""
    widget = QWidget()
    
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(10, 5, 10, 5)

    label = QLabel("...", widget)
    label.setWordWrap(False)
    label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
    label.setStyleSheet("""
        color: #E0E0E0;
        font-size: 14px;
        font-weight: normal;
        background-color: transparent;
        padding: 5px;
    """)
    
    dismiss_button = QPushButton("✕")
    dismiss_button.setFixedSize(20, 20)
    dismiss_button.setStyleSheet("""
        QPushButton { 
            background-color: transparent; 
            color: #E0E0E0; 
            border: none; 
            font-size: 16px;
            font-weight: bold;
        }
        QPushButton:hover { background-color: rgba(255, 0, 0, 0.5); border-radius: 10px; }
    """)

    layout.addWidget(label)
    layout.addStretch()
    layout.addWidget(dismiss_button)
    
    return widget, label, dismiss_button