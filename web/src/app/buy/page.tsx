"use client";

import { CheckIcon } from "@heroicons/react/20/solid";
import Button from "@/components/button";
import { useChain } from "@/providers/chain";

import { toast } from "react-toastify";
import { useState } from "react";
import Loading from "@/components/loading";
import { useWallet } from "@aptos-labs/wallet-adapter-react";

const MODULE_ADDRESS = process.env.NEXT_PUBLIC_ESCROW_ADDRESS || "";

type Tier = {
  name: string;
  id: string;
  price?: string;
  description: string;
  features: string[];
};

const tiers: Tier[] = [
  {
    name: "Basic",
    id: "tier-basic",
    price: "1",
    description: "The essentials to start some DB requests",
    features: ["Cheapest option", "Up to 8 queries aprox"],
  },
  {
    name: "Advanced",
    id: "tier-advanced",
    price: "3",
    description: "A pack that can get you a long way.",
    features: [
      "Most popular",
      "Up to 40 queries aprox",
      "Can handle complex queries",
    ],
  },
  {
    name: "Professional",
    id: "tier-professional",
    price: "10",
    description: "A pack for heavy users.",
    features: [
      "Up to 100 queires aprox",
      "Priority on worker queue",
      "Can handle super complex queries",
    ],
  },
  {
    name: "Custom",
    id: "tier-custom",
    description: "Get what you want.",
    features: [
      "Any amount of queries",
      "Exactly what you need",
      "Can handle super complex queries",
    ],
  },
];

export default function BuyPage() {
  const [loading, setLoading] = useState<boolean>(false);
  const [customPrice, setCustomPrice] = useState<string>("20");
  const { client, handleBalance } = useChain();
  const { account, signAndSubmitTransaction } = useWallet();

  const handleBuy = async (tier: Tier) => {
    if (!client || !account || !signAndSubmitTransaction) {
      toast.error("Make sure your wallet is connected");
      return;
    }
    setLoading(true);

    try {
      const priceString = tier?.price || customPrice;
      const priceAPT = parseFloat(priceString);
      const amountOctas = Math.floor(priceAPT * 1e8); // Convert APT to Octas
      const TRANSFER_AMOUNT = amountOctas.toString();

      console.log("amountOctas", amountOctas);
      console.log("TRANSFER_AMOUNT", TRANSFER_AMOUNT);

      const accountResources = await client.getAccountResources({
        accountAddress: account.address,
      });
      console.log("accountResources", accountResources);
      const coinStore = accountResources.find(
        (resource) =>
          resource.type === "0x1::coin::CoinStore<0x1::aptos_coin::AptosCoin>",
      );

      console.log("coinStore", coinStore);

      if (!coinStore) {
        throw new Error("AptosCoin not registered for this account.");
      }

      const balance = parseInt((coinStore.data as any).coin.value, 10);
      if (balance < amountOctas) {
        throw new Error("Insufficient AptosCoin balance.");
      }

      // Sign and submit the transaction
      const response = await signAndSubmitTransaction({
        sender: account.address,
        data: {
          function: `${MODULE_ADDRESS}::escrow_native::deposit`,
          functionArguments: [amountOctas],
        },
      });

      console.log("response.hash", response.hash);

      // Wait for transaction confirmation
      await client.waitForTransaction({ transactionHash: response.hash });
      await handleBalance?.();

      toast.success("Credits deposited successfully!");
    } catch (e) {
      console.log("error", e);
      toast.error("Error on credits deposit, " + e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-tertiary-900 py-16 sm:py-32 min-h-screen">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-4xl text-center">
          <p className="mt-2 text-4xl font-bold tracking-tight text-secondary-100 sm:text-5xl">
            Buy Credits
          </p>
        </div>

        <p className="mx-auto mt-6 max-w-2xl text-center text-lg leading-8 text-secondary-200">
          <p className="text-white text-xl text-bold">
            Make sure your wallet is connected and funded with APT.
          </p>
          In order to submit requests, you must purchase credits using APT
          (currently in testnet). Select a tier below or provide a custom
          amount.
        </p>

        <div className="mx-auto py-10 flex w-full flex-wrap gap-8 items-center justify-center">
          {loading ? (
            <Loading size="500px" />
          ) : (
            tiers.map((tier) => (
              <div
                key={tier.id}
                className={`ring-1 ring-secondary-500 rounded-3xl p-8 xl:p-10 w-full md:w-1/2 lg:w-1/3 h-[400px]`}
              >
                <div className="flex items-center justify-between gap-x-4">
                  <h3
                    id={tier.id}
                    className="text-lg font-semibold leading-8 text-secondary-100"
                  >
                    {tier.name}
                  </h3>
                </div>
                <p className="mt-4 text-sm leading-6 text-secondary-200">
                  {tier.description}
                </p>
                <p className="mt-6 flex items-baseline gap-x-1">
                  {tier?.price ? (
                    <span className="text-4xl font-bold tracking-tight">
                      $ {tier?.price}
                    </span>
                  ) : (
                    <>
                      <span className="text-4xl font-bold tracking-tight text-primary-500 ml-2">
                        $
                      </span>
                      <input
                        type="number"
                        id="custom-price"
                        value={customPrice}
                        onChange={(e) => setCustomPrice(e.target.value)}
                        className="w-full -ml-8 pl-8 pr-2 pb-1 pt-1.5 h-12 text-[34px] text-primary-500 font-bold bg-transparent border-secondary-500 border-2 rounded-lg focus-visible:outline-none"
                      />
                    </>
                  )}
                </p>

                <Button
                  id={`button-${tier.id}`}
                  type="button"
                  label="Buy credits"
                  className="w-full mt-4 text-xl"
                  onClick={() => {
                    handleBuy({ ...tier, price: tier?.price || customPrice });
                  }}
                />
                <ul
                  role="list"
                  className="mt-8 space-y-3 text-sm leading-6 text-secondary-200 xl:mt-10"
                >
                  {tier.features.map((feature) => (
                    <li key={feature} className="flex gap-x-3">
                      <CheckIcon
                        className="h-6 w-5 flex-none text-primary-500"
                        aria-hidden="true"
                      />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
