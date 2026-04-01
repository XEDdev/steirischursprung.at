export default {
  siteName: "Steirisch Ursprung",
  siteUrl: "https://demo.steirischursprung.at",
  description: "Erlebnishotel, Gasthaus & Brauerei in Brodersdorf bei Graz",
  phone: "+43 3117 5171",
  email: "hotel@steirischursprung.at",
  address: {
    street: "Brodersdorfstraße 85",
    zip: "A-8200",
    city: "Eggersdorf bei Graz"
  },
  nav: {
    left: [
      {
        title: "Hotel", href: "/hotel/",
        children: [
          { title: "Hotel", href: "/hotel/" },
          { title: "Erlebnishotel", href: "/erlebnishotel/" },
          { title: "Angebote & Packages", href: "/angebote-packages/" },
          { title: "Zimmer & Preise", href: "/zimmer-preise/" },
          { title: "Erkundungstour", href: "/zimmer-und-angebote/ursprung-tour/" },
          { title: "Gutscheine bestellen", href: "/gutscheine/" }
        ]
      },
      { title: "Gasthaus", href: "/gasthaus/" },
      {
        title: "Feiern", href: "/feiern-geniessen/",
        children: [
          { title: "Braustube", href: "/zimmer-und-angebote/braustube/" },
          { title: "Veranstaltungssäle", href: "/veranstaltungssaele/" },
          { title: "Hochzeiten", href: "/hochzeiten/" }
        ]
      }
    ],
    right: [
      {
        title: "Seminar", href: "/seminar/",
        children: [
          { title: "Seminar im Bienenstock", href: "/zimmer-und-angebote/bienenstock/" },
          { title: "Veranstaltungssäle", href: "/veranstaltungssaele/" }
        ]
      },
      {
        title: "Brauerei", href: "/brauerei/",
        children: [
          { title: "Sonnenbierführungen", href: "/zimmer-und-angebote/sonnenbierfuehrung/" },
          { title: "Bierempfehlung", href: "/bierempfehlung/" }
        ]
      },
      { title: "Aktuelles", href: "/aktuelles-termine/" }
    ]
  }
};
