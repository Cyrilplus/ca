/**
 * Created by yonie on 2016/8/11.
 */

$(function () {
    var select_workspace = function () {
        $.ajax({
            url: '/rally/workspaces',
            dataType: 'JSON',
            method: 'POST',
            success: function (data) {
                /**
                 * @param {{workspaces:Array}} data
                 */
                $("#workspace > .dropdown-menu").html('');
                $.each(data.workspaces, function (index, wksp) {
                    var item = '<li class="menu-item dropdown dropdown-submenu">' +
                        '<a><i class="pk">' + wksp.pk + '</i><span>' + wksp.name + '</span></a>'
                    '</li>';
                    $("#workspace > .dropdown-menu").append(item);
                });
                $("#workspace > .dropdown-menu a").on('click', function () {
                    alert("You select a workspace-pk:" + $(this).children('i').html());
                });
            },
            error: function () {
                alert("Can't load workspaces information from server");
            }
        });
    };
    var select_project = function () {
        $.ajax({
            url: '/rally/projects-by-workspace',
            dataType: 'JSON',
            method: 'POST',
            data: {
                workspace: 1,
            },
            success: function (data) {
                /**
                 * @param {{projects:Array}} data
                 */
                $("#project > .dropdown-menu").html('');
                $.each(data.projects, function (index, project) {
                    var item = '<li class="menu-item dropdown dropdown-submenu">' +
                        '<a><i class="pk">' + project.pk + '</i><span>' + project.name + '</span></a>'
                    '</li>';
                    // alert(item);
                    $("#project > .dropdown-menu").append(item);
                });
                $("#project > .dropdown-menu a").on('click', function () {
                    $.cookie('project_pk', parseInt($(this).children('i').html()), {expires: 365, path: '/'});
                    $.cookie('project_name', $(this).children('span').html(), {expires: 365, path: '/'});
                    location.reload();
                });
            },
            error: function () {
                alert("Can't load projects information from server");
            }
        });
    };
    $("#project > a > span").html($.cookie('project_name'));
    select_workspace();
    select_project();
});