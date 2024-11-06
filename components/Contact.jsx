import React from 'react'
import Link from 'next/link'

const Contact = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-intro py-8 font-inter">
      <div className="bg-white p-8 rounded-lg shadow-2xl max-w-4xl h-vh w-full">
        <h1 className="text-5xl font-black mb-4 text-center">Get in touch with us!</h1>
        <p className="text-2xl font-bold text-intro text-center mb-6">
          We would love to hear from you! Please reach out to us for any of the following reasons:
        </p>
        <ul className="list-disc place-content-center pl-5 font-bold text-intro mb-4">
          <li>Inquiries about our products or services</li>
          <li>Support or troubleshooting</li>
          <li>Feedback or suggestions</li>
          <li>Collaborations and partnerships</li>
          <li>General questions or concerns</li>
        </ul>
        <p className="text-lg text-center text-intro mt-6 mb-6">
          You can reach us at: 
          <a href="mailto:support@example.com" className="text-intro hover:underline ml-1">
            support@example.com
          </a>
        </p>
        <div className="flex justify-center">
          <Link
            href="mailto:support@example.com"
            className="intro_btn"
          >
            Email Us
          </Link>
        </div>
      </div>
    </div>
  )
}

export default Contact