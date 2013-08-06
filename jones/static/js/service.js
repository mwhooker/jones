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
      var env_components = _.reject(env.split('/'), _.isEmpty)

      $('#addChildModal .modal-header h4').text(env);
      $('#addChildModal').modal();

      $('input', form).bind(
        "propertychange keyup input paste", function(event){
          validate(env_components, $(this).val(), function(path) {
            $('#addChildModal .modal-header h4').text(path);
          });
      });

      form.submit(function() {
        return validate(env_components, $('input', this).val(), function(path) {
          form.attr('action', path);
        });
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
      // AJAX here because of the http semantics.
        $(this).hide();

        $('#add-assoc').removeClass('hidden');
        $('#add-assoc .btn').click(function() {
          validate('service', service, 'association',
            $('#add-assoc input').val(), function(path) {
              $(this).button('loading');
              $.ajax({
                url: path.slice(0,-1),
                data: {env: env},
                type: 'put',
                success: function() {
                  window.location.reload(true);
                }
              });
            });
        });
        return false;
    });

    $('#associations .del-assoc').click(function() {
      validate('service', service, 'association',
        $(this).data('hostname'), function(path) {
          $(this).button('loading');

          $.ajax({
            url: path.slice(0, -1),
            type: 'delete',
            success: function(data) {
              window.location.reload(true);
            }
          });
        });
      return false;
    });

    /*
    window.formatter = new JSONFormatter($('#jsonformatter')[0]);
    window.formatter.set(config);
    window.formatter.onError = console.log
    */
});
