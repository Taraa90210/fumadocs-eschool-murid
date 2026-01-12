const fs = require('fs');
const path = require('path');

// Konfigurasi
const CONFIG = {
  targetDir: './content/docs',  // Folder yang akan diproses
  fileExtensions: ['.mdx', '.md'],  // Extension yang akan diproses
  backup: true,  // Buat backup sebelum modify
  dryRun: false  // Set true untuk preview tanpa mengubah file
};

// Function untuk fix img tags
function fixImgTags(content) {
  // Pattern untuk mendeteksi <img> yang tidak self-closing
  // Matches: <img src="..." alt="..."> (tanpa />)
  // Tidak match: <img src="..." /> (sudah self-closing)
  const imgPattern = /<img\s+([^>]*[^/])>/gi;
  
  let fixedContent = content;
  let fixCount = 0;

  // Replace semua <img ...> menjadi <img ... />
  fixedContent = fixedContent.replace(imgPattern, (match, attributes) => {
    fixCount++;
    // Hilangkan trailing whitespace dari attributes
    const cleanAttributes = attributes.trim();
    return `<img ${cleanAttributes} />`;
  });

  return { content: fixedContent, count: fixCount };
}

// Function untuk proses file
function processFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    const { content: fixedContent, count } = fixImgTags(content);

    if (count > 0) {
      if (CONFIG.dryRun) {
        console.log(`[DRY RUN] Would fix ${count} img tag(s) in: ${filePath}`);
        return { fixed: count, file: filePath };
      }

      // Buat backup jika diaktifkan
      if (CONFIG.backup) {
        const backupPath = `${filePath}.backup`;
        fs.copyFileSync(filePath, backupPath);
      }

      // Tulis file yang sudah diperbaiki
      fs.writeFileSync(filePath, fixedContent, 'utf-8');
      console.log(`✓ Fixed ${count} img tag(s) in: ${filePath}`);
      return { fixed: count, file: filePath };
    }

    return null;
  } catch (error) {
    console.error(`✗ Error processing ${filePath}:`, error.message);
    return null;
  }
}

// Function untuk scan folder secara rekursif
function scanDirectory(dir) {
  const results = [];
  
  try {
    const items = fs.readdirSync(dir);

    items.forEach(item => {
      const fullPath = path.join(dir, item);
      const stat = fs.statSync(fullPath);

      if (stat.isDirectory()) {
        // Rekursif ke subdirectory
        results.push(...scanDirectory(fullPath));
      } else if (stat.isFile()) {
        // Check extension
        const ext = path.extname(item);
        if (CONFIG.fileExtensions.includes(ext)) {
          results.push(fullPath);
        }
      }
    });
  } catch (error) {
    console.error(`Error scanning directory ${dir}:`, error.message);
  }

  return results;
}

// Main function
function main() {
  console.log('🔧 Starting IMG tag auto-fix...\n');
  
  if (CONFIG.dryRun) {
    console.log('⚠️  DRY RUN MODE - No files will be modified\n');
  }

  if (CONFIG.backup && !CONFIG.dryRun) {
    console.log('💾 Backup enabled - .backup files will be created\n');
  }

  // Check if directory exists
  if (!fs.existsSync(CONFIG.targetDir)) {
    console.error(`❌ Directory not found: ${CONFIG.targetDir}`);
    process.exit(1);
  }

  // Scan semua file
  console.log(`📁 Scanning directory: ${CONFIG.targetDir}`);
  const files = scanDirectory(CONFIG.targetDir);
  console.log(`📄 Found ${files.length} file(s) to process\n`);

  // Process semua file
  const results = [];
  let totalFixed = 0;

  files.forEach(file => {
    const result = processFile(file);
    if (result) {
      results.push(result);
      totalFixed += result.fixed;
    }
  });

  // Summary
  console.log('\n📊 Summary:');
  console.log(`   Total files processed: ${files.length}`);
  console.log(`   Files modified: ${results.length}`);
  console.log(`   Total img tags fixed: ${totalFixed}`);

  if (results.length > 0) {
    console.log('\n📝 Modified files:');
    results.forEach(r => {
      console.log(`   - ${r.file} (${r.fixed} tag(s))`);
    });
  }

  if (CONFIG.backup && !CONFIG.dryRun && results.length > 0) {
    console.log('\n💡 Tip: To remove backup files, run:');
    console.log(`   find ${CONFIG.targetDir} -name "*.backup" -delete`);
  }

  console.log('\n✅ Done!');
}

// Helper: Preview mode untuk lihat apa yang akan diubah
function preview(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const imgPattern = /<img\s+([^>]*[^/])>/gi;
  
  let match;
  const matches = [];
  
  while ((match = imgPattern.exec(content)) !== null) {
    matches.push({
      original: match[0],
      fixed: `<img ${match[1].trim()} />`,
      line: content.substring(0, match.index).split('\n').length
    });
  }

  if (matches.length > 0) {
    console.log(`\nPreview for: ${filePath}`);
    matches.forEach((m, i) => {
      console.log(`\n${i + 1}. Line ${m.line}:`);
      console.log(`   Before: ${m.original}`);
      console.log(`   After:  ${m.fixed}`);
    });
  }
}

// Export untuk digunakan di module lain
module.exports = {
  fixImgTags,
  processFile,
  scanDirectory,
  preview
};

// Run jika dipanggil langsung
if (require.main === module) {
  // Parse command line arguments
  const args = process.argv.slice(2);
  
  if (args.includes('--help')) {
    console.log(`
Usage: node fix-img-tags.js [options]

Options:
  --dry-run          Preview changes without modifying files
  --no-backup        Don't create backup files
  --dir <path>       Target directory (default: ./content/docs)
  --preview <file>   Preview changes for a specific file
  --help             Show this help message

Examples:
  node fix-img-tags.js
  node fix-img-tags.js --dry-run
  node fix-img-tags.js --dir ./content
  node fix-img-tags.js --preview ./content/docs/index.mdx
    `);
    process.exit(0);
  }

  if (args.includes('--dry-run')) {
    CONFIG.dryRun = true;
  }

  if (args.includes('--no-backup')) {
    CONFIG.backup = false;
  }

  const dirIndex = args.indexOf('--dir');
  if (dirIndex !== -1 && args[dirIndex + 1]) {
    CONFIG.targetDir = args[dirIndex + 1];
  }

  const previewIndex = args.indexOf('--preview');
  if (previewIndex !== -1 && args[previewIndex + 1]) {
    preview(args[previewIndex + 1]);
    process.exit(0);
  }

  main();
}
