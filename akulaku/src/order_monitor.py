#!/usr/bin/env python3
"""
Akulaku Order Monitor
Real-time monitoring of new orders with notifications.
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import Set, Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.akulaku_utils import (
    setup_credentials,
    list_orders,
    get_order_detail,
    accept_order,
    export_orders_to_csv
)


class OrderMonitor:
    """Monitor Akulaku orders in real-time."""
    
    def __init__(self, poll_interval: int = 60):
        """
        Initialize order monitor.
        
        Args:
            poll_interval: Seconds between API polls (default: 60)
        """
        self.poll_interval = poll_interval
        self.seen_orders: Set[str] = set()
        self.running = False
        
        # Notification settings
        self.telegram_enabled = os.getenv('AKULAKU_NOTIFICATION_TELEGRAM', 'false').lower() == 'true'
        self.telegram_chat_id = os.getenv('AKULAKU_TELEGRAM_CHAT_ID', '')
        
    def send_notification(self, message: str) -> None:
        """Send notification via Telegram."""
        if not self.telegram_enabled or not self.telegram_chat_id:
            print(f'[Notification] {message}')
            return
        
        try:
            import requests
            telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
            if not telegram_token:
                print(f'[Notification] {message}')
                return
            
            url = f'https://api.telegram.org/bot{telegram_token}/sendMessage'
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            requests.post(url, json=data, timeout=10)
            print(f'[Telegram] {message}')
        except Exception as e:
            print(f'[Notification Error] {e}')
            print(f'[Notification] {message}')
    
    def check_new_orders(self) -> None:
        """Check for new orders and send notifications."""
        try:
            result = list_orders(status='pending')
            
            if 'error' in result:
                print(f'[Error] {result["error"]}')
                return
            
            orders = result.get('data', [])
            new_orders = []
            
            for order in orders:
                order_id = order.get('order_id')
                if order_id and order_id not in self.seen_orders:
                    new_orders.append(order)
                    self.seen_orders.add(order_id)
            
            if new_orders:
                for order in new_orders:
                    message = self._format_order_message(order)
                    self.send_notification(message)
                    
                    # Auto-accept order (optional)
                    if os.getenv('AKULAKU_AUTO_ACCEPT', 'false').lower() == 'true':
                        accept_result = accept_order(order['order_id'])
                        if 'error' not in accept_result:
                            print(f'[Auto-Accept] Order {order["order_id"]} accepted')
                        else:
                            print(f'[Auto-Accept Error] {accept_result["error"]}')
            
            print(f'[{datetime.now().strftime("%H:%M:%S")}] Checked: {len(orders)} orders, {len(new_orders)} new')
            
        except Exception as e:
            print(f'[Error] {e}')
    
    def _format_order_message(self, order: Dict[str, Any]) -> str:
        """Format order details for notification."""
        return f"""🆕 <b>ORDER BARU!</b>

📦 Order ID: {order.get('order_id', 'N/A')}
🛍️ Produk: {order.get('product_name', 'N/A')}
📊 Jumlah: {order.get('quantity', 'N/A')}
💰 Total: Rp {order.get('total_amount', '0'):,}
👤 Buyer: {order.get('buyer_name', 'N/A')}
📍 Alamat: {order.get('shipping_address', 'N/A')}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    def start(self) -> None:
        """Start monitoring orders."""
        print('=' * 50)
        print('Akulaku Order Monitor')
        print('=' * 50)
        print(f'Poll interval: {self.poll_interval} seconds')
        print(f'Telegram notifications: {self.telegram_enabled}')
        print(f'Auto-accept: {os.getenv("AKULAKU_AUTO_ACCEPT", "false")}')
        print('=' * 50)
        print('Starting monitor... Press Ctrl+C to stop')
        print()
        
        self.running = True
        
        try:
            while self.running:
                self.check_new_orders()
                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            print('\n[Monitor] Stopped by user')
            self.running = False
    
    def stop(self) -> None:
        """Stop monitoring."""
        self.running = False


def main():
    """Main entry point."""
    # Setup credentials
    if not setup_credentials():
        print('Error: API credentials not configured!')
        print('Set AKULAKU_APP_KEY and AKULAKU_APP_SECRET environment variables')
        sys.exit(1)
    
    # Get poll interval from environment or use default
    poll_interval = int(os.getenv('AKULAKU_POLL_INTERVAL', '60'))
    
    # Create and start monitor
    monitor = OrderMonitor(poll_interval=poll_interval)
    monitor.start()


if __name__ == '__main__':
    main()
