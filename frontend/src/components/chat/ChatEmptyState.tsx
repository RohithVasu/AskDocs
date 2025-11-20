import React from "react";

export const ChatEmptyState: React.FC = () => {
    return (
        <div className="text-center py-24">
            <div className="mb-4 text-4xl">💬</div>
            <h2 className="text-xl font-semibold">Start a new conversation</h2>
            <p className="text-sm text-muted-foreground max-w-md mx-auto mt-2">
                Ask any question about your uploaded documents and I’ll help you find the most relevant answers.
            </p>
        </div>
    );
};
