import React from 'react'
import Logo from "@public/assets/images/log.svg"
import Image from 'next/image'
import Link from 'next/link'


const Footer2 = () => {
    return (
      <footer className="bg-[#17252A] text-white py-10 font-inter xxs:text-sm sm:text-md md:text-lg lg:text-lg">
        <div className="container mx-auto grid grid-cols-1 md:grid-cols-3 gap-8 px-5">
          {/* Company Info Section */}
          <div>
            <h4 className="xxs:text-lg sm:text-lg md:text-xl lg:text-2xl font-bold mb-4">Company</h4>
            <ul className="space-y-2">
              <li><Link href="/aboutus" className="hover:text-gray-400 transition">About Us</Link></li>
              <li><Link href="/news" className="hover:text-gray-400 transition">Blog</Link></li>
              <li><Link href="/contact" className="hover:text-gray-400 transition">Contact Us</Link></li>
            </ul>
          </div>
  
          {/* Quick Links Section */}
          <div>
            <h4 className="xxs:text-lg sm:text-lg md:text-xl lg:text-2xl font-bold mb-4">Quick Links</h4>
            <ul className="space-y-2">
              <li><Link href="/privacypolicy" className="hover:text-gray-400 transition">Privacy Policy</Link></li>
              <li><Link href="/termsandconditions" className="hover:text-gray-400 transition">Terms and Conditions</Link></li>
              <li><Link href="/contact" className="hover:text-gray-400 transition">Support</Link></li>
            </ul>
          </div>
  
          {/* Logo */}
          <div>
            <Image src={Logo} alt="logo" width={350} className="mt-5">

            </Image>
          </div>
        </div>
        <div className="text-center mt-8 border-t border-gray-700 pt-4">
          <p className="text-sm">&copy; {new Date().getFullYear()} MotorAdvisor. All Rights Reserved.</p>
        </div>
      </footer>
    );
  };
  
  export default Footer2;
  