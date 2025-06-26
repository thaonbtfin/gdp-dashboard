import requests
from bs4 import BeautifulSoup
import re

def test_cafef_data(symbol="FPT"):
    url = f"https://cafef.vn/du-lieu/hose/{symbol.lower()}-cong-ty-co-phan-{symbol.lower()}.chn"
    
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Tìm các thông số tài chính
        data = {}
        
        # P/E ratio
        pe_elements = soup.find_all(text=re.compile(r'P/E\s*:'))
        if pe_elements:
            for elem in pe_elements:
                parent = elem.parent
                if parent and parent.next_sibling:
                    pe_text = str(parent.next_sibling).strip()
                    pe_match = re.search(r'[\d,\.]+', pe_text)
                    if pe_match:
                        data['P/E'] = pe_match.group()
        
        # P/B ratio
        pb_elements = soup.find_all(text=re.compile(r'P/B\s*:'))
        if pb_elements:
            for elem in pb_elements:
                parent = elem.parent
                if parent and parent.next_sibling:
                    pb_text = str(parent.next_sibling).strip()
                    pb_match = re.search(r'[\d,\.]+', pb_text)
                    if pb_match:
                        data['P/B'] = pb_match.group()
        
        # EPS
        eps_elements = soup.find_all(text=re.compile(r'EPS.*nghìn đồng'))
        if eps_elements:
            data['EPS_found'] = len(eps_elements)
        
        # Vốn hóa
        market_cap = soup.find_all(text=re.compile(r'Vốn hóa'))
        if market_cap:
            data['Market_Cap_found'] = len(market_cap)
        
        # Doanh thu
        revenue = soup.find_all(text=re.compile(r'Doanh thu'))
        if revenue:
            data['Revenue_found'] = len(revenue)
        
        # Lợi nhuận
        profit = soup.find_all(text=re.compile(r'Lợi nhuận'))
        if profit:
            data['Profit_found'] = len(profit)
        
        # ROE (có thể trong báo cáo tài chính)
        roe = soup.find_all(text=re.compile(r'ROE|Return on Equity'))
        if roe:
            data['ROE_found'] = len(roe)
        
        print(f"=== Kết quả crawl {symbol} từ CafeF ===")
        for key, value in data.items():
            print(f"{key}: {value}")
        
        # Kiểm tra các link báo cáo tài chính
        financial_links = soup.find_all('a', href=re.compile(r'bao-cao-tai-chinh|financial'))
        print(f"\nSố link báo cáo tài chính tìm thấy: {len(financial_links)}")
        
        return data
        
    except Exception as e:
        print(f"Lỗi khi crawl {symbol}: {e}")
        return {}

if __name__ == "__main__":
    test_cafef_data("FPT")