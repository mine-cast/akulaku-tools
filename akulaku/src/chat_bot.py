#!/usr/bin/env python3
"""
Akulaku Chat Bot
Auto-reply untuk pertanyaan buyer.
"""

import os
import sys
import json
import re
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.akulaku_utils import setup_credentials, api_post, api_get


class ChatBot:
    """Bot auto-reply untuk chat buyer."""
    
    def __init__(self):
        self.templates = {}
        self.keywords_map = {}
        self.running = False
        self.replied_messages = set()
        
        # Load default templates
        self._load_default_templates()
    
    def _load_default_templates(self) -> None:
        """Load template default."""
        self.templates = {
            'greeting': {
                'keywords': ['halo', 'hai', 'hi', 'hello', 'selamat'],
                'response': 'Halo Kak! 👋 Selamat datang di toko kami! Ada yang bisa kami bantu? 😊'
            },
            'price': {
                'keywords': ['harga', 'berapa', 'murah', 'diskon', 'promo'],
                'response': 'Harga sudah tercantum di produk ya Kak. Kami juga sering kasih promo! Pantau terus toko kami untuk update terbaru! 🎉'
            },
            'stock': {
                'keywords': ['stok', 'ready', 'ada', 'tersedia'],
                'response': 'Stok produk bisa dilihat di halaman produk ya Kak. Kalau ada pertanyaan spesifik, silakan tanya langsung! 😊'
            },
            'shipping': {
                'keywords': ['kirim', 'pengiriman', 'ekspedisi', 'ongkir', 'ongkos kirim'],
                'response': 'Pengiriman via JNE, J&T, SiCepat, dan AnterAja ya Kak. Estimasi 2-5 hari tergantung lokasi. Gratis ongkir untuk pembelian minimal Rp 50.000! 📦'
            },
            'payment': {
                'keywords': ['bayar', 'pembayaran', 'transfer', 'cicilan', 'kredit'],
                'response': 'Pembayaran bisa via transfer bank, e-wallet (OVO, GoPay, Dana), dan cicilan Akulaku ya Kak! 💳'
            },
            'return': {
                'keywords': ['retur', 'kembali', 'refund', 'tukar', 'garansi'],
                'response': 'Garansi 7 hari setelah barang diterima ya Kak. Jika ada masalah, silakan chat kami dengan foto/video bukti. Kami bantu selesaikan! 🙏'
            },
            'size': {
                'keywords': ['ukuran', 'size', 'besar', 'kecil'],
                'response': 'Untuk info ukuran, silakan cek di deskripsi produk ya Kak. Jika masih bingung, kirimkan tinggi dan berat badan, kami bantu pilihkan ukuran yang pas! 👕'
            },
            'material': {
                'keywords': ['bahan', 'material', 'kain', 'kulit'],
                'response': 'Info bahan/material tercantum di deskripsi produk ya Kak. Jika butuh info lebih detail, silakan tanya langsung! 😊'
            },
            'color': {
                'keywords': ['warna', 'color', 'merah', 'biru', 'hitam', 'putih'],
                'response': 'Warna yang tersedia tercantum di pilihan produk ya Kak. Silakan pilih saat order! 🎨'
            },
            'thankyou': {
                'keywords': ['terima kasih', 'makasih', 'thanks', 'thx'],
                'response': 'Sama-sama Kak! Senang bisa membantu. Jangan lupa kasih review bintang 5 ya! ⭐⭐⭐⭐⭐'
            },
            'complaint': {
                'keywords': ['rusak', 'cacat', 'salah', 'kecewa', 'komplain'],
                'response': 'Mohon maaf atas ketidaknyamanannya Kak. Silakan kirimkan foto/video barang yang bermasalah, kami bantu proses retur/refund. Kepuasan pelanggan prioritas kami! 🙏'
            },
            'default': {
                'keywords': [],
                'response': 'Terima kasih sudah menghubungi kami! Kami akan merespons secepat mungkin. Ada yang bisa kami bantu? 😊'
            }
        }
        
        # Build keywords map
        self._build_keywords_map()
    
    def _build_keywords_map(self) -> None:
        """Build mapping dari keyword ke template."""
        self.keywords_map = {}
        
        for template_name, template_data in self.templates.items():
            for keyword in template_data['keywords']:
                self.keywords_map[keyword] = template_name
    
    def load_templates(self, file_path: str) -> None:
        """
        Load template dari file JSON.
        
        Args:
            file_path: Path ke file JSON
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            self.templates = json.load(f)
            self._build_keywords_map()
        print(f'[ChatBot] ✓ Templates dimuat dari {file_path}')
    
    def export_templates(self, output_path: str) -> None:
        """
        Export template ke file JSON.
        
        Args:
            output_path: Path output file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.templates, f, indent=2, ensure_ascii=False)
        print(f'[ChatBot] ✓ Templates diexport ke {output_path}')
    
    def add_template(self, name: str, keywords: List[str], response: str) -> None:
        """
        Tambah template baru.
        
        Args:
            name: Nama template
            keywords: List keyword
            response: Template response
        """
        self.templates[name] = {
            'keywords': keywords,
            'response': response
        }
        
        # Update keywords map
        for keyword in keywords:
            self.keywords_map[keyword] = name
        
        print(f'[ChatBot] ✓ Template "{name}" ditambahkan')
    
    def match_message(self, message: str) -> str:
        """
        Cari template yang cocok dengan pesan.
        
        Args:
            message: Pesan dari buyer
        
        Returns:
            Nama template yang cocok, atau 'default'
        """
        message_lower = message.lower()
        
        # Cari keyword match
        for keyword, template_name in self.keywords_map.items():
            if keyword in message_lower:
                return template_name
        
        return 'default'
    
    def generate_response(self, message: str, buyer_name: str = None, order_id: str = None) -> str:
        """
        Generate response berdasarkan pesan.
        
        Args:
            message: Pesan dari buyer
            buyer_name: Nama buyer (optional)
            order_id: ID order (optional)
        
        Returns:
            Response yang di-generate
        """
        # Cari template yang cocok
        template_name = self.match_message(message)
        template = self.templates[template_name]
        
        # Format response
        response = template['response']
        
        # Personalisasi jika ada nama buyer
        if buyer_name:
            response = response.replace('Kak', f'Kak {buyer_name}')
        
        return response
    
    def send_reply(self, chat_id: str, message: str) -> Dict[str, Any]:
        """
        Kirim reply ke chat.
        
        Args:
            chat_id: ID chat
            message: Pesan reply
        
        Returns:
            Response dari API
        """
        result = api_post('/chat/send', {
            'chat_id': chat_id,
            'message': message
        })
        
        if 'error' not in result:
            print(f'[ChatBot] ✓ Reply terkirim')
        else:
            print(f'[ChatBot] ✗ Gagal mengirim reply: {result.get("error")}')
        
        return result
    
    def get_unread_messages(self) -> List[Dict[str, Any]]:
        """Ambil pesan yang belum dibaca."""
        result = api_get('/chat/unread')
        
        if 'error' in result:
            return []
        
        return result.get('data', [])
    
    def process_message(self, message_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Proses pesan masuk.
        
        Args:
            message_data: Data pesan
        
        Returns:
            Response yang dikirim, atau None jika sudah diproses
        """
        message_id = message_data.get('message_id')
        chat_id = message_data.get('chat_id')
        message_text = message_data.get('message', '')
        buyer_name = message_data.get('buyer_name')
        
        # Cek apakah sudah diproses
        if message_id in self.replied_messages:
            return None
        
        # Generate response
        response = self.generate_response(message_text, buyer_name)
        
        # Kirim reply
        result = self.send_reply(chat_id, response)
        
        if 'error' not in result:
            self.replied_messages.add(message_id)
        
        return {
            'message_id': message_id,
            'incoming': message_text,
            'outgoing': response,
            'template_used': self.match_message(message_text)
        }
    
    def start_auto_reply(self, poll_interval: int = 30) -> None:
        """
        Mulai auto-reply bot.
        
        Args:
            poll_interval: Interval polling dalam detik
        """
        print('=' * 50)
        print('Akulaku Chat Bot')
        print('=' * 50)
        print(f'Poll interval: {poll_interval} seconds')
        print(f'Loaded templates: {len(self.templates)}')
        print('=' * 50)
        print('Starting bot... Press Ctrl+C to stop')
        print()
        
        self.running = True
        
        try:
            while self.running:
                # Ambil pesan baru
                messages = self.get_unread_messages()
                
                if messages:
                    print(f'[ChatBot] {len(messages)} pesan baru')
                    
                    for msg in messages:
                        result = self.process_message(msg)
                        
                        if result:
                            print(f'[ChatBot] [{result["template_used"]}] {result["incoming"][:50]}...')
                        
                        # Delay antar pesan
                        time.sleep(2)
                
                # Polling interval
                time.sleep(poll_interval)
                
        except KeyboardInterrupt:
            print('\n[ChatBot] Stopped by user')
            self.running = False
    
    def stop(self) -> None:
        """Stop bot."""
        self.running = False
    
    def get_stats(self) -> Dict[str, Any]:
        """Ambil statistik bot."""
        return {
            'total_templates': len(self.templates),
            'total_keywords': len(self.keywords_map),
            'total_replied': len(self.replied_messages),
            'templates': {name: len(data['keywords']) for name, data in self.templates.items()}
        }


def main():
    """Main function untuk testing."""
    if not setup_credentials():
        print('Error: API credentials not configured!')
        sys.exit(1)
    
    bot = ChatBot()
    
    print('=== Chat Bot ===\n')
    
    # Export templates
    print('1. Exporting templates...')
    bot.export_templates('chat_templates.json')
    
    # Test matching
    print('\n2. Testing message matching...')
    test_messages = [
        'Halo, ada yang bisa dibantu?',
        'Berapa harga produk ini?',
        'Stok masih ada?',
        'Kirim pakai apa?',
        'Terima kasih!'
    ]
    
    for msg in test_messages:
        template = bot.match_message(msg)
        response = bot.generate_response(msg, 'Budi')
        print(f'  "{msg}" → [{template}] {response[:50]}...')
    
    # Stats
    print('\n3. Bot statistics:')
    stats = bot.get_stats()
    print(f'  Templates: {stats["total_templates"]}')
    print(f'  Keywords: {stats["total_keywords"]}')
    
    # Start bot (uncomment untuk menjalankan)
    # print('\n4. Starting bot...')
    # bot.start_auto_reply(poll_interval=30)
    
    print('\n✓ Chat Bot siap digunakan!')


if __name__ == '__main__':
    main()
