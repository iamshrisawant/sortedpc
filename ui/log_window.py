from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QFrame, QComboBox,
    QCheckBox, QFileDialog
)
from PySide6.QtCore import Signal, Qt
from pathlib import Path
from typing import Dict, List, Any

class LogEntry(QFrame):
    """A log entry showing file sorting information with editable inference."""
    
    inference_changed = Signal(str, str)  # file_id, new_inference
    
    def __init__(self, file_info: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.file_id = str(file_info['id'])
        
        layout = QVBoxLayout(self)
        
        # File info section
        info_layout = QHBoxLayout()
        
        # File name and path
        file_path = Path(file_info['path'])
        name_label = QLabel(f"<b>{file_path.name}</b>")
        path_label = QLabel(f"({file_path.parent})")
        path_label.setStyleSheet("color: gray;")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(path_label)
        info_layout.addStretch()
        
        layout.addLayout(info_layout)
        
        # Inference section
        inference_layout = QHBoxLayout()
        inference_layout.addWidget(QLabel("Inference:"))
        
        # Dropdown with inferences
        self.inference_combo = QComboBox()
        self.inference_combo.setMinimumWidth(200)
        
        # Add current inference first
        current_inference = file_info.get('inference', '')
        self.inference_combo.addItem(current_inference)
        
        # Add other potential inferences
        other_inferences = file_info.get('potential_inferences', [])
        for inf in other_inferences:
            if inf != current_inference:
                self.inference_combo.addItem(inf)
                
        # Add "Browse..." option
        self.inference_combo.addItem("Browse...")
        
        self.inference_combo.currentTextChanged.connect(self._on_inference_changed)
        inference_layout.addWidget(self.inference_combo)
        
        layout.addLayout(inference_layout)
        
        # Reasoning section
        if 'reasoning' in file_info:
            reason_label = QLabel(f"Reasoning: {file_info['reasoning']}")
            reason_label.setWordWrap(True)
            reason_label.setStyleSheet("color: gray; font-style: italic;")
            layout.addWidget(reason_label)
            
    def _on_inference_changed(self, text: str) -> None:
        """Handle inference selection change."""
        if text == "Browse...":
            # Open folder selection dialog
            path = QFileDialog.getExistingDirectory(
                self,
                "Select Destination Folder",
                str(Path.home())
            )
            if path:
                # Add new path to combo box before last item ("Browse...")
                idx = self.inference_combo.count() - 1
                self.inference_combo.insertItem(idx, path)
                self.inference_combo.setCurrentIndex(idx)
                
                # Emit change
                self.inference_changed.emit(self.file_id, path)
        else:
            self.inference_changed.emit(self.file_id, text)

class LogWindow(QMainWindow):
    """Window showing file sorting logs with editable inferences."""
    
    # Signals
    learn_requested = Signal()  # Emitted when manual learning is triggered
    changes_saved = Signal(dict)  # Emitted when changes are saved
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sorting Logs")
        self.setMinimumSize(600, 400)
        
        # Store changes
        self.changed_inferences = {}  # file_id -> new_inference
        
        # Create central widget and layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Create scrollable log area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # Container for log entries
        self.log_container = QWidget()
        self.log_layout = QVBoxLayout(self.log_container)
        self.log_layout.addStretch()
        
        scroll.setWidget(self.log_container)
        layout.addWidget(scroll)
        
        # Controls section
        controls_layout = QHBoxLayout()
        
        # Learning trigger checkbox
        self.learn_check = QCheckBox("Learn after saving")
        controls_layout.addWidget(self.learn_check)
        
        controls_layout.addStretch()
        
        # Save and Cancel buttons
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._on_save)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        
        controls_layout.addWidget(save_btn)
        controls_layout.addWidget(cancel_btn)
        
        layout.addLayout(controls_layout)
        
    def set_logs(self, logs: List[Dict[str, Any]]) -> None:
        """Populate log entries."""
        # Clear existing entries
        while self.log_layout.count() > 1:  # Keep the stretch
            item = self.log_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
                
        # Add new entries
        for log in logs:
            entry = LogEntry(log)
            entry.inference_changed.connect(self._on_inference_changed)
            self.log_layout.insertWidget(self.log_layout.count() - 1, entry)
            
        # Reset changes
        self.changed_inferences.clear()
        
    def _on_inference_changed(self, file_id: str, new_inference: str) -> None:
        """Track inference changes."""
        self.changed_inferences[file_id] = new_inference
        
    def _on_save(self) -> None:
        """Handle save button click."""
        if self.changed_inferences:
            # Emit changes
            self.changes_saved.emit({
                'changes': self.changed_inferences,
                'learn': self.learn_check.isChecked()
            })
            
        self.close()
