/*
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/


$(function() {
    window.editor = new JSONEditor($('#jsoneditor')[0]);
    window.editor.set(config);

    function join_env(env) {
    }

    $('#update').click(function() {
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
      var form = $('#addChildModal form');
      var env = $(this).data('env');

      $('#addChildModal .modal-header h4').text(env);
      $('#addChildModal').modal();

      $('input', form).focus().bind(
        "propertychange keyup input paste", function(event){
        $('#addChildModal .modal-header h4').text(join_env($(this).val()));
      });

      $(form).submit(function() {
        $(this).attr('action', env + $('input', this).val());
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
