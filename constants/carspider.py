import scrapy
import logging
import re
from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
from time import sleep

class AutoDataSpider(scrapy.Spider):
    name = 'auto_data'
    allowed_domains = ['www.auto-data.net']
    start_urls = ['https://www.auto-data.net/en/']

    custom_settings = {
        'DOWNLOAD_DELAY': 0.1,  # Set a delay of 0.1 seconds between requests
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1  # Limit concurrent requests to 1
    }
   

    def parse(self, response):
        logging.info('Parsing start page: %s', response.url)
        brand_links = response.css('a.marki_blok::attr(href)').extract()[:-1]
        for brand_link in brand_links:
            yield response.follow(brand_link, callback=self.parse_brand)

    def parse_brand(self, response):
        logging.info('Parsing brand page: %s', response.url)
        brand_name = response.css('strong::text').get()
        models = response.css('a.modeli')
        for model in models:
            model_name = model.css('strong::text').get()
            model_link = model.css('::attr(href)').get()
            yield response.follow(model_link, callback=self.parse_model,
                                  meta={'brand_name': brand_name, 'model_name': model_name})

    def parse_model(self, response):
        logging.info('Parsing model page: %s', response.url)
        brand_name = response.meta['brand_name']
        model_name = response.meta['model_name']
        gen_names = response.css('th.i strong.tit::text').getall()
        generations = response.css('strong.end::text').getall()
        generation_links = response.css('th.i a::attr(href)').getall()
        current_data = response.css('strong.cur::text').getall()
        all_generations = current_data + generations
        for generation, generation_link, gen_name in zip(all_generations, generation_links, gen_names):
            yield response.follow(generation_link, callback=self.parse_generation,
                                  meta={'brand_name': brand_name, 'model_name': model_name,
                                        'generation': generation, 'gen_name': gen_name})

    def parse_generation(self, response):
        logging.info('Parsing generation page: %s', response.url)
        brand_name = response.meta['brand_name']
        model_name = response.meta['model_name']
        generation = response.meta['generation']
        gen_name = response.meta['gen_name']
        engine_config_links = response.css('th.i a::attr(href)').getall()
        for engine_config_link in engine_config_links:
            yield response.follow(engine_config_link, callback=self.parse_engine_config,
                                  meta={'brand_name': brand_name, 'model_name': model_name,
                                        'generation': generation, 'gen_name': gen_name})

    def parse_engine_config(self, response):
        logging.info('Parsing engine configuration page: %s', response.url)
        brand_name = response.meta['brand_name']
        model_name = response.meta['model_name']
        generation = response.meta['generation']
        gen_name = response.meta['gen_name']
        if brand_name in gen_name:
            gen_name = gen_name.replace(brand_name, "").strip()
        if model_name in gen_name:
            gen_name = gen_name.replace(model_name, "").strip()
        pattern = r'facelift \d{4}'
        gen_name = re.sub(pattern, '', gen_name).strip()
        headers = response.css('table.cardetailsout.car2 tr th::text').getall()
        cleaned_headers = [element for element in headers if element != ') ']
        filtered_headers = [item for item in cleaned_headers if item != 'CO']
        filtered_headers = [header for header in filtered_headers if header not in ["Charging ports", "Electric motor 1", "Electric motor 2", "Electric motor 3", "Electric motor 4", "Engine oil specification ", "Engine systems", "Battery location", "Battery location "]]

        descriptions = response.css('table.cardetailsout.car2 tr td::text').getall()
        cleaned_desc = [string.replace('\r', '').replace('\n', '').replace('\t', '') for string in descriptions]
        brushed_desc = [item for item in cleaned_desc if item != ') ']
        filtered_desc = [item for item in brushed_desc if item != ' ' and item not in ["Start & Stop System", "Particulate filter", "Under the rear seats ", "Under the trunk", "Cylinder deactivation system", "In the central tunnel", "Below the floor ", "Inside the trunk", "Behind the back wall of the passenger cabin", "Under the rear seats", "Below the floor, under the front seats", "Below the floor, under the rear seats", "Below the floor", "Under the front seats", "Below the floor, between front and rear seats", "Inside the trunk ", "Under the front hood", "Under the trunk ", "Cylinder deactivation system ", "In the central tunnel ", "Behind the back wall of the passenger cabin ", "Under the rear seats ", "Under the front seats ", "Below the floor, under the front seats ", "Below the floor, under the rear seats ", "Under the front hood ", "Below the floor, between front and rear seats "]]

        modification_index = filtered_headers.index('Modification (Engine) ') - 3
        engine_modification = filtered_desc[modification_index]

        type_index = filtered_headers.index('Powertrain Architecture ') - 3
        engine_type = filtered_desc[type_index]

        body_type_index = filtered_headers.index('Body type') - 3
        body_type = filtered_desc[body_type_index]

        seats = None
        if 'Seats ' in filtered_headers:
            seats_index = filtered_headers.index('Seats ') - 3
            seats = filtered_desc[seats_index]
            if "-" in seats:
                seats = self.seats_doors(seats)
                

        doors = None
        if 'Doors ' in filtered_headers:
            doors_index = filtered_headers.index('Doors ') - 3
            doors = filtered_desc[doors_index]
            if "-" in doors:
                doors = self.seats_doors(doors)
                

        fuel_combined_index = None
        fuel_consumption = None

        fuel_type = None
        if 'Fuel Type ' in filtered_headers:
            fuel_type_index = filtered_headers.index('Fuel Type ') - 3
            fuel_type = filtered_desc[fuel_type_index]

        power = None
        if 'Power ' in filtered_headers:
            power_index = filtered_headers.index('Power ') - 3
            power = filtered_desc[power_index]
        if 'System power ' in filtered_headers:
            power_index = filtered_headers.index('System power ') - 3
            power = filtered_desc[power_index]
        if 'Power (Ethanol - E85) ' in filtered_headers:
            power_index = filtered_headers.index('Power (Ethanol - E85) ') - 3
            power = filtered_desc[power_index]


        torque = None
        if 'Torque ' in filtered_headers:
            torque_index = filtered_headers.index('Torque ') - 3
            torque = filtered_desc[torque_index]
        if 'System torque ' in filtered_headers:
            torque_index = filtered_headers.index('System torque ') - 3
            torque = filtered_desc[torque_index]
        if 'Torque (Ethanol - E85) ' in filtered_headers:
            torque_index = filtered_headers.index('Torque (Ethanol - E85) ') - 3
            torque = filtered_desc[torque_index]

        
        kerb_weight = None
        if 'Kerb Weight ' in filtered_headers:
            kerb_weight_index = filtered_headers.index('Kerb Weight ') - 3
            kerb_weight = filtered_desc[kerb_weight_index]
            # Process kerb_weight if it matches the format "number1-number2 kg"
            if "-" in kerb_weight:
                kerb_weight = self.parse_weight(kerb_weight)
                kerb_weight = str(kerb_weight)

        boot_space = None
        if ('Trunk (boot) space - minimum ') in filtered_headers:
            boot_space_index = filtered_headers.index('Trunk (boot) space - minimum ') - 3
            boot_space = filtered_desc[boot_space_index]
            if "-" in boot_space:
                boot_space = self.seats_doors(boot_space)
                boot_space = str(boot_space)

        drivetrain = None
        if 'Drive wheel ' in filtered_headers:
            drivetrain_index = filtered_headers.index('Drive wheel ') - 3
            drivetrain = filtered_desc[drivetrain_index]

        gearbox = None
        if 'Number of gears and type of gearbox ' in filtered_headers:
            gearbox_index = filtered_headers.index('Number of gears and type of gearbox ') - 3
            gearbox = filtered_desc[gearbox_index]

        if engine_type == 'BEV (Electric Vehicle) ':
            if 'Average Energy consumption (WLTP) ' in filtered_headers:
                fuel_combined_index = filtered_headers.index('Average Energy consumption (WLTP) ') - 3
                fuel_consumption = filtered_desc[fuel_combined_index]
                if "-" in fuel_consumption:
                    fuel_consumption = fuel_consumption.replace(" kWh/100 km", "")
                    parts = fuel_consumption.split("-")
                    num1 = float(parts[0])
                    num2 = float(parts[1])
                    average = (num1 + num2) / 2
                    fuel_consumption = str(average)
                else:
                    fuel_consumption = fuel_consumption.replace(" kWh/100 km", "")
            if 'Average Energy consumption (NEDC) ' in filtered_headers:
                fuel_combined_index = filtered_headers.index('Average Energy consumption (NEDC) ') - 3
                fuel_consumption = filtered_desc[fuel_combined_index]
                if "-" in fuel_consumption:
                    fuel_consumption = fuel_consumption.replace(" kWh/100 km", "")
                    parts = fuel_consumption.split("-")
                    num1 = float(parts[0])
                    num2 = float(parts[1])
                    average = (num1 + num2) / 2
                    fuel_consumption = str(average)
                else:
                    fuel_consumption = fuel_consumption.replace(" kWh/100 km", "")
            if 'Average Energy consumption ' in filtered_headers:
                fuel_combined_index = filtered_headers.index('Average Energy consumption ') - 3
                fuel_consumption = filtered_desc[fuel_combined_index]
                if "-" in fuel_consumption:
                    fuel_consumption = fuel_consumption.replace(" kWh/100 km", "")
                    parts = fuel_consumption.split("-")
                    num1 = float(parts[0])
                    num2 = float(parts[1])
                    average = (num1 + num2) / 2
                    fuel_consumption = str(average)
                else:
                    fuel_consumption = fuel_consumption.replace(" kWh/100 km", "")
            if 'All-electric range (WLTP)' in filtered_headers:
                gearbox_index = filtered_headers.index('All-electric range (WLTP)') - 3
                gearbox = filtered_desc[gearbox_index]
                if "-" in gearbox:
                    gearbox = self.parse_weight(gearbox)

            if 'All-electric range (NEDC)' in filtered_headers:
                gearbox_index = filtered_headers.index('All-electric range (NEDC)') - 3
                gearbox = filtered_desc[gearbox_index]
                if "-" in gearbox:
                    gearbox = self.parse_weight(gearbox)
 
            if 'All-electric range ' in filtered_headers:
                gearbox_index = filtered_headers.index('All-electric range ') - 3
                gearbox = filtered_desc[gearbox_index]
                if "-" in gearbox:
                    gearbox = self.parse_weight(gearbox)

            if 'System power ' in filtered_headers:
                power_index = filtered_headers.index('System power ') - 3
                power = filtered_desc[power_index]
            if 'System torque ' in filtered_headers:
                torque_index = filtered_headers.index('System torque ') - 3
                torque = filtered_desc[torque_index]

        else:
            if 'Fuel consumption at Medium speed (WLTP) ' in filtered_headers:
                fuel_combined_index = filtered_headers.index('Fuel consumption at Medium speed (WLTP) ') - 3
                fuel_consumption = filtered_desc[fuel_combined_index]
                if "-" in fuel_consumption:
                    fuel_consumption = fuel_consumption.replace(" l/100 km", "")
                    parts = fuel_consumption.split("-")
                    num1 = float(parts[0])
                    num2 = float(parts[1])
                    average = float((num1 + num2) / 2)
                    fuel_consumption = str(average)
                else:
                    fuel_consumption = fuel_consumption.replace(" l/100 km", "")
            if 'Fuel consumption (economy) - combined (NEDC)' in filtered_headers:
                fuel_combined_index = filtered_headers.index('Fuel consumption (economy) - combined (NEDC)') - 3
                fuel_consumption = filtered_desc[fuel_combined_index]
                if "-" in fuel_consumption:
                    fuel_consumption = fuel_consumption.replace(" l/100 km", "")
                    parts = fuel_consumption.split("-")
                    num1 = float(parts[0])
                    num2 = float(parts[1])
                    average = float((num1 + num2) / 2)
                    fuel_consumption = str(average)
                else:
                    fuel_consumption = fuel_consumption.replace(" l/100 km", "")
            if 'Fuel consumption (economy) - combined' in filtered_headers:
                fuel_combined_index = filtered_headers.index('Fuel consumption (economy) - combined') - 3
                fuel_consumption = filtered_desc[fuel_combined_index]
                if "-" in fuel_consumption:
                    fuel_consumption = fuel_consumption.replace(" l/100 km", "")
                    parts = fuel_consumption.split("-")
                    num1 = float(parts[0])
                    num2 = float(parts[1])
                    average = float((num1 + num2) / 2)
                    fuel_consumption = str(average)
                else:
                    fuel_consumption = fuel_consumption.replace(" l/100 km", "")
            if 'Fuel consumption (economy) - combined (NEDC, WLTP equivalent)' in filtered_headers:
                fuel_combined_index = filtered_headers.index('Fuel consumption (economy) - combined (NEDC, WLTP equivalent)') - 3
                fuel_consumption = filtered_desc[fuel_combined_index]
                if "-" in fuel_consumption:
                    fuel_consumption = fuel_consumption.replace(" l/100 km", "")
                    parts = fuel_consumption.split("-")
                    num1 = float(parts[0])
                    num2 = float(parts[1])
                    average = float((num1 + num2) / 2)
                    fuel_consumption = str(average)
                else:
                    fuel_consumption = fuel_consumption.replace(" l/100 km", "")
            if 'Combined fuel consumption (WLTP) ' in filtered_headers:
                fuel_combined_index = filtered_headers.index('Combined fuel consumption (WLTP) ') - 3
                fuel_consumption = filtered_desc[fuel_combined_index]
                if "-" in fuel_consumption:
                    fuel_consumption = fuel_consumption.replace(" l/100 km", "")
                    parts = fuel_consumption.split("-")
                    num1 = float(parts[0])
                    num2 = float(parts[1])
                    average = float((num1 + num2) / 2)
                    fuel_consumption = str(average)
                else:
                    fuel_consumption = fuel_consumption.replace(" l/100 km", "")
            if 'Fuel consumption (economy) - combined (EPA)' in filtered_headers:
                fuel_combined_index = filtered_headers.index('Fuel consumption (economy) - combined (EPA)') - 3
                fuel_consumption = filtered_desc[fuel_combined_index]
                if "-" in fuel_consumption:
                    fuel_consumption = fuel_consumption.replace(" l/100 km", "")
                    parts = fuel_consumption.split("-")
                    num1 = float(parts[0])
                    num2 = float(parts[1])
                    average = float((num1 + num2) / 2)
                    fuel_consumption = str(average)
                else:
                    fuel_consumption = fuel_consumption.replace(" l/100 km", "")
            if 'Fuel consumption (economy) - urban ' in filtered_headers and 'Fuel consumption (economy) - extra urban' in filtered_headers:
                urban_index = filtered_headers.index('Fuel consumption (economy) - urban ') - 3
                urban = filtered_desc[urban_index]
                if "-" in urban:
                    urban = urban.replace(" l/100 km", "")
                    parts = urban.split("-")
                    num1 = float(parts[0])
                    num2 = float(parts[1])
                    average = float((num1 + num2) / 2)
                    urban = average
                else:
                    urban = urban.replace(" l/100 km", "")
                extra_index = filtered_headers.index('Fuel consumption (economy) - extra urban') - 3
                extra = filtered_desc[extra_index]
                if "-" in extra:
                    extra = extra.replace(" l/100 km", "")
                    parts = extra.split("-")
                    num1 = float(parts[0])
                    num2 = float(parts[1])
                    average = float((num1 + num2) / 2)
                    extra = average
                else:
                    extra = extra.replace(" l/100 km", "")
                combined = (float(urban) + float(extra)) / 2
                fuel_consumption = round(combined, 1)
                fuel_consumption = str(fuel_consumption)
            if 'Fuel consumption (economy) - urban (EPA) ' in filtered_headers and 'Fuel consumption (economy) - extra urban (EPA)' in filtered_headers:
                urban_index = filtered_headers.index('Fuel consumption (economy) - urban (EPA) ') - 3
                urban = filtered_desc[urban_index]
                if "-" in urban:
                    urban = urban.replace(" l/100 km", "")
                    parts = urban.split("-")
                    num1 = float(parts[0])
                    num2 = float(parts[1])
                    average = float((num1 + num2) / 2)
                    urban = average
                else:
                    urban = urban.replace(" l/100 km", "")
                extra_index = filtered_headers.index('Fuel consumption (economy) - extra urban (EPA)') - 3
                extra = filtered_desc[extra_index]
                if "-" in extra:
                    extra = extra.replace(" l/100 km", "")
                    parts = extra.split("-")
                    num1 = float(parts[0])
                    num2 = float(parts[1])
                    average = float((num1 + num2) / 2)
                    extra = average
                else:
                    extra = extra.replace(" l/100 km", "")
                combined = (float(urban) + float(extra)) / 2
                fuel_consumption = round(combined, 1)
                fuel_consumption = str(fuel_consumption)
            if 'Fuel consumption (economy) - urban (NEDC) ' in filtered_headers and 'Fuel consumption (economy) - extra urban (NEDC)' in filtered_headers:
                urban_index = filtered_headers.index('Fuel consumption (economy) - urban (NEDC) ') - 3
                urban = filtered_desc[urban_index]
                if "-" in urban:
                    urban = urban.replace(" l/100 km", "")
                    parts = urban.split("-")
                    num1 = float(parts[0])
                    num2 = float(parts[1])
                    average = float((num1 + num2) / 2)
                    urban = average
                else:
                    urban = urban.replace(" l/100 km", "")
                extra_index = filtered_headers.index('Fuel consumption (economy) - extra urban (NEDC)') - 3
                extra = filtered_desc[extra_index]
                if "-" in extra:
                    extra = extra.replace(" l/100 km", "")
                    parts = extra.split("-")
                    num1 = float(parts[0])
                    num2 = float(parts[1])
                    average = float((num1 + num2) / 2)
                    extra = average
                else:
                    extra = extra.replace(" l/100 km", "")
                combined = (float(urban) + float(extra)) / 2
                fuel_consumption = round(combined, 1)
                fuel_consumption = str(fuel_consumption)
        
        Speed = 0
        Space = 0
        OffroadTowing = 0
        Comfort = 0
        Maintenance = 0
        OK = 0

        if generation is not None:
            age = int(self.remove_after_dash(generation))
        if kerb_weight is not None:
            if 'kg' in kerb_weight:
                kerb_weight = kerb_weight.replace(" kg", "").strip()
                kerb_weight = int(kerb_weight)
            else:
                kerb_weight = int(kerb_weight)
        if torque is not None:
            torque = self.remove_after_at(torque).replace(" Nm", "").strip()
            torque = int(torque)
        if fuel_consumption is not None:
            fuel_consumption = round(float(fuel_consumption)+(5*float(fuel_consumption)/10),1)
        if power is not None:
            power = self.remove_after_at(power).replace(" Hp", "").strip()
            power = int(power)
        if boot_space is not None:
            boot_space = boot_space.replace("l","").strip()
            boot_space = int(boot_space)

        LED = "no"
        Safety_assists = "no"
        Infotainment = "no"
        Parking_cameras = "no"
        Parking_sensor = "no"
        Air_suspension = "no"
        Digital_driver_display = "no"
        Carplay_Auto = "no"
        Ambient_lightning = "no"

        #Comfort points
        OK = 0
        if brand_name is not None:
            OK += 1
            if brand_name == "Rolls-Royce":
                Comfort += 310
            if brand_name == "Bentley":
                Comfort += 280
            if brand_name == "Mercedes-Benz":
                Comfort += 270
            if brand_name == "Bugatti":
                Comfort += 264
            if brand_name == "BMW":
                Comfort += 260
            if brand_name == "Ferrari":
                Comfort += 256
            if brand_name == "Audi":
                Comfort += 252
            if brand_name == "Lamborghini":
                Comfort += 248
            if brand_name == "Alpina":
                Comfort += 244
            if brand_name == "Porsche":
                Comfort += 240
            if brand_name == "Lexus":
                Comfort += 236
            if brand_name == "Genesis":
                Comfort += 232
            if brand_name == "Cadillac":
                Comfort += 228
            if brand_name == "Lincoln":
                Comfort += 224
            if brand_name == "Land Rover":
                Comfort += 220
            if brand_name == "Maserati":
                Comfort += 216
            if brand_name == "Aston Martin":
                Comfort += 212
            if brand_name == "Jaguar":
                Comfort += 208
            if brand_name == "Volvo":
                Comfort += 204
            if brand_name == "Volkswagen":
                Comfort += 200
            if brand_name == "Pagani":
                Comfort += 196
            if brand_name == "McLaren":
                Comfort += 192
            if brand_name == "Koenigsegg":
                Comfort += 188
            if brand_name == "Cupra":
                Comfort += 184
            if brand_name == "Lotus":
                Comfort += 180
            if brand_name == "Ford":
                Comfort += 176
            if brand_name == "Peugeot":
                Comfort += 172
            if brand_name == "DS":
                Comfort += 168
            if brand_name == "Lancia":
                Comfort += 164
            if brand_name == "Alfa Romeo":
                Comfort += 160
            if brand_name == "BYD":
                Comfort += 156
            if brand_name == "Infiniti":
                Comfort += 152
            if brand_name == "Nissan":
                Comfort += 148
            if brand_name == "Seat":
                Comfort += 144
            if brand_name == "Skoda":
                Comfort += 140
            if brand_name == "Mini":
                Comfort += 136
            if brand_name == "Tesla":
                Comfort += 132
            if brand_name == "Kia":
                Comfort += 128
            if brand_name == "Hyundai":
                Comfort += 124
            if brand_name == "GMC":
                Comfort += 120
            if brand_name == "Dodge":
                Comfort += 116
            if brand_name == "Chevrolet":
                Comfort += 112
            if brand_name == "Chrysler":
                Comfort += 108
            if brand_name == "Acura":
                Comfort += 104
            if brand_name == "Honda":
                Comfort += 100
            if brand_name == "Saab":
                Comfort += 96
            if brand_name == "Toyota":
                Comfort += 92
            if brand_name == "NIO":
                Comfort += 88
            if brand_name == "Haval":
                Comfort += 84
            if brand_name == "Renault":
                Comfort += 80
            if brand_name == "MG":
                Comfort += 76
            if brand_name == "Subaru":
                Comfort += 72
            if brand_name == "Mitsubishi":
                Comfort += 68
            if brand_name == "RAM":
                Comfort += 64
            if brand_name == "Citroen":
                Comfort += 60
            if brand_name == "Mazda":
                Comfort += 56
            if brand_name == "Rover":
                Comfort += 52
            if brand_name == "Suzuki":
                Comfort += 48
            if brand_name == "Great Wall":
                Comfort += 44
            if brand_name == "Jeep":
                Comfort += 40
            if brand_name == "Opel":
                Comfort += 36
            if brand_name == "Vauxhall":
                Comfort += 32
            if brand_name == "Fiat":
                Comfort += 28
            if brand_name == "Smart":
                Comfort += 24
            if brand_name == "Hummer":
                Comfort += 20
            if brand_name == "Dacia":
                Comfort += 16
            if brand_name == "Daihatsu":
                Comfort += 12
            if brand_name == "Daewoo":
                Comfort += 8
            if brand_name == "Lada":
                Comfort += 4
        if body_type is not None:
            OK += 1
            if body_type == "Grand Tourer ":
                Comfort += 188
            if body_type == "Coupe ":
                Comfort += 184
            if body_type == "Coupe, Fastback ":
                Comfort += 180
            if body_type == "Sedan ":
                Comfort += 176
            if body_type == "Sedan, Fastback ":
                Comfort += 172
            if body_type == "Fastback ":
                Comfort += 168
            if body_type == "Liftback ":
                Comfort += 164
            if body_type == "SUV ":
                Comfort += 160
            if body_type == "SAV ":
                Comfort += 156
            if body_type == "SAC ":
                Comfort += 152
            if body_type == "Targa ":
                Comfort += 148
            if body_type == "Roadster ":
                Comfort += 144
            if body_type == "Station wagon (estate) ":
                Comfort += 140
            if body_type == "Cabriolet ":
                Comfort += 136
            if body_type == "Cabriolet, Coupe ":
                Comfort += 132
            if body_type == "Coupe - Cabriolet ":
                Comfort += 128
            if body_type == "Coupe - Cabriolet, Roadster ":
                Comfort += 124
            if body_type == "Coupe, SUV ":
                Comfort += 120
            if body_type == "Coupe, SUV, Crossover ":
                Comfort += 116
            if body_type == "Coupe, CUV ":
                Comfort += 112
            if body_type == "CUV":
                Comfort += 110
            if body_type == "Coupe, Liftback ":
                Comfort += 108
            if body_type == "Coupe, Hatchback ":
                Comfort += 104
            if body_type == "Station wagon (estate), Crossover ":
                Comfort += 100
            if body_type == "Hatchback, Fastback ":
                Comfort += 96
            if body_type == "Hatchback, Crossover ":
                Comfort += 92
            if body_type == "Hatchback ":
                Comfort += 88
            if body_type == "Crossover ":
                Comfort += 84
            if body_type == "Crossover, Fastback ":
                Comfort += 80
            if body_type == "Minivan ":
                Comfort += 76
            if body_type == "Minivan, MPV ":
                Comfort += 72
            if body_type == "Minivan, Crossover ":
                Comfort += 68
            if body_type == "MPV ":
                Comfort += 64
            if body_type == "SUV, MPV ":
                Comfort += 60
            if body_type == "SUV, Crossover ":
                Comfort += 56
            if body_type == "Cabriolet, SUV ":
                Comfort += 52
            if body_type == "Cabriolet, Hatchback ":
                Comfort += 48
            if body_type == "Pick-up ":
                Comfort += 44
            if body_type == "Off-road vehicle, Coupe ":
                Comfort += 40
            if body_type == "Off-road vehicle ":
                Comfort += 36
            if body_type == "Off-road vehicle, SUV ":
                Comfort += 32
            if body_type == "Off-road vehicle, Cabriolet ":
                Comfort += 28
            if body_type == "Off-road vehicle, Cabriolet, SUV ":
                Comfort += 24
            if body_type == "Off-road vehicle, Pick-up ":
                Comfort += 20
            if body_type == "Off-road vehicle, Station wagon (estate) ":
                Comfort += 16
            if body_type == "Station wagon (estate), MPV ":
                Comfort += 12
            if body_type == "Van ":
                Comfort += 8
            if body_type == "Quadricycle ":
                Comfort += 4
        if age is not None:
            OK += 1
            Comfort = Comfort + (age-1928)*4
        if kerb_weight is not None:
            OK += 1
            Comfort = Comfort + int(kerb_weight/10)
        if engine_type == "BEV (Electric Vehicle) ":
            OK += 1
            Comfort += 200
        else:
            if gearbox is not None:
                OK += 1
                if "automatic" in gearbox:
                    Comfort += 200
                if "manual" in gearbox:
                    Comfort += 100
        if OK is not 5:
            Comfort = 0

        
        #OffroadTowing points
        OK = 0
        if torque is not None:
            OK += 1
            OffroadTowing = OffroadTowing + int(torque/10)
        if drivetrain is not None:
            OK += 1
            if "All wheel drive" in drivetrain:
                OffroadTowing = OffroadTowing + 100
            if "Rear wheel drive" in drivetrain:
                OffroadTowing = OffroadTowing + 30
            if "Front wheel drive" in drivetrain:
                OffroadTowing = OffroadTowing + 50
        if fuel_type is not None:
            OK += 1
            if "Diesel" in fuel_type:
                OffroadTowing = OffroadTowing + 60
            if "Petrol" in fuel_type:
                OffroadTowing = OffroadTowing + 40
            if "Electricity" in fuel_type:
                OffroadTowing = OffroadTowing + 10
        if body_type is not None:
            OK += 1
            if body_type == "Off-road vehicle, Pick-up ":
                OffroadTowing += 426
            if body_type == "Off-road vehicle ":
                OffroadTowing += 418
            if body_type == "Off-road vehicle, SUV ":
                OffroadTowing += 410
            if body_type == "Off-road vehicle, Station wagon (estate) ":
                OffroadTowing += 402
            if body_type == "Pick-up ":
                OffroadTowing += 398
            if body_type == "Off-road vehicle, Cabriolet ":
                OffroadTowing += 386
            if body_type == "Off-road vehicle, Cabriolet, SUV ":
                OffroadTowing += 378
            if body_type == "SUV ":
                OffroadTowing += 350
            if body_type == "Off-road vehicle, Coupe ":
                OffroadTowing += 312
            if body_type == "SAV ":
                OffroadTowing += 304
            if body_type == "SUV, MPV ":
                OffroadTowing += 296
            if body_type == "Cabriolet, SUV ":
                OffroadTowing += 288
            if body_type == "SAC ":
                OffroadTowing += 280
            if body_type == "Coupe, SUV ":
                OffroadTowing += 272
            if body_type == "SUV, Crossover ":
                OffroadTowing += 264
            if body_type == "Coupe, SUV, Crossover ":
                OffroadTowing += 256
            if body_type == "Coupe, CUV ":
                OffroadTowing += 248
            if body_type == "CUV":
                OffroadTowing += 244
            if body_type == "Crossover ":
                OffroadTowing += 240
            if body_type == "Crossover, Fastback ":
                OffroadTowing += 232
            if body_type == "Hatchback, Crossover ":
                OffroadTowing += 224
            if body_type == "Hatchback ":
                OffroadTowing += 216
            if body_type == "Hatchback, Fastback ":
                OffroadTowing += 208
            if body_type == "Sedan ":
                OffroadTowing += 200
            if body_type == "Sedan, Fastback ":
                OffroadTowing += 192
            if body_type == "Liftback ":
                OffroadTowing += 184
            if body_type == "Fastback ":
                OffroadTowing += 176
            if body_type == "Grand Tourer ":
                OffroadTowing += 168
            if body_type == "Station wagon (estate), Crossover ":
                OffroadTowing += 160
            if body_type == "Station wagon (estate) ":
                OffroadTowing += 152
            if body_type == "Station wagon (estate), MPV ":
                OffroadTowing += 144
            if body_type == "MPV ":
                OffroadTowing += 136
            if body_type == "Minivan, MPV ":
                OffroadTowing += 128
            if body_type == "Minivan, Crossover ":
                OffroadTowing += 120
            if body_type == "Minivan ":
                OffroadTowing += 112
            if body_type == "Van ":
                OffroadTowing += 104
            if body_type == "Cabriolet, Hatchback ":
                OffroadTowing += 96
            if body_type == "Coupe, Hatchback ":
                OffroadTowing += 88
            if body_type == "Coupe, Liftback ":
                OffroadTowing += 80
            if body_type == "Cabriolet, Coupe ":
                OffroadTowing += 72
            if body_type == "Coupe - Cabriolet ":
                OffroadTowing += 64
            if body_type == "Coupe - Cabriolet, Roadster ":
                OffroadTowing += 56
            if body_type == "Targa ":
                OffroadTowing += 48
            if body_type == "Coupe, Fastback ":
                OffroadTowing += 40
            if body_type == "Cabriolet ":
                OffroadTowing += 32
            if body_type == "Coupe ":
                OffroadTowing += 24
            if body_type == "Roadster ":
                OffroadTowing += 16
            if body_type == "Quadricycle ":
                OffroadTowing += 8
            if OK is not 4:
                OffroadTowing = 0


        #Maintenance points
        OK = 0
        if fuel_consumption is not None:
            OK += 1
            if "Electricity" in fuel_type:
                Maintenance = Maintenance + int(371-(fuel_consumption*10))
            if "Diesel" in fuel_type:
                Maintenance = Maintenance + int(309-(fuel_consumption*10))
            if "Petrol" in fuel_type:
                Maintenance = Maintenance + int(309-(fuel_consumption*10))
        if fuel_type is not None:
            OK += 1
            if "Electricity" in fuel_type:
                Maintenance = Maintenance + 200
            if "Petrol" in fuel_type:
                Maintenance = Maintenance + 100
            if "Diesel" in fuel_type:
                Maintenance = Maintenance + 90
        if OK is not 2:
            Maintenance = 0

        #Speed points
        OK = 0
        if body_type is not None:
            OK += 1
            if body_type == "Coupe ":
                Speed = Speed + 300
            elif body_type == "Roadster ":
                Speed = Speed + 300
            elif body_type == "Targa ":
                Speed = Speed + 300
            elif body_type == "Coupe, Liftback ":
                Speed = Speed + 294
            elif body_type == "Coupe, Fastback ":
                Speed = Speed + 291
            elif body_type == "Cabriolet ":
                Speed = Speed + 285
            elif body_type == "Coupe - Cabriolet, Roadster ":
                Speed = Speed + 285
            elif body_type == "Coupe - Cabriolet ":
                Speed = Speed + 285
            elif body_type == "Cabriolet, Coupe ":
                Speed = Speed + 285
            elif body_type == "Off-road vehicle, Coupe ":
                Speed = Speed + 270
            elif body_type == "Coupe, Hatchback ":
                Speed = Speed + 255
            elif body_type == "Cabriolet, Hatchback ":
                Speed = Speed + 252
            elif body_type == "Hatchback ":
                Speed = Speed + 240
            elif body_type == "Hatchback, Fastback ":
                Speed = Speed + 234
            elif body_type == "Grand Tourer ":
                Speed = Speed + 225
            elif body_type == "Liftback ":
                Speed = Speed + 222
            elif body_type == "Fastback ":
                Speed = Speed + 219
            elif body_type == "Sedan, Fastback ":
                Speed = Speed + 210
            elif body_type == "Sedan ":
                Speed = Speed + 207
            elif body_type == "Hatchback, Crossover ":
                Speed = Speed + 201
            elif body_type == "Coupe, SUV, Crossover ":
                Speed = Speed + 195
            elif body_type == "Station wagon (estate), Crossover ":
                Speed = Speed + 186
            elif body_type == "Station wagon (estate) ":
                Speed = Speed + 180
            elif body_type == "Coupe, CUV ":
                Speed = Speed + 174
            elif body_type == "CUV":
                Speed = Speed + 172
            elif body_type == "Crossover, Fastback ":
                Speed = Speed + 171
            elif body_type == "Crossover ":
                Speed = Speed + 165
            elif body_type == "MPV ":
                Speed = Speed + 165
            elif body_type == "Station wagon (estate), MPV ":
                Speed = Speed + 159
            elif body_type == "SUV, Crossover ":
                Speed = Speed + 153
            elif body_type == "Coupe, SUV ":
                Speed = Speed + 150
            elif body_type == "Cabriolet, SUV ":
                Speed = Speed + 141
            elif body_type == "Off-road vehicle, Cabriolet ":
                Speed = Speed + 135
            elif body_type == "SAV ":
                Speed = Speed + 129
            elif body_type == "SAC ":
                Speed = Speed + 129
            elif body_type == "SUV ":
                Speed = Speed + 129
            elif body_type == "SUV, MPV ":
                Speed = Speed + 120
            elif body_type == "Minivan, Crossover ":
                Speed = Speed + 105
            elif body_type == "Minivan ":
                Speed = Speed + 99
            elif body_type == "Minivan, MPV ":
                Speed = Speed + 90
            elif body_type == "Pick-up ":
                Speed = Speed + 78
            elif body_type == "Off-road vehicle, Cabriolet, SUV ":
                Speed = Speed + 75
            elif body_type == "Off-road vehicle, SUV ":
                Speed = Speed + 72
            elif body_type == "Off-road vehicle, Pick-up ":
                Speed = Speed + 60
            elif body_type == "Off-road vehicle ":
                Speed = Speed + 60
            elif body_type == "Off-road vehicle, Station wagon (estate) ":
                Speed = Speed + 51
            elif body_type == "Van ":
                Speed = Speed + 39
            elif body_type == "Quadricycle ":
                Speed = Speed + 15
        if power is not None:
            OK += 1
            Speed = Speed + int(power/10)*6
        if kerb_weight is not None:
            OK += 1
            Speed = Speed + int((4037-kerb_weight)/10)
        if torque is not None:
            OK += 1
            Speed = Speed + int(torque/10)*2
        if engine_type == "BEV (Electric Vehicle) ":
            OK += 1
            Speed += 50
        else:
            if gearbox is not None:
                OK += 1
                if "automatic" in gearbox:
                    Speed += 50
                if "manual" in gearbox:
                    Speed += 25
        if OK is not 5:
            Speed = 0

        #Space points

        OK = 0
        if body_type is not None:
            OK += 1
            if body_type == "SUV ":
                Space = Space + 200
            elif body_type == "SUV, MPV ":
                Space = Space + 196
            elif body_type == "SAV ":
                Space = Space + 190
            elif body_type == "SAC ":
                Space = Space + 180
            elif body_type == "Off-road vehicle, Station wagon (estate) ":
                Space = Space + 174
            elif body_type == "Pick-up ":
                Space = Space + 170
            elif body_type == "Off-road vehicle, Pick-up ":
                Space = Space + 170
            elif body_type == "Sedan ":
                Space = Space + 160
            elif body_type == "Sedan, Fastback ":
                Space = Space + 158
            elif body_type == "Grand Tourer ":
                Space = Space + 156
            elif body_type == "Fastback ":
                Space = Space + 154
            elif body_type == "Liftback ":
                Space = Space + 154
            elif body_type == "Station wagon (estate) ":
                Space = Space + 152
            elif body_type == "Coupe, SUV ":
                Space = Space + 148
            elif body_type == "Off-road vehicle, SUV ":
                Space = Space + 146
            elif body_type == "Cabriolet, SUV ":
                Space = Space + 140
            elif body_type == "Off-road vehicle, Cabriolet, SUV ":
                Space = Space + 140
            elif body_type == "Off-road vehicle ":
                Space = Space + 130
            elif body_type == "Off-road vehicle, Cabriolet ":
                Space = Space + 128
            elif body_type == "Station wagon (estate), MPV ":
                Space = Space + 120
            elif body_type == "Station wagon (estate), Crossover ":
                Space = Space + 118
            elif body_type == "SUV, Crossover ":
                Space = Space + 114
            elif body_type == "Coupe, SUV, Crossover ":
                Space = Space + 112
            elif body_type == "Coupe, CUV ":
                Space = Space + 112
            elif body_type == "CUV":
                Space = Space + 111
            elif body_type == "Minivan ":
                Space = Space + 110
            elif body_type == "Minivan, Crossover ":
                Space = Space + 108
            elif body_type == "Minivan, MPV ":
                Space = Space + 106
            elif body_type == "Van ":
                Space = Space + 104
            elif body_type == "MPV ":
                Space = Space + 102
            elif body_type == "Crossover, Fastback ":
                Space = Space + 100
            elif body_type == "Crossover ":
                Space = Space + 100
            elif body_type == "Coupe, Liftback ":
                Space = Space + 94
            elif body_type == "Cabriolet, Coupe ":
                Space = Space + 92
            elif body_type == "Hatchback, Crossover ":
                Space = Space + 86
            elif body_type == "Hatchback, Fastback ":
                Space = Space + 84
            elif body_type == "Hatchback ":
                Space = Space + 80
            elif body_type == "Cabriolet, Hatchback ":
                Space = Space + 78
            elif body_type == "Coupe, Hatchback ":
                Space = Space + 78
            elif body_type == "Coupe - Cabriolet ":
                Space = Space + 70
            elif body_type == "Coupe - Cabriolet, Roadster ":
                Space = Space + 70
            elif body_type == "Off-road vehicle, Coupe ":
                Space = Space + 60
            elif body_type == "Targa ":
                Space = Space + 50
            elif body_type == "Coupe, Fastback ":
                Space = Space + 50
            elif body_type == "Cabriolet ":
                Space = Space + 48
            elif body_type == "Coupe ":
                Space = Space + 46
            elif body_type == "Roadster ":
                Space = Space + 44
            elif body_type == "Quadricycle ":
                Space = Space + 10
        if seats is not None:
            OK += 1
            if seats == "9 ":
                Space = Space + 45
            if seats == "8 ":
                Space = Space + 40
            if seats == "7 ":
                Space = Space + 35
            if seats == "6 ":
                Space = Space + 30
            if seats == "5 ":
                Space = Space + 25
            if seats == "4 ":
                Space = Space + 20
            if seats == "3 ":
                Space = Space + 15
            if seats == "2 ":
                Space = Space + 10
            if seats == "1 ":
                Space = Space + 5
        if doors is not None:
            OK += 1
            if doors == "5 ":
                Space = Space + 25
            if doors == "4 ":
                Space = Space + 20
            if doors == "3 ":
                Space = Space + 15
            if doors == "2 ":
                Space = Space + 10
            if doors == "1 ":
                Space = Space + 5
        if boot_space is not None:
            OK += 1
            Space = Space + int(boot_space/10)
        else:
            if body_type is not None:
                OK += 1
                if body_type == "Van ":
                    Space += 100
                elif body_type == "Minivan ":
                    Space += 80
                elif body_type == "Pick-up ":
                    Space += 80
                elif body_type == "Off-road vehicle, Pick-up ":
                    Space += 70
                elif body_type == "Minivan, MPV ":
                    Space += 69
                elif body_type == "Minivan, Crossover ":
                    Space += 68
                elif body_type == "SUV, MPV ":
                    Space += 65
                elif body_type == "Off-road vehicle, Station wagon (estate) ":
                    Space += 65
                elif body_type == "Off-road vehicle, SUV ":
                    Space += 60
                elif body_type == "Off-road vehicle, Cabriolet, SUV ":
                    Space += 60
                elif body_type == "Off-road vehicle ":
                    Space += 60
                elif body_type == "MPV ":
                    Space += 55
                elif body_type == "Station wagon (estate) ":
                    Space += 55
                elif body_type == "SUV ":
                    Space += 55
                elif body_type == "SAC ":
                    Space += 55
                elif body_type == "SAV ":
                    Space += 55
                elif body_type == "Station wagon (estate), MPV ":
                    Space += 50
                elif body_type == "Station wagon (estate), Crossover ":
                    Space += 50
                elif body_type == "Liftback ":
                    Space += 50
                elif body_type == "Fastback ":
                    Space += 50
                elif body_type == "Grand Tourer ":
                    Space += 50
                elif body_type == "Sedan, Fastback ":
                    Space += 50
                elif body_type == "Sedan ":
                    Space += 50
                elif body_type == "Coupe, SUV ":
                    Space += 50
                elif body_type == "Off-road vehicle, Cabriolet ":
                    Space += 45
                elif body_type == "Cabriolet, SUV ":
                    Space += 40
                elif body_type == "SUV, Crossover ":
                    Space += 40
                elif body_type == "Coupe, SUV, Crossover ":
                    Space += 40
                elif body_type == "Coupe, CUV ":
                    Space += 40
                elif body_type == "CUV":
                    Space += 40
                elif body_type == "Crossover, Fastback ":
                    Space += 35
                elif body_type == "Crossover ":
                    Space += 35
                elif body_type == "Hatchback, Crossover ":
                    Space += 35
                elif body_type == "Hatchback, Fastback ":
                    Space += 30
                elif body_type == "Hatchback ":
                    Space += 30
                elif body_type == "Cabriolet, Hatchback ":
                    Space += 25
                elif body_type == "Coupe, Hatchback ":
                    Space += 25
                elif body_type == "Coupe, Liftback ":
                    Space += 20
                elif body_type == "Off-road vehicle, Coupe ":
                    Space += 15
                elif body_type == "Cabriolet, Coupe ":
                    Space += 15
                elif body_type == "Coupe - Cabriolet ":
                    Space += 10
                elif body_type == "Coupe - Cabriolet, Roadster ":
                    Space += 10
                elif body_type == "Targa ":
                    Space += 10
                elif body_type == "Coupe, Fastback ":
                    Space += 10
                elif body_type == "Cabriolet ":
                    Space += 10
                elif body_type == "Coupe ":
                    Space += 10
                elif body_type == "Roadster ":
                    Space += 10
                elif body_type == "Quadricycle ":
                    Space += 5
        if OK is not 4:
            Space = 0

        if brand_name == "Acura":
            if age >= 2013:
                LED = "yes"
            if age >= 2011:
                Safety_assists = "yes"
            if age >= 2003:
                Parking_sensor = "yes"
            if age >= 2003:
                Infotainment = "yes"
            if age >= 2003:
                Parking_cameras = "yes"
            if age >= 2022:
                Ambient_lightning = "yes"
            if age >= 2017:
                Carplay_Auto = "yes"
            if age >= 2022:
                Digital_driver_display = "yes"

        if brand_name == "Alfa Romeo":
            if age >= 2014:
                LED = "yes"
            if age >= 2017:
                Safety_assists = "yes"
            if age >= 2005:
                Parking_sensor = "yes"
            if age >= 2005:
                Infotainment = "yes"
            if age >= 2011:
                Parking_cameras = "yes"
            if age >= 2022:
                Ambient_lightning = "yes"
            if age >= 2018:
                Carplay_Auto = "yes"
            if age >= 2024:
                Digital_driver_display = "yes"

        if brand_name == "Alpina":
            if age >= 2011:
                LED = "yes"
            if age >= 2014:
                Safety_assists = "yes"
            if age >= 2008:
                Parking_sensor = "yes"
            if age >= 2003:
                Infotainment = "yes"
            if age >= 2011:
                Parking_cameras = "yes"
            if age >= 2017:
                Ambient_lightning = "yes"
            if age >= 2018:
                Carplay_Auto = "yes"
            if age >= 2018:
                Digital_driver_display = "yes"

        if brand_name == "Aston Martin":
            if age >= 2015:
                LED = "yes"
            if age >= 2016:
                Safety_assists = "yes"
            if age >= 2010:
                Parking_sensor = "yes"
            if age >= 2016:
                Infotainment = "yes"
            if age >= 2016:
                Parking_cameras = "yes"
            if age >= 2020:
                Ambient_lightning = "yes"
            if age >= 2020:
                Carplay_Auto = "yes"
            if age >= 2019:
                Digital_driver_display = "yes"
            
        if brand_name == "Audi":
            if age >= 2008:
                LED = "yes"
            if age >= 2012:
                Safety_assists = "yes"
            if age >= 2003:
                Parking_sensor = "yes"
            if age >= 2004:
                Infotainment = "yes"
            if age >= 2008:
                Parking_cameras = "yes"
            if age >= 2018:
                Ambient_lightning = "yes"
            if age >= 2016:
                Carplay_Auto = "yes"
            if age >= 2016:
                Digital_driver_display = "yes"

        if brand_name == "Bentley":
            if age >= 2011:
                LED = "yes"
            if age >= 2013:
                Safety_assists = "yes"
            if age >= 2003:
                Parking_sensor = "yes"
            if age >= 2003:
                Infotainment = "yes"
            if age >= 2010:
                Parking_cameras = "yes"
            if age >= 2016:
                Ambient_lightning = "yes"
            if age >= 2017:
                Carplay_Auto = "yes"
            if age >= 2018:
                Digital_driver_display = "yes"
            if age >= 2003:
                Air_suspension = "yes"

        if brand_name == "BMW":
            if age >= 2012:
                LED = "yes"
            if age >= 2014:
                Safety_assists = "yes"
            if age >= 2004:
                Parking_sensor = "yes"
            if age >= 2003:
                Infotainment = "yes"
            if age >= 2008:
                Parking_cameras = "yes"
            if age >= 2017:
                Ambient_lightning = "yes"
            if age >= 2018:
                Carplay_Auto = "yes"
            if age >= 2017:
                Digital_driver_display = "yes"
            
        if brand_name == "Bugatti":
            if age >= 2005:
                LED = "yes"
            if age >= 2016:
                Parking_sensor = "yes"
            if age >= 2016:
                Parking_cameras = "yes"
            if age >= 2016:
                Digital_driver_display = "yes"

        if brand_name == "BYD":
            if age >= 2015:
                LED = "yes"
            if age >= 2017:
                Safety_assists = "yes"
            if age >= 2007:
                Parking_sensor = "yes"
            if age >= 2007:
                Infotainment = "yes"
            if age >= 2015:
                Parking_cameras = "yes"
            if age >= 2020:
                Ambient_lightning = "yes"
            if age >= 2020:
                Carplay_Auto = "yes"
            if age >= 2020:
                Digital_driver_display = "yes"

        if brand_name == "Cadillac":
            if age >= 2009:
                LED = "yes"
            if age >= 2013:
                Safety_assists = "yes"
            if age >= 2002:
                Parking_sensor = "yes"
            if age >= 2003:
                Infotainment = "yes"
            if age >= 2008:
                Parking_cameras = "yes"
            if age >= 2018:
                Carplay_Auto = "yes"
            if age >= 2020:
                Digital_driver_display = "yes"

        if brand_name == "Chevrolet":
            if age >= 2011:
                LED = "yes"
            if age >= 2016:
                Safety_assists = "yes"
            if age >= 2006:
                Parking_sensor = "yes"
            if age >= 2003:
                Infotainment = "yes"
            if age >= 2009:
                Parking_cameras = "yes"
            if age >= 2016:
                Ambient_lightning = "yes"
            if age >= 2016:
                Carplay_Auto = "yes"
            if age >= 2022:
                Digital_driver_display = "yes"

        if brand_name == "Chrysler":
            if age >= 2015:
                LED = "yes"
            if age >= 2016:
                Safety_assists = "yes"
            if age >= 2005:
                Parking_sensor = "yes"
            if age >= 2004:
                Infotainment = "yes"
            if age >= 2008:
                Parking_cameras = "yes"
            if age >= 2015:
                Ambient_lightning = "yes"
            if age >= 2019:
                Carplay_Auto = "yes"

        if brand_name == "Citroen":
            if age >= 2011:
                LED = "yes"
            if age >= 2014:
                Safety_assists = "yes"
            if age >= 2002:
                Parking_sensor = "yes"
            if age >= 2008:
                Infotainment = "yes"
            if age >= 2013:
                Parking_cameras = "yes"
            if age >= 2016:
                Carplay_Auto = "yes"
            if age >= 2021:
                Digital_driver_display = "yes"

        if brand_name == "Cupra":
            if age >= 0:
                LED = "yes"
            if age >= 0:
                Safety_assists = "yes"
            if age >= 2:
                Parking_sensor = "yes"
            if age >= 2:
                Infotainment = "yes"
            if age >= 2:
                Parking_cameras = "yes"
            if age >= 2:
                Ambient_lightning = "yes"
            if age >= 2:
                Carplay_Auto = "yes"
            if age >= 2:
                Digital_driver_display = "yes"

        if brand_name == "Dacia":
            if age >= 2018:
                LED = "yes"
            if age >= 2021:
                Safety_assists = "yes"
            if age >= 2013:
                Parking_sensor = "yes"
            if age >= 2014:
                Infotainment = "yes"
            if age >= 2017:
                Parking_cameras = "yes"
            if age >= 2020:
                Carplay_Auto = "yes"
            if age >= 2024:
                Digital_driver_display = "yes"

        if brand_name == "Daihatsu":
            if age >= 2016:
                LED = "yes"
            if age >= 2016:
                Safety_assists = "yes"
            if age >= 2005:
                Parking_sensor = "yes"
            if age >= 2010:
                Infotainment = "yes"
            if age >= 2016:
                Parking_cameras = "yes"
            if age >= 2020:
                Carplay_Auto = "yes"
            if age >= 2019:
                Digital_driver_display = "yes"

        if brand_name == "Dodge":
            if age >= 2012:
                LED = "yes"
            if age >= 2014:
                Safety_assists = "yes"
            if age >= 2006:
                Parking_sensor = "yes"
            if age >= 2008:
                Infotainment = "yes"
            if age >= 2009:
                Parking_cameras = "yes"
            if age >= 2017:
                Carplay_Auto = "yes"

        if brand_name == "DS":
            if age >= 2:
                LED = "yes"
            if age >= 2015:
                Safety_assists = "yes"
            if age >= 2:
                Parking_sensor = "yes"
            if age >= 2:
                Infotainment = "yes"
            if age >= 2:
                Parking_cameras = "yes"
            if age >= 2020:
                Ambient_lightning = "yes"
            if age >= 2016:
                Carplay_Auto = "yes"
            if age >= 2017:
                Digital_driver_display = "yes"

        if brand_name == "Ferrari":
            if age >= 2009:
                LED = "yes"
            if age >= 2018:
                Safety_assists = "yes"
            if age >= 2004:
                Parking_sensor = "yes"
            if age >= 2012:
                Parking_cameras = "yes"
            if age >= 2018:
                Carplay_Auto = "yes"
            if age >= 2014:
                Digital_driver_display = "yes"

        if brand_name == "Fiat":
            if age >= 2015:
                LED = "yes"
            if age >= 2015:
                Safety_assists = "yes"
            if age >= 2007:
                Parking_sensor = "yes"
            if age >= 2012:
                Infotainment = "yes"
            if age >= 2014:
                Parking_cameras = "yes"
            if age >= 2017:
                Carplay_Auto = "yes"

        if brand_name == "Ford":
            if age >= 2012:
                LED = "yes"
            if age >= 2014:
                Safety_assists = "yes"
            if age >= 2003:
                Parking_sensor = "yes"
            if age >= 2005:
                Infotainment = "yes"
            if age >= 2005:
                Parking_cameras = "yes"
            if age >= 2017:
                Carplay_Auto = "yes"
            if age >= 2022:
                Digital_driver_display = "yes"

        if brand_name == "Genesis":
            if age >= 2:
                LED = "yes"
            if age >= 2:
                Safety_assists = "yes"
            if age >= 2:
                Parking_sensor = "yes"
            if age >= 2:
                Infotainment = "yes"
            if age >= 2:
                Parking_cameras = "yes"
            if age >= 2:
                Ambient_lightning = "yes"
            if age >= 2:
                Carplay_Auto = "yes"
            if age >= 2020:
                Digital_driver_display = "yes"

        if brand_name == "GMC":
            if age >= 2015:
                LED = "yes"
            if age >= 2013:
                Safety_assists = "yes"
            if age >= 2000:
                Parking_sensor = "yes"
            if age >= 2006:
                Infotainment = "yes"
            if age >= 2007:
                Parking_cameras = "yes"
            if age >= 2016:
                Carplay_Auto = "yes"
            if age >= 2022:
                Digital_driver_display = "yes"

        if brand_name == "Haval":
            if age >= 2:
                LED = "yes"
            if age >= 2017:
                Safety_assists = "yes"
            if age >= 2:
                Parking_sensor = "yes"
            if age >= 2:
                Infotainment = "yes"
            if age >= 2:
                Parking_cameras = "yes"
            if age >= 2019:
                Carplay_Auto = "yes"
            if age >= 2020:
                Digital_driver_display = "yes"

        if brand_name == "Honda":
            if age >= 2011:
                LED = "yes"
            if age >= 2014:
                Safety_assists = "yes"
            if age >= 2004:
                Parking_sensor = "yes"
            if age >= 2004:
                Infotainment = "yes"
            if age >= 2004:
                Parking_cameras = "yes"
            if age >= 2016:
                Carplay_Auto = "yes"
            if age >= 2021:
                Digital_driver_display = "yes"

        if brand_name == "Hyundai":
            if age >= 2012:
                LED = "yes"
            if age >= 2014:
                Safety_assists = "yes"
            if age >= 2006:
                Parking_sensor = "yes"
            if age >= 2008:
                Infotainment = "yes"
            if age >= 2009:
                Parking_cameras = "yes"
            if age >= 2020:
                Ambient_lightning = "yes"
            if age >= 2016:
                Carplay_Auto = "yes"
            if age >= 2020:
                Digital_driver_display = "yes"

        if brand_name == "Bentley":
            if age >= 2008:
                Infotainment = "yes"

        if brand_name == "Infiniti":
            if age >= 2011:
                LED = "yes"
            if age >= 2007:
                Safety_assists = "yes"
            if age >= 2001:
                Parking_sensor = "yes"
            if age >= 2001:
                Infotainment = "yes"
            if age >= 2001:
                Parking_cameras = "yes"
            if age >= 2017:
                Carplay_Auto = "yes"

        if brand_name == "Jeep":
            if age >= 2016:
                LED = "yes"
            if age >= 2013:
                Safety_assists = "yes"
            if age >= 2005:
                Parking_sensor = "yes"
            if age >= 2010:
                Infotainment = "yes"
            if age >= 2010:
                Parking_cameras = "yes"
            if age >= 2021:
                Ambient_lightning = "yes"
            if age >= 2017:
                Carplay_Auto = "yes"
            if age >= 2021:
                Digital_driver_display = "yes"

        if brand_name == "Kia":
            if age >= 2013:
                LED = "yes"
            if age >= 2014:
                Safety_assists = "yes"
            if age >= 2006:
                Parking_sensor = "yes"
            if age >= 2009:
                Infotainment = "yes"
            if age >= 2009:
                Parking_cameras = "yes"
            if age >= 2019:
                Ambient_lightning = "yes"
            if age >= 2017:
                Carplay_Auto = "yes"
            if age >= 2019:
                Digital_driver_display = "yes"

        if brand_name == "Koenigsegg":
            if age >= 2006:
                LED = "yes"
            if age >= 2014:
                Parking_sensor = "yes"
            if age >= 2010:
                Infotainment = "yes"
            if age >= 2016:
                Parking_cameras = "yes"
            if age >= 2016:
                Carplay_Auto = "yes"
            if age >= 2016:
                Digital_driver_display = "yes"

        if brand_name == "Lada":
            if age >= 2015:
                LED = "yes"
            if age >= 2015:
                Parking_sensor = "yes"
            if age >= 2013:
                Infotainment = "yes"
            if age >= 2015:
                Parking_cameras = "yes"
            if age >= 2019:
                Carplay_Auto = "yes"

        if brand_name == "Lamborghini":
            if age >= 2007:
                LED = "yes"
            if age >= 2018:
                Safety_assists = "yes"
            if age >= 2004:
                Parking_sensor = "yes"
            if age >= 2011:
                Infotainment = "yes"
            if age >= 2011:
                Parking_cameras = "yes"
            if age >= 2016:
                Carplay_Auto = "yes"
            if age >= 2011:
                Digital_driver_display = "yes"

        if brand_name == "Lancia":
            if age >= 2008:
                LED = "yes"
            if age >= 2015:
                Safety_assists = "yes"
            if age >= 2002:
                Parking_sensor = "yes"
            if age >= 2002:
                Infotainment = "yes"
            if age >= 2008:
                Parking_cameras = "yes"
            if age >= 2024:
                Ambient_lightning = "yes"
            if age >= 2021:
                Carplay_Auto = "yes"
            if age >= 2024:
                Digital_driver_display = "yes"

        if brand_name == "Land Rover":
            if age >= 2009:
                LED = "yes"
            if age >= 2012:
                Safety_assists = "yes"
            if age >= 2001:
                Parking_sensor = "yes"
            if age >= 2005:
                Infotainment = "yes"
            if age >= 2005:
                Parking_cameras = "yes"
            if age >= 2017:
                Ambient_lightning = "yes"
            if age >= 2017:
                Carplay_Auto = "yes"
            if age >= 2019:
                Digital_driver_display = "yes"

        if brand_name == "Lexus":
            if age >= 2012:
                LED = "yes"
            if age >= 2015:
                Safety_assists = "yes"
            if age >= 2008:
                Parking_sensor = "yes"
            if age >= 2010:
                Infotainment = "yes"
            if age >= 2010:
                Parking_cameras = "yes"
            if age >= 2020:
                Ambient_lightning = "yes"
            if age >= 2018:
                Carplay_Auto = "yes"
            if age >= 2018:
                Digital_driver_display = "yes"

        if brand_name == "Lotus":
            if age >= 2010:
                LED = "yes"
            if age >= 2022:
                Safety_assists = "yes"
            if age >= 2010:
                Parking_sensor = "yes"
            if age >= 2010:
                Infotainment = "yes"
            if age >= 2022:
                Parking_cameras = "yes"
            if age >= 2022:
                Carplay_Auto = "yes"
            if age >= 2022:
                Digital_driver_display = "yes"

        if brand_name == "Maserati":
            if age >= 2013:
                LED = "yes"
            if age >= 2016:
                Safety_assists = "yes"
            if age >= 2008:
                Parking_sensor = "yes"
            if age >= 2008:
                Infotainment = "yes"
            if age >= 2013:
                Parking_cameras = "yes"
            if age >= 2020:
                Ambient_lightning = "yes"
            if age >= 2018:
                Carplay_Auto = "yes"
            if age >= 2020:
                Digital_driver_display = "yes"

        if brand_name == "Mazda":
            if age >= 2013:
                LED = "yes"
            if age >= 2015:
                Safety_assists = "yes"
            if age >= 2009:
                Parking_sensor = "yes"
            if age >= 2009:
                Infotainment = "yes"
            if age >= 2009:
                Parking_cameras = "yes"
            if age >= 2021:
                Ambient_lightning = "yes"
            if age >= 2018:
                Carplay_Auto = "yes"
            if age >= 2021:
                Digital_driver_display = "yes"

        if brand_name == "McLaren":
            if age >= 2013:
                LED = "yes"
            if age >= 2021:
                Safety_assists = "yes"
            if age >= 2014:
                Parking_sensor = "yes"
            if age >= 2011:
                Infotainment = "yes"
            if age >= 2014:
                Parking_cameras = "yes"
            if age >= 2017:
                Ambient_lightning = "yes"
            if age >= 2019:
                Carplay_Auto = "yes"
            if age >= 2017:
                Digital_driver_display = "yes"

        if brand_name == "Mercedes-Benz":
            if age >= 2012:
                LED = "yes"
            if age >= 2010:
                Safety_assists = "yes"
            if age >= 2004:
                Parking_sensor = "yes"
            if age >= 2004:
                Infotainment = "yes"
            if age >= 2004:
                Parking_cameras = "yes"
            if age >= 2015:
                Ambient_lightning = "yes"
            if age >= 2016:
                Carplay_Auto = "yes"
            if age >= 2018:
                Digital_driver_display = "yes"

        if brand_name == "MG":
            if age >= 2014:
                LED = "yes"
            if age >= 2019:
                Safety_assists = "yes"
            if age >= 2014:
                Parking_sensor = "yes"
            if age >= 2014:
                Infotainment = "yes"
            if age >= 2014:
                Parking_cameras = "yes"
            if age >= 2019:
                Carplay_Auto = "yes"
            if age >= 2020:
                Digital_driver_display = "yes"

        if brand_name == "Mini":
            if age >= 2014:
                LED = "yes"
            if age >= 2019:
                Safety_assists = "yes"
            if age >= 2006:
                Parking_sensor = "yes"
            if age >= 2006:
                Infotainment = "yes"
            if age >= 2014:
                Parking_cameras = "yes"
            if age >= 2020:
                Ambient_lightning = "yes"
            if age >= 2018:
                Carplay_Auto = "yes"
            if age >= 2020:
                Digital_driver_display = "yes"

        if brand_name == "Mitsubishi":
            if age >= 2015:
                LED = "yes"
            if age >= 2019:
                Safety_assists = "yes"
            if age >= 2005:
                Parking_sensor = "yes"
            if age >= 2009:
                Infotainment = "yes"
            if age >= 2009:
                Parking_cameras = "yes"
            if age >= 2018:
                Carplay_Auto = "yes"
            if age >= 2023:
                Digital_driver_display = "yes"

        if brand_name == "NIO":
            if age >= 2:
                LED = "yes"
            if age >= 2:
                Safety_assists = "yes"
            if age >= 2:
                Parking_sensor = "yes"
            if age >= 2:
                Infotainment = "yes"
            if age >= 2:
                Parking_cameras = "yes"
            if age >= 2:
                Ambient_lightning = "yes"
            if age >= 2018:
                Carplay_Auto = "yes"
            if age >= 2:
                Digital_driver_display = "yes"

        if brand_name == "Nissan":
            if age >= 2014:
                LED = "yes"
            if age >= 2019:
                Safety_assists = "yes"
            if age >= 2008:
                Parking_sensor = "yes"
            if age >= 2008:
                Infotainment = "yes"
            if age >= 2008:
                Parking_cameras = "yes"
            if age >= 2021:
                Ambient_lightning = "yes"
            if age >= 2018:
                Carplay_Auto = "yes"
            if age >= 2021:
                Digital_driver_display = "yes"

        if brand_name == "Opel":
            if age >= 2013:
                LED = "yes"
            if age >= 2016:
                Safety_assists = "yes"
            if age >= 2005:
                Parking_sensor = "yes"
            if age >= 2005:
                Infotainment = "yes"
            if age >= 2008:
                Parking_cameras = "yes"
            if age >= 2017:
                Carplay_Auto = "yes"
            if age >= 2020:
                Digital_driver_display = "yes"

        if brand_name == "Pagani":
            if age >= 2011:
                LED = "yes"
            if age >= 2017:
                Parking_sensor = "yes"
            if age >= 2011:
                Infotainment = "yes"
            if age >= 2017:
                Parking_cameras = "yes"
            if age >= 2022:
                Carplay_Auto = "yes"

        if brand_name == "Peugeot":
            if age >= 2013:
                LED = "yes"
            if age >= 2014:
                Safety_assists = "yes"
            if age >= 2004:
                Parking_sensor = "yes"
            if age >= 2004:
                Infotainment = "yes"
            if age >= 2008:
                Parking_cameras = "yes"
            if age >= 2020:
                Ambient_lightning = "yes"
            if age >= 2018:
                Carplay_Auto = "yes"
            if age >= 2019:
                Digital_driver_display = "yes"

        if brand_name == "Porsche":
            if age >= 2012:
                LED = "yes"
            if age >= 2009:
                Safety_assists = "yes"
            if age >= 2002:
                Parking_sensor = "yes"
            if age >= 2003:
                Infotainment = "yes"
            if age >= 2008:
                Parking_cameras = "yes"
            if age >= 2016:
                Ambient_lightning = "yes"
            if age >= 2015:
                Carplay_Auto = "yes"
            if age >= 2016:
                Digital_driver_display = "yes"

        if brand_name == "RAM":
            if age >= 2013:
                LED = "yes"
            if age >= 2018:
                Safety_assists = "yes"
            if age >= 2:
                Parking_sensor = "yes"
            if age >= 2:
                Infotainment = "yes"
            if age >= 2:
                Parking_cameras = "yes"
            if age >= 2018:
                Carplay_Auto = "yes"
            if age >= 2018:
                Digital_driver_display = "yes"
            if age >= 2013:
                Air_suspension = "yes"
        
        if brand_name == "Renault":
            if age >= 2013:
                LED = "yes"
            if age >= 2019:
                Safety_assists = "yes"
            if age >= 2001:
                Parking_sensor = "yes"
            if age >= 2009:
                Infotainment = "yes"
            if age >= 2009:
                Parking_cameras = "yes"
            if age >= 2019:
                Ambient_lightning = "yes"
            if age >= 2016:
                Carplay_Auto = "yes"
            if age >= 2019:
                Digital_driver_display = "yes"

        if brand_name == "Rolls-Royce":
            if age >= 2007:
                LED = "yes"
            if age >= 2017:
                Safety_assists = "yes"
            if age >= 2003:
                Parking_sensor = "yes"
            if age >= 2003:
                Infotainment = "yes"
            if age >= 2007:
                Parking_cameras = "yes"
            if age >= 2017:
                Ambient_lightning = "yes"
            if age >= 2020:
                Carplay_Auto = "yes"
            if age >= 2017:
                Digital_driver_display = "yes"
            if age >= 1965:
                Air_suspension = "yes"
            
        if brand_name == "Rover":
            if age >= 1999:
                Parking_sensor = "yes"
            if age >= 2004:
                Infotainment = "yes"

        if brand_name == "Saab":
            if age >= 2004:
                Parking_sensor = "yes"
            if age >= 2005:
                Infotainment = "yes"

        if brand_name == "Seat":
            if age >= 2012:
                LED = "yes"
            if age >= 2016:
                Safety_assists = "yes"
            if age >= 2004:
                Parking_sensor = "yes"
            if age >= 2006:
                Infotainment = "yes"
            if age >= 2006:
                Parking_cameras = "yes"
            if age >= 2017:
                Ambient_lightning = "yes"
            if age >= 2016:
                Carplay_Auto = "yes"
            if age >= 2018:
                Digital_driver_display = "yes"

        if brand_name == "Skoda":
            if age >= 2013:
                LED = "yes"
            if age >= 2015:
                Safety_assists = "yes"
            if age >= 2004:
                Parking_sensor = "yes"
            if age >= 2006:
                Infotainment = "yes"
            if age >= 2006:
                Parking_cameras = "yes"
            if age >= 2020:
                Ambient_lightning = "yes"
            if age >= 2017:
                Carplay_Auto = "yes"
            if age >= 2020:
                Digital_driver_display = "yes"

        if brand_name == "Smart":
            if age >= 2014:
                LED = "yes"
            if age >= 2018:
                Safety_assists = "yes"
            if age >= 2007:
                Parking_sensor = "yes"
            if age >= 2014:
                Infotainment = "yes"
            if age >= 2014:
                Parking_cameras = "yes"
            if age >= 2023:
                Ambient_lightning = "yes"
            if age >= 2018:
                Carplay_Auto = "yes"
            if age >= 2023:
                Digital_driver_display = "yes"

        if brand_name == "Subaru":
            if age >= 2014:
                LED = "yes"
            if age >= 2009:
                Safety_assists = "yes"
            if age >= 2009:
                Parking_sensor = "yes"
            if age >= 2009:
                Infotainment = "yes"
            if age >= 2009:
                Parking_cameras = "yes"
            if age >= 2017:
                Carplay_Auto = "yes"

        if brand_name == "Suzuki":
            if age >= 2014:
                LED = "yes"
            if age >= 2016:
                Safety_assists = "yes"
            if age >= 2010:
                Parking_sensor = "yes"
            if age >= 2015:
                Infotainment = "yes"
            if age >= 2015:
                Parking_cameras = "yes"
            if age >= 2019:
                Carplay_Auto = "yes"

        if brand_name == "Tesla":
            if age >= 2012:
                LED = "yes"
            if age >= 2012:
                Safety_assists = "yes"
            if age >= 2012:
                Parking_sensor = "yes"
            if age >= 2012:
                Infotainment = "yes"
            if age >= 2012:
                Parking_cameras = "yes"
            if age >= 2020:
                Ambient_lightning = "yes"
            if age >= 2012:
                Digital_driver_display = "yes"

        if brand_name == "Toyota":
            if age >= 2014:
                LED = "yes"
            if age >= 2017:
                Safety_assists = "yes"
            if age >= 2008:
                Parking_sensor = "yes"
            if age >= 2008:
                Infotainment = "yes"
            if age >= 2010:
                Parking_cameras = "yes"
            if age >= 2020:
                Ambient_lightning = "yes"
            if age >= 2019:
                Carplay_Auto = "yes"
            if age >= 2023:
                Digital_driver_display = "yes"

        if brand_name == "Vauxhall":
            if age >= 2013:
                LED = "yes"
            if age >= 2016:
                Safety_assists = "yes"
            if age >= 2005:
                Parking_sensor = "yes"
            if age >= 2005:
                Infotainment = "yes"
            if age >= 2008:
                Parking_cameras = "yes"
            if age >= 2017:
                Carplay_Auto = "yes"
            if age >= 2020:
                Digital_driver_display = "yes"

        if brand_name == "Volkswagen":
            if age >= 2010:
                LED = "yes"
            if age >= 2011:
                Safety_assists = "yes"
            if age >= 2003:
                Parking_sensor = "yes"
            if age >= 2005:
                Infotainment = "yes"
            if age >= 2005:
                Parking_cameras = "yes"
            if age >= 2018:
                Ambient_lightning = "yes"
            if age >= 2016:
                Carplay_Auto = "yes"
            if age >= 2017:
                Digital_driver_display = "yes"

        if brand_name == "Volvo":
            if age >= 2012:
                LED = "yes"
            if age >= 2013:
                Safety_assists = "yes"
            if age >= 2004:
                Parking_sensor = "yes"
            if age >= 2006:
                Infotainment = "yes"
            if age >= 2006:
                Parking_cameras = "yes"
            if age >= 2016:
                Carplay_Auto = "yes"
            if age >= 2015:
                Digital_driver_display = "yes"

        if brand_name == "Acura":
            if model_name == "RL":
                if age >= 2006:
                    Safety_assists = "yes"
            if model_name == "MDX":
                if age >= 2010:
                    Safety_assists = "yes"
            
        if brand_name == "Alpina":
            if model_name == "XB7":
                Air_suspension = "yes"
            if model_name == "B7":
                if age >= 2005:
                    Air_suspension = "yes"
            if model_name == "B5":
                if "Touring" in gen_name:
                    if age >= 2013:
                        Air_suspension = "yes"

        if brand_name == "Aston Martin":
            if model_name == "DB9":
                if age >= 2004:
                    Parking_sensor = "yes"

        if brand_name == "Audi":
            if model_name == "A8":
                if age >= 2001:
                    Safety_assists = "yes"
                    Infotainment = "yes"
                    Parking_cameras = "yes"
                    Air_suspension = "yes"
                if age >= 1997:
                    Parking_sensor = "yes"
            if model_name == "A1":
                Safety_assists = "no"
                if age >= 2018:
                    Safety_assists = "yes"
            if model_name == "S1":
                Safety_assists = "no"
            if model_name == "Q7":
                if age >= 2006:
                    Safety_assists = "yes"
            if model_name == "TT":
                if age >= 2014:
                    Infotainment = "no"
                    Digital_driver_display = "yes"
            if model_name == "A6":
                if "Allroad" in gen_name:
                    if age >= 2000:
                        Air_suspension = "yes"
            if model_name == "A7":
                if age >= 2010:
                    Air_suspension = "yes"
            if model_name == "Q7":
                if age >= 2006:
                    Air_suspension = "yes"
            if model_name == "Q8":
                Air_suspension = "yes"
            if model_name == "Q5":
                if age >= 2017:
                    Air_suspension = "yes"
            if model_name == "e-tron":
                Air_suspension = "yes"
            if model_name == "e-tron GT":
                Air_suspension = "yes"
            if model_name == "S8":
                if age >= 2006:
                    Air_suspension = "yes"
            if model_name == "RS Q8":
                Air_suspension = "yes"  
            if model_name == "A6":
                if age >= 2011:
                    Air_suspension = "yes"
            if model_name == "A7":
                Air_suspension = "yes"
            if model_name == "S6":
                if age >= 2011:
                    Air_suspension = "yes"
            if model_name == "RS6":
                if age >= 2011:
                    Air_suspension = "yes"
            if model_name == "RS7":
                if age >= 2011:
                    Air_suspension = "yes"
            if model_name == "SQ7":
                Air_suspension = "yes"
            if model_name == "SQ6":
                Air_suspension = "yes"
            if model_name == "SQ5":
                if age >= 2017:
                    Air_suspension = "yes"
            if model_name == "SQ8":
                Air_suspension = "yes"
            if model_name == "A6 e-tron":
                Air_suspension = "yes"
            if model_name == "Q6 e-tron":
                Air_suspension = "yes"
            if model_name == "Q8 e-tron":
                Air_suspension = "yes"
            if model_name == "RS e-tron GT":
                Air_suspension = "yes"
            if model_name == "S e-tron GT":
                Air_suspension = "yes"
            if model_name == "S6 e-tron":
                Air_suspension = "yes"
            if model_name == "SQ6 e-tron":
                Air_suspension = "yes"
            if model_name == "SQ8 e-tron":
                Air_suspension = "yes"

        if brand_name == "BMW":
            if model_name == "1 Series":
                Safety_assists = "no"
                if age >= 2017:
                    Safety_assists = "yes"
            if model_name == "7 Series":
                if age >= 2001:
                    Safety_assists = "yes"
                    Infotainment = "yes"
                    Parking_cameras = "yes"
                    Air_suspension = "yes"
                if age >= 2013:
                    Digital_driver_display = "yes"
            if model_name == "5 Series":
                if age >= 2007:
                    Safety_assists = "yes"
                if age >= 2015:
                    Digital_driver_display = "yes"
            if model_name == "X5":
                if age >= 2013:
                    Air_suspension = "yes"
            if model_name == "X7":
                Air_suspension = "yes"
            if model_name == "X6":
                if age >= 2014:
                    Air_suspension = "yes"
            if model_name == "5 Series":
                if "Touring" in gen_name:
                    if age >= 2017:
                        Air_suspension = "yes"
            if model_name == "i7":
                Air_suspension = "yes"
            if model_name == "iX":
                Air_suspension = "yes"

        if brand_name == "Cadillac":
            if model_name == "XLR":
                if age >= 2003:
                    Safety_assists = "yes"
            if model_name == "Lyriq":
                Ambient_lightning = "yes"
            if model_name == "Escalade":
                if age >= 2007:
                    Air_suspension = "yes"
                if age >= 2020:
                    Ambient_lightning = "yes"
            if model_name == "ELR":
                Digital_driver_display = "yes"
            
        if brand_name == "Chevrolet":
            if model_name == "Camaro":
                if age >= 2009:
                    LED = "yes"
            if model_name == "Corvette":
                if age >= 2014:
                    Digital_driver_display = "yes"
            if model_name == "Tahoe":
                if age >= 2020:
                    Air_suspension = "yes"
            if model_name == "Suburban":
                if age >= 2020:
                    Air_suspension = "yes"

        if brand_name == "Chrysler":
            if model_name == "200":
                if age >= 2014:
                    Safety_assists = "yes"

        if brand_name == "Citroen":
            if model_name == "C4":
                if age >= 2018:
                    Digital_driver_display = "yes"
            if model_name == "DS":
                Air_suspension = "yes"

        if brand_name == "Daihatsu":
            if model_name == "Rocky":
                if age >= 2019:
                    Digital_driver_display = "yes"

        if brand_name == "DS" and model_name == "3" and age >= 2019:
            Digital_driver_display = "yes"
        
        if brand_name == "Ferrari":
            if model_name == "GTC4Lusso":
                Infotainment = "yes"
            if model_name == "FF":
                Infotainment = "yes"
            if model_name == "Portofino":
                Infotainment = "yes"
            if model_name == "Purosangue":
                Infotainment = "yes"
            if model_name == "Roma":
                Infotainment = "yes"

        if brand_name == "Fiat":
            if model_name == "500X":
                LED = "yes"
            if model_name == "Scudo":
                Digital_driver_display = "no"
            if model_name == "Tipo":
                Digital_driver_display = "no"
                if age >= 2022:
                    Digital_driver_display = "yes"
            if model_name == "500":
                if "e" in gen_name:
                    if age >= 2020:
                        Digital_driver_display = "yes"
            if model_name == "Pulse":
                Digital_driver_display = "no"
                if age >= 2021:
                    Digital_driver_display = "yes"
            if model_name == "600":
                Digital_driver_display = "no"
                if age >= 2023:
                    Digital_driver_display = "yes"
            if model_name == "Topolino":
                Digital_driver_display = "yes"
            
        if brand_name == "Ford":
            if model_name == "Taurus":
                if age >= 2009:
                    Safety_assists = "yes"
            if model_name == "Expedition":
                if age >= 2021:
                    Ambient_lightning = "yes"
                    Digital_driver_display = "yes"
            if model_name == "Puma":
                if age >= 2019:
                    Digital_driver_display = "yes"
            if model_name == "Evos":
                Digital_driver_display = "yes"
            if model_name == "Tourneo Connect":
                Digital_driver_display = "no"
            if model_name == "Bronco":
                if age >= 2020:
                    Digital_driver_display = "yes"
            if model_name == "Bronco Sport":
                if age >= 2020:
                    Digital_driver_display = "yes"
            if model_name == "Explorer":
                if age >= 2019:
                    Digital_driver_display = "yes"
            if model_name == "Mustang Mach-E":
                Digital_driver_display = "yes"
            if model_name == "Kuga":
                if age >= 2019:
                    Digital_driver_display = "yes"
            if model_name == "Escape":
                if age >= 2019:
                    Digital_driver_display = "yes"
            if model_name == "Expedition":
                if age >= 2003 and age <= 2013:
                    Air_suspension = "yes"

        if brand_name == "Genesis":
            if model_name == "G90/EQ900":
                if age >= 2021:
                    Air_suspension = "yes"

        if brand_name == "GMC":
            if model_name == "Yukon":
                if age >= 2020:
                    Air_suspension = "yes"

        if brand_name == "Honda":
            if model_name == "Civic":
                if age >= 2017:
                    Digital_driver_display = "yes"
            if model_name == "C-RV":
                if age >= 2017:
                    Digital_driver_display = "yes"
            if model_name == "U-RV":
                if age >= 2017:
                    Digital_driver_display = "yes"
            if model_name == "Accord":
                if age >= 2020:
                    Digital_driver_display = "yes"
    
        if brand_name == "Hyundai":
            if model_name == "Equus":
                if age >= 2009:
                    Safety_assists = "yes"
            if model_name == "IONIQ":
                if age >= 2019:
                    Digital_driver_display = "yes"
            if model_name == "Aura":
                Digital_driver_display = "no"

        if brand_name == "Infiniti":
            if model_name == "Q45":
                if age >= 2001:
                    Safety_assists = "yes"
            if model_name == "QX80":
                if age >= 2024:
                    Ambient_lightning = "yes"
                    Digital_driver_display = "yes"
                    Air_suspension = "yes"
            if model_name == "QX60":
                if age >= 2021:
                    Digital_driver_display = "yes"

        if brand_name == "Jaguar":
            if model_name == "XK":
                if age >= 2006:
                    Safety_assists = "yes"
            if model_name == "I-Pace":
                if age >= 2023:
                    Air_suspension = "yes"

        if brand_name == "Jeep":
            if model_name == "Grand Cherokee":
                if age >= 2011:
                    Safety_assists = "yes"
                if age >= 2010:
                    Air_suspension = "yes"
                if age >= 2005:
                    Infotainment = "yes"
            if model_name == "Compass":
                if age >= 2006:
                    Infotainment = "yes"
            if model_name == "Commander":
                if age >= 2006:
                    Infotainment = "yes"
            if model_name == "Patriot":
                if age >= 2007:
                    Infotainment = "yes"
            if model_name == "Cherokee":
                if age >= 2005:
                    Infotainment = "yes"
            if model_name == "Wrangler":
                Ambient_lightning = "no"
                Digital_driver_display = "no"

        if brand_name == "Kia":
            if model_name == "K9":
                if age >= 2018:
                    Ambient_lightning = "yes"
            if model_name == "Stinger":
                Ambient_lightning = "no"
                Digital_driver_display = "no"
            if model_name == "Picanto":
                Ambient_lightning = "no"
                if age >= 2023:
                    Ambient_lightning = "yes"
                    Digital_driver_display = "yes"
            if model_name == "Rio":
                Ambient_lightning = "no"
                Digital_driver_display = "no"
            if model_name == "Stonic":
                Ambient_lightning = "no"
                Digital_driver_display = "no"
            if model_name == "Seltos":
                if age >= 2023:
                    Ambient_lightning = "yes"
                    Digital_driver_display = "yes"
            if model_name == "Niro":
                if age >= 2018:
                    Ambient_lightning = "yes"
                    Digital_driver_display = "yes"
            if model_name == "K7":
                if age >= 2019:
                    Digital_driver_display = "yes"

        if brand_name == "Lamborghini":
            if model_name == "Urus":
                Air_suspension = "yes"
                if age >= 2018:
                    Ambient_lightning = "yes"
            
        if brand_name == "Land Rover":
            if model_name == "Defender":
                Ambient_lightning = "no"
            if model_name == "Range Rover Sport":
                Air_suspension = "yes"
                if age >= 2013:
                    Digital_driver_display = "yes"
            if model_name == "Range Rover Velar":
                Air_suspension = "yes"
                if age >= 2017:
                    Digital_driver_display = "yes"
            if model_name == "Range Rover":
                if age >= 1994:
                    Air_suspension = "yes"
                if age >= 2017:
                    Digital_driver_display = "yes"
            if model_name == "Discovery":
                if age >= 1998:
                    Air_suspension = "yes"
                if age >= 2017:
                    Digital_driver_display = "yes"
            if model_name == "Discovery Sport":
                Air_suspension = "yes"
            if model_name == "Defender":
                if age >= 2019:
                    Air_suspension = "yes"
                    
        if brand_name == "Lexus":
            if model_name == "LS":
                if age >= 2006:
                    if power == 445:
                        LED = "yes"
                if age >= 2003:
                    Safety_assists = "yes"
                if age >= 2001:
                    Parking_sensor = "yes"
                    Air_suspension = "yes"
                if age >= 2000:
                    Infotainment = "yes"
            if model_name == "GS":
                if age >= 2005:
                    Safety_assists = "yes"
            if model_name == "IS":
                if age >= 2005:
                    Safety_assists = "yes"
            if model_name == "RX":
                if age >= 2008:
                    Safety_assists = "yes"
            if model_name == "NX":
                if age >= 2008:
                    Safety_assists = "yes"
            if model_name == "GX":
                if age >= 2023:
                    Digital_driver_display = "yes"
                if age >= 2013:
                    Air_suspension = "yes"
            
        if brand_name == "Maserati":
            if model_name == "Levante":
                Air_suspension = "yes"

        if brand_name == "Mercedes-Benz":
            if model_name == "S-class":
                if age >= 2013:
                    Digital_driver_display = "yes"
                if age >= 2009:
                    LED = "yes"
                if age >= 1998:
                    Safety_assists = "yes"
                    Infotainment = "yes"
                    Air_suspension = "yes"
                if age >= 1994:
                    Parking_sensor = "yes"
            if model_name == "A-class":
                if age >= 2012:
                    LED = "yes"
                if age >= 2008:
                    Infotainment = "yes"
            if model_name == "AMG GT":
                LED = "yes"
            if model_name == "GT 4-Door Coupe":
                LED = "yes"
            if model_name == "AMG ONE":
                LED = "yes"
            if model_name == "B-class":
                if age >= 2011:
                    LED = "yes"
            if model_name == "C-class":
                if age >= 2018:
                    Digital_driver_display = "yes"
                if age >= 2014:
                    Air_suspension = "yes"
                if age >= 2011:
                    LED = "yes"
                if age >= 2005:
                    Safety_assists = "yes"
                if age >= 2000:
                    Parking_sensor = "yes"
            if model_name == "CL":
                if age >= 2010:
                    LED = "yes"
                if age >= 1999:
                    Safety_assists = "yes"
            if model_name == "CLS":
                Air_suspension = "yes"
                if age >= 2011:
                    LED = "yes"
            if model_name == "E-class":
                if age >= 2016:
                    Digital_driver_display = "yes"
                if age >= 2009:
                    LED = "yes"
                if age >= 2005:
                    Safety_assists = "yes"
                if age >= 2001:
                    Parking_sensor = "yes"
                    Air_suspension = "yes"
            if model_name == "G-class":
                if age >= 2012:
                    LED = "yes"
                if age >= 2007:
                    Parking_sensor = "yes"
                if age >= 2018:
                    Air_suspension = "yes"
            if model_name == "GL":
                Air_suspension = "yes"
                if age >= 2009:
                    LED = "yes"
            if model_name == "GLK":
                if age >= 2012:
                    LED = "yes"
            if model_name == "M-class":
                if age >= 2011:
                    LED = "yes"
                if age >= 2005:
                    Air_suspension = "yes"
                if age >= 2001:
                    Parking_sensor = "yes"
            if model_name == "R-class":
                if age >= 2009:
                    LED = "yes"
            if model_name == "SLK":
                if age >= 2011:
                    LED = "yes"
            if model_name == "SLS AMG":
                LED = "yes"
            if model_name == "Vito":
                LED = "no"
                Ambient_lightning = "no"
                Digital_driver_display = "no"
            if model_name == "SL-class":
                if age >= 1998:
                    Safety_assists = "yes"
                if age >= 2001:
                    Parking_sensor = "yes"
                if age >= 2021:
                    Air_suspension = "yes"
            if model_name == "CLK":
                if age >= 1999:
                    Parking_sensor = "yes"
            if model_name == "Sprinter":
                Ambient_lightning = "no"
                Digital_driver_display = "no"
            if model_name == "T-class":
                Ambient_lightning = "no"
                Digital_driver_display = "no"
            if model_name == "X-class":
                Ambient_lightning = "no"
                Digital_driver_display = "no"
            if model_name == "EQE":
                Air_suspension = "yes"
            if model_name == "EQS":
                Air_suspension = "yes"
            if model_name == "EQE SUV":
                Air_suspension = "yes"
            if model_name == "EQG":
                Air_suspension = "yes"
            if model_name == "EQS SUV":
                Air_suspension = "yes"
            if model_name == "GLC":
                Air_suspension = "yes"
            if model_name == "GLE":
                Air_suspension = "yes"
            if model_name == "GLS":
                Air_suspension = "yes"

        if brand_name == "Mini":
            if model_name == "Hatch":
                if age >= 2018:
                    Safety_assists = "yes"

        if brand_name == "Mitsubishi":
            if model_name == "Outlander":
                if age >= 2015:
                    Safety_assists = "yes"
                if age >= 2021:
                    Digital_driver_display = "yes"
            if model_name == "Pajero":
                if age >= 2015:
                    Safety_assists = "yes"
            if model_name == "Pajero Sport":
                if age >= 2016:
                    Safety_assists = "yes"
            if model_name == "Montero Sport":
                if age >= 2015:
                    Safety_assists = "yes"
            if model_name == "ASX":
                if age >= 2016:
                    Safety_assists = "yes"
            if model_name == "Xpander":
                if age >= 2017:
                    Safety_assists = "yes"
            if model_name == "Eclpise Cross":
                if age >= 2017:
                    Safety_assists = "yes"
                if age >= 2021:
                    Digital_driver_display = "yes"
            if model_name == "Lancer":
                if age >= 2017:
                    Digital_driver_display = "yes"
            
        if brand_name == "Nissan":
            if model_name == "Leaf":
                LED = "yes"
                if age >= 2017:
                    Safety_assists = "yes"
            if model_name == "X-Trail":
                if age >= 2014:
                    Safety_assists = "yes"
            if model_name == "Rogue":
                if age >= 2017:
                    Safety_assists = "yes"
            if model_name == "Altima":
                if age >= 2018:
                    Safety_assists = "yes"

        if brand_name == "Opel":
            if model_name == "Vivaro":
                Safety_assists = "yes"

        if brand_name == "Peugeot":
            if model_name == "508":
                if age >= 2018:
                    Ambient_lightning = "yes"
            if model_name == "5008":
                if age >= 2016:
                    Ambient_lightning = "yes"
            if model_name == "3008":
                if age >= 2016:
                    Ambient_lightning = "yes"

        if brand_name == "Porsche":
            if model_name == "911":
                if age >= 2011:
                    LED = "yes"
            if model_name == "Boxster":
                if age >= 2012:
                    LED = "yes"
            if model_name == "Cayenne":
                Air_suspension = "yes"
                if age >= 2010:
                    LED = "yes"
            if model_name == "Cayman":
                if age >= 2013:
                    LED = "yes"
            if model_name == "Macan":
                LED = "yes"
                Air_suspension = "yes"
            if model_name == "Panamera":
                LED = "yes"
                Air_suspension = "yes"
            if model_name == "Taycan":
                Air_suspension = "yes"

        if brand_name == "Renault":
            if model_name == "Clio":
                if age >= 2012:
                    LED = "yes"
            if model_name == "Duster":
                LED = "no"
                Safety_assists = "no"
                Ambient_lightning = "no"
                Digital_driver_display = "no"
                if age >= 2021:
                    LED = "yes"
            if model_name == "Espace":
                if age >= 2015:
                    Safety_assists = "yes"
                    Ambient_lightning = "yes"
            if model_name == "Talisman":
                Safety_assists = "yes"
                if age >= 2015:
                    Ambient_lightning = "yes"
            if model_name == "Megane":
                if age >= 2016:
                    Safety_assists = "yes"
                    Ambient_lightning = "yes"
            if model_name == "Scenic":
                if age >= 2015:
                    Ambient_lightning = "yes"
                if age >= 2016:
                    Safety_assists = "yes"
            if model_name == "Master":
                Ambient_lightning = "no"
                Digital_driver_display = "no"
            if model_name == "Kadjar":
                if age >= 2015:
                    Ambient_lightning = "yes"
            if model_name == "Koleos":
                if age >= 2015:
                    Ambient_lightning = "yes"

        if brand_name == "Seat":
            if model_name == "Leon":
                if age >= 2016:
                    Ambient_lightning = "yes"
            if model_name == "Ateca":
                if age >= 2016:
                    Digital_driver_display = "yes"

        if brand_name == "Subaru":
            if model_name == "WRX":
                if age >= 2014:
                    LED = "yes"
            if model_name == "Legacy":
                if age >= 2012:
                    Safety_assists = "yes"
                if age >= 2014:
                    LED = "yes"   
            if model_name == "Outback":
                if age >= 2013:
                    Safety_assists = "yes"

        if brand_name == "Tesla":
            if model_name == "Model S":
                Air_suspension = "yes"
            if model_name == "Model X":
                Air_suspension = "yes"

        if brand_name == "Toyota":
            if model_name == "Land Cruiser":
                if age >= 2002:
                    Parking_sensor = "yes"
                    Infotainment = "yes"
                    Air_suspension = "yes"
            if model_name == "Corolla":
                if age >= 2022:
                    Digital_driver_display = "yes"
            if model_name == "Yaris":
                if age >= 2020:
                    Digital_driver_display = "yes"
            if model_name == "Veloz":
                Digital_driver_display = "yes"
            if model_name == "Sequoia":
                if age >= 2022:
                    Air_suspension = "yes"

        if brand_name == "Volkswagen":
            if model_name == "Polo":
                Safety_assists = "no"
                Ambient_lightning = "no"
                if age >= 2017:
                    Safety_assists = "no"
                if age >= 2021:
                    Ambient_lightning = "yes"
                    Digital_driver_display = "yes"
            if model_name == "Phaeton":
                Parking_sensor = "yes"
                Safety_assists = "yes"
                Infotainment = "yes"
                Parking_cameras = "yes"
                Air_suspension = "yes"
            if model_name == "Touareg":
                Air_suspension = "yes"
                Infotainment = "yes"
                Parking_cameras = "yes"
                Parking_sensor = "yes"
            if model_name == "Up":
                Ambient_lightning = "no"
                Digital_driver_display = "no"
            if model_name == "Transporter":
                Ambient_lightning = "no"
                if age >= 2021:
                    Ambient_lightning = "yes"
                    Digital_driver_display = "yes"
            if model_name == "Saveiro":
                Ambient_lightning = "no"
                Digital_driver_display = "no"
            if model_name == "Teramont":
                Ambient_lightning = "no"
                Digital_driver_display = "no"
            if model_name == "T-Cross":
                Ambient_lightning = "no"
                if age >= 2021:
                    Ambient_lightning = "yes"

        if brand_name == "Volvo":
            if model_name == "S80":
                if age >= 2002:
                    Parking_sensor = "yes"
                if age >= 2007:
                    Safety_assists = "yes"
            if model_name == "XC90":
                if age >= 2002:
                    Parking_sensor = "yes"
                if age >= 2014:
                    Digital_driver_display = "yes"
                    Air_suspension = "yes"
            if model_name == "XC60":
                if age >= 2017:
                    Air_suspension = "yes"
            if model_name == "V90":
                if age >= 2016:
                    Air_suspension = "yes"
            if model_name == "V60":
                if age >= 2018:
                    Air_suspension = "yes"
        if Speed != 0 and Space != 0 and OffroadTowing != 0 and Comfort != 0 and Maintenance != 0:
            yield {
                'Brand': brand_name,
                'Model': model_name,
                'Generation': generation,
                'Generation name': gen_name,
                'Body type': body_type,
                'Age': age,
                'Speed': Speed,
                'Space': Space,
                'OffroadTowing': OffroadTowing,
                'Maintenance': Maintenance,
                'Comfort': Comfort,
                'Engine Type': engine_type,
                'Engine Modification': engine_modification,
                'Fuel type': fuel_type,
                'Power': power,
                'Torque': torque,
                'Weight': kerb_weight,
                'Seats': seats,
                'Doors': doors,
                'Gearbox': gearbox,
                'Drivetrain': drivetrain,
                'Consumption': fuel_consumption,
                'SafetyFeatures': Safety_assists,
                'AmbientLightning': Ambient_lightning,
                'Infotainment': Infotainment,
                'AppleCarplayAndroidAuto': Carplay_Auto,
                'LED': LED,
                'ParkingSensors': Parking_sensor,
                'ParkingCameras': Parking_cameras,
                'DigitalDriverDisplay': Digital_driver_display,
                'AirSuspension': Air_suspension,

            }

    def parse_weight(self, text):
        pattern = r'(\d+)(?:-(\d+))? kg'
        match = re.match(pattern, text)
        if match:
            num1 = int(match.group(1))
            num2 = match.group(2)
            if num2:
                num2 = int(num2)
                average = (num1 + num2) / 2
                average = int(average)
                return average
            return num1
        return None
    
    def seats_doors(self, text):
        pattern = r'(\d+)(?:-(\d+))?'
        match = re.match(pattern, text)
        if match:
            num1 = int(match.group(1))
            num2 = match.group(2)
            if num2:
                num2 = int(num2)
                average = (num1 + num2) / 2
                average = int(average)
                return average
            return num1
        return None
    
    def remove_after_dash(self, s):
        index = s.find('-')
        if index != -1:
            return s[:index]
        return s
    
    def remove_after_at(self, s):
        index = s.find('@')
        if index != -1:
            return s[:index]
        return s
    
    def process_response(self, request, response, spider):
        if response.status == 429:
            logging.warning("Received 429 response. Too many requests. Retrying...")
            sleep(30)  # Sleep for 30 seconds before retrying
            return request.replace(dont_filter=True)
        return response
