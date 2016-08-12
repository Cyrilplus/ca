/**
 * Created by yonie on 2016/8/12.
 */

$(function () {
    var workspace_project_statistic_chart = false;
    var member_statistic_bar = false;
    var member_statistic;
    var add_workspace;
    var add_project;
    var add_iteration;
    var load_all_projects = function () {
        $.ajax({
            url: '/rally/all-projects',
            dataType: 'JSON',
            method: 'POST',
            success: function (data) {
                /**
                 * @param {{name:String}} data
                 */
                $("#projects-table > tbody").html('');
                member_statistic = {};
                var workspaces = [];
                $("#member-statistic-workspaces").html('');
                $.each(data.projects, function (index, item) {
                    var row = "<tr>" +
                        "<td>" + item.name + "</td>" +
                        "<td>" + item.workspace + "</td>" +
                        "<td>" + item["member-size"] + "</td>" +
                        "</tr>"
                    $("#projects-table > tbody").append(row);

                    if (!member_statistic[item.workspace]) {
                        member_statistic[item.workspace] = [];
                        workspaces.push(item.workspace);
                        $("#member-statistic-workspaces").append('<li><a>' + item.workspace + '</a><li>');
                    }
                    member_statistic[item.workspace].push({
                        name: item.name,
                        value: item['member-size'],
                    });
                });
                $("#member-statistic-workspaces > li > a").click(function () {
                    member_statistic_bar.setData(member_statistic[$(this).html()])
                });
                var current_workspace = $.cookie('workspace_name');
                if (!member_statistic_bar) {
                    member_statistic_bar = Morris.Bar({
                        element: 'member-statistic-bar',
                        data: member_statistic[current_workspace],
                        xkey: 'name',
                        ykeys: ['value'],
                        labels: ['Members',],
                        hideHover: 'auto',
                        resize: true
                    });
                } else {
                    member_statistic_bar.setData(member_statistic[current_workspace])
                }
            },
            error: function () {
                alert("Can't load all projects information from server");
            },
        });
    };
    var load_workspace_statistic = function () {
        $.ajax({
            url: '/rally/workspace-projects-statistic',
            dataType: 'JSON',
            method: 'POST',
            success: function (data) {
                /**
                 * @param {{statistic:Array}} data
                 */
                var statistic = [];
                var workspace_statistic = data.statistic;
                var workspace_size = workspace_statistic.length;
                var i;
                var item;
                for (i = 0; i < workspace_size; i++) {
                    item = {
                        label: workspace_statistic[i].workspace,
                        value: workspace_statistic[i].count,
                    }
                    statistic.push(item);
                }
                if (!workspace_project_statistic_chart) {
                    workspace_project_statistic_chart = Morris.Donut({
                        element: 'workspace-project-statistic-chart',
                        data: statistic,
                        resize: true,
                        colors: [
                            '#87CEFF',
                            '#FF7F50',
                        ]
                    });
                } else {
                    workspace_project_statistic_chart.setData(statistic);
                }
            },
            error: function () {
                alert("Can't load all projects information from server");
            },
        });
    };

    var load_iterations_by_project_workspace_from_rally = function (workspace, project) {

        $("#select-iteration").html('<option value="1" selected="selected">Loading data from Rally ...</option>');
        $.ajax({
            url: '/rally/get-iterations-by-project-workspace',
            dataType: 'JSON',
            method: 'POST',
            data: {workspace: workspace, project: project},
            success: function (data) {
                /**
                 * @param {{iterations:Array}} data
                 */
                $("#select-iteration").html('');
                $.each(data.iterations, function (index, item) {
                    var option = "<option>" + item + "</option>";
                    $("#select-iteration").append(option);
                });
                add_iteration = $("#select-iteration option:selected").text();
            },
            error: function () {
                alert("Can't load workspaces information from rally server");
            }
        });
    };

    var load_projects_by_workspace_from_rally = function (workspace) {
        $("#select-project").html('<option value="1" selected="selected">Loading data from Rally ...</option>');
        $.ajax({
            url: '/rally/get-projects-by-workspace-from-rally',
            dataType: 'JSON',
            method: 'POST',
            data: {workspace: workspace},
            success: function (data) {
                $("#select-project").html('');
                $.each(data.projects, function (index, item) {
                    var option = "<option value='" + item.oid + "'>" + item.name + "</option>";
                    $("#select-project").append(option);
                });
                add_project = $("#select-project option:selected").text();
                load_iterations_by_project_workspace_from_rally(add_workspace, add_project);
            },
            error: function () {
                alert("Can't load workspaces information from rally server");
            }
        });
    };

    var load_workspaces_from_rally = function () {

        $("#select-workspace").html('<option value="1" selected="selected">Loading data from Rally ...</option>');
        $.ajax({
            url: '/rally/get-workspaces-from-rally',
            dataType: 'JSON',
            method: 'POST',
            success: function (data) {
                $("#select-workspace").html('');
                $.each(data.workspaces, function (index, item) {
                    var option = "<option value='" + item.oid + "'>" + item.name + "</option>";
                    $("#select-workspace").append(option);
                });
                add_workspace = $("#select-workspace option:selected").text();
                load_projects_by_workspace_from_rally(add_workspace);
            },
            error: function () {
                alert("Can't load workspaces information from rally server");
            }
        });
    };
    load_workspace_statistic();
    load_all_projects();
    $("#select-workspace").change(function () {
        $("#select-project").html('');
        $("#select-iteration").html('');
        add_workspace = $("#select-workspace option:selected").text();
        load_projects_by_workspace_from_rally(add_workspace);
    });

    $("#select-project").change(function () {
        $("#select-iteration").html('');
        add_project = $("#select-project option:selected").text();
        load_iterations_by_project_workspace_from_rally(add_workspace, add_project);
    });

    $("#select-iteration").change(function () {
        add_iteration = $("#select-iteration option:selected").text();
    });

    $("#btn-add-project").on('click', function () {
        $("#add-project-modal").modal('show');
        load_workspaces_from_rally();
    });
    $("#save-add-project").on('click', function () {
        $("#add-project-modal").modal('hide');
        $.ajax({
            url: '/rally/add-project-from-rally',
            dataType: 'JSON',
            method: 'POST',
            data: {
                workspace: add_workspace,
                project: add_project,
                iteration: add_iteration
            },
            success: function () {
                alert("You are lucky to add or update a project to database");
                location.reload();
            },
            error: function () {
                alert("Can't add this project to database\n Please contact Yong Nie(yonie@cisco.com) to fix this issue");
            }
        });
    });
});