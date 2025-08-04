from PySide6.QtWidgets import (
    QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QFrame)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from application.Styling.general_style_elements import GeneralStyleElements


class WorkflowButton(QPushButton):
    """
    Custom button widget for the home page that handles hovering effects
    and emits a signal when clicked.

    This button is used to select between multiple available workflows.
    """

    def __init__(self, icon: str, title: str, description: str = "",
                 parent=None):
        super().__init__(parent)

        self.style_class = GeneralStyleElements()

        self.setup_local_ui_elements(icon, title, description)

    def setup_local_ui_elements(self, icon: str, title: str,
                                description: str = ""):
        """Set up the button appearance and behavior"""

        # Allow button to grow/shrink with layout
        self.setSizePolicy(QSizePolicy.MinimumExpanding,
                           QSizePolicy.MinimumExpanding)

        # Container frame inside button
        frame_workflow_container = QFrame(self)
        frame_workflow_container.setObjectName("frame_workflow_container")
        frame_workflow_container.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Preferred)

        # The next line makes the container frame transparent to mouse events.
        #
        # Without this attribute, the QFrame would intercept mouse events
        # (e.g., hover), preventing the parent QPushButton from receiving them.
        # This breaks hover styles like QPushButton:hover. By enabling
        # WA_TransparentForMouseEvents, the frame lets all mouse events pass
        # through to its parent, preserving proper interaction behavior.
        frame_workflow_container.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        container_layout = QVBoxLayout(frame_workflow_container)
        container_layout.setContentsMargins(40, 40, 40, 40)
        container_layout.setSpacing(0)

        frame_workflow_layout = QFrame(frame_workflow_container)
        frame_workflow_layout.setObjectName("frame_workflow_layout")
        frame_workflow_layout.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Preferred)

        content_layout = QHBoxLayout(frame_workflow_layout)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)
        content_layout.setAlignment(Qt.AlignLeft)

        # Icon
        icon_label = QLabel()
        pixmap = QPixmap(icon)
        pixmap = QPixmap(icon).scaled(
            140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Title + Description
        text_frame = QFrame()
        text_layout = QVBoxLayout(text_frame)
        text_layout.setContentsMargins(0, 15, 40, 0)
        text_layout.setSpacing(15)
        text_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.title_label = QLabel(title)
        self.title_label.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.style_class.add_property_to_widget(
            self.title_label, property="type", value="button-primary")

        description_label = QLabel(description)
        description_label.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.style_class.add_property_to_widget(
            description_label, property="type", value="button-secondary")

        text_layout.addWidget(self.title_label)
        text_layout.addWidget(description_label)

        content_layout.addWidget(icon_label)
        content_layout.addWidget(text_frame)
        frame_workflow_layout.setLayout(content_layout)

        

        container_layout.addWidget(frame_workflow_layout)
        frame_workflow_container.setLayout(container_layout)

        # Apply final layout
        button_layout = QVBoxLayout(self)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addWidget(frame_workflow_container)

        self.setLayout(button_layout)

    def connect_signals_to_actions(self):
        """Connect signals to actions"""
        
        pass

    def disconnect_signals_from_actions(self):
        """Disconnect signals from actions"""
        pass

    def connect_widgets_to_actions(self):
        """Connect widgets to actions"""
        pass

    def close_widget(self):
        """Disconnect all signals upon deleting of this widget"""
        self.disconnect_signals_from_actions()

    def sizeHint(self):
        """
        Returns the recommended size for this widget based on its internal
        layout.

        This ensures that the widget resizes appropriately according to
        the sizeHint of its child layout, instead of using a default fixed
        size.

        Returns:
            QSize: The recommended size for the widget.
        """
        return self.layout().sizeHint()

    def enterEvent(self, event):
        """
        Handles the mouse enter event.

        Called automatically when the mouse cursor enters the widget's area.
        Commonly used to trigger hover effects, visual feedback, or style
        changes.

        Args:
            event (QEvent): The event object containing context about the
            enter event.
        """
        super().enterEvent(event)
        self.style_class.add_property_to_widget(
            self.title_label, property="class", value="hover")

    def leaveEvent(self, event):
        """
        Handles the mouse leave event.

        Called automatically when the mouse cursor leaves the widget's area.
        Often used to undo hover effects or restore the widget's default state.

        Args:
            event (QEvent): The event object containing context about the
            leave event.
        """
        super().leaveEvent(event)
        self.style_class.add_property_to_widget(
            self.title_label, property="class", value=None)
