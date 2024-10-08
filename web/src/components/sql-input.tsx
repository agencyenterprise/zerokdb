"use client";

import dynamic from "next/dynamic";
import React from "react";

// Dynamically import the Monaco Editor to ensure it works with Next.js
const MonacoEditor = dynamic(() => import("@monaco-editor/react"), {
  ssr: false,
});

interface SqlInputProps {
  label?: string;
  sqlString: string;
  setSqlString: (value: string) => void;
}

const SqlInput: React.FC<SqlInputProps> = ({
  label,
  sqlString,
  setSqlString,
}) => {
  const handleJsonChange = (value: string | undefined) => {
    if (value !== undefined) {
      setSqlString(value);
    }
  };

  return (
    <div>
      {label && (
        <label className="block mb-2 text-sm font-normal">{label}</label>
      )}
      <MonacoEditor
        height="200px"
        defaultLanguage="sql"
        theme="vs-dark"
        value={sqlString}
        onChange={handleJsonChange}
        options={{
          selectOnLineNumbers: true,
          automaticLayout: true,
        }}
      />
    </div>
  );
};

export default SqlInput;
