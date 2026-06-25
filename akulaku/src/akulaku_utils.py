#!/usr/bin/env python3
"""
Akulaku Open Platform API Utilities
Core functions for authentication, API calls, and common operations.
"""

import os
import hashlib
import hmac
import time
import json
import requests
from typing import Dict, Any, Optional
from datetime import datetime

# Configuration from environment variables
AKULAKU_APP_KEY = os.getenv('AKULAKU_APP_KEY', '')
AKULAKU_APP_SECRET=os.get...ET', '')
AKULAKU_API_BASE = os.getenv('AKULAKU_API_BASE', 'https://open.akulaku.com/api')


def generate_sign(app_secret: str, params: Dict[str, Any]) -> str:
    """
    Generate HMAC-SHA256 signature for Akulaku API authentication.
    
    Args:
        app_secret: Application secret key
        params: Dictionary of API parameters (excluding 'sign')
    
    Returns:
        Hex string of HMAC-SHA256 signature
    """
    # Sort parameters alphabetically
    sorted_params = sorted(params.items())
    
    # Create sign string: key1=value1&key2=value2
    sign_string = '&'.join([f'{k}={v}' for k, v in sorted_params])
    
    # Generate HMAC-SHA256
    signature = hmac.new(
        app_secret.encode('utf-8'),
        sign_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return signature


def get_timestamp() -> str:
    """Get current timestamp in milliseconds."""
    return str(int(time.time() * 1000))


def build_params(**kwargs) -> Dict[str, Any]:
    """
    Build API parameters with authentication.
    
    Args:
        **kwargs: Additional parameters for the API call
    
    Returns:
        Complete parameter dictionary with app_key, timestamp, and sign
    """
    params = {
        'app_key': AKULAKU_APP_KEY,
        'timestamp': get_timestamp(),
    }
    params.update(kwargs)
    
    # Generate signature
    params['sign'] = generate_sign(AKULAKU_APP_SECRET, params)
    
    return params


def api_get(endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Make GET request to Akulaku API.
    
    Args:
        endpoint: API endpoint (e.g., '/goods/list')
        params: Additional parameters
    
    Returns:
        JSON response from API
    """
    url = f'{AKULAKU_API_BASE}{endpoint}'
    
    if params is None:
        params = build_params()
    else:
        params = build_params(**params)
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {'error': str(e), 'status': 'failed'}


def api_post(endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Make POST request to Akulaku API.
    
    Args:
        endpoint: API endpoint (e.g., '/goods/publish')
        data: Request body data
    
    Returns:
        JSON response from API
    """
    url = f'{AKULAKU_API_BASE}{endpoint}'
    
    params = build_params()
    
    if data is None:
        data = {}
    data.update(params)
    
    try:
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {'error': str(e), 'status': 'failed'}


# =============================================================================
# Category API
# =============================================================================

def get_categories() -> Dict[str, Any]:
    """Get all product categories."""
    return api_get('/category/list')


def get_category_tree() -> Dict[str, Any]:
    """Get category tree structure."""
    return api_get('/category/tree')


# =============================================================================
# Goods API (Products)
# =============================================================================

def list_products(page: int = 1, page_size: int = 50) -> Dict[str, Any]:
    """List all products with pagination."""
    return api_get('/goods/list', {
        'page': str(page),
        'page_size': str(page_size)
    })


def get_product_detail(goods_id: str) -> Dict[str, Any]:
    """Get detailed product information."""
    return api_get('/goods/detail', {'goods_id': goods_id})


def get_sku_stock(goods_id: str) -> Dict[str, Any]:
    """Get stock information for all SKUs of a product."""
    return api_get('/goods/sku/stock', {'goods_id': goods_id})


def get_sku_detail(sku_id: str) -> Dict[str, Any]:
    """Get details for a specific SKU."""
    return api_get('/goods/sku/detail', {'sku_id': sku_id})


def update_product(goods_id: str, **kwargs) -> Dict[str, Any]:
    """Update product information."""
    data = {'goods_id': goods_id}
    data.update(kwargs)
    return api_post('/goods/update', data)


def update_stock(goods_id: str, sku_id: str, stock: int) -> Dict[str, Any]:
    """Update stock for a specific SKU."""
    return api_post('/goods/stock/update', {
        'goods_id': goods_id,
        'sku_id': sku_id,
        'stock': str(stock)
    })


def update_price(goods_id: str, sku_id: str, price: float) -> Dict[str, Any]:
    """Update price for a specific SKU."""
    return api_post('/goods/price/update', {
        'goods_id': goods_id,
        'sku_id': sku_id,
        'price': str(price)
    })


def update_status(goods_id: str, status: str) -> Dict[str, Any]:
    """Update product status (active/inactive)."""
    return api_post('/goods/status/update', {
        'goods_id': goods_id,
        'status': status
    })


def upload_image(image_path: str) -> Dict[str, Any]:
    """Upload a product image."""
    url = f'{AKULAKU_API_BASE}/goods/image/upload'
    params = build_params()
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, params=params, files=files, timeout=60)
    
    return response.json()


def batch_upload_images(image_paths: list) -> Dict[str, Any]:
    """Upload multiple product images."""
    url = f'{AKULAKU_API_BASE}/goods/image/batch-upload'
    params = build_params()
    
    files = [('file', open(path, 'rb')) for path in image_paths]
    
    try:
        response = requests.post(url, params=params, files=files, timeout=120)
        return response.json()
    finally:
        for _, f in files:
            f.close()


def init_publish() -> Dict[str, Any]:
    """Initialize product publish (get required fields)."""
    return api_post('/goods/publish/init')


def publish_product(product_data: Dict[str, Any]) -> Dict[str, Any]:
    """Publish a new product."""
    return api_post('/goods/publish', product_data)


# =============================================================================
# Order API
# =============================================================================

def list_orders(
    status: str = None,
    page: int = 1,
    page_size: int = 50,
    start_time: str = None,
    end_time: str = None
) -> Dict[str, Any]:
    """List orders with optional filters."""
    params = {
        'page': str(page),
        'page_size': str(page_size)
    }
    if status:
        params['status'] = status
    if start_time:
        params['start_time'] = start_time
    if end_time:
        params['end_time'] = end_time
    
    return api_get('/order/list', params)


def get_order_detail(order_id: str) -> Dict[str, Any]:
    """Get detailed order information."""
    return api_get('/order/detail', {'order_id': order_id})


def accept_order(order_id: str) -> Dict[str, Any]:
    """Accept an order."""
    return api_post('/order/accept', {'order_id': order_id})


def reject_order(order_id: str, reason: str = '') -> Dict[str, Any]:
    """Reject an order."""
    data = {'order_id': order_id}
    if reason:
        data['reason'] = reason
    return api_post('/order/reject', data)


def close_order(order_id: str) -> Dict[str, Any]:
    """Close an order."""
    return api_post('/order/close', {'order_id': order_id})


def cancel_order(order_id: str, reason: str = '') -> Dict[str, Any]:
    """Cancel an order."""
    data = {'order_id': order_id}
    if reason:
        data['reason'] = reason
    return api_post('/order/cancel', data)


# =============================================================================
# Logistics API
# =============================================================================

def get_logistics_info(order_id: str) -> Dict[str, Any]:
    """Get logistics/shipping information for an order."""
    return api_get('/logistics/info', {'order_id': order_id})


def update_tracking(order_id: str, tracking_number: str, courier: str) -> Dict[str, Any]:
    """Update tracking number for an order."""
    return api_post('/logistics/tracking', {
        'order_id': order_id,
        'tracking_number': tracking_number,
        'courier': courier
    })


# =============================================================================
# Shop API
# =============================================================================

def get_shop_info() -> Dict[str, Any]:
    """Get shop information."""
    return api_get('/shop/info')


def update_shop(**kwargs) -> Dict[str, Any]:
    """Update shop settings."""
    return api_post('/shop/update', kwargs)


# =============================================================================
# Utility Functions
# =============================================================================

def load_products_from_csv(csv_path: str) -> list:
    """
    Load products from CSV file.
    
    Expected CSV format:
    name,category_id,price,stock,description,image_urls
    """
    import csv
    products = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            products.append({
                'name': row['name'],
                'category_id': row['category_id'],
                'price': row['price'],
                'stock': row['stock'],
                'description': row['description'],
                'image_urls': row['image_urls'].split(',') if row.get('image_urls') else []
            })
    
    return products


def bulk_upload_products(csv_path: str, delay: float = 1.0) -> Dict[str, Any]:
    """
    Bulk upload products from CSV file.
    
    Args:
        csv_path: Path to CSV file
        delay: Delay between uploads (seconds) to avoid rate limiting
    
    Returns:
        Summary of upload results
    """
    products = load_products_from_csv(csv_path)
    results = {
        'total': len(products),
        'success': 0,
        'failed': 0,
        'errors': []
    }
    
    for i, product in enumerate(products, 1):
        print(f'[{i}/{len(products)}] Uploading: {product["name"]}')
        
        try:
            result = publish_product(product)
            if 'error' not in result:
                results['success'] += 1
                print(f'  ✓ Success')
            else:
                results['failed'] += 1
                results['errors'].append({
                    'product': product['name'],
                    'error': result.get('error', 'Unknown error')
                })
                print(f'  ✗ Failed: {result.get("error")}')
        except Exception as e:
            results['failed'] += 1
            results['errors'].append({
                'product': product['name'],
                'error': str(e)
            })
            print(f'  ✗ Exception: {e}')
        
        # Rate limiting
        if i < len(products):
            time.sleep(delay)
    
    return results


def export_orders_to_csv(orders: list, output_path: str) -> None:
    """Export orders to CSV file."""
    import csv
    
    if not orders:
        print('No orders to export')
        return
    
    fieldnames = orders[0].keys()
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(orders)
    
    print(f'Exported {len(orders)} orders to {output_path}')


def setup_credentials(app_key: str = None, app_secret: str = None):
    """
    Set up API credentials.
    
    Can be passed as arguments or set via environment variables:
    - AKULAKU_APP_KEY
    - AKULAKU_APP_SECRET
    """
    global AKULAKU_APP_KEY, AKULAKU_APP_SECRET
    
    if app_key:
        AKULAKU_APP_KEY = app_key
    elif os.getenv('AKULAKU_APP_KEY'):
        AKULAKU_APP_KEY = os.getenv('AKULAKU_APP_KEY')
    
    if app_secret:
        AKULAKU_APP_SECRET=***    elif os.getenv('AKULAKU_APP_SECRET'):
        AKULAKU_APP_SECRET=os.get...')
    
    if not AKULAKU_APP_KEY or not AKULAKU_APP_SECRET:
        print('Warning: API credentials not configured!')
        print('Set via environment variables or call setup_credentials()')
        return False
    
    return True


# =============================================================================
# Main (for testing)
# =============================================================================

if __name__ == '__main__':
    # Test configuration
    print('Akulaku API Utilities')
    print('=' * 50)
    print(f'App Key: {"*" * 8 if AKULAKU_APP_KEY else "Not set"}')
    print(f'App Secret: {"*" * 8 if AKULAKU_APP_SECRET else "Not set"}')
    print(f'API Base: {AKULAKU_API_BASE}')
    print()
    
    # Test signature generation
    test_params = {
        'app_key': 'test_key',
        'timestamp': '1234567890',
        'page': '1'
    }
    test_sign = generate_sign('test_secret', test_params)
    print(f'Test Signature: {test_sign}')
    print()
    
    # Quick connectivity test
    if setup_credentials():
        print('Testing API connection...')
        result = get_shop_info()
        if 'error' not in result:
            print('✓ API connection successful!')
        else:
            print(f'✗ API connection failed: {result.get("error")}')
