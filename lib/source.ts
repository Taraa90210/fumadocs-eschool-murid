import { docs } from "fumadocs-mdx:collections/server";
import { loader, type InferPageType } from "fumadocs-core/source";
import { lucideIconsPlugin } from "fumadocs-core/source/lucide-icons";
import { icons } from "lucide-react";
import { createElement } from "react";

// ──────────────────────────────────────────────────────────────────────────────
// SOURCE UTAMA
// ──────────────────────────────────────────────────────────────────────────────
export const source = loader({
  baseUrl: "/docs",
  source: docs.toFumadocsSource(),
  // lucideIconsPlugin otomatis menangani properti "icon" di meta.json & frontmatter
  plugins: [lucideIconsPlugin()],
  icon(name) {
    if (name && name in icons) {
      return createElement(icons[name as keyof typeof icons]);
    }
  },
  i18n: {
    languages: ["en", "id"],
    defaultLanguage: "en",
    parser: "dir", // Menggunakan folder /en dan /id sebagai root bahasa
  },
});

// TYPE AMAN
export type DocsPage = InferPageType<typeof source>;

// ──────────────────────────────────────────────────────────────────────────────
// HELPER FUNCTIONS (TETAP DI PERTAHANKAN)
// ──────────────────────────────────────────────────────────────────────────────

/**
 * Mendapatkan tree berdasarkan bahasa tertentu.
 * Note: Dengan i18n aktif, Anda juga bisa menggunakan source.getPageTree(lang)
 */
export function getTreeByLang(lang: "id" | "en") {
  return {
    ...source.pageTree,
    children: source.pageTree.children?.filter((node) => {
      // Memastikan node hanya berasal dari slug bahasa yang dipilih
      return node.type === "folder" && node.name.toLowerCase() === lang;
    }),
  };
}

/**
 * Menghasilkan URL image untuk Open Graph (OG)
 */
export function getPageImage(page: DocsPage) {
  const segments = [...page.slugs, "image.png"];

  return {
    segments,
    url: `/og/docs/${segments.join("/")}`,
  };
}

/**
 * Mengambil teks bersih dari halaman untuk keperluan LLM atau AI
 */
export async function getLLMText(page: DocsPage) {
  const processed = await page.data.getText("processed");

  return `# ${page.data.title}

${processed}`;
}
