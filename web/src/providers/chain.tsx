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

const ChainContext = createContext<{
  client?: Aptos;
  escrowBalance?: bigint;
  fetchTokens?: () => Promise<void>;
}>({
  client: undefined,
  escrowBalance: undefined,
  fetchTokens: undefined,
});

export function ChainProvider({ children }: { children: React.ReactNode }) {
  const { account } = useWallet();
  const [tokens, setTokens] = useState<any>();

  const aptos = useMemo(() => {
    const config = new AptosConfig({ network: Network.TESTNET });
    return new Aptos(config);
  }, []);

  const fetchTokens = useCallback(async () => {
    if (account) {
      const tokens = await aptos.getAccountOwnedTokens({
        accountAddress: account.address,
      });
      console.log("test tokens", tokens);
      setTokens(tokens);

      /*await aptos.fundAccount({
        accountAddress: account.address,
        amount: 100000000,
      });*/
    }
  }, [account, aptos]);

  useEffect(() => {
    fetchTokens();
  }, [account, fetchTokens]);

  const value = useMemo(
    () => ({
      client: aptos,
      escrowBalance: tokens?.[0],
      fetchTokens,
    }),
    [aptos, tokens, fetchTokens],
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
