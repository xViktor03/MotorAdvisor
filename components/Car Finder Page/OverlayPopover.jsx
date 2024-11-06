'use client';

import { useState } from 'react';
import carlist from '@constants/carsDatabase.json'; // Ensure this path is correct

export default function OverlayPopover({ handleNext, handlePanel, onBrandsSelected }) {
  // Extract unique brands and sort them alphabetically
  const uniqueBrands = [...new Set(carlist.map(car => car.Brand))].sort();

  const [toggledOptions, setToggledOptions] = useState({});

  // Handle toggling between options
  const handleToggle = (optionIndex) => {
    const updatedOptions = {
      ...toggledOptions,
      [optionIndex]: !toggledOptions[optionIndex],
    };
    

    setToggledOptions(updatedOptions);

    // Find all toggled brands
    const toggledBrandIds = Object.keys(updatedOptions)
      .filter(key => updatedOptions[key]); // Find keys where value is true

    const selectedBrands = toggledBrandIds.map(id => uniqueBrands[parseInt(id, 10)]); // Get all selected brands

    // Immediately update the parent component with the selected brands
    onBrandsSelected(selectedBrands);
  };

  // Function to handle "Next" button click
  const handleNextClick = () => {
    // Call the parent component's functions
    handleNext();
    handlePanel();
  };

  return (
    <div className="relative">
      <div>
        {/* Blurred Background */}
        <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm"></div>

        {/* Popover Content */}
        <div className="fixed inset-0 flex items-center justify-center z-50 ">
          <div className="bg-white rounded-3xl shadow-lg max-w-md w-full overflow-y-auto max-h-[500px] no-scrollbar border-2 border-intro_button_dark">
            <h2 className="text-xl font-semibold mb-2 bg-intro font-poppins text-white py-4 px-3">Brand list</h2>
            <ul className="space-y-2">
              {uniqueBrands.map((brand, id) => (
                <li
                  key={id}
                  className="px-3 py-1 text-black font-poppins border-b-2 border-black font-[520] tracking-tighter text-lg flex justify-between">
                  {brand}
                  <button onClick={() => handleToggle(id)}>
                    {toggledOptions[id] ? (
                      <svg
                        width="25"
                        height="25"
                        viewBox="0 0 35 35"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <rect
                          x="2"
                          y="2"
                          width="31"
                          height="31"
                          rx="5"
                          fill="#004C4E"
                          stroke="#081D1C"
                          strokeWidth="4"
                        />
                        <path
                          d="M9 16.5L8 19.5L15 26.5L28.5 10L27.5 9L14 22L9 16.5Z"
                          fill="white"
                        />
                      </svg>
                    ) : (
                      <svg
                        width="25"
                        height="25"
                        viewBox="0 0 35 35"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                        className="my-auto"
                      >
                        <rect
                          x="2"
                          y="2"
                          width="31"
                          height="31"
                          rx="5"
                          fill="white"
                          stroke="#1A3C3B"
                          strokeWidth="4"
                        />
                      </svg>
                    )}
                  </button>
                </li>
              ))}
            </ul>
            <div className="w-full bg-intro text-white justify-start flex py-1">
              <button
                onClick={handleNextClick}
                className="ml-2 flex justify-normal items-center rounded-xl bg-intro_button py-[6px] px-[20px] text-white transition-all duration-300 hover:bg-intro_button_dark hover:text-white text-center text-xl font-semibold font-inter mt-1 mb-1 md:text-lg"
              >
                Next
                <svg
                  width="30"
                  height="15"
                  viewBox="0 0 61 30"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  className="ml-1"
                >
                  <path
                    d="M60.4142 16.4142C61.1953 15.6332 61.1953 14.3668 60.4142 13.5858L47.6863 0.857864C46.9052 0.0768158 45.6389 0.0768158 44.8579 0.857864C44.0768 1.63891 44.0768 2.90524 44.8579 3.68629L56.1716 15L44.8579 26.3137C44.0768 27.0948 44.0768 28.3611 44.8579 29.1421C45.6389 29.9232 46.9052 29.9232 47.6863 29.1421L60.4142 16.4142ZM0 17L59 17V13L0 13L0 17Z"
                    fill="white"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
