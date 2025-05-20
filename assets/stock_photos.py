import random

# Stock photo URLs
STOCK_PHOTOS = {
    "logistics": [
        "https://pixabay.com/get/g0a7700865c1d030c7f2a5b69018019e14a42768bdb8ea77cf317c5b14b92de77e12c345b6c8a798a4eb908bee4a1c246436238eb48159359b9687b4b6e313806_1280.jpg",
        "https://pixabay.com/get/g6a3eb52468d5a84b87795d3f94cd323cfd04f156aa3f9cc1683b4c32952c27217fe48e9336f8848978a86c787b228f2cc120799b9b20c661f521ed8442e3c056_1280.jpg",
        "https://pixabay.com/get/g330556a086dad52f5d3f4cd85da227f649450c3822eac9e4f05ac7776e233367c6ccb57190313e8806d1babfbf26ea00e9e4ae91935aae2fb0a5246a83ddde99_1280.jpg",
        "https://pixabay.com/get/gaafed331aa6c2dd0a64f15c6a3b7af83bfce374934ece4764101f2e2d80008e4889d63cc018ad0ab2706b7c9eafc93bfb8c4b3302d84c75a9f9eeb6c5df43792_1280.jpg"
    ],
    "containers": [
        "https://pixabay.com/get/g8cef5c2553d9aa3576112be6e11822c7fe288d7de7a19a261dc3924d34f81ecebcfe89373f3e1fdee3bd7c422de06a7fcdcb00ac10fa911dc2e34eb6126501eb_1280.jpg",
        "https://pixabay.com/get/gdaa5e0c642879f957de056a702bf83c5b059b65e5fced8cefa324c172b74b03402adb90c91a4b990881fb7bf39d725ac74cd31888f6f592ab7763ef64a9117b9_1280.jpg",
        "https://pixabay.com/get/gfffeef8eb296a949e9996faa2b2d07335117358be1bc19d4b5d0cb3a67099532ed1898b91ca0f40489d486e6b7fbfc4589b61c03fcc98cb41d0b469a781277b0_1280.jpg",
        "https://pixabay.com/get/g7b7635e23cadb751a01a08a5cdc36b23b78f2054d45678e7487f2751017953cd97562cd90f0af37fe8671a3a50ec79ce89defc4f14c371ab28c2de3f9cc5679c_1280.jpg"
    ]
}

def get_random_image(category):
    """Get a random stock photo URL for the given category"""
    if category in STOCK_PHOTOS:
        return random.choice(STOCK_PHOTOS[category])
    return random.choice(STOCK_PHOTOS["logistics"])
