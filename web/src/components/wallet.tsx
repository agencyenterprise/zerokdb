"use client";

import { WalletSelector } from "@aptos-labs/wallet-adapter-ant-design";
import { useChain } from "@/providers/chain";

function WalletConnector() {
  const { escrowBalance } = useChain();
  return (
    <>
      <div className="flex flex-row items-center gap-3">
        <p className="font-bold">Credit: {escrowBalance || 0}</p>
        <WalletSelector />
      </div>
    </>
  );
}

export default WalletConnector;
