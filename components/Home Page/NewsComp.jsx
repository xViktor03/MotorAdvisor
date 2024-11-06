import React from 'react';
import Image from 'next/image';
import MockImage from '@public/assets/images/news-mock-image.svg';
import Arrow from '@public/assets/images/arrow.svg';

const NewsComp = () => {
  return (
    <div className="bg-intro py-12">
      <section className="container mx-auto px-4 max-w-[1200px]">
        {/* Latest Car News */}
        <div className="text-white font-inter font-extrabold mb-8 text-center lg:text-4xl md:text-3xl sm:text-2xl xxs:text-lg">Popular cars this week</div>
        <div className="flex flex-wrap justify-center gap-8 mb-12">
          {/* News Items */}
          {[1, 2, 3].map((item, index) => (
            <div key={index} className="sm:w-[340px] xxs:w-[250px]">
              <Image
                src={MockImage}
                alt={`news-image-${index}`}
                width={340}
                height={70}
                className="rounded-md"
              />
            </div>
          ))}
          {/* Read More Button */}
          <div className="flex justify-center w-full">
            <button className="read_more_btn flex items-center justify-center mt-4 text-white  transition max-w-[200px] flex-wrap">
              <Image src={Arrow} alt="arrow" width={50} />
              <span className="ml-2 mt-1 text-lg">Read more</span>
            </button>
          </div>
        </div>

        {/* Latest Blogs */}
        <div className="text-white font-inter font-extrabold  my-12 text-center lg:text-4xl md:text-3xl sm:text-2xl xxs:text-lg">Latest Blogs</div>
        <div className="flex flex-wrap justify-center gap-8">
          {/* Blog Items */}
          {[1, 2, 3].map((item, index) => (
            <div key={index} className="w-full sm:w-[340px] xxs:w-[250px]">
              <Image
                src={MockImage}
                alt={`blog-image-${index}`}
                width={340}
                height={200}
                className="rounded-md"
              />
              <span className="text-white font-inter font-bold text-lg mt-2 block max-w-[300px] ml-5 md:text-md sm:text-sm xxs:text-sm">
                Text about the news.
              </span>
            </div>
          ))}
          {/* Read More Button */}
          <div className="flex justify-center w-full">
            <button className="read_more_btn flex items-center justify-center mt-4 text-white  transition max-w-[200px] flex-wrap">
              <Image src={Arrow} alt="arrow" width={50} />
              <span className="ml-2 mt-1 text-lg">Read more</span>
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default NewsComp;
