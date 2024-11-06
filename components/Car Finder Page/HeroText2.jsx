import React from 'react';
import Link from 'next/link'

const HeroText = () => {
  return (
    <div className="bg-intro text-center content-center mx-auto max-w-[1000px] rounded-3xl xxs:mb-64 sm:mb-72 md:mb-80 lg:mb-96 px-4 drop-shadow-custom inner-shadow -translate-y-24">
      <section className="hero_text_upper mt-6 xxs:text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold">
        Too many cars to choose from?
      </section>
      <section className="hero_text_lower mt-2 xxs:text-2xl sm:text-3xl md:text-4xl lg:text-5xl">
        We have tools designed to help you decide
      </section>
      <div className="flex justify-center">
      <button className="intro_btn mt-5 mb-8 text-xl md:text-lg transition rounded-md ">
        <Link href="/carfinder/carfinder-start">
        Start
        </Link>
      </button>
      </div>
    </div>
  );
};

export default HeroText;
