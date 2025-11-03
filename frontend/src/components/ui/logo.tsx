import { FileText } from 'lucide-react';

export const Logo = ({ className = '' }: { className?: string }) => {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div className="ai-gradient p-2 rounded-lg">
        <FileText className="h-6 w-6 text-white" />
      </div>
      <span className="font-bold text-xl bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
        AskDocs
      </span>
    </div>
  );
};
