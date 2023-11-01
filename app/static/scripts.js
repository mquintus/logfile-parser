document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('log_file').addEventListener('change', function() {
        var selectedFile = this.value;
        htmx.trigger(this, 'get', '/get_available_columns/' + selectedFile);
    });
});

htmx.on('htmx:afterSwap', function(evt) {
    if (evt.detail.trigger && evt.detail.trigger.id === 'log_file') {
        var columnsDropdown = document.getElementById('log_column');
        var columnsData = evt.detail.xhr.response.columns;
        console.log(columnsData);
        columnsDropdown.innerHTML = '';  // Clear existing options

        for (var i = 0; i < columnsData.length; i++) {
            var option = document.createElement('option');
            option.value = columnsData[i];
            option.text = columnsData[i];
            columnsDropdown.appendChild(option);
        }
    }
});