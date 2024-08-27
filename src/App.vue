<script setup>
import { ref, onMounted, computed, watch } from "vue";
import axios from "axios";
import * as d3 from "d3";
import * as topojson from "topojson-client";
import goldPrices from "./goldPrices.json";
import currencyData from "./currencyData.json";
import currencyCodeMap from "./currencyCodeMap.json";

const worldMap = ref(null);
const comparisonBase = ref("USD");
const selectedYear = ref("2023");
const comparisonYear = ref("1973");
const loading = ref(false);
const currentData = ref({});

const baseOptions = [
  { value: "USD", label: "US Dollar" },
  { value: "GOLD", label: "Gold" },
];

const yearOptions = computed(() => {
  const years = Object.keys(goldPrices).sort((a, b) => a - b);
  return years.filter((year) => parseInt(year) <= parseInt(selectedYear.value));
});

function getCurrencyCode(countryCode) {
  return currencyCodeMap[countryCode] || "Unknown";
}

function getPerformance(currencyCode) {
  const yearData = currentData.value;
  if (!yearData) return null;

  if (comparisonBase.value === "USD") {
    return yearData[currencyCode] || null;
  } else {
    const usdPerformance = yearData[currencyCode] || 0;
    const goldPerformance = goldPrices[selectedYear.value] || 0;
    return ((1 + usdPerformance / 100) / (1 + goldPerformance / 100) - 1) * 100;
  }
}

const colorScale = computed(() => {
  return d3
    .scaleLinear()
    .domain([-10, 0, 10])
    .range(["#dc3545", "#dc3545", "#28a745"])
    .clamp(true);
});

function getCountryColor(performance) {
  if (performance === null) return "#000000";
  return colorScale.value(performance);
}

let svg, path, tooltip;

onMounted(() => {
  drawMap();
});

function drawMap() {
  const width = 960;
  const height = 500;

  svg = d3.select(worldMap.value).attr("width", width).attr("height", height);

  const projection = d3
    .geoMercator()
    .scale(140)
    .translate([width / 2, height / 1.4]);

  path = d3.geoPath().projection(projection);

  tooltip = d3
    .select("body")
    .append("div")
    .attr("class", "tooltip")
    .style("opacity", 0)
    .style("position", "absolute")
    .style("pointer-events", "none");

  d3.json(
    "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"
  ).then((world) => {
    const countries = topojson.feature(world, world.objects.countries);
    updateMap(countries);
  });
}

function updateMap(countries) {
  svg.selectAll("path").remove();

  svg
    .selectAll("path")
    .data(countries.features)
    .enter()
    .append("path")
    .attr("d", path)
    .attr("class", "country")
    .attr("fill", (d) => {
      const currencyCode = getCurrencyCode(d.id);
      const performance = getPerformance(currencyCode);
      return getCountryColor(performance);
    })
    .on("mousemove", (event, d) => {
      const currencyCode = getCurrencyCode(d.id);
      const performance = getPerformance(currencyCode);

      tooltip.transition().duration(200).style("opacity", 0.9);
      tooltip
        .html(
          `
          <div class="country-name">${d.properties.name}</div>
          <div class="currency-code">Currency: ${currencyCode}</div>
          <div class="performance">
            ${
              performance !== null
                ? `${performance > 0 ? "+" : ""}${performance.toFixed(2)}% vs ${
                    comparisonBase.value
                  }`
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
}

watch([comparisonBase, selectedYear, comparisonYear], async () => {
  await updateCurrentData();
  d3.json(
    "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"
  ).then((world) => {
    const countries = topojson.feature(world, world.objects.countries);
    updateMap(countries);
  });
});

async function updateCurrentData() {
  const currentYearData = await fetchCurrencyData(selectedYear.value);
  const comparisonYearData = await fetchCurrencyData(comparisonYear.value);
  const currentGoldPrice = await fetchGoldPrice(selectedYear.value);
  const comparisonGoldPrice = await fetchGoldPrice(comparisonYear.value);

  if (
    currentYearData &&
    comparisonYearData &&
    currentGoldPrice &&
    comparisonGoldPrice
  ) {
    currentData.value = Object.fromEntries(
      Object.keys(currentYearData).map((currency) => {
        const currentPerformance = currentYearData[currency] || 0;
        const comparisonPerformance = comparisonYearData[currency] || 0;
        let relativePerformance;

        if (comparisonBase.value === "USD") {
          relativePerformance =
            ((1 + currentPerformance / 100) /
              (1 + comparisonPerformance / 100) -
              1) *
            100;
        } else {
          const currentGoldPerformance =
            (currentGoldPrice / goldPrices["1973"] - 1) * 100;
          const comparisonGoldPerformance =
            (comparisonGoldPrice / goldPrices["1973"] - 1) * 100;
          relativePerformance =
            ((1 + currentPerformance / 100) /
              (1 + currentGoldPerformance / 100) /
              ((1 + comparisonPerformance / 100) /
                (1 + comparisonGoldPerformance / 100)) -
              1) *
            100;
        }

        return [currency, relativePerformance];
      })
    );
  }
}

async function fetchCurrencyData(year) {
  try {
    const response = await axios.get(`/api/currency-data/${year}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching currency data for ${year}:`, error);
    return null;
  }
}

async function fetchGoldPrice(year) {
  try {
    const response = await axios.get(`/api/gold-price/${year}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching gold price for ${year}:`, error);
    return null;
  }
}

onMounted(async () => {
  await updateCurrentData();
  drawMap();
});
</script>

<template>
  <div id="app">
    <div class="controls">
      <div class="control-group">
        <label for="comparisonBase">Compare against:</label>
        <select id="comparisonBase" v-model="comparisonBase">
          <option
            v-for="option in baseOptions"
            :key="option.value"
            :value="option.value"
          >
            {{ option.label }}
          </option>
        </select>
      </div>
      <div class="control-group">
        <label for="selectedYear">Current year:</label>
        <select id="selectedYear" v-model="selectedYear">
          <option v-for="year in yearOptions" :key="year" :value="year">
            {{ year }}
          </option>
        </select>
      </div>
      <div class="control-group">
        <label for="comparisonYear">Comparison year:</label>
        <input
          type="range"
          id="comparisonYear"
          v-model="comparisonYear"
          :min="yearOptions[0]"
          :max="selectedYear"
          step="1"
        />
        <span>{{ comparisonYear }}</span>
      </div>
    </div>
    <div v-if="loading" class="loading">Loading...</div>
    <svg ref="worldMap"></svg>
  </div>
</template>

<style>
#app {
  font-family: Arial, sans-serif;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 20px;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

label {
  font-weight: bold;
}

select,
input[type="range"] {
  width: 200px;
}

.loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 24px;
  font-weight: bold;
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
