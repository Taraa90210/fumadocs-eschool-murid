const fs = require('fs');
const path = require('path');

// Konfigurasi
const CONFIG = {
  gitbookDir: './eSchool-Siakad-Mobile-Siswa',      // Folder GitBook Anda
  fumadocsDir: './content/docs',       // Folder output Fumadocs
  summaryFile: './eSchool-Siakad-Mobile-Siswa/SUMMARY.md'          // Path ke SUMMARY.md
};

// Parse SUMMARY.md
function parseSummary(summaryPath) {
  const content = fs.readFileSync(summaryPath, 'utf-8');
  const lines = content.split('\n');
  const structure = [];
  const stack = [{ children: structure, level: -1 }];

  lines.forEach(line => {
    const match = line.match(/^(\s*)\* \[(.+?)\]\((.+?)\)/);
    if (!match) return;

    const [, indent, title, filepath] = match;
    const level = indent.length / 2;
    const slug = filepath.replace(/\.md$/, '').replace(/README$/, 'index');

    const item = { title, filepath, slug, children: [] };

    // Cari parent yang tepat
    while (stack[stack.length - 1].level >= level) {
      stack.pop();
    }

    stack[stack.length - 1].children.push(item);
    stack.push({ ...item, level });
  });

  return structure;
}

// Convert MD ke MDX
function convertMdToMdx(content, title) {
  // Hapus frontmatter lama jika ada
  content = content.replace(/^---\n[\s\S]*?\n---\n/, '');
  
  // Tambah frontmatter baru
  const frontmatter = `---
title: ${title}
---

`;
  
  // Update image paths jika ada (GitBook relatif -> Fumadocs absolute)
  content = content.replace(/!\[([^\]]*)\]\((?!http)([^)]+)\)/g, (match, alt, src) => {
    const newSrc = src.startsWith('/') ? src : `/${src}`;
    return `![${alt}](${newSrc})`;
  });

  // Update internal links
  content = content.replace(/\[([^\]]+)\]\((?!http)([^)]+)\.md\)/g, (match, text, href) => {
    const cleanHref = href.replace(/^\.\.\//, '').replace(/^\.\//, '');
    return `[${text}](/docs/${cleanHref})`;
  });

  return frontmatter + content;
}

// Generate meta.json
function generateMetaJson(items) {
  return items.map(item => {
    if (item.children.length > 0) {
      return {
        title: item.title,
        pages: generateMetaJson(item.children)
      };
    }
    return item.slug.split('/').pop();
  });
}

// Buat struktur folder dan convert files
function processStructure(items, currentPath = '') {
  const metaItems = [];

  items.forEach(item => {
    const sourcePath = path.join(CONFIG.gitbookDir, item.filepath);
    const isIndex = item.filepath.endsWith('README.md');
    const targetSlug = isIndex ? 
      path.dirname(item.slug) + '/index' : 
      item.slug;
    const targetPath = path.join(CONFIG.fumadocsDir, targetSlug + '.mdx');

    // Buat direktori jika belum ada
    const targetDir = path.dirname(targetPath);
    if (!fs.existsSync(targetDir)) {
      fs.mkdirSync(targetDir, { recursive: true });
    }

    // Convert dan copy file
    if (fs.existsSync(sourcePath)) {
      const content = fs.readFileSync(sourcePath, 'utf-8');
      const converted = convertMdToMdx(content, item.title);
      fs.writeFileSync(targetPath, converted, 'utf-8');
      console.log(`✓ Converted: ${item.filepath} -> ${targetSlug}.mdx`);
    } else {
      console.warn(`⚠ File not found: ${sourcePath}`);
    }

    // Proses children jika ada
    if (item.children.length > 0) {
      const childDir = path.join(CONFIG.fumadocsDir, path.dirname(item.slug));
      processStructure(item.children, childDir);
      
      metaItems.push({
        type: 'folder',
        title: item.title,
        index: isIndex ? 'index' : undefined,
        pages: generateMetaJson(item.children)
      });
    } else {
      metaItems.push(targetSlug.split('/').pop());
    }
  });

  return metaItems;
}

// Generate meta.json untuk setiap folder
function generateAllMetaFiles(structure, basePath = CONFIG.fumadocsDir) {
  const grouped = {};
  
  function traverse(items, currentPath) {
    items.forEach(item => {
      const dir = path.dirname(path.join(basePath, item.slug));
      
      if (!grouped[dir]) {
        grouped[dir] = [];
      }

      if (item.children.length > 0) {
        grouped[dir].push({
          type: 'folder',
          title: item.title,
          pages: item.children.map(child => {
            const slug = child.slug.split('/').pop().replace(/^index$/, '');
            return slug || child.title.toLowerCase().replace(/\s+/g, '-');
          })
        });
        traverse(item.children, path.join(currentPath, item.title));
      } else {
        const filename = item.slug.split('/').pop();
        if (filename !== 'index') {
          grouped[dir].push(filename);
        }
      }
    });
  }

  traverse(structure, '');

  // Write meta.json files
  Object.entries(grouped).forEach(([dir, items]) => {
    const metaPath = path.join(dir, 'meta.json');
    const metaContent = JSON.stringify({ pages: items }, null, 2);
    fs.writeFileSync(metaPath, metaContent, 'utf-8');
    console.log(`✓ Generated: ${metaPath}`);
  });
}

// Main function
function main() {
  console.log('🚀 Starting GitBook to Fumadocs conversion...\n');

  // Buat folder output
  if (!fs.existsSync(CONFIG.fumadocsDir)) {
    fs.mkdirSync(CONFIG.fumadocsDir, { recursive: true });
  }

  // Parse SUMMARY.md
  console.log('📖 Parsing SUMMARY.md...');
  const structure = parseSummary(CONFIG.summaryFile);

  // Convert files
  console.log('\n📝 Converting markdown files...');
  processStructure(structure);

  // Generate meta.json files
  console.log('\n🔧 Generating meta.json files...');
  generateAllMetaFiles(structure);

  console.log('\n✅ Conversion completed!');
  console.log(`\nNext steps:`);
  console.log(`1. Review files in ${CONFIG.fumadocsDir}`);
  console.log(`2. Update meta.json files if needed`);
  console.log(`3. Run: npm run dev`);
}

// Run
try {
  main();
} catch (error) {
  console.error('❌ Error:', error.message);
  process.exit(1);
}
