"use client";

import { useQuery } from "@tanstack/react-query";
import { getApiBaseUrl } from "@/lib/api";

export type HistoryItem = {
  draft_id: string;
  title: string;
  post_type: string;
  status: string;
  updated_at: string;
};

const POST_TYPE_MAP: Record<string, { label: string; emoji: string }> = {
  reflection: { label: "تأمل", emoji: "🧘‍♀️" },
  "clinic story": { label: "قصة جلسة", emoji: "💆‍♀️" },
  promo: { label: "ترويجي", emoji: "✨" },
  "prayer / reflection": { label: "دعاء", emoji: "🤲" },
};

interface HistoryDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  onRestore: (draft_id: string) => void;
}

export default function HistoryDrawer({ isOpen, onClose, onRestore }: HistoryDrawerProps) {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["history"],
    queryFn: async () => {
      const res = await fetch(`${getApiBaseUrl()}/api/v1/content/history?limit=20`);
      if (!res.ok) throw new Error("Failed to fetch history");
      const json = await res.json();
      return json.items as HistoryItem[];
    },
    enabled: isOpen,
  });

  const history = data || [];

  if (!isOpen) return null;

  const getStatusStyle = (status: string) => {
    if (status === "approved_text" || status === "approved") {
      return {
        bg: "bg-green-50",
        border: "border-green-200",
        badge: "bg-green-100 text-green-700",
        label: "✅ معتمد",
      };
    }
    return {
      bg: "bg-amber-50/50",
      border: "border-amber-200/50",
      badge: "bg-amber-100 text-amber-700",
      label: "⏳ مسودة",
    };
  };

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/20 z-[60] backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />
      
      {/* Drawer */}
      <div className="fixed top-0 right-0 h-full w-80 bg-white/95 backdrop-blur-md shadow-2xl z-[70] overflow-y-auto border-l border-[#0D4F5C]/10 rtl:left-0 rtl:right-auto rtl:border-r rtl:border-l-0">
        <div className="p-5">
          {/* Header */}
          <div className="flex justify-between items-center mb-5">
            <h2 className="text-lg font-bold text-[#0D4F5C]">المسودات السابقة</h2>
            <button
              onClick={onClose}
              className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors text-gray-400 hover:text-gray-700"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Content */}
          <div className="space-y-3">
            {isLoading ? (
              <div className="space-y-3 mt-6">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="skeleton h-20 w-full" />
                ))}
              </div>
            ) : isError ? (
              <div className="text-center mt-10">
                <p className="text-3xl mb-2">😔</p>
                <p className="text-red-500 text-sm">حدث خطأ في جلب السجل</p>
                <p className="text-xs text-gray-400 mt-1">تأكد من اتصالك بالإنترنت</p>
              </div>
            ) : history.length === 0 ? (
              <div className="text-center mt-10">
                <p className="text-3xl mb-2">📝</p>
                <p className="text-gray-500 text-sm font-semibold">لا يوجد سجل حتى الآن</p>
                <p className="text-xs text-gray-400 mt-1">ابدئي بصياغة أول منشور</p>
              </div>
            ) : (
              history.map((item, index) => {
                const style = getStatusStyle(item.status);
                const typeInfo = POST_TYPE_MAP[item.post_type] || { label: item.post_type, emoji: "📄" };
                
                return (
                  <div 
                    key={item.draft_id}
                    className={`p-3.5 rounded-xl border ${style.border} ${style.bg} hover:shadow-md cursor-pointer transition-all group`}
                    onClick={() => {
                      onRestore(item.draft_id);
                      onClose();
                    }}
                    style={{ animationDelay: `${index * 50}ms` }}
                  >
                    <p className="font-semibold text-sm line-clamp-2 text-[#0D4F5C] mb-2 group-hover:text-[#C4933F] transition-colors">
                      {item.title}
                    </p>
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-gray-400">
                        {new Date(item.updated_at).toLocaleDateString("ar-EG")}
                      </span>
                      <div className="flex items-center gap-1.5">
                        <span className="px-2 py-0.5 bg-white/80 rounded-lg text-gray-500 font-medium">
                          {typeInfo.emoji} {typeInfo.label}
                        </span>
                        <span className={`px-2 py-0.5 rounded-lg font-bold ${style.badge}`}>
                          {style.label}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </>
  );
}
