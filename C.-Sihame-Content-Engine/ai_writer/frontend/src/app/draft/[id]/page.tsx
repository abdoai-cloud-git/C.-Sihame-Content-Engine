"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getApiBaseUrl } from "@/lib/api";

export default function DraftReview({ params }: { params: { id: string } }) {
  const router = useRouter();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [draft, setDraft] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [editInstruction, setEditInstruction] = useState("");
  const [isRevising, setIsRevising] = useState(false);
  const [isApproving, setIsApproving] = useState(false);

  useEffect(() => {
    fetchDraft();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.id]);

  const fetchDraft = async () => {
    try {
      const apiUrl = getApiBaseUrl();
      const res = await fetch(`${apiUrl}/api/v1/content/${params.id}`);
      if (!res.ok) throw new Error("لم يتم العثور على المسودة");
      const data = await res.json();
      setDraft(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleRevise = async () => {
    if (!editInstruction.trim()) return;
    setIsRevising(true);
    try {
      const apiUrl = getApiBaseUrl();
      const res = await fetch(`${apiUrl}/api/v1/content/revise`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          draft_id: params.id,
          edit_instruction: editInstruction,
        }),
      });
      if (!res.ok) throw new Error("فشل التعديل");
      const data = await res.json();
      setDraft({ ...draft, ...data });
      setEditInstruction("");
    } catch (err) {
      alert((err as Error).message);
    } finally {
      setIsRevising(false);
    }
  };

  const handleApprove = async () => {
    setIsApproving(true);
    try {
      // In a real app, you might let them edit the text manually first
      // For now, we will just approve the body as is
      const finalApprovedText = draft.body;
      const apiUrl = getApiBaseUrl();
      const res = await fetch(`${apiUrl}/api/v1/content/approve-text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          draft_id: params.id,
          approved_text: finalApprovedText,
        }),
      });
      if (!res.ok) throw new Error("فشل اعتماد النص");
      
      // Navigate somewhere or show success
      alert("تم اعتماد النص بنجاح! جاهز للنشر.");
      router.push("/");
    } catch (err) {
      alert((err as Error).message);
      setIsApproving(false);
    }
  };

  if (loading) return <div className="text-center mt-20 text-xl animate-pulse">جاري تحميل المسودة...</div>;
  if (error) return <div className="text-center mt-20 text-red-500 font-bold">{error}</div>;

  return (
    <div className="max-w-4xl mx-auto mt-8 space-y-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold border-b-4 border-[#C4933F] pb-2 inline-block">مراجعة المسودة</h1>
        <div className="px-4 py-2 bg-white/50 rounded-full border border-[#0D4F5C]/20 text-sm font-semibold">
          النموذج: {draft.model_used}
        </div>
      </div>

      {draft.safety_flags && (
        <div className="p-4 bg-orange-50 border border-orange-200 text-orange-800 rounded-xl">
          <strong>⚠️ تنبيه أمان:</strong> {draft.safety_flags}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-6">
          <div className="bg-white/80 backdrop-blur shadow-sm p-6 rounded-2xl border border-[#0D4F5C]/10">
            <h3 className="text-sm font-bold text-[#C4933F] uppercase tracking-wider mb-4">النص الرئيسي (Body)</h3>
            <textarea
              className="w-full h-96 p-4 rounded-xl bg-transparent border-none focus:ring-0 resize-none text-lg leading-relaxed"
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
            <p className="text-sm text-gray-700">{draft.cta}</p>
          </div>
        </div>
      </div>

      {/* Revision Section */}
      <div className="bg-[#0D4F5C] text-white p-6 rounded-2xl shadow-lg mt-8">
        <h3 className="text-xl font-bold mb-4">هل ترغبين بتعديل شيء؟ ✍️</h3>
        <div className="flex gap-4">
          <input
            type="text"
            className="flex-1 p-4 rounded-xl text-[#0D4F5C] focus:outline-none focus:ring-2 focus:ring-[#C4933F]"
            placeholder="مثال: اجعل النص أقصر، أو خفف من العاطفة، أو أضف سؤالاً في النهاية..."
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

      {/* Approval Section */}
      <div className="flex justify-end pt-4 pb-12">
        <button
          onClick={handleApprove}
          disabled={isApproving || isRevising}
          className="bg-green-600 hover:bg-green-700 text-white px-12 py-4 rounded-xl font-bold text-xl shadow-md transition-colors disabled:opacity-50"
        >
          {isApproving ? "جاري الاعتماد..." : "اعتماد هذا النص ✅"}
        </button>
      </div>
    </div>
  );
}
