"use client";

import { useEffect, useMemo, useState } from "react";

import Loading from "@/components/loading";
import { useChain } from "@/providers/chain";
import { toast } from "react-toastify";
import Link from "next/link";
import SqlInput from "@/components/sql-input";
import Button from "@/components/button";
import { Parser } from "node-sql-parser";
import { faker } from "@faker-js/faker";

type FormData = {
  semantic?: string;
  sql?: string;
};

export default function InteractionsPage() {
  const [loading, setLoading] = useState(false);
  const { client, escrowBalance } = useChain();
  const [formData, setFormData] = useState<FormData>({});
  const [requestId, setRequestId] = useState<string>();
  const [response, setResponse] = useState<any>();
  const [polling, setPolling] = useState(false);

  const sqlParser = useMemo(() => new Parser(), []);

  const handleRequest = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!client || !escrowBalance) {
      toast.error("Make sure your wallet is connected");
      return;
    }

    setRequestId(undefined);
    setLoading(true);

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
      } else {
        const message = "Error generating inference";
        console.log(message, e);
        toast.error(message);
      }
    } catch (error) {
      const message = "Error generating inference";
      console.log(message, e);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const isValidSql = (sql: string) => {
    try {
      if (!sql?.length) {
        return false;
      }
      sqlParser.astify(sql);
      return true;
    } catch (e) {
      console.log("parse error:", e);
      return false;
    }
  };

  const handleSelectExample = () => {
    const example = `SELECT * FROM users LIMIT 10`;
    setFormData({ ...formData, sql: example, semantic: "" });
  };

  const handleDataExample = () => {
    const table = faker.food.adjective().replaceAll(" ", "_").toLowerCase();
    const example = faker.helpers.fake(
      `
CREATE TABLE ${table} (
  id INT PRIMARY KEY,
  name VARCHAR(255),
  description TEXT
);

INSERT INTO ${table} (id, name, temp) VALUES (1, '{{food.dish}}', '{{food.description}}');
      `,
    );
    setFormData({ ...formData, sql: example, semantic: "" });
  };

  useEffect(() => {
    let intervalId: NodeJS.Timeout;

    const fetchResponse = async () => {
      if (!requestId) return;

      try {
        const res = await fetch(
          `/api/hub/request/${encodeURIComponent(requestId)}`,
        );

        if (res.ok) {
          const data = await res.json();

          if (data.status === "generated") {
            setResponse(data?.payload && JSON.parse(data.payload));
            setPolling(false);
            clearInterval(intervalId);
            toast.success("Response generated successfully!");
          }
        } else {
          const errorData = await res.json();
          setPolling(false);
          toast.error(errorData.error || "Failed to retrieve response.");
          clearInterval(intervalId);
        }
      } catch (error: any) {
        setPolling(false);
        toast.error("An error occurred while polling.");
        clearInterval(intervalId);
      }
    };

    if (requestId) {
      setPolling(true);
      fetchResponse();
      intervalId = setInterval(fetchResponse, 5000); // Poll every 5 seconds
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [requestId]);

  return (
    <div className="bg-tertiary-900 py-20 sm:py-32 min-h-screen">
      <div className="mx-auto w-full sm:max-w-2xl">
        <h1 className="text-2xl sm:text-4xl font-bold tracking-tight text-secondary-100 pb-6 sm:pb-12 text-center mx-auto">
          DB Interactions
        </h1>
        {!escrowBalance && (
          <div className="py-8 px-4">
            <div
              className="bg-orange-100 border-l-4 border-orange-500 text-orange-700 p-4 mb-3"
              role="alert"
            >
              <p>
                You must have your wallet connected and some credits to do a
                request
              </p>
              <p className="font-bold">
                <Link href="/buy">Click here to buy some credits</Link>
              </p>
            </div>
          </div>
        )}
        {loading ? (
          <div className="mb-6 flex justify-center">
            <Loading size="500px" />
          </div>
        ) : (
          <div className="mb-6 px-4">
            <form onSubmit={handleRequest}>
              <div className="flex flex-row gap-4 w-full pb-6">
                <Button
                  id="submit"
                  type="submit"
                  label="Run Query"
                  className="w-40"
                  disabled={
                    (!isValidSql(formData?.sql ?? "") &&
                      !formData?.semantic?.length) ||
                    !escrowBalance
                  }
                />
                <h2 className="tracking-tight text-secondary-200 ">
                  You can either enter a semantic search or a raw SQL query to
                  send to the ZeroK decentralized database
                </h2>
              </div>
              <div className="mb-6">
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
                    })
                  }
                />
              </div>

              <div className="mb-6">
                <label
                  htmlFor="select"
                  className="block mb-2 text-sm font-medium text-secondary-100"
                >
                  Pre defined examples
                </label>
                <div className="flex flex-row gap-4 w-full">
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
                </div>
              </div>
              <SqlInput
                label="Raw SQL Query"
                sqlString={formData?.sql ?? ""}
                setSqlString={(text) =>
                  setFormData({ ...formData, sql: text, semantic: "" })
                }
              />
              <div className="mt-6 flex flex-col items-end justify-end">
                {formData?.sql &&
                  formData?.sql.length > 0 &&
                  !isValidSql(formData?.sql!) && (
                    <p className="text-primary-500 text-sm mb-6">
                      Invalid SQL query
                    </p>
                  )}
              </div>
            </form>
          </div>
        )}

        {requestId && (
          <div className="px-4 py-6 bg-tertiary-800 rounded-lg mt-8">
            <h2 className="text-xl font-semibold text-secondary-100 mb-4">
              Results
            </h2>
            {polling && (
              <div className="mb-6 flex justify-center">
                <Loading size="200px" />
              </div>
            )}
            {response && (
              <div className="overflow-x-auto">
                <table className="min-w-full bg-tertiary-700 text-secondary-100">
                  <tbody>
                    {response?.map((row: any[], rowIndex: number) => (
                      <tr key={rowIndex} className="hover:bg-tertiary-600">
                        {row.map((cell, cellIndex) => (
                          <td
                            key={cellIndex}
                            className="py-2 px-4 border-b border-secondary-500"
                          >
                            {cell}
                          </td>
                        ))}
                      </tr>
                    ))}
                    {response?.length === 0 && (
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
        )}
      </div>
    </div>
  );
}
