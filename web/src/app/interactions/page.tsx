"use client";

import { useState } from "react";

import Loading from "@/components/loading";

export default function InteractionsPage() {
  const [loading, setLoading] = useState(false);

  return (
    <div className="bg-tertiary-900 py-20 sm:py-32 min-h-screen">
      <form>
        <div className="mx-auto w-full sm:max-w-2xl">
          <h1 className="text-2xl sm:text-4xl font-bold tracking-tight text-secondary-100 pb-0 sm:pb-3 text-center mx-auto">
            DB Interactions
          </h1>
          {loading ? (
            <div className="mb-6 flex justify-center">
              <Loading size="500px" />
            </div>
          ) : (
            <div className="mb-6"></div>
          )}
        </div>
      </form>
    </div>
  );
}
