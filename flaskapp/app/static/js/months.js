
$(document).ready(function() {
    var table = new Tabulator("#table", {
        height: 600,
        columns: [
            {title: "Month", field: "effective_month"},
        ],
    });
    $.get("/api/months", function(data) {
        table.setData(data);
    })
});
