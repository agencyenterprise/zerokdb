"use client";

import Button from "@/components/button";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faUpload,
  faDatabase,
  faShield,
  faCopy,
  faServer,
  faCoins,
  faMemory,
  faCheck,
} from "@fortawesome/free-solid-svg-icons";
import { useEffect, useMemo, useState } from "react";

export default function Home() {
  const router = useRouter();
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(false);
  const [proverCommand, setProverCommand] = useState(
    "curl -sSL https://b4vue13qqtcrf2u0vi7ko0jdu0.ingress.akash-palmito.org/0k-worker.sh | sh",
  );

  useEffect(() => {
    const origin = window.location.origin;
    setProverCommand(`curl -sSL ${origin}/0k-worker.sh | sh`);
  }, []);

  const copyCommand = () => {
    navigator.clipboard.writeText(proverCommand);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const steps = [
    {
      icon: faDatabase,
      title: "Connect to ZerokDB",
      description:
        "Use our SDK or interface to connect to ZerokDB on Aptos.",
    },
    {
      icon: faUpload,
      title: "Store Your Data",
      description:
        "Upload your data securely, stored on IPFS with references on the blockchain.",
    },
    {
      icon: faShield,
      title: "Run Verified Queries",
      description:
        "Execute queries that are verified using zero-knowledge proofs, ensuring data integrity and trustless verification.",
    },
  ];

  const benefits = [
    {
      icon: faServer,
      title: "Lightweight and Fast Worker Setup",
      description:
        "Easy to configure on any machine without heavy hardware requirements.",
    },
    {
      icon: faMemory,
      title: "Low Resource Usage",
      description: "Minimal impact on your system's performance.",
    },
    {
      icon: faCoins,
      title: "Earn APT Tokens",
      description:
        "Get rewarded for contributing to the network's storage and computation.",
    },
  ];

  const handleDownload = async () => {
    setLoading(true);
    const url = process.env.NEXT_PUBLIC_EXECUTABLE_DOWNLOAD || "";
    const filename = "0k-db-worker.zip";

    try {
      const response = await fetch(url, {
        mode: "cors",
      });
      if (!response.ok) throw new Error("Network response was not ok");

      const blob = await response.blob();
      const blobURL = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = blobURL;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(blobURL);
    } catch (error) {
      console.error("Download failed:", error);
      alert("Failed to download the file. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="relative mx-auto max-w-3xl py-16 sm:pt-48 sm:pb-36 px-2 text-secondary-100">
        <div className="hidden sm:mb-8 sm:flex sm:justify-center">
          <div className="relative rounded-full px-3 py-1 text-md leading-6 text-secondary-400 ring-1 ring-tertiary-600 hover:ring-tertiary-400">
            ZerokDB for Aptos Testnet is live!{" "}
            <Link
              target="_blank"
              href="https://github.com/agencyenterprise/zerokdb"
              className="font-semibold text-primary-500 hover:text-primary-400"
            >
              <span className="absolute inset-0" aria-hidden="true" />
              Github <span aria-hidden="true">&rarr;</span>
            </Link>
          </div>
        </div>
        <div className="text-center">
          <h1 className="text-2xl font-bold tracking-tight sm:text-5xl">
            A{" "}
            <span className="text-primary-500">blockchain-based database</span>{" "}
            on Aptos
          </h1>
          <h2 className="text-xl sm:text-4xl">
            for verified queries and secure data storage
          </h2>
          <p className="mt-6 text-lg leading-8 text-white">
            ZerokDB leverages {" "}
            <Link
              target="_blank"
              className="text-primary-500 hover:text-primary-400"
              href="https://aptos.dev/"
            >
              Aptos
            </Link>{" "}
            to run verified queries and save data directly on the blockchain and
            IPFS. By utilizing zero-knowledge proofs, we ensure trustless and
            efficient data storage and retrieval, providing unparalleled data
            integrity and security.
          </p>
          <div className="mt-10 flex items-center justify-center gap-x-6">
            <Button
              className="text-xl"
              id={`button-started`}
              type="button"
              label="Interactive Demo"
              onClick={() => {
                router.push("/interactions");
              }}
            />
            <a
              target="_blank"
              href="https://github.com/agencyenterprise/zerokdb"
              className="text-sm font-semibold leading-6 text-secondary-100 hover:text-secondary-400"
            >
              Learn more <span aria-hidden="true">→</span>
            </a>
          </div>
        </div>
      </div>

      <div className="relative py-5">
        <div className="absolute inset-0 flex items-center" aria-hidden="true">
          <div className="w-full h-0.5 bg-gradient-to-r from-black via-primary-500 to-black"></div>
        </div>
        <div className="relative flex justify-center">
          <span className="bg-black px-6 text-xl font-semibold leading-6 text-primary-500">
            How It Works
          </span>
        </div>
      </div>

      <div className="py-16 sm:py-24">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl lg:text-center">
            <p className="mt-2 text-3xl font-bold tracking-tight text-secondary-100 sm:text-4xl">
              Verified Queries in Three Simple Steps
            </p>
            <p className="mt-6 text-lg leading-8 text-secondary-300">
              ZerokDB simplifies the process of storing data and running
              verified queries on the blockchain.
            </p>
          </div>
          <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
            <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-3">
              {steps.map((step, stepIdx) => (
                <div key={stepIdx} className="flex flex-col">
                  <dt className="flex items-center gap-x-3 text-xl font-semibold leading-7 text-secondary-100">
                    <div className="rounded-lg bg-secondary-800 pb-2 pt-3 px-3 ring-1 ring-secondary-700">
                      <FontAwesomeIcon icon={step.icon} className="w-8 h-8" />
                    </div>
                    {step.title}
                  </dt>
                  <dd className="mt-4 flex flex-auto flex-col text-base leading-7 text-secondary-300">
                    <p className="flex-auto">{step.description}</p>
                  </dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      </div>

      <div id="node" className="relative py-5">
        <div className="absolute inset-0 flex items-center" aria-hidden="true">
          <div className="w-full h-0.5 bg-gradient-to-r from-black via-primary-500 to-black"></div>
        </div>
        <div className="relative flex justify-center">
          <span className="bg-black px-6 text-xl font-semibold leading-6 text-primary-500">
            Join the Network
          </span>
        </div>
      </div>

      <div className="py-16 sm:py-24">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl lg:text-center">
            <p className="mt-2 text-3xl font-bold tracking-tight text-secondary-100 sm:text-4xl">
              Run a ZerokDB Node
            </p>
            <p className="mt-6 text-lg leading-8 text-secondary-300">
              Contribute to the ZerokDB network by running a node. It&apos;s
              easy to set up, and you can earn APT tokens for your contribution.
              You&apos;ll need to have download our executable and{" "}
              <span className="text-primary-500">
                unzip it and right click with your mouse and open it with
                terminal
              </span>{" "}
              to run it on your machine
            </p>
          </div>
          <div className="mt-10 flex justify-center gap-4">
            <button
              className="cursor-pointer text-xl border-2 border-primary-500 rounded-lg px-6 py-3 font-semibold leading-6 hover:border-primary-300 transition-colors duration-300"
              id="button-started"
              type="button"
              onClick={handleDownload}
            >
              {loading ? "Downloading..." : "Download for MAC (ARM)"}
            </button>
            {/* <Link
              className="bg-[#2d2c2c] text-xl border-2 border-primary-500 rounded-lg px-6 py-3 font-semibold leading-6  hover:border-primary-300 transition-colors duration-300"
              id={`button-started`}
              type="button"
              href="#node"
            >
              Download for Windows (soon)
            </Link>
            <Link
              className="bg-[#2d2c2c] text-xl border-2 border-primary-500 rounded-lg px-6 py-3 font-semibold leading-6  hover:border-primary-300 transition-colors duration-300"
              id={`button-started`}
              type="button"
              href="#node"
            >
              Download for Linux (soon)
            </Link> */}
          </div>
          <p className="mt-6 text-lg leading-8 text-secondary-300 w-full text-center">
            Or copy this command to run it on{" "}
            <span className="text-primary-500">Docker</span>
          </p>
          <div className="mt-6 flex justify-center">
            <div className="relative">
              <pre className="bg-secondary-700 text-secondary-100 p-8 rounded-lg font-mono text-sm">
                {proverCommand}
              </pre>
              <button
                onClick={copyCommand}
                className="absolute top-2 right-2 text-secondary-400 hover:text-secondary-800"
                aria-label="Copy command"
              >
                <FontAwesomeIcon
                  icon={copied ? faCheck : faCopy}
                  className="w-5 h-5"
                />
              </button>
            </div>
          </div>
          <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
            <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-3">
              {benefits.map((benefit, index) => (
                <div key={index} className="flex flex-col">
                  <dt className="flex items-center gap-x-3 text-xl font-semibold leading-7 text-white">
                    <div className="rounded-lg bg-primary-500/10 pb-2 pt-3 px-3 ring-1 ring-primary-500/20">
                      <FontAwesomeIcon
                        icon={benefit.icon}
                        className="h-8 w-8 text-primary-500"
                      />
                    </div>
                    {benefit.title}
                  </dt>
                  <dd className="mt-4 flex flex-auto flex-col text-base leading-7 text-gray-300">
                    <p className="flex-auto">{benefit.description}</p>
                  </dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      </div>
    </>
  );
}
