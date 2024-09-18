"use client";

import { ChainProvider } from "@/providers/chain";
import { AptosWalletAdapterProvider } from "@aptos-labs/wallet-adapter-react";
import { PetraWallet } from "petra-plugin-wallet-adapter";
import { OKXWallet } from "@okwallet/aptos-wallet-adapter";
import { Network } from "@aptos-labs/ts-sdk";

const Providers = ({ children }: { children: React.ReactNode }) => {
  const wallets = [new PetraWallet(), new OKXWallet()];

  return (
    <AptosWalletAdapterProvider
      plugins={wallets}
      autoConnect={true}
      dappConfig={{ network: Network.TESTNET }}
      onError={(error) => {
        console.log("error", error);
      }}
      optInWallets={["Petra"]}
    >
      <ChainProvider>{children}</ChainProvider>
    </AptosWalletAdapterProvider>
  );
};

export default Providers;
