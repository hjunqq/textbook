export function createWindowChart(chart) {
  let points = [];
  function replaceWithTwoSeries(level, rain) {
    points = level.slice(-300);
    chart.setOption({
      legend: {data: ['库水位', '时段雨量']},
      xAxis: {type: 'time'},
      yAxis: [{type: 'value', name: '水位/m'},
              {type: 'value', name: '雨量/mm'}],
      series: [
        {id: 'level', name: '库水位', type: 'line',
         yAxisIndex: 0, connectNulls: false, data: points},
        {id: 'rain', name: '时段雨量', type: 'bar',
         yAxisIndex: 1, data: rain.slice(-300)}
      ]
    }, {replaceMerge: ['series'], lazyUpdate: true});
  }
  function appendTail(reading) {
    const value = reading.quality === 'missing' ? null : reading.value;
    points = [...points, [reading.occurredAt, value]].slice(-300);
    chart.setOption({series: [{id: 'level', data: points}]});
  }
  replaceWithTwoSeries([], []);
  return {appendTail, replaceWithTwoSeries};
}
// 页面调用：const live = createWindowChart(chart);
// 收到下一条观测时调用 live.appendTail(reading)。
