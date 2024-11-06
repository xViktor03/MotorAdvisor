
import Image from 'next/image';
import heroImage from '@public/assets/images/Home Hero Image.png';
import imageGradient from '@public/assets/images/Gradient.png';
import heroImageSmall from '@public/assets/images/Home Hero Image-small.png';

const HeroImage = () => {
  

  return (
    <div className="h-[399px] relative w-full transition-all">
      {/* Large Screen Hero Image */}
      <div className="hidden sm:block">
        <Image
          src={heroImage}
          alt="heroimage"
          fill
          className="object-cover object-center w-full mt-0"
          priority={true}
        />
      </div>

      {/* Small Screen Hero Image */}
      <div className="block sm:hidden transition-all">
        <Image
          src={heroImageSmall}
          alt="heroimage-small"
          fill
          className="object-cover object-center w-full h-[370px] mt-0"
          priority={true}
        />
      </div>

    </div>
  );
};

export default HeroImage;
