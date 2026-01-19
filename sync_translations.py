#!/usr/bin/env python3
"""
Script to synchronize translation structure between ID and EN documentation.
Ensures pagination, heading levels, numbering, and indentation match between ID and EN files.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Mapping between ID and EN folder/file names
PATH_MAPPING = {
    # Main folders
    'menu-siswa': 'student-menu',
    'menu-wali': 'guardian-menu',
    'penyelesaian-masalah': 'troubleshooting',
    'pengenalan': 'introduction',
    'kebijakan-dan-keamanan': 'policies-and-security',
    'panduan-pengguna-baru': 'new-user-guide',
    
    # Common subfolders
    'ujian': 'exams',
    'tugas': 'assignments',
    'nilai-ujian': 'exam-results',
    'biaya': 'fees',
    'laporan': 'reports',
    
    # Specific pages
    'ujian-online': 'online-exams',
    'ujian-offline': 'offline-exams',
    'ditugaskan': 'assigned',
    'dikumpulkan': 'submitted',
    'penugasan': 'assigned',
    'pengumpulan-tugas': 'submission',
    'tagihan': 'bill-list',
    'riwayat': 'payment-history',
    'ujian-daring': 'online-exams',
    
    'kehadiran-siswa': 'student-attendance',
    'kehadiran-anak': 'child-attendance',
    'jadwal-pelajaran-harian': 'daily-class-schedule',
    'jadwal-pelajaran-anak': 'child-class-schedule',
    'absen-mapel': 'subject-attendance',
    'ekstrakurikuler': 'extracurricular',
    'galeri': 'gallery',
    'hari-libur': 'holidays',
    'pengumuman': 'announcements',
    'profile-siswa': 'student-profile',
    'detail-wali': 'guardian-details',
    'guru': 'teachers',
    'mengajukan-izin-kehadiran': 'submit-attendance-permit',
    
    'pengerjaan-ujian-online': 'taking-online-exams',
    
    'hubungi-kami': 'contact-us',
    'keamanan': 'security',
    'kebijakan-privasi': 'privacy-policy',
    'syarat-dan-ketentuan-layanan': 'terms-of-service',
    'tentang-kami': 'about-us',
    
    'lupa-password': 'forgot-password',
    'masalah-user-tidak-bisa-login': 'user-cannot-login',
    
    'tampilan-eschool-mobile': 'eschool-mobile-interface',
    'gambaran-umum': 'overview',
    'login': 'login',
}

def get_en_path(id_path: str) -> str:
    """Convert ID path to EN path using mapping"""
    parts = Path(id_path).parts
    en_parts = []
    
    for part in parts:
        # Remove .mdx extension for mapping
        part_name = part.replace('.mdx', '')
        
        # Map to EN equivalent
        if part_name in PATH_MAPPING:
            en_part = PATH_MAPPING[part_name]
            # Add back .mdx if original had it
            if part.endswith('.mdx'):
                en_part += '.mdx'
            en_parts.append(en_part)
        else:
            en_parts.append(part)
    
    return str(Path(*en_parts))

def extract_frontmatter(content: str) -> Tuple[str, str]:
    """Extract frontmatter and body from markdown content"""
    lines = content.split('\n')
    
    if not lines or lines[0].strip() != '---':
        return '', content
    
    frontmatter_lines = ['---']
    body_start = 1
    
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            frontmatter_lines.append('---')
            body_start = i + 1
            break
        frontmatter_lines.append(lines[i])
    
    frontmatter = '\n'.join(frontmatter_lines)
    body = '\n'.join(lines[body_start:])
    
    return frontmatter, body

def analyze_structure(content: str) -> List[Dict]:
    """Analyze markdown structure and return list of elements with their properties"""
    lines = content.split('\n')
    structure = []
    
    in_code_block = False
    code_block_lang = ''
    
    for i, line in enumerate(lines):
        # Check for code blocks
        if line.strip().startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_block_lang = line.strip()[3:].strip()
                structure.append({
                    'type': 'code_block_start',
                    'line': i,
                    'content': line,
                    'lang': code_block_lang
                })
            else:
                in_code_block = False
                structure.append({
                    'type': 'code_block_end',
                    'line': i,
                    'content': line
                })
            continue
        
        if in_code_block:
            structure.append({
                'type': 'code_block_content',
                'line': i,
                'content': line
            })
            continue
        
        # Detect headings
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2)
            structure.append({
                'type': 'heading',
                'line': i,
                'level': level,
                'text': text,
                'content': line
            })
            continue
        
        # Detect numbered lists
        numbered_match = re.match(r'^(\s*)(\d+)\.\s+(.+)$', line)
        if numbered_match:
            indent = numbered_match.group(1)
            number = numbered_match.group(2)
            text = numbered_match.group(3)
            structure.append({
                'type': 'numbered_list',
                'line': i,
                'indent': len(indent),
                'number': number,
                'text': text,
                'content': line
            })
            continue
        
        # Detect bullet lists
        bullet_match = re.match(r'^(\s*)([\*\-\+])\s+(.+)$', line)
        if bullet_match:
            indent = bullet_match.group(1)
            bullet = bullet_match.group(2)
            text = bullet_match.group(3)
            structure.append({
                'type': 'bullet_list',
                'line': i,
                'indent': len(indent),
                'bullet': bullet,
                'text': text,
                'content': line
            })
            continue
        
        # Detect imports
        if line.strip().startswith('import '):
            structure.append({
                'type': 'import',
                'line': i,
                'content': line
            })
            continue
        
        # Detect horizontal rules
        if re.match(r'^[\*\-_]{3,}$', line.strip()):
            structure.append({
                'type': 'hr',
                'line': i,
                'content': line
            })
            continue
        
        # Everything else
        structure.append({
            'type': 'text',
            'line': i,
            'content': line
        })
    
    return structure

def generate_report(id_file: Path, en_file: Path, id_dir: Path, en_dir: Path) -> Tuple[str, bool]:
    """Generate a comparison report between ID and EN files. Returns (report, has_issues)"""
    
    # Read files
    id_content = id_file.read_text(encoding='utf-8')
    
    if not en_file.exists():
        rel_path = id_file.relative_to(id_dir)
        return f"\n[MISSING] {rel_path}\n  EN file not found: {en_file.relative_to(en_dir)}", True
    
    en_content = en_file.read_text(encoding='utf-8')
    
    # Extract frontmatter and body
    id_fm, id_body = extract_frontmatter(id_content)
    en_fm, en_body = extract_frontmatter(en_content)
    
    # Analyze structures
    id_structure = analyze_structure(id_body)
    en_structure = analyze_structure(en_body)
    
    # Count elements
    id_headings = [s for s in id_structure if s['type'] == 'heading']
    en_headings = [s for s in en_structure if s['type'] == 'heading']
    
    id_lists = [s for s in id_structure if s['type'] in ['numbered_list', 'bullet_list']]
    en_lists = [s for s in en_structure if s['type'] in ['numbered_list', 'bullet_list']]
    
    # Build report
    rel_path = id_file.relative_to(id_dir)
    report_lines = [f"\n[FILE] {rel_path}"]
    has_issues = False
    
    # Compare heading counts
    if len(id_headings) != len(en_headings):
        report_lines.append(f"  [WARNING] Headings mismatch: ID={len(id_headings)}, EN={len(en_headings)}")
        has_issues = True
    else:
        report_lines.append(f"  [OK] Headings: {len(id_headings)}")
    
    # Compare heading levels
    for i, (id_h, en_h) in enumerate(zip(id_headings, en_headings)):
        if id_h['level'] != en_h['level']:
            report_lines.append(f"    [WARNING] Heading {i+1} level mismatch: ID=H{id_h['level']}, EN=H{en_h['level']}")
            has_issues = True
    
    # Compare list counts
    if len(id_lists) != len(en_lists):
        report_lines.append(f"  [WARNING] List items mismatch: ID={len(id_lists)}, EN={len(en_lists)}")
        has_issues = True
    else:
        report_lines.append(f"  [OK] List items: {len(id_lists)}")
    
    # Compare list indentation
    indent_mismatches = 0
    for i, (id_l, en_l) in enumerate(zip(id_lists, en_lists)):
        if id_l.get('indent', 0) != en_l.get('indent', 0):
            indent_mismatches += 1
    
    if indent_mismatches > 0:
        report_lines.append(f"  [WARNING] {indent_mismatches} list items have different indentation")
        has_issues = True
    
    return '\n'.join(report_lines), has_issues

def main():
    """Main function to run the synchronization analysis"""
    base_dir = Path(__file__).parent
    id_dir = base_dir / 'content' / 'docs' / 'id'
    en_dir = base_dir / 'content' / 'docs' / 'en'
    
    print("="*70)
    print("Translation Structure Synchronization Analysis")
    print("="*70)
    print(f"ID directory: {id_dir}")
    print(f"EN directory: {en_dir}")
    print()
    
    # Find all ID files
    id_files = sorted(id_dir.rglob('*.mdx'))
    print(f"Found {len(id_files)} ID files\n")
    
    stats = {
        'total': len(id_files),
        'matched': 0,
        'missing': 0,
        'mismatched': 0
    }
    
    reports = []
    files_with_issues = []
    
    for id_file in id_files:
        # Get relative path
        rel_path = id_file.relative_to(id_dir)
        
        # Convert to EN path
        en_rel_path = get_en_path(str(rel_path))
        en_file = en_dir / en_rel_path
        
        # Generate report
        report, has_issues = generate_report(id_file, en_file, id_dir, en_dir)
        reports.append(report)
        
        if not en_file.exists():
            stats['missing'] += 1
            files_with_issues.append(str(rel_path))
        elif has_issues:
            stats['mismatched'] += 1
            files_with_issues.append(str(rel_path))
        else:
            stats['matched'] += 1
    
    # Print all reports
    for report in reports:
        print(report)
    
    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total ID files:        {stats['total']}")
    print(f"Matched & aligned:     {stats['matched']}")
    print(f"Structure mismatched:  {stats['mismatched']}")
    print(f"EN file missing:       {stats['missing']}")
    print("="*70)
    
    if files_with_issues:
        print(f"\n{len(files_with_issues)} files need attention:")
        for f in files_with_issues:
            print(f"  - {f}")
    else:
        print("\nAll files are properly aligned!")

if __name__ == '__main__':
    main()
