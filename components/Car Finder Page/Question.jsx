'use client'

import React, { useState,useEffect } from 'react';
import quizData from '@constants/quizData.json';
import OverlayPopover from './OverlayPopover';
import Link from 'next/link'

const Question = () => {
  const [currentQuestion, setCurrentQuestion] = useState(0);

  // State to track which checkboxes are toggled for each question
  const [toggledOptions, setToggledOptions] = useState({});

  const [selectedBrands, setSelectedBrands] = useState([]);
  const [selectedPurpose, setSelectedPurpose] = useState([]);
  const [selectedLocations, setSelectedLocations] = useState([]);
  const [selectedFeatures, setSelectedFeatures] = useState([]);
  const [jsonData, setJsonData ] = useState({});

  const [showOverlay, setShowOverlay] = useState(false);

  

  useEffect(() => {
    localStorage.removeItem('jsonData'); // Clear data for a fresh start
  }, []);


  const handleSelectedBrands = (brands) => {
    setSelectedBrands(brands);
  };

  const handleName = (index) => {
    let newKey = "";

    if (index === 0){
      newKey = "brands"; 
      handleClick(newKey, selectedBrands);
    }

    if (index === 1) {
      newKey = "purpose";
      handleClick(newKey, selectedPurpose);
      }

    if (index === 2) {
      newKey = "locations";
      handleClick(newKey, selectedLocations);
      }

    if (index === 3) {
      newKey = "features";
      handleClick(newKey, selectedFeatures);
      }
    }
  

    const handleNameDelete = (index) => {
      let newKey = "";
      if (index === 1) {
        newKey = "brands"
        handleDelete(newKey); 
      }
      if (index === 2) {
        newKey = "purpose"
        handleDelete(newKey); 
      }
      if (index === 3){
        newKey = "locations";
        handleDelete(newKey); 
      }
      if (index === 4) {
        newKey = "features";
        handleDelete(newKey); 
      }
      if (index === 5){
        newKey = "delivery"
        handleDelete(newKey); 
      }
      if (index === 6){
        newKey = "sharing"
        handleDelete(newKey); 
      }
      if (index === 7) {
        newKey = "fleet";
        handleDelete(newKey); 
      }
      if (index === 8) {
        newKey = "firstdriver";
        handleDelete(newKey);
        
      }

      
}
  

  const handleDelete = (id) => {
    const newData = { ...jsonData }; 
    delete newData[id]; // Delete the key in the copy
    setJsonData(newData);  // Update the state with the new data
  };

  // Function to add a new variable to the JSON object
  const handleClick = (newKey, newValue) => {
    const updatedData = { ...jsonData, [newKey]: newValue };
    setJsonData(updatedData);
    localStorage.setItem('jsonData', JSON.stringify(updatedData));
  };

  
  
  const handlePanel = () => {
    setShowOverlay(true); // Set state to show the overlay component
    if (showOverlay == true)
      setShowOverlay(false);

  };

  // Handle navigating to the next question
  const handleNext = () => {
    handleName(currentQuestion)
    if (currentQuestion < quizData.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      // Reset toggled state for the next question
      setToggledOptions({});
      
    }
    
  };

  // Handle navigating to the previous question
  const handlePrev = () => {
    if (currentQuestion > 0) {
      if (currentQuestion === 1) {
        handleNameDelete(currentQuestion)
        setSelectedBrands([])
      }
      if (currentQuestion === 2){
        handleNameDelete(currentQuestion)
        setSelectedPurpose([])
      }
      if (currentQuestion === 3){
        handleNameDelete(currentQuestion)
        setSelectedLocations([])
      }
      if (currentQuestion === 4){
        handleNameDelete(currentQuestion)
        setSelectedFeatures([])
      }
      if (currentQuestion === 5)
        handleNameDelete(currentQuestion)
      if (currentQuestion === 6)
        handleNameDelete(currentQuestion) 
      if (currentQuestion === 7)
        handleNameDelete(currentQuestion)
      if (currentQuestion === 8)  
        handleNameDelete(currentQuestion)

      setCurrentQuestion(currentQuestion - 1);
      setToggledOptions({});
    }
  };

  const check = {1: quizData.questions[1].options, // Get the array from quizData
                 2: quizData.questions[2].options,
                 3: quizData.questions[3].options
  }

  // Toggle the checkbox for a specific option
  const handleToggle = (optionIndex) => {
    const updatedOptions = {
      ...toggledOptions, // Spread the current state
      [optionIndex]: !toggledOptions[optionIndex], // Toggle the selected option
    };
    setToggledOptions(updatedOptions); // Update the state with the new toggled options

    const toggledCheckedIds = Object.keys(updatedOptions)
      .filter(key => updatedOptions[key]); // Find keys where value is true
    const Checked = toggledCheckedIds.map(id => check[currentQuestion][parseInt(id)]);

    if (currentQuestion === 1)
      setSelectedPurpose(Checked)
    if (currentQuestion === 2)
      setSelectedLocations(Checked)
    if (currentQuestion === 3)
      setSelectedFeatures(Checked)
  };

  
  const handleBtn = (option) => {
    if (currentQuestion === 4)
      handleClick("delivery", option) 
    if (currentQuestion === 5)
      handleClick("sharing", option)  
    if (currentQuestion === 6)
      handleClick("fleet", option) 
    if (currentQuestion === 7) 
      handleClick("firstdriver", option) 
    if (currentQuestion === 8)
      handleClick("age", option) 
  }

  // Ensure that questions are loaded before rendering
  if (!quizData || !quizData.questions) {
    return <div>Loading...</div>;
  }

  // Function to handle button class depending on question number
  const handleClass = () => {
    if (currentQuestion === 1 || currentQuestion === 2 || currentQuestion === 3)
      return 'mr-6 bg-intro py-2 px-6 rounded-xl xxs:text-base sm:text-lg md:text-xl lg:text-xl font-poppins text-white font-normal cursor-default tracking-tight w-96 text-left';
    else
      return 'mr-6 bg-intro py-2 px-6 rounded-xl xxs:text-base sm:text-lg md:text-xl lg:text-xl font-poppins text-white font-normal transition-all duration-150 hover:bg-intro_button tracking-tight w-96 text-left';
  };


  return (
    <div className="bg-gradient-to-t from-[#2F4F4F] to-[#081D1C] w-full h-[1024px] py-24 md:px-5 sm:px-0">
      <div className="bg-white rounded-3xl lg:p-24 md:p-20 sm:p-16 xxs:p-10 max-w-[1024px] mx-auto ">
        {/* Render the current question */}
        <p className="mb-10 font-inter xxs:text-xl sm:text-2xl md:text-2xl lg:text-4xl font-bold tracking-tighter text-black">
          {quizData.questions[currentQuestion].question}
        </p>
        <ul className="mt-4 space-y-2">
          {/* Render the options for the current question */}
          {quizData.questions[currentQuestion].options.map((option, index) => (
            <li key={index} className="flex items-center">
              {currentQuestion !== 8 ?
              <button
              name={`question-${currentQuestion}`}
              id={`option-${index}`}
              className={handleClass(index)}
              onClick={() => {
                if (currentQuestion === 0 && index === 0) {
                  handlePanel(); // Show panel for the first question's first option
                } else if (currentQuestion !== 1 && currentQuestion !== 2 && currentQuestion !== 3) {
                  handleNext(); // Handle for other questions not equal to 1, 2, or 3
                }
              
                // Additional condition for specific question numbers
                if ([4, 5, 6, 7, 8].includes(currentQuestion)) {
                  handleBtn(option);
                }
              }
              
              }
            >
              {option}
            </button>
            :
            <Link href="/carfinder/carfinder-result">
            <button
            name={`question-${currentQuestion}`}
            id={`option-${index}`}
            
            className={handleClass(index)}
            onClick={() => {
              if (currentQuestion === 0 && index === 0) {
                handlePanel(); // Show panel for the first question's first option
              } else if (currentQuestion !== 1 && currentQuestion !== 2 && currentQuestion !== 3) {
                handleNext(); // Handle for other questions not equal to 1, 2, or 3
              }
            
              // Additional condition for specific question numbers
              if ([4, 5, 6, 7, 8].includes(currentQuestion)) {
                handleBtn(option);
              }
            }
            
            }>
              {option}
            </button>
            </Link>}
              
              {currentQuestion === 1 || currentQuestion === 2 || currentQuestion === 3 ? (
                <button onClick={() => handleToggle(index)}>
                  {toggledOptions[index] ? (
                    <svg
                    width="35"
                    height="35"
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
                      width="35"
                      height="35"
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
              ) : null}
            </li>
          ))}
        </ul>
        {showOverlay && <OverlayPopover handleNext={handleNext} handlePanel={handlePanel} onBrandsSelected={handleSelectedBrands}/>}
        {currentQuestion === 1 || currentQuestion === 2 || currentQuestion === 3 ? 
          <div className="flex justify-start mt-6 gap-8 font-inter font-bold text-lg mb-10">
            {/* Previous button */}
            <button
              onClick={handlePrev}
              disabled={currentQuestion === 0}
            >
              <svg width="90" height="80" viewBox="0 0 90 80" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3.5 10C3.5 6.41015 6.41015 3.5 10 3.5H79C82.5899 3.5 85.5 6.41015 85.5 10V70C85.5 73.5899 82.5899 76.5 79 76.5H10C6.41015 76.5 3.5 73.5899 3.5 70V10Z" stroke="#17252A" strokeWidth="7" strokeMiterlimit="2"/>
                <path d="M20.2642 65V50.4545H26.0881C27.1581 50.4545 28.0507 50.6132 28.7656 50.9304C29.4806 51.2476 30.018 51.688 30.3778 52.2514C30.7377 52.8101 30.9176 53.4541 30.9176 54.1832C30.9176 54.7514 30.804 55.2509 30.5767 55.6818C30.3494 56.108 30.0369 56.4583 29.6392 56.733C29.2462 57.0028 28.7964 57.1946 28.2898 57.3082V57.4503C28.8438 57.474 29.3622 57.6302 29.8452 57.919C30.3329 58.2079 30.7282 58.6127 31.0312 59.1335C31.3343 59.6496 31.4858 60.2652 31.4858 60.9801C31.4858 61.7519 31.294 62.4408 30.9105 63.0469C30.5317 63.6482 29.9706 64.1241 29.2273 64.4744C28.4839 64.8248 27.5677 65 26.4787 65H20.2642ZM23.3395 62.4858H25.8466C26.7036 62.4858 27.3286 62.3224 27.7216 61.9957C28.1146 61.6643 28.3111 61.224 28.3111 60.6747C28.3111 60.2723 28.214 59.9171 28.0199 59.6094C27.8258 59.3016 27.5488 59.0601 27.1889 58.8849C26.8338 58.7098 26.41 58.6222 25.9176 58.6222H23.3395V62.4858ZM23.3395 56.5412H25.6193C26.0407 56.5412 26.4148 56.4678 26.7415 56.321C27.0729 56.1695 27.3333 55.9564 27.5227 55.6818C27.7169 55.4072 27.8139 55.0781 27.8139 54.6946C27.8139 54.169 27.6269 53.7453 27.2528 53.4233C26.8835 53.1013 26.358 52.9403 25.6761 52.9403H23.3395V56.5412ZM36.5408 65.206C35.8448 65.206 35.2246 65.0852 34.68 64.8438C34.1355 64.5975 33.7047 64.2353 33.3874 63.7571C33.0749 63.2741 32.9187 62.6728 32.9187 61.9531C32.9187 61.3471 33.0299 60.8381 33.2525 60.4261C33.475 60.0142 33.7781 59.6828 34.1616 59.4318C34.5451 59.1809 34.9807 58.9915 35.4684 58.8636C35.9608 58.7358 36.4769 58.6458 37.0167 58.5938C37.6512 58.5275 38.1625 58.4659 38.5508 58.4091C38.939 58.3475 39.2208 58.2576 39.396 58.1392C39.5711 58.0208 39.6587 57.8456 39.6587 57.6136V57.571C39.6587 57.1212 39.5167 56.7732 39.2326 56.527C38.9532 56.2808 38.5555 56.1577 38.0394 56.1577C37.4949 56.1577 37.0617 56.2784 36.7397 56.5199C36.4177 56.7566 36.2047 57.0549 36.1005 57.4148L33.3022 57.1875C33.4442 56.5246 33.7236 55.9517 34.1403 55.4688C34.5569 54.9811 35.0943 54.607 35.7525 54.3466C36.4154 54.0814 37.1824 53.9489 38.0536 53.9489C38.6597 53.9489 39.2397 54.0199 39.7937 54.1619C40.3524 54.304 40.8472 54.5241 41.2781 54.8224C41.7137 55.1207 42.0569 55.5043 42.3079 55.973C42.5588 56.437 42.6843 56.9934 42.6843 57.642V65H39.815V63.4872H39.7298C39.5546 63.8281 39.3202 64.1288 39.0266 64.3892C38.7331 64.6449 38.3803 64.8461 37.9684 64.9929C37.5565 65.1349 37.0806 65.206 36.5408 65.206ZM37.4073 63.1179C37.8524 63.1179 38.2454 63.0303 38.5863 62.8551C38.9272 62.6752 39.1947 62.4337 39.3888 62.1307C39.583 61.8277 39.68 61.4844 39.68 61.1009V59.9432C39.5853 60.0047 39.4551 60.0616 39.2894 60.1136C39.1284 60.161 38.9461 60.206 38.7425 60.2486C38.5389 60.2865 38.3353 60.322 38.1317 60.3551C37.9281 60.3835 37.7435 60.4096 37.5778 60.4332C37.2227 60.4853 36.9125 60.5682 36.6474 60.6818C36.3822 60.7955 36.1763 60.9493 36.0295 61.1435C35.8827 61.3329 35.8093 61.5696 35.8093 61.8537C35.8093 62.2656 35.9585 62.5805 36.2567 62.7983C36.5598 63.0114 36.9433 63.1179 37.4073 63.1179ZM49.9606 65.2131C48.8432 65.2131 47.882 64.9763 47.0771 64.5028C46.2769 64.0246 45.6613 63.3617 45.2305 62.5142C44.8043 61.6667 44.5913 60.6913 44.5913 59.5881C44.5913 58.4706 44.8067 57.4905 45.2376 56.6477C45.6732 55.8002 46.2911 55.1397 47.0913 54.6662C47.8915 54.188 48.8432 53.9489 49.9464 53.9489C50.8981 53.9489 51.7314 54.1217 52.4464 54.4673C53.1613 54.813 53.7272 55.2983 54.1438 55.9233C54.5605 56.5483 54.7901 57.2822 54.8327 58.125H51.9776C51.8971 57.5805 51.6841 57.1425 51.3384 56.8111C50.9975 56.4749 50.5501 56.3068 49.9961 56.3068C49.5273 56.3068 49.1178 56.4347 48.7674 56.6903C48.4218 56.9413 48.1519 57.3082 47.9577 57.7912C47.7636 58.2741 47.6665 58.8589 47.6665 59.5455C47.6665 60.2415 47.7612 60.8333 47.9506 61.321C48.1448 61.8087 48.417 62.1804 48.7674 62.4361C49.1178 62.6918 49.5273 62.8196 49.9961 62.8196C50.3417 62.8196 50.6519 62.7486 50.9265 62.6065C51.2058 62.4645 51.4355 62.2585 51.6154 61.9886C51.8001 61.714 51.9208 61.3849 51.9776 61.0014H54.8327C54.7854 61.8348 54.5581 62.5687 54.1509 63.2031C53.7485 63.8329 53.1921 64.3253 52.4819 64.6804C51.7717 65.0355 50.9312 65.2131 49.9606 65.2131ZM59.5114 61.8608L59.5185 58.2315H59.9588L63.4531 54.0909H66.9261L62.2315 59.5739H61.5142L59.5114 61.8608ZM56.7699 65V50.4545H59.7955V65H56.7699ZM63.5881 65L60.3778 60.2486L62.3949 58.1108L67.1321 65H63.5881Z" fill="#17252A"/>
                <path d="M25.5858 26.5858C24.8047 27.3668 24.8047 28.6332 25.5858 29.4142L38.3137 42.1421C39.0948 42.9232 40.3611 42.9232 41.1421 42.1421C41.9232 41.3611 41.9232 40.0948 41.1421 39.3137L29.8284 28L41.1421 16.6863C41.9232 15.9052 41.9232 14.6389 41.1421 13.8579C40.3611 13.0768 39.0948 13.0768 38.3137 13.8579L25.5858 26.5858ZM60 26L27 26V30L60 30V26Z" fill="#17252A"/>
              </svg>

            </button>
            
            {/* Next button */}
            <button
              onClick={handleNext}
              >
              <svg width="90" height="80" viewBox="0 0 90 80" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M0 10C0 4.47715 4.47715 0 10 0H79C84.5228 0 89 4.47715 89 10V70C89 75.5228 84.5228 80 79 80H10C4.47715 80 0 75.5228 0 70V10Z" fill="#17252A"/>
                <path d="M32.4304 50.4545V65H29.7741L23.446 55.8452H23.3395V65H20.2642V50.4545H22.9631L29.2415 59.6023H29.3693V50.4545H32.4304ZM39.886 65.2131C38.7638 65.2131 37.7979 64.9858 36.9883 64.5312C36.1834 64.072 35.5631 63.4233 35.1275 62.5852C34.6919 61.7424 34.4741 60.7457 34.4741 59.5952C34.4741 58.473 34.6919 57.4882 35.1275 56.6406C35.5631 55.7931 36.1763 55.1326 36.967 54.6591C37.7624 54.1856 38.6952 53.9489 39.7653 53.9489C40.485 53.9489 41.1549 54.0649 41.7752 54.2969C42.4002 54.5241 42.9447 54.8674 43.4087 55.3267C43.8775 55.786 44.2421 56.3636 44.5025 57.0597C44.7629 57.7509 44.8931 58.5606 44.8931 59.4886V60.3196H35.6815V58.4446H42.0451C42.0451 58.009 41.9504 57.6231 41.761 57.2869C41.5716 56.9508 41.3088 56.688 40.9727 56.4986C40.6412 56.3045 40.2553 56.2074 39.815 56.2074C39.3557 56.2074 38.9485 56.3139 38.5934 56.527C38.243 56.7353 37.9684 57.017 37.7695 57.3722C37.5707 57.7225 37.4689 58.1132 37.4641 58.544V60.3267C37.4641 60.8665 37.5636 61.3329 37.7624 61.7259C37.966 62.1188 38.2525 62.4219 38.6218 62.6349C38.9911 62.848 39.4291 62.9545 39.9357 62.9545C40.2719 62.9545 40.5797 62.9072 40.859 62.8125C41.1384 62.7178 41.3775 62.5758 41.5763 62.3864C41.7752 62.197 41.9267 61.965 42.0309 61.6903L44.8292 61.875C44.6871 62.5473 44.396 63.1345 43.9556 63.6364C43.52 64.1335 42.9566 64.5218 42.2653 64.8011C41.5787 65.0758 40.7856 65.2131 39.886 65.2131ZM49.2006 54.0909L51.2035 57.9048L53.256 54.0909H56.3597L53.1992 59.5455L56.445 65H53.3555L51.2035 61.2287L49.087 65H45.962L49.2006 59.5455L46.0756 54.0909H49.2006ZM63.9592 54.0909V56.3636H57.3896V54.0909H63.9592ZM58.881 51.4773H61.9066V61.6477C61.9066 61.9271 61.9492 62.1449 62.0344 62.3011C62.1197 62.4527 62.238 62.5592 62.3896 62.6207C62.5458 62.6823 62.7257 62.7131 62.9293 62.7131C63.0714 62.7131 63.2134 62.7012 63.3555 62.6776C63.4975 62.6491 63.6064 62.6278 63.6822 62.6136L64.158 64.8651C64.0065 64.9124 63.7934 64.9669 63.5188 65.0284C63.2442 65.0947 62.9104 65.1349 62.5174 65.1491C61.7882 65.1776 61.149 65.0805 60.5998 64.858C60.0553 64.6354 59.6315 64.2898 59.3285 63.821C59.0254 63.3523 58.8763 62.7604 58.881 62.0455V51.4773Z" fill="white"/>
                <path d="M61.4142 29.4142C62.1953 28.6332 62.1953 27.3668 61.4142 26.5858L48.6863 13.8579C47.9052 13.0768 46.6389 13.0768 45.8579 13.8579C45.0768 14.6389 45.0768 15.9052 45.8579 16.6863L57.1716 28L45.8579 39.3137C45.0768 40.0948 45.0768 41.3611 45.8579 42.1421C46.6389 42.9232 47.9052 42.9232 48.6863 42.1421L61.4142 29.4142ZM27 30H60V26H27V30Z" fill="white"/>
              </svg>

            </button> 
          </div>
            :
            <div className="flex justify-start mt-6 gap-8 font-inter font-bold text-lg">
            {/* Previous button */}
              <button
                onClick={handlePrev}
                disabled={currentQuestion === 0}
                className="mb-10"
              >
                <svg width="90" height="80" viewBox="0 0 90 80" fill="none" xmlns="http://www.w3.org/2000/svg" >
                  <path d="M3.5 10C3.5 6.41015 6.41015 3.5 10 3.5H79C82.5899 3.5 85.5 6.41015 85.5 10V70C85.5 73.5899 82.5899 76.5 79 76.5H10C6.41015 76.5 3.5 73.5899 3.5 70V10Z" stroke="#17252A" strokeWidth="7" strokeMiterlimit="2"/>
                  <path d="M20.2642 65V50.4545H26.0881C27.1581 50.4545 28.0507 50.6132 28.7656 50.9304C29.4806 51.2476 30.018 51.688 30.3778 52.2514C30.7377 52.8101 30.9176 53.4541 30.9176 54.1832C30.9176 54.7514 30.804 55.2509 30.5767 55.6818C30.3494 56.108 30.0369 56.4583 29.6392 56.733C29.2462 57.0028 28.7964 57.1946 28.2898 57.3082V57.4503C28.8438 57.474 29.3622 57.6302 29.8452 57.919C30.3329 58.2079 30.7282 58.6127 31.0312 59.1335C31.3343 59.6496 31.4858 60.2652 31.4858 60.9801C31.4858 61.7519 31.294 62.4408 30.9105 63.0469C30.5317 63.6482 29.9706 64.1241 29.2273 64.4744C28.4839 64.8248 27.5677 65 26.4787 65H20.2642ZM23.3395 62.4858H25.8466C26.7036 62.4858 27.3286 62.3224 27.7216 61.9957C28.1146 61.6643 28.3111 61.224 28.3111 60.6747C28.3111 60.2723 28.214 59.9171 28.0199 59.6094C27.8258 59.3016 27.5488 59.0601 27.1889 58.8849C26.8338 58.7098 26.41 58.6222 25.9176 58.6222H23.3395V62.4858ZM23.3395 56.5412H25.6193C26.0407 56.5412 26.4148 56.4678 26.7415 56.321C27.0729 56.1695 27.3333 55.9564 27.5227 55.6818C27.7169 55.4072 27.8139 55.0781 27.8139 54.6946C27.8139 54.169 27.6269 53.7453 27.2528 53.4233C26.8835 53.1013 26.358 52.9403 25.6761 52.9403H23.3395V56.5412ZM36.5408 65.206C35.8448 65.206 35.2246 65.0852 34.68 64.8438C34.1355 64.5975 33.7047 64.2353 33.3874 63.7571C33.0749 63.2741 32.9187 62.6728 32.9187 61.9531C32.9187 61.3471 33.0299 60.8381 33.2525 60.4261C33.475 60.0142 33.7781 59.6828 34.1616 59.4318C34.5451 59.1809 34.9807 58.9915 35.4684 58.8636C35.9608 58.7358 36.4769 58.6458 37.0167 58.5938C37.6512 58.5275 38.1625 58.4659 38.5508 58.4091C38.939 58.3475 39.2208 58.2576 39.396 58.1392C39.5711 58.0208 39.6587 57.8456 39.6587 57.6136V57.571C39.6587 57.1212 39.5167 56.7732 39.2326 56.527C38.9532 56.2808 38.5555 56.1577 38.0394 56.1577C37.4949 56.1577 37.0617 56.2784 36.7397 56.5199C36.4177 56.7566 36.2047 57.0549 36.1005 57.4148L33.3022 57.1875C33.4442 56.5246 33.7236 55.9517 34.1403 55.4688C34.5569 54.9811 35.0943 54.607 35.7525 54.3466C36.4154 54.0814 37.1824 53.9489 38.0536 53.9489C38.6597 53.9489 39.2397 54.0199 39.7937 54.1619C40.3524 54.304 40.8472 54.5241 41.2781 54.8224C41.7137 55.1207 42.0569 55.5043 42.3079 55.973C42.5588 56.437 42.6843 56.9934 42.6843 57.642V65H39.815V63.4872H39.7298C39.5546 63.8281 39.3202 64.1288 39.0266 64.3892C38.7331 64.6449 38.3803 64.8461 37.9684 64.9929C37.5565 65.1349 37.0806 65.206 36.5408 65.206ZM37.4073 63.1179C37.8524 63.1179 38.2454 63.0303 38.5863 62.8551C38.9272 62.6752 39.1947 62.4337 39.3888 62.1307C39.583 61.8277 39.68 61.4844 39.68 61.1009V59.9432C39.5853 60.0047 39.4551 60.0616 39.2894 60.1136C39.1284 60.161 38.9461 60.206 38.7425 60.2486C38.5389 60.2865 38.3353 60.322 38.1317 60.3551C37.9281 60.3835 37.7435 60.4096 37.5778 60.4332C37.2227 60.4853 36.9125 60.5682 36.6474 60.6818C36.3822 60.7955 36.1763 60.9493 36.0295 61.1435C35.8827 61.3329 35.8093 61.5696 35.8093 61.8537C35.8093 62.2656 35.9585 62.5805 36.2567 62.7983C36.5598 63.0114 36.9433 63.1179 37.4073 63.1179ZM49.9606 65.2131C48.8432 65.2131 47.882 64.9763 47.0771 64.5028C46.2769 64.0246 45.6613 63.3617 45.2305 62.5142C44.8043 61.6667 44.5913 60.6913 44.5913 59.5881C44.5913 58.4706 44.8067 57.4905 45.2376 56.6477C45.6732 55.8002 46.2911 55.1397 47.0913 54.6662C47.8915 54.188 48.8432 53.9489 49.9464 53.9489C50.8981 53.9489 51.7314 54.1217 52.4464 54.4673C53.1613 54.813 53.7272 55.2983 54.1438 55.9233C54.5605 56.5483 54.7901 57.2822 54.8327 58.125H51.9776C51.8971 57.5805 51.6841 57.1425 51.3384 56.8111C50.9975 56.4749 50.5501 56.3068 49.9961 56.3068C49.5273 56.3068 49.1178 56.4347 48.7674 56.6903C48.4218 56.9413 48.1519 57.3082 47.9577 57.7912C47.7636 58.2741 47.6665 58.8589 47.6665 59.5455C47.6665 60.2415 47.7612 60.8333 47.9506 61.321C48.1448 61.8087 48.417 62.1804 48.7674 62.4361C49.1178 62.6918 49.5273 62.8196 49.9961 62.8196C50.3417 62.8196 50.6519 62.7486 50.9265 62.6065C51.2058 62.4645 51.4355 62.2585 51.6154 61.9886C51.8001 61.714 51.9208 61.3849 51.9776 61.0014H54.8327C54.7854 61.8348 54.5581 62.5687 54.1509 63.2031C53.7485 63.8329 53.1921 64.3253 52.4819 64.6804C51.7717 65.0355 50.9312 65.2131 49.9606 65.2131ZM59.5114 61.8608L59.5185 58.2315H59.9588L63.4531 54.0909H66.9261L62.2315 59.5739H61.5142L59.5114 61.8608ZM56.7699 65V50.4545H59.7955V65H56.7699ZM63.5881 65L60.3778 60.2486L62.3949 58.1108L67.1321 65H63.5881Z" fill="#17252A"/>
                  <path d="M25.5858 26.5858C24.8047 27.3668 24.8047 28.6332 25.5858 29.4142L38.3137 42.1421C39.0948 42.9232 40.3611 42.9232 41.1421 42.1421C41.9232 41.3611 41.9232 40.0948 41.1421 39.3137L29.8284 28L41.1421 16.6863C41.9232 15.9052 41.9232 14.6389 41.1421 13.8579C40.3611 13.0768 39.0948 13.0768 38.3137 13.8579L25.5858 26.5858ZM60 26L27 26V30L60 30V26Z" fill="#17252A"/>
                </svg>

              </button>
            </div> 
            }
      </div>
    </div>
  );
};

export default Question;
