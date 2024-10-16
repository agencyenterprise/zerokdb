"use client";

import { useState } from "react";
import { Dialog } from "@headlessui/react";
import { Bars3Icon, XMarkIcon } from "@heroicons/react/24/outline";
import Wallet from "./wallet";
import Image from "next/image";
import Link from "next/link";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faGithub } from "@fortawesome/free-brands-svg-icons";

const navigation = [
  { name: "Home", href: "/" },
  { name: "zerokDB Explorer", href: "/interactions" },
  // { name: "Interactions History", href: "/interactions-history" },
  // { name: "Buy credits", href: "/buy" },
  { name: "Run a Node", href: "/#node" },
];

export default function Example() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="fixed z-10 left-0 right-0 top-0 bg-tertiary-900">
      <nav
        className="flex  items-center justify-between p-4 px-6"
        aria-label="Global"
      >
        {/* Left side: Logo and navigation links */}
        <div className="flex items-center">
          <div className="hidden sm:flex mr-8">
            <Link href="/">
              <span className="sr-only">ZeroK</span>
              <Image width={130} height={130} src="/logodb.svg" alt="" />
            </Link>
          </div>
          <div className="hidden lg:flex lg:gap-x-8">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className="text-md font-semibold leading-6 text-secondary-100 hover:text-primary-500"
              >
                {item.name}
              </Link>
            ))}
          </div>
        </div>

        {/* Right side: Credits, Wallet, and GitHub icon */}
        <div className="hidden lg:flex items-center">
          <Link
            href="/buy"
            className="text-md font-semibold leading-6 text-secondary-100 hover:text-primary-500 mr-8"
          >
            Buy credits
          </Link>
          <Wallet />
          <div className="ml-4">
            <a
              href="https://github.com/agencyenterprise/zerokdb"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-white transition-colors duration-300"
            >
              <FontAwesomeIcon icon={faGithub} size="2x" />
            </a>
          </div>
        </div>

        {/* Mobile menu button */}
        <div className="flex lg:hidden">
          <button
            type="button"
            className="-m-2.5 inline-flex items-center justify-center rounded-md p-2.5 text-secondary-400"
            onClick={() => setMobileMenuOpen(true)}
          >
            <span className="sr-only">Open main menu</span>
            <Bars3Icon className="h-6 w-6" aria-hidden="true" />
          </button>
        </div>
      </nav>
      <Dialog
        as="div"
        className="lg:hidden"
        open={mobileMenuOpen}
        onClose={setMobileMenuOpen}
      >
        <div className="fixed inset-0 z-10" />
        <Dialog.Panel className="fixed inset-y-0 right-0 z-10 w-full overflow-y-auto bg-tertiary-900 px-6 py-6 sm:max-w-sm sm:ring-1 sm:ring-secondary-400">
          <div className="flex items-center justify-between">
            <Link href="/" className="-m-1.5 p-1.5">
              <span className="sr-only">ZeroK</span>
              <Image width={110} height={110} src="/logo.svg" alt="" />
            </Link>
            <button
              type="button"
              className="-m-2.5 rounded-md p-2.5 text-secondary-400"
              onClick={() => setMobileMenuOpen(false)}
            >
              <span className="sr-only">Close menu</span>
              <XMarkIcon className="h-6 w-6" aria-hidden="true" />
            </button>
          </div>
          <div className="mt-6 flow-root">
            <div className="-my-6 divide-y divide-secondary-500/25">
              <div className="space-y-2 py-6">
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className="-mx-3 block rounded-lg px-3 py-2 text-base font-semibold leading-7 text-secondary-100 hover:bg-tertiary-800"
                  >
                    {item.name}
                  </Link>
                ))}
              </div>
              <div className="py-6">
                <Wallet />
              </div>
              <div className="py-6">
                <a
                  href="https://github.com/agencyenterprise/zerokdb"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-white transition-colors duration-300"
                >
                  <FontAwesomeIcon icon={faGithub} size="2x" />
                </a>
              </div>
            </div>
          </div>
        </Dialog.Panel>
      </Dialog>
    </header>
  );
}
