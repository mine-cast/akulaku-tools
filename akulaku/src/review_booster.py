#!/usr/bin/env python3
"""
Akulaku Review Booster
Sistem follow-up buyer untuk meningkatkan review dan rating.
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.akulaku_utils import setup_credentials, api_post, api_get, list_orders, get_order_detail


class ReviewBooster:
    """Sistem untuk meningkatkan review dan rating toko."""
    
    def __init__(self):
        self.followed_up_orders = set()
        self.review_templates = self._load_default_templates()
    
    def _load_default_templates(self) -> Dict[str, str]:
        """Load template chat default."""
        return {
            'greeting': 'Halo Kak {buyer_name}! 👋\n\nTerima kasih sudah berbelanja di toko kami! 🙏',
            
            'shipping_update': '📦 Update pengiriman:\n\nPesanan Kak {buyer_name} sudah dikirim dengan resi {tracking_number}.\n\nEstimasi sampai: {estimated_days} hari lagi.\n\nTerima kasih sudah menunggu! 😊',
            
            'delivered': '🎉 Pesanan sudah sampai!\n\nHalo Kak {buyer_name},\n\nPesanan dengan nomor resi {tracking_number} sudah diterima.\n\nSemoga puas dengan produknya ya! 🙏',
            
            'review_request': '⭐ Minta Review\n\nHalo Kak {buyer_name},\n\nTerima kasih sudah berbelanja di toko kami! 🙏\n\nJika berkenan, mohon bantuannya untuk memberikan review dan bintang 5 ya. Review dari Kakak sangat berarti untuk perkembangan toko kami. ⭐⭐⭐⭐⭐\n\nTerima kasih banyak! 😊',
            
            'follow_up': '💬 Follow Up\n\nHalo Kak {buyer_name},\n\nGimana produknya? Puas ga? 😊\n\nKalau ada pertanyaan atau kendala, jangan ragu chat kami ya!\n\nTerima kasih! 🙏',
            
            'repeat_offer': '🎁 Penawaran Spesial!\n\nHalo Kak {buyer_name},\n\nTerima kasih sudah menjadi pelanggan setia kami! 🙏\n\nSebagai bentuk apresiasi, kami berikan kode voucher khusus: {voucher_code}\n\nDiskon {discount}% untuk pembelian berikutnya!\n\nGunakan sebelum: {expiry_date}\n\nTerima kasih! 😊'
        }
    
    def send_follow_up(self, order_id: str, template_type: str = 'follow_up') -> Dict[str, Any]:
        """
        Kirim follow-up ke buyer.
        
        Args:
            order_id: ID order
            template_type: Tipe template ('greeting', 'shipping_update', 'delivered', 'review_request', 'follow_up', 'repeat_offer')
        
        Returns:
            Response dari API
        """
        # Cek apakah sudah follow-up
        if order_id in self.followed_up_orders:
            print(f'[Review] Order {order_id} sudah di-follow-up')
            return {'status': 'already_followed_up'}
        
        # Ambil detail order
        order = get_order_detail(order_id)
        
        if 'error' in order:
            print(f'[Review] Error: {order["error"]}')
            return order
        
        # Ambil data buyer
        buyer_name = order.get('buyer_name', 'Customer')
        tracking_number = order.get('tracking_number', '-')
        
        # Pilih template
        template = self.review_templates.get(template_type, self.review_templates['follow_up'])
        
        # Format pesan
        message = template.format(
            buyer_name=buyer_name,
            tracking_number=tracking_number,
            estimated_days='3-5',
            voucher_code=f'LOYAL{buyer_name[:4].upper()}',
            discount=10,
            expiry_date=(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        )
        
        # Kirim pesan
        result = api_post('/chat/send', {
            'order_id': order_id,
            'message': message
        })
        
        if 'error' not in result:
            self.followed_up_orders.add(order_id)
            print(f'[Review] ✓ Follow-up terkirim ke {buyer_name}')
        else:
            print(f'[Review] ✗ Gagal mengirim follow-up: {result.get("error")}')
        
        return result
    
    def request_review(self, order_id: str) -> Dict[str, Any]:
        """
        Minta review dari buyer.
        
        Args:
            order_id: ID order
        
        Returns:
            Response dari API
        """
        return self.send_follow_up(order_id, 'review_request')
    
    def send_shipping_update(self, order_id: str, tracking_number: str) -> Dict[str, Any]:
        """
        Kirim update pengiriman.
        
        Args:
            order_id: ID order
            tracking_number: Nomor resi
        
        Returns:
            Response dari API
        """
        order = get_order_detail(order_id)
        
        if 'error' in order:
            return order
        
        buyer_name = order.get('buyer_name', 'Customer')
        
        template = self.review_templates['shipping_update']
        message = template.format(
            buyer_name=buyer_name,
            tracking_number=tracking_number,
            estimated_days='3-5'
        )
        
        result = api_post('/chat/send', {
            'order_id': order_id,
            'message': message
        })
        
        if 'error' not in result:
            print(f'[Review] ✓ Update pengiriman terkirim')
        else:
            print(f'[Review] ✗ Gagal mengirim update: {result.get("error")}')
        
        return result
    
    def send_repeat_offer(self, order_id: str, discount: float = 10) -> Dict[str, Any]:
        """
        Kirim penawaran repeat order.
        
        Args:
            order_id: ID order sebelumnya
            discount: Persen diskon
        
        Returns:
            Response dari API
        """
        order = get_order_detail(order_id)
        
        if 'error' in order:
            return order
        
        buyer_name = order.get('buyer_name', 'Customer')
        voucher_code = f'LOYAL{buyer_name[:4].upper()}{datetime.now().month}'
        
        template = self.review_templates['repeat_offer']
        message = template.format(
            buyer_name=buyer_name,
            voucher_code=voucher_code,
            discount=discount,
            expiry_date=(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        )
        
        result = api_post('/chat/send', {
            'order_id': order_id,
            'message': message
        })
        
        if 'error' not in result:
            print(f'[Review] ✓ Penawaran repeat order terkirim')
        else:
            print(f'[Review] ✗ Gagal mengirim penawaran: {result.get("error")}')
        
        return result
    
    def auto_follow_up_delivered(self, days_after_delivery: int = 3) -> Dict[str, Any]:
        """
        Otomatis follow-up order yang sudah delivered.
        
        Args:
            days_after_delivery: Hari setelah barang sampai
        
        Returns:
            Summary hasil follow-up
        """
        print(f'[Review] Mencari order delivered {days_after_delivery} hari lalu...')
        
        # Ambil order delivered
        orders = list_orders(status='delivered')
        
        if 'error' in orders:
            return orders
        
        results = {
            'total': 0,
            'followed_up': 0,
            'skipped': 0,
            'errors': []
        }
        
        for order in orders.get('data', []):
            order_id = order.get('order_id')
            delivered_at = order.get('delivered_at')
            
            if not order_id or not delivered_at:
                continue
            
            # Cek apakah sudah cukup hari setelah delivery
            delivered_date = datetime.strptime(delivered_at, '%Y-%m-%d %H:%M:%S')
            days_since = (datetime.now() - delivered_date).days
            
            if days_since >= days_after_delivery:
                results['total'] += 1
                
                if order_id not in self.followed_up_orders:
                    result = self.request_review(order_id)
                    
                    if 'error' not in result:
                        results['followed_up'] += 1
                    else:
                        results['errors'].append({
                            'order_id': order_id,
                            'error': result.get('error')
                        })
                    
                    # Delay untuk menghindari rate limit
                    time.sleep(2)
                else:
                    results['skipped'] += 1
        
        print(f'[Review] ✓ Selesai: {results["followed_up"]} di-follow-up, {results["skipped"]} dilewati')
        
        return results
    
    def update_template(self, template_type: str, template: str) -> None:
        """
        Update template chat.
        
        Args:
            template_type: Tipe template
            template: Template baru
        """
        self.review_templates[template_type] = template
        print(f'[Review] ✓ Template {template_type} diupdate')
    
    def load_templates_from_file(self, file_path: str) -> None:
        """
        Load template dari file JSON.
        
        Args:
            file_path: Path ke file JSON
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            self.review_templates = json.load(f)
        print(f'[Review] ✓ Templates dimuat dari {file_path}')
    
    def export_templates(self, output_path: str) -> None:
        """
        Export template ke file JSON.
        
        Args:
            output_path: Path output file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.review_templates, f, indent=2, ensure_ascii=False)
        print(f'[Review] ✓ Templates diexport ke {output_path}')
    
    def get_review_stats(self) -> Dict[str, Any]:
        """Ambil statistik review."""
        result = api_get('/shop/review/stats')
        
        if 'error' not in result:
            return result.get('data', {})
        return {}
    
    def get_follow_up_history(self) -> List[str]:
        """Ambil history follow-up."""
        return list(self.followed_up_orders)


def main():
    """Main function untuk testing."""
    if not setup_credentials():
        print('Error: API credentials not configured!')
        sys.exit(1)
    
    rb = ReviewBooster()
    
    print('=== Review Booster ===\n')
    
    # Export templates
    print('1. Exporting templates...')
    rb.export_templates('review_templates.json')
    
    # Load templates dari file
    print('\n2. Loading templates...')
    rb.load_templates_from_file('review_templates.json')
    
    # Contoh follow-up
    print('\n3. Contoh follow-up...')
    # Uncomment dan ganti dengan order_id yang valid:
    # rb.send_follow_up('ORDER123', 'review_request')
    
    # Auto follow-up delivered orders
    print('\n4. Auto follow-up delivered orders...')
    # Uncomment untuk menjalankan:
    # results = rb.auto_follow_up_delivered(days_after_delivery=3)
    # print(f'Results: {results}')
    
    print('\n✓ Review Booster siap digunakan!')


if __name__ == '__main__':
    main()
