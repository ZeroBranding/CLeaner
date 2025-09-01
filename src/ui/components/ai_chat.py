"""
🤖 AI Chat Widget
Multi-provider AI chat interface with intelligent load balancing
"""

import asyncio
import time
from typing import Dict, List, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, 
    QPushButton, QComboBox, QLabel, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QObject
from PyQt6.QtGui import QFont, QTextCursor, QColor, QTextCharFormat
import logging

logger = logging.getLogger(__name__)

class AIWorker(QObject):
    """Worker thread for AI operations"""
    
    response_ready = pyqtSignal(object)  # AIResponse object
    error_occurred = pyqtSignal(str)
    
    def __init__(self, ai_manager):
        super().__init__()
        self.ai_manager = ai_manager
    
    async def generate_response(self, prompt: str, provider: str = None, priority: str = "balanced"):
        """Generate AI response in worker thread"""
        try:
            from ...ai.ai_manager import AIProvider
            
            # Convert string provider to enum
            provider_enum = None
            if provider and provider != "Auto Select":
                provider_map = {
                    "Llama3-8B (Local)": AIProvider.OLLAMA_LOCAL,
                    "Google Gemini 1.5": AIProvider.GEMINI,
                    "Deepseek 3.1": AIProvider.DEEPSEEK,
                    "Groq (Free)": AIProvider.GROQ
                }
                provider_enum = provider_map.get(provider)
            
            response = await self.ai_manager.generate_response(
                prompt, provider_enum, priority=priority
            )
            self.response_ready.emit(response)
            
        except Exception as e:
            logger.error(f"AI worker error: {e}")
            self.error_occurred.emit(str(e))

class ChatMessage(QFrame):
    """Individual chat message with styling"""
    
    def __init__(self, content: str, is_user: bool, provider: str = None, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.provider = provider
        self._setup_ui(content)
    
    def _setup_ui(self, content: str):
        """Setup message UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        
        # Message header
        if not self.is_user and self.provider:
            header = QLabel(f"🤖 {self.provider}")
            header.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            header.setStyleSheet("color: #00ffff; margin-bottom: 5px;")
            layout.addWidget(header)
        elif self.is_user:
            header = QLabel("👤 You")
            header.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            header.setStyleSheet("color: #ff00ff; margin-bottom: 5px;")
            layout.addWidget(header)
        
        # Message content
        content_label = QLabel(content)
        content_label.setWordWrap(True)
        content_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        content_label.setStyleSheet("color: white; line-height: 1.4; font-size: 11px;")
        layout.addWidget(content_label)
        
        # Message styling
        if self.is_user:
            self.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(255, 0, 255, 0.2),
                        stop:1 rgba(255, 100, 255, 0.1));
                    border: 1px solid rgba(255, 0, 255, 0.3);
                    border-radius: 10px;
                    margin: 5px 50px 5px 5px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(0, 255, 255, 0.2),
                        stop:1 rgba(100, 255, 255, 0.1));
                    border: 1px solid rgba(0, 255, 255, 0.3);
                    border-radius: 10px;
                    margin: 5px 5px 5px 50px;
                }
            """)

class AIChatWidget(QWidget):
    """AI chat interface with multi-provider support"""
    
    def __init__(self, ai_manager, parent=None):
        super().__init__(parent)
        self.ai_manager = ai_manager
        self.conversation_history: List[Dict] = []
        
        # Worker thread for AI operations
        self.ai_thread = QThread()
        self.ai_worker = AIWorker(ai_manager)
        self.ai_worker.moveToThread(self.ai_thread)
        self.ai_worker.response_ready.connect(self._on_ai_response)
        self.ai_worker.error_occurred.connect(self._on_ai_error)
        self.ai_thread.start()
        
        self._setup_ui()
        
        logger.info("AI chat widget initialized")
    
    def _setup_ui(self):
        """Setup chat interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Chat header
        header_layout = QHBoxLayout()
        
        title = QLabel("🤖 AI Assistant")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #00ffff;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Provider selection
        provider_label = QLabel("Provider:")
        provider_label.setStyleSheet("color: white;")
        self.provider_combo = QComboBox()
        self.provider_combo.addItems([
            "Auto Select",
            "Llama3-8B (Local)",
            "Google Gemini 1.5",
            "Deepseek 3.1",
            "Groq (Free)"
        ])
        
        header_layout.addWidget(provider_label)
        header_layout.addWidget(self.provider_combo)
        
        layout.addLayout(header_layout)
        
        # Chat area
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarNever)
        self.chat_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.chat_content = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_content)
        self.chat_layout.addStretch()
        
        self.chat_scroll.setWidget(self.chat_content)
        self.chat_scroll.setStyleSheet("""
            QScrollArea {
                background: rgba(15, 15, 25, 0.9);
                border: 1px solid rgba(0, 255, 255, 0.3);
                border-radius: 8px;
            }
        """)
        
        layout.addWidget(self.chat_scroll)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Ask the AI assistant anything...")
        self.message_input.returnPressed.connect(self._send_message)
        self.message_input.setStyleSheet("""
            QLineEdit {
                background: rgba(25, 25, 35, 0.9);
                border: 2px solid rgba(0, 255, 255, 0.3);
                border-radius: 8px;
                padding: 10px;
                color: white;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid rgba(0, 255, 255, 0.8);
            }
        """)
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self._send_message)
        self.send_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(0, 255, 255, 0.3),
                    stop:1 rgba(255, 0, 255, 0.3));
                border: 2px solid rgba(0, 255, 255, 0.8);
                border-radius: 8px;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(0, 255, 255, 0.5),
                    stop:1 rgba(255, 0, 255, 0.5));
            }
        """)
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        # Add welcome message
        self._add_welcome_message()
    
    def _add_welcome_message(self):
        """Add welcome message to chat"""
        welcome_text = """🌟 Welcome to the Holographic AI Assistant!

I'm powered by multiple AI providers including:
• 🏠 Llama3-8B (Local) - Fast and private
• 🌐 Google Gemini 1.5 - High quality responses  
• ⚡ Groq API - Ultra-fast inference
• 🧠 Deepseek 3.1 - Advanced reasoning

Ask me anything about your system, coding, or general questions!"""
        
        welcome_msg = ChatMessage(welcome_text, is_user=False, provider="System")
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, welcome_msg)
        self._scroll_to_bottom()
    
    def _send_message(self):
        """Send message to AI"""
        message = self.message_input.text().strip()
        if not message:
            return
        
        # Add user message to chat
        user_msg = ChatMessage(message, is_user=True)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, user_msg)
        
        # Clear input
        self.message_input.clear()
        
        # Disable input while processing
        self.message_input.setEnabled(False)
        self.send_button.setEnabled(False)
        self.send_button.setText("Thinking...")
        
        # Add typing indicator
        typing_msg = ChatMessage("🤔 AI is thinking...", is_user=False, provider="System")
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, typing_msg)
        self.typing_indicator = typing_msg
        
        self._scroll_to_bottom()
        
        # Generate response asynchronously
        selected_provider = self.provider_combo.currentText()
        asyncio.run_coroutine_threadsafe(
            self.ai_worker.generate_response(message, selected_provider),
            asyncio.new_event_loop()
        )
    
    def _on_ai_response(self, response):
        """Handle AI response"""
        try:
            # Remove typing indicator
            if hasattr(self, 'typing_indicator'):
                self.typing_indicator.setParent(None)
                delattr(self, 'typing_indicator')
            
            # Add AI response
            if response.success:
                ai_msg = ChatMessage(
                    response.content, 
                    is_user=False, 
                    provider=f"{response.provider.value} ({response.response_time:.1f}s)"
                )
                self.chat_layout.insertWidget(self.chat_layout.count() - 1, ai_msg)
                
                # Store in conversation history
                self.conversation_history.append({
                    'user_message': self.conversation_history[-1]['user_message'] if self.conversation_history else "",
                    'ai_response': response.content,
                    'provider': response.provider.value,
                    'timestamp': time.time(),
                    'tokens_used': response.tokens_used,
                    'response_time': response.response_time
                })
                
            else:
                error_msg = ChatMessage(
                    f"❌ Error: {response.error}", 
                    is_user=False, 
                    provider="Error"
                )
                self.chat_layout.insertWidget(self.chat_layout.count() - 1, error_msg)
            
            # Re-enable input
            self.message_input.setEnabled(True)
            self.send_button.setEnabled(True)
            self.send_button.setText("Send")
            
            self._scroll_to_bottom()
            
        except Exception as e:
            logger.error(f"Failed to handle AI response: {e}")
            self._on_ai_error(str(e))
    
    def _on_ai_error(self, error: str):
        """Handle AI error"""
        # Remove typing indicator
        if hasattr(self, 'typing_indicator'):
            self.typing_indicator.setParent(None)
            delattr(self, 'typing_indicator')
        
        # Add error message
        error_msg = ChatMessage(f"❌ Error: {error}", is_user=False, provider="Error")
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, error_msg)
        
        # Re-enable input
        self.message_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.send_button.setText("Send")
        
        self._scroll_to_bottom()
    
    def _scroll_to_bottom(self):
        """Scroll chat to bottom"""
        QTimer.singleShot(100, lambda: self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()
        ))
    
    def clear_chat(self):
        """Clear chat history"""
        # Remove all messages except welcome
        for i in reversed(range(self.chat_layout.count() - 1)):
            item = self.chat_layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)
        
        # Add welcome message back
        self._add_welcome_message()
        
        # Clear conversation history
        self.conversation_history.clear()
    
    def export_conversation(self) -> str:
        """Export conversation as text"""
        export_text = "# AI Conversation Export\n\n"
        
        for msg in self.conversation_history:
            export_text += f"**User:** {msg.get('user_message', '')}\n\n"
            export_text += f"**AI ({msg.get('provider', 'Unknown')}):** {msg.get('ai_response', '')}\n\n"
            export_text += f"*Response time: {msg.get('response_time', 0):.1f}s, Tokens: {msg.get('tokens_used', 0)}*\n\n"
            export_text += "---\n\n"
        
        return export_text
    
    def get_conversation_stats(self) -> Dict[str, any]:
        """Get conversation statistics"""
        if not self.conversation_history:
            return {}
        
        total_messages = len(self.conversation_history)
        total_tokens = sum(msg.get('tokens_used', 0) for msg in self.conversation_history)
        avg_response_time = sum(msg.get('response_time', 0) for msg in self.conversation_history) / total_messages
        
        # Provider usage
        provider_usage = {}
        for msg in self.conversation_history:
            provider = msg.get('provider', 'Unknown')
            provider_usage[provider] = provider_usage.get(provider, 0) + 1
        
        return {
            'total_messages': total_messages,
            'total_tokens': total_tokens,
            'avg_response_time': avg_response_time,
            'provider_usage': provider_usage
        }