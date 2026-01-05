import { source } from "@/lib/source";
import { createSearchAPI } from "fumadocs-core/search/server";

export const { GET } = createSearchAPI("advanced", {
  // Kita ambil semua halaman dari kedua bahasa (en & id)
  indexes: source.getPages().map((page) => ({
    title: page.data.title,
    content: page.data.description ?? "",
    url: page.url,
    id: page.url,
    structuredData: page.data.structuredData,
    // Tambahkan tag locale agar sistem tahu ini halaman bahasa apa
    tag: page.locale,
  })),
  // Opsi tambahan jika ingin performa lebih baik untuk bahasa Indonesia
  // Namun secara default 'english' sudah cukup baik untuk teks Latin seperti Indonesia
  // language: "english",
});
