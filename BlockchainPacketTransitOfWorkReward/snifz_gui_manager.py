import random
import time
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QGridLayout, QLabel, QLineEdit, QPushButton, 
    QProgressBar, QGroupBox, QScrollArea, QComboBox
)
from PyQt5.QtCore import QTimer, Qt, QObject, pyqtSignal
from PyQt5.QtGui import QColor, QPalette, QPixmap

# --- Core Application Logic Imports ---
from snifz_blockchain_core import SnifZBlockchain, TOKEN_SYMBOL
from snifz_packet_sniffer import SnifZPacketSniffer
from sniff_reward_logic import SnifZRewardSystem, MINT_INTERVAL_SECONDS
from snifz_web3_connect import SnifZWeb3Connector

class GUILogger(QObject):
    """A signal-based logger to safely update GUI from other threads."""
    log_signal = pyqtSignal(str)

class SnifZGUI(QMainWindow):
    """The main high-level quality GUI for the Sniffing-Packeting blockchain."""
    
    THEME_COLORS = {
        "primary": QColor("#007ACC"),  # Azure/Blue for eye-uplifting effect
        "secondary": QColor("#222222"), # Dark background
        "text": QColor("#FFFFFF"),     # White text
        "indicator": QColor("#4CAF50") # Green for success
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sniffing-Packeting Core Node Interface")
        self.setGeometry(100, 100, 1200, 800)
        
        self._setup_style()

        # --- Initialize Backend Components ---
        self.logger = GUILogger()
        self.logger.log_signal.connect(self._update_log)

        self.blockchain = SnifZBlockchain()
        self.web3_connector = SnifZWeb3Connector()
        my_address = self.web3_connector.generate_unique_core_address()
        
        self.reward_system = SnifZRewardSystem(self.blockchain, my_address)
        self.sniffer = SnifZPacketSniffer(interface="wlan0") # Default interface

        self._setup_ui()
        self._initial_ui_update()
        
        # QTimer for the core functional loop and GUI updates (simulating real-time)
        self.main_loop_timer = QTimer(self)
        self.main_loop_timer.timeout.connect(self._run_functional_loop)
        self.main_loop_timer.start(1000) # Update every 1 second

        self.logger.log_signal.emit(f"Genesis Block Created: {self.blockchain.chain[0].compute_hash()}")
        self.logger.log_signal.emit(f"Your unique core address is: {my_address}")
        self.logger.log_signal.emit("System Initialized. Select an interface and start sniffing.")


    def _setup_style(self):
        """Applies a custom, high-quality dark theme."""
        palette = QPalette()
        palette.setColor(QPalette.Window, self.THEME_COLORS["secondary"])
        palette.setColor(QPalette.WindowText, self.THEME_COLORS["text"])
        palette.setColor(QPalette.Base, QColor("#111111"))
        palette.setColor(QPalette.AlternateBase, QColor("#333333"))
        palette.setColor(QPalette.ToolTipBase, self.THEME_COLORS["text"])
        palette.setColor(QPalette.ToolTipText, self.THEME_COLORS["text"])
        palette.setColor(QPalette.Text, self.THEME_COLORS["text"])
        palette.setColor(QPalette.Button, QColor("#555555"))
        palette.setColor(QPalette.ButtonText, self.THEME_COLORS["text"])
        palette.setColor(QPalette.Highlight, self.THEME_COLORS["primary"])
        palette.setColor(QPalette.HighlightedText, self.THEME_COLORS["text"])
        self.setPalette(palette)
        
        # CSS styling for interactive widgets
        self.setStyleSheet(f"""
            QGroupBox {{ border: 2px solid {self.THEME_COLORS["primary"].name()}; margin-top: 10px; }}
            QLabel#LED_Indicator {{ background-color: red; border-radius: 10px; min-width: 20px; max-width: 20px; min-height: 20px; max-height: 20px; }}
            QPushButton {{ background-color: {self.THEME_COLORS["primary"].name()}; color: white; padding: 10px; border-radius: 5px; }}
            QPushButton:hover {{ background-color: {self.THEME_COLORS["primary"].darker(120).name()}; }}
        """)

    def _setup_ui(self):
        """Sets up the 4-dock high-level GUI layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # 4 Docks are implemented as two vertical halves, each with two QGroupBoxes
        
        # --- Left Side Docks (Core Status & Packet Sniffer) ---
        left_column = QVBoxLayout()
        left_column.addWidget(self._create_dock_1()) # Dock 1: Core Node Status
        left_column.addWidget(self._create_dock_2()) # Dock 2: Packet Sniffer
        main_layout.addLayout(left_column)

        # --- Right Side Docks (Wallet & Web3) ---
        right_column = QVBoxLayout()
        right_column.addWidget(self._create_dock_3()) # Dock 3: Wallet & Rewards
        right_column.addWidget(self._create_dock_4()) # Dock 4: Web3 & Global Connectivity
        main_layout.addLayout(right_column)
        
    def _create_dock_1(self):
        """Creates Dock 1: Core Node Status (Widgets 1-8)"""
        group = QGroupBox("Dock 1: Core Node Status & Chain View")
        layout = QGridLayout()
        group.setLayout(layout)
        
        # W1: $@SNFZ@$ CORE STATUS (LED/Indicator)
        self.w1_status_led = QLabel()
        self.w1_status_led.setObjectName("LED_Indicator")
        self.w1_status_text = QLabel("W1: $@SNFZ@$ CORE STATUS: Syncing...")
        layout.addWidget(self.w1_status_led, 0, 0, Qt.AlignLeft)
        layout.addWidget(self.w1_status_text, 0, 1, 1, 2)
        
        # W2: Current Block Count
        self.w2_block_count = QLabel("W2: Current Block Count: 000,000")
        layout.addWidget(self.w2_block_count, 1, 0, 1, 3)
        
        # W4: Next Mint Timer
        self.w4_mint_timer = QLabel("W4: Next Mint Timer: 05:00")
        layout.addWidget(self.w4_mint_timer, 2, 0, 1, 3)

        # W6: Current PoT Difficulty
        self.w6_difficulty = QProgressBar()
        self.w6_difficulty.setFormat("W6: PoT Difficulty %p%")
        layout.addWidget(self.w6_difficulty, 3, 0, 1, 3)

        # W7: Chain Validation Log (Scrollable Text)
        self.w7_log = QLineEdit("W7: Chain Validation Log: Initializing...")
        self.w7_log.setReadOnly(True)
        layout.addWidget(QLabel("Chain Log:"), 4, 0)
        layout.addWidget(self.w7_log, 4, 1, 1, 2) # This will show the latest log message
        
        # W3, W5, W8 placeholders are managed similarly...
        
        return group

    def _create_dock_2(self):
        """Creates Dock 2: Packet Sniffer & Traffic Algorithm (Widgets 9-16)"""
        group = QGroupBox("Dock 2: Packet Sniffer & Traffic Algorithm")
        layout = QGridLayout()
        group.setLayout(layout)
        
        # W9: Active Network Interface
        self.w9_iface_select = QComboBox()
        self.w9_iface_select.addItems(["wlan0", "eth0", "lo"])
        self.w9_iface_select.currentTextChanged.connect(self._change_interface)
        layout.addWidget(QLabel("W9: Interface:"), 0, 0)
        layout.addWidget(self.w9_iface_select, 0, 1)

        # W10: Total Session Packets I/O
        self.w10_total_packets = QLabel("W10: Total Packets I/O: 0")
        layout.addWidget(self.w10_total_packets, 1, 0, 1, 2)

        # W11: Packets to Next Block
        self.w11_progress = QProgressBar()
        self.w11_progress.setFormat("W11: Packets to Next Block %p%")
        layout.addWidget(self.w11_progress, 2, 0, 1, 2)
        
        # W16: Start/Stop Packet Sniffing
        self.w16_start_stop = QPushButton("W16: Start/Stop Packet Sniffing")
        self.w16_start_stop.clicked.connect(self._toggle_sniffer)
        layout.addWidget(self.w16_start_stop, 3, 0, 1, 2)

        # W13: External Node Traffic (Data Grid Placeholder)
        self.w13_traffic_grid = QLabel("W13: External Node Traffic Grid (Dynamic Table)")
        layout.addWidget(self.w13_traffic_grid, 4, 0, 1, 2)
        
        # W12, W14, W15 placeholders...

        return group
        
    def _create_dock_3(self):
        """Creates Dock 3: Wallet, Rewards, and Token Management (Widgets 17-24)"""
        group = QGroupBox("Dock 3: Wallet, Rewards, and Token Management")
        layout = QGridLayout()
        group.setLayout(layout)
        
        # W17: My Unique Core Address
        self.w17_address = QLineEdit("W17: 0xSnifZ_Unique_Address...")
        self.w17_address.setReadOnly(True)
        layout.addWidget(QLabel("Address:"), 0, 0)
        layout.addWidget(self.w17_address, 0, 1, 1, 2)

        # W19: Current $@SNFZ@$ Balance
        self.w19_balance = QLabel("W19: Current $@SNFZ@$ Balance: 0.00")
        self.w19_balance.setStyleSheet("font-size: 24px; color: yellow;")
        layout.addWidget(self.w19_balance, 1, 0, 1, 3)

        # W21 & W22: Send/Receive
        self.w21_send = QPushButton("W21: Send $@SNFZ@$")
        self.w22_receive = QPushButton("W22: Show/Hide QR Code")
        self.w22_receive.clicked.connect(self._toggle_qr_code)
        layout.addWidget(self.w21_send, 2, 0)
        layout.addWidget(self.w22_receive, 2, 1)
        
        # W18: QR Code
        self.w18_qr_code = QLabel("")
        layout.addWidget(self.w18_qr_code, 3, 0, 1, 3, Qt.AlignCenter)

        # W23: Randomization Factor
        self.w23_random = QLabel("W23: Randomization Factor: 3.5%")
        layout.addWidget(self.w23_random, 4, 0, 1, 3)

        # W20, W24 placeholders...

        return group

    def _create_dock_4(self):
        """Creates Dock 4: Web3 & Global Connectivity (Widgets 25-30)"""
        group = QGroupBox("Dock 4: Web3 & Global Connectivity")
        layout = QVBoxLayout()
        group.setLayout(layout)

        # W25: WalletConnect Web3 Button
        self.w25_wallet_connect = QPushButton("W25: 🌐 Wallet Connect Web3")
        self.w25_wallet_connect.setStyleSheet("background-color: #F6851B;") # Web3 Orange
        layout.addWidget(self.w25_wallet_connect)

        # W26: WalletConnect Status
        self.w26_status = QLabel("W26: WalletConnect Status: Disconnected")
        layout.addWidget(self.w26_status)
        
        # W28: In-App Swap/Trade (Placeholder)
        self.w28_swap = QLabel("W28: In-App Swap/Trade Widget")
        layout.addWidget(self.w28_swap)

        # W29: Network Peer Count
        self.w29_peer_count = QLabel("W29: Network Peer Count: 1 (Core)")
        layout.addWidget(self.w29_peer_count)

        # W30: Download Core Documentation
        self.w30_docs = QPushButton("W30: Download Core Documentation")
        layout.addWidget(self.w30_docs)
        
        # W27 placeholder...
        
        return group

    def _initial_ui_update(self):
        """Sets the initial state of the UI from the backend components."""
        self.w17_address.setText(self.reward_system.my_node_address)
        self.w6_difficulty.setValue(self.reward_system.blockchain.difficulty * 10) # Scale for visibility

    def _update_log(self, message: str):
        """Updates the log widget with a new message."""
        self.w7_log.setText(message)

    def _change_interface(self, interface_name: str):
        """Handles changing the network interface."""
        if self.sniffer._is_sniffing:
            self.logger.log_signal.emit("Stop sniffer before changing interface.")
            # Revert selection
            self.w9_iface_select.setCurrentText(self.sniffer.interface)
            return
        self.sniffer.interface = interface_name
        self.logger.log_signal.emit(f"Interface set to {interface_name}. Ready to start.")

    def _toggle_sniffer(self):
        """Starts or stops the packet sniffer."""
        if self.sniffer._is_sniffing:
            self.sniffer.stop_sniffing()
            self.logger.log_signal.emit("Packet capture stopped.")
            self.w1_status_led.setStyleSheet("background-color: red;")
        else:
            self.sniffer.start_sniffing()
            self.logger.log_signal.emit(f"Packet capture started on {self.sniffer.interface}.")
            self.w1_status_led.setStyleSheet(f"background-color: {self.THEME_COLORS['indicator'].name()};")

    def _toggle_qr_code(self):
        """Shows or hides the wallet address QR code."""
        if self.w18_qr_code.pixmap():
            self.w18_qr_code.clear()
        else:
            qr_stream = self.web3_connector.generate_address_qr_code()
            pixmap = QPixmap()
            pixmap.loadFromData(qr_stream.getvalue())
            self.w18_qr_code.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))

    def _run_functional_loop(self):
        """
        The main functional loop running every second. 
        This is where the high-level system logic is executed and the GUI is updated.
        """
        # 1. Update Block Count and Timer
        self.w2_block_count.setText(f"W2: Current Block Count: {self.blockchain.last_block.index:06d}")
        remaining_time = MINT_INTERVAL_SECONDS - (time.time() - self.reward_system._last_mint_time)
        remaining_time = max(0, remaining_time)
        self.w4_mint_timer.setText(f"W4: Next Mint Timer: {int(remaining_time // 60):02d}:{int(remaining_time % 60):02d}")
        
        # 2. Check for new blocks (and attempt to mint if time is up)
        if self.sniffer._is_sniffing:
            my_traffic = self.sniffer.get_current_traffic_data()
            if self.reward_system.try_to_mint_block(my_traffic):
                # A block was minted, update log and balance
                last_block = self.blockchain.last_block
                winner = last_block.transactions[0]['recipient']
                self.logger.log_signal.emit(f"Block {last_block.index} minted! Winner: {winner[:10]}...")
                # Update balance if we are the winner
                if winner == self.reward_system.my_node_address:
                    balance = self.reward_system.get_balance(self.reward_system.my_node_address)
                    self.w19_balance.setText(f"W19: Current {TOKEN_SYMBOL} Balance: {balance:,.2f}")
        
        # 3. Update Packet I/O in Dock 2
        if self.sniffer._is_sniffing:
            total_io = self.sniffer.packets_in_count + self.sniffer.packets_out_count
            self.w10_total_packets.setText(f"W10: Total Packets I/O: {total_io}")
            # Simulate progress to next block (based on time)
            progress = ((MINT_INTERVAL_SECONDS - remaining_time) / MINT_INTERVAL_SECONDS) * 100
            self.w11_progress.setValue(int(progress))
        
        # 4. Color Changing (Thematic Engine Concept)
        # Change a widget's color randomly for the "color changing GUI system" effect
        if random.randint(1, 20) == 1:
            self.w16_start_stop.setStyleSheet(f"background-color: #{random.randint(0, 0xFFFFFF):06x}; color: white; padding: 10px; border-radius: 5px;")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = SnifZGUI()
    gui.show()
    sys.exit(app.exec_())