#!/usr/bin/env python3
"""
Akulaku Analytics Dashboard
Monitor performa toko dan analisis penjualan.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.akulaku_utils import setup_credentials, api_get, list_orders, list_products


class Analytics:
    """Dashboard analytics untuk toko Akulaku."""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 menit
    
    def get_daily_report(self, date: str = None) -> Dict[str, Any]:
        """
        Generate laporan harian.
        
        Args:
            date: Tanggal (YYYY-MM-DD), default hari ini
        
        Returns:
            Laporan harian
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        print(f'[Analytics] Generating laporan untuk {date}...')
        
        # Ambil data order
        orders = list_orders(
            start_time=f'{date} 00:00:00',
            end_time=f'{date} 23:59:59'
        )
        
        if 'error' in orders:
            return orders
        
        order_list = orders.get('data', [])
        
        # Hitung statistik
        total_orders = len(order_list)
        total_revenue = sum(float(o.get('total_amount', 0)) for o in order_list)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Status breakdown
        status_counts = {}
        for order in order_list:
            status = order.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Produk terlaris
        product_counts = {}
        for order in order_list:
            product_name = order.get('product_name', 'Unknown')
            product_counts[product_name] = product_counts.get(product_name, 0) + 1
        
        top_products = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        report = {
            'date': date,
            'summary': {
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'average_order_value': avg_order_value
            },
            'status_breakdown': status_counts,
            'top_products': [{'name': p[0], 'orders': p[1]} for p in top_products],
            'generated_at': datetime.now().isoformat()
        }
        
        print(f'[Analytics] ✓ Laporan selesai:')
        print(f'  Total order: {total_orders}')
        print(f'  Total revenue: Rp {total_revenue:,.0f}')
        print(f'  Rata-rata order: Rp {avg_order_value:,.0f}')
        
        return report
    
    def get_weekly_report(self, end_date: str = None) -> Dict[str, Any]:
        """
        Generate laporan mingguan.
        
        Args:
            end_date: Tanggal akhir (YYYY-MM-DD), default hari ini
        
        Returns:
            Laporan mingguan
        """
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        end = datetime.strptime(end_date, '%Y-%m-%d')
        start = end - timedelta(days=7)
        
        print(f'[Analytics] Generating laporan mingguan {start.strftime("%Y-%m-%d")} hingga {end_date}...')
        
        # Kumpulkan data harian
        daily_reports = []
        current = start
        
        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            daily = self.get_daily_report(date_str)
            
            if 'error' not in daily:
                daily_reports.append(daily)
            
            current += timedelta(days=1)
        
        # Hitung total mingguan
        total_orders = sum(d['summary']['total_orders'] for d in daily_reports)
        total_revenue = sum(d['summary']['total_revenue'] for d in daily_reports)
        
        # Trend
        if len(daily_reports) >= 2:
            first_half = daily_reports[:len(daily_reports)//2]
            second_half = daily_reports[len(daily_reports)//2:]
            
            first_revenue = sum(d['summary']['total_revenue'] for d in first_half)
            second_revenue = sum(d['summary']['total_revenue'] for d in second_half)
            
            revenue_trend = ((second_revenue - first_revenue) / first_revenue * 100) if first_revenue > 0 else 0
        else:
            revenue_trend = 0
        
        report = {
            'period': f'{start.strftime("%Y-%m-%d")} to {end_date}',
            'summary': {
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'daily_average_orders': total_orders / 7,
                'daily_average_revenue': total_revenue / 7
            },
            'trend': {
                'revenue_change_percent': revenue_trend,
                'direction': 'up' if revenue_trend > 0 else 'down'
            },
            'daily_breakdown': [{
                'date': d['date'],
                'orders': d['summary']['total_orders'],
                'revenue': d['summary']['total_revenue']
            } for d in daily_reports],
            'generated_at': datetime.now().isoformat()
        }
        
        print(f'[Analytics] ✓ Laporan mingguan selesai:')
        print(f'  Total order: {total_orders}')
        print(f'  Total revenue: Rp {total_revenue:,.0f}')
        print(f'  Trend: {"↑" if revenue_trend > 0 else "↓"} {abs(revenue_trend):.1f}%')
        
        return report
    
    def get_top_products(self, limit: int = 10, period_days: int = 30) -> List[Dict[str, Any]]:
        """
        Ambil produk terlaris.
        
        Args:
            limit: Jumlah produk
            period_days: Periode hari
        
        Returns:
            List produk terlaris
        """
        print(f'[Analytics] Mengambil top {limit} produk terlaris...')
        
        start_date = (datetime.now() - timedelta(days=period_days)).strftime('%Y-%m-%d')
        
        orders = list_orders(start_time=f'{start_date} 00:00:00')
        
        if 'error' in orders:
            return []
        
        # Hitung penjualan per produk
        product_sales = {}
        
        for order in orders.get('data', []):
            product_id = order.get('goods_id')
            product_name = order.get('product_name', 'Unknown')
            quantity = int(order.get('quantity', 1))
            revenue = float(order.get('total_amount', 0))
            
            if product_id not in product_sales:
                product_sales[product_id] = {
                    'product_id': product_id,
                    'product_name': product_name,
                    'total_sold': 0,
                    'total_revenue': 0
                }
            
            product_sales[product_id]['total_sold'] += quantity
            product_sales[product_id]['total_revenue'] += revenue
        
        # Sort by total sold
        top_products = sorted(
            product_sales.values(),
            key=lambda x: x['total_sold'],
            reverse=True
        )[:limit]
        
        print(f'[Analytics] ✓ Ditemukan {len(top_products)} produk terlaris')
        
        return top_products
    
    def get_conversion_rate(self, period_days: int = 30) -> Dict[str, Any]:
        """
        Hitung conversion rate.
        
        Args:
            period_days: Periode hari
        
        Returns:
            Data conversion rate
        """
        print(f'[Analytics] Menghitung conversion rate...')
        
        # Ambil data produk (visits)
        products = list_products(page=1, page_size=100)
        
        if 'error' in products:
            return products
        
        total_visits = sum(int(p.get('visit_count', 0)) for p in products.get('data', []))
        
        # Ambil data order
        start_date = (datetime.now() - timedelta(days=period_days)).strftime('%Y-%m-%d')
        orders = list_orders(start_time=f'{start_date} 00:00:00')
        
        if 'error' in orders:
            return orders
        
        total_orders = len(orders.get('data', []))
        
        # Hitung conversion
        conversion_rate = (total_orders / total_visits * 100) if total_visits > 0 else 0
        
        result = {
            'period_days': period_days,
            'total_visits': total_visits,
            'total_orders': total_orders,
            'conversion_rate': conversion_rate,
            'benchmark': {
                'excellent': conversion_rate >= 5,
                'good': conversion_rate >= 2,
                'average': conversion_rate >= 1,
                'needs_improvement': conversion_rate < 1
            },
            'generated_at': datetime.now().isoformat()
        }
        
        print(f'[Analytics] ✓ Conversion rate: {conversion_rate:.2f}%')
        
        return result
    
    def get_hourly_distribution(self, period_days: int = 7) -> Dict[str, Any]:
        """
        Analisis distribusi order per jam.
        
        Args:
            period_days: Periode hari
        
        Returns:
            Distribusi order per jam
        """
        print(f'[Analytics] Menganalisis distribusi order per jam...')
        
        start_date = (datetime.now() - timedelta(days=period_days)).strftime('%Y-%m-%d')
        orders = list_orders(start_time=f'{start_date} 00:00:00')
        
        if 'error' in orders:
            return orders
        
        # Hitung order per jam
        hourly_counts = {str(h).zfill(2): 0 for h in range(24)}
        
        for order in orders.get('data', []):
            order_time = order.get('created_at', '')
            
            if order_time:
                try:
                    hour = datetime.strptime(order_time, '%Y-%m-%d %H:%M:%S').strftime('%H')
                    hourly_counts[hour] += 1
                except:
                    pass
        
        # Find peak hours
        peak_hour = max(hourly_counts.items(), key=lambda x: x[1])
        
        result = {
            'period_days': period_days,
            'hourly_distribution': hourly_counts,
            'peak_hour': {
                'hour': peak_hour[0],
                'orders': peak_hour[1]
            },
            'recommendation': f'Jam ramai order: {peak_hour[0]}:00. Sebaiknya aktif chat pada jam ini.',
            'generated_at': datetime.now().isoformat()
        }
        
        print(f'[Analytics] ✓ Peak hour: {peak_hour[0]}:00 ({peak_hour[1]} orders)')
        
        return result
    
    def get_product_performance(self, goods_id: str, period_days: int = 30) -> Dict[str, Any]:
        """
        Analisis performa produk tertentu.
        
        Args:
            goods_id: ID produk
            period_days: Periode hari
        
        Returns:
            Performa produk
        """
        print(f'[Analytics] Menganalisis performa produk {goods_id}...')
        
        # Ambil data produk
        from scripts.akulaku_utils import get_product_detail, get_sku_stock
        
        product = get_product_detail(goods_id)
        
        if 'error' in product:
            return product
        
        stock = get_sku_stock(goods_id)
        
        # Ambil order untuk produk ini
        start_date = (datetime.now() - timedelta(days=period_days)).strftime('%Y-%m-%d')
        orders = list_orders(start_time=f'{start_date} 00:00:00')
        
        if 'error' in orders:
            return orders
        
        # Filter order untuk produk ini
        product_orders = [
            o for o in orders.get('data', [])
            if o.get('goods_id') == goods_id
        ]
        
        total_sold = sum(int(o.get('quantity', 1)) for o in product_orders)
        total_revenue = sum(float(o.get('total_amount', 0)) for o in product_orders)
        
        result = {
            'product_id': goods_id,
            'product_name': product.get('goods_name'),
            'current_price': product.get('price'),
            'current_stock': stock.get('data', [{}])[0].get('stock', 0) if stock.get('data') else 0,
            'period_days': period_days,
            'performance': {
                'total_orders': len(product_orders),
                'total_sold': total_sold,
                'total_revenue': total_revenue,
                'daily_average': total_sold / period_days
            },
            'generated_at': datetime.now().isoformat()
        }
        
        print(f'[Analytics] ✓ Performa produk:')
        print(f'  Total terjual: {total_sold}')
        print(f'  Total revenue: Rp {total_revenue:,.0f}')
        
        return result
    
    def export_dashboard(self, output_path: str) -> None:
        """Export dashboard ke JSON."""
        print(f'[Analytics] Exporting dashboard...')
        
        dashboard = {
            'generated_at': datetime.now().isoformat(),
            'daily_report': self.get_daily_report(),
            'top_products': self.get_top_products(limit=10),
            'conversion_rate': self.get_conversion_rate(),
            'hourly_distribution': self.get_hourly_distribution()
        }
        
        with open(output_path, 'w') as f:
            json.dump(dashboard, f, indent=2)
        
        print(f'[Analytics] ✓ Dashboard diexport ke {output_path}')
    
    def print_summary(self) -> None:
        """Print ringkasan performa."""
        print('\n' + '=' * 50)
        print('RINGKASAN PERFORMA TOKO')
        print('=' * 50)
        
        daily = self.get_daily_report()
        
        if 'error' not in daily:
            print(f'\n📅 Hari Ini ({daily["date"]}):')
            print(f'   Order: {daily["summary"]["total_orders"]}')
            print(f'   Revenue: Rp {daily["summary"]["total_revenue"]:,.0f}')
            print(f'   Rata-rata: Rp {daily["summary"]["average_order_value"]:,.0f}')
            
            if daily['top_products']:
                print(f'\n🏆 Produk Terlaris:')
                for i, p in enumerate(daily['top_products'][:5], 1):
                    print(f'   {i}. {p["name"]} ({p["orders"]} order)')
        
        conversion = self.get_conversion_rate()
        
        if 'error' not in conversion:
            print(f'\n📊 Conversion Rate: {conversion["conversion_rate"]:.2f}%')
            
            if conversion['benchmark']['excellent']:
                print('   Rating: ⭐ Excellent!')
            elif conversion['benchmark']['good']:
                print('   Rating: 👍 Good')
            elif conversion['benchmark']['average']:
                print('   Rating: 👌 Average')
            else:
                print('   Rating: ⚠️ Needs Improvement')
        
        hourly = self.get_hourly_distribution()
        
        if 'error' not in hourly:
            print(f'\n⏰ Peak Hour: {hourly["peak_hour"]["hour"]}:00')
            print(f'   {hourly["recommendation"]}')
        
        print('\n' + '=' * 50)


def main():
    """Main function untuk testing."""
    if not setup_credentials():
        print('Error: API credentials not configured!')
        sys.exit(1)
    
    analytics = Analytics()
    
    print('=== Analytics Dashboard ===\n')
    
    # Print summary
    analytics.print_summary()
    
    # Export dashboard
    print('\nExporting dashboard...')
    analytics.export_dashboard('analytics_dashboard.json')
    
    print('\n✓ Analytics siap digunakan!')


if __name__ == '__main__':
    main()
