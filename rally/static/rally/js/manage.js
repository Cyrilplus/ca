/**
auth: Yong nie
created time: 2016/8/4
*/


$(function() {
    var options = {};
    var select = '';
    var statistic = false;
    var donut_yesterday = false;
    var donut_today =  false;
    var team_status_pk = false;
    var notes_cell = false;
    // {
    //     1: 'Thumb up',
    //     2: 'Architecture unclear',
    //     3: 'Interface definition unclear',
    //     4: 'Verification definition unclear',
    //     5: 'US unclear',
    //     6: 'US AC unclear',
    //     7: 'Interrupted by temporary task',
    //     8: 'Dependency on testbed',
    //     9: 'Dependency on developer',
    //     10: 'CFD Support',
    //     11: 'Bug-Fix (Unrelated to US)',
    //     12: 'Technical Skillset',
    //     13: 'Critical Accidental',
    //     14: 'Dependency on board',
    //     15: 'Others',
    // };

    var get_options = function() {
        $.ajax({
            url: '/rally/options',
            dataType: 'JSON',
            method: 'POST',
            async: "false",
            success: function(data) {
                $.each(data.options, function(index, item) {
                    options[item.pk] = item.name;
                });
                select = "<select>";
                for (var item in options) {
                    select += "<option value='" + item + "'>" + options[item] + "</option>";
                }
                select += "</select>";
            },
            error: function() {
                alert("Can't load options from server");
            }
        });
    };
    get_options();

    var modified_field = function(pk, field, data) {
        $.ajax({
            url: '/rally/modifiedfield',
            dataType: 'JSON',
            method: 'POST',
            data: {
                pk: pk,
                field: field,
                data: data,
            },
            success: function(data) {
              display_statistic('today');
            },
            error: function() {
                alert("Can't modify the data");
            }
        });
    };


    var find_val_by_name = function(opts, name) {
        for (var item in opts) {
            if (opts[item] == name) {
                return item;
            }
        }
        return -1;
    };


    var select_changed = function() {
        var opt = $(this).find('option:selected').text();
        var val = $(this).val();
        var status = $(this).parent().parent().children('.thumb-down-status');
        var pk = $(this).parent().parent().children('td').eq(0).html();
        var tr = $(this).parent().parent('tr');
        modified_field(pk, 'status', val);
        $(this).parent("td").html(opt);
        if (val != 1) {
            status.html('1');
            if(!tr.hasClass('thumb-down-color')){
              tr.addClass('thumb-down-color');
            }
        } else {
            status.html('0');
            tr.removeClass('thumb-down-color');
        }
    };

    var select_blur = function() {
        var opt = $(this).find('option:selected').text();
        var val = $(this).val();
        var status = $(this).parent().parent().children('.thumb-down-status');
        var pk = $(this).parent().parent().children('td').eq(0).html();
        $(this).parent("td").html(opt);
        if (val != 1) {
            status.html('1');
        } else {
            status.html('0');
        }
    };

    $("#notes-modal .btn-save").click(function(){
      var content = $(".modal-body-content").val();
      modified_field(team_status_pk, 'notes', content);
      if(notes_cell)
        notes_cell.html(content);
      $("#notes-modal").modal('hide');
    });

    var display_one_day = function(table, date, edit) {
        var tbody = table + ' > tbody';
        var seletor = table + ' .option';
        var notes = table + ' .notes';
        $.ajax({
            url: '/rally/teamstatus',
            dataType: 'JSON',
            method: 'POST',
            data: {
                date: date,
            },
            success: function(data) {
                team_status_list = data.team_status;
                $(tbody).html('');
                $.each(team_status_list, function(index, item) {
                    var status_val = 0;
                    var color_class = '';
                    if (item.status != 'Thumb up') {
                        status_val = 1;
                        color_class = 'thumb-down-color';
                    }

                    var row = '<tr class="' + color_class + '">' +
                        '<td>' + item.pk + "</td>" +
                        '<td>' + item.user + "</td>" +
                        '<td class="option">' + item.status + "</td>" +
                        '<td class="notes">' + item.notes + "</td>" +
                        '<td class="thumb-down-status">' + status_val + "</td>" +
                        '</tr>';
                    $(tbody).append(row);
                });
                $(seletor).dblclick(function() {
                    var current_option = $(this).html();
                    $(this).html('');
                    $(this).html(select);
                    var val = find_val_by_name(options, current_option);
                    $(this).children('select').val(val.valueOf());
                    $(this).children('select').change(select_changed);
                    $(this).children('select').blur(select_blur);
                });

                $(notes).dblclick(function() {
                    $(".modal-body-content").val('');
                    notes_cell = $(this);
                    $(".modal-body-content").val($(this).html());
                    if (edit) {
                        $(".modal-body-content").attr("disabled", false);
                        $("#notes-modal .btn-save").attr("disabled", false);
                    } else {
                        $(".modal-body-content").attr("disabled", true);
                        $("#notes-modal .btn-save").attr("disabled", true);
                    }
                    team_status_pk = $(this).parent().children('td').eq(0).html();
                    $("#notes-modal").modal('show');
                });
            },
            error: function() {
                alert("error");
            }
        });
    };
    var display_statistic = function(date) {
        $.ajax({
            url: '/rally/totalstatus',
            dataType: 'JSON',
            method: 'POST',
            data: {
                date: date,
            },
            success: function(data) {
                statistic = [{
                    label: "Thumb up",
                    value: data.thumb_up
                }, {
                    label: "Thumb down",
                    value: data.thumb_down
                }];
                if (date == 'today') {
                    if (!donut_today) {
                        donut_today = Morris.Donut({
                            element: 'today-statistic',
                            data: statistic,
                            resize: true,
                            colors: [
                                '#5cb85c',
                                '#d9534f',
                            ]
                        });
                    } else {
                        donut_today.setData(statistic);
                    }

                } else if (date == 'yesterday') {
                    if (!donut_yesterday) {
                        donut_yesterday = Morris.Donut({
                            element: 'yesterday-statistic',
                            data: statistic,
                            resize: true,
                            colors: [
                                '#5cb85c',
                                '#d9534f',
                            ]
                        });
                    } else {
                        donut_yesterday.setData(statistic);
                    }

                }
            },
            error: function() {
                alert('can not get total status data from server');
            }
        });
    };

    display_one_day('#today-table', 'today', true);
    display_one_day('#yesterday-table', 'yesterday', true);

    display_statistic('today');
    display_statistic('yesterday');
});
