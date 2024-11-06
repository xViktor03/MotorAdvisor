import '@styles/globals.css';
import Navibar from "@components/Layout/Navibar"
import Footer2 from "@components/Layout/Footer2"
import Provider from "@components/Provider"


export const metadata = {
    title: "MotorAdvisor",
    description: 'Discover the car you need'

}
const RootLayout = ({ children }) => {
  return (
    <html lang="en" >
        <body>
          <Provider>
            <main>
                <Navibar className="z-50"/>
                {children}
            </main>
          </Provider>
        </body>
    </html>
  )
}

export default RootLayout