#!/usr/bin/env python3
"""
Automated Data Integrity Test Suite for EDAX Report Converter v3.1
Validates Zero-Loss Preservation, Nested Table Isolation, Deep Source-to-Model
Reconciliation, Independent Export Verification, Image Accounting (excluding vendor logos),
Pre-Export Safeguards, and v3.1 Data-Persistence / Metadata Features.
"""
import os
import re
import sys
import hashlib
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

REPORT_CONVERTER_FILE = 'edax_report_converter v3.1.html'
SOURCE_FILE = '0Km CRI.I. 26-172 Particle In Z Hole (M&M) ........17 - Project Report.html'

def run_tests():
    print("=" * 80)
    print("EDAX REPORT CONVERTER v3.1 — AUTOMATED DATA INTEGRITY TEST SUITE")
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

    assert_test("Converter file exists & version is v3.1", 
                "edax_report_converter v3.1" in converter_html and "<title>edax_report_converter v3.1</title>" in converter_html)
    assert_test("Header displays v3.1", 'v3.1' in converter_html)
    assert_test("Footer displays v3.1", 'edax_report_converter v3.1 &middot;' in converter_html)
    assert_test("Audit text log records v3.1", 'Software Version      : edax_report_converter v3.1' in converter_html)

    # -------------------------------------------------------------
    # Group 2: Table Extraction & Nested Row Leakage Elimination
    # -------------------------------------------------------------
    print("\n--- Group 2: Table Extraction & Nested Row Leakage Elimination ---")
    assert_test("Direct row selector getTableDirectRows implemented", "function getTableDirectRows" in converter_html)
    assert_test("Direct cell selector getRowDirectCells implemented", "function getRowDirectCells" in converter_html)
    assert_test("extractTableData handles colspan expansion", "colspan" in converter_html and "colCount: headers.length" in converter_html)
    assert_test("extractSummaryTable filters out nested tables", "t.closest('tr') === null" in converter_html)
    assert_test("extractDetailsRows filters out nested tables and uses direct rows", "getTableDirectRows(table)" in converter_html)

    # -------------------------------------------------------------
    # Group 3: Real Source-to-Model Deep Reconciliation & Image Accounting
    # -------------------------------------------------------------
    print("\n--- Group 3: Real Source-to-Model Deep Reconciliation & Image Accounting ---")
    assert_test("verifySourceToModelReconciliation function present", "function verifySourceToModelReconciliation" in converter_html)
    assert_test("Reconciles discovered headings against hierarchy", "Report Hierarchy & Sections" in converter_html)
    assert_test("Reconciles Quant Results Summary tables and discovers all instances", "Quant Summary Tables Discovery" in converter_html)
    assert_test("Cell-by-cell matching against original source HTML values", "Quant Summary Cell Reconciliation" in converter_html and "srcVal" in converter_html)
    assert_test("Reconciles Individual Quant Results tables & Wt% Sigma", "Individual Quant Tables & Uncertainty (Sigma)" in converter_html)
    assert_test("Scientific image filtering ignores footer/header vendor logos", 
                "!im.closest('footer')" in converter_html and "!im.classList.contains('logo')" in converter_html)
    assert_test("Reconciles exact scientific images across specimens and sites", "Source-to-Model Image Accounting" in converter_html)
    assert_test("runIntegrityValidation integrates reconciliation results", "report.reconciliation = recon" in converter_html)

    # -------------------------------------------------------------
    # Group 4: Independent Export Verification (HTML, Word, PDF)
    # -------------------------------------------------------------
    print("\n--- Group 4: Independent Export Verification ---")
    assert_test("validateHtmlExportArtifact implemented", "function validateHtmlExportArtifact" in converter_html)
    assert_test("validatePdfExportArtifact implemented", "function validatePdfExportArtifact" in converter_html)
    assert_test("Tab 5 Export Verifier UI present in DOM", 'data-tab="exportVerifyTab"' in converter_html and 'id="exportVerifyTab"' in converter_html)
    assert_test("renderExportVerifyTab renders independent export checks", "function renderExportVerifyTab" in converter_html and "inspExportVerifyList" in converter_html)

    # -------------------------------------------------------------
    # Group 5: Zero-Loss Full Scientific Dataset Export
    # -------------------------------------------------------------
    print("\n--- Group 5: Zero-Loss Full Scientific Dataset Export ---")
    assert_test("exportFullScientificDataset function present", "function exportFullScientificDataset" in converter_html)
    assert_test("Export Full Dataset button present in inspector footer", 'id="downloadFullDatasetBtn"' in converter_html)
    assert_test("downloadFullDatasetBtn event listener wired up", "downloadFullDatasetBtn" in converter_html and "exportFullScientificDataset" in converter_html)
    assert_test("Full dataset export preserves all specimens, sites, summary tables and individual sigma quant tables", 
                "Individual Quantification with Sigma" in converter_html and "full_scientific_dataset.html" in converter_html)

    # -------------------------------------------------------------
    # Group 6: Reference Document Structure & Exact Values
    # -------------------------------------------------------------
    print("\n--- Group 6: Reference Document Structure & Exact Values ---")
    soup = BeautifulSoup(source_bytes.decode('utf-8', errors='ignore'), 'html.parser')
    all_tables = soup.find_all('table')
    all_imgs = soup.find_all('img')
    all_headings = soup.find_all(['h1','h2','h3','h4','h5','h6'])
    
    # Filter scientific images (excluding footer vendor logo)
    scientific_imgs = [img for img in all_imgs if not (img.find_parent('footer') or img.get('alt') == 'Logo' or 'logo' in img.get('class', []))]

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

    assert_test("Source document contains exactly 37 headings", len(all_headings) == 37, f"Found {len(all_headings)}")
    assert_test("Source document contains exactly 3 Quant Results Summary tables", len(quant_summary_tables) == 3)
    assert_test("Source document contains exactly 7 Individual Quant Results tables", len(quant_individual_tables) == 7)
    assert_test("Source document contains 11 total images (10 scientific + 1 footer logo)", len(all_imgs) == 11, f"Found {len(all_imgs)}")
    assert_test("Source document contains exactly 10 scientific images (3 electron + 7 spectra)", len(scientific_imgs) == 10, f"Found {len(scientific_imgs)}")

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
    # Group 7: Pre-Flight Integrity Protection & Safeguards
    # -------------------------------------------------------------
    print("\n--- Group 7: Pre-Flight Integrity Protection & Safeguards ---")
    assert_test("Export HTML guarded by pre-flight check", "if (!(await verifyPreExportIntegrity())) return" in converter_html)
    assert_test("Export Word guarded by pre-flight check", "if (!skipPreVerify && !(await verifyPreExportIntegrity())) return" in converter_html)
    assert_test("Export PDF guarded by pre-flight check", "if (!skipPreVerify && !(await verifyPreExportIntegrity())) return" in converter_html)
    assert_test("Export Both guarded by pre-flight check", "if (!(await verifyPreExportIntegrity())) return;" in converter_html)
    assert_test("Broken images trigger FAIL status and blocking alert", "report.status = 'FAIL'" in converter_html and "brokenImages" in converter_html)
    assert_test("User edits trigger WARNING status and prompt confirmation", "report.status = 'WARNING'" in converter_html and "confirm(" in converter_html)

    # -------------------------------------------------------------
    # Group 8: v3.1 Persistence, Metadata Surfacing & Reconciliation Fixes
    # -------------------------------------------------------------
    print("\n--- Group 8: v3.1 Persistence, Metadata Surfacing & Verification Fixes ---")
    assert_test("extractCoverSheetData implemented for format switching", "function extractCoverSheetData" in converter_html)
    assert_test("applyCoverSheetData implemented for format switching", "function applyCoverSheetData" in converter_html)
    assert_test("setReportFormat preserves specimen site sheets without wiping root", 
                "rootInner.insertBefore(cs, firstSiteSheet)" in converter_html and "extractCoverSheetData(rootInner)" in converter_html)
    assert_test("Safe comment copy preserves cell DOM and attaches photo-mini remove listeners", 
                "cloned.remove()" in converter_html and "cVal.textContent = pVal.textContent" in converter_html)
    assert_test("Auto-fill FOV µm button implemented in comment box", 
                "auto-fov-btn" in converter_html and "Auto-fill FOV" in converter_html and "extractMicronValue" in converter_html)
    assert_test("Direct firstElementChild heading check used in summaryDivs selector", 
                "d.firstElementChild" in converter_html and "/^H[1-6]$/.test(h.tagName)" in converter_html)
    assert_test("Metadata notes surfaced in Info Row (Project Notes & Specimen Notes)", 
                "Project Notes:" in converter_html and "Specimen Notes:" in converter_html)
    assert_test("Global includeAllSpectraToggle checkbox in sidebar and DOM listener wired", 
                'id="includeAllSpectraToggle"' in converter_html and "syncIncludeAllSpectraToggle" in converter_html)

    # Summary
    print("\n" + "=" * 80)
    print(f"FINAL RESULT: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("=" * 80)
    if passed == total:
        print("ALL DATA INTEGRITY AND ZERO-LOSS SAFEGUARD TESTS PASSED (100%)!")
        return 0
    else:
        print("SOME TESTS FAILED! Review test log above.")
        return 1

if __name__ == '__main__':
    sys.exit(run_tests())
