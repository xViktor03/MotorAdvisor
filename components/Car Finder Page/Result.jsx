'use client';

import React, { useEffect, useState } from 'react';
import cars from '@constants/carsDatabase.json'
import survey from '@constants/survey.json'
import Link from 'next/link'



const Result = () => {
  const [jsonData, setJsonData] = useState({});
  const [isDataLoaded, setIsDataLoaded] = useState(false);
  const [filteredData, setFilteredData] = useState([])
  const [highestSpeedCar, setHighestSpeedCar] = useState(null);
  const [highestOffroadCar, setHighestOffroadCar] = useState(null);
  const [highestMaintenanceCar, setHighestMaintenanceCar] = useState(null);
  const [highestComfortCar, setHighestComfortCar] = useState(null)



useEffect(() => {
  // Fetch data from localStorage
  const savedData = localStorage.getItem('jsonData');
  if (savedData) {
    setJsonData(JSON.parse(savedData));
  } else {
    setJsonData({});
  }
  setIsDataLoaded(true); // Set flag to true once data is loaded
}, []);

useEffect(() => {
  if (isDataLoaded) {
    // Add further data modification logic here, only executed once data is fully loaded
    

  const brands = jsonData.brands;

  const filterCarsByBrand = (carList, selectedBrands) => {
    // If selectedBrands is empty, return the full carList
    if (selectedBrands.length === 0) {
      return carList;
    }
    
    // Otherwise, filter carList to include only cars with a brand in selectedBrands
    return carList.filter(car => selectedBrands.includes(car.Brand));
  };


  const filteredCarsbyBrand = filterCarsByBrand(cars, brands);
  let purposes = jsonData.purpose;
  if (jsonData.delivery == "Yes")
    purposes.push("Delivery/transportation services") 
  if (jsonData.fleet == "Yes")
    purposes.push("Company fleet")
  if (jsonData.sharing == "Yes")
    purposes.push("Ride-sharing")
  if (jsonData.firstdriver == "Yes")
    purposes.push("First driver car")
  
  const filterCarsByPurpose = (carList, selectedPurposes) => {
    let comfort = [0,0];
    let space = [0,0];
    let speed = [0,0];
    let offroad = [0,0];
    let numberOfPurposes = 0;
    
    selectedPurposes.forEach((purposeData) => {
      numberOfPurposes ++;
      for (let index = 0; index <= 1; index ++) {
        comfort[index] += survey.comfort[purposeData][index]
        space[index] += survey.space[purposeData][index]
        speed[index] += survey.speed[purposeData][index]
        offroad[index] += survey.offroad[purposeData][index]
      
      }
    })
  
    for (let index = 0; index <= 1; index ++) {
        comfort[index] = comfort[index]/numberOfPurposes
        space[index] = space[index]/numberOfPurposes
        speed[index] = speed[index]/numberOfPurposes
        offroad[index] = offroad[index]/numberOfPurposes
    }

    let lastCarList =  carList.filter(car =>
      car.Comfort >= comfort[0] && car.Comfort <= comfort[1] &&
      car.Speed >= speed[0] && car.Speed <= speed[1] &&
      car.Space >= space[0] && car.Space <= space[1] &&
      car.OffroadTowing >= offroad[0] && car.OffroadTowing <= offroad[1]
    );
    
    if (selectedPurposes.includes("Delivery/transportation services"))
      lastCarList = lastCarList.filter(car =>
        car.BodyType == "Off-road vehicle, Pick-up " || 
        car.BodyType == "Pick-up " ||
        car.BodyType == "Minivan " ||
        car.BodyType == "Van "
      )
    if (selectedPurposes.includes("Long drives"))
      lastCarList = lastCarList.filter(car =>
        car.FuelType == "Diesel " ||
        car.FuelType == "Diesel / electricity "
    )
    
    let offroadcars = [
      "Off-road vehicle, Pick-up ",
      "Off-road vehicle ",
      "Off-road vehicle, SUV ",
      "Off-road vehicle, Station wagon (estate) ",
      "Pick-up "
    ]

    
    if (selectedPurposes.includes("Heavy loads or towing"))
      lastCarList = lastCarList.filter(car =>
        offroadcars.includes(car.BodyType)
    )

    /*let smallcars = [
      "Cabriolet, Coupe ",
      "Hatchback, Crossover ",
      "Hatchback, Fastback ",
      "Hatchback ",
      "Cabriolet, Hatchback ",
      "Coupe, Hatchback ",
      "Coupe - Cabriolet ",
      "Coupe - Cabriolet, Roadster ",
      "Off-road vehicle, Coupe ",
      "Targa ",
      "Coupe, Fastback ",
      "Cabriolet ",
      "Coupe ",
      "Roadster ",
      "Quadricycle "
    ]

    if (selectedPurposes.includes("First driver car"))
      lastCarList = lastCarList.filter(car =>
        smallcars.includes(car.BodyType)
    )
    */

    return lastCarList;
    
  }

  
  const filteredCarsByPurpose = filterCarsByPurpose(filteredCarsbyBrand, purposes)

  const location = jsonData.locations
  
  const filterCarsbyLocation = (carsList, selectedLocations) => {
    let carssmall = [
      "Crossover, Fastback ", "Crossover ", "Coupe, Liftback ", "Cabriolet, Coupe ",
      "Hatchback, Crossover ", "Hatchback, Fastback ", "Hatchback ", "Cabriolet, Hatchback ",
      "Coupe, Hatchback ", "Coupe - Cabriolet ", "Coupe - Cabriolet, Roadster ",
      "Off-road vehicle, Coupe ", "Targa ", "Coupe, Fastback ", "Cabriolet ",
      "Coupe ", "Roadster ", "Quadricycle "
    ]
    
    let carsmedium =
      ["SUV ", "SUV, MPV ", "SAV ", "SAC ", "Off-road vehicle, Station wagon (estate) ", "Pick-up ", "Off-road vehicle, Pick-up ", 
        "Sedan ", "Sedan, Fastback ", "Grand Tourer ", "Fastback ", "Liftback ", "Station wagon (estate) ", "Coupe, SUV ", "Off-road vehicle, SUV ",
        "Cabriolet, SUV ", "Off-road vehicle, Cabriolet, SUV ", "Off-road vehicle ", "Off-road vehicle, Cabriolet ", "Station wagon (estate), MPV ",
        "Station wagon (estate), Crossover ", "SUV, Crossover ", "Coupe, SUV, Crossover ", "Coupe, CUV ", "CUV", "Minivan ", "Minivan, Crossover ", 
        "Minivan, MPV ", "Van ", "MPV ", "Crossover, Fastback ", "Crossover ", "Coupe, Liftback "]

    let carslarge = [
      "Off-road vehicle, Pick-up ", "Off-road vehicle ", "Off-road vehicle, SUV ",
      "Off-road vehicle, Station wagon (estate) ", "Pick-up ", "Off-road vehicle, Cabriolet ",
      "Off-road vehicle, Cabriolet, SUV ", "SUV ", "Off-road vehicle, Coupe ", "SAV ",
      "SUV, MPV ", "Cabriolet, SUV ", "SAC ", "Coupe, SUV ", "SUV, Crossover ",
      "Coupe, SUV, Crossover ", "Coupe, CUV ", "CUV"
    ]
    
    let finale = []

    if (selectedLocations.includes("City streets")) 
      finale = finale.concat(carssmall);
    
  
    if (selectedLocations.includes("Suburban or extraurban areas")) 
      finale = finale.concat(carsmedium);
    
  
    if (selectedLocations.includes("Off-road or rough terrain")) 
      finale = finale.concat(carslarge);

    const uniqueArray = [...new Set(finale)];
    finale = uniqueArray;
    
    carsList = carsList.filter(car =>
      finale.includes(car.BodyType)
    )



    let finaleEngines = []

    let cityEngines = [
      "PHEV (Plug-in Hybrid Electric Vehicle) ","MHEV (Mild Hybrid Electric Vehicle, power-assist hybrid, battery-assisted hybrid vehicles, BAHV) ",
      "BEV (Electric Vehicle) ","FHEV (Full Hybrid Electric Vehicle) "
    ]

    let nonCityEngines = [
      "PHEV (Plug-in Hybrid Electric Vehicle) ","MHEV (Mild Hybrid Electric Vehicle, power-assist hybrid, battery-assisted hybrid vehicles, BAHV) ",
      "FHEV (Full Hybrid Electric Vehicle) ","Internal Combustion engine "
    ]

    if (selectedLocations.includes('City streets'))
      finaleEngines = finaleEngines.concat(cityEngines)

    if (selectedLocations.includes('Suburban or extraurban areas'))
      finaleEngines = finaleEngines.concat(nonCityEngines)

    if (selectedLocations.includes('Off-road or rough terrain'))
      finaleEngines = finaleEngines.concat(nonCityEngines)

    const uniqueArrayEngines = [...new Set(finaleEngines)];
    finaleEngines = uniqueArrayEngines;


    carsList = carsList.filter(car =>
      finaleEngines.includes(car.EngineType)
    )

    return carsList;
    
  }

  const filteredCarsByLocation = filterCarsbyLocation(filteredCarsByPurpose, location)

  const feature = jsonData.features

  const filterCarsByFeatures = (lastCarList, selectedFeatures) =>{
    if (selectedFeatures.includes("LED headlights"))
      lastCarList = lastCarList.filter(car =>
        car.LED == "yes"
      );

    if (selectedFeatures.includes("Advanced safety features"))
      lastCarList = lastCarList.filter(car =>
        car.SafetyFeatures == "yes"
      );
    
    if (selectedFeatures.includes("Ambient interior lighting"))
      lastCarList = lastCarList.filter(car =>
        car.AmbientLightning == "yes"
      );
    
    if (selectedFeatures.includes("Infotainment"))
      lastCarList = lastCarList.filter(car =>
        car.Infotainment == "yes"
      );
    
    if (selectedFeatures.includes("Apple CarPlay/Android Auto"))
      lastCarList = lastCarList.filter(car =>
        car.AppleCarplayAndroidAuto == "yes"
      );
    
    if (selectedFeatures.includes("Parking sensors"))
      lastCarList = lastCarList.filter(car =>
        car.ParkingSensors == "yes"
      );
    
    if (selectedFeatures.includes("Parking cameras"))
      lastCarList = lastCarList.filter(car =>
        car.ParkingCameras == "yes"
      );
    
    if (selectedFeatures.includes("Digital driver's display"))
      lastCarList = lastCarList.filter(car =>
        car.DigitalDriversDisplay == "yes"
      );
    
    if (selectedFeatures.includes("Air suspension"))
      lastCarList = lastCarList.filter(car =>
        car.AirSuspension == "yes"
      );
  
    return lastCarList

  }

  const filteredCarsByFeatures = filterCarsByFeatures(filteredCarsByLocation, feature)

  const ages = jsonData.age

  const filterCarsByYear = (carsList, selectedAge) => {
    if (selectedAge == "New")
      carsList = carsList.filter(car =>
        car.Age >= 2023
      )
    if (selectedAge == "Almost new")
      carsList = carsList.filter(car =>
        car.Age >= 2021
      )
    if (selectedAge == "Under 5 years")
      carsList = carsList.filter(car =>
        car.Age >= 2019
      )
    if (selectedAge == 'Under 10 years')
      carsList = carsList.filter(car =>
        car.Age >= 2014
      )
    if (selectedAge == "Around 15 years")
      carsList = carsList.filter(car =>
        car.Age >= 2004 && car.Age <= 2014
      )

    return carsList;
  }
      
  const filteredCars = filterCarsByYear(filteredCarsByFeatures, ages)

  setFilteredData(filteredCars)
  
  if (filteredCars.length > 0) {
    const speediestCar = filteredCars.reduce((prev, current) =>
      current.Speed > prev.Speed ? current : prev
    );
    setHighestSpeedCar(speediestCar);
  }
  if (filteredCars.length > 0) {
    const offroadiestCar = filteredCars.reduce((prev, current) =>
      current.OffroadTowing > prev.OffroadTowing ? current : prev
    );
    setHighestOffroadCar(offroadiestCar);
  }
  if (filteredCars.length > 0) {
    const economiestCar = filteredCars.reduce((prev, current) =>
      current.Maintenance > prev.Maintenance ? current : prev
    );
    setHighestMaintenanceCar(economiestCar);
  }
  if (filteredCars.length > 0) {
    const comfiestCar = filteredCars.reduce((prev, current) =>
      current.Comfort > prev.Comfort ? current : prev
    );
    setHighestComfortCar(comfiestCar);
  }

  }
}, [isDataLoaded, jsonData]);

  
// Group cars by Brand and Model
const carsGroupedByBrandModel = filteredData.reduce((acc, car) => {
  const key = `${car.Age}-${car.Brand}-${car.Model}-${car.GenerationName}`;
  if (!acc[key]) {
    acc[key] = [];
  }
  acc[key].push(car.EngineModification);
  return acc;
}, {});

const [modificationIndex, setModificationIndex] = useState({});

const toggleModification = (key) => {
  setModificationIndex((prevState) => ({
    ...prevState,
    [key]: prevState[key] !== undefined
      ? (prevState[key] + 1) % carsGroupedByBrandModel[key].length
      : 1, // Start with the second modification if undefined
  }));
};

return (
  <div className="px-80">
    {/*<div>{JSON.stringify(jsonData)}</div>
    */}
    <div className="global_text mt-16">Results</div>
    
    {
      filteredData.length === 0 ? 
      <div className="mb-96">
      <div className="sub_global_text my-8">
        Unfortunately, there are no cars that match your search.
      </div>
      <div className="flex justify-center">
        <Link href="../carfinder/carfinder-start">
          <button className="intro_btn">
            Go back
          </button>
          </Link>
      </div>
      </div>
      :
      <div className="sub_global_text my-8">
      {Object.keys(carsGroupedByBrandModel).length} unique cars found
    </div>
    }

    {highestSpeedCar && (
        <div className="py-10 px-4 mb-8 place-items-center rounded-3xl bg-intro_button font-inter text-white flex justify-around">
          <div className="font-inter text-white text-4xl font-black">
            Best for performance
          </div>
          <div>
          <div className="font-bold tracking-tight text-2xl">
            {highestSpeedCar.Age} {highestSpeedCar.Brand} {highestSpeedCar.Model}
          </div>
          <div className="font-semibold tracking-tight text-base">
            {highestSpeedCar.EngineModification}
          </div>
        </div>
        </div>
      )}
    {highestComfortCar && (
        <div className="py-10 px-4 mb-8 place-items-center rounded-3xl bg-intro_button font-inter text-white flex justify-around">
          <div>
          <div className="font-bold tracking-tight text-2xl">
          {highestComfortCar.Age} {highestComfortCar.Brand} {highestComfortCar.Model}
          </div>
          <div className="font-semibold tracking-tight text-base">
            {highestComfortCar.EngineModification}
          </div>
        </div>
        <div className="font-inter text-white text-4xl font-black">
            Best for comfort
          </div>
        </div>
      )}
    {highestOffroadCar && (
        <div className="py-10 px-4 mb-8 place-items-center rounded-3xl bg-intro_button font-inter text-white flex justify-around">
          <div className="font-inter text-white text-4xl font-black">
            Best for offroad
          </div>
          <div>
          <div className="font-bold tracking-tight text-2xl">
          {highestOffroadCar.Age} {highestOffroadCar.Brand} {highestOffroadCar.Model}
          </div>
          <div className="font-semibold tracking-tight text-base">
            {highestOffroadCar.EngineModification}
          </div>
        </div>
        </div>
      )}
    {highestMaintenanceCar && (
        <div className="py-10 px-4 mb-8 place-items-center rounded-3xl bg-intro_button font-inter text-white flex justify-around">
          
          <div>
          <div className="font-bold tracking-tight text-2xl">
            {highestMaintenanceCar.Age} {highestMaintenanceCar.Brand} {highestMaintenanceCar.Model}
          </div>
          <div className="font-semibold tracking-tight text-base">
            {highestMaintenanceCar.EngineModification}
          </div>
        </div>
        <div className="font-inter text-white text-4xl font-black">
            Best for economy
          </div>
        </div>
      )}

    <div className="grid grid-cols-2 gap-x-10 gap-y-5 my-20">
      {Object.entries(carsGroupedByBrandModel).map(([key, modifications], index) => (
        <div key={index} className="px-4 py-3 place-items-center rounded-3xl bg-navbar font-inter text-white">
          {/* Display Brand and Model */}
          <div className="font-bold tracking-tight text-2xl">
            {key.split('-').join(' ')}
          </div>
          <div className="flex gap-2">
          {/* Display the current EngineModification */}
          <div className="font-semibold tracking-tight text-base">
            {modifications[modificationIndex[key] || 0]}
          </div>
          {/* Arrow button to toggle modifications if there are multiple */}
          {modifications.length > 1 && (
            <button onClick={() => toggleModification(key)} className="text-xl font-bold">
              <svg width="23" height="15" viewBox="0 0 35 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M34.0607 13.0607C34.6464 12.4749 34.6464 11.5251 34.0607 10.9393L24.5147 1.3934C23.9289 0.807611 22.9792 0.807611 22.3934 1.3934C21.8076 1.97919 21.8076 2.92893 22.3934 3.51472L30.8787 12L22.3934 20.4853C21.8076 21.0711 21.8076 22.0208 22.3934 22.6066C22.9792 23.1924 23.9289 23.1924 24.5147 22.6066L34.0607 13.0607ZM0 13.5H33V10.5H0V13.5Z" fill="white"/>
              </svg>
            </button>
          )}
        </div>
        </div>
      ))}
    </div>
  </div>
);
}


export default Result;
