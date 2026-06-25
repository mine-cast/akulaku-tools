#!/usr/bin/env python3
"""
Akulaku Kompetitor Tracker
Pantau harga dan strategi kompetitor.
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.akulaku_utils import setup_credentials, api_get, list_products


class KompetitorTracker:
    """Tool untuk memantau kompetitor di Akulaku."""
    
    def __init__(self):
        self.tracked_competitors = {}
        self.price_history = {}
    
    def search_competitors(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Cari kompetitor berdasarkan keyword.
        
        Args:
            keyword: Kata kunci pencarian
            limit: Jumlah hasil maksimal
        
        Returns:
            List produk kompetitor
        """
        print(f'[Tracker] Mencari kompetitor untuk: {keyword}')
        
        result = api_get('/goods/search', {
            'keyword': keyword,
            'page': '1',
            'page_size': str(limit),
            'sort': 'price_asc'
        })
        
        if 'error' in result:
            print(f'[Tracker] Error: {result["error"]}')
            return []
        
        competitors = result.get('data', [])
        print(f'[Tracker] Ditemukan {len(competitors)} produk kompetitor')
        
        return competitors
    
    def track_competitor(self, shop_id: str, shop_name: str = None) -> Dict[str, Any]:
        """
        Mulai track kompetitor.
        
        Args:
            shop_id: ID toko kompetitor
            shop_name: Nama toko (optional)
        
        Returns:
            Info kompetitor
        """
        print(f'[Tracker] Mulai track kompetitor: {shop_id}')
        
        # Ambil info toko
        shop_info = api_get('/shop/info', {'shop_id': shop_id})
        
        if 'error' in shop_info:
            print(f'[Tracker] Error: {shop_info["error"]}')
            return shop_info
        
        # Simpan info kompetitor
        self.tracked_competitors[shop_id] = {
            'shop_id': shop_id,
            'shop_name': shop_name or shop_info.get('shop_name', 'Unknown'),
            'tracked_since': datetime.now().isoformat(),
            'products_count': shop_info.get('products_count', 0),
            'rating': shop_info.get('rating', 0),
            'followers': shop_info.get('followers', 0)
        }
        
        print(f'[Tracker] ✓ Tracking {self.tracked_competitors[shop_id]["shop_name"]}')
        
        return self.tracked_competitors[shop_id]
    
    def get_competitor_products(self, shop_id: str) -> List[Dict[str, Any]]:
        """
        Ambil produk dari kompetitor.
        
        Args:
            shop_id: ID toko kompetitor
        
        Returns:
            List produk
        """
        result = api_get('/goods/list', {
            'shop_id': shop_id,
            'page': '1',
            'page_size': '100'
        })
        
        if 'error' in result:
            return []
        
        return result.get('data', [])
    
    def get_price_comparison(self, keyword: str) -> Dict[str, Any]:
        """
        Bandingkan harga untuk keyword tertentu.
        
        Args:
            keyword: Kata kunci produk
        
        Returns:
            Data perbandingan harga
        """
        print(f'[Tracker] Membandingkan harga untuk: {keyword}')
        
        competitors = self.search_competitors(keyword, limit=50)
        
        if not competitors:
            return {'error': 'No competitors found'}
        
        # Analisis harga
        prices = [float(p.get('price', 0)) for p in competitors if p.get('price')]
        
        if not prices:
            return {'error': 'No price data available'}
        
        analysis = {
            'keyword': keyword,
            'total_products': len(competitors),
            'price_stats': {
                'min': min(prices),
                'max': max(prices),
                'avg': sum(prices) / len(prices),
                'median': sorted(prices)[len(prices) // 2]
            },
            'top_cheapest': sorted(competitors, key=lambda x: float(x.get('price', 999999)))[:5],
            'top_expensive': sorted(competitors, key=lambda x: float(x.get('price', 0)), reverse=True)[:5],
            'analyzed_at': datetime.now().isoformat()
        }
        
        print(f'[Tracker] ✓ Analisis selesai:')
        print(f'  Harga terendah: Rp {analysis["price_stats"]["min"]:,.0f}')
        print(f'  Harga tertinggi: Rp {analysis["price_stats"]["max"]:,.0f}')
        print(f'  Harga rata-rata: Rp {analysis["price_stats"]["avg"]:,.0f}')
        
        return analysis
    
    def monitor_price_changes(self, product_ids: List[str]) -> Dict[str, Any]:
        """
        Monitor perubahan harga produk.
        
        Args:
            product_ids: List ID produk
        
        Returns:
            Data perubahan harga
        """
        print(f'[Tracker] Monitoring {len(product_ids)} produk...')
        
        changes = []
        
        for product_id in product_ids:
            # Ambil harga saat ini
            product = api_get('/goods/detail', {'goods_id': product_id})
            
            if 'error' in product:
                continue
            
            current_price = float(product.get('price', 0))
            
            # Cek history
            if product_id in self.price_history:
                last_price = self.price_history[product_id][-1]['price']
                
                if current_price != last_price:
                    change = {
                        'product_id': product_id,
                        'product_name': product.get('goods_name'),
                        'old_price': last_price,
                        'new_price': current_price,
                        'change': current_price - last_price,
                        'change_percent': ((current_price - last_price) / last_price) * 100,
                        'detected_at': datetime.now().isoformat()
                    }
                    changes.append(change)
            
            # Update history
            if product_id not in self.price_history:
                self.price_history[product_id] = []
            
            self.price_history[product_id].append({
                'price': current_price,
                'timestamp': datetime.now().isoformat()
            })
            
            # Simpan hanya 30 data terakhir
            if len(self.price_history[product_id]) > 30:
                self.price_history[product_id] = self.price_history[product_id][-30:]
            
            time.sleep(1)  # Rate limiting
        
        if changes:
            print(f'[Tracker] Ditemukan {len(changes)} perubahan harga')
        else:
            print(f'[Tracker] Tidak ada perubahan harga')
        
        return {
            'monitored': len(product_ids),
            'changes': changes,
            'checked_at': datetime.now().isoformat()
        }
    
    def get_trending_products(self, category: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Ambil produk trending.
        
        Args:
            category: Filter kategori (optional)
            limit: Jumlah hasil
        
        Returns:
            List produk trending
        """
        params = {
            'page': '1',
            'page_size': str(limit),
            'sort': 'sales_desc'
        }
        
        if category:
            params['category'] = category
        
        result = api_get('/goods/search', params)
        
        if 'error' in result:
            return []
        
        return result.get('data', [])
    
    def analyze_competitor_strategy(self, shop_id: str) -> Dict[str, Any]:
        """
        Analisis strategi kompetitor.
        
        Args:
            shop_id: ID toko kompetitor
        
        Returns:
            Analisis strategi
        """
        print(f'[Tracker] Menganalisis strategi kompetitor {shop_id}...')
        
        products = self.get_competitor_products(shop_id)
        
        if not products:
            return {'error': 'No products found'}
        
        # Analisis produk
        prices = [float(p.get('price', 0)) for p in products if p.get('price')]
        categories = [p.get('category') for p in products if p.get('category')]
        
        analysis = {
            'shop_id': shop_id,
            'total_products': len(products),
            'price_range': {
                'min': min(prices) if prices else 0,
                'max': max(prices) if prices else 0,
                'avg': sum(prices) / len(prices) if prices else 0
            },
            'top_categories': list(set(categories))[:10],
            'products_on_sale': len([p for p in products if p.get('discount')]),
            'avg_rating': sum(float(p.get('rating', 0)) for p in products) / len(products) if products else 0,
            'analyzed_at': datetime.now().isoformat()
        }
        
        # Rekomendasi
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        print(f'[Tracker] ✓ Analisis selesai')
        
        return analysis
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate rekomendasi berdasarkan analisis."""
        recommendations = []
        
        if analysis['price_range']['avg'] > 0:
            recommendations.append(f"Harga rata-rata kompetitor: Rp {analysis['price_range']['avg']:,.0f}")
        
        if analysis['products_on_sale'] > 0:
            recommendations.append(f"{analysis['products_on_sale']} produk sedang diskon")
        
        recommendations.append("Pantau harga kompetitor secara berkala")
        recommendations.append("Buat promo yang lebih menarik dari kompetitor")
        recommendations.append("Fokus pada kecepatan response dan kualitas foto")
        
        return recommendations
    
    def export_competitor_report(self, output_path: str) -> None:
        """Export laporan kompetitor ke JSON."""
        report = {
            'generated_at': datetime.now().isoformat(),
            'tracked_competitors': self.tracked_competitors,
            'price_history': self.price_history
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f'[Export] Laporan kompetitor diexport ke {output_path}')
    
    def get_price_alerts(self, threshold_percent: float = 10) -> List[Dict[str, Any]]:
        """
        Ambil alert perubahan harga signifikan.
        
        Args:
            threshold_percent: Threshold persen perubahan
        
        Returns:
            List alert
        """
        alerts = []
        
        for product_id, history in self.price_history.items():
            if len(history) < 2:
                continue
            
            latest = history[-1]['price']
            previous = history[-2]['price']
            
            change_percent = abs((latest - previous) / previous * 100)
            
            if change_percent >= threshold_percent:
                alerts.append({
                    'product_id': product_id,
                    'previous_price': previous,
                    'current_price': latest,
                    'change_percent': change_percent,
                    'direction': 'up' if latest > previous else 'down',
                    'detected_at': datetime.now().isoformat()
                })
        
        return alerts


def main():
    """Main function untuk testing."""
    if not setup_credentials():
        print('Error: API credentials not configured!')
        sys.exit(1)
    
    kt = KompetitorTracker()
    
    print('=== Kompetitor Tracker ===\n')
    
    # Contoh: Cari kompetitor
    print('1. Mencari kompetitor...')
    # Uncomment dan ganti dengan keyword yang valid:
    # competitors = kt.search_competitors('iphone 15')
    # print(f'Found {len(competitors)} competitors')
    
    # Contoh: Bandingkan harga
    print('\n2. Membandingkan harga...')
    # comparison = kt.get_price_comparison('iphone 15')
    # print(f'Price comparison: {comparison}')
    
    # Contoh: Track kompetitor
    print('\n3. Track kompetitor...')
    # kt.track_competitor('shop_id_123', 'Toko Kompetitor')
    
    # Export laporan
    print('\n4. Export laporan...')
    kt.export_competitor_report('kompetitor_report.json')
    
    print('\n✓ Kompetitor Tracker siap digunakan!')


if __name__ == '__main__':
    main()
