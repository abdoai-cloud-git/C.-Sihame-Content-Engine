"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { getApiBaseUrl } from "@/lib/api";
import HistoryDrawer from "@/components/HistoryDrawer";
import { useQueryClient } from "@tanstack/react-query";

/* ─── Platform config with icons & brand colors ─── */
const PLATFORMS = [
  { id: "facebook", label: "فيسبوك", icon: "📘", color: "#1877F2", bg: "bg-[#1877F2]/10", border: "border-[#1877F2]/30", activeBg: "bg-[#1877F2]" },
  { id: "instagram", label: "إنستغرام", icon: "📸", color: "#E4405F", bg: "bg-[#E4405F]/10", border: "border-[#E4405F]/30", activeBg: "bg-[#E4405F]" },
  { id: "telegram", label: "تليغرام", icon: "✈️", color: "#0088CC", bg: "bg-[#0088CC]/10", border: "border-[#0088CC]/30", activeBg: "bg-[#0088CC]" },
  { id: "tiktok", label: "تيك توك", icon: "🎵", color: "#000000", bg: "bg-gray-100", border: "border-gray-300", activeBg: "bg-black" },
];

/* ─── Quick-start post types for welcome state ─── */
const QUICK_START = [
  { type: "reflection", label: "تأمل", emoji: "🧘‍♀️", desc: "منشور تأملي عميق", color: "from-teal-500/10 to-emerald-500/10" },
  { type: "clinic story", label: "قصة جلسة", emoji: "💆‍♀️", desc: "قصة من العيادة", color: "from-amber-500/10 to-orange-500/10" },
  { type: "promo", label: "ترويجي", emoji: "✨", desc: "عرض أو دعوة", color: "from-purple-500/10 to-pink-500/10" },
  { type: "prayer / reflection", label: "دعاء أو نية", emoji: "🤲", desc: "نية أو دعاء صباحي", color: "from-blue-500/10 to-cyan-500/10" },
];

function MainWorkspace() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();

  // Navigation / Drawer
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  // App State: compose | review | approved
  const [appState, setAppState] = useState<"compose" | "review" | "approved">("compose");
  const [isComposerExpanded, setIsComposerExpanded] = useState(false);

  // Compose State
  const [rawInput, setRawInput] = useState("");
  const [moodContext, setMoodContext] = useState("");
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
  const [isRejecting, setIsRejecting] = useState(false);
  const [showRejectInput, setShowRejectInput] = useState(false);
  const [rejectReason, setRejectReason] = useState("");

  // Adapt State
  const [adaptPlatforms, setAdaptPlatforms] = useState<string[]>([]);
  const [isAdapting, setIsAdapting] = useState(false);
  const [adaptResults, setAdaptResults] = useState<Record<string, string>>({});
  const [copiedPlatform, setCopiedPlatform] = useState<string | null>(null);
  const [mainCopySuccess, setMainCopySuccess] = useState(false);

  // Design State
  const [designTitle, setDesignTitle] = useState('');
  const [designSupport, setDesignSupport] = useState('');
  const [designSymbol, setDesignSymbol] = useState('');
  const [designConceptAr, setDesignConceptAr] = useState('');
  const [designImageUrl, setDesignImageUrl] = useState('');
  const [designLoading, setDesignLoading] = useState(false);
  const [extractLoading, setExtractLoading] = useState(false);

  // Load draft from URL if any
  useEffect(() => {
    const urlDraftId = searchParams.get("draftId");
    if (urlDraftId) {
      loadDraft(urlDraftId);
      router.replace("/");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  // Auto-minimize composer when drawer opens
  useEffect(() => {
    if (isDrawerOpen) setIsComposerExpanded(false);
  }, [isDrawerOpen]);

  const invalidateHistory = () => {
    queryClient.invalidateQueries({ queryKey: ["history"] });
  };

  const buildPostText = (content: {
    approved_text?: string | null;
    hook?: string | null;
    body?: string | null;
    cta?: string | null;
  }) => {
    const approved = content.approved_text?.trim();
    if (approved) return approved;

    return [content.hook, content.body, content.cta]
      .map((s) => s?.trim())
      .filter(Boolean)
      .join("\n\n");
  };

  const parseApiError = async (response: Response, fallbackMessage: string) => {
    try {
      const errorData = await response.json();
      return errorData.detail || fallbackMessage;
    } catch {
      return fallbackMessage;
    }
  };

  const loadDraft = async (id: string) => {
    setIsLoadingDraft(true);
    setError("");
    setAdaptResults({});
    
    try {
      const apiUrl = getApiBaseUrl();
      if (!apiUrl) {
        setError("API URL is not configured. Please check environment variables.");
        return;
      }
      const res = await fetch(`${apiUrl}/api/v1/content/${id}`);
      if (!res.ok) throw new Error("لم يتم العثور على المسودة");
      const data = await res.json();
      setDraft(data);
      setDraftId(id);
      setRawInput(data.raw_input || "");
      setMoodContext(data.mood_context || "");
      setPostType(data.post_type || "reflection");
      setEditInstruction("");
      setRejectReason("");
      setShowRejectInput(false);
      setAdaptResults({});
      setAdaptPlatforms([]);
      setCopiedPlatform(null);
      setMainCopySuccess(false);
      setDesignTitle(data.design_title || "");
      setDesignSupport(data.design_support || "");
      setDesignSymbol(data.design_symbol || "");
      setDesignConceptAr("");
      setDesignImageUrl(data.design_image_url || "");
      
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
    } finally {
      setIsLoadingDraft(false);
    }
  };

  const generateDraft = async (options?: {
    rawInput?: string;
    moodContext?: string;
    postType?: string;
    platform?: string;
    rejectionFeedback?: string;
  }) => {
    const nextRawInput = options?.rawInput ?? rawInput;
    const nextMoodContext = options?.moodContext ?? moodContext;
    const nextPostType = options?.postType ?? postType;
    const nextPlatform = options?.platform ?? draft?.platform ?? "general";
    const nextRejectionFeedback = options?.rejectionFeedback?.trim() || undefined;

    if (!nextRawInput.trim()) {
      throw new Error("الرجاء كتابة الفكرة أولاً");
    }

    setIsGenerating(true);
    setError("");

    try {
      const apiUrl = getApiBaseUrl();
      if (!apiUrl) {
        throw new Error("API URL is not configured. Please check environment variables.");
      }
      const response = await fetch(`${apiUrl}/api/v1/content/draft`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          raw_input: nextRawInput,
          mood_context: nextMoodContext.trim() || undefined,
          post_type: nextPostType,
          platform: nextPlatform,
          rejection_feedback: nextRejectionFeedback,
        }),
      });

      if (!response.ok) {
        throw new Error(await parseApiError(response, "حدث خطأ أثناء التوليد"));
      }

      const data = await response.json();
      setRawInput(nextRawInput);
      setPostType(nextPostType);
      setDraft(data);
      setDraftId(data.draft_id);
      setAppState("review");
      setIsComposerExpanded(false);
      invalidateHistory();
      return data;
    } catch (err) {
      console.error(err);
      setError((err as Error).message || "حدث خطأ غير متوقع.");
      throw err;
    } finally {
      setIsGenerating(false);
    }
  };

  // 1. Generate new draft
  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await generateDraft();
    } catch {
      // generateDraft already set UI error state
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
      if (!res.ok) throw new Error(await parseApiError(res, "فشل التعديل"));
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

  /**
   * 3. Approve draft
   * Transitions the app to the 'approved' state and updates the backend record.
   */
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
          approved_text: buildPostText(draft),
        }),
      });
      if (!res.ok) throw new Error(await parseApiError(res, "فشل اعتماد النص"));
      
      const data = await res.json();
      setDraft({ ...draft, status: data.status || "approved_text", approved_text: data.approved_text });
      setAppState("approved");
      invalidateHistory();
    } catch (err) {
      alert((err as Error).message);
    } finally {
      setIsApproving(false);
    }
  };

  /**
   * 3b. Reject and Regenerate
   * The core of the feedback loop.
   * 1. Calls the /reject endpoint to mark the current draft as REJECTED and store the reason.
   * 2. Immediately triggers a fresh generation attempt using the stored draft context.
   * 3. Passes the rejection reason back into generation as an active correction constraint.
   */
  const handleRejectAndRegenerate = async (e: React.FormEvent | React.MouseEvent) => {
    e.preventDefault();
    if (!draftId || !draft) return;
    setIsRejecting(true);
    try {
      const apiUrl = getApiBaseUrl();
      // First hit the reject endpoint
      const res = await fetch(`${apiUrl}/api/v1/content/reject`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          draft_id: draftId,
          reason: rejectReason.trim() || undefined,
        }),
      });
      if (!res.ok) throw new Error(await parseApiError(res, "فشل رفض النص"));

      const feedback = rejectReason.trim();

      // Reset UI reject state before regeneration starts
      setRejectReason("");
      setShowRejectInput(false);

      // Regenerate from the stored draft context, not from whatever local composer state happens to be left.
      try {
        await generateDraft({
          rawInput: draft.raw_input,
          postType: draft.post_type,
          platform: draft.platform,
          rejectionFeedback: feedback,
        });
      } catch (regenerationError) {
        setDraft({ ...draft, status: "rejected" });
        setAppState("review");
        setError(`تم رفض المسودة لكن إعادة التوليد فشلت: ${(regenerationError as Error).message}`);
      }
    } catch (err) {
      alert((err as Error).message);
    } finally {
      setIsRejecting(false);
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
      if (!res.ok) throw new Error(await parseApiError(res, "فشل التكيف مع المنصة"));
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
      const fullText = buildPostText(draft);
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

  const handleNewDraft = () => {
    setDraft(null);
    setDraftId(null);
    setAppState("compose");
    setRawInput("");
    setAdaptResults({});
    setAdaptPlatforms([]);
    setCopiedPlatform(null);
    setMainCopySuccess(false);
    setEditInstruction("");
    setRejectReason("");
    setShowRejectInput(false);
    setError("");
    setIsComposerExpanded(false);
    setDesignTitle('');
    setDesignSupport('');
    setDesignSymbol('');
    setDesignConceptAr('');
    setDesignImageUrl('');
  };

  const handleQuickStart = (type: string) => {
    setPostType(type);
    setIsComposerExpanded(true);
  };

  /* ─── State label for breadcrumb ─── */
  const stateLabel = appState === "compose" 
    ? "صياغة جديدة" 
    : appState === "review" 
    ? "مراجعة المسودة" 
    : "جاهز للنشر ✅";
  const stateColor = appState === "compose" 
    ? "bg-[#0D4F5C]/10 text-[#0D4F5C]" 
    : appState === "review" 
    ? "bg-amber-100 text-amber-800" 
    : "bg-green-100 text-green-800";

  // ─── Design Handlers ───
  const handleExtractDesignText = async () => {
    if (!draftId) return;
    setExtractLoading(true);
    try {
      const apiUrl = getApiBaseUrl();
      const res = await fetch(`${apiUrl}/api/v1/content/design/extract`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ draft_id: draftId }),
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'فشل استخراج النص');
      }
      const data = await res.json();
      setDesignTitle(data.design_title);
      setDesignSupport(data.design_support);
      setDesignSymbol(data.design_symbol || '');
      setDesignConceptAr(data.design_concept_ar || '');
    } catch (err) {
      alert((err as Error).message);
    } finally {
      setExtractLoading(false);
    }
  };

  const handleGenerateDesignImage = async () => {
    if (!draftId || !designTitle.trim() || !designSupport.trim()) return;
    setDesignLoading(true);
    setDesignImageUrl('');
    try {
      const apiUrl = getApiBaseUrl();
      const res = await fetch(`${apiUrl}/api/v1/content/design/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          draft_id: draftId,
          design_title: designTitle,
          design_support: designSupport,
          design_symbol: designSymbol,
          design_concept_ar: designConceptAr,
        }),
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'فشل توليد الصورة');
      }
      const data = await res.json();
      setDesignImageUrl(data.design_image_url);
    } catch (err) {
      alert((err as Error).message);
    } finally {
      setDesignLoading(false);
    }
  };

  return (
    <>
      <HistoryDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        onRestore={loadDraft}
      />

      <div className="max-w-3xl mx-auto pb-40 relative">
        {/* ─── HEADER ─── */}
        <div className="flex justify-between items-center mb-2 px-4">
          <button
            onClick={() => setIsDrawerOpen(true)}
            className="w-10 h-10 flex items-center justify-center text-[#0D4F5C] hover:bg-[#0D4F5C]/10 rounded-full transition-all"
            title="سجل المسودات"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>
          <h1 className="text-2xl font-bold text-center text-[#0D4F5C]">
            مساعد الكوتش سهام 🪄
          </h1>
          <div className="w-10" /> {/* spacer */}
        </div>

        {/* ─── BREADCRUMB ─── */}
        <div className="flex justify-center mb-6">
          <span className={`px-4 py-1.5 rounded-full text-xs font-bold ${stateColor} transition-all`}>
            {stateLabel}
          </span>
        </div>

        {/* ─── GLOBAL ERROR ─── */}
        {error && (
          <div className="p-3 mb-4 mx-4 bg-red-50 text-red-600 rounded-xl border border-red-100 text-sm animate-slide-up">
            ❌ {error}
          </div>
        )}

        {/* ─── LOADING SKELETON ─── */}
        {(isLoadingDraft || isGenerating) && !draft && (
          <div className="px-4 space-y-4 animate-fade-in">
            <div className="skeleton h-6 w-48 mx-auto" />
            <div className="skeleton h-64 w-full" />
            <div className="skeleton h-20 w-full" />
            <div className="skeleton h-20 w-full" />
            <div className="flex gap-4">
              <div className="skeleton h-14 flex-1" />
              <div className="skeleton h-14 flex-1" />
            </div>
          </div>
        )}

        {/* ═══════════════════════════════════════════════════ */}
        {/* ─── WELCOME / EMPTY STATE ─── */}
        {/* ═══════════════════════════════════════════════════ */}
        {appState === "compose" && !draft && !isGenerating && !isLoadingDraft && (
          <div className="px-4 animate-slide-up">
            <div className="text-center mb-8 mt-8">
              <p className="text-4xl mb-3">🌿</p>
              <h2 className="text-xl font-bold text-[#0D4F5C] mb-2">أهلاً كوتش سهام</h2>
              <p className="text-sm text-gray-500">اختاري نوع المنشور أو اكتبي فكرتك مباشرة</p>
            </div>

            <div className="grid grid-cols-2 gap-3 mb-6">
              {QUICK_START.map((item) => (
                <button
                  key={item.type}
                  onClick={() => handleQuickStart(item.type)}
                  className={`p-4 rounded-2xl border border-[#0D4F5C]/10 bg-gradient-to-br ${item.color} hover:border-[#C4933F] hover:shadow-md transition-all text-center group`}
                >
                  <span className="text-2xl block mb-2 group-hover:scale-110 transition-transform">{item.emoji}</span>
                  <span className="font-bold text-sm text-[#0D4F5C] block">{item.label}</span>
                  <span className="text-xs text-gray-500">{item.desc}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* ═══════════════════════════════════════════════════ */}
        {/* ─── REVIEW & APPROVED — CLEAN LAYOUT ─── */}
        {/* ═══════════════════════════════════════════════════ */}
        {!isLoadingDraft && draft && (appState === "review" || appState === "approved") && (
          <div className="px-4 space-y-4 animate-slide-up">

            {/* ─── Sticky Copy + New Draft Bar ─── */}
            <div className="sticky top-0 z-30 bg-[#FAF7F2]/90 backdrop-blur-md py-3 flex justify-between items-center border-b border-[#0D4F5C]/5">
              <button
                onClick={handleNewDraft}
                className="px-3 py-1.5 bg-white hover:bg-gray-50 rounded-full text-xs font-bold text-gray-600 border border-gray-200 transition-all"
              >
                + صياغة جديدة
              </button>
              <button
                onClick={handleCopyMainPost}
                className="px-4 py-1.5 bg-[#0D4F5C] hover:bg-[#093a44] text-white rounded-full text-xs font-bold transition-all flex items-center gap-1.5"
              >
                {mainCopySuccess ? "✅ تم النسخ" : "📋 نسخ المنشور"}
              </button>
            </div>

            {/* ─── Safety Note ─── */}
            {draft.safety_flags && (
              <div className="p-3 bg-amber-50 border border-amber-200 text-amber-800 rounded-xl text-sm leading-relaxed">
                <strong>⚠️ ملاحظة:</strong> {draft.safety_flags}
              </div>
            )}

            {/* ─── Approved Success Banner ─── */}
            {appState === "approved" && (
              <div className="bg-green-50 border border-green-200 rounded-2xl p-4 flex items-center gap-3 animate-slide-up">
                <span className="text-2xl">🎉</span>
                <div>
                  <p className="font-bold text-green-800 text-sm">تم اعتماد النص بنجاح</p>
                  <p className="text-xs text-green-600">يمكنك نسخه أو تكييفه للمنصات الأخرى</p>
                </div>
              </div>
            )}

            {/* ─── Main Post — Single Clean Card ─── */}
            <div className={`bg-white/80 backdrop-blur-sm rounded-2xl border shadow-sm overflow-hidden ${
              appState === "approved" 
                ? "border-green-200" 
                : "border-amber-200"
            }`}>
              {/* Status Badge */}
              <div className={`px-5 py-2.5 flex items-center justify-between ${
                appState === "approved" 
                  ? "bg-green-50 border-b border-green-100" 
                  : "bg-amber-50 border-b border-amber-100"
              }`}>
                <span className={`text-xs font-bold flex items-center gap-1.5 ${
                  appState === "approved" ? "text-green-700" : "text-amber-700"
                }`}>
                  {appState === "approved" ? "✅ معتمد — جاهز للنشر" : "⏳ قيد المراجعة"}
                </span>
                {draft.model_used && (
                  <span className="text-[10px] text-gray-400 font-mono">{draft.model_used}</span>
                )}
              </div>

              {/* Hook */}
              {draft.hook && (
                <div className="px-5 pt-4 pb-3 border-b border-dashed border-[#0D4F5C]/10">
                  <p className="text-xs font-bold text-[#C4933F] mb-1.5">الخطاف</p>
                  <p className="text-base font-semibold text-[#0D4F5C] leading-relaxed">{draft.hook}</p>
                </div>
              )}
              
              {/* Body */}
              <div className="px-5 py-4">
                <p className="text-xs font-bold text-[#C4933F] mb-2">النص الرئيسي</p>
                <div className="text-base text-gray-800 leading-[1.9] whitespace-pre-wrap">{draft.body}</div>
              </div>
              
              {/* CTA */}
              {draft.cta && (
                <div className="px-5 pt-3 pb-5 border-t border-dashed border-[#0D4F5C]/10">
                  <p className="text-xs font-bold text-[#C4933F] mb-1.5">الدعوة للتفاعل</p>
                  <p className="text-base font-semibold text-[#0D4F5C] leading-relaxed">{draft.cta}</p>
                </div>
              )}
            </div>

            {/* ─── Angle (collapsible detail) ─── */}
            {draft.angle && (
              <details className="group">
                <summary className="text-xs font-bold text-gray-400 cursor-pointer hover:text-[#C4933F] transition-colors list-none flex items-center gap-1">
                  <span className="group-open:rotate-90 transition-transform">◀</span>
                  الزاوية المستخدمة
                </summary>
                <p className="mt-2 text-sm text-gray-500 pr-4 leading-relaxed">{draft.angle}</p>
              </details>
            )}

            {/* ═══ REVIEW ONLY ═══ */}
            {appState === "review" && (
              <div className="space-y-3 pt-2">
                {/* Edit Instruction */}
                <div className="bg-[#0D4F5C] p-4 rounded-2xl">
                  <div className="flex gap-3">
                    <input
                      type="text"
                      className="flex-1 p-3 rounded-xl text-sm text-[#0D4F5C] focus:outline-none focus:ring-2 focus:ring-[#C4933F]"
                      placeholder="تعديل: مثلاً اجعله أقصر..."
                      value={editInstruction}
                      onChange={(e) => setEditInstruction(e.target.value)}
                      disabled={isRevising || isApproving}
                      onKeyDown={(e) => e.key === "Enter" && handleRevise()}
                    />
                    <button
                      onClick={handleRevise}
                      disabled={isRevising || !editInstruction.trim() || isApproving}
                      className="bg-[#C4933F] hover:bg-[#b08030] text-white px-5 font-bold rounded-xl transition-colors disabled:opacity-50 text-sm"
                    >
                      {isRevising ? (
                        <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spinner" />
                      ) : "تعديل ✍️"}
                    </button>
                  </div>
                </div>

                {/* Approve Button */}
                <button
                  onClick={handleApprove}
                  disabled={isApproving || isRevising || isRejecting}
                  className="w-full bg-gradient-to-l from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 text-white py-4 rounded-2xl font-bold text-lg shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {isApproving ? (
                    <>
                      <span className="inline-block w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spinner" />
                      جاري الاعتماد...
                    </>
                  ) : "اعتماد هذا النص ✅"}
                </button>

                {/* Reject & Regenerate UI */}
                {showRejectInput ? (
                  <div className="bg-amber-50 border border-amber-200 p-4 rounded-2xl space-y-3 animate-slide-up mt-2">
                    <p className="text-sm font-bold text-amber-800">لماذا لم يعجبك هذا النص؟ (اختياري)</p>
                    <textarea
                      value={rejectReason}
                      onChange={(e) => setRejectReason(e.target.value)}
                      className="w-full p-3 rounded-xl border border-amber-200 bg-white focus:outline-none focus:ring-2 focus:ring-amber-500 text-sm resize-none h-20"
                      placeholder="مثال: النص طويل جداً ولا يعكس شخصيتي..."
                      disabled={isRejecting}
                      autoFocus
                    />
                    <div className="flex gap-2">
                      <button
                        onClick={handleRejectAndRegenerate}
                        disabled={isRejecting}
                        className="flex-1 bg-amber-600 hover:bg-amber-700 text-white font-bold py-2.5 rounded-xl text-sm flex items-center justify-center gap-2 transition-colors"
                      >
                        {isRejecting ? (
                          <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spinner" />
                        ) : "تأكيد الرفض وإعادة التوليد 🔄"}
                      </button>
                      <button
                        onClick={() => { setShowRejectInput(false); setRejectReason(""); }}
                        disabled={isRejecting}
                        className="px-4 bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold rounded-xl text-sm transition-colors"
                      >
                        إلغاء
                      </button>
                    </div>
                  </div>
                ) : (
                  <button
                    onClick={() => setShowRejectInput(true)}
                    disabled={isApproving || isRevising || isRejecting}
                    className="w-full bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 py-3 rounded-2xl font-bold text-sm shadow-sm transition-all disabled:opacity-50 flex items-center justify-center gap-2 mt-2"
                  >
                    رفض وإعادة توليد 🔄
                  </button>
                )}
              </div>
            )}

            {/* ═══ APPROVED ONLY — Platform Adaptation ═══ */}
            {appState === "approved" && (
              <div className="bg-gradient-to-br from-[#0D4F5C]/5 to-[#C4933F]/5 p-5 rounded-2xl border border-[#0D4F5C]/10 space-y-4">
                <div className="text-center">
                  <h3 className="font-bold text-[#0D4F5C] mb-1">تكييف للمنصات 📱</h3>
                  <p className="text-xs text-gray-500">اختاري المنصات وسنكيّف النص تلقائياً</p>
                </div>
                
                <div className="flex flex-wrap gap-2 justify-center">
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
                        className={`px-4 py-2.5 rounded-full text-sm font-bold transition-all flex items-center gap-2 ${
                          isSelected 
                            ? `${p.activeBg} text-white shadow-md scale-105` 
                            : `${p.bg} ${p.border} border text-gray-700 hover:shadow-sm`
                        }`}
                        disabled={isAdapting}
                      >
                        <span>{p.icon}</span>
                        {p.label}
                      </button>
                    );
                  })}
                </div>

                <button
                  onClick={handleAdapt}
                  disabled={isAdapting || adaptPlatforms.length === 0}
                  className="w-full bg-[#0D4F5C] hover:bg-[#093a44] text-white py-3 font-bold rounded-xl transition-all disabled:opacity-40 flex items-center justify-center gap-2 text-sm"
                >
                  {isAdapting ? (
                    <>
                      <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spinner" />
                      جاري التكييف...
                    </>
                  ) : `تكييف النص (${adaptPlatforms.length}) 🔄`}
                </button>

                {/* Adapted Results */}
                {Object.keys(adaptResults).length > 0 && (
                  <div className="space-y-4 pt-2">
                    {Object.entries(adaptResults).map(([platform, text]) => {
                      const platformInfo = PLATFORMS.find(p => p.id === platform);
                      return (
                        <div key={platform} className="animate-slide-up bg-white rounded-xl border border-gray-100 overflow-hidden">
                          <div className="flex justify-between items-center p-3 bg-gray-50">
                            <span className="font-bold text-sm">
                              {platformInfo?.icon} {platformInfo?.label}
                            </span>
                            <button
                              onClick={() => handleCopyPlatform(platform, text)}
                              className="text-xs px-3 py-1 bg-white hover:bg-gray-100 rounded-lg text-gray-600 font-semibold transition border border-gray-200"
                            >
                              {copiedPlatform === platform ? "✅ تم" : "📋 نسخ"}
                            </button>
                          </div>
                          <div className="p-4 text-sm text-gray-800 leading-relaxed whitespace-pre-wrap">{text}</div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            {/* ═══ APPROVED ONLY — 🎨 Graphics Designer Section ═══ */}
            {appState === "approved" && (
              <div className="bg-gradient-to-br from-[#C67B5C]/5 via-[#F5E6D3]/10 to-[#D4AF37]/5 p-5 rounded-2xl border border-[#C67B5C]/20 space-y-4">
                <div className="text-center">
                  <h3 className="font-bold text-[#0D4F5C] mb-1">🎨 تصميم المنشور</h3>
                  <p className="text-xs text-gray-500">استخرجي النص ثم عدّليه وولّدي صورة احترافية</p>
                </div>

                {/* Extract Button */}
                <button
                  onClick={handleExtractDesignText}
                  disabled={extractLoading || designLoading}
                  className="w-full bg-[#C67B5C] hover:bg-[#b06a4d] text-white py-3 font-bold rounded-xl transition-all disabled:opacity-50 flex items-center justify-center gap-2 text-sm"
                >
                  {extractLoading ? (
                    <>
                      <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spinner" />
                      جاري استخراج النص...
                    </>
                  ) : '📝 استخراج النص من المنشور'}
                </button>

                {/* Editable Text Fields */}
                {(designTitle || designSupport) && (
                  <div className="space-y-3 animate-slide-up">
                    <div>
                      <label className="block text-xs font-bold text-[#C67B5C] mb-1.5">العنوان</label>
                      <input
                        type="text"
                        value={designTitle}
                        onChange={(e) => setDesignTitle(e.target.value)}
                        className="w-full p-3 rounded-xl border border-[#C67B5C]/20 bg-white focus:ring-2 focus:ring-[#D4AF37] focus:outline-none text-sm text-right"
                        placeholder="العنوان الرئيسي للصورة..."
                        disabled={designLoading}
                        dir="rtl"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-[#C67B5C] mb-1.5">النص الداعم</label>
                      <textarea
                        value={designSupport}
                        onChange={(e) => setDesignSupport(e.target.value)}
                        className="w-full p-3 rounded-xl border border-[#C67B5C]/20 bg-white focus:ring-2 focus:ring-[#D4AF37] focus:outline-none text-sm text-right resize-none h-20"
                        placeholder="النص الداعم للصورة..."
                        disabled={designLoading}
                        dir="rtl"
                      />
                    </div>
                    {/* Visual Concept — editable Arabic field for the coach */}
                    <div>
                      <label className="block text-xs font-bold text-[#C67B5C] mb-1.5">الفكرة البصرية 🖼️ <span className="text-gray-400 font-normal">(يمكنك تعديلها بكلماتك الخاصة)</span></label>
                      <textarea
                        value={designConceptAr}
                        onChange={(e) => setDesignConceptAr(e.target.value)}
                        className="w-full p-3 rounded-xl border border-[#D4AF37]/30 bg-[#FDF8F0] focus:ring-2 focus:ring-[#D4AF37] focus:outline-none text-sm text-right resize-none h-24 leading-relaxed text-[#3d2b1a]"
                        placeholder="صفي ما تريدين أن تغؚ الصورة... مثلاً: أريد صورة تُظهِر يدين واحدة شديدة وأخرى مرتاحة"
                        disabled={designLoading}
                        dir="rtl"
                      />
                      <p className="text-[10px] text-gray-400 mt-1 text-right" dir="rtl">✨ سيتولى النظام تحويل فكرتك تلقائياً إلى تعليمات تقنية للمولد</p>
                    </div>

                    {/* Generate Image Button */}
                    <button
                      onClick={handleGenerateDesignImage}
                      disabled={designLoading || !designTitle.trim() || !designSupport.trim()}
                      className="w-full bg-gradient-to-l from-[#D4AF37] to-[#C4933F] hover:from-[#C4933F] hover:to-[#b08030] text-white py-3.5 font-bold rounded-xl transition-all disabled:opacity-40 flex items-center justify-center gap-2 text-sm shadow-md"
                    >
                      {designLoading ? (
                        <>
                          <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spinner" />
                          جاري توليد الصورة... (قد يستغرق دقيقة)
                        </>
                      ) : '🎨 توليد الصورة'}
                    </button>
                  </div>
                )}

                {/* Image Preview */}
                {designImageUrl && (
                  <div className="space-y-3 animate-slide-up">
                    <div className="bg-white rounded-xl border border-[#D4AF37]/30 overflow-hidden shadow-sm">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src={designImageUrl}
                        alt="التصميم المولّد"
                        className="w-full h-auto"
                      />
                    </div>
                    <div className="flex gap-2">
                      <a
                        href={designImageUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex-1 bg-[#0D4F5C] hover:bg-[#093a44] text-white py-2.5 font-bold rounded-xl transition-all text-sm text-center flex items-center justify-center gap-2"
                      >
                        ⬇️ تحميل الصورة
                      </a>
                      <button
                        onClick={handleGenerateDesignImage}
                        disabled={designLoading}
                        className="flex-1 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 py-2.5 font-bold rounded-xl text-sm transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                      >
                        🔄 إعادة التوليد
                      </button>
                    </div>
                    <p className="text-[10px] text-gray-400 text-center">⏳ رابط الصورة صالح لمدة 14 يوم</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* ═══════════════════════════════════════════════════ */}
        {/* ─── FLOATING COMPOSER / FAB ─── */}
        {/* ═══════════════════════════════════════════════════ */}

        {/* FAB Button (when composer is minimized) */}
        {!isComposerExpanded && (
          <button
            onClick={() => setIsComposerExpanded(true)}
            className="fixed bottom-6 left-1/2 -translate-x-1/2 z-40 bg-gradient-to-l from-[#C4933F] to-[#D4A34F] text-white px-6 py-3 rounded-full font-bold shadow-lg hover:shadow-xl transition-all animate-pulse-glow flex items-center gap-2"
          >
            <span className="text-lg">✨</span>
            فكرة جديدة
          </button>
        )}

        {/* Expanded Composer */}
        {isComposerExpanded && (
          <>
            {/* Backdrop */}
            <div 
              className="fixed inset-0 bg-black/10 z-40 backdrop-blur-[2px]"
              onClick={() => setIsComposerExpanded(false)}
            />
            
            {/* Composer Panel */}
            <div className="fixed bottom-0 left-0 right-0 z-50 animate-slide-up">
              <div className="max-w-3xl mx-auto">
                <div className="bg-white/95 backdrop-blur-md rounded-t-3xl shadow-[0_-10px_40px_rgba(0,0,0,0.12)] border-t border-x border-[#0D4F5C]/10 p-5 pb-8">
                  {/* Handle + Minimize */}
                  <button
                    onClick={() => setIsComposerExpanded(false)}
                    className="mx-auto block mb-4"
                  >
                    <div className="w-10 h-1 bg-gray-300 rounded-full mx-auto mb-1" />
                    <span className="text-[10px] text-gray-400 font-semibold">تصغير</span>
                  </button>

                  <form onSubmit={handleGenerate} className="space-y-3">
                    <textarea
                      value={rawInput}
                      onChange={(e) => setRawInput(e.target.value)}
                      className="w-full h-28 p-4 rounded-xl border border-[#0D4F5C]/15 bg-[#FAF7F2]/50 focus:ring-2 focus:ring-[#C4933F] focus:border-transparent focus:outline-none resize-none transition-all text-sm"
                      placeholder="الفكرة الأساسية (بصمتك، صوتك مفرغ، أو نص خام)..."
                      disabled={isGenerating}
                      autoFocus
                    />
                    <input
                      type="text"
                      value={moodContext}
                      onChange={(e) => setMoodContext(e.target.value)}
                      className="w-full p-3 rounded-xl border border-[#0D4F5C]/15 bg-white focus:ring-2 focus:ring-[#C4933F] focus:outline-none text-sm text-right text-gray-600"
                      placeholder="كيف تشعرين اليوم؟ (الحالة الداخلية - اختياري)"
                      disabled={isGenerating}
                      dir="rtl"
                    />
                    <div className="flex gap-3 items-center">
                      <select
                        value={postType}
                        onChange={(e) => setPostType(e.target.value)}
                        className="flex-1 p-3 rounded-xl border border-[#0D4F5C]/15 bg-white focus:ring-2 focus:ring-[#C4933F] focus:outline-none text-sm"
                        disabled={isGenerating}
                      >
                        <option value="reflection">تأمل</option>
                        <option value="clinic story">قصة جلسة</option>
                        <option value="promo">ترويجي</option>
                        <option value="prayer / reflection">دعاء أو نية</option>
                      </select>
                      <button
                        type="submit"
                        disabled={isGenerating || !rawInput.trim()}
                        className={`flex-1 py-3 font-bold rounded-xl transition-all shadow-md flex items-center justify-center gap-2 text-sm ${
                          rawInput.trim() && !isGenerating
                            ? "bg-gradient-to-l from-[#C4933F] to-[#D4A34F] hover:from-[#b08030] hover:to-[#C4933F] text-white shadow-[0_4px_15px_rgba(196,147,63,0.3)]"
                            : "bg-gray-200 text-gray-400 cursor-not-allowed shadow-none"
                        }`}
                      >
                        {isGenerating ? (
                          <>
                            <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spinner" />
                            جاري الصياغة...
                          </>
                        ) : "صياغة المنشور ✨"}
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          </>
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
