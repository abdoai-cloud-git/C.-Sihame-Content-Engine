"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function DraftRedirect({ params }: { params: { id: string } }) {
  const router = useRouter();

  useEffect(() => {
    router.replace(`/?draftId=${params.id}`);
  }, [params.id, router]);

  return (
    <div className="text-center mt-20 text-xl animate-pulse text-[#0D4F5C]">
      جاري التحويل للمساحة الرئيسية...
    </div>
  );
}
