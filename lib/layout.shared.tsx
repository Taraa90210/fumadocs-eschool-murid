import type { BaseLayoutProps } from "fumadocs-ui/layouts/shared";
import Image from "next/image";

export function baseOptions(): BaseLayoutProps {
  return {
    nav: {
      title: (
        <div className="flex items-center gap-2">
          <Image
            src="/images/eschool.png" // Pastikan file ada di public/logo.png
            alt="eSchool Logo"
            width={30}
            height={30}
            className="rounded-sm"
          />
          <span className="font-bold text-lg tracking-tight">eSchool Website</span>
        </div>
      ),
    },
  };
}
