import React from 'react';
import Image from 'next/image';
import MockImage from '@public/assets/images/news-mock-image-black.svg';

const page = () => {
    const news = [1,2,3,4,5,6,7,8,9,10,11,12,13,14]

    return (
    <div className="py-12">
      <section className="container mx-auto px-4 max-w-[1200px]">
        {/* Latest Car News */}
        <div className="text-white font-inter font-extrabold mb-8 text-center lg:text-4xl md:text-3xl sm:text-2xl xxs:text-lg">Popular cars this week</div>
        <div className="flex flex-wrap justify-center gap-8 mb-12">
          {/* News Items */}
          {news.map((item, index) => (
            <div key={index} className="sm:w-[340px] xxs:w-[250px]">
              <Image
                src={MockImage}
                alt={`news-image-${index}`}
                width={340}
                height={70}
                className="rounded-md"
              />
            <span className="text-intro font-inter font-bold text-lg mt-2 block max-w-[300px] ml-5 md:text-md sm:text-sm xxs:text-sm">
                Text about the news.
              </span>
            </div>
          ))}
          
        </div>
      </section>
    </div>
  );
};

export default page;
