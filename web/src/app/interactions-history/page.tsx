"use client";

import Button from "@/components/button";
import Loading from "@/components/loading";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import Link from "next/link";

type Request = {
  id: string;
  name: string;
  description: string;
  status: string;
  worker_wallet: string;
  ai_model_output: string;
  ai_model_inputs: string;
};

export default function InteractionsHistoryPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [requests, setRequests] = useState<Request[]>([]);
  const [selectedRequest, setSelectedRequest] = useState<Request>();

  useEffect(() => {
    const fetchRequests = async () => {
      setLoading(true);
      try {
        const response = await fetch(`/api/hub/request`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        });
        if (response.ok) {
          const data = await response.json();
          setRequests(data);
        } else {
          toast.error("Failed to fetch requests");
        }
      } catch (error) {
        toast.error("Failed to fetch requests");
      } finally {
        setLoading(false);
      }
    };

    fetchRequests();
  }, []);

  const NoRequests = () => {
    return (
      <div className="text-center text-secondary-200">
        No History
        <Button
          id={`button-started`}
          type="button"
          label="Get started"
          className="ml-8"
          onClick={() => {
            router.push("/interactions");
          }}
        />
      </div>
    );
  };

  const RequestsList = () => {
    return (
      <div className="overflow-x-auto">
        <table className="min-w-full text-secondary-100">
          <thead>
            <tr className="bg-tertiary-700">
              <th className="py-2 px-4 text-left">Query</th>
              <th className="py-2 px-4 text-left">Status</th>
              <th className="py-2 px-4 text-left">Type</th>
              <th className="py-2 px-4 text-left">Worker</th>
            </tr>
          </thead>
          <tbody>
            {requests.map((request, index) => {
              const input = request?.ai_model_inputs && JSON.parse(request.ai_model_inputs);

              return (
                <tr
                  key={index}
                  className="hover:bg-tertiary-700 cursor-pointer"
                  onClick={() => setSelectedRequest(request)}
                >
                  <td className="py-2 px-4 border-b border-secondary-500">{request.name}</td>
                  <td className="py-2 px-4 border-b border-secondary-500">{request.status}</td>
                  <td className="py-2 px-4 border-b border-secondary-500">{input?.type || '-'}</td>
                  <td className="py-2 px-4 border-b border-secondary-500">
                    {request?.worker_wallet && request?.worker_wallet !== "None" ? (
                      <Link
                        href={`https://explorer.aptoslabs.com/account/${request.worker_wallet}?network=testnet`}
                        target="_blank"
                        className="underline text-primary-500 hover:text-primary-400"
                      >
                        {`${request.worker_wallet.slice(0, 6)}...${request.worker_wallet.slice(-4)}`}
                      </Link>
                    ) : '-'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    );
  };

  const RequestDetails = () => {
    if (!selectedRequest) {
      return null;
    }

    const payload =
      selectedRequest?.ai_model_output &&
      JSON.parse(selectedRequest.ai_model_output);

    const input =
      selectedRequest?.ai_model_inputs &&
      JSON.parse(selectedRequest.ai_model_inputs);

    return (
      <div className="flex flex-col w-full">
        <div className="flex flex-col p-4 bg-tertiary-800 border border-secondary-500 rounded-lg shadow w-full gap-2">
          <h4 className="text-left mb-1 text-lg font-bold tracking-tight text-secondary-100">
            {selectedRequest.name}
          </h4>
          <p className="text-left text-sm text-secondary-200">
            {`Status: ${selectedRequest.status}`}
          </p>
          {input?.type && (
            <p className="text-left text-sm text-secondary-200">
              {`Type: ${input.type}`}
            </p>
          )}
          <p className="text-left text-sm text-secondary-200">
            {selectedRequest.description}
          </p>
          {selectedRequest.worker_wallet &&
            selectedRequest?.worker_wallet !== "None" && (
              <p className="text-left text-sm text-secondary-200">
                Paid to worker:{" "}
                <Link
                  href={`https://explorer.aptoslabs.com/account/${selectedRequest.worker_wallet}?network=testnet`}
                  target="_blank"
                  className="underline text-primary-500 hover:text-primary-400"
                >
                  {selectedRequest.worker_wallet}
                </Link>
              </p>
            )}
        </div>

        {payload?.length > 0 && (
          <>
            <h2 className="text-xl font-semibold text-secondary-100 py-4 text-center mt-4">
              Results
            </h2>
            <div className="p-4 bg-tertiary-800 border border-secondary-500 rounded-lg shadow w-full">
              <div className="overflow-x-auto">
                <table className="min-w-full text-secondary-100">
                  <tbody>
                    {payload?.map((row: any[], rowIndex: number) => (
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
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}

        <div className="flex justify-center mt-8">
          <Button
            id={`button-back`}
            type="button"
            label="Back"
            className="ml-8"
            onClick={() => setSelectedRequest(undefined)}
          />
        </div>
      </div>
    );
  };

  return (
    <div className="bg-tertiary-900 py-12 sm:py-24 min-h-screen">
      <div className="mx-auto w-full px-4 sm:max-w-7xl">
        <div className="mx-auto max-w-4xl text-center py-8">
          <h2 className="text-2xl font-bold tracking-tight text-secondary-100 sm:text-4xl">
            Request History
          </h2>
        </div>
        <div className="flex justify-center mt-8">
          {loading && (
            <div className="mb-6 flex justify-center">
              <Loading size="500px" />
            </div>
          )}

          {!loading && (
            <>
              {selectedRequest && <RequestDetails />}
              {!selectedRequest && requests?.length > 0 && <RequestsList />}
              {!selectedRequest && requests?.length === 0 && <NoRequests />}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
