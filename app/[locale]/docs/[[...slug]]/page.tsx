// 1. Import 'icons' dari lucide-react di sini
import { icons } from "lucide-react";
import { source } from "@/lib/source";
import { DocsPage, DocsBody, DocsTitle } from "fumadocs-ui/page";
import defaultMdxComponents from "fumadocs-ui/mdx";
import { notFound } from "next/navigation";

export default async function Page({
  params,
}: {
  params: Promise<{ locale: string; slug?: string[] }>;
}) {
  const { locale, slug } = await params;
  const page = source.getPage(slug, locale);

  if (!page) notFound();

  const MDX = page.data.body;

  // 2. AMBIL STRING IKON DAN UBAH JADI KOMPONEN
  // Jika page.data.icon berisi "Home", maka LucideIcon akan berisi komponen <Home />
  const iconName = page.data.icon as keyof typeof icons;
  const LucideIcon = iconName ? icons[iconName] : null;

  return (
    <DocsPage
      toc={page.data.toc}
      full={false}
      tableOfContent={{
        enabled: true,
        component:
          page.data.toc.length > 0 ? undefined : (
            <div className="hidden lg:block w-[293px] shrink-0" />
          ),
      }}
    >
      <DocsBody>
        <div className="mb-8 flex flex-row items-center gap-3">
          {/* Ikon */}
          {LucideIcon && (
            <div className="flex shrink-0 items-center justify-center text-fd-primary">
              {/* 
         Ukuran size 32px biasanya cocok dengan teks 3xl. 
         StrokeWidth ditebalkan sedikit agar seimbang dengan font bold.
      */}
              <LucideIcon size={32} strokeWidth={2.5} />
            </div>
          )}

          {/* Judul */}
          <DocsTitle className="!m-0 !p-0 text-3xl font-bold leading-tight">
            {page.data.title}
          </DocsTitle>
        </div>

        <MDX components={{ ...defaultMdxComponents }} />
      </DocsBody>
    </DocsPage>
  );
}
