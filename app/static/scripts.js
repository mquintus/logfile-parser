htmx.on('htmx:afterSwap', function (evt) {
    console.log(evt.detail.elt.id);
    if (evt.detail.elt && evt.detail.elt.id === 'log_column') {
        var columnsDropdown = document.getElementById('log_column');
        console.log(JSON.parse(evt.detail.xhr.response));
        var columnsData = JSON.parse(evt.detail.xhr.response).columns;
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