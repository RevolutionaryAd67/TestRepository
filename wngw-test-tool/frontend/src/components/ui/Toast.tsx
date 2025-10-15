import { ReactNode, useEffect, useState } from "react";

interface ToastProps {
  message: string;
}

export function Toast({ message }: ToastProps) {
  const [visible, setVisible] = useState(true);
  useEffect(() => {
    const timer = setTimeout(() => setVisible(false), 3000);
    return () => clearTimeout(timer);
  }, []);
  if (!visible) return null;
  return (
    <div className="fixed bottom-6 right-6 bg-slate-900 text-slate-100 px-4 py-2 rounded shadow-lg">
      {message}
    </div>
  );
}
