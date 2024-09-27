"use client";

import Button from "@/components/button";
import Loading from "@/components/loading";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import Link from "next/link";

type Item = {
  id: string;
  name: string;
};

export default function Me() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<Item[]>([]);
  const [selected, setSelected] = useState<Item>();
  const [showMore, setShowMore] = useState(false);

  useEffect(() => {
    setShowMore(false);
  }, [selected]);

  const NoItem = () => {
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

  const List = () => {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-8">
        {history.map((item, index) => (
          <div
            key={index}
            className="flex flex-col p-4 bg-tertiary-800 border border-secondary-500 rounded-lg shadow hover:bg-tertiary-700 w-full cursor-pointer"
            onClick={() => setSelected(item)}
          >
            <h4 className="text-left mb-2 text-lg font-bold tracking-tight text-secondary-100">
              {item.name}
            </h4>
          </div>
        ))}
      </div>
    );
  };

  const Details = () => {
    if (!selected) {
      return null;
    }

    return <div className="flex flex-col w-full"></div>;
  };

  return (
    <div className="bg-tertiary-900 py-12 sm:py-24 min-h-screen">
      <div className="mx-auto w-full sm:max-w-2xl px-4 sm:px-8">
        <div className="mx-auto max-w-4xl text-center py-8">
          <h2 className="text-2xl font-bold tracking-tight text-secondary-100 sm:text-4xl">
            History
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
              {selected && <Details />}
              {!selected && history?.length > 0 && <List />}
              {!selected && history?.length == 0 && <NoItem />}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
