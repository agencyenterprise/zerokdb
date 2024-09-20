"use client";

import React, {
  createContext,
  useContext,
  useState,
  useMemo,
  useEffect,
  useCallback,
} from "react";
import { useWallet } from "@aptos-labs/wallet-adapter-react";
import { Aptos, AptosConfig, Network } from "@aptos-labs/ts-sdk";
import { toast } from "react-toastify";

const MODULE_ADDRESS = process.env.NEXT_PUBLIC_ESCROW_ADDRESS || "";

const ChainContext = createContext<{
  client?: Aptos;
  escrowBalance?: bigint;
  handleBalance?: () => Promise<void>;
}>({
  client: undefined,
  escrowBalance: undefined,
  handleBalance: undefined,
});

export function ChainProvider({ children }: { children: React.ReactNode }) {
  const { account, signMessage } = useWallet();
  const [tokens, setTokens] = useState<any>();

  const aptos = useMemo(() => {
    const config = new AptosConfig({ network: Network.DEVNET });
    return new Aptos(config);
  }, []);

  const handleLogin = useCallback(async () => {
    if (account) {
      try {
        const nonceValue = await fetch("/api/auth/nonce").then((res) =>
          res.text(),
        );

        const signature = await signMessage({
          message: `Login to ZerokDB. Nonce: ${nonceValue}`,
          nonce: nonceValue,
          address: true,
        });

        await fetch("/api/auth/login", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            ...signature,
            publicKey: account.publicKey,
          }),
        });
      } catch (error) {
        const message = "Error logging in";
        console.error(message, error);
        toast.error(message);
      }
    }
  }, [account, signMessage]);

  const handleBalance = useCallback(async () => {
    if (account) {
      console.log("getting balance");
      const response = await aptos.view({
        payload: {
          function: `${MODULE_ADDRESS}::escrow_native::balance_of`,
          functionArguments: [account.address],
        },
      });
      console.log("response balance", response);

      setTokens(response?.[0] || 0);
    }
  }, [account, aptos]);

  useEffect(() => {
    if (account) {
      handleLogin();
      handleBalance();
    }
  }, [account]);

  const value = useMemo(
    () => ({
      client: aptos,
      escrowBalance: tokens?.[0],
      handleBalance,
    }),
    [aptos, tokens, handleBalance],
  );

  return (
    <ChainContext.Provider value={value}>{children}</ChainContext.Provider>
  );
}

export function useChain() {
  const context = useContext(ChainContext);
  if (!context) {
    throw new Error("useChain must be used within a ChainProvider");
  }
  return context;
}
