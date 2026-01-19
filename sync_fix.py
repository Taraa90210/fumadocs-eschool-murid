#!/usr/bin/env python3
"""
Script to automatically synchronize EN file structure to match ID files.
This script will:
1. Match heading levels between ID and EN
2. Match list numbering and indentation
3. Preserve EN translation text
4. Create backup before modifying files
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# Import PATH_MAPPING from sync_translations.py
PATH_MAPPING = {
    'menu-siswa': 'student-menu',
    'menu-wali': 'guardian-menu',
    'penyelesaian-masalah': 'troubleshooting',
    'pengenalan': 'introduction',
    'kebijakan-dan-keamanan': 'policies-and-security',
    'panduan-pengguna-baru': 'new-user-guide',
    'pengaturan-personal': 'personal-settings',
    'ujian': 'exams',
    'tugas': 'assignments',
    'nilai-ujian': 'exam-results',
    'biaya': 'fees',
    'laporan': 'reports',
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
    'ubah-password': 'change-password',
}

def get_en_path(id_path: str) -> str:
    """Convert ID path to EN path"""
    parts = Path(id_path).parts
    en_parts = []
    
    for part in parts:
        part_name = part.replace('.mdx', '')
        if part_name in PATH_MAPPING:
            en_part = PATH_MAPPING[part_name]
            if part.endswith('.mdx'):
                en_part += '.mdx'
            en_parts.append(en_part)
        else:
            en_parts.append(part)
    
    return str(Path(*en_parts))

def extract_frontmatter(content: str) -> Tuple[str, str]:
    """Extract frontmatter and body"""
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

def parse_line(line: str) -> Dict:
    """Parse a markdown line and return its structure"""
    # Heading
    heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
    if heading_match:
        return {
            'type': 'heading',
            'level': len(heading_match.group(1)),
            'text': heading_match.group(2),
            'original': line
        }
    
    # Numbered list
    numbered_match = re.match(r'^(\s*)(\d+)\.\s+(.+)$', line)
    if numbered_match:
        return {
            'type': 'numbered_list',
            'indent': len(numbered_match.group(1)),
            'number': numbered_match.group(2),
            'text': numbered_match.group(3),
            'original': line
        }
    
    # Bullet list
    bullet_match = re.match(r'^(\s*)([\*\-\+])\s+(.+)$', line)
    if bullet_match:
        return {
            'type': 'bullet_list',
            'indent': len(bullet_match.group(1)),
            'bullet': bullet_match.group(2),
            'text': bullet_match.group(3),
            'original': line
        }
    
    return {'type': 'other', 'original': line}

def sync_file(id_file: Path, en_file: Path, dry_run=True) -> bool:
    """Synchronize EN file structure to match ID file"""
    
    if not en_file.exists():
        print(f"  [SKIP] EN file not found: {en_file.name}")
        return False
    
    # Read files
    id_content = id_file.read_text(encoding='utf-8')
    en_content = en_file.read_text(encoding='utf-8')
    
    # Extract frontmatter
    id_fm, id_body = extract_frontmatter(id_content)
    en_fm, en_body = extract_frontmatter(en_content)
    
    # Split into lines
    id_lines = id_body.split('\n')
    en_lines = en_body.split('\n')
    
    # Parse both files
    id_parsed = [parse_line(line) for line in id_lines]
    en_parsed = [parse_line(line) for line in en_lines]
    
    # Track changes
    changes_made = False
    new_en_lines = []
    
    # Simple alignment: match headings and lists by order
    id_idx = 0
    en_idx = 0
    
    while id_idx < len(id_parsed) and en_idx < len(en_parsed):
        id_item = id_parsed[id_idx]
        en_item = en_parsed[en_idx]
        
        # Match headings
        if id_item['type'] == 'heading' and en_item['type'] == 'heading':
            if id_item['level'] != en_item['level']:
                # Adjust EN heading level to match ID
                new_line = '#' * id_item['level'] + ' ' + en_item['text']
                new_en_lines.append(new_line)
                changes_made = True
                print(f"    [FIX] Heading level: H{en_item['level']} -> H{id_item['level']}")
            else:
                new_en_lines.append(en_item['original'])
            id_idx += 1
            en_idx += 1
        
        # Match numbered lists
        elif id_item['type'] == 'numbered_list' and en_item['type'] == 'numbered_list':
            if id_item['indent'] != en_item['indent']:
                # Adjust indentation
                indent_str = ' ' * id_item['indent']
                new_line = f"{indent_str}{en_item['number']}. {en_item['text']}"
                new_en_lines.append(new_line)
                changes_made = True
            else:
                new_en_lines.append(en_item['original'])
            id_idx += 1
            en_idx += 1
        
        # Match bullet lists
        elif id_item['type'] == 'bullet_list' and en_item['type'] == 'bullet_list':
            if id_item['indent'] != en_item['indent']:
                # Adjust indentation
                indent_str = ' ' * id_item['indent']
                new_line = f"{indent_str}{en_item['bullet']} {en_item['text']}"
                new_en_lines.append(new_line)
                changes_made = True
            else:
                new_en_lines.append(en_item['original'])
            id_idx += 1
            en_idx += 1
        
        # Keep other lines as-is
        else:
            new_en_lines.append(en_item['original'])
            if id_item['type'] == en_item['type']:
                id_idx += 1
            en_idx += 1
    
    # Add remaining EN lines
    while en_idx < len(en_parsed):
        new_en_lines.append(en_parsed[en_idx]['original'])
        en_idx += 1
    
    if changes_made:
        new_content = en_fm + '\n' + '\n'.join(new_en_lines)
        
        if not dry_run:
            # Create backup
            backup_path = en_file.with_suffix('.mdx.bak')
            shutil.copy2(en_file, backup_path)
            
            # Write new content
            en_file.write_text(new_content, encoding='utf-8')
            print(f"  [UPDATED] {en_file.name} (backup: {backup_path.name})")
        else:
            print(f"  [DRY-RUN] Would update {en_file.name}")
        
        return True
    
    return False

def main():
    """Main function"""
    import sys
    
    base_dir = Path(__file__).parent
    id_dir = base_dir / 'content' / 'docs' / 'id'
    en_dir = base_dir / 'content' / 'docs' / 'en'
    
    # Check for --apply flag
    dry_run = '--apply' not in sys.argv
    
    print("="*70)
    print("Translation Structure Synchronization")
    print("="*70)
    if dry_run:
        print("MODE: DRY RUN (use --apply to make actual changes)")
    else:
        print("MODE: APPLY CHANGES (backups will be created)")
    print("="*70)
    print()
    
    # Find all ID files
    id_files = sorted(id_dir.rglob('*.mdx'))
    
    stats = {
        'total': 0,
        'updated': 0,
        'skipped': 0,
        'no_change': 0
    }
    
    for id_file in id_files:
        rel_path = id_file.relative_to(id_dir)
        en_rel_path = get_en_path(str(rel_path))
        en_file = en_dir / en_rel_path
        
        print(f"\n[FILE] {rel_path}")
        stats['total'] += 1
        
        if sync_file(id_file, en_file, dry_run):
            stats['updated'] += 1
        elif not en_file.exists():
            stats['skipped'] += 1
        else:
            stats['no_change'] += 1
            print(f"  [OK] No changes needed")
    
    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total files processed:  {stats['total']}")
    print(f"Files updated:          {stats['updated']}")
    print(f"Files skipped:          {stats['skipped']}")
    print(f"No changes needed:      {stats['no_change']}")
    print("="*70)
    
    if dry_run and stats['updated'] > 0:
        print("\nTo apply changes, run: python sync_fix.py --apply")

if __name__ == '__main__':
    main()
