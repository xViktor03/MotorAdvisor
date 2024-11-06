"use client";

import { useState,useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import { MenuIcon, XIcon } from "@heroicons/react/outline"; // Heroicons needed for menu icon
import Logo from "@public/assets/images/log.svg"
import { signIn, signOut, useSession, getProviders } from 'next-auth/react'

const Navibar = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  const { data: session } = useSession()

  const [providers, setProviders] = useState(null);

  useEffect(() => {
    const fetchProviders = async () => {
      const response = await getProviders();

      setProviders(response);
    }

    fetchProviders();
  }, [])

  return (
    <nav className="bg-[#112D2C] p-3">
      <div className="max-w-7xl mx-auto px-2 sm:px-6 lg:px-8 font-inter">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <Link href="/" passHref>
              <Image
                src={Logo}
                alt="Logo"
                width={208}
                height={40}
              />
            </Link>
          </div>

          {/* Menu for larger screens */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-center space-x-4">
              <Link href="/news" className="text-white px-3 py-2 rounded-md text-md font-medium hover:text-gray-400 transition">
                News
              </Link>
              <Link href="/carfinder" className="text-white px-3 py-2 rounded-md text-md font-medium hover:text-gray-400 transition">
                Car Finder
              </Link>
              <Link href="/contact" className="text-white px-3 py-2 rounded-md text-md font-medium hover:text-gray-400 transition">
                Contact
              </Link>
              {session?.user ?
              (
                <div className="flex gap-4">
                  <button type="button" onClick={signOut} className="text-white px-3 py-2 rounded-md text-md font-medium hover:bg-white hover:text-[#112D2C] transition duration-300">
                    Sign Out
                  </button>
                  <Link href="/profile" >
                    <Image src={session?.user.image} alt="profile" width={37} height={37} className="rounded-full"/>
                  </Link>
                </div>
              )
              :
              <>
                {providers && 
                  Object.values(providers).map((provider) => (
                    <button
                    type="button"
                    key={provider.name}
                    onClick={() => signIn(provider.id)}
                    className="bg-white text-[#112D2C] px-3 py-2 rounded-md text-sm font-medium border border-transparent hover:bg-transparent hover:border-white hover:text-white transition duration-300">      
                      Sign In  
                    </button>

                  ))}

              </>
            }
              
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center gap-4">
            {session?.user ?
            (
              <Link href="/profile" >
                <Image src={session?.user.image} alt="profile" width={37} height={37} className="rounded-full"/>
              </Link>
            )
            :
            null
            }
            <button onClick={toggleMenu} className="text-white focus:outline-none">
              {isOpen ? (
                <XIcon className="h-6 w-6" />
              ) : (
                <MenuIcon className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu, show/hide based on menu state */}
      {isOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1">
            <Link href="/news" className="block text-white px-3 py-2 rounded-md text-base font-medium">
              News
            </Link>
            <Link href="/carfinder" className="block text-white px-3 py-2 rounded-md text-base font-medium">
              Car Finder
            </Link>
            <Link href="/contact" className="block text-white px-3 py-2 rounded-md text-base font-medium">
              Contact
            </Link>
            {session?.user ?
              (
                <div className="flex gap-4">
                  <button type="button" onClick={signOut} className="text-white px-3 py-2 rounded-md text-md font-medium hover:bg-white hover:text-[#112D2C] transition duration-300">
                    Sign Out
                  </button>
                  
                </div>
              )
              :
              <>
                {providers && 
                  Object.values(providers).map((provider) => (
                    <button
                    type="button"
                    key={provider.name}
                    onClick={() => signIn(provider.id)}
                    className="bg-white text-[#112D2C] px-3 py-2 rounded-md text-sm font-medium border border-transparent hover:bg-transparent hover:border-white hover:text-white transition duration-300">      
                      Sign In  
                    </button>

                  ))}

              </>
            }
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navibar;
