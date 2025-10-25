from scapy.all import sniff, Packet
from threading import Thread
import time
from collections import deque

class SnifZPacketSniffer:
    """Listens, counts, and reports packet I/O data for the PoT algorithm."""
    def __init__(self, interface: str):
        self.interface = interface
        self._is_sniffing = False
        self.packets_in_count = 0
        self.packets_out_count = 0
        self.session_io_history = deque(maxlen=10) # Store recent block I/O

    def start_sniffing(self):
        """Starts the packet sniffing thread."""
        if not self._is_sniffing:
            self._is_sniffing = True
            print(f"[*] Starting packet capture on interface: {self.interface}...")
            # Run sniff in a separate thread to prevent GUI lockup
            self.sniff_thread = Thread(target=self._sniff_loop, daemon=True)
            self.sniff_thread.start()

    def stop_sniffing(self):
        """Stops the packet sniffing thread."""
        self._is_sniffing = False
        print("[*] Packet capture stopped.")

    def _packet_callback(self, packet: Packet):
        """Callback function executed on every captured packet."""
        if not self._is_sniffing:
            return

        # Simple logic: check direction based on IP layer
        # This requires more complex logic for accurate in/out tracking, 
        # but provides the skeleton concept.
        
        # Example: Check if the packet is destined for this machine's IP (Inbound)
        # Note: True I/O is usually determined by the network adapter driver.
        # For Scapy, we approximate:
        
        # Assume all packets are counted as I/O for the PoT metric
        self.packets_in_count += 1
        self.packets_out_count += 1
        
    def _sniff_loop(self):
        """The main sniffing loop using scapy."""
        # Use store=0 to avoid excessive memory usage
        try:
            sniff(iface=self.interface, prn=self._packet_callback, stop_filter=lambda x: not self._is_sniffing, store=0)
        except Exception as e:
            print(f"[!] Sniffing Error on {self.interface}: {e}")
            self.stop_sniffing()

    def get_current_traffic_data(self) -> dict[str, int]:
        """Resets and returns the traffic count for the PoT algorithm."""
        data = {
            "packets_in": self.packets_in_count,
            "packets_out": self.packets_out_count
        }
        # Reset counters for the next 5-minute block
        self.packets_in_count = 0
        self.packets_out_count = 0
        self.session_io_history.append(data)
        return data

# Example Usage (To be run by GUI):
sniffer = SnifZPacketSniffer(interface="wlan0") # Replace "wlan0" with your adapter name
sniffer.start_sniffing()