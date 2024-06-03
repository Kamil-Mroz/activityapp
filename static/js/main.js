let chart, pieChart={"pie-chart-challenge":null,"pie-chart-exercise":null};
var stats; 
var dates; 

var data_challenge; 
var labels_challenge; 
var colors_challenge; 
var data_exercise; 
var labels_exercise; 
var colors_exercise; 

function renderChart(stats, dates) {
  const options = {
    chart: {
      height: "90%",
      maxWidth: "100%",
      type: "line",
      fontFamily: "Inter, sans-serif",
      dropShadow: {
        enabled: false,
      },
      toolbar: {
        show: false,
      },
    },
    tooltip: {
      enabled: true,
    },
    dataLabels: {
      enabled: true,
    },
    stroke: {
      width: 6,
    },
    grid: {
      show: true,
      strokeDashArray: 4,
      padding: {
        left: 15,
        right: 2,
      },
    },
    series: [
      {
        name: "Data",
        data: stats,
        color: "#1A56DB",
      },
    ],
    legend: {
      show: false
    },
    stroke: {
      curve: 'straight'
    },
    xaxis: {
      categories: dates,
      labels: {
        show: true,
        style: {
          fontFamily: "Inter, sans-serif",
          cssClass: 'text-xs font-normal fill-black dark:fill-white'
        }
      },
      axisBorder: {
        show: false,
      },
      axisTicks: {
        show: false,
      },
    },
    yaxis: {
      labels: {
        show: true,
        style: {
          fontFamily: "Inter, sans-serif",
          cssClass: 'text-xs font-normal fill-black dark:fill-white'
        },
        offsetX: -10,
      },
    },
  };

  
  if (chart) {
    chart.destroy();
  }

  if (document.getElementById("line-chart") && typeof ApexCharts !== 'undefined') {
    chart = new ApexCharts(document.getElementById("line-chart"), options);
    chart.render();
  }
}





function renderPieChart(data,labels,colors,chart_stat)  {
  const options = {
    series: data,
    colors: colors,
    chart: {
      height: 420,
      width: "100%",
      type: "pie",
    },
    stroke: {
      colors: ["white"],
      lineCap: "",
    },
    plotOptions: {
      pie: {
        labels: {
          show: true,
        },
        size: "100%",
        dataLabels: {
          offset: -25
        }
      },
    },
    labels: labels,
    dataLabels: {
      enabled: true,
      style: {
        fontFamily: "Inter, sans-serif",
      },
    },
    legend: {
      position: "bottom",
      fontFamily: "Inter, sans-serif",
    },
    yaxis: {
      labels: {
        formatter: function (value) {
          return value + "%"
        },
      },
    },
    xaxis: {
      labels: {
        formatter: function (value) {
          return value  + "%"
        },
      },
      axisTicks: {
        show: false,
      },
      axisBorder: {
        show: false,
      },
    },
  }


  if (pieChart[chart_stat]) {
      pieChart[chart_stat].destroy();
    }

  if (document.getElementById(chart_stat) && typeof ApexCharts !== 'undefined') {
    pieChart[chart_stat] = new ApexCharts(document.getElementById(chart_stat), options);
    pieChart[chart_stat].render();
  }
}

if(stats && dates){
  renderChart(stats, dates);
}

renderPieChart(data_challenge,labels_challenge,colors_challenge,"pie-chart-challenge");
renderPieChart(data_exercise,labels_exercise,colors_exercise,"pie-chart-exercise");

setInterval(function() {
  
  renderPieChart(data_challenge,labels_challenge,colors_challenge,"pie-chart-challenge");

  renderPieChart(data_exercise,labels_exercise,colors_exercise,"pie-chart-exercise");

  renderChart(stats, dates);
}, 1000 * 60 * 5);
