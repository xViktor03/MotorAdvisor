import React from 'react';
import Link from 'next/link';

const HeroText = () => {
  return (
    <div className="bg-intro text-center content-center mx-auto max-w-[1200px] rounded-3xl xxs:mb-64 sm:mb-72 md:mb-80 lg:mb-96 -translate-y-20 drop-shadow-custom inner-shadow">
      <section className="hero_text_upper mt-6 xxs:text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold">
        Introducing the ULTIMATE car buying platform
      </section>
      <section className="hero_text_lower mt-2 xxs:text-2xl sm:text-3xl md:text-4xl lg:text-5xl">
        Explore our latest news and the best car finder system
      </section>
      <div className="flex justify-center">
      <Link href="/news">
        <button className="intro_btn mt-5 mb-8 text-xl md:text-lg transition rounded-md">
          Explore
        </button>
      </Link>
      </div>
    </div>
  );
};

export default HeroText;
