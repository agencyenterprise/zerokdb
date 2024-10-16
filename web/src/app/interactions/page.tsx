"use client";

import { useEffect, useState } from "react";
import Loading from "@/components/loading";
import { useChain } from "@/providers/chain";
import { toast } from "react-toastify";
import Link from "next/link";
import SqlInput from "@/components/sql-input";
import Button from "@/components/button";
import { faker } from "@faker-js/faker";
import { isValidSql } from "@/utils/sql";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlay, faSpinner } from '@fortawesome/free-solid-svg-icons';

type FormData = {
  table?: string;
  semantic?: string;
  sql?: string;
};

type Request = {
  id: string;
  name: string;
  description: string;
  status: string;
  worker_wallet: string;
  worker_id: string;
  ai_model_output: string;
  ai_model_inputs: string;
  proof?: any;
};

export default function InteractionsPage() {
  const [loading, setLoading] = useState(false);
  const { client, escrowBalance } = useChain();
  const [formData, setFormData] = useState<FormData>({});
  const [requestId, setRequestId] = useState<string>();
  const [requestResponse, setRequestResponse] = useState<any>();
  const [polling, setPolling] = useState(false);
  const [activeTab, setActiveTab] = useState<'query' | 'history'>('query');
  const [requests, setRequests] = useState<Request[]>([]);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [selectedHistoryItem, setSelectedHistoryItem] = useState<Request | null>(null);

  useEffect(() => {
    fetchRequests();
  }, []);

  const fetchRequests = async () => {
    setHistoryLoading(true);
    try {
      const response = await fetch(`/api/hub/request`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });
      if (response.ok) {
        const data = await response.json();
        setRequests(data.reverse()); // Reverse the order of requests
      } else {
        toast.error("Failed to fetch request history");
      }
    } catch (error) {
      toast.error("Failed to fetch request history");
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleRequest = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!client || !escrowBalance) {
      toast.error("Make sure your wallet is connected");
      return;
    }

    setRequestId(undefined);
    setLoading(true);
    setSelectedHistoryItem(null); // Close query details when running a new query

    try {
      const response = await fetch("/api/hub/request", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const data = await response.json();
        setRequestId(data.id);
        toast.success("Request submitted successfully!");

        // Add the new request to the history
        const newRequest: Request = {
          id: data.id,
          name: formData.sql || formData.semantic || "",
          description: "",
          status: "PENDING",
          worker_wallet: "",
          worker_id: "",
          ai_model_output: "",
          ai_model_inputs: JSON.stringify(formData),
        };
        setRequests(prevRequests => [newRequest, ...prevRequests]);

        // Start polling for updates
        pollForUpdates(data.id);
      } else {
        toast.error("Error generating inference");
      }
    } catch (error) {
      toast.error("Error generating inference");
    } finally {
      setLoading(false);
    }
  };

  const pollForUpdates = async (id: string) => {
    const intervalId = setInterval(async () => {
      try {
        const res = await fetch(`/api/hub/request/${encodeURIComponent(id)}`);
        if (res.ok) {
          const data = await res.json();
          updateRequestInHistory(data);

          if (data.status === "PROCESSED" || data.status === "FAILED") {
            clearInterval(intervalId);
            if (data.status === "PROCESSED") {
              setRequestResponse(data?.ai_model_output && JSON.parse(data.ai_model_output));
              toast.success("Response generated successfully!");
            } else {
              toast.error("Request processing failed.");
            }
          }
        } else {
          clearInterval(intervalId);
          toast.error("Failed to retrieve response.");
        }
      } catch (error) {
        clearInterval(intervalId);
        toast.error("An error occurred while polling.");
      }
    }, 5000); // Poll every 5 seconds

    // Clear interval after 5 minutes (300000 ms) to prevent indefinite polling
    setTimeout(() => clearInterval(intervalId), 300000);
  };

  const updateRequestInHistory = (updatedRequest: Request) => {
    setRequests(prevRequests =>
      prevRequests.map(req =>
        req.id === updatedRequest.id ? updatedRequest : req
      )
    );
  };

  const handleSelectExample = () => {
    const example = `SELECT * FROM users LIMIT 10`;
    setFormData({ ...formData, sql: example, semantic: "", table: "" });
  };

  const handleTableExample = () => {
    const table = faker.food.adjective().replaceAll(" ", "_").toLowerCase() + faker.number.int();
    const example = `
CREATE TABLE ${table} (
  id INT,
  name STRING
);
    `;
    setFormData({ ...formData, sql: example, semantic: "", table: "" });
  };

  const handleDataExample = () => {
    const example = faker.helpers.fake(
      `INSERT INTO users (id, name) VALUES (1, '{{food.dish}}')`
    );
    setFormData({ ...formData, sql: example, semantic: "", table: "" });
  };

  const renderToolbar = () => (
    <div className="bg-tertiary-800 p-2 flex items-center space-x-2">
      <Button
        id="submit"
        type="submit"
        label={loading ? "Running..." : "Run Query"}
        className="w-40 flex items-center justify-center"
        disabled={
          loading ||
          (!isValidSql(formData?.sql ?? "") &&
            (!formData?.semantic?.length || !formData?.table?.length)) ||
          !escrowBalance
        }
      >
      </Button>
      <Button
        type="button"
        id="select"
        label="Select Query"
        className="w-40"
        disabled={loading}
        onClick={handleSelectExample}
      />
      <Button
        type="button"
        id="insert"
        label="Insert Data"
        className="w-40"
        disabled={loading}
        onClick={handleDataExample}
      />
      <Button
        type="button"
        id="table"
        label="Create Table"
        className="w-40"
        disabled={loading}
        onClick={handleTableExample}
      />
      {!escrowBalance && (
        <Link href="/buy" className="ml-auto">
          <Button
            type="button"
            id="buy-credits"
            label="Buy Credits"
            className="w-40 bg-primary-600 hover:bg-primary-700"
          />
        </Link>
      )}
    </div>
  );

  const renderQueryEditor = () => (
    <div className="flex flex-col h-1/2 overflow-hidden">
      <form onSubmit={handleRequest} className="h-full flex flex-col">
        {renderToolbar()}
        <div className="flex-grow p-4 overflow-auto">
          <div className="flex w-full gap-3 mb-4">
            <div className="flex-1">
              <label
                htmlFor="semantic"
                className="block mb-2 text-sm font-medium text-secondary-100"
              >
                Semantic Search
              </label>
              <input
                type="text"
                id="semantic"
                className="bg-tertiary-800 border border-secondary-500 text-secondary-100 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5"
                value={formData.semantic}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    semantic: e.target.value,
                    sql: "",
                    table: e.target.value ? process.env.NEXT_PUBLIC_SEMANTIC_TABLE_NAME : "",
                  })
                }
                placeholder="Enter your semantic search query here"
              />
            </div>
            <div className="w-1/3">
              <label
                htmlFor="semantic"
                className="block mb-2 text-sm font-medium text-secondary-100"
              >
                From Table
              </label>
              <input
                type="text"
                id="table"
                className="bg-tertiary-800 border border-secondary-500 text-secondary-100 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 disabled:bg-tertiary-700 disabled:border-secondary-600 disabled:text-secondary-400 disabled:cursor-not-allowed"
                value={process.env.NEXT_PUBLIC_SEMANTIC_TABLE_NAME}
                disabled
              />
            </div>
          </div>
          <SqlInput
            label="Raw SQL Query"
            sqlString={formData?.sql ?? ""}
            setSqlString={(text) =>
              setFormData({
                ...formData,
                sql: text,
                semantic: "",
                table: "",
              })
            }
          />
          {formData?.sql &&
            formData?.sql.length > 0 &&
            !isValidSql(formData?.sql!) && (
              <p className="text-primary-500 text-sm mt-2">
                Invalid SQL query
              </p>
            )}
        </div>
      </form>
    </div>
  );

  const renderResultsToolbar = () => (
    <div className="bg-tertiary-700 p-2 flex items-center justify-between">
      <h2 className="text-lg font-semibold text-secondary-100">
        {selectedHistoryItem ? "Query Details" : "Results"}
      </h2>
      {selectedHistoryItem && (
        <Button
          id="close-details"
          type="button"
          label="Close"
          className="px-4 py-1 text-sm"
          onClick={() => setSelectedHistoryItem(null)}
        />
      )}
    </div>
  );

  const renderQueryResults = () => (
    <div className="flex flex-col h-1/2 overflow-hidden">
      {renderResultsToolbar()}
      <div className="flex-grow overflow-auto p-4">
        {polling && (
          <div className="mb-6 flex justify-center">
            <Loading size="100px" />
          </div>
        )}
        {selectedHistoryItem ? (
          <div className="bg-tertiary-800 p-4 rounded-lg">
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <h3 className="text-lg font-semibold text-secondary-100 mb-2">Name</h3>
                <p className="text-secondary-200 break-words">{selectedHistoryItem.name}</p>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-secondary-100 mb-2">Status</h3>
                <p className="text-secondary-200 break-words">{selectedHistoryItem.status}</p>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-secondary-100 mb-2">Description</h3>
                <p className="text-secondary-200 break-words">{selectedHistoryItem.description}</p>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-secondary-100 mb-2">Worker</h3>
                <p className="text-secondary-200 break-all">{selectedHistoryItem.worker_id}</p>
              </div>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-secondary-100 mb-2">AI Model Inputs</h3>
              <pre className="bg-tertiary-700 p-4 rounded-lg overflow-x-auto text-secondary-200 text-sm mb-4 whitespace-pre-wrap break-words">
                {JSON.stringify(JSON.parse(selectedHistoryItem.ai_model_inputs), null, 2)}
              </pre>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-secondary-100 mb-2">AI Model Output</h3>
              <pre className="bg-tertiary-700 p-4 rounded-lg overflow-x-auto text-secondary-200 text-sm mb-4 whitespace-pre-wrap break-words">
                {JSON.stringify(JSON.parse(selectedHistoryItem?.ai_model_output), null, 2)}
              </pre>
            </div>
            {selectedHistoryItem.proof ? (
              <div>
                <h3 className="text-lg font-semibold text-secondary-100 mb-2">Proof</h3>
                <div className="bg-tertiary-700 p-4 rounded-lg overflow-hidden text-secondary-200 text-sm">
                  <p className="truncate">{selectedHistoryItem.proof}</p>
                  <button
                    className="mt-2 text-primary-500 hover:text-primary-400"
                    onClick={() => {
                      navigator.clipboard.writeText(selectedHistoryItem.proof);
                      toast.success("Proof copied to clipboard");
                    }}
                  >
                    Copy full proof to clipboard
                  </button>
                </div>
              </div>
            ) : (
              <p className="text-secondary-200 italic">No proof available for this query.</p>
            )}
          </div>
        ) : requestResponse && (
          <div className="overflow-x-auto">
            <table className="min-w-full bg-[#1e1e1e] p-4">
              <tbody>
                {requestResponse?.map((row: any[], rowIndex: number) => (
                  <tr key={rowIndex} className="hover:bg-tertiary-600">
                    {row.map((cell, cellIndex) => (
                      <td
                        key={cellIndex}
                        className="py-2 px-4 border-b border-secondary-500 break-words"
                      >
                        {cell}
                      </td>
                    ))}
                  </tr>
                ))}
                {requestResponse?.length === 0 && (
                  <tr>
                    <td
                      colSpan={1}
                      className="py-2 px-4 border-b border-secondary-500 text-center"
                    >
                      No result
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );

  const renderHistory = () => (
    <div className="h-full overflow-y-auto p-4">
      <h2 className="text-xl font-semibold text-secondary-100 mb-4">
        Query History
      </h2>
      {historyLoading ? (
        <div className="mb-6 flex justify-center">
          <Loading size="100px" />
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-secondary-100">
            <thead>
              <tr className="bg-tertiary-700">
                <th className="py-2 px-4 text-left w-3/4">Query</th>
                <th className="py-2 px-4 text-left w-1/4">Status</th>
              </tr>
            </thead>
            <tbody>
              {requests.map((request, index) => (
                <tr
                  key={index}
                  className="hover:bg-tertiary-700 cursor-pointer"
                  onClick={() => {
                    setSelectedHistoryItem(request);
                    setRequestResponse(null);
                  }}
                >
                  <td className="py-2 px-4 border-b border-secondary-500">
                    <div className="truncate max-w-xs" title={request.name}>
                      {request.name}
                    </div>
                  </td>
                  <td className="py-2 px-4 border-b border-secondary-500 whitespace-nowrap">
                    {(['PENDING', 'WORKER DESIGNATED', 'PROCESSING'].includes(request.status)) ? (
                      <span className="flex items-center">
                        <FontAwesomeIcon icon={faSpinner} spin className="mr-2" />
                        {request.status}
                      </span>
                    ) : (
                      request.status
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );

  return (
    <div className="bg-tertiary-900 h-screen flex pt-20">
      <div className="flex-grow flex flex-col overflow-hidden">
        {renderQueryEditor()}
        {renderQueryResults()}
      </div>
      <div className="w-[500px] flex-shrink-0 bg-tertiary-800 border-l border-secondary-500 overflow-hidden">
        {renderHistory()}
      </div>
    </div>
  );
}
