var addChildHeaderTpl = "Add child to ";
$(function() {
    window.editor = new JSONEditor($('#jsoneditor')[0]);
    window.editor.set(config);
    $('#update').click(function() {
        console.log(JSON.stringify(editor.get()));
        $.ajax({
            url: window.location.href,
            data: {
                data: JSON.stringify(editor.get()),
                version: version
            },
            type: 'put',
            success: function() {
                window.location.reload(true);
            }
        });
    });

    $('#addChildModal form').submit(function() {
        $('#modalSubmit').click();
        return false;
    });

    $('.add-env').click(function() {
        var input = $('#addChildModal input');
        var href = $(this).attr('href');

        $('#addChildModal .modal-header h4').text(href);
        $('#addChildModal').modal();
        input.focus();
        console.log(href);
        $('#modalSubmit').click(function() {
            console.log(input.val());
            console.log(href);

            // TODO: validate no slashes
            $.post(href + '/' + input.val(), {}, function () {
                $('#addChildModal').modal('hide');
                window.location.reload(true);
            });
            return false;
        });
        return false;
    });

    $('#addChildModal').on('hide', function () {
        $('#modalSubmit').unbind('click');
    });

    // TODO: confirm delete.
    $('.del-env').click(function() {
        var href = $(this).attr('href');

        $.ajax({
            url: href,
            type: 'delete',
            success: function() {
                window.location.reload(true);
            }
        });
        return false;
    });

    $("#associations > .btn").click(function() {
        $(this).hide();

        $('#add-assoc').show();
        $('#add-assoc .btn').click(function() {
            var href = '/association/' + $('#add-assoc input').val();
            href += '/' + service + '/' + env;

            $(this).button('loading');

            $.ajax({
                url: href,
                type: 'post',
                success: function() {
                    window.location.reload(true);
                }
            });
        });
        return false;
    });

    $('#associations .del-assoc').click(function() {
      $(this).button('loading');
      var href = '/association/' + $(this).data('hostname');
      href += '/' + service + '/' + env;

      $.ajax({
        url: href,
        type: 'delete',
        success: function() {
          window.location.reload(true);
        }
      });
      return false;
    });

    /*
    window.formatter = new JSONFormatter($('#jsonformatter')[0]);
    window.formatter.set(config);
    window.formatter.onError = console.log
    */
});
