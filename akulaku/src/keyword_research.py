#!/usr/bin/env python3
"""
Akulaku Keyword Research Tool
Riset keyword trending dan generate judul SEO untuk produk Akulaku.
"""

import os
import sys
import json
import time
from typing import List, Dict, Any
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.akulaku_utils import setup_credentials, list_products, get_categories


class KeywordResearch:
    """Tool untuk riset keyword dan optimasi SEO produk Akulaku."""
    
    def __init__(self):
        self.trending_keywords = []
        self.category_keywords = {}
        
    def get_trending_keywords(self, category: str = None, limit: int = 50) -> List[str]:
        """
        Ambil keyword trending dari produk populer.
        
        Args:
            category: Filter by category (optional)
            limit: Jumlah keyword maksimal
        
        Returns:
            List keyword trending
        """
        print(f'[Keyword Research] Mencari keyword trending...')
        
        # Ambil produk populer
        products = list_products(page=1, page_size=100)
        
        if 'error' in products:
            print(f'[Error] {products["error"]}')
            return []
        
        # Ekstrak keyword dari judul produk
        all_words = []
        for product in products.get('data', []):
            title = product.get('goods_name', '')
            words = title.lower().split()
            # Filter kata pendek dan umum
            filtered_words = [w for w in words if len(w) > 2 and w not in ['dan', 'untuk', 'dengan', 'yang', 'ini', 'itu']]
            all_words.extend(filtered_words)
        
        # Hitung frekuensi keyword
        word_counts = Counter(all_words)
        
        # Ambil top keywords
        trending = [word for word, count in word_counts.most_common(limit)]
        
        self.trending_keywords = trending
        print(f'[Keyword Research] Ditemukan {len(trending)} keyword trending')
        
        return trending
    
    def generate_seo_title(self, keywords: List[str], product_name: str, max_length: int = 100) -> str:
        """
        Generate judul SEO dari keyword.
        
        Args:
            keywords: List keyword untuk digunakan
            product_name: Nama produk dasar
            max_length: Maksimal panjang judul
        
        Returns:
            Judul SEO yang dioptimasi
        """
        # Prioritas keyword (ambil top 5)
        priority_keywords = keywords[:5]
        
        # Buat judul dengan keyword
        title_parts = [product_name] + priority_keywords
        
        # Gabung dan potong jika terlalu panjang
        title = ' '.join(title_parts)
        if len(title) > max_length:
            title = title[:max_length-3] + '...'
        
        return title
    
    def generate_seo_description(self, keywords: List[str], base_description: str, product_features: List[str] = None) -> str:
        """
        Generate deskripsi SEO.
        
        Args:
            keywords: List keyword
            base_description: Deskripsi dasar
            product_features: Fitur produk (optional)
        
        Returns:
            Deskripsi SEO yang dioptimasi
        """
        # Mulai dengan deskripsi dasar
        description = base_description + '\n\n'
        
        # Tambah fitur produk
        if product_features:
            description += '✨ Fitur:\n'
            for feature in product_features:
                description += f'• {feature}\n'
            description += '\n'
        
        # Tambah keyword sebagai tag
        description += '🔍 Tag: ' + ', '.join(keywords[:10])
        
        return description
    
    def analyze_competitor_keywords(self, competitor_products: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Analisis keyword dari produk kompetitor.
        
        Args:
            competitor_products: List produk kompetitor
        
        Returns:
            Dictionary keyword dan frekuensi
        """
        all_words = []
        
        for product in competitor_products:
            title = product.get('name', '')
            words = title.lower().split()
            filtered_words = [w for w in words if len(w) > 2]
            all_words.extend(filtered_words)
        
        return dict(Counter(all_words).most_common(30))
    
    def get_keyword_suggestions(self, seed_keyword: str) -> List[str]:
        """
        Dapat suggestion keyword berdasarkan seed keyword.
        
        Args:
            seed_keyword: Keyword dasar
        
        Returns:
            List keyword suggestion
        """
        # Suffix dan prefix umum di Indonesia
        suffixes = ['murah', 'original', 'terbaru', 'premium', 'best seller', 'ready stock', 'garansi']
        prefixes = ['jual', 'beli', 'harga', 'promo', 'diskon', 'grosir']
        
        suggestions = []
        
        # Tambah suffix
        for suffix in suffixes:
            suggestions.append(f'{seed_keyword} {suffix}')
        
        # Tambah prefix
        for prefix in prefixes:
            suggestions.append(f'{prefix} {seed_keyword}')
        
        return suggestions
    
    def export_keywords_csv(self, keywords: List[str], output_path: str) -> None:
        """Export keyword ke CSV."""
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['keyword', 'suggested_title', 'suggested_tags'])
            
            for keyword in keywords:
                title = self.generate_seo_title([keyword], keyword)
                tags = ', '.join(self.get_keyword_suggestions(keyword)[:5])
                writer.writerow([keyword, title, tags])
        
        print(f'[Export] Keywords exported to {output_path}')


def main():
    """Main function untuk testing."""
    if not setup_credentials():
        print('Error: API credentials not configured!')
        sys.exit(1)
    
    kr = KeywordResearch()
    
    # Contoh penggunaan
    print('=== Keyword Research Tool ===\n')
    
    # 1. Get trending keywords
    print('1. Getting trending keywords...')
    trending = kr.get_trending_keywords(limit=20)
    print(f'Top 20 trending: {trending}\n')
    
    # 2. Generate SEO title
    print('2. Generating SEO title...')
    title = kr.generate_seo_title(trending, 'iPhone 15 Pro Max')
    print(f'SEO Title: {title}\n')
    
    # 3. Generate SEO description
    print('3. Generating SEO description...')
    desc = kr.generate_seo_description(
        trending[:5],
        'iPhone 15 Pro Max 256GB',
        ['Chip A17 Pro', 'Kamera 48MP', 'Titanium Design']
    )
    print(f'SEO Description:\n{desc}\n')
    
    # 4. Keyword suggestions
    print('4. Getting keyword suggestions...')
    suggestions = kr.get_keyword_suggestions('iphone')
    print(f'Suggestions for "iphone": {suggestions}\n')


if __name__ == '__main__':
    main()
