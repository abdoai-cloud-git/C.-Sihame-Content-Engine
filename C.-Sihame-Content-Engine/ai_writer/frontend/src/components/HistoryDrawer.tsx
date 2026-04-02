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

  return (
    <>
      {/* Backdrop overlay */}
      <div 
        className="fixed inset-0 bg-black/20 z-40 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />
      
      {/* Drawer */}
      <div className="fixed top-0 right-0 h-full w-80 bg-white/95 backdrop-blur-md shadow-2xl z-50 transform transition-transform overflow-y-auto border-l border-[#0D4F5C]/10 rtl:left-0 rtl:right-auto rtl:border-r rtl:border-l-0">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-[#0D4F5C]">المسودات السابقة</h2>
            <button onClick={onClose} className="text-gray-500 hover:text-black">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="space-y-4">
            {isLoading ? (
              <p className="text-gray-500 text-sm text-center mt-10 animate-pulse">جاري جلب المسودات...</p>
            ) : isError ? (
              <p className="text-red-500 text-sm text-center mt-10">حدث خطأ في جلب السجل.</p>
            ) : history.length === 0 ? (
              <p className="text-gray-500 text-sm text-center mt-10">لا يوجد سجل حتى الآن.</p>
            ) : (
              history.map((item) => (
                <div 
                  key={item.draft_id} 
                  className="p-4 rounded-xl border border-[#0D4F5C]/10 hover:border-[#C4933F] hover:shadow-sm cursor-pointer transition-all bg-white"
                  onClick={() => {
                    onRestore(item.draft_id);
                    onClose();
                  }}
                >
                  <p className="font-semibold text-sm line-clamp-2 text-[#0D4F5C] mb-2">{item.title}</p>
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>{new Date(item.updated_at).toLocaleDateString("ar-EG")}</span>
                    <span className="px-2 py-1 bg-gray-100 rounded-lg">{item.post_type}</span>
                  </div>
                  <div className="mt-2 text-xs font-medium">
                    {item.status === "approved_text" ? (
                      <span className="text-green-600">✅ معتمد</span>
                    ) : (
                      <span className="text-orange-500">⏳ قيد المراجعة</span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </>
  );
}
