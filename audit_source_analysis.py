import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
from bs4 import BeautifulSoup

source_path = '0Km CRI.I. 26-172 Particle In Z Hole (M&M) ........17 - Project Report.html'
with open(source_path, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("=== SOURCE DOCUMENT AUDIT ===")
print("File size:", len(html), "bytes")
tables = soup.find_all('table')
print(f"Total <table> elements in source: {len(tables)}")
imgs = soup.find_all('img')
print(f"Total <img> elements in source: {len(imgs)}")

# Audit headings
h_tags = soup.find_all(['h1','h2','h3','h4','h5','h6'])
print(f"Total headings in source: {len(h_tags)}")

sections = []
for h in h_tags:
    div = h.find_parent('div')
    # Direct tables in this div before any child div
    direct_tables = []
    direct_imgs = []
    if div:
        for c in div.children:
            if getattr(c, 'name', None) == 'table':
                direct_tables.append(c)
            elif getattr(c, 'name', None) == 'img':
                direct_imgs.append(c)
            elif getattr(c, 'name', None) == 'div':
                pass # child section
    sections.append({
        'tag': h.name,
        'title': h.get_text(strip=True),
        'classes': h.get('class', []),
        'all_tables': len(div.find_all('table')) if div else 0,
        'all_imgs': len(div.find_all('img')) if div else 0
    })

print("\n--- Sections Breakdown ---")
for s in sections:
    print(f"{s['tag'].upper()} | {s['title'][:40]:40s} | Tables: {s['all_tables']} | Images: {s['all_imgs']}")

# Audit Quant Results Summary tables vs Individual Quant tables
print("\n--- Quant Results Summary Tables vs Individual Quant Tables ---")
summary_tables = []
individual_quant_tables = []
details_tables = []

for idx, tbl in enumerate(tables):
    div = tbl.find_parent('div')
    first_h = div.find(['h1','h2','h3','h4','h5','h6']) if div else None
    title = first_h.get_text(strip=True) if first_h else 'Unknown'
    trs = tbl.find_all('tr')
    headers = [th.get_text(strip=True) for th in tbl.find_all('th')]
    if not headers and trs:
        headers = [td.get_text(strip=True) for td in trs[0].find_all('td')]
    
    if 'Quant Results Summary' in title:
        summary_tables.append((idx+1, title, len(trs), headers))
    elif 'Quant Results' in title:
        individual_quant_tables.append((idx+1, title, len(trs), headers))
    elif 'Details' in title:
        details_tables.append((idx+1, title, len(trs), headers))

print(f"Quant Results Summary Tables found: {len(summary_tables)}")
for st in summary_tables:
    print(" ", st)

print(f"Individual Quant Results Tables found: {len(individual_quant_tables)}")
for iqt in individual_quant_tables:
    print(" ", iqt)

print(f"Details Tables found: {len(details_tables)}")
for dt in details_tables:
    print(" ", dt)
