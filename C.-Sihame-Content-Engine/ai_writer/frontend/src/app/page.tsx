"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { getApiBaseUrl } from "@/lib/api";

export default function Home() {
  const router = useRouter();
  const [rawInput, setRawInput] = useState("");
  const [postType, setPostType] = useState("reflection");
  const [platform, setPlatform] = useState("telegram");
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState("");

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!rawInput.trim()) {
      setError("الرجاء كتابة الفكرة أولاً");
      return;
    }

    setIsGenerating(true);
    setError("");

    try {
      const apiUrl = getApiBaseUrl();
      const response = await fetch(`${apiUrl}/api/v1/content/draft`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          raw_input: rawInput,
          post_type: postType,
          platform: platform,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "حدث خطأ أثناء التوليد");
      }

      const data = await response.json();
      router.push(`/draft/${data.draft_id}`);
    } catch (err) {
      console.error(err);
      setError((err as Error).message || "حدث خطأ غير متوقع. تأكد من تشغيل الخادم الخلفي.");
      setIsGenerating(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto mt-12 bg-white/60 backdrop-blur-md p-8 rounded-3xl shadow-sm border border-[#0D4F5C]/10">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-2">مساعد صناعة المحتوى 🪄</h1>
        <p className="text-[#0D4F5C]/70">أدخلي فكرتك الخام، وسيقوم المايسترو بصياغتها بأسلوبك.</p>
      </div>

      <form onSubmit={handleGenerate} className="space-y-6">
        <div>
          <label className="block text-lg font-medium mb-3">الفكرة الأساسية (تسجيل صوتي مفرغ أو نص عشوائي)</label>
          <textarea
            value={rawInput}
            onChange={(e) => setRawInput(e.target.value)}
            className="w-full h-40 p-4 rounded-xl border border-[#0D4F5C]/20 bg-white/50 focus:ring-2 focus:ring-[#C4933F] focus:outline-none resize-none transition-all"
            placeholder="مثال: كنت أتحدث اليوم مع عميلة عن الخوف من الرفض وكيف يمنعها من قول لا..."
            disabled={isGenerating}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">نوع المنشور (Post Type)</label>
            <select
              value={postType}
              onChange={(e) => setPostType(e.target.value)}
              className="w-full p-3 rounded-xl border border-[#0D4F5C]/20 bg-white/50 focus:ring-2 focus:ring-[#C4933F] focus:outline-none"
              disabled={isGenerating}
            >
              <option value="reflection">تأمل (Reflection)</option>
              <option value="clinic story">قصة من العيادة (Clinic Story)</option>
              <option value="promo">ترويج (Promo / Offer)</option>
              <option value="prayer / reflection">دعاء أو نية (Prayer / Intention)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">المنصة (Platform)</label>
            <select
              value={platform}
              onChange={(e) => setPlatform(e.target.value)}
              className="w-full p-3 rounded-xl border border-[#0D4F5C]/20 bg-white/50 focus:ring-2 focus:ring-[#C4933F] focus:outline-none"
              disabled={isGenerating}
            >
              <option value="telegram">تليغرام (Telegram)</option>
              <option value="instagram">إنستغرام (Instagram)</option>
              <option value="email">إيميل (Newsletter)</option>
            </select>
          </div>
        </div>

        {error && (
          <div className="p-4 bg-red-50 text-red-600 rounded-xl border border-red-100 text-sm">
            ❌ {error}
          </div>
        )}

        <button
          type="submit"
          disabled={isGenerating || !rawInput.trim()}
          className="w-full py-4 text-white font-bold text-lg rounded-xl transition-all shadow-md bg-[#0D4F5C] hover:bg-[#093a44] disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center space-x-2 rtl:space-x-reverse"
        >
          {isGenerating ? (
            <>
              <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>جاري صياغة المحتوى بكل حب... قد يستغرق الأمر دقيقة</span>
            </>
          ) : (
            <span>صياغة المنشور ✨</span>
          )}
        </button>
      </form>
    </div>
  );
}
