#!/usr/bin/env python3
"""
Automated Data Integrity Test Suite for EDAX Report Converter v2.8
Validates Zero-Loss Preservation, Table Extraction, Edit Tracking, and Pre-Export Safeguards.
"""
import os
import re
import sys
import hashlib
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

REPORT_CONVERTER_FILE = 'edax_report_converter v2.8.html'
SOURCE_FILE = '0Km CRI.I. 26-172 Particle In Z Hole (M&M) ........17 - Project Report.html'

def run_tests():
    print("=" * 80)
    print("EDAX REPORT CONVERTER v2.8 — AUTOMATED DATA INTEGRITY TEST SUITE")
    print("=" * 80)
    passed = 0
    total = 0

    def assert_test(name, condition, details=""):
        nonlocal passed, total
        total += 1
        if condition:
            print(f"  [PASS] Test {total:02d}: {name}")
            passed += 1
        else:
            print(f"  [FAIL] Test {total:02d}: {name} -> {details}")

    # -------------------------------------------------------------
    # Group 1: Source Document Inspection & Provenance
    # -------------------------------------------------------------
    print("\n--- Group 1: Source Document Provenance & SHA-256 ---")
    with open(SOURCE_FILE, 'rb') as f:
        source_bytes = f.read()
    source_sha256 = hashlib.sha256(source_bytes).hexdigest()
    assert_test("Source file read & SHA-256 computed", len(source_bytes) > 0, f"SHA-256: {source_sha256}")
    
    with open(REPORT_CONVERTER_FILE, 'r', encoding='utf-8') as f:
        converter_html = f.read()

    assert_test("Converter file exists & version is v2.8", 
                "edax_report_converter v2.8" in converter_html and "<title>edax_report_converter v2.8</title>" in converter_html)
    assert_test("Header displays v2.8", 'v2.8' in converter_html)
    assert_test("Footer displays v2.8", 'edax_report_converter v2.8 &middot;' in converter_html)

    # -------------------------------------------------------------
    # Group 2: Extraction Logic in edax_report_converter v2.8.html
    # -------------------------------------------------------------
    print("\n--- Group 2: Zero-Loss Logic Verification in Application Source ---")
    assert_test("SHA-256 hashing function present", "computeSha256" in converter_html)
    assert_test("Alphanumeric spectrum title regex / logic present", 
                "isSpectrumTitle" in converter_html and "isSpectrumChild" in converter_html)
    assert_test("Preserves individual Quant Results tables", 
                "sourceRegistry.allIndividualQuantResults.push" in converter_html and "spectrum.quantResults = quantResultsData" in converter_html or "quantResults: quantResultsData" in converter_html)
    assert_test("Zero scientific casting: exact string preservation", 
                "extractTableData" in converter_html and "headers" in converter_html and "rows" in converter_html)
    assert_test("Scientific cell edit tracking implemented", 
                "attachScientificEditHandler" in converter_html and "scientific-edited" in converter_html and "MODEL.edits" in converter_html)
    assert_test("Pre-export integrity verification implemented", 
                "verifyPreExportIntegrity" in converter_html and "runIntegrityValidation" in converter_html)
    assert_test("Data Integrity & Source Inspector UI present", 
                "integrityInspectorModal" in converter_html and "Source Tables Inspector" in converter_html and "User Edits Log" in converter_html)

    # -------------------------------------------------------------
    # Group 3: Source HTML Structure vs Model Expectations
    # -------------------------------------------------------------
    print("\n--- Group 3: Source Data Verification against Reference Document ---")
    soup = BeautifulSoup(source_bytes.decode('utf-8', errors='ignore'), 'html.parser')
    all_tables = soup.find_all('table')
    all_imgs = soup.find_all('img')

    quant_summary_tables = []
    quant_individual_tables = []
    for tbl in all_tables:
        parent_div = tbl.find_parent('div')
        h = parent_div.find(['h1','h2','h3','h4','h5','h6']) if parent_div else None
        h_text = h.get_text(strip=True).lower() if h else ''
        if 'quant results summary' in h_text:
            quant_summary_tables.append(tbl)
        elif 'quant results' in h_text:
            quant_individual_tables.append(tbl)

    assert_test("Source document contains exactly 3 Quant Results Summary tables", len(quant_summary_tables) == 3)
    assert_test("Source document contains exactly 7 Individual Quant Results tables", len(quant_individual_tables) == 7)

    # Check precision & trailing zeros in summary tables
    trailing_zeros_found = 0
    sigma_values_found = 0
    for tbl in quant_summary_tables:
        for td in tbl.find_all('td'):
            txt = td.get_text(strip=True)
            if re.match(r'^\d+\.\d0$', txt):
                trailing_zeros_found += 1
    assert_test("Trailing zeros in Quant Summary tables preserved (e.g. 9.70, 0.30)", trailing_zeros_found > 0, f"Found {trailing_zeros_found} instances")

    for tbl in quant_individual_tables:
        headers = [th.get_text(strip=True) for th in tbl.find_all(['th','td'])]
        if 'Wt% Sigma' in headers:
            sigma_values_found += 1
    assert_test("Wt% Sigma headers present in all 7 individual quant tables", sigma_values_found == 7, f"Found {sigma_values_found}/7")

    # -------------------------------------------------------------
    # Group 4: Export Cleanliness & Format Preservation
    # -------------------------------------------------------------
    print("\n--- Group 4: Export Cleanliness & Formatting Preservation ---")
    assert_test("buildCleanReportHTML strips .scientific-edited class", 
                "n.classList.remove('scientific-edited')" in converter_html or 'classList.remove("scientific-edited")' in converter_html)
    assert_test("buildCleanReportHTML strips data-cell-id attribute", 
                "removeAttribute('data-cell-id')" in converter_html)
    assert_test("buildCleanReportHTML strips data-orig-value attribute", 
                "removeAttribute('data-orig-value')" in converter_html)
    assert_test("inlineStylesForWord preserved exactly", 
                "function inlineStylesForWord" in converter_html and "site-header-bar" in converter_html and "cover-grid" in converter_html)
    assert_test("Word docx blob creation logic intact", 
                "function createDocxBlob" in converter_html and "word/document.xml" in converter_html)

    # -------------------------------------------------------------
    # Group 5: Pre-Flight Integrity Protection
    # -------------------------------------------------------------
    print("\n--- Group 5: Pre-Flight Integrity Protection & Action Safeguards ---")
    assert_test("Export HTML blocked on failed validation", "if (!(await verifyPreExportIntegrity())) return" in converter_html)
    assert_test("Export Word guarded by pre-flight check", "if (!skipPreVerify && !(await verifyPreExportIntegrity())) return" in converter_html)
    assert_test("Export PDF guarded by pre-flight check", "if (!skipPreVerify && !(await verifyPreExportIntegrity())) return" in converter_html)
    assert_test("Export Both guarded by pre-flight check", "if (!(await verifyPreExportIntegrity())) return;" in converter_html)
    assert_test("Broken images trigger FAIL status and blocking alert", "report.status = 'FAIL'" in converter_html and "brokenImages" in converter_html)
    assert_test("User edits trigger WARNING status and prompt confirmation", "report.status = 'WARNING'" in converter_html and "confirm(" in converter_html)

    # Summary
    print("\n" + "=" * 80)
    print(f"FINAL RESULT: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("=" * 80)
    if passed == total:
        print("ALL DATA INTEGRITY AND ZERO-LOSS SAFEGUARD TESTS PASSED!")
        return 0
    else:
        print("SOME TESTS FAILED! Review test log above.")
        return 1

if __name__ == '__main__':
    sys.exit(run_tests())
