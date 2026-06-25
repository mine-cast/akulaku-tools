#!/usr/bin/env python3
"""
Akulaku Promo Manager
Otomasi pembuatan voucher, diskon, dan flash sale.
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.akulaku_utils import setup_credentials, api_post, api_get


class PromoManager:
    """Manager untuk promo dan voucher Akulaku."""
    
    def __init__(self):
        self.active_promos = []
        self.voucher_codes = []
    
    def create_voucher(
        self,
        code: str,
        discount_percent: float,
        min_purchase: float = 0,
        max_discount: float = None,
        start_date: str = None,
        end_date: str = None,
        usage_limit: int = 100
    ) -> Dict[str, Any]:
        """
        Buat voucher diskon.
        
        Args:
            code: Kode voucher (misal: DISKON10)
            discount_percent: Persen diskon (1-100)
            min_purchase: Minimal pembelian
            max_discount: Maksimal diskon
            start_date: Tanggal mulai (YYYY-MM-DD)
            end_date: Tanggal berakhir (YYYY-MM-DD)
            usage_limit: Batas penggunaan
        
        Returns:
            Response dari API
        """
        print(f'[Promo] Membuat voucher: {code}')
        
        # Default dates
        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')
        if not end_date:
            end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        data = {
            'voucher_code': code,
            'discount_type': 'percent',
            'discount_value': str(discount_percent),
            'min_purchase': str(min_purchase),
            'start_date': start_date,
            'end_date': end_date,
            'usage_limit': str(usage_limit)
        }
        
        if max_discount:
            data['max_discount'] = str(max_discount)
        
        result = api_post('/promo/voucher/create', data)
        
        if 'error' not in result:
            self.voucher_codes.append(code)
            print(f'[Promo] ✓ Voucher {code} berhasil dibuat')
        else:
            print(f'[Promo] ✗ Gagal membuat voucher: {result.get("error")}')
        
        return result
    
    def create_discount(
        self,
        goods_id: str,
        discount_percent: float,
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, Any]:
        """
        Buat diskon untuk produk.
        
        Args:
            goods_id: ID produk
            discount_percent: Persen diskon
            start_date: Tanggal mulai
            end_date: Tanggal berakhir
        
        Returns:
            Response dari API
        """
        print(f'[Promo] Membuat diskon untuk produk {goods_id}')
        
        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')
        if not end_date:
            end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        data = {
            'goods_id': goods_id,
            'discount_type': 'percent',
            'discount_value': str(discount_percent),
            'start_date': start_date,
            'end_date': end_date
        }
        
        result = api_post('/promo/discount/create', data)
        
        if 'error' not in result:
            print(f'[Promo] ✓ Diskon berhasil dibuat')
        else:
            print(f'[Promo] ✗ Gagal membuat diskon: {result.get("error")}')
        
        return result
    
    def schedule_flash_sale(
        self,
        product_ids: List[str],
        discount: float,
        sale_time: str = None,
        duration_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Jadwalkan flash sale.
        
        Args:
            product_ids: List ID produk
            discount: Persen diskon
            sale_time: Waktu mulai (YYYY-MM-DD HH:MM)
            duration_hours: Durasi flash sale (jam)
        
        Returns:
            Response dari API
        """
        print(f'[Promo] Menjadwalkan flash sale untuk {len(product_ids)} produk')
        
        if not sale_time:
            # Default: besok jam 10 pagi
            tomorrow = datetime.now() + timedelta(days=1)
            sale_time = tomorrow.strftime('%Y-%m-%d') + ' 10:00'
        
        data = {
            'product_ids': ','.join(product_ids),
            'discount_type': 'percent',
            'discount_value': str(discount),
            'sale_time': sale_time,
            'duration_hours': str(duration_hours)
        }
        
        result = api_post('/promo/flash-sale/schedule', data)
        
        if 'error' not in result:
            print(f'[Promo] ✓ Flash sale dijadwalkan: {sale_time}')
            self.active_promos.append({
                'type': 'flash_sale',
                'products': product_ids,
                'discount': discount,
                'time': sale_time
            })
        else:
            print(f'[Promo] ✗ Gagal menjadwalkan flash sale: {result.get("error")}')
        
        return result
    
    def create_bundle(
        self,
        main_product_id: str,
        bundle_product_ids: List[str],
        bundle_discount: float
    ) -> Dict[str, Any]:
        """
        Buat bundle deal.
        
        Args:
            main_product_id: Produk utama
            bundle_product_ids: Produk bundle
            bundle_discount: Diskon bundle (persen)
        
        Returns:
            Response dari API
        """
        print(f'[Promo] Membuat bundle deal')
        
        data = {
            'main_product': main_product_id,
            'bundle_products': ','.join(bundle_product_ids),
            'discount_type': 'percent',
            'discount_value': str(bundle_discount)
        }
        
        result = api_post('/promo/bundle/create', data)
        
        if 'error' not in result:
            print(f'[Promo] ✓ Bundle deal berhasil dibuat')
        else:
            print(f'[Promo] ✗ Gagal membuat bundle: {result.get("error")}')
        
        return result
    
    def set_free_shipping(self, min_purchase: float = 50000) -> Dict[str, Any]:
        """
        Set promo gratis ongkir.
        
        Args:
            min_purchase: Minimal pembelian
        
        Returns:
            Response dari API
        """
        print(f'[Promo] Mengaktifkan gratis ongkir (min: Rp {min_purchase:,.0f})')
        
        data = {
            'promo_type': 'free_shipping',
            'min_purchase': str(min_purchase)
        }
        
        result = api_post('/promo/shipping/create', data)
        
        if 'error' not in result:
            print(f'[Promo] ✓ Gratis ongkir diaktifkan')
        else:
            print(f'[Promo] ✗ Gagal mengaktifkan gratis ongkir: {result.get("error")}')
        
        return result
    
    def get_active_promos(self) -> List[Dict[str, Any]]:
        """Ambil daftar promo aktif."""
        result = api_get('/promo/list', {'status': 'active'})
        
        if 'error' not in result:
            return result.get('data', [])
        return []
    
    def delete_promo(self, promo_id: str) -> Dict[str, Any]:
        """Hapus promo."""
        print(f'[Promo] Menghapus promo {promo_id}')
        return api_post('/promo/delete', {'promo_id': promo_id})
    
    def auto_create_weekly_promo(self, products: List[str]) -> None:
        """
        Otomatis buat promo mingguan.
        
        Args:
            products: List ID produk untuk promo
        """
        print('[Promo] Membuat promo mingguan otomatis...')
        
        # Voucher mingguan
        week_num = datetime.now().isocalendar()[1]
        voucher_code = f'MINGGU{week_num}'
        
        self.create_voucher(
            code=voucher_code,
            discount_percent=10,
            min_purchase=100000,
            max_discount=50000,
            usage_limit=50
        )
        
        # Flash sale weekend
        self.schedule_flash_sale(
            product_ids=products[:5],
            discount=20,
            sale_time=self._get_next_saturday() + ' 10:00',
            duration_hours=48
        )
        
        # Gratis ongkir
        self.set_free_shipping(min_purchase=50000)
        
        print('[Promo] ✓ Promo mingguan berhasil dibuat')
    
    def _get_next_saturday(self) -> str:
        """Dapatkan tanggal Sabtu berikutnya."""
        today = datetime.now()
        days_until_saturday = (5 - today.weekday()) % 7
        if days_until_saturday == 0:
            days_until_saturday = 7
        next_saturday = today + timedelta(days=days_until_saturday)
        return next_saturday.strftime('%Y-%m-%d')
    
    def export_promo_report(self, output_path: str) -> None:
        """Export laporan promo ke JSON."""
        report = {
            'generated_at': datetime.now().isoformat(),
            'active_vouchers': self.voucher_codes,
            'active_promos': self.active_promos,
            'recommendations': self._get_promo_recommendations()
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f'[Export] Laporan promo diexport ke {output_path}')
    
    def _get_promo_recommendations(self) -> List[str]:
        """Dapat rekomendasi promo."""
        return [
            'Buat voucher 10% setiap minggu untuk repeat buyer',
            'Adakan flash sale setiap weekend (Sabtu-Minggu)',
            'Aktifkan gratis ongkir minimal Rp 50.000',
            'Buat bundle deal untuk produk komplementer',
            'Gunakan limited time offer untuk create urgency'
        ]


def main():
    """Main function untuk testing."""
    if not setup_credentials():
        print('Error: API credentials not configured!')
        sys.exit(1)
    
    pm = PromoManager()
    
    print('=== Promo Manager ===\n')
    
    # Contoh: Buat voucher
    print('1. Membuat voucher...')
    pm.create_voucher(
        code='TEST10',
        discount_percent=10,
        min_purchase=100000,
        usage_limit=10
    )
    
    # Contoh: Set gratis ongkir
    print('\n2. Mengaktifkan gratis ongkir...')
    pm.set_free_shipping(min_purchase=50000)
    
    # Contoh: Rekomendasi
    print('\n3. Rekomendasi promo:')
    for rec in pm._get_promo_recommendations():
        print(f'  • {rec}')
    
    # Export laporan
    print('\n4. Export laporan...')
    pm.export_promo_report('promo_report.json')


if __name__ == '__main__':
    main()
