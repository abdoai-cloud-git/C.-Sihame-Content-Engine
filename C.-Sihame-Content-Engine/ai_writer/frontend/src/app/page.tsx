"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { getApiBaseUrl } from "@/lib/api";
import HistoryDrawer from "@/components/HistoryDrawer";
import { useQueryClient } from "@tanstack/react-query";

const PLATFORMS = [
  { id: "facebook", label: "فيسبوك (Facebook)" },
  { id: "instagram", label: "إنستغرام (Instagram)" },
  { id: "telegram", label: "تليغرام (Telegram)" },
  { id: "tiktok", label: "تيك توك (TikTok)" },
];

function MainWorkspace() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();

  // Navigation / Drawer
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  // App State: compose | review | approved
  const [appState, setAppState] = useState<"compose" | "review" | "approved">("compose");
  const [isComposerExpanded, setIsComposerExpanded] = useState(true);

  // Compose State
  const [rawInput, setRawInput] = useState("");
  const [postType, setPostType] = useState("reflection");
  
  // Draft State
  const [draftId, setDraftId] = useState<string | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [draft, setDraft] = useState<any>(null);

  // Status flags
  const [isGenerating, setIsGenerating] = useState(false);
  const [isLoadingDraft, setIsLoadingDraft] = useState(false);
  const [error, setError] = useState("");

  // Review State
  const [editInstruction, setEditInstruction] = useState("");
  const [isRevising, setIsRevising] = useState(false);
  const [isApproving, setIsApproving] = useState(false);

  // Adopt State
  const [adaptPlatforms, setAdaptPlatforms] = useState<string[]>([]);
  const [isAdapting, setIsAdapting] = useState(false);
  const [adaptResults, setAdaptResults] = useState<Record<string, string>>({});
  const [copiedPlatform, setCopiedPlatform] = useState<string | null>(null);
  const [mainCopySuccess, setMainCopySuccess] = useState(false);

  // Load draft from URL if any
  useEffect(() => {
    const urlDraftId = searchParams.get("draftId");
    if (urlDraftId) {
      loadDraft(urlDraftId);
      // Clean up URL without reloading
      router.replace("/");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  // History Helper (Database fetch invalidated)
  const invalidateHistory = () => {
    queryClient.invalidateQueries({ queryKey: ["history"] });
  };

  // Helper load draft
  const loadDraft = async (id: string) => {
    setIsLoadingDraft(true);
    setError("");
    setAdaptResults({});
    
    try {
      const apiUrl = getApiBaseUrl();
      const res = await fetch(`${apiUrl}/api/v1/content/${id}`);
      if (!res.ok) throw new Error("لم يتم العثور على المسودة");
      const data = await res.json();
      setDraft(data);
      setDraftId(id);
      
      const currentStatus = data.status || "";
      if (currentStatus === "approved_text" || currentStatus === "approved") {
        setAppState("approved");
      } else {
        setAppState("review");
      }
      setIsComposerExpanded(false);
    } catch (err) {
      setError((err as Error).message);
      setAppState("compose");
      setIsComposerExpanded(true);
    } finally {
      setIsLoadingDraft(false);
    }
  };

  // 1. Generate new draft
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
          // Platform is no longer required at generation, defaults to 'general' via backend
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "حدث خطأ أثناء التوليد");
      }

      const data = await response.json();
      setDraft(data);
      setDraftId(data.draft_id);
      setAppState("review");
      setIsComposerExpanded(false);
      invalidateHistory();
    } catch (err) {
      console.error(err);
      setError((err as Error).message || "حدث خطأ غير متوقع. تأكد من تشغيل الخادم الخلفي.");
    } finally {
      setIsGenerating(false);
    }
  };

  // 2. Revise existing draft
  const handleRevise = async () => {
    if (!editInstruction.trim() || !draftId) return;
    setIsRevising(true);
    try {
      const apiUrl = getApiBaseUrl();
      const res = await fetch(`${apiUrl}/api/v1/content/revise`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          draft_id: draftId,
          edit_instruction: editInstruction,
        }),
      });
      if (!res.ok) throw new Error("فشل التعديل");
      const data = await res.json();
      setDraft({ ...draft, ...data });
      setEditInstruction("");
      invalidateHistory();
    } catch (err) {
      alert((err as Error).message);
    } finally {
      setIsRevising(false);
    }
  };

  // 3. Approve draft
  const handleApprove = async () => {
    if (!draftId || !draft) return;
    setIsApproving(true);
    try {
      const apiUrl = getApiBaseUrl();
      const res = await fetch(`${apiUrl}/api/v1/content/approve-text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          draft_id: draftId,
          approved_text: draft.body,
        }),
      });
      if (!res.ok) throw new Error("فشل اعتماد النص");
      
      const data = await res.json();
      setDraft({ ...draft, status: data.status || "approved_text" });
      setAppState("approved");
      invalidateHistory();
    } catch (err) {
      alert((err as Error).message);
    } finally {
      setIsApproving(false);
    }
  };

  // 4. Adapt for platform
  const handleAdapt = async () => {
    if (!draftId || adaptPlatforms.length === 0) return;
    setIsAdapting(true);
    try {
      const apiUrl = getApiBaseUrl();
      const res = await fetch(`${apiUrl}/api/v1/content/adapt`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          draft_id: draftId,
          target_platforms: adaptPlatforms,
        }),
      });
      if (!res.ok) throw new Error("فشل التكيف مع المنصة");
      const data = await res.json();
      setAdaptResults(data.results);
      setCopiedPlatform(null);
      invalidateHistory();
    } catch (err) {
      alert((err as Error).message);
    } finally {
      setIsAdapting(false);
    }
  };

  const handleCopyMainPost = () => {
    if (draft) {
      const fullText = [draft.hook, draft.body, draft.cta]
        .map((s) => s?.trim())
        .filter(Boolean)
        .join("\n\n");
      navigator.clipboard.writeText(fullText);
      setMainCopySuccess(true);
      setTimeout(() => setMainCopySuccess(false), 2000);
    }
  };

  const handleCopyPlatform = (platform: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedPlatform(platform);
    setTimeout(() => setCopiedPlatform(null), 2000);
  };


  return (
    <>
      <HistoryDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        onRestore={loadDraft}
      />

      <div className="max-w-4xl mx-auto mt-8 pb-96 relative">
        {/* Header & Drawer Trigger */}
        <div className="flex justify-between items-center mb-8 px-4">
          <div className="flex-1" />
          <h1 className="text-3xl font-bold text-center text-[#0D4F5C]">
             مساعد الكوتش سهام 🪄
          </h1>
          <div className="flex-1 flex justify-end">
            <button
              onClick={() => setIsDrawerOpen(true)}
              className="p-2 text-[#0D4F5C] hover:bg-[#0D4F5C]/10 rounded-full transition-colors flex items-center space-x-2 rtl:space-x-reverse"
              title="سجل المسودات"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>
          </div>
        </div>

        {/* Global Loading / Error */}
        {isLoadingDraft && (
          <div className="text-center mt-20 text-xl animate-pulse text-[#0D4F5C]">جاري تحميل المسودة...</div>
        )}
        {error && (
          <div className="p-4 mb-6 mx-4 bg-red-50 text-red-600 rounded-xl border border-red-100 text-sm">
            ❌ {error}
          </div>
        )}

        {/* --- FLOATING COMPOSER --- */}
        <div 
          className={`fixed bottom-0 left-0 right-0 bg-white/95 backdrop-blur-md shadow-[0_-10px_40px_rgba(0,0,0,0.1)] border-t border-[#0D4F5C]/10 transition-transform duration-500 z-50 ${
            isComposerExpanded ? "translate-y-0" : "translate-y-[calc(100%-80px)]"
          }`}
        >
          <div className="max-w-4xl mx-auto p-4 md:p-8 relative">
            <button
              onClick={() => setIsComposerExpanded(!isComposerExpanded)}
              className="absolute -top-6 left-1/2 -translate-x-1/2 bg-white px-6 py-2 rounded-t-xl shadow-sm border border-[#0D4F5C]/10 hover:bg-gray-50 flex flex-col items-center justify-center space-y-1"
            >
              <div className="w-8 h-1 bg-gray-300 rounded-full" />
              <span className="text-xs text-gray-500 font-semibold">{isComposerExpanded ? "تصغير" : "فكرة جديدة"}</span>
            </button>

            <div className={isComposerExpanded ? "block" : "hidden"}>
              <form onSubmit={handleGenerate} className="space-y-4">
                <textarea
                  value={rawInput}
                  onChange={(e) => setRawInput(e.target.value)}
                  className="w-full h-32 p-4 rounded-xl border border-[#0D4F5C]/20 bg-white/50 focus:ring-2 focus:ring-[#C4933F] focus:outline-none resize-none transition-all"
                  placeholder="الفكرة الأساسية (بصمتك، صوتك مفرغ، أو نص خام)..."
                  disabled={isGenerating}
                />
                <div className="flex gap-4 items-center">
                  <select
                    value={postType}
                    onChange={(e) => setPostType(e.target.value)}
                    className="flex-1 p-3 rounded-xl border border-[#0D4F5C]/20 bg-white focus:ring-2 focus:ring-[#C4933F] focus:outline-none"
                    disabled={isGenerating}
                  >
                    <option value="reflection">تأمل (Reflection)</option>
                    <option value="clinic story">قصة من العيادة (Clinic Story)</option>
                    <option value="promo">ترويج (Promo / Offer)</option>
                    <option value="prayer / reflection">دعاء أو نية (Prayer / Intention)</option>
                  </select>
                  <button
                    type="submit"
                    disabled={isGenerating || !rawInput.trim()}
                    className="flex-1 py-3 text-white font-bold rounded-xl transition-all shadow-md bg-[#0D4F5C] hover:bg-[#093a44] disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center space-x-2 rtl:space-x-reverse"
                  >
                    {isGenerating ? "جاري الصياغة..." : "صياغة المنشور ✨"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>

        {/* --- REVIEW & APPROVED STATE SHARED CONTENT --- */}
        {!isLoadingDraft && draft && (appState === "review" || appState === "approved") && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-2xl font-bold border-b-4 border-[#C4933F] pb-2 inline-block">
                {appState === "approved" ? "نص معتمد جاهز للنشر 🎉" : "مراجعة المسودة"}
              </h2>
              <div className="flex space-x-2 rtl:space-x-reverse">
                <div className="px-4 py-2 bg-white/50 rounded-full border border-[#0D4F5C]/20 text-sm font-semibold">
                  {draft.model_used}
                </div>
                <button
                  onClick={() => {
                    setDraft(null);
                    setDraftId(null);
                    setAppState("compose");
                    setRawInput("");
                  }}
                  className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-sm font-semibold transition text-gray-800"
                >
                  صياغة جديدة +
                </button>
              </div>
            </div>

            {draft.safety_flags && (
              <div className="p-4 bg-orange-50 border border-orange-200 text-orange-800 rounded-xl">
                <strong>⚠️ تنبيه أمان:</strong> {draft.safety_flags}
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="md:col-span-2 space-y-6">
                <div className="bg-white/80 backdrop-blur shadow-sm p-6 rounded-2xl border border-[#0D4F5C]/10 relative">
                  <h3 className="text-sm font-bold text-[#C4933F] uppercase tracking-wider mb-4">النص الرئيسي (Body)</h3>
                  {appState === "approved" && (
                    <button
                      onClick={handleCopyMainPost}
                      className="absolute top-4 left-4 p-2 text-gray-500 hover:text-[#0D4F5C] hover:bg-gray-100 rounded-lg transition-colors"
                      title="نسخ النص"
                    >
                      {mainCopySuccess ? "✅ منسوخ" : "📋 نسخ"}
                    </button>
                  )}
                  <textarea
                    className="w-full h-96 p-4 rounded-xl bg-transparent border-none focus:ring-0 resize-none text-lg leading-relaxed dark:text-gray-900"
                    value={draft.body}
                    readOnly
                  />
                </div>
              </div>

              <div className="space-y-6">
                <div className="bg-white/80 backdrop-blur shadow-sm p-6 rounded-2xl border border-[#0D4F5C]/10">
                  <h3 className="text-sm font-bold text-[#C4933F] uppercase tracking-wider mb-2">الزاوية (Angle)</h3>
                  <p className="text-sm text-gray-700 leading-relaxed">{draft.angle}</p>
                </div>

                <div className="bg-white/80 backdrop-blur shadow-sm p-6 rounded-2xl border border-[#0D4F5C]/10">
                  <h3 className="text-sm font-bold text-[#C4933F] uppercase tracking-wider mb-2">الخطاف (Hook)</h3>
                  <p className="text-sm text-gray-700 font-semibold">{draft.hook}</p>
                </div>

                <div className="bg-white/80 backdrop-blur shadow-sm p-6 rounded-2xl border border-[#0D4F5C]/10">
                  <h3 className="text-sm font-bold text-[#C4933F] uppercase tracking-wider mb-2">الدعوة (CTA)</h3>
                  <p className="text-sm text-gray-700 font-semibold">{draft.cta}</p>
                </div>
              </div>
            </div>

            {/* --- REVIEW ONLY SECTION --- */}
            {appState === "review" && (
              <>
                <div className="bg-[#0D4F5C] text-white p-6 rounded-2xl shadow-lg mt-8">
                  <h3 className="text-xl font-bold mb-4">هل ترغبين بتعديل شيء؟ ✍️</h3>
                  <div className="flex gap-4">
                    <input
                      type="text"
                      className="flex-1 p-4 rounded-xl text-[#0D4F5C] focus:outline-none focus:ring-2 focus:ring-[#C4933F]"
                      placeholder="مثال: اجعل النص أقصر، أو خفف من العاطفة..."
                      value={editInstruction}
                      onChange={(e) => setEditInstruction(e.target.value)}
                      disabled={isRevising || isApproving}
                    />
                    <button
                      onClick={handleRevise}
                      disabled={isRevising || !editInstruction.trim() || isApproving}
                      className="bg-[#C4933F] hover:bg-[#b08030] text-white px-8 font-bold rounded-xl transition-colors disabled:opacity-50"
                    >
                      {isRevising ? "جاري التعديل..." : "تعديل"}
                    </button>
                  </div>
                </div>

                <div className="flex justify-end pt-4">
                  <button
                    onClick={handleApprove}
                    disabled={isApproving || isRevising}
                    className="bg-green-600 hover:bg-green-700 text-white px-12 py-4 rounded-xl font-bold text-xl shadow-md transition-colors disabled:opacity-50"
                  >
                    {isApproving ? "جاري الاعتماد..." : "اعتماد هذا النص ✅"}
                  </button>
                </div>
              </>
            )}

            {/* --- APPROVED ONLY SECTION (Platform Adaptation) --- */}
            {appState === "approved" && (
              <div className="bg-white/80 backdrop-blur shadow-sm p-8 rounded-3xl border border-[#0D4F5C]/20 mt-8 mb-12">
                <h3 className="text-xl font-bold text-[#0D4F5C] mb-4">تكييف النص لمنصة محددة 📱</h3>
                <p className="text-gray-600 mb-6 text-sm">النص المعتمد جاهز للنشر. يمكنك هنا تكييفه تلقائياً ليتناسب مع طبيعة المنصات الأخرى.</p>
                
                <div className="flex flex-wrap gap-3 mb-6">
                  {PLATFORMS.map((p) => {
                    const isSelected = adaptPlatforms.includes(p.id);
                    return (
                      <button
                        key={p.id}
                        onClick={() => {
                          if (isSelected) {
                            setAdaptPlatforms(adaptPlatforms.filter(id => id !== p.id));
                          } else {
                            setAdaptPlatforms([...adaptPlatforms, p.id]);
                          }
                        }}
                        className={`px-4 py-2 rounded-full border text-sm font-semibold transition-colors ${
                          isSelected 
                            ? "bg-[#C4933F] text-white border-[#C4933F]" 
                            : "bg-white text-gray-600 border-gray-200 hover:border-[#C4933F]"
                        }`}
                        disabled={isAdapting}
                      >
                        {p.label}
                      </button>
                    );
                  })}
                </div>

                <div className="flex gap-4">
                  <button
                    onClick={handleAdapt}
                    disabled={isAdapting || adaptPlatforms.length === 0}
                    className="bg-[#0D4F5C] hover:bg-[#093a44] text-white px-8 py-3 font-bold rounded-xl transition-colors disabled:opacity-50 flex items-center shadow-md w-full justify-center"
                  >
                    {isAdapting ? "جاري التكييف..." : "تكييف النص للمنصات المحددة 🔄"}
                  </button>
                </div>

                {Object.keys(adaptResults).length > 0 && (
                  <div className="mt-8 space-y-6">
                    {Object.entries(adaptResults).map(([platform, text]) => (
                      <div key={platform} className="animate-in fade-in duration-500 pt-6 border-t border-gray-100">
                        <div className="flex justify-between items-center mb-4">
                          <h4 className="font-bold text-[#C4933F]">النص المخصص لـ ({PLATFORMS.find(p => p.id === platform)?.label || platform}):</h4>
                          <button
                            onClick={() => handleCopyPlatform(platform, text)}
                            className="text-sm px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-gray-700 font-semibold transition"
                          >
                            {copiedPlatform === platform ? "✅ تم النسخ" : "📋 نسخ"}
                          </button>
                        </div>
                        <textarea
                          className="w-full h-64 p-4 rounded-xl bg-gray-50 border border-gray-200 focus:ring-0 resize-none text-md leading-relaxed dark:text-gray-800"
                          value={text}
                          readOnly
                        />
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </>
  );
}

export default function Home() {
  return (
    <Suspense fallback={<div className="text-center mt-20">جاري التحميل...</div>}>
      <MainWorkspace />
    </Suspense>
  );
}
