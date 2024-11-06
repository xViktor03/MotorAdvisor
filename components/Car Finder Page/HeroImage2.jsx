

import React from 'react';
import Image from 'next/image';
import heroImage from '@public/assets/images/Hero Image Car Finder.png';

const HeroImage2 = () => {
  

  return (
    <div className="h-[370px] relative w-full transition-all">
      {/* Large Screen Hero Image */}
        <Image
          src={heroImage}
          alt="heroimage"
          fill
          className="object-cover object-center w-full mt-0"
          priority={true}
        />
    </div>
  );
};

export default HeroImage2;
