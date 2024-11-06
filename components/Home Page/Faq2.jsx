'use client'

import { useState } from 'react';
import React from 'react';


const Faq2 = () => {
  const [activeIndex, setActiveIndex] = useState(null);

  const faqData = [
    { question: "How does the car selection work?", answer: "Our process is simple! First, you'll answer a few questions about your lifestyle, driving habits, and preferences. Then, we’ll match you with a range of cars that fit your criteria. From there, you can compare models, and features to find the perfect match." },
    { question: "Do I need to create an account?", answer: "No, you don’t need to create an account to explore car options. However, creating an account allows you to save your preferences, receive personalized recommendations, and track your car search progress." },
    { question: "How do you recommend cars for me?", answer: "We use a combination of your inputs (lifestyle, driving needs) and a database of vehicle specifications, expert reviews, and user feedback to suggest cars that meet your needs. Our algorithm prioritizes factors that are most important to you." },
    { question: "Is this service free to use?", answer: "Yes, our car-matching service is completely free. You can explore recommendations, compare cars, and save your choices without any cost." },
    { question: "What if I need more help?", answer: "If you need assistance, we offer customer support to answer any questions or provide additional guidance. You can contact us via chat, phone, or email anytime during your car search process." },
];
  const toggleDropdown = (index) => {
    setActiveIndex(activeIndex === index ? null : index);
  };

  return (
    <div className="w-full max-w-3xl mx-auto p-5 mb-40 ">
      <h2 className="font-inter xxs:text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-black tracking-tighter text-black text-center mt-32 mb-32">Frequently Asked Questions</h2>
      <div className="space-y-4 border-4 rounded-2xl mt-10 border-intro p-10">
        {faqData.map((item, index) => (
          <div key={index} className="border-b border-gray-300 pb-3">
            <button
              onClick={() => toggleDropdown(index)}
              className="mx-4 my-4 font-inter font-extrabold xxs:text-md sm:text-lg md:text-xl lg:text-2xl tracking-tighter flex focus:outline-none">
              {item.question}
              <svg
                className={`w-6 h-7 ml-1 transform transition-transform duration-300 ${
                  activeIndex === index ? 'rotate-180' : 'rotate-0'
                }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            <div
              className={`mt-2 text-gray-600 overflow-hidden transition-all duration-300 ${
                activeIndex === index ? 'max-h-screen' : 'max-h-0'
              }`}>
              <p className="mt-2 font-inter font-bold text-intro">{item.answer}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Faq2;
