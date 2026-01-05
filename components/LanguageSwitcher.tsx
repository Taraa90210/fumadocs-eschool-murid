"use client";

import { usePathname, useRouter } from "next/navigation";
import {
  Select,
  SelectTrigger,
  SelectContent,
  SelectItem,
  SelectValue,
} from "@/components/ui/select";

const locales = ["id", "en"] as const;

export function LanguageSwitcher() {
  const pathname = usePathname();
  const router = useRouter();

  const currentLocale =
    locales.find((l) => pathname.startsWith(`/docs/${l}`)) ?? "id";

  function switchLocale(locale: string) {
    const newPath = pathname.replace(/^\/docs\/(id|en)/, `/docs/${locale}`);
    router.push(newPath);
  }

  return (
    <Select value={currentLocale} onValueChange={switchLocale}>
      <SelectTrigger className="w-[110px]">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="id">🇮🇩 ID</SelectItem>
        <SelectItem value="en">🇺🇸 EN</SelectItem>
      </SelectContent>
    </Select>
  );
}
