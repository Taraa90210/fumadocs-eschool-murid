"use client";
import { useState } from "react";

export function useLanguage() {
  const [lang, setLang] = useState<"id" | "en">("id");
  return { lang, setLang };
}
