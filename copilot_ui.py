import sys
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTextEdit, QLineEdit, QPushButton, 
                           QLabel, QScrollArea, QFrame, QSplitter, QDialog,
                           QComboBox, QFormLayout)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, QSize, pyqtSignal
from PyQt6.QtGui import QPalette, QColor, QFont, QIcon
import random
import queue
import threading
from transcribe import (load_whisper_model, record_audio, transcribe_worker,
                       agent_audio_queue, customer_audio_queue, select_devices)
import numpy as np

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setStyleSheet("""
            QDialog {
                background-color: #1A1A1A;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 13px;
            }
            QComboBox {
                background-color: #2C2C2C;
                color: #FFFFFF;
                border: 1px solid #3C3C3C;
                border-radius: 5px;
                padding: 5px;
                min-width: 150px;
            }
            QComboBox:hover {
                border: 1px solid #4ECDC4;
            }
        """)
        
        layout = QFormLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Language selection
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Hindi", "Spanish", "French", "German"])
        layout.addRow("Language:", self.language_combo)
        
        # Add more settings here as needed

class ObjectionWidget(QFrame):
    def __init__(self, objection, response):
        super().__init__()
        self.setObjectName("objectionWidget")
        self.setStyleSheet("""
            #objectionWidget {
                background-color: #2C2C2C;
                border-radius: 10px;
                margin: 10px;
                padding: 15px;
                min-height: 150px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Objection section
        objection_label = QLabel("🚫 Objection Detected:")
        objection_label.setStyleSheet("color: #FF6B6B; font-weight: bold; font-size: 14px;")
        objection_text = QLabel(objection)
        objection_text.setWordWrap(True)
        objection_text.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                padding: 10px;
                font-size: 13px;
                background-color: #1E1E1E;
                border-radius: 5px;
            }
        """)
        
        layout.addWidget(objection_label)
        layout.addWidget(objection_text)
        
        self.setLayout(layout)

class ResponseWidget(QFrame):
    def __init__(self, response):
        super().__init__()
        self.setObjectName("responseWidget")
        self.setStyleSheet("""
            #responseWidget {
                background-color: #2C2C2C;
                border-radius: 10px;
                margin: 10px;
                padding: 15px;
                min-height: 100px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Response section
        response_label = QLabel("💡 Suggested Response:")
        response_label.setStyleSheet("color: #4ECDC4; font-weight: bold; font-size: 14px;")
        response_text = QLabel(response)
        response_text.setWordWrap(True)
        response_text.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                padding: 10px;
                font-size: 13px;
                background-color: #1E1E1E;
                border-radius: 5px;
            }
        """)
        
        layout.addWidget(response_label)
        layout.addWidget(response_text)
        
        self.setLayout(layout)

class CopilotUI(QMainWindow):
    transcription_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.start_time = time.time()
        self.setupTimers()
        
        # Connect transcription signal
        self.transcription_signal.connect(self.update_transcript)
        
        # TEMPORARY: Demo objections and responses
        self.demo_objections = [
            ("The price is too high", "Emphasize the value proposition and ROI. Break down the cost benefits."),
            ("We're already using a competitor", "Highlight our unique features and ask about their pain points with the current solution."),
            ("I need to think about it", "Create urgency by mentioning limited-time offers or discussing the cost of delay."),
            ("We don't have the budget right now", "Explore flexible payment options and demonstrate how our solution saves money.")
        ]
        
        # Setup demo timer for objections (TEMPORARY)
        self.demo_timer = QTimer()
        self.demo_timer.timeout.connect(self.add_demo_objection)
        self.demo_timer.start(10000)  # Add new objection every 10 seconds
        
        # Start transcription
        self.start_transcription()

    def initUI(self):
        self.setWindowTitle('AI Sales Copilot')
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        
        # Set window size and position (bottom right)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen.width() - 400, screen.height() - 700, 380, 680)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header section
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Logo and title
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        copilot_label = QLabel('🤖 Copilot')
        copilot_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        
        settings_button = QPushButton('⚙️ Settings')
        settings_button.setStyleSheet("""
            QPushButton {
                color: #FFFFFF;
                background: transparent;
                border: none;
                font-size: 16px;
                padding: 5px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 5px;
            }
        """)
        settings_button.clicked.connect(self.show_settings)
        
        close_button = QPushButton('✕')
        close_button.setStyleSheet("""
            QPushButton {
                color: #FFFFFF;
                background: transparent;
                border: none;
                font-size: 16px;
                padding: 5px;
            }
            QPushButton:hover {
                background: rgba(255, 0, 0, 0.2);
                border-radius: 5px;
            }
        """)
        close_button.clicked.connect(self.close)
        
        title_layout.addWidget(copilot_label)
        title_layout.addStretch()
        title_layout.addWidget(settings_button)
        title_layout.addWidget(close_button)
        layout.addWidget(title_container)

        # Status bar
        status_container = QWidget()
        status_container.setObjectName("statusBar")
        status_container.setStyleSheet("""
            #statusBar {
                background-color: #2C2C2C;
                border-radius: 8px;
                margin-top: 5px;
            }
        """)
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(12, 8, 12, 8)
        
        # Live status with dot
        live_container = QWidget()
        live_layout = QHBoxLayout(live_container)
        live_layout.setContentsMargins(0, 0, 0, 0)
        live_layout.setSpacing(5)
        
        live_dot = QLabel('●')
        live_dot.setStyleSheet("""
            QLabel {
                color: #00FF00;
                font-size: 12px;
            }
        """)
        
        live_text = QLabel('Live Call')
        live_text.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 13px;
                font-weight: bold;
            }
        """)
        
        live_layout.addWidget(live_dot)
        live_layout.addWidget(live_text)
        
        # Timer
        self.timer_label = QLabel('00:15:32')
        self.timer_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 13px;
                font-weight: bold;
            }
        """)
        
        status_layout.addWidget(live_container)
        status_layout.addStretch()
        status_layout.addWidget(self.timer_label)
        
        layout.addWidget(status_container)
        
        # Create splitter for transcript and objections
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Transcription section
        transcript_container = QWidget()
        transcript_container.setObjectName("transcriptContainer")
        transcript_container.setStyleSheet("""
            #transcriptContainer {
                background-color: #2C2C2C;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        transcript_layout = QVBoxLayout(transcript_container)
        transcript_layout.setContentsMargins(0, 0, 0, 0)
        
        self.transcript_area = QTextEdit()
        self.transcript_area.setReadOnly(True)
        self.transcript_area.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: none;
                border-radius: 5px;
                font-size: 13px;
                line-height: 1.6;
                padding: 10px;
            }
        """)
        self.transcript_area.setFixedHeight(200)
        
        transcript_layout.addWidget(self.transcript_area)
        splitter.addWidget(transcript_container)
        
        # Objections and Responses section
        objections_container = QWidget()
        objections_container.setObjectName("objectionsContainer")
        objections_container.setStyleSheet("""
            #objectionsContainer {
                background-color: #2C2C2C;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        objections_layout = QVBoxLayout(objections_container)
        objections_layout.setContentsMargins(0, 0, 0, 0)
        
        objections_scroll = QScrollArea()
        objections_scroll.setWidgetResizable(True)
        objections_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.objections_container = QWidget()
        self.objections_layout = QVBoxLayout(self.objections_container)
        self.objections_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        objections_scroll.setWidget(self.objections_container)
        
        objections_layout.addWidget(objections_scroll)
        splitter.addWidget(objections_container)
        
        layout.addWidget(splitter)
        
        # AI Chat section
        chat_container = QWidget()
        chat_container.setObjectName("chatContainer")
        chat_container.setStyleSheet("""
            #chatContainer {
                background-color: #2C2C2C;
                border-radius: 20px;
                margin: 10px 0;
            }
        """)
        chat_layout = QHBoxLayout(chat_container)
        chat_layout.setContentsMargins(15, 8, 8, 8)
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask AI for help...")
        self.chat_input.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                color: #FFFFFF;
                border: none;
                font-size: 13px;
                padding: 5px;
            }
        """)
        
        send_button = QPushButton("➤")
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #4ECDC4;
                color: #FFFFFF;
                border: none;
                border-radius: 15px;
                padding: 8px 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45B7AE;
            }
        """)
        send_button.setFixedSize(30, 30)
        send_button.clicked.connect(self.send_chat)
        
        chat_layout.addWidget(self.chat_input)
        chat_layout.addWidget(send_button)
        layout.addWidget(chat_container)
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1A1A1A;
            }
        """)
        
        # Enable window resizing
        self.setMinimumSize(380, 500)
        self.setMaximumSize(screen.width() - 100, screen.height() - 100)

    def show_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def add_demo_objection(self):
        # TEMPORARY: Add random objection for demo purposes
        objection, response = random.choice(self.demo_objections)
        objection_widget = ObjectionWidget(objection, response)
        response_widget = ResponseWidget(response)
        self.objections_layout.insertWidget(0, objection_widget)
        self.objections_layout.insertWidget(1, response_widget)

    def setupTimers(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateTimer)
        self.timer.start(1000)

    def updateTimer(self):
        elapsed = int(time.time() - self.start_time)
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        self.timer_label.setText(f'{hours:02d}:{minutes:02d}:{seconds:02d}')

    @pyqtSlot()
    def send_chat(self):
        # TODO: Implement actual AI chat functionality
        question = self.chat_input.text()
        if question:
            self.transcript_area.append(f"\nYou: {question}")
            self.chat_input.clear()
            # Mock AI response
            self.transcript_area.append(f"AI: I received your question: {question}")

    def mousePressEvent(self, event):
        self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        delta = event.globalPosition().toPoint() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPosition().toPoint()

    def start_transcription(self):
        # Load the Whisper model
        self.model = load_whisper_model("medium")
        
        # Get device indices
        agent_device_index, customer_device_index = select_devices()
        
        # Start audio recording threads
        self.agent_thread = threading.Thread(target=record_audio, 
                                           args=(agent_device_index, agent_audio_queue, "Agent Microphone"), 
                                           daemon=True)
        
        # Start transcription threads
        self.agent_transcription_thread = threading.Thread(target=self.transcribe_worker_wrapper, 
                                                         args=(agent_audio_queue, "Agent"), 
                                                         daemon=True)
        
        # Start threads
        self.agent_thread.start()
        self.agent_transcription_thread.start()

    def transcribe_worker_wrapper(self, audio_q, speaker_label):
        """Wrapper for transcribe_worker that emits signals to update UI"""
        print(f"\n[{time.strftime('%H:%M:%S')}] Starting transcription for {speaker_label}...")
        while True:
            try:
                print(f"[{time.strftime('%H:%M:%S')}] Waiting for audio chunk...")
                audio_chunk = audio_q.get(timeout=2.0)
                print(f"[{time.strftime('%H:%M:%S')}] Received audio chunk, processing...")
                
                if audio_chunk.ndim > 1:
                    audio_chunk = np.mean(audio_chunk, axis=1)
                audio_chunk = np.array(audio_chunk, dtype=np.float32)
                
                if np.abs(audio_chunk).mean() < 0.005:  # Silence threshold
                    print(f"[{time.strftime('%H:%M:%S')}] Silence detected, skipping...")
                    continue
                
                print(f"[{time.strftime('%H:%M:%S')}] Transcribing audio chunk...")
                result = self.model.transcribe(audio_chunk)
                text = result.get("text", "").strip()
                if text:
                    timestamp = time.strftime("%H:%M:%S")
                    formatted_text = f"[{timestamp}] {speaker_label}: {text}"
                    print(f"\n=== Transcription Result ===\n{formatted_text}\n=========================")
                    self.transcription_signal.emit(formatted_text)
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] No text detected in audio chunk")
            except queue.Empty:
                print(f"[{time.strftime('%H:%M:%S')}] No audio received in the last 2 seconds...")
                continue
            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] Error during {speaker_label} transcription: {e}")

    @pyqtSlot(str)
    def update_transcript(self, text):
        self.transcript_area.append(text)
        # Auto-scroll to bottom
        self.transcript_area.verticalScrollBar().setValue(
            self.transcript_area.verticalScrollBar().maximum()
        )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set dark palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(26, 26, 26))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(40, 40, 40))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(44, 44, 44))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    ex = CopilotUI()
    ex.show()
    sys.exit(app.exec()) 