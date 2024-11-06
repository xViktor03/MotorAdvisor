import HeroImage from "@components/Home Page/HeroImage"
import React from "react"
import HeroText from "@components/Home Page/HeroText"
import NewsComp from "@components/Home Page/NewsComp"
import Faq2 from "@components/Home Page/Faq2"
import Footer2 from "@components/Layout/Footer2"

const Home = () => {
  return (
    <div>
      <HeroImage/>
      <HeroText/>
      <NewsComp/>
      <Faq2/>
      <Footer2/>
    </div>
  )
}

export default Home