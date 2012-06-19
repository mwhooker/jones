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

    $('.add-env').click(function() {
      console.log('hi');
      var form = $('#addChildModal form');
      var env = $(this).data('env');
      console.log(env)

      $('#addChildModal .modal-header h4').text(env);
      $('#addChildModal').modal();

      $('input', form).focus();
      $(form).submit(function() {
        $(this).attr('action', env + '/' + $('input', this).val());
        console.log($(this).attr('action'));
      });

      return false;
    });

    $('#modalSubmit').click(function() {
      $('#addChildModal form').submit();
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
            var href = '/service/' + service;
            href += '/association/' + $('#add-assoc input').val();

            $(this).button('loading');

            $.ajax({
              url: href,
              data: {env: env},
              type: 'put',
              success: function() {
                window.location.reload(true);
              }
            });
        });
        return false;
    });

    $('#associations .del-assoc').click(function() {
      $(this).button('loading');
      var href = '/service/' + service;
      href += '/association/' + $(this).data('hostname');

      $.ajax({
        url: href,
        type: 'delete',
        success: function(data) {
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
