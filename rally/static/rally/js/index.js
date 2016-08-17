$(function () {
    var chart_statistic = false;
    var donut_today = false;
    var end = new Date();
    var start = new Date();
    var statistic = function (date) {
        $.ajax({
            url: '/rally/totalstatus',
            dataType: 'JSON',
            method: 'POST',
            data: {
                date: date,
            },
            success: function (data) {
                /**
                 * @param {{thumb_up:string,thumb_down:string}} data
                 *
                 */
                if (date == 'yesterday') {
                    $("#yesterday-up").html(data.thumb_up);
                    $("#yesterday-down").html(data.thumb_down);
                } else if (date == 'today') {
                    $("#today-up").html(data.thumb_up);
                    $("#today-down").html(data.thumb_down);
                    var statistic_today = [{
                        label: "Thumb-up",
                        value: data.thumb_up,
                    }, {
                        label: "Thumb-down",
                        value: data.thumb_down,
                    },];
                    if (!donut_today) {
                        donut_today = Morris.Donut({
                            element: 'morris-donut-chart',
                            data: statistic_today,
                            resize: true,
                            colors: [
                                '#87CEFF',
                                '#FF7F50',
                            ]
                        });
                    } else {
                        donut_today.setData(statistic_today);
                    }
                }
            },
            error: function () {
                alert('can not get total status data from server');
            }
        });
    };


    var chart_statistic_of_days = function (start, end) {
        $.ajax({
            url: '/rally/statisticofdays',
            dataType: 'JSON',
            method: 'POST',
            data: {
                start: start,
                end: end,
            },
            success: function (data) {
                /**
                 * @param {{statistic:Array}} data
                 */
                if (!chart_statistic) {
                    chart_statistic = Morris.Line({
                        element: 'morris-chart-daily-team-trend',
                        data: data.statistic,
                        xkey: 'date',
                        xLabels: 'day',
                        ykeys: ['up', 'down'],
                        labels: ['Thumb-up', 'Thumb-down'],
                        lineColors: [
                            '#87CEFF',
                            '#FF7F50',
                        ],
                    });
                } else {
                    chart_statistic.setData(data.statistic);
                }
            },
            error: function () {
                alert("Can't load statistic data from server");
            }
        });
    };

    var thumb_down_statistic = function (start, end) {
        $.ajax({
            url: '/rally/thumbdownstatistic',
            dataType: 'JSON',
            method: 'POST',
            data: {
                start: start,
                end: end,
            },
            success: function (data) {
                $("#thumbdownstatistic-table > thead > tr").html('');
                $("#thumbdownstatistic-table > thead > tr").append("<td>#</td>");
                $("#thumbdownstatistic-table > tbody  tr").each(function () {
                    var label = $(this).children("td").eq(0).html();
                    $(this).html("<td>" + label + "</td>");
                });

                $.each(data.thumbdownstatistic, function (index, item) {
                    /**
                     * @param {{Others:String}} item
                     */
                    $("#thumbdownstatistic-table > thead > tr").append("<td>" + item.date.slice(5, 10) + "</td>");
                    $("#thumbdownstatistic-table > tbody > tr").eq(0).append("<td>" + item['Architecture unclear'] + "</td>");
                    $("#thumbdownstatistic-table > tbody > tr").eq(1).append("<td>" + item['Interface definition unclear'] + "</td>");
                    $("#thumbdownstatistic-table > tbody > tr").eq(2).append("<td>" + item['Verification definition unclear'] + "</td>");
                    $("#thumbdownstatistic-table > tbody > tr").eq(3).append("<td>" + item['US unclear'] + "</td>");
                    $("#thumbdownstatistic-table > tbody > tr").eq(4).append("<td>" + item['US AC unclear'] + "</td>");
                    $("#thumbdownstatistic-table > tbody > tr").eq(5).append("<td>" + item['Interrupted by temporary task'] + "</td>");
                    $("#thumbdownstatistic-table > tbody > tr").eq(6).append("<td>" + item['Dependency on testbed'] + "</td>");
                    $("#thumbdownstatistic-table > tbody > tr").eq(7).append("<td>" + item['Dependency on developer'] + "</td>");
                    $("#thumbdownstatistic-table > tbody > tr").eq(8).append("<td>" + item['CFD Support'] + "</td>");
                    $("#thumbdownstatistic-table > tbody > tr").eq(9).append("<td>" + item['Bug-Fix (Unrelated to US)'] + "</td>");
                    $("#thumbdownstatistic-table > tbody > tr").eq(10).append("<td>" + item['Technical Skillset'] + "</td>");
                    $("#thumbdownstatistic-table > tbody > tr").eq(11).append("<td>" + item['Critical Accidental'] + "</td>");
                    $("#thumbdownstatistic-table > tbody > tr").eq(12).append("<td>" + item['Dependency on board'] + "</td>");
                    $("#thumbdownstatistic-table > tbody > tr").eq(13).append("<td>" + item.Others + "</td>");
                });
                $("#thumbdownstatistic-table > thead > tr").append("<td>sum</td>");
                $("#thumbdownstatistic-table > tbody  tr").each(function () {
                    var total = 0;
                    $(this).children('td').each(function (index, item) {
                        if (index !== 0)
                            total += parseInt($(this).html());
                    });
                    $(this).append("<td>" + total + "</td>");
                });
            },
            error: function () {
                alert("Can't load thumb down statistic data from server");
            },
        });
    };
    if($.cookie('workspace_pk') == 0){
        alert('I guess that you are the first time to use this tool');
        return;
    }
    statistic('yesterday');
    statistic('today');
    start.setDate(start.getDate() - 9);
    chart_statistic_of_days(start.toISOString().slice(0, 10), end.toISOString().slice(0, 10));
    thumb_down_statistic(start.toISOString().slice(0, 10), end.toISOString().slice(0, 10));

});
