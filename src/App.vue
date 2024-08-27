<script setup>
import { ref, onMounted } from "vue";
import * as d3 from "d3";
import * as topojson from "topojson-client";

const worldMap = ref(null);
const currencyData = ref({});

async function fetchCurrencyData() {
  const currencies = [
    "EUR",
    "GBP",
    "JPY",
    "CHF",
    "CAD",
    "AUD",
    "NZD",
    "CNY",
    "HKD",
    "SGD",
    "INR",
    "MXN",
    "BRL",
    "ZAR",
    "RUB",
    "SEK",
    "NOK",
    "DKK",
    "PLN",
    "TRY",
    "KRW",
    "TWD",
    "MYR",
    "THB",
    "IDR",
    "PHP",
    "AED",
    "SAR",
    "ILS",
    "EGP",
    "COP",
    "CLP",
    "ARS",
    "PEN",
    "CZK",
    "HUF",
    "RON",
    "ISK",
    "BGN",
    "HRK",
    "RSD",
    "UAH",
    "KZT",
    "VND",
    "JOD",
    "BHD",
    "QAR",
    "KWD",
    "OMR",
    "PKR",
    "LKR",
    "MMK",
    "NPR",
    "GHS",
    "KES",
    "NGN",
    "TZS",
    "UGX",
    "BDT",
    "MAD",
  ];
  const promises = currencies.map((currency) =>
    fetch(`/api/v8/finance/chart/${currency}USD=X?interval=1d&range=1y`)
      .then((response) => response.json())
      .catch((error) => {
        console.error(`Error fetching data for ${currency}:`, error);
        return null;
      })
  );

  try {
    const results = await Promise.all(promises);
    const performanceData = {};
    results.forEach((result, index) => {
      if (
        result &&
        result.chart &&
        result.chart.result &&
        result.chart.result[0] &&
        result.chart.result[0].indicators &&
        result.chart.result[0].indicators.quote &&
        result.chart.result[0].indicators.quote[0] &&
        result.chart.result[0].indicators.quote[0].close
      ) {
        const prices = result.chart.result[0].indicators.quote[0].close;
        const startPrice = prices[0];
        const endPrice = prices[prices.length - 1];
        if (startPrice && endPrice) {
          const performance = ((endPrice - startPrice) / startPrice) * 100;
          performanceData[currencies[index]] = performance;
        }
      } else {
        console.warn(`No valid data for ${currencies[index]}`);
      }
    });
    currencyData.value = performanceData;
  } catch (error) {
    console.error("Error processing currency data:", error);
  }
}

function getCurrencyCode(countryCode) {
  const currencyMap = {
    "004": "AFN", // Afghanistan
    "008": "ALL", // Albania
    "012": "DZD", // Algeria
    "020": "AND", // Andorra
    "024": "AOA", // Angola
    "028": "XCD", // Antigua and Barbuda
    "032": "ARS", // Argentina
    "051": "AMD", // Armenia
    "036": "AUD", // Australia
    "040": "EUR", // Austria
    "031": "AZN", // Azerbaijan
    "044": "BSD", // Bahamas
    "048": "BHD", // Bahrain
    "050": "BDT", // Bangladesh
    "052": "BBD", // Barbados
    112: "BYN", // Belarus
    "056": "EUR", // Belgium
    "084": "BZD", // Belize
    204: "XOF", // Benin
    "064": "BTN", // Bhutan
    "068": "BOB", // Bolivia
    "070": "BAM", // Bosnia and Herzegovina
    "072": "BWP", // Botswana
    "076": "BRL", // Brazil
    "096": "BND", // Brunei
    100: "BGN", // Bulgaria
    854: "BIF", // Burundi
    116: "KHR", // Cambodia
    120: "XAF", // Cameroon
    124: "CAD", // Canada
    132: "CVE", // Cape Verde
    140: "XAF", // Central African Republic
    148: "XAF", // Chad
    152: "CLP", // Chile
    156: "CNY", // China
    170: "COP", // Colombia
    174: "KMF", // Comoros
    178: "XAF", // Congo
    180: "CDF", // Democratic Republic of the Congo
    188: "CRC", // Costa Rica
    191: "HRK", // Croatia
    192: "CUP", // Cuba
    196: "EUR", // Cyprus
    203: "CZK", // Czech Republic
    208: "DKK", // Denmark
    262: "DJF", // Djibouti
    214: "DOP", // Dominican Republic
    218: "USD", // Ecuador
    818: "EGP", // Egypt
    222: "SVC", // El Salvador
    226: "XAF", // Equatorial Guinea
    232: "ERN", // Eritrea
    233: "EUR", // Estonia
    231: "ETB", // Ethiopia
    242: "FJD", // Fiji
    246: "EUR", // Finland
    250: "EUR", // France
    266: "XAF", // Gabon
    270: "GMD", // Gambia
    268: "GEL", // Georgia
    276: "EUR", // Germany
    288: "GHS", // Ghana
    300: "EUR", // Greece
    320: "GTQ", // Guatemala
    324: "GNF", // Guinea
    624: "GWP", // Guinea-Bissau
    328: "GYD", // Guyana
    332: "HTG", // Haiti
    340: "HNL", // Honduras
    348: "HUF", // Hungary
    352: "ISK", // Iceland
    356: "INR", // India
    360: "IDR", // Indonesia
    364: "IRR", // Iran
    368: "IQD", // Iraq
    372: "EUR", // Ireland
    376: "ILS", // Israel
    380: "EUR", // Italy
    388: "JMD", // Jamaica
    392: "JPY", // Japan
    400: "JOD", // Jordan
    398: "KZT", // Kazakhstan
    404: "KES", // Kenya
    408: "KPW", // North Korea
    410: "KRW", // South Korea
    414: "KWD", // Kuwait
    417: "KGS", // Kyrgyzstan
    418: "LAK", // Laos
    428: "EUR", // Latvia
    422: "LBP", // Lebanon
    426: "LSL", // Lesotho
    430: "LRD", // Liberia
    434: "LYD", // Libya
    438: "CHF", // Liechtenstein
    440: "EUR", // Lithuania
    442: "EUR", // Luxembourg
    807: "MKD", // North Macedonia
    450: "MGF", // Madagascar
    454: "MWK", // Malawi
    458: "MYR", // Malaysia
    462: "MVR", // Maldives
    466: "XOF", // Mali
    470: "EUR", // Malta
    478: "MRU", // Mauritania
    480: "MUR", // Mauritius
    484: "MXN", // Mexico
    498: "MDL", // Moldova
    492: "EUR", // Monaco
    496: "MNT", // Mongolia
    499: "EUR", // Montenegro
    504: "MAD", // Morocco
    508: "MZN", // Mozambique
    104: "MMK", // Myanmar
    516: "NAD", // Namibia
    524: "NPR", // Nepal
    528: "EUR", // Netherlands
    554: "NZD", // New Zealand
    558: "NIO", // Nicaragua
    562: "XOF", // Niger
    566: "NGN", // Nigeria
    578: "NOK", // Norway
    512: "OMR", // Oman
    586: "PKR", // Pakistan
    275: "ILS", // Palestine
    591: "PAB", // Panama
    598: "PGK", // Papua New Guinea
    600: "PYG", // Paraguay
    604: "PEN", // Peru
    608: "PHP", // Philippines
    616: "PLN", // Poland
    620: "EUR", // Portugal
    634: "QAR", // Qatar
    642: "RON", // Romania
    643: "RUB", // Russia
    646: "RWF", // Rwanda
    659: "XCD", // Saint Kitts and Nevis
    662: "XCD", // Saint Lucia
    670: "XCD", // Saint Vincent and the Grenadines
    882: "WST", // Samoa
    674: "EUR", // San Marino
    678: "STN", // Sao Tome and Principe
    682: "SAR", // Saudi Arabia
    686: "XOF", // Senegal
    688: "RSD", // Serbia
    690: "SCR", // Seychelles
    694: "SLL", // Sierra Leone
    702: "SGD", // Singapore
    703: "EUR", // Slovakia
    705: "EUR", // Slovenia
    "090": "SBD", // Solomon Islands
    706: "SOS", // Somalia
    710: "ZAR", // South Africa
    724: "EUR", // Spain
    144: "LKR", // Sri Lanka
    729: "SDG", // Sudan
    740: "SRD", // Suriname
    748: "SZL", // Eswatini (Swaziland)
    752: "SEK", // Sweden
    756: "CHF", // Switzerland
    760: "SYP", // Syria
    158: "TWD", // Taiwan
    762: "TJS", // Tajikistan
    834: "TZS", // Tanzania
    764: "THB", // Thailand
    626: "XOF", // Togo
    776: "TOP", // Tonga
    780: "TTD", // Trinidad and Tobago
    788: "TND", // Tunisia
    792: "TRY", // Turkey
    795: "TMT", // Turkmenistan
    800: "UGX", // Uganda
    804: "UAH", // Ukraine
    784: "AED", // United Arab Emirates
    826: "GBP", // United Kingdom
    840: "USD", // United States
    858: "UYU", // Uruguay
    860: "UZS", // Uzbekistan
    548: "VUV", // Vanuatu
    862: "VES", // Venezuela
    704: "VND", // Vietnam
    887: "YER", // Yemen
    894: "ZMW", // Zambia
    716: "ZWL", // Zimbabwe
  };
  return currencyMap[countryCode] || "N/A";
}

function getCurrencyPerformance(currencyCode) {
  return currencyData.value[currencyCode] || null;
}

const colorScale = d3
  .scaleLinear()
  .domain([-10, 0, 10])
  .range(["#dc3545", "#dc3545", "#28a745"])
  .clamp(true);

function getCountryColor(performance) {
  if (performance === null) return "#000000";
  return colorScale(performance);
}

onMounted(async () => {
  await fetchCurrencyData();

  const width = 960;
  const height = 500;

  const svg = d3
    .select(worldMap.value)
    .attr("width", width)
    .attr("height", height);

  const projection = d3
    .geoMercator()
    .scale(140)
    .translate([width / 2, height / 1.4]);

  const path = d3.geoPath().projection(projection);

  const world = await d3.json(
    "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"
  );
  const countries = topojson.feature(world, world.objects.countries);

  const tooltip = d3
    .select("body")
    .append("div")
    .attr("class", "tooltip")
    .style("opacity", 0)
    .style("position", "absolute")
    .style("pointer-events", "none");

  svg
    .selectAll("path")
    .data(countries.features)
    .enter()
    .append("path")
    .attr("d", path)
    .attr("class", "country")
    .attr("fill", (d) => {
      const currencyCode = getCurrencyCode(d.id);
      const performance = getCurrencyPerformance(currencyCode);
      return getCountryColor(performance);
    })
    .on("mousemove", (event, d) => {
      const currencyCode = getCurrencyCode(d.id);
      const performance = getCurrencyPerformance(currencyCode);

      tooltip.transition().duration(200).style("opacity", 0.9);
      tooltip
        .html(
          `
          <div class="country-name">${d.properties.name}</div>
          <div class="currency-code">Currency: ${currencyCode}</div>
          <div class="performance">
            ${
              performance !== null
                ? `${performance > 0 ? "+" : ""}${performance.toFixed(
                    2
                  )}% vs USD`
                : "No data"
            }
          </div>
        `
        )
        .style("left", `${event.pageX + 10}px`)
        .style("top", `${event.pageY - 28}px`);
    })
    .on("mouseout", () => {
      tooltip.transition().duration(500).style("opacity", 0);
    });
});
</script>

<template>
  <div id="app">
    <svg ref="worldMap"></svg>
  </div>
</template>

<style>
#app {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem;
  font-weight: normal;
}

.country {
  stroke: #fff;
  stroke-width: 0.5;
  transition: stroke-width 0.3s;
}

.country:hover {
  stroke-width: 1.5;
  stroke: #333;
}

.tooltip {
  background-color: rgba(255, 255, 255, 0.98);
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 14px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  max-width: 250px;
  line-height: 1.6;
  text-align: left;
}

.tooltip .country-name {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 8px;
  color: #333;
}

.tooltip .currency-code {
  font-weight: 500;
  color: #030303;
  margin-bottom: 4px;
}

.tooltip .performance {
  font-weight: bold;
  font-size: 16px;
  margin-top: 8px;
  color: #030303;
}

@media (min-width: 1024px) {
  body {
    display: flex;
    place-items: center;
  }

  #app {
    display: grid;
    grid-template-columns: 1fr 1fr;
    padding: 0 2rem;
  }
}
</style>
