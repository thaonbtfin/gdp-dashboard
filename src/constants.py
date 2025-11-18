import os
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = PROJECT_DIR + "/data"
REPORTS_DIR = DATA_DIR + "/reports"

DATA_GDP = PROJECT_DIR + "/data/gdp_data.csv"
DATA_HISTORY = PROJECT_DIR + "/data/history_data.csv"

API_URL = "https://api.mocki.io/v2/12345678/stockdata"  # Replace with actual API URL

GIST_URL_SAMPLE_HISTORY = "https://gist.githubusercontent.com/thaonbtfin/fcb2906734735389faa0d32c8b47d456/raw/5dcc232d24f45b95e388e334c3ceeddc874752e9/sample_history_stockData.csv"
GIST_URL_TH_HISTORY="https://gist.githubusercontent.com/thaonbtfin/702773bb825afd63553f515b61645e8b/raw/8fe2a6cfe9cb5db792eabf07bf0d61d7f525b5c0/TH_toGoogleSheet.csv"
GIST_URL_DH_HISTORY="https://gist.githubusercontent.com/thaonbtfin/4c3a7018a1058d5f1e31fcf91d2367a9/raw/6205af6e9522710c4e88c80cbe234c1592fa5d05/DH_toGoogleSheet.csv"

# location
TEMP_DIR = os.path.join(PROJECT_DIR, '.temp')
DEFAULT_OUTPUT_DIR = os.path.join(PROJECT_DIR, 'data')
DEFAULT_USE_SUB_DIR = True

# Default values for fetching stock data
DEFAULT_SYMBOL = 'ACB'
DEFAULT_SOURCE = 'VCI'
DEFAULT_START_DATE = '2024-12-01'
DEFAULT_END_DATE = '2024-12-31'

# For calculating profit rate
DEFAULT_PERIOD = 1251   # Default period for calculating profit rate, in days
DEFAULT_INVESTMENT_AMOUNT = 100000000  # Default investment amount in VND
DEFAULT_INFLATION_RATE_PERCENTAGE = 3.5  # Default inflation rate in percentage

# Portfolio
# Sample
SYMBOLS = ['ACB', 'FPT']

# BizUni
SYMBOLS_BIZUNI_NOW = [
    'VNINDEX',
    'ACB', 'BID', 'BMP', 'BWE', 'CMG', 'CTG', 'CTR', 'DBD', 'DGC', 'DGW', 
    'DPG', 'FPT', 'FRT', 'GMD', 'HDG', 'HPG', 'IJC', 'MBB', 'MWG', 'PNJ', 
    'PTB', 'QNS', 'REE', 'SIP', 'SSI', 'TCB', 'TLG', 'TPB', 'VCB', 'VGC', 
    'VHC', 'VIB'
]
SYMBOLS_BIZUNI_OLD = [
    'VNINDEX',
    'ACB', 'AST', 'BCM', 'BID', 'BMP', 'BWE', 'CMG', 'CTG', 'CTR', 'DBD', 
    'DGC', 'DGW', 'DPG', 'FMC', 'FPT', 'FRT', 'GMD', 'HAX', 'HCM', 'HDB', 
    'HDG', 'HPG', 'HVN', 'IDC', 'IJC', 'LHG', 'MBB', 'MSH', 'MSN', 'MWG', 
    'NTP', 'PNJ', 'PTB', 'PVS', 'QNS', 'QTP', 'REE', 'SIP', 'SSI', 'TCB', 
    'TCM', 'TLG', 'TNG', 'TPB', 'VCB', 'VGC', 'VHC', 'VIB'
]

# BizUni - Long term
SYMBOLS_BIZUNI_DH = [
    'VNINDEX',
    'ACB', 'BID', 'BMP', 'BWE', 'CMG', 'CTG', 'CTR', 'DBD', 'DGC', 'DGW', 
    'DPG', 'FPT', 'FRT', 'GMD', 'HDG', 'HPG', 'IJC', 'MBB', 'MWG', 'PNJ', 
    'PTB', 'QNS', 'REE', 'SIP', 'SSI', 'TCB', 'TLG', 'TPB', 'VCB', 'VGC', 
    'VHC', 'VIB'
]

# Dai han
SYMBOLS_DH = [
    'VNINDEX',
    'ACB', 'DGC', 'DGW', 'DHC', 'FMC', 'FPT', 'FRT', 'GIL', 'HDG','HPG',
    'IDC', 'IDV', 'IJC', 'MBB', 'MWG', 'NTL', 'PDR', 'PNJ', 'PTB','PHR',
    'QNS', 'REE', 'SSI', 'TCB', 'THG', 'TNG', 'TPB', 'CTR', 'TVS','VCB',
    'VCI', 'VCS', 'BVB', 'VPB'
]

# Trung han
SYMBOLS_TH = [
    'VNINDEX',
    'ACB', 'FPT','HPG',
    'MBB', 'MWG','PNJ',
    'TCB',
    'BVB'
]

# VN30
SYMBOLS_VN30 = [
    'VNINDEX',
    'ACB', 'BCM', 'BID', 'BVH', 'CTG', 'FPT', 'GAS', 'GVR', 'HDB', 'HPG',
    'LPB', 'MBB', 'MSN', 'MWG', 'PLX', 'SAB', 'SHB', 'SSB', 'SSI', 'STB',
    'TCB', 'TPB', 'VCB', 'VHM', 'VIB', 'VIC', 'VJC', 'VNM', 'VPB', 'VRE'
]

# VN100
SYMBOLS_VN100 = [
    'VNINDEX',
    'AAA', 'ACB', 'ANV', 'BCM', 'BID', 'BMP', 'BSI', 'BVH', 'BWE', 'CII',
    'CMG', 'CTD', 'CTG', 'CTR', 'CTS', 'DBC', 'DCM', 'DGC', 'DGW', 'DIG',
    'DPM', 'DSE', 'DXG', 'DXS', 'EIB', 'EVF', 'FPT', 'FRT', 'FTS', 'GAS',
    'GEX', 'GMD', 'GVR', 'HAG', 'HCM', 'HDB', 'HDC', 'HDG', 'HHV', 'HPG',
    'HSG', 'HT1', 'IMP', 'KBC', 'KDC', 'KDH', 'KOS', 'LPB', 'MBB', 'MSB',
    'MSN', 'MWG', 'NAB', 'NKG', 'NLG', 'NT2', 'OCB', 'PAN', 'PC1', 'PDR',
    'PHR', 'PLX', 'PNJ', 'POW', 'PPC', 'PTB', 'PVD', 'PVT', 'REE', 'SAB',
    'SBT', 'SCS', 'SHB', 'SIP', 'SJS', 'SSB', 'SSI', 'STB', 'SZC', 'TCB',
    'TCH', 'TLG', 'TPB', 'VCB', 'VCG', 'VCI', 'VGC', 'VHC', 'VHM', 'VIB',
    'VIC', 'VIX', 'VJC', 'VND', 'VNM', 'VPB', 'VPI', 'VRE', 'VSC', 'VTP'
]

# Portfolio - Static fallback (kept for backward compatibility)
PORTFOLIOS = {
    "VN30": SYMBOLS_VN30,
    "VN100": SYMBOLS_VN100,
    "LongTerm": SYMBOLS_DH,
    "MidTerm": SYMBOLS_TH
}

# Google Sheets configuration - Replace with your actual Google Sheets ID
# Example: https://docs.google.com/spreadsheets/d/1ABC123DEF456/export?format=csv&gid=0
GSHEET_PORTFOLIOS_URL = "https://docs.google.com/spreadsheets/d/1TMMwSp3x0F-6cwq2F8uX1sbD0ytFNu5ACJUobFnkMqA/export?format=csv&gid=0"